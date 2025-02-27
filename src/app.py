from bson import ObjectId
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_pymongo import PyMongo
import os
import mysql.connector


load_dotenv()


app = Flask(__name__)

username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')
cluster = os.getenv('MONGO_CLUSTER')

#app.config['MONGO_URI'] = 'mongodb+srv://' + username + ':' + password + '@cluster0.kewqy.mongodb.net/listacliente?retryWrites=true&w=majority&appName=Cluster0'
app.config['MONGO_URI'] = 'mongodb+srv://visanmar:Uy9AEiw9zHpIK0Uh@cluster0.kewqy.mongodb.net/listacliente?retryWrites=true&w=majority&appName=Cluster0'
mongo = PyMongo(app)


mysql_conn = {
    'host': os.getenv('MYSQL_HOST'),
    'port': os.getenv('MYSQL_PORT'),
    'user': os.getenv('MYSQL_USER'),
    'passwd': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'charset': os.getenv('MYSQL_CHARSET'),
    'collation': os.getenv('MYSQL_COLLATION')
}

### >>> mysql.connector.errors.ProgrammingError: Collation 'utf8mb4_0900_ai_ci' unknown
### 'charset': utf8mb4,
### 'collation': utf8mb4_unicode_ci

mydb = mysql.connector.connect(**mysql_conn)




# MONGODB
@app.route('/mongo', methods=['GET', 'POST'])
def mongo_api():
    if request.method == 'GET':
        libros = mongo.db.libros.find()
        count = mongo.db.libros.count_documents({})
        print( count )
        return jsonify( {'count':count, 'data':libros} ), 200
    elif request.method == 'POST':
        req = request.get_json()
        data = {
            'titulo': req['titulo'],
            'autor': req['autor'],
            'ISBN': req['ISBN'],
            'publicado': req['publicado']
        }
        r = mongo.db.libros.insert_one( data )
        return jsonify( {'inserted_id':r.inserted_id} ), 200
    else:
        return 'Method not allowed'
    

@app.route('/mongo/<string:id>', methods=['GET', 'PUT', 'DELETE'])
def mongo_api_id(id):
    if request.method == 'GET':
        libro = mongo.db.libros.find({"_id":ObjectId(id)})
        return jsonify( libro ), 200
    elif request.method == 'PUT':
        req = request.get_json()
        data = {
            'titulo': req['titulo'],
            'autor': req['autor'],
            'ISBN': req['ISBN'],
            'publicado': req['publicado']
        }
        r = mongo.db.libros.update_one({"_id":ObjectId(id)}, {"$set": data})
        return jsonify({"modified":r.modified_count}), 200
    elif request.method == 'DELETE':
        r = mongo.db.libros.delete_one({"_id":ObjectId(id)})
        return jsonify({"deleted":r.deleted_count}), 200
    else:
        return 'Method not allowed', 200



## MYSQL
@app.route('/mysql', methods=['GET', 'POST'])
def mysql():
    cursor = mydb.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM cars;')
        data = cursor.fetchall()
        data = [ {
            "marca": d[0],
            "modelo": d[1],
            "year": d[2],
            "color": d[3]
        } for d in data]
        count = cursor.rowcount
        cursor.close()
        return jsonify({'count':count, 'data': data}), 200
    elif request.method == 'POST':
        req = request.get_json()
        data = (req['marca'], req['modelo'], req['year'], req['color'])
        cursor.execute('INSERT INTO cars (marca, modelo, year, color) VALUES (%s, %s, %s, %s);', data)
        mydb.commit()
        count = cursor.rowcount
        cursor.close()
        return jsonify({'inserted': cursor.rowcount}), 200
    else:
        return 'Method not allowed', 200
        
    


@app.route('/mysql/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def mysql_api(id):
    cursor = mydb.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM cars WHERE id=%s;', (id,))
        data = cursor.fetchall()
        data = [ {
            "marca": d[0],
            "modelo": d[1],
            "year": d[2],
            "color": d[3]
        } for d in data]
        count = cursor.rowcount
        cursor.close()
        return jsonify({'count':count, 'data': data}), 200
    elif request.method == 'PUT':
        req = request.get_json()
        data = (req['marca'], req['modelo'], req['year'], req['color'], id)
        cursor.execute('UPDATE cars set marca=%s, modelo=%s, year=%s, color=%s WHERE id=%s;', data)
        mydb.commit()
        count = cursor.rowcount
        cursor.close()
        return jsonify({'modified': count}), 200
    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM cars WHERE id=%s', (id,))
        mydb.commit()
        count = cursor.rowcount
        cursor.close()
        return jsonify({'deleted': count}), 200
    else:
        return 'Method not allowed', 200





'''
app = Flask(__name__)

mysql = MySQL(app)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

cursor = mysql.connection.cursor()
cursor.execute(' CREATE TABLE table_name(field1, field2...) ')

mysql.connection.commit()

cursor.close()
'''





if __name__ == '__main__':
    app.run(debug=True)