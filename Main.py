# -*- coding: UTF-8 -*-
# https://github.com/LonGgGgGgGgCN/SteamAccountSwitcher
import steamid_converter as Converter
from time import strftime, localtime, sleep
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor
from sys import argv, exit
from os import startfile, listdir
from webbrowser import open as webopen
from winreg import OpenKey, KEY_ALL_ACCESS, QueryValueEx, HKEY_CURRENT_USER, SetValueEx, REG_SZ, CloseKey, OpenKeyEx
from ctypes import windll
from subprocess import Popen
import SteamAS_rcc  # 修改了qrc资源文件需要把qrc文件重新打包为py文件


# 账号类 用来储存账号的各种属性
class Account(object):
    def __init__(self, steamID64, name_account, name_persona, time_stamp):
        self.steamID64 = steamID64  # steamid64
        self.name_account = name_account  # 登录账号
        self.name_persona = name_persona  # 账号昵称
        self.time_stamp = time_stamp  # 最后登录时间的时间戳
        self.time_last = strftime('%Y-%m-%d %H:%M', localtime(time_stamp))  # 格式化时间戳


# 窗口类 主窗口所在的类
class Window(QMainWindow):
    _startPos = None
    _endPos = None
    _isTracking = False

    def __init__(self):
        super(Window, self).__init__()
        self.init_ui()
        self.m_flag = False

    def init_ui(self):
        # 加载界面
        self.ui = loadUi('SteamAS.ui', self)
        # 设置无边框窗口，窗口置顶
        self.ui.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 设置背景透明
        self.ui.setAttribute(Qt.WA_TranslucentBackground)  # 不设置这个的话 窗口的圆角后面会有背景
        # comboBox
        self.comboBox = self.ui.comboBox  # 账号选择框
        # label
        self.label_name = self.ui.label_name  # 昵称
        self.label_time = self.ui.label_time  # 时间
        # pushButton
        self.pushButton_login = self.ui.pushButton_login  # 按钮
        self.pushButton_config = self.ui.pushButton_config  # 设置按钮
        self.pushButton_title = self.ui.pushButton_title  # 标题按钮
        self.pushButton_By = self.ui.pushButton_By  # 署名
        self.pushButton_quit = self.ui.pushButton_quit  # 退出
        # 定义组件的信号/槽
        self.pushButton_login.clicked.connect(self.loginSteam)  # 登录按钮点击触发loginSteam方法
        self.pushButton_config.clicked.connect(self.getUserConfig)  # 打开设置按钮点击触发getUserConfig
        self.comboBox.currentIndexChanged.connect(self.changeComboBox)  # 当combobox选项索引改变时执行changecombobox
        self.comboBox.currentTextChanged.connect(self.inputComboBox)  # 当combobox输入框改变时执行inputComboBox
        self.pushButton_By.clicked.connect(self.openGithub)  # 点击右下角署名执行openGithub
        self.pushButton_title.clicked.connect(self.openGithub)  # 点击左上角标题图标执行openGithub
        self.pushButton_quit.clicked.connect(self.quitMain)  # 右上角退出按钮执行quitMain
        # 组件变形、设置
        self.pushButton_login.pressed.connect(self.deformation_pushButton1)  # 当登录按钮按下时触发deformation_pushButton1
        self.pushButton_login.released.connect(self.deformation_pushButton2)  # 当登录按钮松开时触发deformation_pushButton2

    # 鼠标按下
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    # 鼠标移动
    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()
        print(self.m_Position)

    # 鼠标松开
    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    # 打开github网页
    def openGithub(self):
        # 打开url
        webopen('https://github.com/LonGgGgGgGgCN/SteamAccountSwitcher')

    # 改变pushButton_login的样式
    def deformation_pushButton1(self):
        # 设置background的图片和边框的图片
        self.pushButton_login.setStyleSheet('background-image: url(:/background/login_btn2.png);\n'
                                            'border-image: url(:/background/login_btn2.png);\n')

    # 改变pushButton_login的样式
    def deformation_pushButton2(self):
        # 设置background的图片和边框的图片
        self.pushButton_login.setStyleSheet('background-image: url(:/background/login_btn.png);\n'
                                            'border-image: url(:/background/login_btn.png);\n')

    # 打开所选择账号的设置文件夹
    def getUserConfig(self):
        SteamID64 = ''  # 创建空的steamid64变量
        # 确定选择的账号
        choice = self.comboBox.currentText()  # 获取combobox上的内容
        for i in self.accounts:  # 遍历账号列表
            if i.name_account == choice:  # 判断账号是否为选择的内容
                SteamID64 = i.steamID64  # 如果是就传入steamid64
        # 引用steamid_converter api 获取SteamID3
        try:
            SteamID3 = Converter.convert_steamID(SteamID64, 'SteamID3')  # 得到steamid3
            SteamID3 = SteamID3[5:].replace(']', "")  # 格式化steamid3
        except ValueError:  # 如果报错代表steamid64是错误的
            SteamID3 = ''
        path = self.root_path + '\\userdata\\' + SteamID3  # 通过格式化好的steamID3获取到路径
        startfile(path)  # 打开文件夹

    # 关闭主程序
    def quitMain(self):
        sleep(0.5)  # 添加延迟
        exit()  # 退出

    # 输入内容修改label的内容
    def inputComboBox(self):
        self.label_name.setText('正在输入账号')
        self.label_time.setText('账号最后登录时间：????.??.?? ??:??')
        # 确定选择的账号
        choice = self.comboBox.currentText()
        for i in self.accounts:  # 通过遍历账号列表 获取选择的账号名字和最后登录时间
            if i.name_account == choice:  # 判断账号是否为选择的账号
                self.label_name.setText(i.name_persona)  # 设置label的文本
                self.label_time.setText('账号最后登录时间：' + i.time_last)  # 设置label的文本

    # 从loginuser文件中获取下拉框items和tooltips，从avatarcache文件夹中获取items对应的icon
    def getComboBox(self):
        self.comboBox.clear()  # 清除combobox中的内容
        self.avatar_path = self.root_path + '/config/avatarcache/'  # 获取头像地址
        self.filenames = listdir(self.avatar_path)  # 获取头像文件列表
        comboBoxItems = []  # 创建列表用来储存combobox的内容
        autoUser = ""  # 创建临时变量储存目前登录的账号
        for i in self.accounts:  # 遍历账号列表
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
            tooltip = str(i.name_persona + '\n' + i.time_last)  # 格式化tooltip
            self.comboBox.setItemData(num, tooltip, Qt.ToolTipRole)  # 根据索引添加tooltip
            for j in self.filenames:  # 循环列表filenames用来添加items的icon
                if j[0:-4] == i.steamID64:  # 如果filenames中有相应的steamid就添加icon
                    self.comboBox.setItemIcon(num, QIcon(self.avatar_path + j))  # 设置icon
        self.comboBox.addItem('-----------手动输入其他账号-----------')

    # 选择选项改变label显示内容
    def changeComboBox(self):
        # 判断是否选择最后一个选项
        if self.comboBox.currentIndex() == len(self.accounts):
            # 如果是 则打开输入框的编辑权限
            self.comboBox.setEditable(True)
            # 并设置combobox的stylesheet
            self.comboBox.setStyleSheet('background-color:rgb(50, 53, 60);\n'
                                        'color:rgb(175,175,175);\n'
                                        'background-image:url()\n')
        # 确定选择的账号
        choice = self.comboBox.currentText()
        for i in self.accounts:  # 通过遍历账号列表 获取选择的账号名字和最后登录时间
            if i.name_account == choice:  # 判断账号是否为选择的账号
                self.label_name.setText(i.name_persona)  # 设置label的文本
                self.label_time.setText('账号最后登录时间：' + i.time_last)  # 设置label的文本

    # 获取steam路径
    def getSteamReg(self):
        key = OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Valve\Steam')  # steam在reg里面的路径
        self.root_path = QueryValueEx(key, "SteamPath")[0]  # steam文件夹路径
        self.exe_path = QueryValueEx(key, "SteamExe")[0]  # steam启动程序.exe路径
        self.vdf_path = self.root_path + '/config/loginusers.vdf'  # loginusers.vdf文件路径
        self.user = QueryValueEx(key, "AutoLoginUser")[0]  # 自动登录的steam账号
        CloseKey(key)  # 关闭与注册表的链接

    # 修改注册表+关闭steam程序并打开steam+关闭本程序
    def loginSteam(self):
        key = OpenKeyEx(HKEY_CURRENT_USER, r'SOFTWARE\Valve\Steam', access=KEY_ALL_ACCESS)  # 打开注册表
        SetValueEx(key, "AutoLoginUser", 0, REG_SZ, self.comboBox.currentText())  # 修改注册表的autologinuser为输入框的文本
        CloseKey(key)  # 关闭注册表
        Popen(r'taskkill /f /im steam.exe')  # 关闭steam程序
        Popen(r"taskkill /f /im SteamService.exe")  # 关闭steam服务
        sleep(0.5)  # 添加延迟 操作太快会使得没关闭steam就打开了
        Popen(r"{}".format(self.exe_path))  # 打开steam
        self.quitMain()  # 关闭此程序

    # 获取vdf里面的账号信息
    def getAccount(self):
        # 入读文件
        try:
            with open(self.vdf_path, encoding='utf-8') as f:  # 打开loginusers.vdf文件
                content = f.readlines()  # 获取文件的内容 type:list
        except FileNotFoundError:  # 如果没有找到文件
            self.accounts = []  # 列表清空
            # 添加报错的账号对象
            account = Account(1024, 'steam登录文件缺失', '请检查steam/config/loginusers.vdf', 0000000000)
            self.accounts.append(account)  # 将报错对象 添加到账号列表中
        else:  # 如果找到了文件
            # 删除多余内容
            del content[0:2]  # 删除前0,1,2行内容
            del content[-1]  # 删除最后一行内容
            users = []  # 创建列表临时保存文件内容
            self.accounts = []  # 创建账号列表
            for i in range(0, len(content), 11):  # 分割内容的列表
                users.append(content[i:i + 11])  # 每11行为一个新列表 添加到users里面
            for i in users:  # 获取列表中需要的信息
                # 格式化内容
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
    # 设置标题
    window.setWindowTitle('Steam账号切换器_v1.1.3')
    # 判断是否管理员模式运行
    if not windll.shell32.IsUserAnAdmin():
        error = QMessageBox(QMessageBox.Critical, ' 请以管理员模式运行！！！！', '1、右键exe文件(或快捷方式)\n2、属性\n3、兼容性\n4、√以管理员身份运行此程序')
        error.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        error.setWindowIcon(QIcon('steam.ico'))
        error.exec_()
    else:
        # 展示窗口
        window.show()
        # 获取本地信息
        window.getSteamReg()  # 获取注册表里的内容
        window.getAccount()  # 获取账号
        window.getComboBox()  # 下拉框内容
        window.changeComboBox()  # 改变label显示内容
        # 程序循环等待操作
        app.exec_()


#
# if __name__ == '__main__':
#     # 创建qt对象
#     app = QApplication(argv)
#     # 创建页面对象加载ui文件
#     window = Window()
#     # 设置标题
#     window.setWindowTitle('开发者模式！！！测试使用！！！')
#     # 展示窗口
#     window.show()
#     # 获取本地信息
#     window.getSteamReg()  # 获取注册表里的内容
#     window.getAccount()  # 获取账号
#     window.getComboBox()  # 下拉框内容
#     window.changeComboBox()  # 改变label显示内容
#     # 程序循环等待操作
#     app.exec_()

# 打包指令
# pyinstaller -F -w -i steam.ico --clean --version-file version_info.txt Main.py
# 编译qrc资源文件为py文件
# pyrcc5 SteamAS_rcc.qrc -o SteamAS_rcc.py
# 编译ui文件为py文件
# pyuic5 SteamAS.ui -o SteamAS_uic.py


main()
