'''
-*- coding:utf-8 -*-
@File   : mix_xcode_one.py
@author : wyy
@Time   : 2022/11/02 09:49
'''

import os
import hashlib
import re
import numpy as np
import sqlite3
from sqlite3 import Error

# 自动获取工程文件路径
def get_xcodePath():
    global meariPath
    global xcodeprojPath
    for i in os.listdir(os.getcwd()):
        if os.path.splitext(i)[1] == ".xcodeproj":
            xcodeprojPath = os.getcwd() + "/" + i + "/project.pbxproj"
            print(f"xcodeprojPath路径为：{xcodeprojPath}")
            if os.path.exists(os.getcwd() + "/" + os.path.splitext(i)[0]) == True:
                meariPath = os.getcwd() + "/" + os.path.splitext(i)[0]
                print(f"meariPath路径为：{meariPath}")
            else:
                print("未找到meariPath路径")
        else:
            print("未找到xcodeprojPath路径")

# 文件做递归， 拿到有用的.h, .m 文件
def get_filePath():
    path1 = []
    global tempList
    tempList = []
    try:
        for i in os.listdir(meariPath):
            tempPath1 = meariPath + "/" + i
            if "." not in os.path.splitext(i)[0] and "SDK" not in os.path.splitext(i)[0] or "pch" in os.path.splitext(i)[0]:
                path1.append(tempPath1)
        # print(path1)
        return path1
    except Exception as err:
        print(f"err:{err}")

def findLastFilePathList(file: list):
    for i in file:
        # print(i)
        if os.path.isfile(i):
            if ".h" == os.path.splitext(i)[1] or ".m" == os.path.splitext(i)[1] or ".xib" == os.path.splitext(i)[1]:
                # or ".xib" == os.path.splitext(i)[1] or ".pch" == os.path.splitext(i)[1]
                tempList.append(i)
        else:
            tempPath = []
            for j in os.listdir(i):
                tempPath.append(i + "/" + j)
            findLastFilePathList(tempPath)

# 提取文件名，放入列表
def fileNameList():
    classNameList = []
    for i in tempList:
        className = i.split("/")[-1].split(".")[0]
        classNameList.append(className)
    # print(classNameList)
    classNameList = list(set(classNameList))
    classNameList.sort(key=lambda i: len(i), reverse=True)
    classNameList.remove("ViewController")
    classNameList.remove("main")
    # print(classNameList)
    return classNameList

# 正则函数提取函数名
def func_name_get():
    func_name = []
    for i in tempList:
        with open(i, "r") as file:
            str1 = file.read()
            pattern1 = re.compile(
                r'(\)+[ a-zA-Z_0-9]+[:;{])')
            m = pattern1.findall(str1)
            # print(m)
            list1 = ''
            for i in np.array(m):
                if len(i) > 4:
                    # print(i)
                    list1 = list1 + str(i)
                    list1 += '\n'
                for t in list1:
                    if t == ")" or t == "{" or t == ";" or t == ":":
                        list1 = list1.replace(t, "")
            string = ""
            t = string.join(list1)
            x = t.splitlines()
            func_name.extend(x)
    # print(func_name)
    # 整理函数名并放入列表中
    list_new = []
    for i in func_name:
        i = i.strip()
        # print(i)
        if i.find(" "):
            i = i.split(" ")[-1]
            # print(i)
            if len(i) != 0:
                list_new.append(i)
    # print(list_new)
    list_new1 = list(set(list_new))               # 列表去重
    list_new1.sort(key=lambda i: len(i), reverse=True)  # 列表按照字符从大到小排序
    ignore_sqlList = ['request', 'data', 'viewDidLoad', 'prefersStatusBarHidden', 'viewSafeAreaInsetsDidChange',
                      'preferredScreenEdgesDeferringSystemGestures', 'supportedInterfaceOrientations',
                      'shouldAutorotate', 'preferredStatusBarStyle', 'webView', 'decidePolicyForNavigationAction',
                      'decisionHandler', 'didFailNavigation', 'withError', 'webViewWebContentProcessDidTerminate',
                      'didFinishLaunchingWithOptions', 'application', 'load', 'set', 'forKey', 'del', 'count',
                      'objectForKey', 'Zone', 'removeObjectForKey', 'back', 'withObject', 'userContentController',
                      'obj', 'self', 'error', 'source', 'cachedSource', 'result', 'type', 'defaultName', 'popCode',
                      'key', 'block', 'string', 'gameType', 'level', 'flag', 'sender', 'number', 'index', 'dataArr',
                      'tile', 'playModel', 'message', 'rect', 'url', 'forControlEvents', 'button', 'R_handler', 'dict',
                      'object', 'fillType', 'index', 'scrollAbled', 'right', 'current', 'acc']
    for i in ignore_sqlList:
        # print(i)
        if i in list_new1:
            list_new1.remove(i)
    return list_new1
    # print(list_new1)

