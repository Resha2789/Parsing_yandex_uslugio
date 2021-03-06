from PyQt5.QtCore import QThread
from myLibrary import DriverChrome
from myLibrary import MainWindow
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
import locale
import re
import time

locale.setlocale(locale.LC_ALL, '')


class FindProxyThreading(QThread, DriverChrome.Execute):
    def __init__(self, mainWindow=None, *args, **kwargs):
        super(FindProxyThreading, self).__init__(mainWindow=mainWindow, *args, **kwargs)
        self.mainWindow = mainWindow
        m: MainWindow.MainWindow
        m = self.mainWindow
        self.url_proxy = kwargs.get('url')
        self.time_out_proxy = None
        self.working = False
        self.page = 1

    def run(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        self.working = True

        self.manual_input_and_check_proxy()

        self.stop_threading()

        self.working = False

    def stop_threading(self):

        try:
            if self.driver is not None:
                self.driver.quit()
                self.driver = None

        except Exception as error:
            print("ERROR stop_threading:", error)

    def manual_input_and_check_proxy(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        try:
            if not m.parsing_uslugio_yandex:
                return

            m.uslugio_proxy_finded = open(m.inp_path_manual_proxy).read().split('\n')

            for i in m.uslugio_proxy_finded:
                if not m.parsing_uslugio_yandex:
                    return

                if self.proxy_check('https://uslugi.yandex.ru', i):
                    if not i in m.verified_proxies and not i in m.uslugio_used_proxies:
                        m.verified_proxies.append(i)
                        # Посылаем сигнал на главное окно в прокси
                        m.Commun.proxyUpdate.emit(m.verified_proxies)
                        print(f"Подходящий прокси сервер найден")

            time.sleep(5)
            return self.manual_input_and_check_proxy()

        except Exception as error:
            print(f"ERROR manual_input_and_check_proxy {error}")
            time.sleep(5)

        return False