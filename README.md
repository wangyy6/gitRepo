# gitRepo
## 1.开发环境
###  pycharm：python3
###  SQL:SQLite3
## 2.项目简介
###  本工具是基于python开发的对xcode工程代码进行混淆的工具，包括对.h、.m文件名和文件引用代码进行混淆，混淆方式如下：
 （1）混淆方式为字符串转换成加盐MD5值
 
 （2）记录字符串和MD5的混淆映射关系
 
 （3）可以通过映射表，对混淆后的工程还原
 ## 3.使用方法
 ### 代码下载后将mix_xcode_one.py文件放入需要混淆的xcode工程文件夹内，然后运行工具混淆代码
