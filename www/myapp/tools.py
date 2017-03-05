# coding:utf-8

import os
import re
import functools

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
