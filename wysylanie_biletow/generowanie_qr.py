import base64
from io import BytesIO

import qrcode
import hashlib
import secrets
import base64
import io


def gen_obraz_qr(id_biletu):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)
    qr.add_data(id_biletu)
    qr.make(fit=True)


    img = qr.make_image() # fill_color, back_color dla kustomizacji
    filepath = f"C:/Users/stane_kgevii5/Documents/GitHub/Projekt_Bileciki/wysylanie_biletow/QR-{secrets.token_urlsafe(16)}.png"
    img.save(filepath)

    return filepath


def gen_base64(id_biletu):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,                
                        border=4)
    qr.add_data(id_biletu)
    qr.make(fit=True)


    img = qr.make_image() # fill_color, back_color dla kustomizacji
    buffer = io.BytesIO()
    img.save(buffer,format='PNG')


    return base64.b64encode(buffer.getvalue()).decode(encoding='ascii')


id = secrets.token_urlsafe(16)
print(id)
print(gen_base64(id))
print(len(gen_base64(id)))