# 连接数据库
def sql_connection():
    try:
        con = sqlite3.connect('databases_mix.db')
        return con
    except Error:
        print(Error)
def sql_table():
    con = sql_connection()
    cursorObj = con.cursor()
    cursorObj.execute(
        "CREATE TABLE IF NOT EXISTS class(Classname, Password, PRIMARY KEY(Classname, Password))")          # 创建数据库表，存入文件名，执行后注释
    cursorObj.execute(
        "CREATE TABLE IF NOT EXISTS function(Class_name, Password, PRIMARY KEY(Class_name, Password))")        # 创建数据库表，存入函数名，执行后注释
    con.commit()

# md5值加盐
def creat_salt():
    salt = 'cdhflsfveudsfshdksrthyhfhtyue'
    return salt
def create_md5(pwd, salt):
    md5_obj = hashlib.md5()
    md5_obj.update((pwd+salt).encode('utf-8'))
    return 'xxy' + md5_obj.hexdigest()

# 将文件名导入数据库
def import_class():
    con = sql_connection()
    classNameList = fileNameList()
    for i in classNameList:
        salt = creat_salt()
    #   加密后的密码
        md5_pwd = create_md5(i, salt)
        cursorObj = con.cursor()
        cursorObj.execute(
            'INSERT OR REPLACE INTO class(Classname, Password) VALUES(?, ?)', (i, md5_pwd))
        con.commit()
    # print(f"函数名为：{i},对应的md5值为：{md5_pwd}")

# 将函数名导入数据库
def import_func():
    list_new1 = func_name_get()
    con = sql_connection()
    for i in list_new1:
        salt = creat_salt()
        md5_pwd = create_md5(i, salt)
        cursorObj = con.cursor()
        cursorObj.execute(
            'INSERT OR REPLACE INTO function(Class_name, Password) VALUES(?, ?)', (i, md5_pwd))
        con.commit()
    # print(f"函数名为：{i},对应的md5值为：{md5_pwd}")

# 定义混淆函数名
def func_e():
    list_new1 = func_name_get()
    con = sql_connection()
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT Class_name, Password FROM function")
    for row in cursorObj:
        oldKey1 = row[0]
        newKey1 = row[1]
        for i in tempList:
            try:
                with open(i, "r") as file:
                    str1 = file.read()
                with open(i, "w") as file:
                    for name in list_new1:
                        newName = name.replace(oldKey1, newKey1)  # 混淆str1.replace(name, newName)
                        str1 = str1.replace(name, newName)      # 还原str1.replace(newName, name)
                    file.write(str1)
            except Exception as err:
                print(f"err1{err}")

# # 定义混淆文件内的类名
def class_e():
    classNameList = fileNameList()
    con = sql_connection()
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT Classname, Password FROM class")
    for row in cursorObj:
        oldKey2 = row[0]
        newKey2 = row[1]
        for i in tempList:
            # 混淆文件内的类名
            try:
                with open(i, "r") as file:
                    str1 = file.read()
                with open(i, "w") as file:
                    for name in classNameList:
                        newName = name.replace(oldKey2, newKey2)  # 混淆str1.replace(name, newName)
                        str1 = str1.replace(name, newName)      # 还原str1.replace(newName, name)
                    file.write(str1)
            except Exception as err:
                print(f"err2{err}")

