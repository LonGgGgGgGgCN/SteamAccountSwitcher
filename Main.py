# -*- coding: UTF-8 -*-
# https://github.com/LonGgGgGgGgCN/SteamAccountSwitcher
import steamid_converter as Converter
from time import strftime, localtime, sleep
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QInputDialog
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


# 输入窗口类 弹窗输入窗口的类
class InputWindow(QInputDialog):
    def __init__(self, window):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setTextValue('备注')
        self.setWindowTitle('Rename')
        self.setLabelText('账号')
        self.setModal(True)
        self.show()


# 账号类 用来储存账号的各种属性
class Account(object):
    def __init__(self, steamID64, name_account, name_persona, time_stamp):
        self.steamID64 = steamID64  # steamid64
        self.name_account = name_account  # 登录账号
        self.name_persona = name_persona  # 账号昵称
        self.time_stamp = time_stamp  # 最后登录时间的时间戳
        self.time_last = strftime('%Y-%m-%d %H:%M', localtime(time_stamp))  # 格式化时间戳
        self.name_mark = ''


# 窗口类 主窗口所在的类
class Window(QMainWindow):
    _startPos = None
    _endPos = None
    _isTracking = False

    def __init__(self):
        super(Window, self).__init__()
        self.init_ui()
        self.m_flag = False
        self.cfg_path = 'rename.ini'

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
        self.pushButton_markname = self.ui.pushButton_markname  # 备注按钮
        # 定义组件的信号/槽
        self.pushButton_login.clicked.connect(self.loginSteam)  # 登录按钮点击触发loginSteam方法
        self.pushButton_config.clicked.connect(self.getUserConfig)  # 打开设置按钮点击触发getUserConfig
        self.comboBox.currentTextChanged.connect(self.inputComboBox)  # 当combobox输入框改变时执行inputComboBox
        self.comboBox.currentIndexChanged.connect(self.changeComboBox)  # 当combobox选项索引改变时执行changecombobox
        self.pushButton_By.clicked.connect(self.openGithub)  # 点击右下角署名执行openGithub
        self.pushButton_title.clicked.connect(self.openGithub)  # 点击左上角标题图标执行openGithub
        self.pushButton_quit.clicked.connect(self.quitMain)  # 右上角退出按钮执行quitMain
        self.pushButton_markname.clicked.connect(self.addMarkName)  # 点击备注按钮
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
                break
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
        with open('rename.ini', 'w', encoding='utf-8')as f:  # 写入rename.ini
            for i in self.accounts:  # 遍历账号
                if i.name_mark:  # 找到有name_mark的对象
                    f.write(i.name_account + ':' + i.name_mark + '\n')  # 写入 账号:备注
        exit()  # 退出

    # 从loginuser文件中获取下拉框items和tooltips，从avatarcache文件夹中获取items对应的icon
    def getComboBox(self):
        self.comboBox.clear()  # 清除combobox中的内容
        self.avatar_path = self.root_path + '/config/avatarcache/'  # 获取头像地址
        filenames = listdir(self.avatar_path)  # 获取头像文件列表
        autoUser = ""  # 创建临时变量储存目前登录的账号
        for i in self.accounts:  # 遍历账号列表
            if i.name_account == self.user:  # 判断如果为目前的登录账号，就赋值给autoUser
                autoUser = i
                break
        self.accounts.sort(key=lambda account: account.time_stamp, reverse=True)  # 给列表按account的time_stamp排序
        if type(autoUser).__name__ == 'Account':  # 如果autoUser赋值了Account对象
            self.accounts.remove(autoUser)  # 删除现有的对象
            self.accounts.insert(0, autoUser)  # 就把autoUser插队到列表首位
        for i in self.accounts:  # 循环列表
            self.comboBox.addItem(i.name_account)  # 添加到下拉框
            index = self.accounts.index(i)  # 获取元素在列表中的索引
            # 根据索引添加tooltip
            tooltip = str(i.name_persona + '\n' + i.time_last)  # 格式化tooltip
            self.comboBox.setItemData(index, tooltip, Qt.ToolTipRole)  # 根据索引index添加tooltip
            # 根据索引添加账号对象
            self.comboBox.setItemData(index, i, Qt.UserRole)  # 根据索引index添加账号对象i
            # 根据索引添加备注
            if i.name_mark:
                self.comboBox.setItemText(index, i.name_mark)  # 根据索引index添加备注name_mark到combobox显示
            # 根据索引添加icon
            for j in filenames:  # 循环列表filenames用来添加items的icon
                if j[0:-4] == i.steamID64:  # 如果filenames中有相应的steamid就添加icon
                    self.comboBox.setItemIcon(index, QIcon(self.avatar_path + j))  # 设置icon
                    filenames.remove(j)  # 从列表中删除已添加的icon，减少运算
                    break
        self.comboBox.addItem('-----------手动输入其他账号-----------')

    # 选择选项改变label显示内容
    def changeComboBox(self):
        # 判断是否选择最后一个选项
        lastIndex = len(self.accounts)
        if self.comboBox.currentIndex() == lastIndex:
            # 如果是 则打开combobox的编辑权限
            self.comboBox.setEditable(True)
            # 并设置combobox的stylesheet
            self.comboBox.setStyleSheet('background-color:rgb(50, 53, 60);\n'
                                        'color:rgb(175,175,175);\n'
                                        'background-image:url()\n')
        elif self.comboBox.currentIndex() > lastIndex:
            # 如果选择了输入并输入内容回车 currentIndex()为最后一个选项
            self.label_name.setText('(Not Found!!!???')  # 设置label的文本
            self.label_time.setText('账号最后登录时间：????.??.?? ??:??')  # 设置label的文本
            self.comboBox.setEditable(False)  # 关闭combobox编辑权限
        else:
            self.comboBox.setEditable(False)  # 关闭combobox编辑权限

    # 输入内容修改label的内容
    def inputComboBox(self):
        account = self.comboBox.currentData(Qt.UserRole)  # 获取保存在item里的userrole data
        if account:  # 如果有内容
            self.label_name.setText(account.name_persona)  # 设置label的文本
            self.label_time.setText('账号最后登录时间：' + account.time_last)  # 设置label的文本
        else:
            self.label_name.setText('(Not Found!!!???')  # 设置label的文本
            self.label_time.setText('账号最后登录时间：????.??.?? ??:??')  # 设置label的文本
        choice = self.comboBox.currentText()  # 获取combobox内容
        for i in self.accounts:  # 通过遍历账号列表 获取选择的账号名字和最后登录时间
            if i.name_account == choice:  # 判断账号是否为选择的账号
                self.label_name.setText(i.name_persona)  # 设置label的文本
                self.label_time.setText('账号最后登录时间：' + i.time_last)  # 设置label的文本
                break

    def addMarkName(self):
        user = self.comboBox.currentData(Qt.UserRole)  # 获取当前combobox的item的data
        if type(user).__name__ == 'Account':  # 如果data里面存放着Account对象
            username = user.name_account  # 获取username
            markname = user.name_mark  # 获取markname
            self.inputWindow = InputWindow(self)  # 实例化inputwindow对象
            if username:  # 如果username有
                self.inputWindow.setLabelText('备注将在下次运行软件时生效\n\n账号 ' + username + ' 输入备注↓ ')  # 设置username为label内容
                self.inputWindow.setWindowTitle(username + ' 备注信息')  # 设置username为标题
                if markname:  # 如果markname有
                    self.inputWindow.setTextValue(markname)  # 设置markname为输入框默认内容
                else:  # 如果markname没有
                    self.inputWindow.setTextValue(username)  # 设置username为输入框默认内容
            self.setDisabled(True)  # 设置主窗口不能操作
            ok = self.inputWindow.exec()  # 获取输入内容
            self.setDisabled(False)  # 设置主窗口可以操作
            if ok:  # 如果选择了ok
                rename = self.inputWindow.textValue()  # 获取输入的内容为rename
                for i in self.accounts:  # 遍历账号列表
                    if i.name_account == username:  # 判断如果账号相同
                        i.name_mark = rename  # 给账号对象的name_mark赋值rename
                        break  # 结束循环
            else:  # 如果选择了否
                self.inputWindow.close()  # 关闭输入窗口

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
        account = self.comboBox.currentData(Qt.UserRole)  # 获取item的data
        if type(account).__name__ == 'Account':  # 如果有
            username = account.name_account  # 登录账号为data里的name_account
        else:  # 如果没有
            username = self.comboBox.currentText()  # 登录账号为combobox的内容text
        SetValueEx(key, "AutoLoginUser", 0, REG_SZ, username)  # 修改注册表的autologinuser为输入框的文本
        CloseKey(key)  # 关闭注册表
        Popen(r'taskkill /f /im steam.exe')  # 关闭steam程序
        Popen(r"taskkill /f /im SteamService.exe")  # 关闭steam服务
        sleep(0.5)  # 添加延迟 操作太快会使得没关闭steam就打开了
        Popen(r"{}".format(self.exe_path))  # 打开steam
        self.quitMain()  # 关闭此程序

    # 获取vdf里面的账号信息，读ini里面的备注信息
    def getAccount(self):
        # 入读文件
        try:
            with open(self.vdf_path, encoding='utf-8') as f:  # 打开loginusers.vdf文件
                content = f.readlines()  # 获取文件的内容 type:list
        except FileNotFoundError:  # 如果没有找到文件
            self.accounts = []  # 列表清空
            # 添加报错的账号对象
            account = Account('404', 'steam自带的账号文件缺失', '请检查steam/config/loginusers.vdf', 0000000000)
            self.accounts.append(account)  # 将报错对象 添加到账号列表中
        else:  # 如果找到了文件
            try:
                with open(self.cfg_path, encoding='utf-8') as fi:  # 打开ini文件
                    self.content_ini = fi.readlines()  # 读取内容 type:list
            except FileNotFoundError:  # 如果没有找到文件
                with open(self.cfg_path, 'w', encoding='utf-8') as fi:  # 创建ini文件
                    fi.close()  # 关闭文件
                self.content_ini = ['', '']  # 赋值变量为空白列表
            # 删除多余内容
            del content[0:2]  # 删除前0,1,2行内容
            del content[-1]  # 删除最后一行内容
            users = []  # 创建列表临时保存文件内容
            self.accounts = []  # 创建账号列表
            for i in range(0, len(content), 11):  # 分割内容的列表
                # 0代表从0开始 len(content)代表总循环次数 11代表每次循环计数+11
                users.append(content[i:i + 11])  # 每11行为一个新列表 添加到users里面
                # content[i:i+11] i到i+11个
            for i in users:  # 获取列表中需要的信息
                # 格式化内容
                steamID64 = i[0].replace('\t', '').replace('\"', '').replace('\n', '')
                AccountName = i[2].replace('\t', '').replace('\"', '')[11:].replace('\n', '')
                PersonaName = i[3].replace('\t', '').replace('\"', '')[11:].replace('\n', '')
                Timestamp = i[9].replace('\t', '').replace('\"', '')[9:].replace('\n', '')
                account = Account(steamID64, AccountName, PersonaName, int(Timestamp))  # 实例化对象Account
                for j in self.content_ini:  # 遍历cfg的内容
                    if len(j.split(':')) == 2:  # 判断内容是否有空格
                        username, markname = j.split(':')  # 获取username、markname
                        if AccountName == username:  # 判断账号名是否和上面获取的username相同
                            account.name_mark = markname.replace('\n', '')  # 赋值给对象的name_mark
                            break
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
