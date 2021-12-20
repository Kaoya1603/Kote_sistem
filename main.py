import sqlite3
import datetime as dt
from mail import message
from doc import compose_file

from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, \
    QLabel, QLineEdit
from PyQt5.QtCore import Qt

import sys


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect('timu3.db')
        self.cur = self.con.cursor()
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 400, 200)
        self.setWindowTitle("Вход в систему")

        self.login_label = QLabel('Логин', self)
        self.login_label.move(30, 30)
        self.login_label.resize(self.login_label.sizeHint())

        self.shuru_login = QLineEdit(self)
        self.shuru_login.setGeometry(80, 30, 200, 20)

        self.denglu_anniu = QPushButton('Войти', self)
        self.denglu_anniu.setGeometry(80, 60, 100, 30)
        self.denglu_anniu.clicked.connect(self.denglu)

        self.cuowu_xinxi = QLabel('', self)
        self.cuowu_xinxi.move(30, 100)

    def denglu(self):
        login = self.shuru_login.text()
        xing = login[:-2]
        mingzi_wen = login[-2]
        fuqin_mingzi_wen = login[-1]

        data_gongjuren = self.cur.execute(
            f'''SELECT * FROM сотрудники WHERE (фамилия = '{xing}' AND имя LIKE '{mingzi_wen}%' 
                AND отчество LIKE '{fuqin_mingzi_wen}%')''').fetchall()
        data_yonghu = self.cur.execute(
            f'''SELECT * FROM пользователи WHERE (фамилия = '{xing}' AND имя LIKE '{mingzi_wen}%' 
                AND отчество LIKE '{fuqin_mingzi_wen}%')''').fetchall()
        if data_gongjuren or data_yonghu:
            if data_gongjuren:
                self.mainWindow = MainWindow(data_gongjuren[0][1], data_gongjuren[0][2], data_gongjuren[0][3])
                self.mainWindow.show()
            elif data_yonghu:
                self.userWindow = UserWindow(data_yonghu[0][0], data_yonghu[0][1], data_yonghu[0][2], data_yonghu[0][3],
                                             data_yonghu[0][4], data_yonghu[0][6])
                self.userWindow.show()
            LoginWindow.hide()
        else:
            self.cuowu_xinxi.setText('Логин некорректен или отсутствует в базе данных')
            self.cuowu_xinxi.resize(self.cuowu_xinxi.sizeHint())


