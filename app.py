from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect
from datetime import datetime
import os, re

from db import mysql, init_db  

app = Flask(__name__)
app.secret_key = "See_Im_a_suicidal_kid_with_no_future_Im_quicker_to_bust_your_face_with_a_baseball_bat_before_I_shoot_ya"

csrf = CSRFProtect(app)


init_db(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA


@app.route('/uploads/<namePic>')
def uploads(namePic):
    return send_from_directory(app.config['CARPETA'], namePic)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/home')
def home_():
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'txtName' in request.form and 'txtPass' in request.form:
        _name = request.form['txtName']
        _email = request.form['txtEmail']
        _pic = request.files['txtPic']
        _pass = request.form['txtPass']
        _confpass = request.form['txtConfPass']

        if _confpass == _pass:
            sql = 'SELECT * FROM `users` WHERE name = % s;'
            data = (_name, )
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            user = cursor.fetchone()
            if user:
                flash('!Nombre de usuario ya esta en uso!')
            elif not _name or not _email or not _pass :
                flash('¡Porfavor rellene todo el formulario!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', _email):
                flash('Correo electronico invalido...')
            elif not re.match(r'[A-Za-z0-9]+', _name):
                flash('El nombre de usuario debe contener solo letras y numeros...')
            else:
                now = datetime.now()
                tiemp = now.strftime("%Y%H%M%S")
                if _pic.filename != '':
                    newNamePic = tiemp + _pic.filename
                    _pic.save("uploads/" + newNamePic)
                    _pass = __create_password(_pass)
                    sql = "INSERT INTO `users` (`id`, `name`, `email`, `pic`, `pass`) VALUES (NULL, %s, %s, %s, %s);"
                    data = (_name, _email, newNamePic, _pass)
                else:
                    _pass = __create_password(_pass)
                    sql = "INSERT INTO `users` (`id`, `name`, `email`, `pass`) VALUES (NULL, %s, %s, %s);"
                    data = (_name, _email, _pass)
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
                flash('¡Ha creado su cuenta con exito!')
        else:
            flash('¡No se confirmo la contraseña!')
    return render_template('register.html')


def __create_password(_pass):
    return generate_password_hash(_pass)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'txtName' in request.form and 'txtPass' in request.form:
        _name = request.form['txtName']
        _pass = request.form['txtPass']

        sql = 'SELECT * FROM `users` WHERE name = % s;'
        data = (_name )
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        user = cursor.fetchone()
        if user:
            verificad = check_password_hash(user[4], _pass)
            if verificad== True:
                session['loggedin'] = True
                session['name'] = user[1]
                flash('¡Ha iniciado sesión correctamente!')
                return redirect('/dashboard')
            else:
                flash('¡Contraseña incorrecta!')
        else:
            flash('¡Usuario inexistente!')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('name', None)
    flash('A cerrado sesion')
    return redirect(url_for('login'))


# INICIO CRUD USUARIOS
@app.route('/users')
def index_users():
    if 'loggedin' in session:
        sql = "SELECT * FROM `users`;"
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        users = cursor.fetchall()
        print(users)
        conn.commit()
        return render_template('users/index.html', users=users)
    else:
        return redirect(url_for('login'))
    

@app.route('/users/destroy/<int:id>')
def destroy_user(id):
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT pic FROM users WHERE id=%s", id)
        fila = cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

        cursor.execute("DELETE FROM `users` WHERE id=%s", (id))
        conn.commit()
        return redirect('/users')
    else:
        return redirect(url_for('login'))
   


@app.route('/users/edit/<int:id>')
def edit_user(id):
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `users` WHERE id=%s", (id))
        users = cursor.fetchall()
        conn.commit()
        return render_template('users/edit.html', users=users)
    else:
        return redirect(url_for('login'))
 

@app.route('/users/update', methods=['POST'])
def update_user():
    if 'loggedin' in session:
        id = request.form['txtID']
        _name = request.form['txtName']
        _email = request.form['txtEmail']
        _pic = request.files['txtPic']
        _pass = request.form['txtPass']
        _passnew = request.form['txtPassNew']
        
        if not _passnew:
            sql = "UPDATE `users` SET `name`=%s,`email`=%s, `pass`=%s WHERE id=%s;"
            data = (_name, _email, _pass, id)
            conn = mysql.connect()
            cursor = conn.cursor()
        elif _passnew !='':
            _passnew = __create_password(_passnew)
            sql = "UPDATE `users` SET `pass`=%s WHERE id=%s;"
            data = (_passnew, id)
            conn = mysql.connect()
            cursor = conn.cursor()
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', _email):
            flash('Correo electronico invalido...')
        elif not re.match(r'[A-Za-z0-9]+', _name):
            flash('El nombre de usuario debe contener solo letras y numeros...')
        now = datetime.now()
        tiemp = now.strftime("%Y%H%M%S")
        if _pic.filename != '':
            newNamePic = tiemp + _pic.filename
            _pic.save("uploads/" + newNamePic)
            cursor.execute("SELECT pic FROM users WHERE id=%s", id)
            fila = cursor.fetchall()
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
            cursor.execute("UPDATE users SET pic=%s WHERE id=%s", (newNamePic, id))
            conn.commit()
            sql = "UPDATE `users` SET `name`=%s,`email`=%s, `pass`=%s WHERE id=%s;"
            data = (_name, _email, _pass, id)
        else:
            sql = "UPDATE `users` SET `name`=%s,`email`=%s, `pass`=%s WHERE id=%s;"
            data = (_name, _email, _pass, id)
        cursor.execute(sql, data)
        conn.commit()
        return redirect('/users')
    else:
        return redirect(url_for('login'))


@app.route('/users/create')
def create_user():
    if 'loggedin' in session:
        return render_template('users/create.html')
    else:
        return redirect(url_for('login'))
    


@app.route('/users/store', methods=['POST'])
def storage_user():
    if 'loggedin' in session:
        _name = request.form['txtName']
        _email = request.form['txtEmail']
        _pic = request.files['txtPic']
        _pass = request.form['txtPass']

        if _name == '' or _email == '' or _pic == '' or _pass == '':
            flash('¡Porfavor rellene el formulario!')
            return redirect(url_for('create_user'))

        now = datetime.now()
        tiemp = now.strftime("%Y%H%M%S")

        if _pic.filename != '':
            newNamePic = tiemp+_pic.filename
            _pic.save("uploads/"+newNamePic)
            sql = "INSERT INTO `users` (`id`, `name`, `email`, `pic`, `pass`) VALUES (NULL, %s, %s, %s, %s);"
            data = (_name, _email, newNamePic, _pass)
        else:
            sql = "INSERT INTO `users` (`id`, `name`, `email`, `pass`) VALUES (NULL, %s, %s, %s);"
            data = (_name, _email, _pass)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        flash('Usuario agregado')
        return redirect('/users')
    else:
        return redirect(url_for('login'))
# FIN CRUD USUARIOS


# INICIO CRUD PACIENTES
@app.route('/pacients')
def index_pacients():
    if 'loggedin' in session:
        sql = "SELECT * FROM `pacients`;"
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        pacients = cursor.fetchall()
        print(pacients)
        conn.commit()
        return render_template('pacients/index.html', pacients=pacients)
    else:
        return redirect(url_for('login'))


@app.route('/pacients/destroy/<int:id>')
def destroy_pacient(id):
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT pic FROM pacients WHERE id=%s", id)

        fila = cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

        cursor.execute("DELETE FROM `pacients` WHERE id=%s", (id))
        conn.commit()
        return redirect('/pacients')
    else:
        return redirect(url_for('login'))
    


@app.route('/pacients/edit/<int:id>')
def edit_pacient(id):
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `pacients` WHERE id=%s", (id))
        pacients = cursor.fetchall()
        conn.commit()
        return render_template('pacients/edit.html', pacients=pacients) 
    else:
        return redirect(url_for('login'))
    


@app.route('/pacients/update', methods=['POST'])
def update_pacient():
    if 'loggedin' in session:
        _name = request.form['txtName']
        _email = request.form['txtEmail']
        _pic = request.files['txtPic']
        id = request.form['txtID']
        sql = "UPDATE `pacients` SET `name`=%s,`email`=%s WHERE id=%s;"
        data = (_name, _email, id)
        conn = mysql.connect()
        cursor = conn.cursor()

        now = datetime.now()
        tiemp = now.strftime("%Y%H%M%S")

        if _pic.filename != '':
            newNamePic = tiemp + _pic.filename
            _pic.save("uploads/" + newNamePic)
            cursor.execute("SELECT pic FROM pacients WHERE id=%s", id)
            fila = cursor.fetchall()
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
            cursor.execute("UPDATE pacients SET pic=%s WHERE id=%s", (newNamePic, id))
            conn.commit()
            sql = "UPDATE `pacients` SET `name`=%s,`email`=%s WHERE id=%s;"
            data = (_name, _email, id)
        else:
            sql = "UPDATE `pacients` SET `name`=%s,`email`=%s WHERE id=%s;"
            data = (_name, _email, id)
        cursor.execute(sql, data)
        conn.commit()
        return redirect('/pacients')
    else:
        return redirect(url_for('login'))
   


@app.route('/pacients/create')
def create_pacient():
    if 'loggedin' in session:
        return render_template('pacients/create.html')
    else:
        return redirect(url_for('login'))
    
  
@app.route('/pacients/store', methods=['POST'])
def storage_pacient():
    if 'loggedin' in session:
        _name = request.form['txtName']
        _email = request.form['txtEmail']
        _pic = request.files['txtPic']

        if _name == '' or _email == '' or _pic == '':
            flash('¡Recuerda llenar todos los campos!')
            return redirect(url_for('create'))

        now = datetime.now()
        tiemp = now.strftime("%Y%H%M%S")

        if _pic.filename != '':
            newNamePic = tiemp + _pic.filename
            _pic.save("uploads/" + newNamePic)
            sql = "INSERT INTO `pacients` (`id`, `name`, `email`, `pic`) VALUES (NULL, %s, %s, %s);"
            data = (_name, _email, newNamePic)
        else:
            sql = "INSERT INTO `pacients` (`id`, `name`, `email`) VALUES (NULL, %s, %s);"
            data = (_name, _email)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        flash('¡Paciente agregado!')
        return redirect('/pacients')
    else:
        return redirect(url_for('login'))
# FIN CRUD PACIENTES

# LISTAR CITAS
@app.route('/appointments')
def index_appointments():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT a.id, p.name as pacient, d.name as doctor, a.date, a.reason, a.status
                 FROM appointments a
                 JOIN pacients p ON a.pacient_id = p.id
                 JOIN doctors d ON a.doctor_id = d.id;"""
        cursor.execute(sql)
        appointments = cursor.fetchall()
        return render_template('appointments/index.html', appointments=appointments)
    else:
        return redirect(url_for('login'))


# CREAR CITA
@app.route('/appointments/create', methods=['GET', 'POST'])
def create_appointment():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()

    # Obtener pacientes y doctores para desplegarlos en formulario
    cursor.execute("SELECT id, name FROM pacients")
    pacients = cursor.fetchall()
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()

    if request.method == 'POST':
        pacient_id = request.form['pacient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        reason = request.form['reason']

        sql = "INSERT INTO appointments (pacient_id, doctor_id, date, reason) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql, (pacient_id, doctor_id, date, reason))
        conn.commit()
        flash("Cita creada correctamente")
        return redirect(url_for('index_appointments'))

    return render_template('appointments/create.html', pacients=pacients, doctors=doctors)

# LISTAR DOCTORES
@app.route('/doctors')
def index_doctors():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors;")
        doctors = cursor.fetchall()
        return render_template('doctors/index.html', doctors=doctors)
    else:
        return redirect(url_for('login'))


# CREAR DOCTOR
@app.route('/doctors/create')
def create_doctor():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('doctors/create.html')


# GUARDAR DOCTOR
@app.route('/doctors/store', methods=['POST'])
def store_doctor():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    name = request.form['txtName']
    email = request.form['txtEmail']
    phone = request.form['txtPhone']
    specialty = request.form['txtSpecialty']
    pic = request.files['txtPic']
    now = datetime.now()
    tiemp = now.strftime("%Y%H%M%S")

    if pic.filename != '':
        newFileName = tiemp + pic.filename
        pic.save(os.path.join('uploads', newFileName))
        sql = "INSERT INTO doctors (name, email, phone, specialty, pic) VALUES (%s, %s, %s, %s, %s)"
        data = (name, email, phone, specialty, newFileName)
    else:
        sql = "INSERT INTO doctors (name, email, phone, specialty) VALUES (%s, %s, %s, %s)"
        data = (name, email, phone, specialty)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()

    flash("Doctor agregado correctamente")
    return redirect(url_for('index_doctors'))


# EDITAR DOCTOR
@app.route('/doctors/edit/<int:id>')
def edit_doctor(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE id=%s", (id,))
    doctor = cursor.fetchall()
    return render_template('doctors/edit.html', doctors=doctor)


# ACTUALIZAR DOCTOR
@app.route('/doctors/update', methods=['POST'])
def update_doctor():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    id = request.form['txtID']
    name = request.form['txtName']
    email = request.form['txtEmail']
    phone = request.form['txtPhone']
    specialty = request.form['txtSpecialty']
    pic = request.files['txtPic']

    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiemp = now.strftime("%Y%H%M%S")

    if pic.filename != '':
        newFileName = tiemp + pic.filename
        pic.save(os.path.join('uploads', newFileName))
        sql = "UPDATE doctors SET name=%s, email=%s, phone=%s, specialty=%s, pic=%s WHERE id=%s"
        data = (name, email, phone, specialty, newFileName, id)
    else:
        sql = "UPDATE doctors SET name=%s, email=%s, phone=%s, specialty=%s WHERE id=%s"
        data = (name, email, phone, specialty, id)

    cursor.execute(sql, data)
    conn.commit()

    flash("Doctor actualizado correctamente")
    return redirect(url_for('index_doctors'))


# ELIMINAR DOCTOR
@app.route('/doctors/destroy/<int:id>')
def destroy_doctor(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE id=%s", (id,))
    conn.commit()

    flash("Doctor eliminado correctamente")
    return redirect(url_for('index_doctors'))


if __name__ == '__main__':
    app.run(debug=True)
