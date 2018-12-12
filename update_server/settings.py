# mysql设置
DB_NAME = "novel_site_beta"
DB_HOST = "193.112.150.18"
DB_PORT = 3306
DB_USER = "ouru"
DB_PASSWORD = "5201314Ouru..."
DB_CHARSET = "utf8"

# peewee_async设置
ALLOW_SYNC = True

# 日志设置
LOG_NAME = "update_server"
LOG_FILE = "update_server.log"
LOG_LEVEL = "DEBUG"
LOG_FORMATTER = "[%(asctime)s] [%(name)s] [%(levelname)s] : %(message)s"

FAV_UPDATE_INTERVAL = 30 * 60  # 用户收藏小说更新间隔
NOVEL_UPDATE_INTERVAL = 1 * 60 * 60  # 小说更新时间间隔
DOWNLOAD_DELAY = 1  # 延迟时间
CONCURRENT_REQUESTS = 8  # 并发数

# 邮件设置
EMAIL_HOST = "smtp.163.com"
EMAIL_PORT = 465
EMAIL_HOST_USER = "anjubaoouru@163.com"
EMAIL_HOST_PASSWORD = "qq5201314ouru"
EMAIL_CHARSET = "utf-8"

# 短信设置
SMS_URL = r'https://api.mysubmail.com/message/xsend'
SMS_APPID = "27038"
SMS_APPKEY = "c7ed55eb026edf67c87183a28948872a"

# 线上邮件设置
ONLINE_EMAIL_URL = r'https://api.mysubmail.com/mail/xsend'
ONLINE_EMAIL_APPID = "13955"
ONLINE_EMAIL_APPKEY = "2d21d55a5bdc018fbf7123544264dd9b"
