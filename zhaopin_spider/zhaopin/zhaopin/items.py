# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


def Get_sql(obj,table,rm=None):
    cls = obj.__class__
    fields = list(cls.__dict__['fields'])
    if rm:
        try:
           rm_list = rm.split(',')
        except:
            rm_list = list(rm)
        for rm in rm_list:
            fields.remove(rm)
    v = ('%s,' * len(fields))[:-1]
    k = ('{},' * len(fields)).format(*fields)[:-1]
    sql = 'insert into {}({})'.format(table,k) + ' VALUE ({})'.format(v)
    data = [obj[i] for i in fields]
    return sql, data


class ScrapyItem(scrapy.Item):
    title = scrapy.Field()
    salary_l = scrapy.Field()
    salary_h = scrapy.Field()
    location = scrapy.Field()
    exp = scrapy.Field()
    degree = scrapy.Field()
    job_type = scrapy.Field()
    date_time = scrapy.Field()
    aid = scrapy.Field()
    addr = scrapy.Field()
    company = scrapy.Field()
    link = scrapy.Field()
    content = scrapy.Field()
    referer = scrapy.Field()
    def get_sql(self):
        return Get_sql(self,'lagou')