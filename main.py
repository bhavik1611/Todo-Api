import pymysql
from app import app
from db_config import mysql
from flask import jsonify, request, session
from cryptography.fernet import Fernet
from datetime import datetime

cipher_suite = Fernet(b'NnYKRnFCRUXvlAPrK7zVlZmO2-q9RX69DXNvZqro98M=')

app.config['SECRET_KEY'] = "thisissecret"

@app.route('/app/agent', methods=['POST'])
def register():
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		a_id = request.form['agent_id']
		pwd = request.form['password'].encode('utf-8')
		if a_id and pwd and request.method == 'POST':
			check = 'SELECT agent_id from accounts where agent_id = %s'
			cursor.execute(check, a_id)
			agents = cursor.fetchall()
			if len(agents)!=0:
				res = jsonify({'status':'Failure!', 'reason': 'Account exists!', 'status_code': 400})
				return res
			else:
				encrypted_password = cipher_suite.encrypt(pwd)
				sql = "INSERT INTO accounts(agent_id, password) VALUES(%s, %s)"
				data = (a_id, encrypted_password)
				cursor.execute(sql, data)
				conn.commit()
				res = jsonify({'status':'Account created!', 'status_code': 200})
				return res
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/app/agent/auth', methods=["POST"])
def login():
	conn = mysql.connect()
	cursor = conn.cursor(pymysql.cursors.DictCursor)
	if request.method == 'POST':
		print(request.json)
		a_id = request.form['agent_id']
		pwd = request.form['password']
		cursor.execute("SELECT * FROM accounts WHERE agent_id='" + a_id + "'")
		user = cursor.fetchone()
		print(user)
		if len(user) > 0:
			password_stored = (user['password']).encode('utf-8')
			if cipher_suite.decrypt(password_stored).decode('utf-8') == pwd:
				session['agent_id'] = a_id
				res = jsonify({"status": "Success", 'agent_id': user['agent_id'], 'status_code':200})
				return res
			else:
				res = jsonify({'status': 'failure', 'status_code': 401})
				return res
	else:
		res = jsonify({'status': 'failure', 'status_code': 401})
		return res

@app.route('/app/sites/list', methods=["GET"])
def all_items():
	a_id = request.args['agent']
	if a_id != session['agent_id']:
		res = jsonify({'status': 'failure', 'reason': 'Incorrect login. Please Login again', 'status_code': 401})
		return res
	conn = mysql.connect()
	cursor = conn.cursor(pymysql.cursors.DictCursor)
	cursor.execute("SELECT * from items where agent_id = '" + a_id + "' ORDER BY due_date")
	items = cursor.fetchall()
	if len(items)>0:
		print(items)
		res = jsonify(items)
		return res 
	res = jsonify({'status': 'failure', 'status_code': 401})
	return res

@app.route('/app/sites', methods=["POST"])
def add_item():
	a_id = request.args['agent']
	if a_id != session['agent_id']:
		res = jsonify({'status': 'failure', 'reason': 'Incorrect login. Please Login again', 'status_code': 401})
		return res
	title = request.form['title']
	desc = request.form['description']
	cat = request.form['category']
	due = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
	    
	conn = mysql.connect()
	cursor = conn.cursor(pymysql.cursors.DictCursor)
	if a_id and title and desc and cat and due and request.method == 'POST':
		sql = "INSERT into items(agent_id, title, description, category, due_date) values (%s, %s, %s, %s, %s)"
		data = (a_id, title, desc, cat, due)
		cursor.execute(sql, data)
		conn.commit()
		res = jsonify({'status': 'success', 'status_code': 200})
		return res 

	else:
		res = jsonify({'status': 'failure', 'reason': 'Invalid/Incomplete Data','status_code': 401})
		return res

@app.route('/app/agent/logout')
def logout():
	if session:
		session.clear()
		return jsonify({'status' : 'You successfully logged out', 'status_code': 200})
	return jsonify({'status' : 'Failure. Please login', 'status_code': 400})
	


if __name__ == "__main__":
	app.run(debug=True)