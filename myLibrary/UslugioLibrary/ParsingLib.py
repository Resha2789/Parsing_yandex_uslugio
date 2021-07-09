from selenium.webdriver.common.by import By
from selenium import webdriver
from myLibrary import MainWindow, DriverChrome, TesseractImg
from myLibrary.UslugioLibrary import ParsingThreading
import time


class ParsingUslugio(DriverChrome.Execute, TesseractImg.TesseractImg):
    def __init__(self, mainWindow=None, uslugioThreading=None, *args, **kwargs):
        super(ParsingUslugio, self).__init__(mainWindow=mainWindow, *args, **kwargs)
        self.mainWindow = mainWindow
        self.uslugioThreading = uslugioThreading
        self.stop_parsing = False
        self.pause_parsing = False
        self.urls_in_page = None
        self.services_in_page = None
        self.current_page = 1
        self.last_page = None
        self.total_found = 0
        self.reload = False
        self.tesseract_img_init()

    def start_parsing_avito(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        u: ParsingThreading.UslugioThreading
        u = self.uslugioThreading

        self.driver: webdriver.Firefox
        time.sleep(10)

        try:
            firewall = self.execute_js(rt=True, t=2, exit_loop=True, data='firewall_title()')

            if firewall or  firewall == 'not execute':
                self.driver.delete_all_cookies()
                # self.set_proxy(proxy=True, change=False)
                # print(f"$<b style='color: rgb(16, 28, 255);'>Переход на следующию страницу {self.current_page}</b>")
                # u.url = f"https://www.avito.ru/{u.slugify(m.inp_city)}/predlozheniya_uslug?p={self.current_page}&q={u.key_word}"
                # self.driver.get(u.url)
                # # Устанавливаем на вебсайт скрипты
                # if not self.set_library():
                #     return
                # # self.set_proxy(proxy=True, change=False)
                # return self.start_parsing_avito()
                return self.up_date(proxy=False)

            # Всего найдено
            total = self.execute_js(rt=True, t=2, exit_loop=True, data='count_all_items()')
            print(f"$<b style='color: rgb(255, 196, 17);'>Объявления по запросу {u.key_word} в {m.inp_city} найдено: {total}</b>")

            while True:

                # Завершаем если парсинг остановлен
                if not m.parsing_avito:
                    return

                # Последняя страница
                self.last_page = self.execute_js(rt=True, t=2, exit_loop=True, data='last_page()')
                print(f'Последняя страница {self.last_page}')

                # Если last_page вернет False то обнавляем страницу
                if type(self.last_page) == bool:
                    print(f"$<b style='color: rgb(255, 0, 0);'>Последняя страница не найдена</b>")
                    self.last_page = 1

                print('Все заголовки и url предлогаемых услуг')
                # Все заголовки и url предлогаемых услуг
                result = self.execute_js(rt=True, t=2, exit_loop=True, data='get_title_and_url_items()')
                if type(result) != bool and result != 'not execute':
                    self.services_in_page = result[0]
                    self.urls_in_page = result[1]
                else:
                    self.last_page = self.current_page
                    return


                print(f"$<b style='color: rgb(255, 196, 17);'>По ключевому слову {u.key_word} на странице найдено: {len(self.urls_in_page)}</b>")

                # Количество предлогаемых услуг на странице
                total_in_page = len(self.urls_in_page)

                for i in range(0, total_in_page):
                    # Количество попыток
                    for retry in range(0, 5):
                        # Завершаем если парсинг остановлен
                        if not m.parsing_avito:
                            return

                        if retry >= 4:
                            self.driver.delete_all_cookies()
                            return self.up_date()

                        self.reload = False
                        if self.urls_in_page[i] not in m.out_url:

                            print('Открываем url клиента')
                            # Открываем url клиента
                            self.driver.get(self.urls_in_page[i])

                            # time.sleep(5)

                            print('Устанавливаем на страницу скрипты')
                            # Устанавливаем на страницу скрипты
                            if not self.set_library():
                                print('back continue')
                                continue

                            print('Контактное лицо')
                            # Контактное лицо
                            name = self.execute_js(sl=1, rt=True, t=2, exit_loop=True, data=f"name()")
                            if not name:
                                print('back continue')
                                continue

                            print('Показываем номер телефона')
                            # Показываем номер телефона
                            result = self.execute_js(sl=1, rt=True, t=2, exit_loop=True, data=f"click_phone()")
                            if not result:
                                print('back continue')
                                continue
                            if result == "Без звонков":
                                print("БEЗ ЗВОНКОВ")
                                break

                            print('Сохранаяем картинку номера телефона')
                            # Сохранаяем картинку номера телефона
                            phone_number_base64 = self.execute_js(sl=1, rt=True, t=2, exit_loop=True, data=f"get_phone_number_base64()")
                            if not phone_number_base64:
                                print('back continue')
                                continue

                            # Распознаем цифры с картинки
                            phone_number = self.image_to_string(phone_number_base64)
                            print(f"Кол. цифр в номере {len(str(phone_number))}")

                            # Если 0 то перезагружаем страницу
                            if phone_number == 0:
                                return self.up_date()

                            # Телефоны
                            m.out_phone_number.append(phone_number)

                            # Имена
                            m.out_full_name.append(name)

                            # Услуги
                            m.out_service.append(self.services_in_page[i])

                            # Города
                            m.out_city.append(m.inp_city)

                            # Ключевое слово
                            m.out_key_word.append(u.key_word)

                            # url клиента
                            m.out_url.append(self.urls_in_page[i])

                            # Массив данных для записи в Excel
                            m.out_avito_all_data.append(
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
                            # Посылаем сигнал на главное окно в прогресс бар uslugio
                            m.Commun.progressBar.emit({'i': i, 'items': total_in_page})
                            print(f"Найдено {i + 1} из {total_in_page}")
                            # Активируем кнопку остановки
                            if not m.webdriver_loaded:
                                m.Commun.pushButton_uslugio_stop_enabled.emit(True)

                            break
                        break

                if self.current_page == self.last_page:
                    # Посылаем сигнал на главное окно в прогресс бар uslugio
                    m.Commun.progressBar.emit({'i': total_in_page - 1, 'items': total_in_page})
                    print(f"Найдено {total_in_page} из {total_in_page}")
                    self.current_page = 1
                    self.total_found = 0
                    return
                else:

                    self.total_found += total_in_page
                    # Посылаем сигнал на главное окно в прогресс бар uslugio
                    m.Commun.progressBar.emit({'i': total_in_page - 1, 'items': total_in_page})
                    print(f"Найдено {total_in_page} из {total_in_page}")

                    # Активируем кнопку остановки
                    if not m.webdriver_loaded:
                        m.Commun.pushButton_uslugio_stop_enabled.emit(True)

                    if not self.reload:
                        self.current_page += 1

                    print(f"$<b style='color: rgb(16, 28, 255);'>Удаляем все куки. Переход на следующию страницу {self.current_page}</b>")
                    self.driver.delete_all_cookies()
                    u.url = f"https://www.avito.ru/{u.slugify(m.inp_city)}/predlozheniya_uslug?p={self.current_page}&q={u.key_word}"
                    self.driver.get(u.url)

                    time.sleep(5)

                    print('Устанавливаем на страницу скрипты')
                    # Устанавливаем на страницу скрипты
                    if not self.set_library():
                        return self.up_date()

        except Exception as detail:
            print("ERROR start_parsing_avito", detail)
            self.up_date()

    def up_date(self, proxy=False):
        try:
            m: MainWindow.MainWindow
            m = self.mainWindow

            u: ParsingThreading.UslugioThreading
            u = self.uslugioThreading

            print('UP_DATE')
            self.reload = True
            self.driver.delete_all_cookies()
            time.sleep(20)

            if not m.parsing_avito:
                return

            # Запус WebDriver
            if not self.star_driver(url=u.url, proxy=proxy):
                return

            time.sleep(40)

            # Устанавливаем на вебсайт скрипты
            if not self.set_library():
                return

            # Запускаем цикл парсинга uslugio
            self.start_parsing_avito()

        except Exception as detail:
            print("ERROR up_date:", detail)
            time.sleep(10)
            return
