import re
from selenium import webdriver
from myLibrary import ProxyCheck
from myLibrary import MainWindow
from datetime import datetime, timedelta
import time
import os
import psutil


# Запуск webDriverFirefox
class StartDriver(ProxyCheck.ProxyCheck):
    def __init__(self, mainWindow=None, url='', proxy=None, browser=False):
        super().__init__()
        self.mainWindow = mainWindow
        m: MainWindow.MainWindow
        m = self.mainWindow
        self.driver_path = 'Все для сборщика данных/geckodriver_64.exe'
        self.driver = None
        self.show_browser = browser
        self.driver_closed = False
        self.set_url = url
        self.total_person = None
        self.time_out = 0
        self.proxy_installed = False
        self.proc_name = "geckodriver_64.exe"

    def kill_geckodriver(self):
        try:
            for proc in psutil.process_iter():
                # check whether the process name matches
                if proc.name() == self.proc_name:
                    proc.kill()
        except Exception as error:
            return

    def star_driver(self, url=None, proxy=False):
        m: MainWindow.MainWindow
        m = self.mainWindow

        if not m.parsing_avito:
            return

        self.set_url = url
        m.proxy_server_installed = False

        time.sleep(3)
        try:
            # Запускаем webDriverFirefox
            profile = self.get_profile()[0]
            options = self.get_profile()[1]
            if self.driver is None:
                self.driver = webdriver.Firefox(executable_path=self.driver_path,
                                                firefox_profile=profile,
                                                options=options,
                                                service_log_path=os.path.devnull)
                print(f"DRIVER START {self.set_url}")
            else:
                self.set_proxy(proxy=proxy, change=False)
                self.driver.refresh()
                print(f"DRIVER REFRESH {self.set_url}")

            self.driver.maximize_window()
            self.driver.get(url)

            print("Заргузка страницы успешна прошла.")

        except Exception as detail:
            # Если разрядность системы не 64бит то запускаем весрию geckodriver_32
            if re.search(r'Expected browser binary location', str(detail)) or re.search(r'geckodriver_64', str(detail)):
                self.driver_path = 'Все для сборщика данных/geckodriver_32.exe'
                self.proc_name = "geckodriver_32.exe"
                return self.star_driver(url=self.set_url, proxy=proxy)

            print(f"ERROR star_driver: {self.set_url}", detail)
            return self.star_driver(url=self.set_url, proxy=proxy)

        return True

    # Timeout update website 5min
    def tim_out_thread(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        while m.parsing_avito:
            try:
                if not m.parsing_avito:
                    return
                if self.total_person != len(m.out_phone_number):
                    self.total_person = len(m.out_phone_number)
                    self.time_out = datetime.now() + timedelta(minutes=5)
                    # print(f"START TIME_OUT_THREAD {str(self.time_out)}")

                if datetime.now() > self.time_out:
                    self.time_out = datetime.now() + timedelta(minutes=5)
                    if m.uslugio_threading.driver is not None:
                        print(f"TIME_OUT_THREAD!")
                        print(f"DRIVER REFRESH {m.uslugio_threading.set_url}")
                        self.set_proxy(proxy=False, change=False)
                        m.uslugio_threading.driver.refresh()
                time.sleep(5)

            except Exception as detail:
                print(f"ERROR tim_out_thread:", detail)
                print("Перезапускаем tim_out_thread")
                self.driver = None

                if m.parsing_avito:
                    return self.tim_out_thread()
                else:
                    return

        return

    def get_profile(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.25")

        # # Disable CSS
        # profile.set_preference('permissions.default.stylesheet', 2)
        # # Disable images
        # profile.set_preference('permissions.default.image', 2)
        # # Disable Flash
        # profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        options = webdriver.FirefoxOptions()

        # Показать браузер
        if not self.show_browser:
            # Не показываем веб браузер
            # webdriver.Firefox.
            options.add_argument('-headless')

        return [profile, options]

    def set_proxy(self, proxy=True, change=False, http_addr='', http_port=0, ssl_addr='', ssl_port=0, socks_addr='', socks_port=0):

        m: MainWindow.MainWindow
        m = self.mainWindow

        if proxy:
            if change or len(m.verified_proxies) == 0:
                while len(m.verified_proxies) == 0:
                    if not m.parsing_avito:
                        return
                    print(f"Ждем прокси...")
                    time.sleep(2)
                else:
                    print(f"Работаем через прокси: {m.verified_proxies[0]}")
                    ssl_addr = m.verified_proxies[0].split(':')[0]
                    ssl_port = int(m.verified_proxies[0].split(':')[1])

                    m.uslugio_used_proxies.append(m.verified_proxies[0])
                    m.verified_proxies = m.verified_proxies[1:]
                    m.Commun.proxyUpdate.emit(m.verified_proxies)
            else:
                ssl_addr = m.verified_proxies[0].split(':')[0]
                ssl_port = int(m.verified_proxies[0].split(':')[1])

        self.driver.execute("SET_CONTEXT", {"context": "chrome"})

        try:
            self.driver.execute_script("""
              Services.prefs.setIntPref('network.proxy.type', 1);
              Services.prefs.setCharPref("network.proxy.http", arguments[0]);
              Services.prefs.setIntPref("network.proxy.http_port", arguments[1]);
              Services.prefs.setCharPref("network.proxy.ssl", arguments[2]);
              Services.prefs.setIntPref("network.proxy.ssl_port", arguments[3]);
              Services.prefs.setCharPref('network.proxy.socks', arguments[4]);
              Services.prefs.setIntPref('network.proxy.socks_port', arguments[5]);
              """, http_addr, http_port, ssl_addr, ssl_port, socks_addr, socks_port)

        finally:
            self.driver.execute("SET_CONTEXT", {"context": "content"})


class Execute(StartDriver):
    def __init__(self, mainWindow=None, url='', proxy=None, browser=False, js=''):
        super().__init__(mainWindow=mainWindow, url=url, proxy=proxy, browser=browser)
        self.mainWindow = mainWindow
        self.count_recurs = 0
        self.js = js

    # Добавляем на страницу свою библиотеку js
    def set_library(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        if not m.parsing_avito:
            return

        try:
            # Считываем скрипты
            library_js = open(self.js, 'r', encoding='utf-8').read()

            # Устанавливаем в нутри <body> последним элемент <script> </script> </body>
            # time.sleep(5)  # Останавливаем дальнейшее выполнения кода на 5 секунд

            # Внедряем скрирт set_library(data) в веб страницу
            self.driver.execute_script("""      
                script_set_library = function set_library(data) {
                        if ($('body').length != 0) {
                            var scr = document.createElement('script');
                            scr.textContent = data;
                            document.body.appendChild(scr);

                            return true;
                        }
                            return false;
                        }

                var scr = document.createElement('script');
                scr.textContent = script_set_library;
                document.body.appendChild(scr);
                
                script_check_function = function check_function(array){
                            var data = [];
                            for (var i = 0; i < array.length; i++) {
                                if (new Function('return typeof ' + array[i])() !== 'undefined') {
                                    console.log('Функция с именем ' + array[i] + ' существует!')
                                }
                                else{
                                    console.log('Функция с именем ' + array[i] + 'НЕ СУЩЕСТВУЕТ!')
                                    data.push(array[i]);
                                }
                            }
                            return data;
                        }
                
                scr = document.createElement('script');
                scr.textContent = script_check_function;
                document.body.appendChild(scr);
                
                if (!window.jQuery){
                    scr = document.createElement('script');
                    scr.type = 'text/javascript';
                    scr.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
                    document.head.appendChild(scr);
                }
            """)

            # Запускаем ранее внедренный скрипт set_library(data)
            self.execute_js(tr=1, sl=1, data=f"set_library({[library_js]})")

            data = re.findall(r'function\s+(\w+)[(]', library_js)
            js_functions = self.execute_js(tr=0, sl=1, rt=True, data=f"check_function({data})")

            if type(js_functions) == list and len(js_functions) > 0:
                for i in js_functions:
                    print(f"Не найден {i}")
                raise Exception("Не все скрепты были внедрены на вебстраницу!")
            print(f"Все скрипты установлены")

            return True

        except FileNotFoundError:
            print(f'Файл скрипты не найден {self.js}')
            return False

        except Exception as detail:
            print("ERROR set_library:", detail)
            if m.parsing_avito:
                return self.star_driver(url=self.set_url)
            else:
                return

    # js_execute запускает внедренные скрипты на странице и получает от них ответ
    def execute_js(self, tr=0, sl=0, rt=False, t=0, exit_loop=False, data=None):
        """
        :param tr: int Количество рекурсией (количество попыток найти элемент)
        :param sl: int Количество секунд ожидать перед выполнения кода
        :param rt: Если параметр rt = True то возвращам полученый от скрипта значение
        :param t: Если элемент не найден то вернуть: 0 - Данных нет; 1 - 0; 2 - False;
        :param exit_loop: Если метод вызван внутри цикла то exit_loop=True завершит цикл
        :param data: Название скрипта
        :return: Возвращает ответ если rt=True
        """
        m: MainWindow.MainWindow
        m = self.mainWindow

        if sl > 0:
            time.sleep(sl)  # Засыпаем

        try:
            # Запускаем javaScript в браузере и получаем результат
            result = self.driver.execute_script(f"return {data}")
        except Exception as detail:
            if not m.parsing_avito:
                return
            print(f"EXCEPT execute_js: {data}")
            print("ERROR:", detail)
            if exit_loop:
                print("ERROR:", detail)
                return 'not execute'
            else:
                return self.star_driver(url=self.set_url)  # Рекурсия с темеже параметрами

        # Если результа False и count_recurs < tr засыпаем на 2 сек. и запускаем рекурсию (рекурсия на случие если элемент не успел появится)
        if not result and self.count_recurs < tr:
            self.count_recurs += 1  # Увеличиваем счетчик рекурсии на +1
            return self.execute_js(tr=tr, sl=sl, rt=rt, t=t, exit_loop=exit_loop, data=data)  # Рекурсия с темеже параметрами

        # Результат False то возвращам по условию значение (Данных нет, 0, False)
        if not result:
            if t == 0:
                result = 'Данных нет'
            if t == 1:
                result = 0
            if t == 2:
                result = False

        # Обнуляем счетчик количество рекурсии
        self.count_recurs = 0

        # Если параметр rt = True то возвращам полученый от скрипта значение
        if rt:
            return result
