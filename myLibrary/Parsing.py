from selenium.webdriver.common.by import By
from selenium import webdriver
from myLibrary import MainWindow, DriverChrome
from myLibrary.ThreadingLibrary import ParsingThreading
import time
import traceback
import sys


class ParsingUslugio(DriverChrome.Execute):
    def __init__(self, mainWindow=None, uslugioThreading=None, *args, **kwargs):
        super(ParsingUslugio, self).__init__(mainWindow=mainWindow, *args, **kwargs)
        self.mainWindow = mainWindow
        self.uslugioThreading = uslugioThreading
        self.stop_parsing = False
        self.pause_parsing = False
        self.urls_in_page = None
        self.services_in_page = None
        self.current_page = 0
        self.last_page = None
        self.total_found = 0
        self.reload = False

    def start_parsing_yandex(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        u: ParsingThreading.UslugioThreading
        u = self.uslugioThreading

        self.driver: webdriver.Firefox
        time.sleep(10)

        try:

            while True:

                # Завершаем если парсинг остановлен
                if not m.parsing_uslugio_yandex:
                    return

                print('Получаем все Имена, url и заголовки услуг')
                #                 # Получаем все Имена, url и заголовки услуг
                names_urls_titles = self.execute_js(rt=True, t=2, exit_loop=True, data='get_names_urls_titles()')

                names = names_urls_titles[1]
                titles = names_urls_titles[0]
                url = names_urls_titles[2]

                print(f"$<b style='color: rgb(255, 196, 17);'>По ключевому слову {u.key_word} на странице найдено: {len(url)}</b>")
                print('Устанавливаем прокси')
                if self.reload:
                    self.set_proxy(proxy=True, change=True)
                else:
                    self.set_proxy(proxy=True, change=False)

                # Проходим по всем клиентам
                for i in range(0, len(url)):
                    # Количество попыток
                    for retry in range(0, 5):
                        if retry == 4:
                            self.set_proxy(proxy=True)
                        # Завершаем если парсинг остановлен
                        if not m.parsing_uslugio_yandex:
                            return

                        if url[i] not in m.out_url:

                            print('Показываем номер телефона')
                            # Показываем номер телефона
                            result = self.execute_js(sl=1, rt=True, t=2, exit_loop=True, data=f"click_phone({i})")
                            if not result:
                                print('back continue')
                                continue
                            if result == 'not execute':
                                return self.up_date()

                            print('Сохранаяем номера телефона')
                            # Сохранаяем номера телефона
                            phone_number = self.execute_js(tr=3, sl=10, rt=True, t=2, exit_loop=True, data=f"get_phone_number()")
                            if type(phone_number) == bool:
                                print('back continue')
                                continue
                            if result == 'not execute':
                                return self.up_date()

                            print('Закрываем окошко с телефоном')
                            # Закрываем окошко с телефоном
                            result = self.execute_js(sl=1, rt=True, t=2, exit_loop=True, data=f"close_phone_bar()")
                            if not result:
                                print('back continue')
                                continue
                            if result == 'not execute':
                                return self.up_date()

                            # Телефоны
                            m.out_phone_number.append(phone_number)

                            # Имена
                            m.out_full_name.append(names[i])

                            # Услуги
                            m.out_service.append(titles[i])

                            # Города
                            m.out_city.append(m.inp_city)

                            # Ключевое слово
                            m.out_key_word.append(u.key_word)

                            # url клиента
                            m.out_url.append(url[i])

                            # Массив данных для записи в Excel
                            m.out_all_data.append(
                                [m.out_full_name[-1],
                                 m.out_service[-1],
                                 m.out_phone_number[-1],
                                 m.out_key_word[-1],
                                 m.out_city[-1],
                                 m.out_url[-1]])

                            print(f"$<b style='color: rgb(0, 203, 30);'>"
                                  f"{len(m.out_service)}. "
                                  f"{m.out_full_name[-1]}, "
                                  f"{m.out_service[-1]}, "
                                  f"{phone_number}, "
                                  f"{m.out_key_word[-1]}"
                                  f"</b>")

                            self.total_found += 1

                        # Активируем кнопку остановки
                        if not m.webdriver_loaded:
                            m.Commun.pushButton_uslugio_stop_enabled.emit(True)

                        # Посылаем сигнал на главное окно в прогресс бар uslugio
                        m.Commun.progressBar.emit({'i': i, 'items': len(url)})
                        print(f"Найдено {i + 1} из {len(url)}")

                        break

                print('Убираем прокси')
                self.set_proxy(proxy=False)

                # Проверяем на наличие следующей страницы
                check_next_page = self.execute_js(sl=1, rt=True, t=2, exit_loop=True, data=f"check_next_page()")
                if not check_next_page:
                    # Посылаем сигнал на главное окно в прогресс бар uslugio
                    m.Commun.progressBar.emit({'i': 99, 'items': 100})
                    print(f"$<b style='color: rgb(255, 196, 17);'>Парсинг по ключевому слову {u.key_word} завершили. Найдено {self.total_found}</b>")
                    self.current_page = 1
                    self.total_found = 0
                    return

                else:
                    # Если это не обновление страницы то увеличиваем на +1
                    if not self.reload:
                        self.current_page += 1

                    print(f"$<b style='color: rgb(16, 28, 255);'>Удаляем все куки. Переход на следующию страницу {self.current_page + 1}</b>")
                    self.driver.delete_all_cookies()
                    u.url = f"https://uslugi.yandex.ru{m.cod_city_eng}/category?from=suggest&p={self.current_page}&text={u.key_word}"
                    self.driver.get(u.url)
                    self.reload = False

                    time.sleep(5)

                    print('Устанавливаем на страницу скрипты')
                    # Устанавливаем на страницу скрипты
                    if not self.set_library():
                        return self.up_date()


        except Exception as detail:
            print("ERROR start_parsing_yandex", detail)
            traceback.print_exc(file=sys.stdout)
            # self.up_date()

    def up_date(self, proxy=False):
        try:
            m: MainWindow.MainWindow
            m = self.mainWindow

            u: ParsingThreading.UslugioThreading
            u = self.uslugioThreading

            print('UP_DATE')
            self.reload = True
            self.driver.delete_all_cookies()
            time.sleep(10)

            if not m.parsing_uslugio_yandex:
                return

            # Запус WebDriver
            if not self.star_driver(url=u.url, proxy=proxy):
                return

            time.sleep(5)

            # Устанавливаем на вебсайт скрипты
            if not self.set_library():
                return

            # Запускаем цикл парсинга parsing_yandex
            self.start_parsing_yandex()

        except Exception as detail:
            print("ERROR up_date:", detail)
            time.sleep(10)
            return
