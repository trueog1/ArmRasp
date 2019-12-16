from socket import *
from xArmUi import Ui_Form
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sqlite3
import sys
import resource

class MainWindow(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        # self.setWindowIcon(QIcon(':/tubiao.png'))
        self.tabWidget.setCurrentIndex(0)  # 设置默认标签为第一个标签
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置选中整行，若不设置默认选中单元格
        
        self.client = socket(AF_INET, SOCK_STREAM)
        # try:
        #     self.client.connect(('127.0.0.1', 1075))
        # except:
        #     self.message_From("无法连接到服务器")
        #     sys.exit()
        # th = threading.Thread(target=self.tcpsocket_receive)
        # th.setDaemon(True)
        # th.start()
        # self.button_controlaction_clicked('reflash')

        ########################主界面###############################
        self.validator1 = QIntValidator(0, 1000)
        self.lineEdit_1.setValidator(self.validator1)
        self.lineEdit_2.setValidator(self.validator1)
        self.lineEdit_3.setValidator(self.validator1)
        self.lineEdit_4.setValidator(self.validator1)
        self.lineEdit_5.setValidator(self.validator1)
        self.lineEdit_6.setValidator(self.validator1)

        # 滑竿同步对应文本框的数值,及滑竿控制相应舵机转动与valuechange函数绑定
        self.horizontalSlider_1.valueChanged.connect(lambda: self.valuechange1('id1'))
        self.horizontalSlider_2.valueChanged.connect(lambda: self.valuechange1('id2'))
        self.horizontalSlider_3.valueChanged.connect(lambda: self.valuechange1('id3'))
        self.horizontalSlider_4.valueChanged.connect(lambda: self.valuechange1('id4'))
        self.horizontalSlider_5.valueChanged.connect(lambda: self.valuechange1('id5'))
        self.horizontalSlider_6.valueChanged.connect(lambda: self.valuechange1('id6'))

        self.horizontalSlider_11.valueChanged.connect(lambda: self.valuechange2('d1'))
        self.horizontalSlider_12.valueChanged.connect(lambda: self.valuechange2('d2'))
        self.horizontalSlider_13.valueChanged.connect(lambda: self.valuechange2('d3'))
        self.horizontalSlider_14.valueChanged.connect(lambda: self.valuechange2('d4'))
        self.horizontalSlider_15.valueChanged.connect(lambda: self.valuechange2('d5'))
        self.horizontalSlider_16.valueChanged.connect(lambda: self.valuechange2('d6'))

        # tableWidget点击获取定位的信号与icon_position函数（添加运行图标）绑定
        self.tableWidget.pressed.connect(self.icon_position)

        self.validator3 = QIntValidator(20, 30000)
        self.lineEdit_time.setValidator(self.validator3)

        # 将编辑动作组的按钮点击时的信号与button_editaction_clicked函数绑定
        self.Button_ServoPowerDown.pressed.connect(lambda: self.button_editaction_clicked('servoPowerDown'))
        self.Button_AngularReadback.pressed.connect(lambda: self.button_editaction_clicked('angularReadback'))
        self.Button_AddAction.pressed.connect(lambda: self.button_editaction_clicked('addAction'))
        self.Button_DelectAction.pressed.connect(lambda: self.button_editaction_clicked('delectAction'))
        self.Button_UpdateAction.pressed.connect(lambda: self.button_editaction_clicked('updateAction'))
        self.Button_InsertAction.pressed.connect(lambda: self.button_editaction_clicked('insertAction'))
        self.Button_MoveUpAction.pressed.connect(lambda: self.button_editaction_clicked('moveUpAction'))
        self.Button_MoveDownAction.pressed.connect(lambda: self.button_editaction_clicked('moveDownAction'))        

        # 将在线运行及停止运行按钮点击的信号与button_runonline函数绑定
        self.Button_RunOnline.clicked.connect(self.button_runonline)

        self.Button_OpenActionGroup.pressed.connect(lambda: self.button_flie_operate('openActionGroup'))
        self.Button_SaveActionGroup.pressed.connect(lambda: self.button_flie_operate('saveActionGroup'))
        self.Button_ReadDeviation.pressed.connect(lambda: self.button_flie_operate('readDeviation'))
        self.Button_DownloadDeviation.pressed.connect(lambda: self.button_flie_operate('downloadDeviation'))
        self.Button_TandemActionGroup.pressed.connect(lambda: self.button_flie_operate('tandemActionGroup'))
        self.Button_ReSetServos.clicked.connect(lambda: self.button_clicked('reSetServos'))
        self.Button_ReSetDev.clicked.connect(lambda: self.button_clicked('reSetDev'))
        
        # 将控制动作的按钮点击的信号与action_control_clicked函数绑定
        self.Button_DelectSingle.pressed.connect(lambda: self.button_controlaction_clicked('delectSingle'))
        self.Button_AllDelect.pressed.connect(lambda: self.button_controlaction_clicked('allDelect'))
        self.Button_RunAction.pressed.connect(lambda: self.button_controlaction_clicked('runAction'))
        self.Button_StopAction.pressed.connect(lambda: self.button_controlaction_clicked('stopAction'))
        self.Button_Reflash.pressed.connect(lambda: self.button_controlaction_clicked('reflash'))
        self.Button_Quit.pressed.connect(lambda: self.button_controlaction_clicked('quit'))

        self.devNew = [0, 0, 0, 0, 0, 0]
        self.devOld = [0, 0, 0, 0, 0, 0]
        #################################副界面#######################################
        self.temp = 0
        self.servoMin = 0
        self.servoMax = 0
        self.servoMinV = 0
        self.servoMaxV = 0
        self.servoMove = 0
        self.horizontalSlider_servoTemp.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoTemp'))
        self.horizontalSlider_servoMin.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMin'))
        self.horizontalSlider_servoMax.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMax'))
        self.horizontalSlider_servoMinV.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMinV'))
        self.horizontalSlider_servoMaxV.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMaxV'))
        self.horizontalSlider_servoMove.valueChanged.connect(lambda: self.horizontalSlider_valuechange('servoMove'))

        self.pushButton_read.pressed.connect(lambda: self.button_clicked('read'))
        self.pushButton_set.pressed.connect(lambda: self.button_clicked('set'))
        self.pushButton_default.pressed.connect(lambda: self.button_clicked('default'))

        self.validator2 = QIntValidator(-125, 125)
        self.lineEdit_servoDev.setValidator(self.validator2)

    # 弹窗提示函数
    def message_From(self, str):
        messageBox = QMessageBox()
        messageBox.setWindowTitle(' ')
        messageBox.setText(str)
        messageBox.addButton(QPushButton('确定'), QMessageBox.YesRole)
        return messageBox.exec_()

    # 弹窗提示函数
    def message_delect(self, str):
        messageBox = QMessageBox()
        messageBox.setWindowTitle(' ')
        messageBox.setText(str)
        messageBox.addButton(QPushButton('确定'), QMessageBox.YesRole)
        messageBox.addButton(QPushButton('取消'), QMessageBox.NoRole)
        return messageBox.exec_()

    def tcpsocket_receive(self):
        while True:                        
            recv_data = self.client.recv(1024).decode()
            recv = recv_data.split('\r\n')          
            cmd = recv[0][:4]
            id = ''
            dev = []
            angle = []
            if cmd == 'I004':
                recv = recv[0].split('-')
                if int(recv[1]) == len(recv) - 2:
                    self.comboBox_action.clear()
                    for i in range(2, len(recv)):
                        self.comboBox_action.addItem(recv[i])
                elif int(recv[1]) == 0:
                    self.comboBox_action.clear()
                else:
                    self.message_From('动作组列表获取失败!')
            if cmd == 'I008':
                recv = recv[0].split('-')
                if recv[3] == 'ok':
                    self.message_From('下载偏差成功!')
                elif recv[3] == 'no':
                    self.message_From('偏差数量错误，下载失败!')
                else:
                    self.message_From('偏差值超出范围-125~125，下载失败!')
                print(recv)
            if cmd == 'I009':
                recv = recv[0].split('-')
                if int(recv[1]) == len(recv) - 2:
                    for i in range(2, len(recv)):
                        if recv[i] == '999':
                            dev.append(0)
                            id += str(i - 2)
                        else:
                            dev.append(int(recv[i]))
                    if id == '':                        
                        self.message_From('读取偏差成功!')
                    else:
                        self.message_From('id' + id + '号舵机偏差读取失败!')
                    self.setDev(dev)
                else:
                    self.message_From('未检测到舵机，读取偏差失败!')
            if cmd == 'I010':
                recv = recv[0].split('-')
                if recv[3] == 'ok':
                    self.message_From('成功!')
                elif recv[3] == 'no':
                    self.message_From('失败!')
                else:
                    self.message_From('指令错误!')
                print(recv)
            if cmd == 'I011':
                recv = recv[0].split('-')
                if int(recv[1]) == len(recv) - 2:
                    for i in range(2, len(recv)):
                        if recv[i] > 1000:
                            recv[i] = 1000
                        elif recv[i] < 0:
                            recv[i] = 0
                        angle.append(recv[i])
                    RowCont = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(RowCont)    # 增加一行
                    self.tableWidget.selectRow(RowCont)    # 定位最后一行为选中行                       
                    self.add_line(RowCont, str(self.lineEdit_time.text()), angle[0], angle[1], angle[2], angle[3], angle[4], angle[5])                            
                else:
                    self.message_From('指令长度错误!')
                            
    # 滑竿同步对应文本框的数值,及滑竿控制相应舵机转动
    def valuechange1(self, name):
        cmd = None
        if name == 'id1':
            servoAngle = str(self.horizontalSlider_1.value())
            self.lineEdit_1.setText(servoAngle)
            cmd = 'I001-20-1-1-' + servoAngle + '\r\n'
        if name == 'id2':
            servoAngle = str(self.horizontalSlider_2.value())
            self.lineEdit_2.setText(servoAngle)
            cmd = 'I001-20-1-2-' + servoAngle + '\r\n'
        if name == 'id3':
            servoAngle = str(self.horizontalSlider_3.value())
            self.lineEdit_3.setText(servoAngle)
            cmd = 'I001-20-1-3-' + servoAngle + '\r\n'
        if name == 'id4':
            servoAngle = str(self.horizontalSlider_4.value())
            self.lineEdit_4.setText(servoAngle)
            cmd = 'I001-20-1-4-' + servoAngle + '\r\n'
        if name == 'id5':
            servoAngle = str(self.horizontalSlider_5.value())
            self.lineEdit_5.setText(servoAngle)
            cmd = 'I001-20-1-5-' + servoAngle + '\r\n'
        if name == 'id6':
            servoAngle = str(self.horizontalSlider_6.value())
            self.lineEdit_6.setText(servoAngle)
            cmd = 'I001-20-1-6-' + servoAngle + '\r\n'
        if cmd is not None:
            self.client.send(cmd.encode())

    def valuechange2(self, name):
        if name == 'd1':
            self.devNew[0] = str(self.horizontalSlider_11.value())
            self.label_d1.setText(self.devNew[0])
        if name == 'd2':
            self.devNew[1] = str(self.horizontalSlider_12.value())
            self.label_d2.setText(self.devNew[1])
        if name == 'd3':
            self.devNew[2] = str(self.horizontalSlider_13.value())
            self.label_d3.setText(self.devNew[2])
        if name == 'd4':
            self.devNew[3] = str(self.horizontalSlider_14.value())
            self.label_d4.setText(self.devNew[3])
        if name == 'd5':
            self.devNew[4] = str(self.horizontalSlider_15.value())
            self.label_d5.setText(self.devNew[4])
        if name == 'd6':
            self.devNew[5] = str(self.horizontalSlider_16.value())
            self.label_d6.setText(self.devNew[5])

    def setDev(self, dev=[0, 0, 0, 0, 0, 0]):
        self.horizontalSlider_11.setValue(dev[0])
        self.horizontalSlider_12.setValue(dev[1])
        self.horizontalSlider_13.setValue(dev[2])
        self.horizontalSlider_14.setValue(dev[3])
        self.horizontalSlider_15.setValue(dev[4])
        self.horizontalSlider_16.setValue(dev[5])

        self.label_d1.setText(str(dev[0]))
        self.label_d2.setText(str(dev[1]))
        self.label_d3.setText(str(dev[2]))
        self.label_d4.setText(str(dev[3]))
        self.label_d5.setText(str(dev[4]))
        self.label_d6.setText(str(dev[5]))          

    # 复位按钮点击事件
    def button_clicked(self, name):
        if name == 'reSetServos':
            self.horizontalSlider_1.setValue(500)
            self.horizontalSlider_2.setValue(500)
            self.horizontalSlider_3.setValue(500)
            self.horizontalSlider_4.setValue(500)
            self.horizontalSlider_5.setValue(500)
            self.horizontalSlider_6.setValue(500)

            self.lineEdit_1.setText('500')
            self.lineEdit_2.setText('500')
            self.lineEdit_3.setText('500')
            self.lineEdit_4.setText('500')
            self.lineEdit_5.setText('500')
            self.lineEdit_6.setText('500')
            cmd = 'I001-500-6-1-500-2-500-3-500-4-500-5-500-6-500\r\n'
            self.client.send(cmd.encode())
        elif name == 'reSetDev':
           self.setDev()      

    # 选项卡选择标签状态，获取对应舵机数值
    def tabindex(self, index):       
        return  [str(self.horizontalSlider_1.value()), str(self.horizontalSlider_2.value()),
                 str(self.horizontalSlider_3.value()), str(self.horizontalSlider_4.value()),
                 str(self.horizontalSlider_5.value()), str(self.horizontalSlider_6.value())]
    
    def getIndexData(self, index):
        data = []
        for j in range(2, self.tableWidget.columnCount()):
            data.append(str(self.tableWidget.item(index, j).text()))
        
        return data
    
    # 往tableWidget表格添加一行数据的函数
    def add_line(self, item, timer, id1, id2, id3, id4, id5, id6):
        self.tableWidget.setItem(item, 1, QtWidgets.QTableWidgetItem(str(item + 1)))
        self.tableWidget.setItem(item, 2, QtWidgets.QTableWidgetItem(timer))
        self.tableWidget.setItem(item, 3, QtWidgets.QTableWidgetItem(id1))
        self.tableWidget.setItem(item, 4, QtWidgets.QTableWidgetItem(id2))
        self.tableWidget.setItem(item, 5, QtWidgets.QTableWidgetItem(id3))
        self.tableWidget.setItem(item, 6, QtWidgets.QTableWidgetItem(id4))
        self.tableWidget.setItem(item, 7, QtWidgets.QTableWidgetItem(id5))
        self.tableWidget.setItem(item, 8, QtWidgets.QTableWidgetItem(id6))

    # 在定位行添加运行图标按钮
    def icon_position(self):
        toolButton_run = QtWidgets.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/index.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        toolButton_run.setIcon(icon)
        toolButton_run.setObjectName("toolButton_run")
        item = self.tableWidget.currentRow()
        self.tableWidget.setCellWidget(item, 0, toolButton_run)
        for i in range(self.tableWidget.rowCount()):
            if i != item:
                self.tableWidget.removeCellWidget(i, 0)
        toolButton_run.clicked.connect(self.action_one)

    def action_one(self):
        item = self.tableWidget.currentRow()
        alist = []
        for j in range(3, 9):
            alist.append(int(self.tableWidget.item(item, j).text()))
        self.horizontalSlider_1.setValue(alist[0])
        self.horizontalSlider_2.setValue(alist[1])
        self.horizontalSlider_3.setValue(alist[2])
        self.horizontalSlider_4.setValue(alist[3])
        self.horizontalSlider_5.setValue(alist[4])
        self.horizontalSlider_6.setValue(alist[5])
        try:
            timer = int(self.tableWidget.item(self.tableWidget.currentRow(), 2).text())
            cmd = 'I001-' + str(timer) + '-6'
            for j in range(1, 7):
                cmd += '-' + str(j) + '-'
                cmd += str(int(self.tableWidget.item(self.tableWidget.currentRow(), j+2).text())) + ''
            cmd += '\r\n'
            self.client.send(cmd.encode())
        except Exception:
            self.message_From('运行出错')

    # 编辑动作组按钮点击事件
    def button_editaction_clicked(self, name):
        list = self.tabindex(self.tabWidget.currentIndex())
        RowCont = self.tableWidget.rowCount()
        item = self.tableWidget.currentRow()
        
        if name == 'servoPowerDown':
            cmd = 'I010\r\n'
            self.client.send(cmd.encode())
        if name == 'angularReadback':
            cmd = 'I011\r\n'
            self.client.send(cmd.encode())
        if name == 'addAction':    # 添加动作
            self.tableWidget.insertRow(RowCont)    # 增加一行
            self.tableWidget.selectRow(RowCont)    # 定位最后一行为选中行
            self.add_line(RowCont, str(self.lineEdit_time.text()), list[0], list[1], list[2], list[3], list[4], list[5])
        if name == 'delectAction':    # 删除动作
            self.tableWidget.removeRow(item)  # 删除选定行
        if name == 'updateAction':    # 更新动作
            self.add_line(item, str(self.lineEdit_time.text()), list[0], list[1], list[2], list[3], list[4], list[5])
        if name == 'insertAction':    # 插入动作
            self.tableWidget.insertRow(item)       # 插入一行
            self.tableWidget.selectRow(item)
            self.add_line(item, str(self.lineEdit_time.text()), list[0], list[1], list[2], list[3], list[4], list[5])
        if name == 'moveUpAction':
            print(item, RowCont)
            if item == 0:
                return
            current_data = self.getIndexData(item)
            uplist_data = self.getIndexData(item - 1)
            self.add_line(item - 1, current_data[0], current_data[1], current_data[2], current_data[3], current_data[4], current_data[5], current_data[6])
            self.add_line(item, uplist_data[0], uplist_data[1], uplist_data[2], uplist_data[3], uplist_data[4], uplist_data[5], uplist_data[6])
            self.tableWidget.selectRow(item - 1) 
        if name == 'moveDownAction':
            print(item, RowCont)
            if item == RowCont - 1:
                return
            current_data = self.getIndexData(item)
            downlist_data = self.getIndexData(item + 1)           
            self.add_line(item + 1, current_data[0], current_data[1], current_data[2], current_data[3], current_data[4], current_data[5], current_data[6])
            self.add_line(item, downlist_data[0], downlist_data[1], downlist_data[2], downlist_data[3], downlist_data[4], downlist_data[5], downlist_data[6])
            self.tableWidget.selectRow(item + 1) 
        for i in range(self.tableWidget.rowCount()):    #刷新编号值
            self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(str(i + 1)))
        self.icon_position()

    # 在线运行按钮点击事件
    def button_runonline(self):
        if self.tableWidget.rowCount() == 0:
            self.message_From('请先添加动作!')
        else:
            if self.Button_RunOnline.text() == '在线运行':
                self.Button_RunOnline.setText('停止')
                self.tableWidget.selectRow(0)
                self.icon_position()
                self.action_online(0)
                self.timer = QTimer()
                if self.checkBox.isChecked():
                    for i in range(self.tableWidget.rowCount()):
                        s = self.tableWidget.item(i,2).text()
                        self.timer.start(int(s))       # 设置计时间隔并启动
                    self.timer.timeout.connect(self.operate1)
                else:
                    for i in range(self.tableWidget.rowCount()):
                        s = self.tableWidget.item(i,2).text()
                        self.timer.start(int(s))       # 设置计时间隔并启动
                    self.timer.timeout.connect(self.operate2)
            elif self.Button_RunOnline.text() == '停止':
                self.timer.stop()
                self.Button_RunOnline.setText('在线运行')
                self.message_From('运行结束!')

    def operate1(self):
        item = self.tableWidget.currentRow()
        if item == self.tableWidget.rowCount() - 1:
            self.tableWidget.selectRow(0)
            self.action_online(0)
        else:
            self.tableWidget.selectRow(item + 1)
            self.action_online(item + 1)
        self.icon_position()

    def operate2(self):
        item = self.tableWidget.currentRow()
        if item == self.tableWidget.rowCount() - 1:
            self.timer.stop()
            self.Button_RunOnline.setText('在线运行')
            self.message_From('运行结束!')
        else:
            self.tableWidget.selectRow(item + 1)
            self.action_online(item + 1)
        self.icon_position()

    def action_online(self, item):
        try:
            timer = int(self.tableWidget.item(item, 2).text())
            cmd = 'I001-' + str(timer) + '-6'
            for j in range(1, 7):
                cmd += '-' + str(j) + '-'
                cmd += str(int(self.tableWidget.item(item, j+2).text()))
            cmd += '\r\n'
            self.client.send(cmd.encode())
        except Exception:
            self.timer.stop()
            self.Button_RunOnline.setText('在线运行')
            self.message_From('运行出错')

    # 文件打开及保存按钮点击事件
    def button_flie_operate(self, name):
        try:
            
            if name == 'openActionGroup':
                dig_o = QFileDialog()
                dig_o.setFileMode(QFileDialog.ExistingFile)
                dig_o.setNameFilter('d6a Flies(*.d6a)')
                openfile = dig_o.getOpenFileName(self, 'OpenFile', '', 'd6a Flies(*.d6a)')
                # 打开单个文件
                # 参数一：设置父组件；参数二：QFileDialog的标题
                # 参数三：默认打开的目录，“.”点表示程序运行目录，/表示当前盘符根目录
                # 参数四：对话框的文件扩展名过滤器Filter，比如使用 Image files(*.jpg *.gif) 表示只能显示扩展名为.jpg或者.gif文件
                # 设置多个文件扩展名过滤，使用双引号隔开；“All Files(*);;PDF Files(*.pdf);;Text Files(*.txt)”
                path = openfile[0]
                try:
                    if path != '':
                        rbt = QSqlDatabase.addDatabase("QSQLITE")
                        rbt.setDatabaseName(path)
                        if rbt.open():
                            actgrp = QSqlQuery()
                            if (actgrp.exec("select * from ActionGroup ")):
                                self.tableWidget.setRowCount(0)
                                self.tableWidget.clearContents()
                                while (actgrp.next()):
                                    count = self.tableWidget.rowCount()
                                    self.tableWidget.setRowCount(count + 1)
                                    for i in range(8):
                                        self.tableWidget.setItem(count, i + 1, QtWidgets.QTableWidgetItem(str(actgrp.value(i))))
                                        self.tableWidget.item(count, i + 1).setTextAlignment(Qt.AlignCenter)
                                        self.tableWidget.update()
                                        self.tableWidget.selectRow(count)               
                        self.icon_position()
                        rbt.close()
                except:
                    self.message_From('动作组错误')
            if name == 'saveActionGroup':
                dig_s = QFileDialog()
                if self.tableWidget.rowCount() == 0:
                    self.message_From('动作列表是空的哦，没啥要保存的')
                    return
                savefile = dig_s.getSaveFileName(self, 'Savefile', '', 'd6a Flies(*.d6a)')
                path = savefile[0]
                if path != '':                    
                    if path[-4:] == '.d6a':                        
                        conn = sqlite3.connect(path)
                    else:
                        conn = sqlite3.connect(path + '.d6a')
                    c = conn.cursor()                    
                    c.execute('''CREATE TABLE ActionGroup([Index] INTEGER PRIMARY KEY AUTOINCREMENT
                    NOT NULL ON CONFLICT FAIL
                    UNIQUE ON CONFLICT ABORT,
                    Time INT,
                    Servo1 INT,
                    Servo2 INT,
                    Servo3 INT,
                    Servo4 INT,
                    Servo5 INT,
                    Servo6 INT);''')                      
                    for i in range(self.tableWidget.rowCount()):
                        insert_sql = "INSERT INTO ActionGroup(Time, Servo1, Servo2, Servo3, Servo4, Servo5, Servo6) VALUES("
                        for j in range(2, self.tableWidget.columnCount()):
                            if j == self.tableWidget.columnCount() - 1:
                                insert_sql += str(self.tableWidget.item(i, j).text())
                            else:
                                insert_sql += str(self.tableWidget.item(i, j).text()) + ','
                        
                        insert_sql += ");"
                        c.execute(insert_sql)
                    conn.commit()
                    conn.close()
                    self.button_controlaction_clicked('reflash')
            if name == 'readDeviation':
                cmd = 'I009'
                self.client.send(cmd.encode())
            if name == 'downloadDeviation':
                cmd = 'I008-6-' + str(self.horizontalSlider_11.value()) + '-' + str(self.horizontalSlider_12.value()) + '-' + \
                str(self.horizontalSlider_13.value()) + '-' + str(self.horizontalSlider_14.value()) + '-' + \
                str(self.horizontalSlider_15.value()) + '-' + str(self.horizontalSlider_16.value()) + '\r\n'
                print(cmd)
                self.client.send(cmd.encode())
            if name == 'tandemActionGroup':
                dig_t = QFileDialog()
                dig_t.setFileMode(QFileDialog.ExistingFile)
                dig_t.setNameFilter('d6a Flies(*.d6a)')
                openfile = dig_t.getOpenFileName(self, 'OpenFile', '', 'd6a Flies(*.d6a)')
                # 打开单个文件
                # 参数一：设置父组件；参数二：QFileDialog的标题
                # 参数三：默认打开的目录，“.”点表示程序运行目录，/表示当前盘符根目录
                # 参数四：对话框的文件扩展名过滤器Filter，比如使用 Image files(*.jpg *.gif) 表示只能显示扩展名为.jpg或者.gif文件
                # 设置多个文件扩展名过滤，使用双引号隔开；“All Files(*);;PDF Files(*.pdf);;Text Files(*.txt)”
                path = openfile[0]
                try:
                    if path != '':
                        tbt = QSqlDatabase.addDatabase("QSQLITE")
                        tbt.setDatabaseName(path)
                        if tbt.open():
                            actgrp = QSqlQuery()
                            if (actgrp.exec("select * from ActionGroup ")):
                                while (actgrp.next()):
                                    count = self.tableWidget.rowCount()
                                    self.tableWidget.setRowCount(count + 1)
                                    for i in range(8):
                                        if i == 0:
                                            self.tableWidget.setItem(count, i + 1, QtWidgets.QTableWidgetItem(str(count + 1)))
                                        else:                      
                                            self.tableWidget.setItem(count, i + 1, QtWidgets.QTableWidgetItem(str(actgrp.value(i))))
                                        self.tableWidget.item(count, i + 1).setTextAlignment(Qt.AlignCenter)
                                        self.tableWidget.update()
                                        self.tableWidget.selectRow(count)               
                        self.icon_position()
                        tbt.close()
                except:
                    self.message_From('动作组错误')
        except BaseException as e:
            print(e)

    # 控制动作组按钮点击事件
    def button_controlaction_clicked(self, name):
        cmd = None
        if name == 'delectSingle':
            cmd = 'I005-' + str(self.comboBox_action.currentText()) + '\r\n'
        if name == 'allDelect':
            result = self.message_delect('此操作会删除所有动作组，是否继续？')
            if result == 0:                              
                cmd = 'I006\r\n'
            else:
                pass
        if name == 'runAction':   # 动作组运行
            cmd = 'I003-' + str(self.comboBox_action.currentText()) + '-1\r\n'
        if name == 'stopAction':   # 停止运行
            cmd = 'I002\r\n'
        if name == 'reflash':
            cmd = 'I004\r\n'
        if name == 'quit':
            sys.exit()
        if cmd is not None:
            self.client.send(cmd.encode())

    def horizontalSlider_valuechange(self, name):
        if name == 'servoTemp':
            self.temp = str(self.horizontalSlider_servoTemp.value())
            self.label_servoTemp.setText(self.temp + '℃')
        if name == 'servoMin':
            self.servoMin = str(self.horizontalSlider_servoMin.value())
            self.label_servoMin.setText(self.servoMin)
        if name == 'servoMax':
            self.servoMax = str(self.horizontalSlider_servoMax.value())
            self.label_servoMax.setText(self.servoMax)
        if name == 'servoMinV':
            self.servoMinV = str(self.horizontalSlider_servoMinV.value()/10)
            self.label_servoMinV.setText(self.servoMinV + 'V')
        if name == 'servoMaxV':
            self.servoMaxV = str(self.horizontalSlider_servoMaxV.value()/10)
            self.label_servoMaxV.setText(self.servoMaxV + 'V')
        if name == 'servoMove':
            self.servoMove = str(self.horizontalSlider_servoMove.value())
            self.label_servoMove.setText(self.servoMove)

    def button_clicked(self, name):
        if name == 'read':

            pass
        if name == 'set':
            pass
        if name == 'default':
            pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myshow = MainWindow()
    myshow.show()
    #widget = QtWidgets.QWidget()
    #ui = Ui_Form()
    #ui.setupUi(widget)
    #widget.setWindowIcon(QIcon('web.png'))#增加icon图标，如果没有图片可以没有这句
    #widget.show()
    sys.exit(app.exec_())