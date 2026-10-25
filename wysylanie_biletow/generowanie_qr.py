import base64
from io import BytesIO

import qrcode


def gen_qr(id_biletu: str) -> str:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)
    qr.add_data(id_biletu)
    qr.make(fit=True)

    image = qr.make_image()
    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")
    return base64.b64encode(image_buffer.getvalue()).decode("ascii")