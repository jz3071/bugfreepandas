# -*- coding: utf-8 -*-
# @Time    : 2019/11/8 15:41
# @Author  : Yunjie Cao
# @FileName: test_verfication.py
# @Software: PyCharm
# @Email   ：YunjieCao@hotmail.com


import pymysql

def select_user():
    c_info = {
        'host': 'sedatabase.ccrfnreg6ro1.us-east-1.rds.amazonaws.com',
        'user': 'yangli',
        'password': 'columbialiyang',
        'port': 3306,
        'db': 'e6156'
    }

    db_connection = pymysql.connect(
        host=c_info['host'],
        user=c_info['user'],
        password=c_info['password'],
        port=c_info['port'],
        db=c_info['db'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = db_connection.cursor()
    res = cur.execute('SELECT * FROM e6156.users')
    data = cur.fetchall()
    print(data)


if __name__ == "__main__":
    select_user()