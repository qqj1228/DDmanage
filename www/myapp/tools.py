import re
import os


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
