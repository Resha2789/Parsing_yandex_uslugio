from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject
from myLibrary.My_pyqt5 import Avito_ui_parsing
from myLibrary.InitialData import InitialData
from myLibrary.UslugioLibrary.ParsingThreading import UslugioThreading
from myLibrary.UslugioLibrary.FindProxy import FindProxyThreading
from myLibrary import Loger, Ecxel, RequestTime, TesseractImg, DriverChrome
import re
import os
import win32com.client
import threading

# Для иконки в приложении
try:
    # Включите в блок try/except, если вы также нацелены на Mac/Linux
    from PyQt5.QtWinExtras import QtWin  # !!!

    myappid = 'mycompany.myproduct.subproduct.version'  # !!!
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)  # !!!
except ImportError:
    pass


class Communicate(QObject):
    progressBar = QtCore.pyqtSignal(object)
    proxyUpdate = QtCore.pyqtSignal(object)
    change_key_words = QtCore.pyqtSignal(object)
    change_textBrowser_console = QtCore.pyqtSignal(object)
    pushButton_uslugio_stop_enabled = QtCore.pyqtSignal(object)


class MainWindow(QtWidgets.QMainWindow, Avito_ui_parsing.Ui_MainWindow, Loger.OutLogger, Loger.OutputLogger, InitialData,
                 RequestTime.RequestTime, TesseractImg.TesseractImg):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.load_md()
        self.uslugio_threading = None
        self.uslugio_find_proxy_threading = None
        self.log = False

        # Конектим пользовательский сигнал на MainWindow
        self.Commun = Communicate()

        self.set_value()
        self.set_connect()
        # self.set_event_filter()

    def set_value(self):
        # Устанавливаем иконку
        self.setWindowIcon(QtGui.QIcon("""Все для сборщика данных/icon_phone.ico"""))
        # Город
        self.lineEdit_uslugio_city.setText(self.inp_city)
        # Ключевые слова
        self.textBrowser_uslugio_key_words.setText(self.key_words_str)
        # Показывать браузер
        self.checkBox_uslugio_show_brawser.setChecked(self.inp_show_browser)
        # Дерриктория файла excel uslugio
        if os.path.isfile(self.inp_path_excel_uslugio):
            self.pushButton_file_excel_path.setText(f"Файл Excel: {self.inp_path_excel_uslugio}")
            # Кнопка открытия файла Excel
            self.pushButton_file_excel_open.setText(f"Отк. {self.inp_name_excel_avito}")
        # Продолжить файл excel uslugio
        self.checkBox_continuation.setChecked(self.inp_continuation_uslugio)
        # Начать занова запись в excel uslugio
        self.checkBox_rewriting.setChecked(self.inp_rewriting_uslugio)
        # Данные вручную указываем откуда брать
        self.checkBox_uslugio_auto_input.setChecked(self.inp_auto_get_proxy)
        # Сайт указанный вручную для получения прокси
        self.checkBox_uslugio_manual_input.setChecked(self.inp_manual_get_proxy)
        # Показать все логи
        self.checkBox_show_all_logs.setChecked(self.inp_show_all_logs)
        # Подсказка что перед использованием программы нужно установить tesseract-ocr
        self.textBrowser_console.append("Привет!"
                                        "<br>Для использования данной программы нужно установить: <b style='color: rgb(0, 0, 255);'>tesseract-ocr</b>"
                                        "<br>Установочный файл лежит в папке: <b style='color: rgb(0, 0, 255);'>Все для сборщика данных/tesseract-ocr-setup-3.02.02.exe</b>"
                                        )
        # "<br>Ccылки на бесплатные прокси сервера:"
        # "<br><b style='font: 75 14pt Arial'>https://awmproxy.com/freeproxy.php</b>"
        # "<br><b style='font: 75 14pt Arial'>https://advanced.name/ru/freeproxy</b>"

    def set_connect(self):
        # СТАРТ парсинга
        self.pushButton_start.clicked.connect(self.start_main_threading)
        # СТОП парсинг
        self.pushButton_stop.clicked.connect(self.stop_main_threading)
        # Выбыр файла Excel uslugio
        self.pushButton_file_excel_path.clicked.connect(self.set_path_file_excel)
        # Продолжить запись uslugio
        self.checkBox_continuation.clicked.connect(self.check_box_continuation)
        # Перезаписать файл uslugio
        self.checkBox_rewriting.clicked.connect(self.check_box_rewriting)
        # Кнопка открытия Excel файла uslugio
        self.pushButton_file_excel_open.clicked.connect(self.file_excel_open)

        # Обновляем прогрес бар
        self.Commun.progressBar.connect(self.progressBar)
        # Обновляем прокси сервера
        self.Commun.proxyUpdate.connect(self.proxyUpdate)
        # Обновляем textBrowser_uslugio_key_words
        self.Commun.change_key_words.connect(self.set_key_words)
        # Обновляем change_textBrowser_console (консоль логов)
        self.Commun.change_textBrowser_console.connect(self.set_textBrowser_console)
        # Активируем или деактивируем кнопку pushButton_start
        self.Commun.pushButton_uslugio_stop_enabled.connect(self.set_enabled_pushButton_uslugio_stop)

        # Вывод сообщений в консоль
        self.OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        self.OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)

        # Записываем город
        self.lineEdit_uslugio_city.textChanged.connect(self.set_city)

        # Записываем ключевые слова
        self.textBrowser_uslugio_key_words.textChanged.connect(self.set_key_words)

        # Записываем прокси сервера
        self.textEdit_uslugio_proxy.textChanged.connect(self.set_proxy)

        # Записываем отображение браузера
        self.checkBox_uslugio_show_brawser.clicked.connect(self.set_show_browser)

        # Сайт указанный вручную для получения прокси
        self.pushButton_uslugio_set_manual_proxy.clicked.connect(self.set_manual_proxy)

        # Данные вручную указываем откуда брать
        self.checkBox_uslugio_auto_input.clicked.connect(self.set_check_auto_input)

        # Сайт указанный вручную для получения прокси
        self.checkBox_uslugio_manual_input.clicked.connect(self.set_check_manual_input)

        # Показать все логи
        self.checkBox_show_all_logs.clicked.connect(self.set_check_show_all_logs)

    def set_event_filter(self):

        # EventFilter на виджет ключевые слова
        self.textBrowser_uslugio_key_words.installEventFilter(self)

    def eventFilter(self, source, event):
        # Вес на роторе
        if source.objectName() == self.textBrowser_uslugio_key_words.objectName():
            if event.type() == QtCore.QEvent.Leave:
                print(self.textBrowser_uslugio_key_words.toPlainText())

        return False

    def start_uslugio_find_proxy(self):
        pass
        # Запускаем дополнительный поток Uslugio.com
        if self.uslugio_find_proxy_threading is None:
            self.uslugio_find_proxy_threading = FindProxyThreading(mainWindow=self,
                                                                          url='https://advanced.name/ru/freeproxy?type=https&page=1',
                                                                          browser=False,
                                                                          js='Все для сборщика данных/javaScript/ProxyJsLibrary.js')

        self.log = True
        self.uslugio_find_proxy_threading.start()

    def start_main_threading(self):

        if not os.path.isfile(self.inp_path_excel_uslugio):
            print(f"$<b style='color: rgb(255, 0, 0);'>Выберите файл Excel для записи!</b>")
            return

        if not self.find_tesseract():
            return

        if self.inp_manual_get_proxy:
            try:
                proxy = open(self.inp_path_manual_proxy).read()
                if not re.search(r'\d+[.]\d+[.]\d+[.]\d+[:]\d+', proxy):
                    print(f"$В файле не найдены прокси сервера!")
                    return
            except:
                print(f"$В файле не найдены прокси сервера!")
                return

        # if not self.check_time():
        #     return

        self.parsing_avito = True
        # self.start_uslugio_find_proxy()

        if self.inp_continuation_uslugio:
            excel = Ecxel.ExcelWrite(mainWindow=self)
            excel.load_work_book()
            if not excel.read_from_excel():
                pass

        # Запускаем дополнительный поток Uslugio.com
        if self.uslugio_threading is None:
            self.uslugio_threading = UslugioThreading(mainWindow=self,
                                                      proxy=self.inp_proxy,
                                                      browser=self.inp_show_browser,
                                                      js='Все для сборщика данных/javaScript/AvitoJsLibrary.js')

        self.log = True
        self.uslugio_threading.start()
        self.pushButton_start.setEnabled(False)

    def stop_main_threading(self):

        threading.Thread(target=self.uslugio_threading.stop_threading).start()

        self.pushButton_stop.setEnabled(False)
        self.pushButton_start.setEnabled(False)

    def append_log(self, text, severity):
        if len(text) > 3:
            if severity == self.Severity.ERROR:
                # self.textBrowser_console.append(text)
                if self.inp_show_all_logs:
                    self.textBrowser_console.append(f"<br><b style='font: 8pt Arial'>{text}</b>")
                    self.update_json()
                    return
                if re.search(r'^[$](.*)', text):
                    self.textBrowser_console.append(text)
                    return
            else:
                # self.textBrowser_console.append(text)
                if self.inp_show_all_logs:
                    self.textBrowser_console.append(re.sub(r'[$]', '', text))
                    return
                if re.search(r'^[$](.*)', text):
                    self.textBrowser_console.append(re.findall(r'^[$](.*)', text)[0])
                    return

    def set_textBrowser_console(self, data):
        if data[1] > 0:
            cursor = self.textBrowser_console.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(data[0])
        else:
            # f"$<b style='color: rgb(0, 0, 0);'>data[0]</b>"
            self.textBrowser_console.append(f"<br><b style='color: rgb(0, 0, 0);'>{data[0]}</b>")

    def closeEvent(self, event):
        self.uslugio_threading: DriverChrome.StartDriver

        self.update_json()
        self.parsing_avito = False
        if self.uslugio_threading is not None:
            try:
                self.uslugio_threading.kill_geckodriver()
            except Exception as error:
                return
        self.close()

    def set_city(self, val):
        self.inp_city = val

    def set_key_words(self, data=None):
        if data is None:
            val = self.textBrowser_uslugio_key_words.toPlainText()
            data = re.split(r'[,.]+\s*', val)
            self.inp_key_words = []
            for i in data:
                if len(i) > 1:
                    self.inp_key_words.append(i)
            # print(self.inp_key_words)

        else:
            # Ключевые слова
            self.key_words_str = ''
            for i in self.inp_key_words:
                if i == data:
                    self.key_words_str += f"<b style='color: rgb(0, 203, 30);'>{i}</b>, "
                else:
                    self.key_words_str += i + ', '
            if len(self.key_words_str) > 0:
                self.key_words_str = re.sub(r'(,\s)$', '', self.key_words_str)
                self.textBrowser_uslugio_key_words.setText(f"{self.key_words_str}")

    def set_proxy(self):
        data = re.split(r'[,]+\s*|\n', self.textEdit_uslugio_proxy.toPlainText())
        self.inp_proxy = []
        self.verified_proxies = []
        for i in data:
            if len(i) > 1:
                self.inp_proxy.append(i)
                self.verified_proxies.append(i)

    def set_show_browser(self):
        if self.checkBox_uslugio_show_brawser.isChecked():
            self.inp_show_browser = True
        else:
            self.inp_show_browser = False
        # print(self.inp_key_words)
        # print(self.inp_proxy)

    def progressBar(self, data):
        percent = (100 / (data['items'] / (data['i'] + 1)))
        self.progressBar_uslugio.setValue(int(percent))

    def proxyUpdate(self, data):
        self.inp_proxy = data
        self.proxy_str = ''
        for i in data:
            self.proxy_str += f"{i}\n"
        self.textEdit_uslugio_proxy.setText(self.proxy_str)

    def set_path_file_excel(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Выберите файл: Excel", directory='')
        # print(directory[0])
        # открыть диалог выбора директории и установить значение переменной
        if directory[0]:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.pushButton_file_excel_path.setText(f"Файл Excel: {directory[0]}")
            self.inp_path_excel_uslugio = directory[0]
            self.inp_name_excel_avito = re.sub(r'.*[/]+', '', directory[0])
            # Кнопка открытия файла Excel
            self.pushButton_file_excel_open.setText(f"Отк. {self.inp_name_excel_avito}")
            self.update_json()

    def check_box_continuation(self):
        print(100)
        if self.checkBox_continuation.isChecked():
            self.inp_continuation_uslugio = True
            self.inp_rewriting_uslugio = False
            self.checkBox_rewriting.setChecked(False)
        else:
            self.inp_continuation_uslugio = False
            self.inp_rewriting_uslugio = True
            self.checkBox_rewriting.setChecked(True)
        self.update_json()

    def check_box_rewriting(self):
        print(100)
        if self.checkBox_rewriting.isChecked():
            self.inp_continuation_uslugio = False
            self.inp_rewriting_uslugio = True
            self.checkBox_continuation.setChecked(False)
        else:
            self.inp_continuation_uslugio = True
            self.inp_rewriting_uslugio = False
            self.checkBox_continuation.setChecked(True)
        self.update_json()

    def file_excel_open(self):
        if self.uslugio_threading is not None:
            # Запись в EXcel
            self.write_to_excel()
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.Run(f""""{self.inp_path_excel_uslugio}""")

    def write_to_excel(self):
        # Запись в файл Excel
        excel = Ecxel.ExcelWrite(mainWindow=self)
        if not excel.load_work_book():
            return False
        if not excel.write_to_excel(self.out_avito_all_data):
            return False
        return True

    def set_manual_proxy(self):
        file_path = os.path.abspath(self.inp_path_manual_proxy)
        os.startfile(file_path)

    def set_check_auto_input(self):
        if self.checkBox_uslugio_auto_input.isChecked():
            self.inp_auto_get_proxy = True
            self.inp_manual_get_proxy = False
            self.checkBox_uslugio_manual_input.setChecked(False)
        else:
            self.inp_auto_get_proxy = False
            self.inp_manual_get_proxy = True
            self.checkBox_uslugio_manual_input.setChecked(True)
        self.update_json()

    def set_check_manual_input(self):
        if self.checkBox_uslugio_manual_input.isChecked():
            self.inp_auto_get_proxy = False
            self.inp_manual_get_proxy = True
            self.checkBox_uslugio_auto_input.setChecked(False)
        else:
            self.inp_auto_get_proxy = True
            self.inp_manual_get_proxy = False
            self.checkBox_uslugio_auto_input.setChecked(True)
        self.update_json()

    def set_check_show_all_logs(self):
        self.inp_show_all_logs = self.checkBox_show_all_logs.isChecked()
        self.update_json()

    def set_enabled_pushButton_uslugio_stop(self, data):
        self.pushButton_stop.setEnabled(data)
        self.webdriver_loaded = data
