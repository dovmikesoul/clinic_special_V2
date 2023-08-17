from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
from flask_wtf import CSRFProtect
from datetime import datetime
import os, re


app = Flask(__name__)
app.secret_key = "See_Im_a_suicidal_kid_with_no_future_Im_quicker_to_bust_your_face_with_a_baseball_bat_before_I_shoot_ya"
csrf = CSRFProtect(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_USER'] = 'Miguel'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Develop22'
app.config['MYSQL_DATABASE_DB'] = 'clinic_special_v2'
mysql.init_app(app)


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

        sql = 'SELECT * FROM `users` WHERE name = % s;'
        data = (_name, )
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        user = cursor.fetchone()
        if user:
            flash('!Nombre de usuario ya esta en uso!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', _email):
            flash('Correo electronico invalido...')
        elif not re.match(r'[A-Za-z0-9]+', _name):
            flash('El nombre de usuario debe contener solo letras y numeros...')
        elif not _name or not _email or not _pic or not _pass :
            flash('¡Porfavor rellene todo el formulario!')
        else:
            now = datetime.now()
            tiemp = now.strftime("%Y%H%M%S")
            newNamePic = tiemp+_pic.filename
            _pic.save("uploads/"+newNamePic)
            
            _pass = __create_password(_pass)

            sql = "INSERT INTO `users` (`id`, `name`, `email`, `pic`, `pass`) VALUES (NULL, %s, %s, %s, %s);"
            data = (_name, _email, newNamePic, _pass)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('¡Ha creado su cuenta con exito!')

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
        verificad = check_password_hash(user[4], _pass)
        if verificad== True:
            session['loggedin'] = True
            session['name'] = user[1]
            flash('¡Ha iniciado sesión correctamente!')
            return redirect('/dashboard')
        else:
            flash('¡Usuario o contraseña incorrectos!')
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
        _name = request.form['txtName']
        _email = request.form['txtEmail']
        _pic = request.files['txtPic']
        _pass = request.form['txtPass']
        id = request.form['txtID']
        sql = "UPDATE `users` SET `name`=%s,`email`=%s, `pass`=%s WHERE id=%s;"
        data = (_name, _email, _pass, id)
        conn = mysql.connect()
        cursor = conn.cursor()

        now = datetime.now()
        tiemp = now.strftime("%Y%H%M%S")

        if _pic.filename != '':
            newNamePic = tiemp+_pic.filename
            _pic.save("uploads/"+newNamePic)
            cursor.execute("SELECT pic FROM users WHERE id=%s", id)
            fila = cursor.fetchall()
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
            cursor.execute("UPDATE users SET pic=%s WHERE id=%s",
                        (newNamePic, id))
            conn.commit()
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
            return redirect(url_for('create'))

        now = datetime.now()
        tiemp = now.strftime("%Y%H%M%S")

        if _pic.filename != '':
            newNamePic = tiemp+_pic.filename
            _pic.save("uploads/"+newNamePic)

        sql = "INSERT INTO `users` (`id`, `name`, `email`, `pic`, `pass`) VALUES (NULL, %s, %s, %s, %s);"
        data = (_name, _email, newNamePic, _pass)
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
            newNamePic = tiemp+_pic.filename
            _pic.save("uploads/"+newNamePic)
            cursor.execute("SELECT pic FROM pacients WHERE id=%s", id)
            fila = cursor.fetchall()
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
            cursor.execute("UPDATE pacients SET pic=%s WHERE id=%s",
                        (newNamePic, id))
            conn.commit()
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
            newNamePic = tiemp+_pic.filename
            _pic.save("uploads/"+newNamePic)

        sql = "INSERT INTO `pacients` (`id`, `name`, `email`, `pic`) VALUES (NULL, %s, %s, %s);"
        data = (_name, _email, newNamePic)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        flash('¡Paciente agregado!')
        return redirect('/pacients')
    else:
        return redirect(url_for('login'))
# FIN CRUD PACIENTES


if __name__ == '__main__':
    app.run(debug=True)
