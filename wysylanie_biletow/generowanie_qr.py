import qrcode
import hashlib
import secrets


def gen_qr(id_biletu):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,                
                       border=4)
    qr.add_data(id_biletu)
    qr.make(fit=True)


    img = qr.make_image() # fill_color, back_color dla kustomizacji
    filepath = f"C:/Users/stane_kgevii5/Documents/GitHub/Projekt_Bileciki/wysylanie_biletow/QR-{secrets.token_urlsafe(16)}.png"
    img.save(filepath)

    return filepath


gen_qr('just_testing')