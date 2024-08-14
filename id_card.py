import os
import sys
import barcode
import io
from PIL import Image, ImageDraw, ImageFont
from barcode.writer import ImageWriter
import segno


def resource_path(relative_path):
    """ Get absolute path to resource, works for development and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


def create_id_card(student_details):
    """
    Creates an ID card with the student's details, barcode, and QR code.

    Parameters:
        student_details (dict): Dictionary containing student's information.

    Returns:
        tuple: BytesIO objects for the front and back images of the ID card.
    """
    # Load the front and back template images
    id_card_front = Image.open(resource_path("Idcard_front.png"))
    front_draw = ImageDraw.Draw(id_card_front)
    id_card_back = Image.open(resource_path("Idcard_back.png"))
    back_draw = ImageDraw.Draw(id_card_back)

    # Student's image
    student_img = Image.open(resource_path("student.jpg"))

    # Load the font
    font_path = resource_path("arial.ttf")
    font = ImageFont.truetype(font_path, 40)
    font2 = ImageFont.truetype(font_path, 30)

    # Extract student details
    name = student_details["name"]
    reg_no = student_details["reg_no"]
    branch = student_details["branch"]
    dob = student_details["dob"]
    parent_mob_no = student_details["parent_mob_no"]
    mob_no = student_details["mob_no"]
    address = student_details["address"]

    # Calculate the width of the name text and position to center it
    name_width = font.getlength(name)
    card_width = 817
    x_position_student_name = (card_width - name_width) // 2
    x_position_other_details = 294

    # Draw text on the front of the ID card
    front_draw.text((x_position_student_name, 730), name, font=font, fill="red")
    front_draw.text((x_position_other_details, 805), reg_no, font=font2, fill="black")
    front_draw.text((x_position_other_details, 860), branch, font=font2, fill="black")
    front_draw.text((x_position_other_details, 995), dob, font=font2, fill="black")
    front_draw.text((x_position_other_details, 1058), mob_no, font=font2, fill="black")

    # Generate and add barcode and QR code to the back of the ID card
    barcode_img = generate_barcode(reg_no)
    qrcode_img = generate_qr_code(f"{name.upper()}.Mobile.-{mob_no}.Parent Mob.-{parent_mob_no}.Address : {address}")
    qrcode_img = qrcode_img.resize((300, 300))

    # Position the barcode and QR code on the back of the ID card
    id_card_back.paste(barcode_img, ((card_width - barcode_img.width) // 2, 610))
    id_card_back.paste(qrcode_img, ((card_width - qrcode_img.width) // 2, 750))

    # Resize and position student profile image on id card front
    student_img = student_img.resize((293, 362))
    id_card_front.paste(student_img, ((card_width - student_img.width) // 2, 353))

    # Format the address text and draw it on the back of the ID card
    address_lines = address.split(",")
    formatted_address = f"Address: {', '.join(address_lines[:len(address_lines) // 2])}\n{', '.join(address_lines[len(address_lines) // 2:])}"
    back_draw.text((60, 80), formatted_address, font=font2, fill="black")

    # Save the ID card images in memory
    front_image_io = io.BytesIO()
    id_card_front.save(front_image_io, format="PNG")
    back_image_io = io.BytesIO()
    id_card_back.save(back_image_io, format="PNG")

    front_image_io.seek(0)
    back_image_io.seek(0)

    return front_image_io, back_image_io


def generate_barcode(data):
    """
    Generates a barcode for the given data.

    Parameters:
        data (str): The data to encode in the barcode.

    Returns:
        Image: PIL Image object of the barcode.
    """
    options = {
        'module_width': 0.3,
        'module_height': 7.0,
        'quiet_zone': 1.0,
        'font_size': 0,
        'text_distance': 0.0,
        'background': 'white',
        'foreground': 'black',
        'write_text': False
    }

    barcode_io = io.BytesIO()
    code128 = barcode.get_barcode_class('code128')
    barcode_instance = code128(data, writer=ImageWriter())
    barcode_instance.write(barcode_io, options=options)
    barcode_io.seek(0)

    return Image.open(barcode_io)


def generate_qr_code(data):
    """
    Generates a QR code for the given data.

    Parameters:
        data (str): The data to encode in the QR code.

    Returns:
        Image: PIL Image object of the QR code.
    """
    qr_io = io.BytesIO()
    qrcode = segno.make_qr(data)
    qrcode.save(qr_io, kind='png')
    qr_io.seek(0)

    return Image.open(qr_io)