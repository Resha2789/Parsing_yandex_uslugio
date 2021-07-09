Компеляция в .exe
pyinstaller --onefile --noconsole --distpath D:\Фриланс\Авито\None\ -n Сборщик Main.py
pyinstaller --onefile --noconsole --icon "D:\Programming\Python\Parsing_uslugio_ru_64bit\Все для сборщика данных\icon_phone.ico" --distpath D:\Фриланс\Авито\Сборщик_данных_uslugio_64bit\ -n Сборщик_телефонов_64bit Main.py
pyinstaller --onefile --icon "D:\Programming\Python\Parsing_uslugio_ru_64bit\Все для сборщика данных\icon_phone.ico" --distpath D:\Фриланс\Авито\Сборщик_данных_uslugio_64bit\ -n Сборщик_телефонов_64bit Main.py

--hidden-import winapps ##

Конвертация ui в py
pyuic5 D:\Programming\Python\Goblin_drilling_v.2.2\Lib\site-packages\QtDesigner\Avito_parsing.ui -o myLibrary/My_pyqt5/Avito_ui_parsing.py

В библиотеке venv/Lib/site-packages/selenium/webdriver/common/service.py
изменил строку 77 добавил аргумент в subprocess.Popen add (shell = True) что бы не показывать консоли geckodriver

Используемые библиотеки
DAWG-Python	0.7.2	0.7.2
Pillow	8.2.0	8.2.0
PyQt5	5.15.4	5.15.4
PyQt5-Qt5	5.15.2	5.15.2
PyQt5-sip	12.9.0	12.9.0
Unidecode	1.2.0	1.2.0
altgraph	0.17	0.17
beautifulsoup4	4.9.3	4.9.3
cachetools	4.2.2	4.2.2
certifi	2021.5.30	2021.5.30
chardet	4.0.0	4.0.0
docopt	0.6.2	0.6.2
future	0.18.2	0.18.2
grpcio	1.38.1	1.38.1
idna	2.10	3.2
lxml	4.6.3	4.6.3
numpy	1.21.0	1.21.0
packaging	20.9	20.9
pefile	2021.5.24	2021.5.24
pip	21.1.2	21.1.3
plumbum	1.7.0	1.7.0
proto-plus	1.18.1	1.18.1
protobuf	3.17.3	3.17.3
psutil	5.8.0	5.8.0
pyasn1	0.4.8	0.4.8
pyasn1-modules	0.2.8	0.2.8
pyinstaller	4.3	4.3
pyinstaller-hooks-contrib	2021.1	2021.2
pymorphy2	0.9.1	0.9.1
pymorphy2-dicts-ru	2.4.417127.4579844	2.4.417127.4579844
pyparsing	2.4.7	2.4.7
pypiwin32	223	223
pytesseract	0.3.7	0.3.7
pytz	2021.1	2021.1
pywin32	301	301
pywin32-ctypes	0.2.0	0.2.0
requests	2.25.1	2.25.1
rsa	4.7.2	4.7.2
selenium	3.141.0	3.141.0
setuptools	57.0.0	57.0.0
six	1.16.0	1.16.0
soupsieve	2.2.1	2.2.1
urllib3	1.26.5	1.26.6
winapps	0.2.0	0.2.0