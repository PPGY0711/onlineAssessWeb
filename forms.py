#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@objective: define form schemas used in the project
@author: pengguanyan
@update date: 2022/01/09
"""
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, FloatField, FileField
from wtforms.validators import DataRequired


# 登录表单
class LoginForm(FlaskForm):
    # 域初始化时，第一个参数是设置label属性的
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember me', default=False)


# 注册表单
class RegisterForm(FlaskForm):
    # 域初始化时，第一个参数是设置label属性的
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeatPassword = PasswordField('Password', validators=[DataRequired()])


# 个人资料表单
class personModifyForm(FlaskForm):
    # 域初始化时，第一个参数是设置label属性的
    user_id = StringField('User Id', validators=[DataRequired()])
    username = StringField('User Name', validators=[DataRequired()])
    register_time = StringField('Register Time', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    profession = StringField('profession')
    workplace = StringField('workplace')


# 建筑信息表单
class buildingForm(FlaskForm):
    user_id = StringField('User Id')
    building_id = StringField('Building Id', validators=[DataRequired()])
    building_name = StringField('Building Name', validators=[DataRequired()])
    address = StringField('Address')
    area = FloatField('Area', validators=[DataRequired()])
    building_type = StringField('Building Type')
    cold_source = StringField('Cold Source', validators=[DataRequired()])
    terminal_type = StringField('Terminal Type', validators=[DataRequired()])


# 建筑信息表单
class buildingSimpleForm(FlaskForm):
    building_id = StringField('Building Id', validators=[DataRequired()])
    building_name = StringField('Building Name', validators=[DataRequired()])


class dataForm(FlaskForm):
    building_id = StringField('Building Id', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    FileName = StringField('File Name', validators=[DataRequired()])
    FileId = StringField('File Id', validators=[DataRequired()])


class dataDeleteForm(FlaskForm):
    building_id = StringField('Building Id', validators=[DataRequired()])
    building_name = StringField('Building Name', validators=[DataRequired()])
    case_id = StringField('Case Id', validators=[DataRequired()])
    data_type = StringField('Data Type', validators=[DataRequired()])