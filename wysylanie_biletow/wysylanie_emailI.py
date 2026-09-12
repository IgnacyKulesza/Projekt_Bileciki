from generowanie_qr import gen_qr

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from email.mime.image import MIMEImage

def send_email(email_odbiorcy,id_biletu,imie,koncert):

    adres_email = "mailKoncert@mail.com"
    tekst = f"""{imie}, oto twój bilet do koncertu {koncert}."""

    mail = MIMEMultipart()
    mail['From'] = adres_email
    mail['To'] = email_odbiorcy
    mail['Subject'] = f"Bilet na {koncert}"

    

    mail.attach(MIMEText(tekst, 'plain'))

    kod_qr = gen_qr(id_biletu)

    with open(kod_qr, "rb") as f:
        img_data = f.read()
        image = MIMEImage(img_data, name=kod_qr)

    mail.attach(image)

    with smtplib.SMTP('smtp.gmail.com', 587) as server: # claude powiedzał że gmail używa portu 587 więc się posłucham
        server.starttls()
        server.login(adres_email, "hało_do_maila_czy_coś")
        server.send_message(mail)