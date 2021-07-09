from PIL import Image
import pytesseract
import os
import re
import winapps
import traceback
import sys
# import requests
from urllib import request


class TesseractImg:
    def __init__(self):
        self.path_tesseract = None
        self.path_phone_img = None
        self.width = None
        self.height = None

    def tesseract_img_init(self):
        self.path_tesseract = None
        self.path_phone_img = os.path.abspath("Все для сборщика данных/Телефон.png")
        self.width = 1500
        self.height = 300
        self.find_tesseract()
        print(self.path_tesseract)

    def image_to_string(self, phone_number):

        try:
            if self.path_tesseract is None:
                return False

            for i in range(0, 10):

                response = request.urlopen(phone_number)
                with open(self.path_phone_img, 'wb') as f:
                    f.write(response.file.read())

                # img = Image.open(os.path.abspath("Все для сборщика данных/Телефон.png"))
                img = Image.open(self.path_phone_img)

                self.width = self.width - 50
                self.height = self.height - 10

                if self.width < 1000:
                    self.width = 1500
                    self.height = 300

                resized = img.resize((self.width, self.height))
                resized.save(self.path_phone_img)

                img = Image.open(self.path_phone_img)
                # r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
                pytesseract.pytesseract.tesseract_cmd = self.path_tesseract
                custom_config = r'--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789'
                phone = pytesseract.image_to_string(img, config=custom_config)
                phone = re.sub(r'\s+|[-]+', '', phone)
                phone = re.sub(r'[ОоOo]+', '0', phone)
                phone = int(re.sub(r'[^0-9]+', '', phone))

                # Если phone < 11 то пробуем распознать снова
                if len(str(phone)) != 11:
                    continue

                print(f"Номер телефона: {phone} колл. цифр: {len(str(phone))}")

                return phone

            return 0

        except Exception as error:
            print(f"image_to_string {error}")
            traceback.print_exc(file=sys.stdout)
            return 0

    def find_tesseract(self):
        try:
            for app in winapps.search_installed('Tesseract-OCR'):
                test = app.uninstall_string
                self.path_tesseract = re.sub(r'uninstall.exe', 'tesseract.exe', r"" + str(app.uninstall_string))
        except Exception as error:
            pass

        if self.path_tesseract is None:
            print(f"$<b style='color: rgb(255, 0, 0);'>Tesseract не найден! Установите Tesseract!</b>")
            return False

        return True


def test():
    # ts = TesseractImg()
    # data = ts.image_to_string()

    img_data = "data:image/png;base64,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"

    response = request.urlopen(img_data)
    with open('D:\Programming\Python\Parsing_avito\Все для сборщика данных\Телефон.png', 'wb') as f:
        f.write(response.file.read())


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    test()  # то запускаем функцию main()
