#!/usr/bin/env python
# coding: utf-8
import sqlite3
import csv
from os import listdir
import tracebackdef create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except BaseException:
        traceback.print_exc()
        
    return Nonedef create_table(c, sql):
        try:
            c.execute(sql)
        except BaseException:
            traceback.print_exc()def insert_table(c, sql, data):
        try:
            c.execute(sql, data)
        except BaseException:
            traceback.print_exc()def insert_date(date):
        temp = date.split('/')
        insert_date = temp[0]
        if len(temp[1]) < 2:
            insert_date += '-0' + temp[1]
        else:
            insert_date += '-' + temp[1]
        if len(temp[2]) < 2:
            insert_date += '-0' + temp[2]
        else:
            insert_date += '-' + temp[2]
        return insert_datedef check_space(row):
    for i in range(8):
        if row[i] == '':
            return False
    return Truedef csv_to_db(file):
    with open(file, newline='') as csvfile:
        rows = csv.reader(csvfile)
        for i,row in enumerate(rows):
            if i != 0 and row[2] != '':
                sql = "INSERT INTO price VALUES (?,?,?)"
                row[2] = row[2].split(',')
                row[2] = ''.join(row[2])
                data = [row[0],insert_date(row[1]), row[2]]
                insert_table(c, sql,data)

            if i != 0 and row[-1] != '':
                sql = "INSERT INTO interest VALUES (?,?,?)"
                data = [row[0],insert_date(row[1]), row[-1]]
                insert_table(c, sql,data)conn = create_connection("fund.db")
c = conn.cursor()c.execute('''PRAGMA foreign_keys = ON;''')c.execute('''CREATE TABLE basic_information(
id TEXT NOT NULL,
full_name TEXT NOT NULL,
ISIN_code TEXT NOT NULL,
entry_day TEXT NOT NULL,
type TEXT NOT NULL,
manager_fee REAL NOT NULL,
custody_fee REAL NOT NULL,
sales_fee REAL NOT NULL,
area TEXT NOT NULL,
PRIMARY KEY(id)
);''')c.execute('''CREATE TABLE price(
id TEXT NOT NULL,
date TEXT NOT NULL,
NAV REAL NOT NULL,
PRIMARY KEY(id,date)
FOREIGN KEY(id) REFERENCES basic_information(id)
);''')c.execute('''CREATE TABLE interest(
id TEXT NOT NULL,
date TEXT NOT NULL,
interest REAL NOT NULL,
PRIMARY KEY(id,date)
FOREIGN KEY(id) REFERENCES basic_information(id)
);''')with open('境內基本資料 utf8.csv', newline='') as csvfile:
    
    rows = csv.reader(csvfile)
    for i,row in enumerate(rows):
        if i == 0 or row[-1] !='' or check_space(row) == False:
            continue
        sql = "INSERT INTO basic_information VALUES(?,?,?,?,?,?,?,?,?)"
        data = row[0:8]
        data.append('境內')
        insert_table(c, sql, data)with open('境外基本資料 utf8.csv', newline='') as csvfile:
    
    rows = csv.reader(csvfile)
    for i,row in enumerate(rows):
        if i == 0 or row[-1] !='' or check_space(row) == False:
            continue
        sql = "INSERT INTO basic_information VALUES(?,?,?,?,?,?,?,?,?)"
        data = row[0:8]
        data.append('境外')
        insert_table(c, sql, data)my_path = '/home/xiangli/文件/programming/DB/境內 utf8'
files = listdir(my_path)for i,file in enumerate(files):
    files[i] = my_path + '/' + filefor file in files:
    csv_to_db(file)
conn.commit()my_path = '/home/xiangli/文件/programming/DB/境外 utf8'
files = listdir(my_path)for i,file in enumerate(files):
    files[i] = my_path + '/' + filefor file in files:
    csv_to_db(file)
conn.commit()conn.commit()
conn.close()