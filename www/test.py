#!/usr/bin/env python3
# coding:utf-8

import sys
import unittest
from getopt import GetoptError, getopt

from myapp import app, models, tools, apis


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client(use_cookies=True)

    def tearDown(self):
        models.db.session.remove()

    def test_index(self):
        response = self.client.get('/')
        self.assertIn('当前打开的目录', response.get_data(as_text=True))

    def test_password_setter(self):
        with app.app_context():
            u = models.User(password='cash')
            self.assertTrue(u.password_hash is not None)

    def test_password_getter_error(self):
        with app.app_context():
            u = models.User(password='cash')
            with self.assertRaises(AttributeError):
                u.password

    def test_password_verify(self):
        with app.app_context():
            u = models.User(password='cash')
            self.assertTrue(u.verify_password('cash'))
            self.assertFalse(u.verify_password('qian'))

    def test_password_salts_random(self):
        with app.app_context():
            u1 = models.User(password='cash')
            u2 = models.User(password='cash')
            self.assertFalse(u1.password_hash == u2.password_hash)

    def test_secure_filename(self):
        self.assertEqual('abc.txt', tools.secure_filename('abc.txt'))
        self.assertEqual('中文.txt', tools.secure_filename('中文.txt'))
        self.assertEqual('abc.txt', tools.secure_filename('../abc.txt'))
        self.assertEqual('abc-dfg.txt', tools.secure_filename('/abc/dfg.txt'))
        self.assertEqual('abc-abc.txt', tools.secure_filename('abc../abc.txt'))

    def test_roles_and_permissions(self):
        with app.app_context():
            models.Role.insert_roles()
            u = models.User(email='john@example.com', password='cat')
            self.assertTrue(u.can(models.Permission.DEFAULT))
            self.assertFalse(u.can(models.Permission.DWG_BROWSE))

    def test_todir(self):
        self.assertEqual('HRCS', apis.todir('HT.HRCS95.41-00'))
        self.assertEqual('HRCS', apis.todir('HRCS95.41-00'))
        self.assertEqual('HRCS', apis.todir('HT.RSCS2.41-00'))
        self.assertEqual('HT.0', apis.todir('HT.0M20.41-00'))
        self.assertEqual('HT.a', apis.todir('HT.aM20.41-00'))
        self.assertEqual('HT.A', apis.todir('HT.AM20.41-00'))
        self.assertEqual('H', apis.todir('HM20.41-00'))
        self.assertEqual('4', apis.todir('4M20.41-00'))
        self.assertEqual('S', apis.todir('S6M20.41-00'))
        self.assertEqual('我', apis.todir('我的文件'))


if __name__ == '__main__':
    cov = None
    try:
        opts, args = getopt(sys.argv[1:], 'c')
    except GetoptError as err:
        print(err)
        exit()

    for opt, value in opts:
        if opt in ('-c'):
            from coverage import coverage
            cov = coverage(branch=True, include='myapp/*')
            cov.start()

    try:
        unittest.main()
    except:
        pass

    if cov:
        cov.stop()
        cov.save()
        print('\nCoverage Summary:')
        cov.report()
        cov.html_report(directory='./coverage')
        cov.erase()
