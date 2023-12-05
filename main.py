from flask import Flask, render_template, request, redirect, send_file, url_for, flash, session, abort
from flask_mysqldb import MySQL
import mysql.connector
import base64
from PIL import Image




app = Flask(__name__)

app.secret_key = 'bebasapasaja'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aurisarabina20'
app.config['MYSQL_DB'] = 'hotelpython'
mysql = MySQL(app)

#proses inisialisasi website + session
@app.route('/')
def home():
    if 'id' in session:
        user_id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(f"select username from users where id = {user_id}")
        username = cur.fetchone()[0]
        cur.close()

        return render_template('index.html', username=username, user_id=user_id)
    else:
        return render_template('index.html')
        
@app.route('/booking')
def booking():
    if 'id' in session:
        user_id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(f"select username from users where id = {user_id}")
        username = cur.fetchone()[0]
        cur.close()

        return render_template('booking.html', username=username, user_id=user_id)
    else:
        return render_template('index.html')

@app.route('/payment')
def payment():
    if 'id' in session:
        user_id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(f"select username from users where id = {user_id}")
        username = cur.fetchone()[0]
        cur.close()

        return render_template('payment.html', username=username, user_id=user_id)
    else:
        return render_template('index.html')

@app.route('/history')
def history():
        if 'id' in session:
            user_id = session['id']
            cur = mysql.connection.cursor()

            cur.execute(f"select username from users where id = {user_id}")
            username = cur.fetchone()[0]

            cur.execute(f"SELECT * FROM customer where user_id = {user_id}")
            historytampil = cur.fetchall()

            cur.close()

            return render_template('history.html', username=username, user_id=user_id, historytampil=historytampil)
        else:
            return render_template('index.html')     

#proses inisialisasi website + session untuk admin
@app.route('/admin')
def customertampildata():
        if 'usernameadmin' in session:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM customer ORDER BY id DESC")
            datatampil = cur.fetchall()
            cur.close()
            data_list = [list(row) for row in datatampil]
            for i, row in enumerate(data_list):
                if row[11]:  
                    encoded_image_data = base64.b64encode(row[11]).decode('utf-8')
                    row[11] = f"data:image/jpeg;base64,{encoded_image_data}"
                    datatampil = [tuple(row) for row in data_list]

            return render_template('admin.html', usernameadmin=session['usernameadmin'], datapemesan=datatampil)
        else:
                    return render_template('adminlogin.html')
                

#proses inisialisasi website + session untuk admin#userdata     
@app.route('/admin#user-data')
def datauser():
        if 'usernameadmin' in session:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users ORDER BY id DESC")
            datausertampil = cur.fetchall()
            cur.close()
            return render_template ('data-user.html', userdata=datausertampil)
        else:
                        return render_template('adminlogin.html')


#proses inisialisasi website + session untuk admin#kamar    
@app.route('/admin#kamar')
def kamar():
        if 'usernameadmin' in session:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users ORDER BY id DESC")
            kamartampil = cur.fetchall()
            cur.close()
            return render_template ('data-kamar.html', kamar=kamartampil)
        else:
                        return render_template('adminlogin.html')


#proses register user
@app.route('/userregister', methods=['POST'])
def userregister():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirmpassword = request.form["confirmpassword"]
        cur = mysql.connection.cursor()
        if password == confirmpassword:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s)", (username, email, phone, password))  # Memperbaiki query untuk memasukkan level yang didapat dari form
            mysql.connection.commit()
            flash("Data Berhasil di kirim")
            return redirect(url_for('home'))
        else:
            return "Passwords do not match"


#proses login user
@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    username = request.form['username']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute(f"select id, password from users where username = '{username}'")
    user = cur.fetchone()
    cur.close()

    if user and password == user[1]:
        session['id'] = user[0]
        return redirect(url_for('home'))
    else:
        return 'Email atau password salah'


#proses login admin
@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    usernameadmin = request.form['usernameadmin']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute(f"select usernameadmin, password from admin where usernameadmin= '{usernameadmin}'")
    user = cur.fetchone()
    cur.close()

    if user and password == user[1]:
        session['usernameadmin'] = user[0]
        return redirect(url_for('customertampildata'))
    else:
        return 'Email atau password salah'


