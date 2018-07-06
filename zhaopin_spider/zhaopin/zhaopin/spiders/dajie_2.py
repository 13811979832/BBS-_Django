# -*- coding: utf-8 -*-
import scrapy

from scrapy_redis.spiders import RedisSpider
import datetime
from datetime import timedelta
from hashlib import md5
from ..items import ScrapyItem
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re


class dajie(RedisSpider):
    name = 'dajie'
    allowed_domains = ['dajie.com']
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
    def parse(self, response):
        web = webdriver.Chrome()
        url = 'https://www.dajie.com/qz'
        web.get(url)
        time.sleep(0.7)
        web.find_element_by_css_selector('input.page_jump').send_keys(1320)
        web.find_element_by_css_selector('span.go_jump').click()
        time.sleep(0.7)
        source = web.page_source
        while 'class="next"' in source:
            web.find_element_by_css_selector('#page-con a.next').click()
            time.sleep(0.7)
            source = web.page_source
            html = BeautifulSoup(source,'html.parser')
            jobList = html.find('div',{'id':'container_jobList'})
            alist = jobList.find_all('a',href=re.compile(r'\.html'))
            for a in alist:
                link = a.get("href")
                if link:
                    yield scrapy.Request(link,self.parse_item,priority=1)

    def parse_item(self, response):
        item = ScrapyItem()
        link = response.url
        title = response.css('.job-msg-top-text span.job-name::text').extract()[0]
        job_type = response.css('.job-msg-top-text span.blue-icon::text').extract()[0].strip('（）')
        salary = response.css('.job-msg-top span.job-money::text').extract()[0]
        salary_l, salary_h = self.toInt(salary)
        location = response.css('li.ads span::text').extract()
        exp = response.css('li.exp span::text').extract()
        degree = response.css('li.edu span::text').extract()
        content = response.css('div#jp_maskit pre::text').extract()
        date_time = response.css('.job-msg-bottom .date::text').extract()
        addr = response.css('div.ads-msg span::text').extract()
        company = response.css('div.p-side-right p.title a::text').extract()
        location, exp, degree, content, date_time, addr, company = self.default_value(
            [location, exp, degree, content, date_time, addr, company])
        content = ''.join([i.replace('\n\r\t\xa0', '').strip() for i in content if i])
        p = re.compile(r'(\d+)')
        exp = p.search(exp)
        if not exp:
            exp = 0
        else:
            exp = int(exp.group(1))
        exp = int(exp)
        date_time = date_time.strip('发布于')
        aid = self.trmd5(link)

        item['aid'] = aid
        item['job_type'] = job_type
        item['salary_l'] = salary_l
        item['salary_h'] = salary_h
        item['location'] = location
        item['exp'] = exp
        item['degree'] = degree
        item['content'] = content
        item['date_time'] = date_time
        item['title'] = title
        item['link'] = link
        item['addr'] = addr
        item['company'] = company
        item['referer'] = '大街网'
        yield item

    def toInt(self, salary):
        salary = salary.strip('元/月天')
        if ('k' in salary or 'K' in salary) and '-' in salary:
            lt = [int(float(i.strip('kK'))*1000) for i in salary.split('-')]
        elif ('k' in salary or 'K' in salary) and '+' in salary:
            lt = [int(float(salary.strip('kK+'))*1000)]*2
        elif ('k' in salary or 'K' in salary) and '-' not in salary:
            lt =  [int(float(salary.strip('kK'))*1000)]*2
        elif '面议' in salary:
            lt = [0]*2
        else:
            lt = [int(salary)*30]*2
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
                if v == 'exp':
                    res = 0
                else:
                    res = ''
            yield res

    def Strfdate(self, date):
        if ':' in date:
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
