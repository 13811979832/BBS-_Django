# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class DianshangPipeline(object):
    def __init__(self):
        try:
            self.client = pymongo.MongoClient()
            self.db = self.client.dianshan
        except Exception:
            print('数据库连接失败')
    def process_item(self, item, spider):
        try:
            self.db[item['collection']].insert(dict(item))
            print('数据插入成功')
        except:
            print('数据插入失败')
        return item

    def close_spider(self, spider):
        self.client.close()
