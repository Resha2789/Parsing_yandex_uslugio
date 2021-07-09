import PyInstaller.__main__
import shutil

def install(sistem=64, name='Сборщик_телефонов_64bit'):
    folder = 'Сборщик_данных_avito_64bit'
    if sistem == 32:
        folder = 'Сборщик_данных_avito_32bit'

    src_data = f"D:\Programming\Python\Parsing_avito\Все для сборщика данных"
    dst_data = f"D:\Фриланс\Авито\Валерий\{folder}\Все для сборщика данных"
    try:
        shutil.rmtree(dst_data)
    except FileNotFoundError:
        print('Файл не найден!')

    shutil.copytree(src_data, dst_data, ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))

    PyInstaller.__main__.run([
        "Main.py",
        "--noconsole",
        "--onefile",
        "--hidden-import=winapps",
        f"--icon=D:\Programming\Python\Parsing_avito\\""Все для сборщика данных\icon_phone.ico",
        f"--distpath=D:\Фриланс\Авито\Валерий\\{folder}\\",
        f"-n={name}"
    ])

if __name__ == '__main__':
    install(sistem=32, name='Сборщик_телефонов_avito')
