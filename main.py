from flask import Flask, render_template, request, send_file, redirect, url_for
from id_card import create_id_card
from pdf_converter import convert_to_pdf
from firebase_config import initialize_firebase, fetch_student_details, db
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
            pdf_io = convert_to_pdf(front_img_io, back_img_io)
            pdf_io.seek(0)

            return send_file(pdf_io, as_attachment=True, download_name=f"{details['name']}IDCard.pdf")

        finally:
            # Close the BytesIO streams to free memory
            front_img_io.close()
            back_img_io.close()

    return render_template('index.html')


@app.route('/add-student', methods=['GET', 'POST'])
def add_student_page():
    if request.method == 'POST':
        return render_template("add_student.html")
    return render_template("add_student.html")


@app.route('/go-to-new-page', methods=['POST'])
def go_to_new_page():
    return redirect(url_for('add_student_page'))


@app.route('/to-home-screen', methods=['POST'])
def go_to_home():
    return redirect('/')


@app.route('/add-new-student', methods=['POST'])
def add_new_student():
    # Extract form data
    student_details = {
        "name": request.form.get("name"),
        "reg_no": request.form.get("reg_no").upper(),
        "branch": request.form.get("branch"),
        "dob": request.form.get("dob"),
        "mob_no": request.form.get("mob_no"),
        "parent_mob_no": request.form.get("parent_mob_no"),
        "address": request.form.get("address")
    }

    # Validate the registration number
    if not check_inputs.check_reg(student_details["reg_no"]):
        return render_template('add_student.html', error="Invalid registration number format.",
                               **student_details)

    # Add student to Firebase
    ref = db.reference(f'/students/{student_details["reg_no"]}')
    ref.set(student_details)

    # Redirect back to home or show a success message
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
