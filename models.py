#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@objective: create identity classes for tables
@author: pengguanyan
@update date: 2022/01/09
"""
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import datetime
from utils import generateUUID
import json


class User(UserMixin):
    def __init__(self, username, dbs, get_profile=0):
        # is_new用于区分调用入口，is_new=0表示用户选择登录，默认不是要注册新用户
        self.username = username
        self.dbs = dbs
        data = self.get_id()
        if data:
            self.id = data[0]
            self.password_hash = data[1]
        else:
            self.id = None
            self.password_hash = None
        # print('user_id: {}, password_hash: {}'.format(self.id, self.password_hash))
        if get_profile == 0:
            self.profile = {}
        else:
            self.profile = User.get_user_info(username, dbs)

    def verify_password(self, password):
        password_hash = self.get_password_hash()
        print(password_hash)
        # print(password)
        if password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_password_hash(self):
        """
        try to get password hash from file.
        :return password_hash: if the there is corresponding user in
                the file, return password hash.
                None: if there is no corresponding user, return None.
        """
        table = self.dbs.db_obj["user_table"]
        sql = """select password from {table} where user_name = '{username}';""".format(table=table,
                                                                                       username=self.username)
        print('sql is %s' % sql)
        data = self.dbs.execute(sql=sql)
        print("data is {}".format(data))
        return data[0] if data is not None else None

    def get_id(self):
        """get user id from profile file, if not exist, it will
        generate a uuid for the user.
        """
        if self.username is not None:
            if isinstance(self.username, tuple):
                self.username = self.username[0]
            table = self.dbs.db_obj["user_table"]
            sql = """select user_id, password from {table} 
                     where user_name = '{username}';""".format(table=table, username=self.username)
            data = self.dbs.execute(sql=sql)
            return data if data is not None else None
        else:
            return None

    def modify_profile(self, profile):
        table = self.dbs.db_obj['user_profile']
        gender = profile['gender']
        profession = profile['profession']
        belong = profile['belong']
        user_id = profile['user_id']
        sql = "UPDATE {table} SET gender = '{gender}', profession='{profession}', belong='{belong}'" \
              "WHERE user_id = '{user_id}';".format(table=table, gender=gender,
                                                   profession=profession, belong=belong, user_id=user_id)
        self.dbs.execute(sql=sql, fetch_type=2)
        self.profile = profile

    @staticmethod
    def modify_password(username, password, dbs):
        id = User.get_id_static(username, dbs)
        password_hash = generate_password_hash(password)
        table = dbs.db_obj['user_table']
        # SQL 插入语句
        sql = """UPDATE {table} set password = '{password}'
              WHERE user_id = '{id}';""".format(table=table, id=id, password=password_hash)
        dbs.execute(sql, fetch_type=2)

    @staticmethod
    def modify_avatar(username, avatarUrl, dbs):
        id = User.get_id_static(username, dbs)
        table = dbs.db_obj['user_profile']
        # SQL 插入语句
        sql = """UPDATE {table} set avatar = '{url}'
              WHERE user_id = '{id}';""".format(table=table, id=id, url=avatarUrl)
        dbs.execute(sql, fetch_type=2)

    @staticmethod
    def get(user_id, dbs):
        """try to return user_id corresponding User object.
        This method is used by load_user callback function
        """
        if not user_id:
            return None
        elif isinstance(user_id, str):
            user_id = eval(user_id)
        if isinstance(user_id, tuple):
            user_id = user_id[0]
        table = dbs.db_obj["user_table"]
        sql = """select user_name from {table} where user_id = '{user_id}';""".format(table=table,
                                                                                     user_id=user_id)
        data = dbs.execute(sql=sql)
        return User(data, dbs, get_profile=1) if data is not None else None

    @staticmethod
    def isUsernameTaken(username, dbs):
        """
        查询当前用户名是否被占用
        :param username:
        :param dbs:
        :return:
        """
        if not username:
            return None
        table = dbs.db_obj["user_table"]
        sql = """select user_id from {table} where user_name = '{username}';""".format(table=table,
                                                                                      username=username)
        data = dbs.execute(sql=sql)
        return True if data is not None else False

    @staticmethod
    def register(username, password, dbs):
        """Register a new user: save user name, id and password hash to database"""
        password_hash = generate_password_hash(password)
        # print("新用户注册：\n用户名：{username}\n加密密码：{phash}".format(username=username, phash=password_hash))
        table = dbs.db_obj['user_table']
        profile = dbs.db_obj['user_profile']
        uid = generateUUID()
        # SQL 插入语句
        reg_sql = "INSERT INTO %s (user_id, user_name, password) VALUES" \
                  " ('%s', '%s', '%s');" % (table, uid, username, password_hash)
        dbs.execute(reg_sql, fetch_type=2)
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        profile_sql = "INSERT INTO %s (user_id, user_name, register_time) " \
                      "VALUES ('%s','%s', '%s');" % (profile, uid, username, dt)
        dbs.execute(profile_sql, fetch_type=2)

    @staticmethod
    def get_user_info(username, dbs):
        """After User login: get the whole profile for a particular user"""
        if isinstance(username, tuple):
            username = username[0]
        table = dbs.db_obj['user_profile']
        profile_sql = "SELECT user_id, user_name, avatar, gender, profession, belong, register_time" \
                      " FROM {table} WHERE user_name = '{username}';".format(table=table, username=username)
        data = dbs.execute(profile_sql)
        profile = {}
        if data is not None:
            profile['user_id'] = data[0]
            profile['username'] = data[1]
            profile['avatar'] = data[2]
            profile['gender'] = data[3]
            profile['profession'] = data[4]
            profile['belong'] = data[5]
            profile['register_time'] = data[6].strftime("%Y-%m-%d %H:%M:%S")
        return profile

    @staticmethod
    def get_id_static(username, dbs):
        """get user id from profile file, if not exist, it will
        generate a uuid for the user.
        """
        if username is not None:
            table = dbs.db_obj["user_table"]
            sql = """select user_id, password from {table} 
                      where user_name = '{username}';""".format(table=table, username=username)
            data = dbs.execute(sql=sql)
            return data[0] if data is not None else None
        else:
            return None

    @staticmethod
    def verify_code(username, code, inputTime, dbs):
        id = User.get_id_static(username, dbs)
        if id is not None:
            table = dbs.db_obj['code_table']
            sql = """SELECT sendTime from {table}
                     WHERE user_id = '{id}' and code = '{code}';""".format(table=table, id=id, code=code)
            data = dbs.execute(sql=sql)
            print(data)
            if data is not None:
                sendTime = data[0]
                inputTime = datetime.datetime.strptime(inputTime, '%Y-%m-%d %H:%M:%S')
                if (inputTime-sendTime).seconds > 120:
                    return {'msg': 'expired'}
                else:
                    return {'msg': 'valid'}
            else:
                return {'msg': 'error'}
        else:
            return {'msg': 'not exist'}

    @staticmethod
    def insert_code(username, code, sendTime, dbs):
        id = User.get_id_static(username, dbs)
        table = dbs.db_obj['code_table']
        sql = """insert into {table} (user_id, code, sendTime)
                 VALUES ('{id}', '{code}', '{sendTime}')""".format(table=table, id=id, code=code, sendTime=sendTime)
        dbs.execute(sql=sql, fetch_type=2)


class Building:
    def __init__(self, buidling_info, dbs):
        self.info = buidling_info
        self.dbs = dbs

    @staticmethod
    def getBuildingsOfUser(user_id, dbs):
        table = dbs.db_obj['building_table']
        building_sql = "SELECT * FROM {table} WHERE user_id = '{user_id}';".format(table=table, user_id=user_id)
        data = dbs.execute(building_sql, fetch_type=1)
        if data is None:
            return [], 0
        else:
            building_list = []
            data_cnt = 0
            for i in range(len(data)):
                building_info = dict()
                building_info['building_id'] = data[i][0]
                building_info['data_list'] = BuildingData.getData(building_info['building_id'], dbs)
                data_cnt += len(building_info['data_list'])
                building_info['building_name'] = data[i][2]
                building_info['building_img'] = data[i][3]
                building_info['address'] = "" if data[i][4] is None else data[i][4]
                building_info['building_type'] = "" if data[i][5] is None else data[i][5]
                building_info['area'] = 0.0 if data[i][6] is None else data[i][6]
                building_info['cold_source'] = data[i][7]
                building_info['terminal_type'] = data[i][8]
                building_info['create_time'] = data[i][9].strftime("%Y-%m-%d %H:%M:%S")
                building_list.append(building_info)
            return building_list, data_cnt

    @staticmethod
    def getBuildingInfo(building_id, dbs):
        table = dbs.db_obj['building_table']
        building_sql = "SELECT * FROM {table} WHERE building_id = '{building_id}';".format(table=table,
                                                                                           building_id=building_id)
        data = dbs.execute(building_sql, fetch_type=0)
        binfo = {}
        if data is not None:
            binfo['building_id'] = data[0]
            binfo['building_name'] = data[2]
            binfo['address'] = data[4]
            binfo['area'] = data[6]
            binfo['cold_source'] = data[7]
            binfo['terminal_equipment'] = data[8]
        return binfo

    @staticmethod
    def createBuildingInfo(building_info, dbs):
        table = dbs.db_obj['building_table']
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO {table} (building_id, user_id, building_name, area, address, building_type," \
              "cold_source, terminal_equipment, create_time ) VALUES(" \
              "'{bid}','{uid}','{bname}', {area}, '{addr}', '{btype}', '{cs}','{ty}','{ct}');"\
              .format(table=table, bid=generateUUID(), uid=building_info['user_id'],
                      bname=building_info['building_name'], btype=building_info['building_type'],
                      area=float(building_info['area']), addr=building_info['address'], cs=building_info['cold_source'],
                      ty=building_info['terminal_type'], ct=dt)
        dbs.execute(sql, fetch_type=2)

    @staticmethod
    def modifyBuildingInfo(building_info, dbs):
        table = dbs.db_obj['building_table']
        sql = "UPDATE {table} SET building_name = '{bname}', building_type = '{btype}'," \
              "address = '{addr}', area = {area}, cold_source = '{cs}', terminal_equipment = '{ty}' " \
              "WHERE building_id='{bid}';".format(table=table, bname=building_info['building_name'],
                                                 btype=building_info['building_type'], addr=building_info['address'],
                                                 area=building_info['area'], cs=building_info['cold_source'],
                                                 ty=building_info['terminal_type'], bid=building_info['building_id'])
        dbs.execute(sql, fetch_type=2)

    @staticmethod
    def deleteBuildingInfo(building_info, dbs):
        table = dbs.db_obj['building_table']
        sql = "DELETE FROM {table} WHERE building_id='{bid}';".format(table=table, bid=building_info['building_id'])
        dbs.execute(sql, fetch_type=2)


class BuildingData:
    def __init__(self, building_info):
        self.building_info = building_info

    @staticmethod
    def getData(building_id, dbs):
        table = dbs.db_obj['data_info']
        sql = "SELECT * FROM {table} WHERE building_id = '{building_id}';".format(table=table, building_id=building_id)
        data = dbs.execute(sql, fetch_type=1)
        if data is None:
            return []
        else:
            building_data_list = []
            for i in range(len(data)):
                building_data = dict()
                building_data['case_id'] = data[i][0]
                building_data['building_id'] = data[i][1]
                building_data['data_type'] = data[i][2]
                building_data['has_fix'] = data[i][3]
                building_data['data'] = {} if data[i][4] is None else json.loads(data[i][4])
                building_data['upload_time'] = data[i][5].strftime("%Y-%m-%d %H:%M:%S")
                building_data['has_report'] = data[i][6]
                building_data['report_url'] = data[i][7]
                building_data_list.append(building_data)
            return building_data_list

    @staticmethod
    def insertData(dataInfo, dbs):
        table = dbs.db_obj['data_info']
        tsql = """INSERT INTO {table} (case_id, building_id, data_type, has_fix,
                  data, upload_time) VALUES ('{cid}', '{bid}', {dy}, {hf}, '{data}', '{ut}');"""
        print(dataInfo['data'])
        # 不把单引号替换成双引号的话，插入会出错
        dataStr = json.dumps(dataInfo['data']).replace('\'', '\"')
        print(dataStr)
        sql = tsql.format(table=table, cid=dataInfo['case_id'], bid=dataInfo['building_id'],
                          dy=dataInfo['data_type'], hf=dataInfo['has_fix'],
                          data=dataStr,
                          ut=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        dbs.execute(sql, fetch_type=2)

    @staticmethod
    def deleteData(dataInfo, dbs):
        table = dbs.db_obj['data_info']
        tsql = """DELETE FROM {table} WHERE case_id='{cid}';""".format(table=table, cid=dataInfo['case_id'])
        dbs.execute(tsql, fetch_type=2)

    @staticmethod
    def modifyData(dataInfo, dbs):
        table = dbs.db_obj['data_info']
        tsql = """UPDATE {table} SET generate_report = {hr}, report_addr = '{ru}' 
                WHERE case_id='{cid}';""".format(table=table, cid=dataInfo['case_id'], hr=dataInfo['has_report'],
                                                 ru=dataInfo['report_url'])
        dbs.execute(tsql, fetch_type=2)


if __name__ == "__main__":
    print(generate_password_hash('123456'))
    print(generate_password_hash('123456789'))
    print(generateUUID())


