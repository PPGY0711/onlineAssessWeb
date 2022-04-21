#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@objective: get mysql session
@author: pengguanyan
@update date: 2021/12/28
"""
import pymysql


class DBSession():
    def __init__(self, db_obj):
        self.db_obj = db_obj

    def connect(self):
        # 打开数据库连接
        host = self.db_obj['host']
        user = self.db_obj['user']
        password = self.db_obj['password']
        dbname = self.db_obj['dbname']
        db = pymysql.connect(host=host, user=user, password=password, database=dbname)
        return db

    def execute(self, sql, fetch_type=0):
        # 每次查询建立一次临时的mysql连接，确保不会出现没有关闭cursor和db的情况出现
        # 使用 cursor() 方法创建一个游标对象 cursor
        db = self.connect()
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            if fetch_type == 0:
                print('选择查询单条数据: %s' % sql)
                data = cursor.fetchone()
                db.commit()
            elif fetch_type == 1:
                print('选择查询多条数据: %s' % sql)
                data = cursor.fetchall()
                db.commit()
            else:
                print('当前执行的是非Select语句: %s' % sql)
                data = None
                db.commit()
            cursor.close()
            db.close()
            return data
        except:
            db.rollback()
            print('SQL执行失败，执行语句为%s' % str(sql))
            db.close()


if __name__ == "__main__":
    import yaml
    # 读取全局配置文件
    f = open('config.yaml', encoding='UTF-8')
    config = yaml.safe_load(f)
    print(config)
    db_obj = config['mysql']
    f.close()
    dbs = DBSession(db_obj)
    print(dbs.db_obj)
    data = dbs.execute("SELECT VERSION()")
    print("Database version : %s " % data)
    data = dbs.execute("SELECT user_id, password from user_info where user_name = 'testUser1'")
    print("Select result : {} ".format(data))
    table = 'building_info'
    building_sql = "SELECT * FROM {table} WHERE user_id = '{user_id}'".format(table=table, user_id='ry1krQ23')
    data = dbs.execute(building_sql, fetch_type=1)
    building_list = []
    for i in range(len(data)):
        building_info = {}
        building_info['building_id'] = data[i][0]
        building_info['building_name'] = data[i][2]
        building_info['building_img'] = data[i][3]
        building_info['address'] = "" if data[i][4] is None else data[i][4]
        building_info['building_type'] = "" if data[i][5] is None else data[i][5]
        building_info['area'] = 0.0 if data[i][6] is None else data[i][6]
        building_info['cold_source'] = data[i][7]
        building_info['terminal_type'] = data[i][8]
        building_info['create_time'] = data[i][9].strftime("%Y-%m-%d %H:%M:%S")
        building_list.append(building_info)
    print(building_list)
    from models import BuildingData
    data = BuildingData.getData('7pSGMbvJ', dbs)
    print(data)