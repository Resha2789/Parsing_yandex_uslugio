from PyQt5.QtCore import QThread
from myLibrary import DriverChrome
from myLibrary import MainWindow
import time, traceback, sys


class FindCityThreading(QThread, DriverChrome.Execute):
    def __init__(self, mainWindow=None, *args, **kwargs):
        super(FindCityThreading, self).__init__(mainWindow=mainWindow, *args, **kwargs)
        self.mainWindow = mainWindow
        m: MainWindow.MainWindow
        m = self.mainWindow
        self.url = kwargs.get('url')

    def run(self):
        m: MainWindow.MainWindow
        m = self.mainWindow

        m: MainWindow.MainWindow
        m = self.mainWindow

        try:

            # Количество попыток
            for retry in range(0, 5):
                # Запус WebDriverChrome
                if not self.star_driver(url=self.url, proxy=False):
                    continue
                time.sleep(10)

                # Устанавливаем на вебсайт скрипты
                if not self.set_library():
                    return

                print('Получаем города')
                # Получаем города
                data = self.execute_js(sl=1, rt=True, t=2, exit_loop=True, data=f"get_city_array()")
                if type(data) == bool:
                    print('back continue')
                    continue

                m.inp_cities_eng = data[0]
                m.inp_cities_rus = data[1]

                if self.driver is not None:
                    self.driver.quit()

                print("Поиск городов завершен")

                self.kill_geckodriver()

                # Посылаем сигнал на главное окно
                m.Commun.comboBox_city_change.emit(m.inp_cities_rus)

                break

            return

        except Exception as detail:
            print("ERROR FindCityThreading:", detail)
            traceback.print_exc(file=sys.stdout)
            return
