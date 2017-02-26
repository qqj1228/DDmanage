# 需要管理的图纸文档目录
DWG_DIR = '/users/dwg'
# 用于图纸文档预览的缓存目录
TMP_DIR = 'tmp'
# 网站名称
WEB_NAME = '图纸管理程序'
# 程序名称
APP_NAME = 'DDmanage'
# 每页显示多少个文件，大于100就会感到明显延时
RANGE = 100
# 上传文件存放地址
UPLOAD_FOLDER = '/users/cash/DDmanage/www/upload'

# 是否启用调试模式，请一定不要在生产环境中启用
# 默认值为False
DEBUG = False
# cookie密钥，必须设置，用于cookie加密
SECRET_KEY = 'DDmanage'

# Flask-SQLAlchemy配置项
SQLALCHEMY_DATABASE_URI = ''
SQLALCHEMY_TRACK_MODIFICATIONS = True
