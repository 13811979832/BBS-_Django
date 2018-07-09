# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
import re,json
from ..items import *
import requests

class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = 'https://list.jd.com/list.html?cat=9987,653,655'
    headers = {
        'cookie': ' __jdu=1514444266346637349766; TrackID=1SEdYLguFuc68hC7r0K7xWRFHIAT9MwQPGUo_DYASi892zWko_QO3LUOaMuCRni0ILKW1eOK3AAsWd5PHX7QnVeLIGsCddWi0drVvbC-E_WPbM3usIS97Dl_Fpveb15Wu; pinId=dmpur6ueAIzB6EKIj6glBbV9-x-f3wj7; shshshfpa=2143c4c6-326d-e70a-795b-52a013b1112a-1526548550; shshshfpb=0fe7b1b3fe63745615c703dd732164a349933a80fe7ffab035afd48461; ipLoc-djd=1-72-2799-0; unpl=V2_ZzNtbUZXEUJxWxVceRtaVmJTF1VKUUMRc19AB38bXFI3BEEPclRCFXwUR1BnGloUZAMZXEJcRhVFCHZXchBYAWcCGllyBBNNIEwHDCRSBUE3XHxcFVUWF3RaTwEoSVoAYwtBDkZUFBYhW0IAKElVVTUFR21yVEMldQl2VH8ZWQBiBhFaRVVGEnIKQFZ%2bEVoCYDMiWnJncx1wDEZdeSldNWYzUAkeU0YVdA8LVH8ZWQBiBhFaRVVGEnIKQFZ%2bEVoCYDMTbUE%3d; CCC_SE=ADC_zx8kfUbHVM9mNvZY6DxMmOrbD23tJOo9%2b8R8S7b%2bg%2bWKj8KQ80bt3j0WWZNJ7rIqkcRJoQjnFaXJ%2bLs1YsRcOhdaMc2JTWMGQIDJAzX73dzrgTgZnMP6ZCWylLfTB8Hv3snjOScmS6HkHdUWiEWYXgkqYyAbjuxGR0gGyPppbto4OfLZgbhStVsOOQfUbaA2wnQBoQYjJt91PDgNIlbDc85oBL3OOWcGqf9Yy7kyR2VrzshuFnsDj8cCT%2bzaPNBmhlM%2bt%2bZhBn4fTlulHg8mk49h9PSEAQI%2fF%2fnwtPdx0%2fnqPhLW%2bGcShpZ3iskFzB800FM3dGq6G3iwNQzPC1cjw%2bwtOstTz7FRCBdnQxxy%2f5Y6wr%2b9beXdLcQAHVdi%2f%2fEezF%2bFrcs7ipA3iHL8XUJGta9ZRDKMofyYYTaerCO%2fdT3tGp7jS5a7zr2FJ8qCq2A7Q2tBrWlEHczFNXHs25YJIrHNWEoUPIiuieULAmriR0EYSh7drF88gyGqOSaU%2f5rFMYydBtYNkH9XZPQQxsOtvpjuP6ZWNoE36Aked8cPlztCsBIgwQS51fHbDVnKs%2bg3KdThX8kBrumwsmr3eT02pBnfcttUGw%2fF%2fiBHyIXHmku7xNEjieRS7YomYSuJAhWn; __jdc=122270672; PCSYCityID=1; __jda=122270672.1514444266346637349766.1514444266.1527482215.1527484380.8; __jdv=122270672|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_51cf5bb9337b4a4997157f7b531fa6bc|1527484380256; user-key=856c8244-a7bf-4e13-b43a-c98e141da4b4; cn=0; listck=516af7cf1534b52d744a82765f4c24e2; 3AB9D23F7A4B3C9B=UZJWICUQJYISR7JOKST7EKVSCSHJGURL2LHZHQ4VKAGI2HNJSOYZZQSWJVQ2BOFX5UX5ZDXFVB4KD6CCTZPXXJK7CU; shshshfp=1301482532fcdf6ca60e0fa9455c177c; shshshsID=79800095e0b31c0a0b56699ea4c41d2f_7_1527485988330; __jdb=122270672.38.1514444266346637349766|8.1527484380',
        'referer': ' https://list.jd.com/list.html?cat=9987,653,655',
        'user-agent': ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }
    def start_requests(self):
        yield scrapy.Request(self.start_urls,self.list_parse)

    def list_parse(self,response):
        detail_urls = response.xpath('//div[@id="plist"]//li[@class="gl-item"]//div[@class="p-img"]/a/@href').extract()
        detail_urls = ['https:' + i for i in detail_urls if 'http' not in i]
        for durl in detail_urls:
            yield SplashRequest(durl,self.detail_parse,args={'wait':2})
        next = response.css('#J_bottomPage span.p-num a[class*="curr"]+a::attr(href) ').extract_first()
        if next:
            next_url = 'https://list.jd.com' + next
            yield scrapy.Request(next_url,self.list_parse)
    def detail_parse(self,response):
        #temp用于临时储存评论
        self.comment_temp = []
        item = JDItem()
        url = response.url
        pid = url.split('/')[-1].split('.')[0]
        name = response.xpath('//div[@class="sku-name"]/text()').extract_first(default='').strip()
        price = response.xpath('//span[@class="p-price"]//span[@class]/text()') or response.xpath('//span[contains(@class,"J-presale-price")]/text()')
        price = price.extract_first(default='').strip()
        comment_count = response.xpath('//div[@id="comment-count"]//a/text()').extract_first(default='').strip()
        parameter_li = response.xpath('//ul[contains(@class,"parameter2")]/li')
        parameter = []
        for li in parameter_li:
            parameter.append(li.xpath('./text()').extract_first(default='').split('：'))
        item['collection'] = 'jingdong'
        item['name'] = name
        item['price'] = price
        item['parameter'] = parameter
        item['comment_count'] = comment_count
        item['url'] = url
        item['pid'] = pid
        item['comment_info'] = self.comment_temp
        comment_url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv5778&productId={pid}&score=0&sortType=5&page={page}&pageSize=10&isShadowSku=0&rid=0&fold=1'
        #抓取10页评论内容
        for i in range(0,11):
            res = requests.get(comment_url.format(pid=pid, page=i))
            data = res.text
            pat = re.compile(r'.*\((.*)\)')
            r = pat.search(data)
            if r:
                res = r.group(1)
                p = re.compile(r'.*?topped.*?\"content\":\"(.*?)\".*?\"nickname\":\"(.*?)\"')
                res = p.findall(res)
                if res:
                    for content, nick in res:
                        self.comment_temp.append((nick,content.replace('\n','').strip()))
        yield item