class UserWindow(QWidget):  # личный кабинет пользователя
    def __init__(self, xing, mingzi, fuqin_mingzi, dianhuahao, dianziyoujian, status):
        super().__init__()
        self.con = sqlite3.connect('timu3.db')
        self.cur = self.con.cursor()
        self.xing = xing  # фимилия
        self.mingzi = mingzi  # имя
        self.fuqin_mingzi = fuqin_mingzi  # отчество
        self.dianhuahao = dianhuahao  # номер телефона
        self.dianziyoudian = dianziyoujian  # эл. почта
        self.status = status  # статус
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle(f"Здравствуйте, {self.mingzi} {self.fuqin_mingzi}!")

        self.status_label = QLabel(f'Ваш статус: {self.status}', self)
        self.status_label.move(20, 20)

        self.dazhe = self.cur.execute(f"""SELECT * FROM скидки WHERE статус = '{self.status}'""").fetchall()[0][1]
        self.dazhe_label = QLabel(f'Ваша скидка: {self.dazhe}%', self)
        self.dazhe_label.move(20, 45)

        jieshijian = sum(list(map(lambda x: x[4], self.cur.execute(
            f'''SELECT * FROM 'оплата аренды' WHERE пользователь = '{self.xing}' ''').fetchall())))
        self.jiesjijian_label = QLabel(f'Ваше суммарное время аренды: {jieshijian}', self)
        self.jiesjijian_label.move(200, 20)

        jiangjin = jieshijian // 10
        self.jiangjin_label = QLabel(f'Сейчас у вас {jiangjin} бонусов.', self)
        self.jiangjin_label.move(200, 45)

        self.biaoge = QTableWidget(self)
        self.biaoge.setGeometry(20, 70, 560, 320)

        dangshi_biaoge = self.cur.execute(f'''SELECT * FROM 'номенклатура' WHERE используется = "да";''').fetchall()
        zhonglei = list(map(lambda x: x[2], dangshi_biaoge))

        jiage = list(map(lambda x: x[1], filter(lambda x: x[0] in zhonglei,
                                                self.cur.execute(f'''SELECT * FROM 'прайс по тарифам' ''').fetchall())))

        try:  # риуем таблицу "номенклатура" + новый столбец с ценой
            self.biaoge.setRowCount(len(dangshi_biaoge))
            self.biaoge.setColumnCount(len(dangshi_biaoge[0]) + 1)

            tablenames = list(
                map(lambda x: x[1], self.cur.execute(f"""PRAGMA table_info("номенклатура")""").fetchall()))
            tablenames.append('тариф')
            for i in range(len(tablenames)):
                self.biaoge.setHorizontalHeaderItem(i, QTableWidgetItem(tablenames[i]))

            for i in range(len(tablenames)):
                self.biaoge.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)
            self.biaoge.horizontalHeader().setMinimumSectionSize(555 // len(tablenames))

            for i in range(len(dangshi_biaoge)):
                for j in range(len(dangshi_biaoge[0]) + 1):
                    if j in [0, 2, 3]:
                        item = QTableWidgetItem(str(dangshi_biaoge[i][j]))
                        self.biaoge.setItem(i, j, item)
                    if j == 1:
                        anniu = QPushButton(str(dangshi_biaoge[i][j]), self)  # каждый товар - кнопка
                        anniu.clicked.connect(
                            self.zhanshi_huowu_mingpian)  # при нажатии на нее открывается карточка товара
                        self.biaoge.setCellWidget(i, j, anniu)
                    if j == 4:
                        item = QTableWidgetItem(str(jiage[i]))
                        self.biaoge.setItem(i, j, QTableWidgetItem(str(jiage[i])))
                    item.setFlags(Qt.ItemIsEnabled)
            self.biaofe.resizeColumnsToContents()
        except IndexError:
            pass

    def zhanshi_huowu_mingpian(self):  # открываем карточку товара
        sender = self.sender()
        self.huowu_mingzi = HuowuMingpian(sender.text(), self.xing, self.mingzi, self.fuqin_mingzi, self.dazhe,
                                          self.dianziyoudian)
        self.huowu_mingzi.show()


class HuowuMingpian(QWidget):  # карточка товара
    def __init__(self, huowu_mingzi, yonghu, mingzi, fuqin_mingzi, dazhe, dianziyoujian):
        super().__init__()
        self.huowu_mingzi = huowu_mingzi  # название товара
        self.yonghu = yonghu  # пользователь
        self.mingzi = mingzi
        self.fuqin_mingzi = fuqin_mingzi
        self.dazhe = dazhe  # его скидка
        self.dianziyoujian = dianziyoujian
        self.kaishi_shijian = list()
        self.con = sqlite3.connect('timu3.db')
        self.cur = self.con.cursor()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle(self.huowu_mingzi)

        artikul = list(filter(lambda x: x[1] == self.huowu_mingzi,
                              self.cur.execute('''SELECT * FROM 'номенклатура';''').fetchall()))
        self.artikul = artikul[0][0]
        self.artikul_label = QLabel(f'Артикул: {self.artikul}', self)
        self.artikul_label.move(20, 20)

        self.nom_type_label = QLabel(f'Тип номенклатуры: {artikul[0][2]}', self)
        self.nom_type_label.move(20, 45)

        self.jiage = list(filter(lambda x: x[0] == artikul[0][2],
                                 self.cur.execute('''SELECT * FROM 'прайс по тарифам';''').fetchall()))[0][1]
        self.jiage_label = QLabel(f'Тариф: {self.jiage}', self)
        self.jiage_label.move(20, 70)

        self.taidu = QLabel('', self)  # строка состояния ("товар арендован"\"товар возвращен")
        self.taidu.move(20, 95)

        jie_kaishi = list(filter(lambda x: x[3] == self.huowu_mingzi,
                                 self.cur.execute('''SELECT * FROM 'начало аренды';''').fetchall()))
        jie_jieshu = list(filter(lambda x: x[3] == self.huowu_mingzi,
                                 self.cur.execute('''SELECT * FROM 'окончание аренды';''').fetchall()))
        self.jie_anniu = QPushButton('Взять в аренду', self)  # кнопка для взятия в аренду
        self.jie_anniu.setGeometry(20, 160, 150, 30)
        if len(jie_kaishi) != len(jie_jieshu):
            self.jie_anniu.setEnabled(False)
        self.jie_anniu.clicked.connect(self.jie)

        jie_kaishi = list(filter(lambda x: self.yonghu in x, jie_kaishi))
        jie_jieshu = list(filter(lambda x: self.yonghu in x, jie_jieshu))
        self.huan_anniu = QPushButton('Вернуть товар', self)  # кнопка для возвращения
        self.huan_anniu.setGeometry(230, 160, 150, 30)
        if len(jie_kaishi) == len(jie_jieshu):
            self.huan_anniu.setEnabled(False)
        self.huan_anniu.clicked.connect(self.huan)

    def jie(self):  # взять в аренду
        yiqian = int(self.cur.execute('''SELECT * FROM 'начало аренды';''').fetchall()[-1][0])
        xianzai = str(yiqian + 1)
        xianzai = '0' * (6 - len(xianzai)) + xianzai
        date, time = str(dt.datetime.now()).split()
        date = '.'.join(reversed(date.split('-')))
        time = time[:time.index('.')]
        date_time = ' '.join([date, time])

        a = "'" + "', '".join([xianzai, date_time, self.yonghu, self.huowu_mingzi]) + "'"
        self.cur.execute(f'''INSERT INTO 'начало аренды' VALUES({a})''')
        self.con.commit()

        self.jie_anniu.setEnabled(False)
        self.huan_anniu.setEnabled(True)
        self.taidu.setText('Товар взят в аренду!')
        self.taidu.resize(self.taidu.sizeHint())

        date, time = str(dt.datetime.now()).split()
        date = '.'.join(reversed(date.split('-')))
        time = time[:time.index('.')]
        data = [' '.join([self.mingzi, self.fuqin_mingzi]), date, time, self.huowu_mingzi, self.artikul, self.jiage,
                self.dazhe]
        message(self.dianziyoujian, 2, data)

        self.kaishi_shijian.append(dt.datetime.now())

    def huan(self):  # вернуть товар
        yiqian = int(self.cur.execute('''SELECT * FROM 'окончание аренды';''').fetchall()[-1][0])
        xianzai = str(yiqian + 1)
        xianzai = '0' * (6 - len(xianzai)) + xianzai
        date, time = str(dt.datetime.now()).split()
        date = '.'.join(reversed(date.split('-')))
        time = time[:time.index('.')]
        date_time = ' '.join([date, time])

        a = "'" + "', '".join([xianzai, date_time, self.yonghu, self.huowu_mingzi]) + "'"
        self.cur.execute(f'''INSERT INTO 'окончание аренды' VALUES({a})''')
        self.con.commit()

        self.jie_anniu.setEnabled(False)
        self.taidu.setText('Товар возвращен из аренды!')
        self.taidu.resize(self.taidu.sizeHint())

        jieshijian = str(int(str(dt.datetime.now() - self.kaishi_shijian[0]).split(':')[1]))
        a = "'" + "', '".join(
            [xianzai, date_time, self.yonghu, str(self.dazhe), jieshijian, self.huowu_mingzi, str(self.jiage),
             str(self.jiage * (1 - self.dazhe / 100))]) + "'"
        self.cur.execute(f'''INSERT INTO 'оплата аренды' VALUES({a})''')
        self.con.commit()

        date, time = str(dt.datetime.now()).split()
        date = '.'.join(reversed(date.split('-')))
        time = time[:time.index('.')]
        data = [' '.join([self.mingzi, self.fuqin_mingzi]), date, time, self.huowu_mingzi, self.artikul, self.jiage,
                self.dazhe]
        message(self.dianziyoujian, 3, data)

        self.jie_anniu.setEnabled(True)
        self.huan_anniu.setEnabled(False)


class MainWindow(QWidget):
    def __init__(self, mingzi, fuqin_mingzi, dianziyoujian):
        super().__init__()
        self.list_of_tables = ['Номенклатура', 'Прайс по тарифам', 'Пользователи', 'ввод в эксплуатацию товара',
                               'вывод из эксплуатации товара', 'начало аренды', 'окончание аренды',
                               'оплата аренды', 'сотрудники']
        self.mingzi = mingzi
        self.fuqin_mingzi = fuqin_mingzi
        self.dianziyoujian = dianziyoujian
        self.con = sqlite3.connect('timu3.db')
        self.cur = self.con.cursor()
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle("Добро пожаловать в информационную систему!")

        self.biaoge = QTableWidget(self)
        self.biaoge.setGeometry(10, 35, 580, 320)
        self.biaoge.setSortingEnabled(True)

        self.xuanze_biaoge = QComboBox(self)
        self.xuanze_biaoge.move(10, 7)
        self.xuanze_biaoge.addItems(self.list_of_tables)

        self.fasong_anniu = QPushButton('Отправить отчет о работе системы на эл. почту', self)
        self.fasong_anniu.setGeometry(205, 5, 280, 25)
        self.fasong_anniu.clicked.connect(self.fasong)

        self.huaqilai_biaoge()
        self.xuanze_biaoge.currentIndexChanged.connect(self.huaqilai_biaoge)

        self.cunzai_anniu = QPushButton('Сохранить', self)
        self.cunzai_anniu.setGeometry(490, 5, 100, 25)
        self.cunzai_anniu.clicked.connect(self.cunzai)

        self.tianjia_anniu = QPushButton('Добавить стрoку', self)
        self.tianjia_anniu.setGeometry(10, 360, 150, 25)
        self.tianjia_anniu.clicked.connect(self.tianjia)

        self.quechu_anniu = QPushButton('Удалить строку', self)
        self.quechu_anniu.setGeometry(440, 360, 150, 25)
        self.quechu_anniu.clicked.connect(self.quechu)

    def fasong(self):
        compose_file()

        date, time = str(dt.datetime.now()).split()
        date = '.'.join(reversed(date.split('-')))
        data = [' '.join([self.mingzi, self.fuqin_mingzi]), date]
        message(self.dianziyoujian, 1, data)

    def quechu(self):  # удаление выделенной строки
        if self.biaoge.selectionModel().selectedRows():
            xuanze_rows = self.biaoge.selectionModel().selectedRows()

            valid = QMessageBox.question(
                self, '', 'Действительно удалить выбранные элементы?', QMessageBox.Yes, QMessageBox.No)

            if valid == QMessageBox.Yes:
                while xuanze_rows:
                    self.biaoge.removeRow(xuanze_rows[0].row())
                    del xuanze_rows[0]

    def tianjia(self):  # добавление пустой строки
        self.biaoge.insertRow(self.biaoge.rowCount())

    def cunzai(self):  # сохранение
        biaoge_mingzi = self.xuanze_biaoge.currentText().lower()
        xin_data = list()

        for i in range(self.biaoge.rowCount()):
            a = list()
            for j in range(self.biaoge.columnCount()):
                a.append(self.biaoge.item(i, j).text())
            xin_data.append(a)

        self.cur.execute(f'''DELETE FROM '{biaoge_mingzi}' ''')

        for i in range(len(xin_data)):
            a = "'" + "', '".join(xin_data[i]) + "'"
            self.cur.execute(
                f'''INSERT INTO '{biaoge_mingzi}' VALUES({a})''')
        self.con.commit()

    def huaqilai_biaoge(self):  # отрисовнка таблицы
        biaoge_mingzi = self.xuanze_biaoge.currentText().lower()

        self.biaoge.clear()

        dangshi_biaoge = self.cur.execute(f'''SELECT * FROM '{biaoge_mingzi}' ''').fetchall()
        try:
            self.biaoge.setRowCount(len(dangshi_biaoge))
            self.biaoge.setColumnCount(len(dangshi_biaoge[0]))

            tablenames = list(
                map(lambda x: x[1], self.cur.execute(f"""PRAGMA table_info("{biaoge_mingzi}")""").fetchall()))
            self.biaoge.setHorizontalHeaderLabels(tablenames)

            for i in range(len(dangshi_biaoge[0])):
                self.biaoge.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)
            self.biaoge.horizontalHeader().setMinimumSectionSize(560 // len(dangshi_biaoge[0]))

            for i in range(len(dangshi_biaoge)):
                for j in range(len(dangshi_biaoge[0])):
                    self.biaoge.setItem(i, j, QTableWidgetItem(str(dangshi_biaoge[i][j])))
        except IndexError:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    LoginWindow = LoginWindow()
    LoginWindow.show()
    sys.exit(app.exec())
