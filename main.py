from django.template.defaultfilters import title
from flask import Flask, render_template, request, send_file
from io import BytesIO
from id_card import create_id_card
from pdf_converter import convert_to_pdf
from firebase_config import initialize_firebase, fetch_student_details
import check_inputs

app = Flask(__name__)

# Initialize Firebase
initialize_firebase()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        reg_no = request.form.get('reg_no').upper()
        if not check_inputs.check_reg(reg_no):
            return render_template('index.html', error="Invalid registration number format.")

        details = fetch_student_details(reg_no)
        if not details:
            return render_template('index.html', error="No student details found in the database")

        try:
            # Generate ID Card
            front_img_io, back_img_io = create_id_card(details)

            # Convert to PDF
            pdf_io = convert_to_pdf(front_img_io, back_img_io, details['name'])
            pdf_io.seek(0)

            return send_file(pdf_io, as_attachment=True, download_name=f"{details['name']}IDCard.pdf")

        finally:
            # Close the BytesIO streams to free memory
            front_img_io.close()
            back_img_io.close()

    return render_template('index.html')

# # Incomplete function:
# @app.route('/add_student', methods=['GET', 'POST'])
# def add_student():
#     if request.method == 'POST':
#         return render_template('add_student.html', title=title('Submit Student Details'))


if __name__ == "__main__":
    app.run(debug=True)
