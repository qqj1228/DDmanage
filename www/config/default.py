# coding:utf-8

# 需要管理的图纸文档目录填写绝对路径
DWG_DIR = '/users/dwg'
# 用于图纸文档预览的缓存目录填写相对于static的相对路径
TMP_DIR = 'tmp'
# 网站名称
WEB_NAME = '图纸管理程序'
# 程序名称
APP_NAME = 'DDmanage'
# 网站logo图片地址填写相对于static的相对路径
WEB_LOGO = 'img/logo.svg'
# 每页显示多少个文件，大于100就会感到明显延时
RANGE = 100

# 上传文件存放地址
UPLOAD_FOLDER = '/users/cash/DDmanage/www/upload'

# 网站管理员email，注册时的email与这个值一致的话则自动设为管理员
EMAIL_ADMIN = ''

# 以下email选项用于发送重置密码确认邮件
# 发送email的账号
EMAIL_FROM = ''
# 管理员email密码
EMAIL_PWORD = ''
# 管理员smtp服务器地址
SMTP_SRV = ''
# 管理员smtp服务器端口
SMTP_PORT = '25'

# 是否启用调试模式，请一定不要在生产环境中启用
# 默认值为False
DEBUG = False
# cookie密钥，必须设置，用于cookie加密
SECRET_KEY = 'DDmanage'

# Flask-SQLAlchemy配置项
SQLALCHEMY_DATABASE_URI = ''
SQLALCHEMY_TRACK_MODIFICATIONS = True
