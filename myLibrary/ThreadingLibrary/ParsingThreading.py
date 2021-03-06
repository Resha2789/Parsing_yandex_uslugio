import time

from myLibrary.Parsing import ParsingUslugio
from PyQt5.QtCore import QThread
from myLibrary import MainWindow, Slug
import threading


class UslugioThreading(QThread, ParsingUslugio, Slug.Slugify):
    def __init__(self, mainWindow=None, *args, **kwargs):
        self.url = ''
        self.mainWindow = mainWindow
        self.key_word = ''
        self.working = False
        super(UslugioThreading, self).__init__(mainWindow=mainWindow, uslugioThreading=self, *args, **kwargs)

    def run(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        self.working = True

        threading.Thread(target=self.tim_out_thread).start()

        for i in m.inp_key_words:
            if self.stop_parsing or not m.parsing_uslugio_yandex:
                break

            print(f"$<b style='color: rgb(16, 28, 255);'>Парсим по ключевому слову: {i}</b>")

            # Посылаем сигнал на главное окно в textBrowser_uslugio_key_words
            m.Commun.change_key_words.emit(i)

            # https://uslugi.yandex.ru/54-yekaterinburg/category?from=suggest&p=0&text=ОПС
            self.key_word = i
            index_city = m.inp_cities_rus.index(m.inp_city)
            m.cod_city_eng = m.inp_cities_eng[index_city]
            self.url = f"https://uslugi.yandex.ru{m.cod_city_eng}/category?from=suggest&p=0&text={i}"

            # Запус WebDriverChrome
            if not self.star_driver(url=self.url, proxy=False):
                return

            # Устанавливаем на вебсайт скрипты
            if not self.set_library():
                return

            # Запускаем цикл парсинга uslugio
            self.start_parsing_yandex()

            # Посылаем сигнал на главное окно в прогресс бар avito
            m.Commun.progressBar.emit({'i': 0, 'items': 100})

        if m.parsing_uslugio_yandex:
            m.stop_main_threading()

        self.working = False

    def stop_threading(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        m.log = False
        m.parsing_uslugio_yandex = False
        save = False
        total = 0
        dots = 1

        # Активируем кнопку остановки
        if m.webdriver_loaded:
            m.Commun.pushButton_uslugio_stop_enabled.emit(False)

        while True:
            if not self.working:
                # Запись в EXcel
                if m.write_to_excel():
                    save = True
                else:
                    save = False

                if self.driver is not None:
                    self.driver.quit()

                print("Программа завершена")

                self.kill_geckodriver()
                break

            total += 10

            if dots > 5:
                dots = 1

            m.Commun.change_textBrowser_console.emit([f"Ждите, идет процесс завершения программы" + "." * dots, dots])
            dots += 1
            # Посылаем сигнал на главное окно в прогресс бар uslugio
            m.Commun.progressBar.emit({'i': total, 'items': 100})
            time.sleep(2)

        m.log = True

        print(f"$Сбор данных закончили\n$Всего собрано: {len(m.out_all_data)}")
        if save:
            print(f"$Данные сохранились успешно {m.inp_name_excel_avito}")
        else:
            print(f"$Данные не сохранились!")

        # Посылаем сигнал на главное окно в прогресс бар uslugio
        m.Commun.progressBar.emit({'i': 99, 'items': 100})
        m.pushButton_start.setEnabled(True)
        m.uslugio_yandex_threading = None
