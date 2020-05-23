# 设置MongoDB相应的参数
MONGO_CONNECTTON_STRING = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'haiwaiwang'
MONGO_CONNECTTON_NAME = 'haiwainews'

# 设置Redis相应的参数
REDIS_HOST = '127.0.0.1'
REDIS_PWD = None
REDIS_PROT = 6379
REDIS_DB=0
SET_URL='TEST:urlset'

# 定时参数
CELERY_RESULT_BACKEND='redis://@127.0.0.1:6379/2'
CELERY_TIME='*/30'


BASE_URL = 'http://opa.haiwainet.cn/apis/news'
