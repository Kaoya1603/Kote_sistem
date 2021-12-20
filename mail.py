import smtplib  # Импортируем библиотеку по работе с SMTP
from email import encoders
# Добавляем необходимые подклассы - MIME-типы
from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
from email.mime.base import MIMEBase
from email.mime.text import MIMEText  # Текст/HTML
import os


def message(to_whom, role, data):
    addr_from = "cote.issup@gmail.com"  # Адресант
    addr_to = to_whom  # Получатель
    password = "sT6-2Jm-VGH-Aut"  # Пароль

    filepath = "res.docx"
    basename = os.path.basename(filepath)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(filepath, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % basename)

    msg = MIMEMultipart()  # Создаем сообщение
    msg['From'] = addr_from  # Адресат
    msg['To'] = addr_to  # Получатель
    if role == 1:
        msg['Subject'] = 'Отчёт для администратора'
        body = f"Добрый день, {data[0]}!\nСегодня, {data[1]},\nвы запросили отчет о работе системы на сегодняшнее число.\nВо вложении письмо в формате .docx."
    elif role == 2:
        msg['Subject'] = 'Спасибо, за то, что выбрали нас'
        body = f"Добрый день, {data[0]}!\n\nСегодня, {data[1]} в {data[2]},\nвы взяли в аренду товар {data[3]},\n артикул - {data[4]}.\n\nТариф - {data[5]} за минуту. Ваша скидка Пользователя - {data[6]}%.\n\nПриятного использования!\nС уважением, компания КОТЭ."
    else:
        msg['Subject'] = f"Чек за покупку"
        body = f'Добрый день, {data[0]}!\n\nСегодня, {data[1]} в {data[2]},\nвы закончили аренду товара {data[4]}, артикул - {data[4]}.\n\nТариф - {data[5]} за минуту. Ваша скидка Пользователя - {data[6]}%.\n\nВо вложении чек в формате .pdf.\n\nСпасибо, что выбрали нас!\nС уважением, компания КОТЭ.'
    msg.attach(MIMEText(body, 'plain'))  # Добавляем в сообщение текст

    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Создаем объект SMTP
        server.starttls()  # Начинаем шифрованный обмен по TLS
        server.login(addr_from, password)  # Получаем доступ
        server.send_message(msg)  # Отправляем сообщение
        server.quit()
    except:
        pass
