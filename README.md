# Steam账号切换器

读取本地已登录过的steam账号 实现免密登录\
下载地址:
https://github.com/LonGgGgGgGgCN/SteamAccountSwitcher/releases


## 概述

读取steam存储账号信息的文件```*\Steam\config\loginusers.vdf```作为登录账号的选项\
此代码提供这些账号的登录 若三个月以内在本地登陆并记住密码过选择的账号 则可以实现该账号的免密(令牌)登录

使用软件需要通过电脑的管理员模式打开 这是因为关闭或打开steam.exe程序不以管理员模式运行会出现意外的错误\
仅仅测试win10、win11的系统 由于开发python的版本为3.9.7 某些不支持的系统可能会出现无法运行打包好的exe文件的错误(暂没想法更换python版本)


## 功能

免密(令牌)登录在本地记住密码并成功登录过的steam账号\
点击ui上的登录按钮后，自动关闭已启动的steam程序

更新日志请查看changelog.log

## 声明

此程序来自 [LonGgGgGgGg](https://github.com/LonGgGgGgGgCN)

Steam是Valve公司的版权，Valve公司与本软件及其作者无关，本软件不涉及任何破解Steam账号或密码的功能
