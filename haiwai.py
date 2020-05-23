'''
http://news.haiwainet.cn/
海外网原创新闻信息爬取
'''
from config import *
from celery_setting import *
from pyquery import PyQuery as pq
import requests
import time, datetime
import random
import re
import json
import pymongo
import redis
import hashlib

client = pymongo.MongoClient(MONGO_CONNECTTON_STRING)
db = client[MONGO_DB_NAME]
collention = db[MONGO_CONNECTTON_NAME]
# 链接redis数据库
red = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PROT, db=REDIS_DB)
headers = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36', }
# 当前日期
date = datetime.datetime.now().strftime('%Y-%m')


def get_md5(url):
    '''把目标url进行哈希'''
    md5 = hashlib.md5()
    md5.update(url.encode('utf-8'))
    return md5.hexdigest()


def news_url(pages=0):
    '''获取详细新闻的链接'''
    while True:
        pages += 1
        s_time = str(int(time.time() * 1000))
        params = {
            'catid': '3541093',
            'num': '10',
            'page': pages,
            'moreinfo': '1',
            'relation': '1',
            'format': 'jsonp',
            'callback': 'jQuery11020' + str(''.join(random.choice('0123456789') for i in range(16))) + '_' + s_time,
            '_': str(int(s_time) + random.randint(1, 5))
        }
        response = requests.get(BASE_URL, headers=headers, params=params)
        result = re.search('"result":(.*?)}\);', response.text).group(1)
        res = json.loads(result)
        for item in res:
            news_time = datetime.datetime.strptime(item['pubtime'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
            # 判断是不是当月的数据，不是则返回False
            if date != news_time:
                return False
            res = red.sadd(SET_URL, get_md5(item['link']))  # 注意是 保存set的方式
            if res == 0:  # 若返回0,说明插入不成功，表示有重复
                continue
            else:
                yield item['link']


def news_info(url):
    '''对新闻网站进行解析，提取数据'''
    doc = pq(url, encoding='utf-8')
    time.sleep(random.random())
    title = doc('.show_wholetitle').text()
    date = doc('span.first').text()
    n_source = doc('div.contentExtra span:contains(来源)')
    source = n_source.text().split('：')[1] if n_source else '无'
    content = doc('div.contentMain p').text()
    point = doc('div.summary')
    digested = point.text() if point else '无'
    images = doc('div.contentMain p img[src^="http"]')
    images = ' ,'.join([images.attr('src') for i in images]) if images else '无'
    return {
        'title': title,
        'digested': digested,
        'date': date,
        'source': source,
        'content': content,
        'images': images,
        'url': url
    }


def save_date(data):
    '''将数据保存到Mongodb数据中'''
    collention.update_one({
        'title': data.get('title')
    }, {
        '$set': data  # $set操作符表示更新操作
    }, upsert=True)  # upsert设为True，表示存在即更新，不存在即插入
    print('写入完成！')


@app.task
def main():
    for item in news_url():
        data = news_info(item)
        save_date(data)
