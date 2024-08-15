from PIL import Image
from reportlab.lib.pagesizes import landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from io import BytesIO


def convert_to_pdf(front_image_io, back_image_io):
    pdf_io = BytesIO()

    front_img = Image.open(front_image_io)
    back_img = Image.open(back_image_io)

    front_width, front_height = front_img.size
    back_width, back_height = back_img.size

    c = canvas.Canvas(pdf_io, pagesize=(front_width, front_height))

    c.drawImage(ImageReader(front_img), 0, 0, width=front_width, height=front_height)
    c.showPage()

    c.setPageSize((back_width, back_height))
    c.drawImage(ImageReader(back_img), 0, 0, width=back_width, height=back_height)
    c.save()

    pdf_io.seek(0)
    return pdf_io
