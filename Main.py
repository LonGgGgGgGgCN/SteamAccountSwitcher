# -*- coding: UTF-8 -*-
# https://github.com/LonGgGgGgGgCN/SteamAccountSwitcher
import steamid_converter as Converter
from time import strftime, localtime
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from sys import argv
from os import system, startfile
from winreg import OpenKey, KEY_ALL_ACCESS, QueryValueEx, HKEY_CURRENT_USER, SetValueEx, REG_SZ, CloseKey, OpenKeyEx
from subprocess import Popen
from ctypes import windll


class Account(object):
    def __init__(self, steamID64, name_account, name_persona, time_stamp):
        self.steamID64 = steamID64
        self.name_account = name_account
        self.name_persona = name_persona
        self.time_stamp = time_stamp
        self.time_last = strftime('%Y-%m-%d %H:%M', localtime(time_stamp))


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 加载界面
        self.ui = loadUi('SteamHelper.ui')
        # 只显示关闭按钮，窗口置顶
        self.ui.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        # 设置图标
        self.ui.setWindowIcon(QIcon('steam.ico'))
        # comboBox
        self.comboBox = self.ui.comboBox  # 账号选择框
        # label
        self.label_name = self.ui.label_name  # 昵称
        self.label_time = self.ui.label_time  # 时间
        # pushButton
        self.pushButton = self.ui.pushButton  # 按钮
        self.pushButton_config = self.ui.pushButton_config  # 设置按钮
        # 获取本地信息
        self.getSteamReg()  # 获取注册表里的内容
        self.getAccount()  # 获取账号
        self.getComboBox()  # 下拉框内容
        self.changeComboBox()  # 改变label显示内容
        # 定义组件的信号/槽
        self.pushButton.clicked.connect(self.loginSteam)  # 打开steam进程
        self.pushButton_config.clicked.connect(self.getUserConfig)  # 打开设置
        self.comboBox.currentIndexChanged.connect(self.changeComboBox)  # 改变label显示内容
        self.comboBox.currentTextChanged.connect(self.inputComboBox)  # 输入文本

    def getUserConfig(self):
        SteamID64 = ''
        # 确定选择的账号
        choice = self.comboBox.currentText()
        for i in self.accounts:
            if i.name_account == choice:
                SteamID64 = i.steamID64
        # 引用steamid_converter api 获取SteamID3
        try:
            SteamID3 = Converter.convert_steamID(SteamID64, 'SteamID3')
            SteamID3 = SteamID3[5:].replace(']', "")
        except ValueError:
            SteamID3 = ''
        # 通过格式化好的steamID3获取到路径并打开文件夹
        path = self.root_path + '\\userdata\\' + SteamID3
        startfile(path)

    # 关闭主程序
    def quitMain(self):
        quit()

    # 输入内容
    def inputComboBox(self):
        self.label_name.setText('正在输入账号')
        self.label_time.setText('账号最后登录时间：????.??.?? ??:??')
        # 确定选择的账号
        choice = self.comboBox.currentText()
        for i in self.accounts:
            if i.name_account == choice:
                self.label_name.setText(i.name_persona)
                self.label_time.setText('账号最后登录时间：' + i.time_last)

    # 获取下拉框内容
    def getComboBox(self):
        comboBoxItems = []  # 创建列表用来储存combobox的内容
        autoUser = ""  # 创建临时变量储存目前登录的账号
        for i in self.accounts:
            if i.name_account == self.user:  # 判断如果为目前的登录账号，就赋值给autoUser
                autoUser = i
            else:
                comboBoxItems.append(i)  # 否则就添加到列表
        comboBoxItems.sort(key=lambda account: account.time_stamp, reverse=True)  # 给列表按account的time_stamp排序
        if type(autoUser).__name__ == 'Account':  # 如果autoUser赋值了Account对象
            comboBoxItems.insert(0, autoUser)  # 就把autoUser插队到列表首位
        for i in comboBoxItems:  # 循环列表
            self.comboBox.addItem(i.name_account)  # 添加到下拉框
            num = comboBoxItems.index(i)  # 获取元素在列表中的索引
            tooltip = str(i.name_persona + '\n' + i.time_last)
            self.comboBox.setItemData(num, tooltip, Qt.ToolTipRole)  # 根据索引添加tooltip

    # 改变label显示内容
    def changeComboBox(self):
        choice = self.comboBox.currentText()
        for i in self.accounts:
            if i.name_account == choice:
                self.label_name.setText(i.name_persona)
                self.label_time.setText('账号最后登录时间：' + i.time_last)

    # 获取steam路径
    def getSteamReg(self):
        key = OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Valve\Steam')
        self.root_path = QueryValueEx(key, "SteamPath")[0]
        self.exe_path = QueryValueEx(key, "SteamExe")[0]
        self.vdf_path = self.root_path + '/config/loginusers.vdf'
        self.user = QueryValueEx(key, "AutoLoginUser")[0]
        CloseKey(key)

    # 登录
    def loginSteam(self):
        key = OpenKeyEx(HKEY_CURRENT_USER, r'SOFTWARE\Valve\Steam', access=KEY_ALL_ACCESS)
        SetValueEx(key, "AutoLoginUser", 0, REG_SZ, self.comboBox.currentText())
        CloseKey(key)
        system('killSteam.bat')  # 关闭后台的steam
        Popen(r"{}".format(self.exe_path))  # 打开steam
        self.quitMain()

    # 获取vdf里面的账号信息
    def getAccount(self):
        # 入读文件
        try:
            with open(self.vdf_path, encoding='utf-8') as f:
                content = f.readlines()
        except FileNotFoundError:
            self.accounts = []
            account = Account(1024, 'steam登录文件缺失', '请检查steam/config/loginusers.vdf', 0000000000)
            self.accounts.append(account)
        else:
            # 删除多余内容
            del content[0:2]
            del content[-1]
            users = []
            self.accounts = []
            for i in range(0, len(content), 11):  # 分割内容的列表
                users.append(content[i:i + 11])  # 每11行为一个新列表 添加到users里面
            for i in users:  # 获取列表中需要的信息
                steamID64 = i[0].replace('\t', '').replace('\"', '').replace('\n', '')
                AccountName = i[2].replace('\t', '').replace('\"', '')[11:].replace('\n', '')
                PersonaName = i[3].replace('\t', '').replace('\"', '')[11:].replace('\n', '')
                Timestamp = i[9].replace('\t', '').replace('\"', '')[9:].replace('\n', '')
                account = Account(steamID64, AccountName, PersonaName, int(Timestamp))  # 实例化对象Account
                self.accounts.append(account)  # 列表保存刚刚实例化的对象


def main():
    # 创建qt对象
    app = QApplication(argv)
    # 创建页面对象加载ui文件
    window = Window()
    # 判断是否管理员模式运行
    if not windll.shell32.IsUserAnAdmin():
        error = QMessageBox(QMessageBox.Critical, ' 请以管理员模式运行！！！！', '1、右键exe文件(或快捷方式)\n2、属性\n3、兼容性\n4、√以管理员身份运行此程序')
        error.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        error.setWindowIcon(QIcon('steam.ico'))
        error.exec_()
    else:
        # 展示窗口
        window.ui.show()
        # 设置标题
        window.ui.setWindowTitle('Steam账号切换器_v1.1.2')
        # 程序循环等待操作
        app.exec_()


# if __name__ == '__main__':
#     # 创建qt对象
#     app = QApplication(argv)
#     # 创建页面对象加载ui文件
#     window = Window()
#     window.ui.setWindowTitle('开发者模式！！！测试使用！！！')
#     # 展示窗口
#     window.ui.show()
#     # 程序循环等待操作
#     app.exec_()
# pyinstaller -F -w -i steam.ico --clean --version-file version_info.txt Main.py


main()
