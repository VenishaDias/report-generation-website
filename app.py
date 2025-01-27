from flask import Flask, render_template, request, redirect, session # type: ignore
from flask_mysqldb import MySQL # type: ignore
from datetime import datetime

app = Flask(__name__)
app.secret_key = '6b4f0c8078d7b69f2bfe52d3a2ea7d13c25e5e1238b372e4cd2f8df75de9a1a4'  # Required for session security

# Database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Db.RUN97'
app.config['MYSQL_DB'] = 'asr_metallurgy'

mysql = MySQL(app)

# Fetch max ulr_no from the reports table
def get_max_ulr():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT MAX(ulr_no) FROM reports")
    result = cursor.fetchone()[0]
    cursor.close()
    return result if result is not None else 0

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/sample-entry', methods=['GET', 'POST'])
def sample_entry():
    today_date = datetime.today().strftime('%Y-%m-%d')
    #return render_template('sample_entry.html', today=today_date)
    if request.method == 'POST':
        session['form_data'] = request.form.to_dict()  # Store all form data in session
        total_reports = int(request.form.get('total_reports', 0))
        print(session['form_data'])
        print(f"Redirecting to /report_entry/{total_reports}")  # Debugging
        return redirect(f'/report_entry/{total_reports}')
    return render_template('sample_entry.html', today=today_date)


@app.route('/report_entry/<int:total_reports>', methods=['GET', 'POST'])
def report_entry(total_reports):
    if 'form_data' not in session:
        return redirect('/')
    form_data = session['form_data']
    
    print(f"Rendering report entry page with {total_reports} reports.")  # Debugging

    max_ulr = int(get_max_ulr()) + 1  # Get max ULR number and increment by 1
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        
        for i in range(1, total_reports + 1):
            ulr_no = request.form.get('ulr_' + str(i), '')
            report_no = request.form.get('report_no_' + str(i), '')
            type_of_test = request.form.get('type_of_test_' + str(i), '')
            test_method = request.form.get('test_method_' + str(i), '')
            equipment_used = request.form.get('equipment_used_' + str(i), '')
            doc_type = request.form.get('doc_type' + str(i), '')


            cursor.execute("""
                INSERT INTO reports 
                (issued_to, address, asr_job_id, cust_date, report_date, 
                asr_job_date, testing_date, customer_ref_no, sample_description, 
                total_reports, tested_by, ulr_no, report_no, type_of_test, 
                test_method, equipment_used,doc_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            """, (form_data['issued_to'], form_data['address'], form_data['asr_job_id'], 
                  form_data['cust_date'], form_data['report_date'], form_data['asr_job_date'], 
                  form_data['testing_date'], form_data['customer_ref_no'], 
                  form_data['sample_description'], total_reports, form_data['tested_by'], 
                  ulr_no, report_no, type_of_test, test_method, equipment_used, doc_type))
        
        mysql.connection.commit()
        cursor.close()
        session.pop('form_data')
        return "Data submitted successfully!"

    return render_template('report_entry.html', total_reports=total_reports, max_ulr=max_ulr)


if __name__ == '__main__':
    app.run(debug=True)
