# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
import datetime
from datetime import timedelta
from hashlib import md5
from ..items import ScrapyItem
import re


class Tc58Spider(RedisCrawlSpider):
    name = 'tc58'
    allowed_domains = ['58.com']
    redis_key = 'start_urls'
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            # 'User-Agent':'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Baiduspider'
            # 'User-Agent':'Mozilla/5.0 (Linux; Android 7.0; SM-G935P Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.92 Mobile Safari/537.36'
            # 'Cookie': '_ga=GA1.2.729308262.1515999800; user_trace_token=20180115150320-2baeff3c-f9c2-11e7-9ad0-525400f775ce; LGUID=20180115150320-2baf01d0-f9c2-11e7-9ad0-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD; JSESSIONID=ABAAABAAAFCAAEG1E9059DD35CB0074A3CAC41F6F12746D; _gid=GA1.2.31556095.1516618533; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1515999802,1516618534; LGSID=20180122185528-c227d701-ff62-11e7-a5a8-5254005c3644; PRE_UTM=m_cf_cpt_baidu_pc; PRE_HOST=bzclk.baidu.com; PRE_SITE=http%3A%2F%2Fbzclk.baidu.com%2Fadrc.php%3Ft%3D06KL00c00f7Ghk60yUKm0FNkUs0gsvNp00000PW4pNb00000XRRNRW.THL0oUhY1x60UWdBmy-bIfK15yuhnW6dmWcYnj0sPHI-nWn0IHYLnRFDrjnsPWnsfWnzfH7DrHcsrDmzwj9arDR1rjczn0K95gTqFhdWpyfqn101n1csPHnsPausThqbpyfqnHm0uHdCIZwsT1CEQLILIz4_myIEIi4WUvYE5LNYUNq1ULNzmvRqUNqWu-qWTZwxmh7GuZNxTAn0mLFW5HnkP1T3%26tpl%3Dtpl_10085_15730_11224%26l%3D1500117464%26attach%3Dlocation%253D%2526linkName%253D%2525E6%2525A0%252587%2525E9%2525A2%252598%2526linkText%253D%2525E3%252580%252590%2525E6%25258B%252589%2525E5%25258B%2525BE%2525E7%2525BD%252591%2525E3%252580%252591%2525E5%2525AE%252598%2525E7%2525BD%252591-%2525E4%2525B8%252593%2525E6%2525B3%2525A8%2525E4%2525BA%252592%2525E8%252581%252594%2525E7%2525BD%252591%2525E8%252581%25258C%2525E4%2525B8%25259A%2525E6%25259C%2525BA%2526xp%253Did%28%252522m6c247d9c%252522%29%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FH2%25255B1%25255D%25252FA%25255B1%25255D%2526linkType%253D%2526checksum%253D220%26ie%3Dutf-8%26f%3D8%26tn%3Dbaidu%26wd%3D%25E6%258B%2589%25E5%258B%25BE%25E7%25BD%2591%26oq%3Dwin10%252520python%252520portia%252520%2525E5%2525AE%252589%2525E8%2525A3%252585%26rqlang%3Dcn%26inputT%3D508%26bs%3Dwin10%2520python%2520portia%2520%25E5%25AE%2589%25E8%25A3%2585; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F%3Futm_source%3Dm_cf_cpt_baidu_pc; X_HTTP_TOKEN=5608d432cc526b93496d12c0753a37a0; _gat=1; TG-TRACK-CODE=index_navigation; LGRID=20180122190943-bfbb0b93-ff64-11e7-b4a1-525400f775ce; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1516619391; SEARCH_ID=335731afdaa945d891544cef0aa75074',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        },
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {
            'scrapy_redis.pipelines.RedisPipeline': 400,
        },
        'LOG_LEVEL ': 'DEBUG',

    }
    rules = (
        Rule(LinkExtractor(allow=(r'/\w+/'), restrict_css=(r'div.allPos', r'div.pagesout')), follow=True),
        Rule(LinkExtractor(allow=(r'shtml'), restrict_css=r'div.main'), callback='parse_item', process_request='pro',
             follow=False),
    )

    def pro(self, request):
        request.priority = 1
        return request

    def parse_item(self, response):
        item = ScrapyItem()
        link = response.url
        title = response.css('div.pos_base_info .pos_title::text').extract()[0]
        salary = response.css('div.pos_base_info .pos_salary::text').extract()[0]
        info = response.css('div.pos_base_condition span::text').extract()
        adinfo = response.xpath('//div[@class="pos-area"]/span//text()').extract()
        company = response.css('div.comp_baseInfo_title .baseInfo_link a::text').extract()[0]
        content = response.css('div.des::text').extract()
        content = ''.join(
            [i.replace('\n\r\t\xa0', '').strip() for i in content if i])
        location = adinfo[1]
        addr = ''.join(adinfo[3:6:2])
        date_time = response.css('span.pos_base_update span::text').extract()[0]
        date_time = self.Strfdate(date_time)
        _, degree, exp = info
        p = re.compile(r'(\d+)')
        exp = p.search(exp)
        if exp:
            exp = exp.group(1)
        else:
            exp = 0

        item['location'] = location
        item['addr'] = addr
        item['job_type'] = '全职'
        item['date_time'] = date_time
        item['exp'] = int(exp)
        item['degree'] = degree
        item['salary_l'], item['salary_h'] = self.toInt(salary)
        item['title'] = title
        item['company'] = company
        item['aid'] = self.trmd5(link)
        item['link'] = link
        item['content'] = content
        item['referer'] = '58同城'

        yield item

    def default_value(self, values):
        for v in values:
            if v:
                res = v[0]
            else:
                res = ''
            yield res

    def toInt(self, salary):
        if '面议' in salary:
            lt = [0] * 2
        elif '上' in salary or '下' in salary:
            sa = int(salary.strip('元以上/月下\xa0'))
            lt = [sa] * 2
        else:
            sa = salary.strip('元/月\xa0')
            lt = [int(i.replace('\xa0', '').strip()) for i in sa.split('-')]
        return lt

    def Strfdate(self, date):
        if ':' or '今' in date:
            strf = datetime.datetime.now().strftime('%Y-%m-%d')
        elif '天' in date:
            n = int(date.strip('天前'))
            days = timedelta(days=n)
            strf = datetime.datetime.now() - days
            strf = strf.strftime('%Y-%m-%d')
        else:
            strf = date
        return strf

    def trmd5(self, link):
        m = md5()
        m.update(bytes(link, encoding='utf-8'))
        return m.hexdigest()
