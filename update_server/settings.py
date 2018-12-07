# mysql设置
DB_NAME = "novel_site_beta"
DB_HOST = "193.112.150.18"
DB_PORT = 3306
DB_USER = "ouru"
DB_PASSWORD = "5201314Ouru..."
DB_CHARSET = "utf8"

# peewee_async设置
ALLOW_SYNC = False

# 日志设置
LOG_NAME = "update_server"
LOG_FILE = "update_server.log"
LOG_LEVEL = "DEBUG"
LOG_FORMATTER = "[%(asctime)s] [%(name)s] [%(levelname)s] : %(message)s"

UPDATE_INTERVAL = 30 * 60 #更新时间间隔
DOWNLOAD_DELAY = 0.5 #延迟时间
CONCURRENT_REQUESTS = 8 #并发数
