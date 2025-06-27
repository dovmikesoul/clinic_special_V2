from flaskext.mysql import MySQL

mysql = MySQL()

def init_db(app):
    app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'DEVELOPMENT24'
    app.config['MYSQL_DATABASE_DB'] = 'clinic_special_v2'
    mysql.init_app(app)
