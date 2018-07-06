# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
import datetime, math
from datetime import timedelta
from hashlib import md5
from ..items import ScrapyItem
from bs4 import BeautifulSoup

import re


class job51(RedisCrawlSpider):
    name = '51job'
    allowed_domains = ['51job.com']
    redis_key = 'start_urls'
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            # 'User-Agent':'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': '_ga=GA1.2.729308262.1515999800; user_trace_token=20180115150320-2baeff3c-f9c2-11e7-9ad0-525400f775ce; LGUID=20180115150320-2baf01d0-f9c2-11e7-9ad0-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD; JSESSIONID=ABAAABAAAFCAAEG1E9059DD35CB0074A3CAC41F6F12746D; _gid=GA1.2.31556095.1516618533; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1515999802,1516618534; LGSID=20180122185528-c227d701-ff62-11e7-a5a8-5254005c3644; PRE_UTM=m_cf_cpt_baidu_pc; PRE_HOST=bzclk.baidu.com; PRE_SITE=http%3A%2F%2Fbzclk.baidu.com%2Fadrc.php%3Ft%3D06KL00c00f7Ghk60yUKm0FNkUs0gsvNp00000PW4pNb00000XRRNRW.THL0oUhY1x60UWdBmy-bIfK15yuhnW6dmWcYnj0sPHI-nWn0IHYLnRFDrjnsPWnsfWnzfH7DrHcsrDmzwj9arDR1rjczn0K95gTqFhdWpyfqn101n1csPHnsPausThqbpyfqnHm0uHdCIZwsT1CEQLILIz4_myIEIi4WUvYE5LNYUNq1ULNzmvRqUNqWu-qWTZwxmh7GuZNxTAn0mLFW5HnkP1T3%26tpl%3Dtpl_10085_15730_11224%26l%3D1500117464%26attach%3Dlocation%253D%2526linkName%253D%2525E6%2525A0%252587%2525E9%2525A2%252598%2526linkText%253D%2525E3%252580%252590%2525E6%25258B%252589%2525E5%25258B%2525BE%2525E7%2525BD%252591%2525E3%252580%252591%2525E5%2525AE%252598%2525E7%2525BD%252591-%2525E4%2525B8%252593%2525E6%2525B3%2525A8%2525E4%2525BA%252592%2525E8%252581%252594%2525E7%2525BD%252591%2525E8%252581%25258C%2525E4%2525B8%25259A%2525E6%25259C%2525BA%2526xp%253Did%28%252522m6c247d9c%252522%29%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FDIV%25255B1%25255D%25252FH2%25255B1%25255D%25252FA%25255B1%25255D%2526linkType%253D%2526checksum%253D220%26ie%3Dutf-8%26f%3D8%26tn%3Dbaidu%26wd%3D%25E6%258B%2589%25E5%258B%25BE%25E7%25BD%2591%26oq%3Dwin10%252520python%252520portia%252520%2525E5%2525AE%252589%2525E8%2525A3%252585%26rqlang%3Dcn%26inputT%3D508%26bs%3Dwin10%2520python%2520portia%2520%25E5%25AE%2589%25E8%25A3%2585; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F%3Futm_source%3Dm_cf_cpt_baidu_pc; X_HTTP_TOKEN=5608d432cc526b93496d12c0753a37a0; _gat=1; TG-TRACK-CODE=index_navigation; LGRID=20180122190943-bfbb0b93-ff64-11e7-b4a1-525400f775ce; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1516619391; SEARCH_ID=335731afdaa945d891544cef0aa75074',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        },
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {
            'scrapy_redis.pipelines.RedisPipeline': 400,
        },
        'LOG_LEVEL ': 'DEBUG',

    }
    rules = (
        Rule(LinkExtractor(allow=(r'search\.51job\.com/list/'),
                           restrict_xpaths=(r'//div[@class="cn hlist"]', r'//div[@class="dw_page"]')), follow=True),
        Rule(LinkExtractor(allow=(r'http://jobs\.51job\.com/.*?/\d+.html\?s=01&t=0$')), callback='parse_item',
             follow=False),
    )

    def parse_item(self, response):
        item = ScrapyItem()
        html = BeautifulSoup(response.text, 'html.parser')
        link = response.url
        title = response.css('div.cn h1::text').extract()
        adinfo = response.css('div.cn span.lname::text').extract()
        salary = response.css('div.cn strong::text').extract()
        company = response.css('div.cn p.cname a::text').extract()
        title, adinfo, company = self.default_value([title, adinfo, company])
        if salary:
            salary = salary[0]
            item['salary_l'],item['salary_h'] = self.toInt(salary)
        else:
            item['salary_l'] = item['salary_h'] = 0
        info = [html.find('em', {'class': 'i{}'.format(i)}) for i in range(1, 5)]
        info = self.default_info(info)
        exp, degree, _, date_time = info
        p = re.compile(r'(\d+)')
        exp = p.search(exp)
        if not exp:
            exp = 0
        else:
            exp = exp.group(1)
        date_time = self.Strfdate(date_time)

        content = response.xpath('//div[@class="bmsg job_msg inbox"]//text()').extract()
        content = ''.join(
            [i.replace('\n\t\r\xa0', '').strip() for i in content])

        if '-' in adinfo:
            location, addr = adinfo.split('-')
            item['addr'] = addr
        else:
            location = adinfo
            item['addr'] = ''
        item['job_type'] = '全职'
        item['link'] = link
        item['title'] = title
        item['company'] = company
        item['location'] = location
        item['content'] = content
        item['exp'] = exp
        item['degree'] = degree
        item['date_time'] = date_time
        item['aid'] = self.trmd5(link)
        item['referer'] = '51Job'
        yield item

    def toInt(self, salary):
        if '万/月' in salary:
            salary = salary.strip('万/月')
            lt = [int(float(i) * 10000) for i in salary.split('-')]
        elif '万/年' in salary:
            salary = salary.strip('万/年')
            lt = [math.ceil(float(i)*10000 / 12) for i in salary.split('-')]
        else:
            salary = salary.strip('千/月')
            lt = [int(float(i)*1000) for i in salary.split('-')]
        return lt

    def default_info(self, info):
        for i in info:
            if not i:
                res = ''
            else:
                res = i.find_parent().get_text()
            yield res

    def default_value(self, values):
        for v in values:
            if v:
                res = v[0]
            else:
                res = '暂无'
            yield res

    def Strfdate(self, date):
        date = date.strip('发布')
        p = re.compile(r'\d{4}')
        res = p.search(date)
        if not res:
            m = int(date.split('-')[0])
            if m < 2:
                date = '2018-' + date
            else:
                date = '2017-' + date
        return date
    def trmd5(self, link):
        m = md5()
        m.update(bytes(link, encoding='utf-8'))
        return m.hexdigest()
