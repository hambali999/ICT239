from flask import Flask, render_template, request, flash, redirect, url_for, session
import pymongo
import bcrypt
#from flask_wtf import Form 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, AnyOf
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import csv
import io
from datetime import datetime
from flask_mongoengine import MongoEngine, Document


#setting up the application
app = Flask(__name__)

#=======================================================
#connect to mongodb
# client = pymongo.MongoClient('localhost:27017')
#get the database name
# db = client.get_database('flaskLoginMongodb')
#get specific records from the collections
# records = db.register
#=======================================================
# setup secret key
app.secret_key = "secretlah"
#=======================================================

app.config['MONGODB_SETTINGS'] = {
    'db': 'your_database',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

#models
class User(db.Document):
    email = db.StringField()
    password = db.BinaryField()
    name = db.StringField()

class Booking(db.Document):
    check_in_date = db.StringField()
    customer = db.StringField()
    hotel_name = db.StringField()

#hotel_name,duration,unit_cost,image_url,description
class Staycation(db.Document):
    hotel_name = db.StringField()
    duration = db.StringField()
    unit_cost = db.StringField()
    image_url = db.StringField()
    description = db.StringField()



#format = userList.append([name, email, password])
userList = [] #for question 1, hardcoded the userlist to store information

#routes login page
@app.route('/', methods=['GET', 'POST'])
def index():
	
	if "email" in session: #tma how to validate user login session, this is how
		return redirect(url_for("products"))

	if request.method == 'POST':

		email = request.form.get('email')
		password = request.form.get('password')

		#validation
		if len(email) == 0:
			flash("Email cannot be empty", category='error')
			return render_template('index.html')
		elif len(password) == 0:
			flash("Password cannot be empty.", category='error')
			return render_template('index.html')
		elif len(email)<4:
			flash("Email must be more than 4 characters.", category='error')
			return render_template('index.html')
		elif len(password)<5:
			flash("Password must be more than 5 characters.", category='error')
			return render_template('index.html')

		# email_found = records.find_one({"email": email})
		email_found = User.objects(email=email).first()
		print(email_found)


		if email_found: #if email found
			email_val = email_found['email']
			passwordcheck = email_found['password']
			print("LOGIN TEST")
			#check to see if encrypted password integrity
			# print(password)
			# print(passwordcheck)
			# print("---")
			# b = password.encode('utf-8')
			# hashedPass = bcrypt.checkpw(b, bcrypt.gensalt())
			# print(b)
			# print(hashedPass)
			# print("END")
			if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
				session["email"] = email_val
				return redirect(url_for('products'))
			else: #wrong password integrity
				if "email" in session:
					return redirect(url_for('products'))
				flash("Please key in the correct password again", category='error')
				return render_template('index.html')
		else: #email not found
			flash("Email not found", category='error')
			return render_template('index.html')
	return render_template('index.html')

	# form = LoginForm()
	# if form.validate_on_submit():
	# 	return 'Form Successfully Submitted!'
	# return render_template('index.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
	data = request.form #here we access the data
	print(data)
	if request.method == 'GET':
		return render_template('register.html')

	elif request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		name = request.form.get('name')

		#validation
		if len(email) == 0:
			flash("Email cannot be empty", category='error')
			return render_template('register.html')
		elif len(password) == 0:
			flash("Password cannot be empty.", category='error')
			return render_template('register.html')
		elif len(name) == 0:
			flash("Please enter a name", category='error')
			return render_template('register.html')
		elif len(email)<4:
			flash("Email must be more than 4 characters.", category='error')
			return render_template('register.html')
		elif len(password)<5:
			flash("Password must be more than 5 characters.", category='error')
			return render_template('register.html')

		#if name,email found in mongodb then show that user is found
		# name_found = records.find_one({"name": name})
		name_found = User.objects(name=name).first()
		# email_found = records.find_one({"email": email})
		email_found = User.objects(email=email).first()
		print("test")
		print(name, email)
		print(name_found, email_found)

		if email_found:
			flash("Email is already registered!", category='error')
			return render_template('register.html')
		if name_found:
			flash("User is already registered!", category='error')
			return render_template('register.html')
		else:
			hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #encode
			user_input = {'name': name, 'email': email, 'password': hashed} #arrange the records into key value pair
			#insert into db collection
			User(email=email, name=name, password=hashed).save()
			# records.insert_one(user_input)

			#find the newly created account via email
			# user_data = records.find_one({"email": email})
			# new_email = user_data['email']
			flash("User registered! Please login now", category='success') #after user is registered, now go to login page to ask the user to login
			return render_template('index.html', email=email)
			# return render_template('products.html', email=new_email)
	return render_template('register.html')

	
@app.route('/logout', methods=['GET', 'POST'])
def logout():
	# return render_template('signout.html')
	#if successfully logout
	#if email in session then we remove the email from the session to prevent any session then lead them back to the login page which is our index.html
	if "email" in session:
		session.pop("email", None)
		return render_template('index.html')
	else:
		return render_template('index.html')


@app.route('/products', methods=['GET', 'POST'])
def products():
	print("IN PRODUCTS URL")
	if "email" in session:
		email=session["email"]
		email_found = User.objects(email=email).first()
		# email_found = records.find_one({"email": email})
		# nameofuser = email_found.get("name")
		nameofuser = email_found['name']
		
		#open csv staycation data -- part of question 1 where we were told to use hardcode to get the csv not through mongodb
		# file = open('./static/staycation.csv')
		# csvreader = csv.reader(file)
		# csvHeader = []
		# csvHeader = next(csvreader)
		# rows = []
		# for row in csvreader:
		# 	rows.append(row)
			# print(row)
		# for x in rows:
			# print(x[0])

		#question 2 - get all the documents related to the staycation in that collection
		staycationList = []
		for item in Staycation.objects():
			hotel_name=item['hotel_name']
			duration=item['duration']
			unit_cost=item['unit_cost']
			image_url=item['image_url']
			description=item['description']
			staycationList.append([hotel_name, duration, unit_cost, image_url, description])
		# print(staycationList)
		
		# return render_template('products.html', email=email, name=nameofuser, datas=rows) -- part of question1 where need to get data directly from csv
		return render_template('products.html', email=email, name=nameofuser, datas=staycationList) # -- part of question2 where need to get data from mongodb
		# return render_template('products.html', email=email, name=nameofuser)

	else:
		return redirect(url_for("login"))
	# if request.method == 'GET':
	# 	return render_template('products.html')
	# return render_template('products.html')

@app.route('/view', methods=['GET', 'POST'])
def view():
	#session data, and finding the name of the user
	email=session["email"]
	# email_found = records.find_one({"email": email})
	email_found = User.objects(email=email).first()
	nameofuser = email_found['name']
	#hotel data
	image = request.form.get('image')
	title = request.form.get('title')
	text = request.form.get('text')

	if request.method == 'GET':
		return render_template('view.html', email=email, name=nameofuser, image=image, text=text, title=title)
	elif request.method == 'POST':
		print("IN POST /VIEW")
		print(request.form)

		date = request.form.get('date')
		today = datetime.today()
		datetoday = (str(today)[:10])
		if date == None:
			date = datetoday
		else:
			year = date[6:]
			month = date[3:5]
			day = date[:2]
			dateCleanse = year + "-" + month + "-" + day #since the format of date is in YYYY-MM-DD
			date = dateCleanse

		#for booking, need these data => check_in_date,customer,hotel_name
		print(f"check_in_date = {date}\ncustomer = {email}\nhotel_name = {title}")

		if request.form.get('submit') == "submit":
			#submit button pressed to submit the booking
			print("YES PLEASE SUBMIT")
			Booking(check_in_date=date, customer=email, hotel_name=title).save()
			flash("Booking has been successfully submitted! Thank you!", category='success')
		else:
			print("NOPE DONT SUBMIT")
		



		if date == None:
			flash("Please enter or pick a date before submitting!", category='error')
			return render_template('view.html', email=email, name=nameofuser, image=image, text=text, title=title)
		return render_template('view.html', email=email, name=nameofuser, image=image, text=text, title=title)

	return render_template('products.html', email=email, name=nameofuser)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	#session data, and finding the name of the user
	email=session["email"]
	email_found = User.objects(email=email).first()
	nameofuser = email_found['name']

	if request.method == 'GET':
		return render_template('upload.html', email=email, name=nameofuser)

	elif request.method == 'POST':
		#get request form and file information to check which csv and read data
		type = request.form.get('type')
		uploadtype = request.form.get('uploads')
		file = request.files.get('file')                    
		data = file.read().decode('utf-8')
		dict_reader = csv.DictReader(io.StringIO(data), delimiter=',', quotechar='"')
		file.close()		

		if uploadtype == "users":
			for data in list(dict_reader):
				userEmail=data['email']
				userPassword=data['password']
				userName=data['name']
				# print(userEmail, userPassword, userName)
				hashedPassword = bcrypt.hashpw(userPassword.encode('utf-8'), bcrypt.gensalt()) #encode
				#insert into db collection
				User(email=userEmail, name=userName, password=hashedPassword).save()
			flash("File successfully uploaded!", category='success')
			return render_template('upload.html', email=email, name=nameofuser)
		elif uploadtype == "staycation":
			for data in list(dict_reader):
				hotel_name=data['hotel_name']
				duration=data['duration']
				unit_cost=data['unit_cost']
				image_url=data['image_url']
				description=data['description']
				Staycation(hotel_name=hotel_name, duration=duration, unit_cost=unit_cost, image_url=image_url, description=description).save()
			flash("File successfully uploaded!", category='success')
			return render_template('upload.html', email=email, name=nameofuser)
		elif uploadtype == "booking":
			for data in list(dict_reader):
				check_in_date=data['check_in_date']
				customer=data['customer']
				hotel_name=data['hotel_name']
				Booking(check_in_date=check_in_date, customer=customer, hotel_name=hotel_name).save()	
			flash("File successfully uploaded!", category='success')
			return render_template('upload.html', email=email, name=nameofuser)

		return render_template('upload.html', email=email, name=nameofuser)
	return render_template('upload.html', email=email, name=nameofuser)

@app.route('/trend_chart', methods=['GET', 'POST'])
def trend_chart():
	#session data, and finding the name of the user
	email=session["email"]
	email_found = User.objects(email=email).first()
	nameofuser = email_found['name']

	#question 2 - get all the documents related to the bookings in that collection
	bookingList = []
	capellaSingaporeBookings = []
	shangriLaSingaporeBookings = []
	wSingaporeSentosaCoveBookings = []
	yorkHotelSingaporeBookings = []
	studioMBookings = []
	discoveryPackageBookings = []
				
	#theres actually data inconsistency in this booking.csv, for shangri-la singapore, the check_in_date = '2022-01-7' 
	# => this data => 2022-01-7,steve@mno.com,"Shangri-La Singapore"
	#where as the format for all the check_in_date data is yyyy-mm-dd, this one row in the csv is yyyy-mm-d.
	#hence i will have to cleanse it shown below to match is with the rest of the data before sorting it.
	for item in Booking.objects():
		check_in_date=item['check_in_date']
		hotel_name=item['hotel_name']
		if check_in_date == '2022-01-7': #here for the inconsistency
			check_in_date = '2022-01-07' #cleansing it and formating it to the corect format 
		bookingList.append([check_in_date, hotel_name])
	# print(bookingList)
	bookingList.sort(key = lambda x: x[0]) #sort the dates of the list of bookings
	for data in bookingList:
		if data[1] == 'Capella Singapore':
			capellaSingaporeBookings.append((data[0], 330, data[1]))
		elif data[1] == 'Shangri-La Singapore':
			shangriLaSingaporeBookings.append((data[0], 450, data[1]))
		elif data[1] == 'W Singapore - Sentosa Cove':
			wSingaporeSentosaCoveBookings.append((data[0], 300, data[1]))
		elif data[1] == 'York Hotel Singapore':
			yorkHotelSingaporeBookings.append((data[0], 180, data[1]))
		elif data[1] == 'Studio M': 
			studioMBookings.append((data[0], 230, data[1]))
		elif data[1] == 'Discovery Package':
			discoveryPackageBookings.append((data[0], 120, data[1]))

	#cleansing the data, if bookings appear on same date, total the price of bookings that appear on the same date
	capellaSingaporeBookingsDict = {}
	for check_in_date,unit_cost,hotel_name in capellaSingaporeBookings:
		total = capellaSingaporeBookingsDict.get(check_in_date, 0) + unit_cost
		capellaSingaporeBookingsDict[check_in_date] = total
	# print("capellaSingaporeBookingsDict")
	# print(capellaSingaporeBookingsDict.items())
	# print("---")

	shangriLaSingaporeBookingsDict = {}
	for check_in_date,unit_cost,hotel_name in shangriLaSingaporeBookings:
		total = shangriLaSingaporeBookingsDict.get(check_in_date, 0) + unit_cost
		shangriLaSingaporeBookingsDict[check_in_date] = total
	# print("shangriLaSingaporeBookingsDict")
	# print(shangriLaSingaporeBookingsDict.items())
	# print("---")

	wSingaporeSentosaCoveBookingsDict = {}
	for check_in_date,unit_cost,hotel_name in wSingaporeSentosaCoveBookings:
		total = wSingaporeSentosaCoveBookingsDict.get(check_in_date, 0) + unit_cost
		wSingaporeSentosaCoveBookingsDict[check_in_date] = total
	# print("wSingaporeSentosaCoveBookingsDict")
	# print(wSingaporeSentosaCoveBookingsDict.items())
	# print("---")

	yorkHotelSingaporeBookingsDict = {}
	for check_in_date,unit_cost,hotel_name in yorkHotelSingaporeBookings:
		total = yorkHotelSingaporeBookingsDict.get(check_in_date, 0) + unit_cost
		yorkHotelSingaporeBookingsDict[check_in_date] = total
	# print("yorkHotelSingaporeBookingsDict")
	# print(yorkHotelSingaporeBookingsDict.items())
	# print("---")

	studioMBookingsDict = {}
	for check_in_date,unit_cost,hotel_name in studioMBookings:
		total = studioMBookingsDict.get(check_in_date, 0) + unit_cost
		studioMBookingsDict[check_in_date] = total
	# print("studioMBookingsDict")
	# print(studioMBookingsDict.items())
	# print("---")

	discoveryPackageBookingsDict = {}
	for check_in_date,unit_cost,hotel_name in discoveryPackageBookings:
		total = discoveryPackageBookingsDict.get(check_in_date, 0) + unit_cost
		discoveryPackageBookingsDict[check_in_date] = total
	# print("discoveryPackageBookingsDict")
	# print(discoveryPackageBookingsDict.items())
	# print("---")

	discoveryPackageBookingsTupleList = list(discoveryPackageBookingsDict.items())
	studioMBookingsTupleList = list(studioMBookingsDict.items())
	yorkHotelSingaporeBookingsTupleList = list(yorkHotelSingaporeBookingsDict.items())
	wSingaporeSentosaCoveBookingsTupleList = list(wSingaporeSentosaCoveBookingsDict.items())
	shangriLaSingaporeBookingsTupleList = list(shangriLaSingaporeBookingsDict.items())
	capellaSingaporeBookingsTupleList = list(capellaSingaporeBookingsDict.items())

	#each dates for each hotel
	discoveryPackageDates = [row[0] for row in discoveryPackageBookingsTupleList]
	studioMDates = [row[0] for row in studioMBookingsTupleList]
	yorkHotelSingaporeDates = [row[0] for row in yorkHotelSingaporeBookingsTupleList]
	wSingaporeSentosaCoveDates = [row[0] for row in wSingaporeSentosaCoveBookingsTupleList]
	shangriLaSingaporeDates = [row[0] for row in shangriLaSingaporeBookingsTupleList]
	capellaSingaporeDates = [row[0] for row in capellaSingaporeBookingsTupleList]

	#conbine all the dates and sort
	allDatesInBooking = discoveryPackageDates + studioMDates + yorkHotelSingaporeDates + wSingaporeSentosaCoveDates + shangriLaSingaporeDates + capellaSingaporeDates
	sortedBookingDates = sorted(allDatesInBooking)

	discoveryPackageIncome = [row[1] for row in discoveryPackageBookingsTupleList]
	studioMIncome = [row[1] for row in studioMBookingsTupleList]
	yorkHotelSingaporeIncome = [row[1] for row in yorkHotelSingaporeBookingsTupleList]
	wSingaporeSentosaCoveIncome = [row[1] for row in wSingaporeSentosaCoveBookingsTupleList]
	shangriLaSingaporeIncome = [row[1] for row in shangriLaSingaporeBookingsTupleList]
	capellaSingaporeIncome = [row[1] for row in capellaSingaporeBookingsTupleList]

	discoveryPackageDates = [row[0] for row in discoveryPackageBookingsTupleList]


	# print(studioMIncome)

	# print(labels) #dates
	# print(values) #price
	print(discoveryPackageDates)
	print(discoveryPackageIncome)
	discoveryPackageData = zip(discoveryPackageDates,discoveryPackageIncome)

	testData = []

	x = "x"
	y = "y"
	for a,b in discoveryPackageBookingsTupleList:
		testData.append({x: a, y: b})

	print(testData)
	# print(discoveryPackageDates)



		

	# return render_template('trend_chart.html', email=email, name=nameofuser)
	return render_template(
		'trend_chart.html',
		email=email, 
		name=nameofuser, 
		labels=sortedBookingDates, 
		discoveryPackageBookingsTupleList=discoveryPackageBookingsTupleList, 
		studioMBookingsTupleList=studioMBookingsTupleList, 
		yorkHotelSingaporeBookingsTupleList=yorkHotelSingaporeBookingsTupleList, 
		wSingaporeSentosaCoveBookingsTupleList=wSingaporeSentosaCoveBookingsTupleList, 
		shangriLaSingaporeBookingsTupleList=shangriLaSingaporeBookingsTupleList, 
		capellaSingaporeBookingsTupleList=capellaSingaporeBookingsTupleList
	)



@app.errorhandler(404) 
def page_not_found(e):
    return render_template('notFound.html'), 888

#running application
if __name__ == '__main__':
	app.run(debug=True)