# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from ..items import DianshangItem

class TianmaoSpider(scrapy.Spider):
    name = 'tianmao'
    allowed_domains = ['tmall.com']
    start_urls = 'https://nvzhuang.tmall.com/'
    def start_requests(self):
        yield SplashRequest(self.start_urls,self.index_parse,args={'wait':1})

    def index_parse(self,response):
        list_urls = response.xpath('//ul[@class="cate-nav"]//a[contains(@href,"list.tmall.com/search_product.htm")]/@href').extract()
        for lurl in list_urls:
            lurl = 'https:' + lurl
            yield SplashRequest(lurl,self.list_parse,args={'wait':1})
    def list_parse(self,response):
        detail_urls = response.xpath('//div[@id="J_ItemList"]//div[@class="productImg-wrap"]/a/@href').extract()
        for durl in detail_urls:
            durl = 'https:' + durl
            yield SplashRequest(durl,self.detail_parse,args={'wait':1})
        next_url = response.xpath('//div[@class="ui-page"]/b[@class="ui-page-num"]/b/following-sibling::*[1]/@href').extract_first()
        if next_url:
            next_url = 'https://list.tmall.com/search_product.htm' + next_url
            yield SplashRequest(next_url, self.list_parse, args={'wait': 1})

    def detail_parse(self,response):
        item = DianshangItem()
        name = response.xpath('//div[@class="tb-detail-hd"]/h1/text()').extract_first(default='暂无').strip()
        price = response.xpath('//div[@class="tm-promo-price"]/span[@class="tm-price"]/text()').extract_first(default='暂无').strip()
        counts = response.xpath('//span[@class="tm-count"]/text()').extract()
        sales,comments,*_ = counts
        attr_li = response.xpath('//ul[@id="J_AttrUL"]/li')
        attrs = []
        for li in attr_li:
            info = li.xpath('./text()').extract_first()
            attr,value = info.split(':')
            attrs.append((attr,value.replace('\xa0','')))
        item['collection'] = 'tianmao'
        item['name'] = name
        item['price'] = price
        item['sales'] = sales
        item['comments'] = comments
        item['attr'] =  attrs
        yield item

