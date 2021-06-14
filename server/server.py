import os

import cherrypy
import json
import mysql.connector
import logging


DATABASE = "crudDB"


try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootadmin",
        database=DATABASE
    )

    mycursor = mydb.cursor()
except Exception as NODB:
    print(NODB, 'try to create it')
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootadmin"
    )
    mycursor = mydb.cursor()

    creation_query = 'CREATE DATABASE {};'.format(DATABASE)
    mycursor.execute(creation_query)

    mydb.commit()

try:
    mycursor.execute('USE {} ;'.format(DATABASE))

    mycursor.execute('CREATE TABLE office('
                     'id INT AUTO_INCREMENT PRIMARY KEY,'
                     'name CHAR(40) NOT NULL,'
                     'city CHAR(40),'
                     'n_department INT)')

    mycursor.execute('CREATE TABLE employee('
                     'id INT AUTO_INCREMENT PRIMARY KEY,'
                     'first_name CHAR(40) NOT NULL,'
                     'last_name CHAR(40) NOT NULL,'
                     'position CHAR(40),'
                     'cod_office INT NOT NULL,'
                     'FOREIGN KEY (cod_office) references office(id),'
                     'extn INT,'
                     'start_date DATETIME NOT NULL,'
                     'salary FLOAT)')

    mycursor.execute('CREATE VIEW first_view AS (SELECT employee.*, office.name FROM employee, office WHERE employee.cod_office = office.id)')

    mydb.commit()

    val = [
        ("ufficio_uno", "Roma", "1"),
        ("ufficio_due", "Lecce", "2"),
        ("ufficio_tre", "Verona", "3")
    ]
    sql = "INSERT INTO office (name, city, n_department) VALUES (%s, %s, %s)"

    for entry in val:
        mycursor.execute(sql, entry)
    mydb.commit()
except Exception as insertFIELDS:
    print('Creating tables: ', insertFIELDS)


class Server(object):
    @cherrypy.expose()
    def get_data(self):
        print("getting data...")

        # select_from_first_view = "SELECT * FROM first_view"
        # select_from_first_view = "SELECT employee.*, office.name FROM employee, office WHERE employee.cod_office = office.id"

        # mycursor.execute(select_from_first_view)
        # myresult = mycursor.fetchall()

        mycursor.callproc('findAll')
        myresults = mycursor.stored_results()

        data = []
        # print out the result
        for myresult in myresults:
            for x in myresult:
                # print(x)
                item = {
                    "DT_RowId": "row_" + str(x[0]),
                    "first_name": x[1],
                    "last_name": x[2],
                    "position": x[3],
                    "office": x[8],
                    "extn": x[5],
                    "start_date": str(x[6]).split(' ')[0],
                    "salary": x[7],
                }
                data.append(item)

        return json.dumps({'data': data})

    @cherrypy.expose()
    def get_office_data(self):
        print("getting office data...")
        mycursor.execute("SELECT * from office")
        myresult = mycursor.fetchall()
        data = []
        for x in myresult:
            print(x)
            item = {
                "id": x[0],
                "name": x[1],
                "city": x[2],
                "n_department": x[3],
            }
            data.append(item)
        return json.dumps({'data': data})

    @cherrypy.expose()
    def insert_data(self):
        print('create...')
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = json.loads(rawbody)
        print(body)

        val = []
        sql = "INSERT INTO employee (first_name, last_name, position, cod_office, extn, start_date, salary) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        for k, v in body.items():
            if v == '':
                val.append(None)
            else:
                val.append(v)
        print('body: ', tuple(val))

        try:
            mycursor.execute(sql, tuple(val))
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
            return json.dumps({'response': 'ok'})
        except Exception as e:
            logging.debug("record not inserted. Exception: ", e.__dict__['sqlstate'])
            raise cherrypy.HTTPError(status=self.get_error_code(e.__dict__['sqlstate']), message=e.__dict__['sqlstate'])

    @cherrypy.expose()
    def update_data(self):
        print('updating...')
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = json.loads(rawbody)
        print('body: ', body)

        val = []
        sql = "UPDATE employee SET first_name=%s, last_name=%s, position=%s, cod_office=%s, extn=%s, start_date=%s, salary=%s WHERE id=%s"
        for k, v in body.items():
            if v == '':
                val.append(None)
            else:
                val.append(v)

        try:
            mycursor.execute(sql, tuple(val))
            mydb.commit()
            print(str(mycursor.rowcount) + " record(s) updated.")
            return json.dumps({'response': 'ok'})
        except Exception as e:
            logging.debug("record not updated. Exception: ", e.__dict__['sqlstate'])
            raise cherrypy.HTTPError(status=self.get_error_code(e.__dict__['sqlstate']), message=e.__dict__['sqlstate'])

    @staticmethod
    def get_error_code(argument):
        switcher = {
            '01000': 512,
            '22007': 513,
            '45000': 514
        }
        return switcher.get(argument)

    @cherrypy.expose()
    def delete_data(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = json.loads(rawbody)
        print('delete...', body)
        id = int(body['DT_RowId'].split('_')[1])

        sql = "DELETE FROM employee WHERE id = %s"
        mycursor.execute(sql, (id,))

        try:
            mydb.commit()
            print(mycursor.rowcount, "record deleted.")
            return json.dumps({'response': 0})
        except:
            print("record not deleted.")
            return json.dumps({'response': 1})

    @cherrypy.expose
    def index(self):
        cursor = mydb.cursor()

        cursor.execute(" drop trigger if exists salaryUpdate")
        qrystr = "CREATE TRIGGER salaryUpdate BEFORE UPDATE ON employee FOR EACH ROW BEGIN IF NEW.salary<0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Salary less then 0'; END IF; END"
        cursor.execute(qrystr)
        mydb.commit()

        cursor.execute(" drop trigger if exists salaryCreate")
        qrystrtwo = "CREATE TRIGGER salaryCreate BEFORE INSERT ON employee FOR EACH ROW BEGIN IF NEW.salary<0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Salary less then 0'; END IF; END"
        cursor.execute(qrystrtwo)
        mydb.commit()

        cursor.execute(" drop procedure if exists findAll")
        qrystr = "CREATE PROCEDURE findAll () BEGIN SELECT * FROM first_view; END"
        cursor.execute(qrystr)
        mydb.commit()

        return open("static/index.html")


current_dir = os.path.dirname(os.path.abspath(__file__))

cherrypy.config.update({'server.socket_host': '127.0.0.1',
                        'server.socket_port': 8080})

conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(current_dir, 'static')}}
cherrypy.quickstart(Server(), '/', config=conf)
