from scrapy import cmdline

import os
os.chdir('zhaopin/spiders')

cmdline.execute('scrapy crawl zhilian'.split())