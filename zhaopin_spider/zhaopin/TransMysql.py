# -*- coding: utf-8 -*-
import json
import redis  # pip install redis
import pymysql
from concurrent import futures

def main():
    # 指定redis数据库信息
    rediscli = redis.StrictRedis(host='', port = 6379, db = 0,password='')
    # 指定mysql数据库
    mysqlcli = pymysql.connect(host='127.0.0.1', user='root',passwd='', db='zhaopin', charset='utf8')

    # 无限循环
    while True:
        source, data = rediscli.blpop(['zhilian:items']) # 从redis里提取数据

        item = json.loads(data.decode('utf-8')) # 把 json转字典

        try:
            # 使用cursor()方法获取操作游标
            cur = mysqlcli.cursor()
            # 使用execute方法执行SQL INSERT语句
            sql = 'insert into zhaopin(aid,link,title,salary_l,salary_h,location,exp,degree,job_type,date_time,content,addr,company,referer) ' \
                  'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update date_time=values(date_time),salary_l=VALUES(salary_l),salary_h=values(salary_h)'

            data = (item.get('aid',''),item.get('link',''), item.get('title',''), item.get('salary_l',0), item.get('salary_h',0), item.get("location",''), item.get("exp",0),item.get("degree",''), item.get("job_type",''), item.get("date_time",''), item.get("content",''),item.get("addr",''), item.get("company",''), item.get("referer",''))
            cur.execute(sql, data)

            # 提交sql事务
            mysqlcli.commit()
            #关闭本次操作
            cur.close()
            print ("插入 %s" % item['title'])
        except pymysql.Error as e:
            mysqlcli.rollback()
            print ("插入错误" ,str(e))

if __name__ == '__main__':
    # with futures.ProcessPoolExecutor(8) as executor:
    #     executor.submit(main)
    with futures.ThreadPoolExecutor(10) as executor:
        for i in range(10):
            executor.submit(main)