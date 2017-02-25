#!/usr/bin/env python3
# coding:utf-8

import unittest
import sys
from getopt import getopt, GetoptError
from myapp import app, models, tools


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
        u = models.User(password='cash')
        self.assertTrue(u.password_hash is not None)

    def test_password_getter_error(self):
        u = models.User(password='cash')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verify(self):
        u = models.User(password='cash')
        self.assertTrue(u.verify_password('cash'))
        self.assertFalse(u.verify_password('qian'))

    def test_password_salts_random(self):
        u1 = models.User(password='cash')
        u2 = models.User(password='cash')
        self.assertFalse(u1.password_hash == u2.password_hash)

    def test_secure_filename(self):
        self.assertEqual('abc.txt', tools.secure_filename('abc.txt'))
        self.assertEqual('中文.txt', tools.secure_filename('中文.txt'))
        self.assertEqual('abc.txt', tools.secure_filename('../abc.txt'))
        self.assertEqual('abc-dfg.txt', tools.secure_filename('/abc/dfg.txt'))
        self.assertEqual('abc-abc.txt', tools.secure_filename('abc../abc.txt'))


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