#proses insert from booking
@app.route('/submit-booking', methods=['POST'])
def submit_form1():
    # Extract form data
    user_id = request.form['user_id']
    nama = request.form['nama']
    email = request.form['email']
    phone = request.form['phone']
    tipe = request.form['tipe']
    checkin = request.form['checkin']
    checkout = request.form['checkout']
    roomQuantity = request.form['roomQuantity']
    ket = request.form['ket']
    bookingPrice = request.form['bookingPrice']

    # Store data for template
    booking_data = {'user_id': user_id, 'nama': nama, 'email': email, 'phone': phone, 'tipe': tipe, 'checkin': checkin, 'checkout': checkout, 'roomQuantity': roomQuantity, 'ket': ket, 'bookingPrice': bookingPrice,}

    # Render template with data
    return render_template('payment.html', booking_data=booking_data)


#proses insert into customer
@app.route('/submit-payment', methods=['POST'])
def customerinsert():
    if request.method == 'POST':
        if 'image' in request.files:
            image_file = request.files['image']
            imagedata = image_file.read()
            user_id = request.form['user_id']
            nama = request.form['nama']
            email = request.form['email']
            phone = request.form['phone']
            tipe = request.form['tipe']
            checkin = request.form['checkin']
            checkout = request.form['checkout']
            jml = request.form['roomQuantity']
            ket = request.form['ket']
            bookingPrice = request.form['bookingPrice']


            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO customer (user_id, nama, email, phone, tipe, checkin, checkout, jml, ket, imagedata, bookingPrice) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, nama, email, phone, tipe, checkin, checkout, jml, ket, imagedata, bookingPrice))
            mysql.connection.commit()

            flash("Data Berhasil di kirim")
            return redirect(url_for('home'))
        else:
            flash('Invalid image file.')
            return render_template('payment')


#proses update into customer
@app.route('/customerupdate', methods=['POST'])
def customerupdate():
    if request.method == 'POST':
        id = request.form['id']
        nama = request.form['nama']
        email = request.form['email']
        phone = request.form['phone']
        tipe = request.form['tipe']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        jml = request.form['jml']
        status = request.form['status']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE customer SET nama=%s, email=%s, phone=%s, tipe=%s, checkin=%s, checkout=%s, jml=%s, status=%s WHERE id=%s", (nama, email, phone, tipe, checkin, checkout, jml, status, id))
        mysql.connection.commit()
        flash("Data Berhasil di Update")
        return redirect(url_for('customertampildata'))

#proses refund dari user
@app.route('/refund', methods=['POST'])
def refund():
    if request.method == 'POST':
        id = request.form['id']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE customer SET status='refund' WHERE id=%s", (id))
        mysql.connection.commit()
        flash("Data Berhasil di Update")
        return redirect(url_for('history'))

     
#delete data customer
@app.route('/customerhapus/<int:id>', methods=["GET"])
def customerhapus(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customer WHERE id=%s", (id,))
    mysql.connection.commit()
    flash("data Berhasil di Hapus")
    return redirect( url_for('customertampildata'))


#proses update into user
@app.route('/userupdate', methods=['POST'])
def userupdate():
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username=%s, email=%s, phone=%s, password=%s, WHERE id=%s", (username, email, phone, password, id))
        mysql.connection.commit()
        flash("Data Berhasil di Update")
        return redirect(url_for('datauser'))


#delete data user
@app.route('/userhapus/<int:id>', methods=["GET"])
def userhapus(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    mysql.connection.commit()
    flash("data Berhasil di Hapus")
    return redirect( url_for('datauser'))


#session logout user
@app.route('/logoutuser')
def userlogout():
    session.pop('id', None)
    return redirect(url_for('home'))

#session logout admin
@app.route('/logoutadmin')
def adminlogout():
    session.pop('usernameadmin', None)
    session.pop('level', None)
    return redirect(url_for('customertampildata'))

if __name__ == '__main__':
    app.run(debug=True)
