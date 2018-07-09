# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DianshangItem(scrapy.Item):
    collection = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    sales = scrapy.Field()
    comments = scrapy.Field()
    attr = scrapy.Field()

class JDItem(scrapy.Item):
    collection = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    parameter = scrapy.Field()
    url = scrapy.Field()
    pid = scrapy.Field()
    comment_count = scrapy.Field()
    comment_info = scrapy.Field()