# 定义混淆 .m .h .xib文件名
def doc_e():
    con = sql_connection()
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT Classname, Password FROM class")
    for row in cursorObj:
        # global oldKey
        # global newKey
        oldKey = row[0]
        newKey = row[1]
        for i in tempList:
            try:
                oriName = os.path.splitext(i)[0].split("/")[-1]
                changeName = oriName.replace(newKey, oldKey)
                changeName1 = oriName.replace(oldKey, newKey)          # 混淆fileName = changeName1 + os.path.splitext(i)[1]
                fileName = changeName1 + os.path.splitext(i)[1]        # 还原fileName = changeName + os.path.splitext(i)[1]
                os.rename(i, os.path.dirname(i) + "/" + fileName)
            except Exception as err1:
                print(f"err3{err1}")

    # 混淆工程引用
            with open(xcodeprojPath, "r") as file:
                str1 = file.read()
            with open(xcodeprojPath, "w") as file:                    # 混淆str1.replace(oriName, changeName1)
                str2 = str1.replace(oriName, changeName1)           # 还原str1.replace(changeName1, changeName)
                file.write(str2)

# 定义还原函数名
def func_m():
    list_new1 = func_name_get()
    con = sql_connection()
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT Class_name, Password FROM function")
    for row in cursorObj:
        oldKey1 = row[0]
        newKey1 = row[1]
        for i in tempList:
            try:
                with open(i, "r") as file:
                    str1 = file.read()
                with open(i, "w") as file:
                    for name in list_new1:
                        newName = name.replace(oldKey1, newKey1)  # 混淆str1.replace(name, newName)
                        nameNew = name.replace(newKey1, oldKey1)
                        str1 = str1.replace(newName, nameNew)      # 还原str1.replace(newName, name)
                    file.write(str1)
            except Exception as err:
                print(f"err1{err}")

# # 定义还原文件内的类名
def class_m():
    classNameList = fileNameList()
    con = sql_connection()
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT Classname, Password FROM class")
    for row in cursorObj:
        oldKey2 = row[0]
        newKey2 = row[1]
        for i in tempList:
            # 还原文件内的类名
            try:
                with open(i, "r") as file:
                    str1 = file.read()
                with open(i, "w") as file:
                    for name in classNameList:
                        newName = name.replace(oldKey2, newKey2)  # 混淆str1.replace(name, newName)
                        nameNew = name.replace(newKey2, oldKey2)
                        str1 = str1.replace(newName, nameNew)      # 还原str1.replace(newName, name)
                    file.write(str1)
            except Exception as err:
                print(f"err2{err}")

# 定义还原 .m .h .xib文件名
def doc_m():
    con = sql_connection()
    cursorObj = con.cursor()
    cursorObj.execute(
        "SELECT Classname, Password FROM class")
    for row in cursorObj:
        # global oldKey
        # global newKey
        oldKey = row[0]
        newKey = row[1]
        for i in tempList:
            try:
                oriName = os.path.splitext(i)[0].split("/")[-1]
                changeName = oriName.replace(newKey, oldKey)
                changeName1 = oriName.replace(oldKey, newKey)          # 混淆fileName = changeName1 + os.path.splitext(i)[1]
                fileName = changeName + os.path.splitext(i)[1]        # 还原fileName = changeName + os.path.splitext(i)[1]
                os.rename(i, os.path.dirname(i) + "/" + fileName)
            except Exception as err1:
                print(f"err3{err1}")

    # 还原工程引用
            with open(xcodeprojPath, "r") as file:
                str1 = file.read()
            with open(xcodeprojPath, "w") as file:                    # 混淆str1.replace(oriName, changeName1)
                str2 = str1.replace(changeName1, changeName)           # 还原str1.replace(changeName1, changeName)
                file.write(str2)

def main():
    get_xcodePath()
    get_filePath()
    path1 = get_filePath()
    findLastFilePathList(path1)
    fileNameList()
    func_name_get()
    sql_table()

def main():
    get_xcodePath()
    get_filePath()
    try:
        path1 = get_filePath()
        findLastFilePathList(path1)
        fileNameList()
        func_name_get()
        sql_table()
    except Exception as err1:
        print(f"err4{err1},未找到工程路径")
        return False

if __name__ == '__main__':
    main()
# 混淆工程调用
    if main() is not False:
        print("start mix")
        import_func()
        import_class()
        func_e()
        class_e()
        doc_e()
        # 如果还原，在运行框输入1回车
        guest = int(input("如果要对程序还原请输入：1"))
        if guest == 1:
            print("reverse mix")
            main()
            func_m()
            class_m()
            doc_m()




