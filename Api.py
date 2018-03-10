from flask import Flask,request,jsonify
import sqlite3
import random,string
import plivo

app=Flask(__name__)

auth_id= "private"
auth_token = "private"
p = plivo.RestAPI(auth_id, auth_token)

def isValidPhone(phone):
 if len(phone)== 10 and phone.isdigit():
	return True
 return False   

def isValidPassword(password):
 if len(password) > 7:
	return True
 return False

def img_path():
	chars = string.ascii_uppercase+string.ascii_lowercase
	imgPath=''
	for i in range(10):
		imgPath += random.choice(chars)
	return imgPath

def session_key():
	chars = string.ascii_uppercase+string.ascii_lowercase+string.digits
	sessionkey=''
	for i in range(12):
		sessionkey += random.choice(chars)
	return sessionkey

def fp_key():
	chars = string.ascii_uppercase+string.ascii_lowercase+string.digits
	fpkey=''
	for i in range(6):
		fpkey += random.choice(chars)
	return fpkey 

def access_key():
	chars = string.ascii_uppercase+string.ascii_lowercase+string.digits
	sessionkey=''
	for i in range(15):
		sessionkey += random.choice(chars)
	return sessionkey

def access_token():
	chars = string.ascii_uppercase+string.ascii_lowercase+string.digits
	sessionkey=''
	for i in range(28):
		sessionkey += random.choice(chars)
	return sessionkey	

@app.route("/")
def welcome():
	return jsonify(Infinity = "Health")

@app.route("/about/")
def about():
	return jsonify('CREDITS : Arun,Riaz Ahmed')

@app.route('/signup/', methods= ['GET', 'POST'])
def signup():
	try:
	 password=request.args.get('password')
	 cp=request.args.get('cp')
	 phone=request.args.get('phone')
	 if password != cp:
		return jsonify(msg="passwords does not match") 
	 chk=isValidPhone(phone) and isValidPassword(password)
	 print chk
	 if chk==False:
		return jsonify(msg='invalid phoneNumber or password')
	 msg="failed"
	 with sqlite3.connect("api.db") as con:
			cur = con.cursor()
			print 1
			cur.execute("SELECT * from User where PhoneNumber=?",(phone,))
			chk = cur.fetchone()
			if chk :
				return jsonify(msg="Account is already registered with this PhoneNumber")				
			else:
				print 3
				ak,at=access_key(),access_token()
				print ak,at
				cur.execute("INSERT INTO User(Password,PhoneNumber,accessKey,accessToken) VALUES (?,?,?,?)",(password,phone,ak,at))
				con.commit()
				msg = "Record successfully added " + phone  
				return jsonify(msg=msg)
	except:
	 #con.rollback()
	 msg = "error in insert operation"
	 return jsonify(msg=msg)

@app.route('/getKeys/', methods= ['GET', 'POST'])
def login():	
	password=request.args.get('password')
	phone=request.args.get('phone')
	msg="failed"	
	try:
         with sqlite3.connect("api.db") as con:
			cur = con.cursor()
			cur.execute("SELECT Password FROM User where PhoneNumber=?",(phone,))
			p = cur.fetchone()
			if p is None:
				return jsonify(msg='Invalid password or phoneNumber')
			if p[0] == password:
				msg = "login successful" 
				cur.execute("SELECT accessKey,accessToken FROM User where PhoneNumber=?",(phone,))
				ak,at=cur.fetchone()
				con.commit()
				return jsonify(accessKey=ak,accessToken=at)
			return jsonify(msg='Invalid password or phoneNumber')
	except:
		return jsonify(msg='db error')

@app.route("/forgotPassword/")
def forgotPassword():
	try:
	 phone=request.args.get('phone')
	 chk=isValidPhone(phone)
	 print chk
	 if chk==False:
		return jsonify(msg='invalid phoneNumber')
	 reset=fp_key()
	 msg="failed"
	 with sqlite3.connect("api.db") as con:
			cur = con.cursor()
			cur.execute("SELECT Password from User where PhoneNumber=?",(phone,))
			chk = cur.fetchone()
			print chk
			if chk :
				print chk[0]
				print type(phone)
				params = {
				'dst': '+91'+phone, # Sender's phone number with country code
				'src' : '8608810617', # Receiver's phone Number with country code
				'text' : "Your password is "+chk[0]} # Your SMS Text Message - English
				#'url' : "http://52.2.98.181/plivo" # The URL to which with the status of the message is sent
				#'method' : 'POST'
				print 1342
				response = p.send_message(params)
				print str(response)
				print 234
				if response[0]==202:
					msg = "Your password is sent to your mobile : " + phone
				else :
					msg="reset failed"
				#print str(response)				
				return jsonify(msg=msg)
			else:
				return jsonify(msg="Account is not registered with this number")
	except:
	 msg = "error in db"
	 return jsonify(msg=msg)

@app.route("/resetPassword/")    
def resetPassword():
	try:
	 password=request.args.get('password')
	 phone=request.args.get('phone')
	 reset=request.args.get('reset')
	 msg="failed"
	 with sqlite3.connect("api.db") as con:
			cur = con.cursor()
			cur.execute("SELECT Password from User where PhoneNumber=?",(phone,))
			chk = cur.fetchone()
			if chk :
				cur.execute("UPDATE User SET Password = ? WHERE PhoneNumber = ?",(reset,phone))
				con.commit()
				params = {
				'dst': '+91'+phone, # Sender's phone number with country code
				'src' : '8608810617', # Receiver's phone Number with country code
				'text' : "Your new password is "+reset} # Your SMS Text Message - English
				#'url' : "http://52.2.98.181/plivo" # The URL to which with the status of the message is sent
				#'method' : 'POST'
				print 5
				response = p.send_message(params)
				if response[0]==202:
					msg = "Your new password is sent to your mobile : " + phone
				else:
					msg="reset failed"
				print str(response)
				return jsonify(msg=msg)
			else:
				return jsonify(msg="Invalid credentials")
	except:
	 msg = "error in db"
	 return jsonify(msg=msg)

@app.route('/monitor/',methods=['GET','POST'])
def monitor():
	accesskey=request.args.get('accesskey')
	accesstoken=request.args.get('accesstoken')
	log=request.args.get('log')
	type=request.args.get('type')
	try:
		msg="failed"
		print 1,accesskey,accesstoken,log
		with sqlite3.connect("api.db") as con:
			cur = con.cursor()
			print 2
			cur.execute("SELECT accessToken from User where accessKey = ?",(accesskey,))
			print 1
			chkAT = cur.fetchone()
			if chkAT is None:
				return jsonify(msg="Invalid accessKey or accessToken")
			if chkAT[0] == accesstoken:
				cur.execute("SELECT fileType from Files where accessKey = ?",(accesskey,))
				fileListTuple=cur.fetchall()
				fileList=[]
				for i in fileListTuple:
					fileList.append(i[0])
				print fileList,fileListTuple
				if type in fileList:
					cur.execute("SELECT fileName from Files where accessKey = ?",(accesskey,))
				print log
				if myfile is None:
					myfile=img_path()
					cur.execute("SELECT fileName from Files where accessKey = ?",(accesskey,))
				filelog=open(myfile,'a')
				filelog.write(log+'\n');
				filelog.close()
				msg = "done"
				return jsonify(msg="logged",log=log)
	except:
		return jsonify(msg="error connecting")

if __name__ == '__main__':
	app.run(debug=True,port=8080)
	app.debug = True
