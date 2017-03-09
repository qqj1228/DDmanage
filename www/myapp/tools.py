# coding:utf-8

import os
import re
import functools
import zipfile
from io import BytesIO

from flask import abort
from flask_login import current_user

from .models import Permission


def r_slash(s):
    """Ensure user submited string not contains '/' or muti '-'.
    Args:
        s: submited string
    Returns:
        replaced slash string
    """
    s = re.sub('[" "\/\--.]+', '-', s)
    s = re.sub(r':-', ':', s)
    s = re.sub(r'^-|-$', '', s)
    return s


def secure_filename(filename):
    name_ext = os.path.splitext(filename)
    secure_name = r_slash(name_ext[0])
    return secure_name + name_ext[1]


def permission_required(permission):
    def decorator(func):
        @functools.wraps(func)
        def wraps(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return wraps
    return decorator


def admin_required(func):
    return permission_required(Permission.ADMIN)(func)


class InMemoryZip(object):

    def __init__(self):
        # Create the in-memory file-like object
        self.in_memory_zip = BytesIO()

    def appendFile(self, filepath):
        '''
        从本地磁盘读取文件，并将其添加到压缩文件中
        file_path 为包括文件名和文件路径的完整文件名
        '''
        p, fn = os.path.split(filepath)
        with open(filepath, "rb") as f:
            c = f.read()
            self.append(fn, c)
        return self

    def append(self, filename_in_zip, file_contents):
        '''
        Appends a file with name filename_in_zip and contents of
        file_contents to the in-memory zip.
        '''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)
        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0
        return self

    def read(self):
        '''
        Returns a string with the contents of the in-memory zip.
        '''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writetofile(self, filepath):
        '''
        Writes the in-memory zip to a file.
        filepath 为包括文件名和文件路径的完整文件名
        '''
        with open(filepath, "wb") as f:
            f.write(self.read())
