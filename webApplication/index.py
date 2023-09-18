from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from sqlalchemy import select, create_engine, update
import os
from datetime import datetime, date

file_path = os.path.abspath(os.getcwd())+"/databaseStruct/mockIoT.db"

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + file_path
db.init_app(app)
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

def createConnectionAndExecuteQuery(sqlStatement):
    engine = create_engine('sqlite:///' + file_path)
    with engine.connect() as connection:
        result = connection.execute(sqlStatement)
        return result

# define models for query
class ParkingBayDetail(db.Model):
    rowid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parking_bay_name = db.Column(db.String, nullable=False)
    parking_bay_status = db.Column(db.Integer, nullable=False)

class ParkingBayTimestamp(db.Model):
    rowid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parking_bay_id = db.Column(db.Integer, nullable=False)
    parking_bay_entry_time = db.Column(db.DateTime, nullable=False)
    parking_bay_exit_time = db.Column(db.DateTime, nullable=True) 
    parking_bay_total_minutes = db.Column(db.Integer, nullable=True)

class BookingParkingBay(db.Model):
    rowid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parking_bay_id = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    plate_number = db.Column(db.String, nullable=False)
    booking_entry_time = db.Column(db.DateTime, nullable=False)
    booking_exit_time = db.Column(db.DateTime, nullable=False)

@app.route("/home")
def homePage():
    arrayOfParkingBay = []
    totalAvailableParkingBay = 0

    parking_bays = ParkingBayDetail.query.all()

    for row in parking_bays:
        
        parkingBayData = {
            'parkingBayName':row.parking_bay_name,
            'status':row.parking_bay_status,
        }

        if(row.parking_bay_status == 0):
            totalAvailableParkingBay = totalAvailableParkingBay + 1

        arrayOfParkingBay.append(parkingBayData)

    result = {
        'availableSpace':totalAvailableParkingBay,
        'perBay':arrayOfParkingBay
    }
    return render_template('homePage.html', result=result)

@app.route("/bookingForm/<string:parking_bay>", methods=['GET','POST'])
def bookingForm(parking_bay):
    if request.method == 'GET':
        result = {
            'pickedParkingBay':parking_bay
        }
        return render_template('bookingForm.html', result=result)
    if request.method == 'POST':
        fullName = request.form['fname']
        email = request.form['email']
        phoneNumber = request.form['phnumber']
        plateNumber = request.form['pnumber']
        timeIn = request.form['tIn']
        timeOut = request.form['tOut']

        print("a bay is being reserved")
        # publish message to indicate a parking bay is reserved

        # wait for a feedback from the raspberry pi via subscriber 

        getParkingBayDetail = select(ParkingBayDetail).where(ParkingBayDetail.parking_bay_name==parking_bay)
        queryResult = createConnectionAndExecuteQuery(getParkingBayDetail)
        for row in queryResult:
            parkingBayId = int(row.rowid)
            parkingName = row.parking_bay_name
        updateParkingBayDetailQuery = ParkingBayDetail.query.filter_by(rowid=parkingBayId).first()
        updateParkingBayDetailQuery.parking_bay_status = 2
        splitTimeIn = timeIn.split(":")
        splitTimeOut = timeOut.split(":")
        today = date.today()
        entryDate = datetime(today.year, today.month, today.day, int(splitTimeIn[0]), int(splitTimeIn[1]))
        exitDate = datetime(today.year, today.month, today.day, int(splitTimeOut[0]), int(splitTimeOut[1]))
        entry = BookingParkingBay(parking_bay_id = parkingBayId,
                full_name = fullName,
                email = email,
                phone_number = phoneNumber,
                plate_number = plateNumber,
                booking_entry_time = entryDate,
                booking_exit_time = exitDate)
        db.session.add(entry)
        
        # except do rollback
    
        # finally commit  
        db.session.commit() 
        
        result = {
            'pickedParkingBay':parking_bay,
            'fname':fullName,
            'email':email,
            'phnumber':phoneNumber,
            'pnumber':plateNumber,
            'tIn':timeIn,
            'tOut':timeOut,
        }
        
        return render_template('bookingFormSuccess.html', result=result)  

# function to subscribe the mqtt topic and change the status accordingly (when a car is entering a valid bay, when a car is exiting a non-reserved bay, 
# when a car is entering a reserved bay, when a car is exiting a reserved bay)

# function for checking the db each minutes to check for expiring reservation but the bay is not filled(status=1)


# later deprecate all of below
@app.route("/")
def index():
    arrayOfParkingBay = []
    totalAvailableParkingBay = 0
    totalReservedParkingBay = 0
    totalOccupiedParkingBay = 0

    parking_bays = ParkingBayDetail.query.all()

    for row in parking_bays:
        parkingBayData = {
            'parkingBayName':row.parking_bay_name,
            'status':row.parking_bay_status,
        }
        if(row.parking_bay_status == 0):
            totalAvailableParkingBay = totalAvailableParkingBay + 1
        elif(row.parking_bay_status == 1):
            totalReservedParkingBay = totalReservedParkingBay + 1
        elif(row.parking_bay_status == 2):
            totalOccupiedParkingBay = totalOccupiedParkingBay + 1
        arrayOfParkingBay.append(parkingBayData)

    result = {
        'availableSpace':totalAvailableParkingBay,
        'reservedSpace':totalReservedParkingBay,
        'occupiedSpace':totalOccupiedParkingBay,
        'perBay':arrayOfParkingBay
    }

    return render_template('base.html',result=result)

@app.route("/receiveStatusChange", methods=['POST'])
def statusChange():
    if request.method == 'POST':
        request_data = request.get_json()
        parkingName = request_data['parkingName']
        statusChange = request_data['statusChange']
        getParkingBayDetail = select(ParkingBayDetail).where(ParkingBayDetail.parking_bay_name==parkingName)
        queryResult = createConnectionAndExecuteQuery(getParkingBayDetail)
        for row in queryResult:
            parkingBayId = int(row.rowid)
            parkingName = row.parking_bay_name
        if(statusChange == 0):
            print("car is exiting parking bay")
            latestParkingBayTimestamp = select(ParkingBayTimestamp).where(ParkingBayTimestamp.parking_bay_id==parkingBayId).order_by(ParkingBayTimestamp.parking_bay_entry_time.desc()).limit(1)
            executeQueryFindLatestParkingStamp = createConnectionAndExecuteQuery(latestParkingBayTimestamp)
            #create exception when no data is found
            for row in executeQueryFindLatestParkingStamp:
                timeStampRowid = row.rowid
                parkingBayId = row.parking_bay_id
                entryTime = row.parking_bay_entry_time
            exitTime = datetime.now()
            totalDuration = exitTime-entryTime
            secondsInDay = 24 * 60 * 60
            totalMinutes = (totalDuration.days * secondsInDay + totalDuration.seconds) / 60

            updateParkingBayTimestampQuery = ParkingBayTimestamp.query.filter_by(rowid=timeStampRowid).first()
            updateParkingBayTimestampQuery.parking_bay_exit_time = exitTime
            updateParkingBayTimestampQuery.parking_bay_total_minutes = totalMinutes

            # updateParkingBayTimestampQuery = update(ParkingBayTimestamp).where(ParkingBayTimestamp.parking_bay_id==parkingBayId).values(parking_bay_exit_time = exitTime,
                                                                                                                                        # parking_bay_total_minutes = totalMinutes)
            # make a try statement
            # executeQueryUpdateParkingBayTimestamp = createConnectionAndExecuteQuery(updateParkingBayTimestampQuery)
            
            updateParkingBayDetailQuery = ParkingBayDetail.query.filter_by(rowid=parkingBayId).first()
            updateParkingBayDetailQuery.parking_bay_status = statusChange
            # updateParkingBayDetailQuery = update(ParkingBayDetail).where(ParkingBayDetail.rowid==parkingBayId).values(parking_bay_status = statusChange)
            # make a try statement
            # executeQueryUpdateParkingBayDetail = createConnectionAndExecuteQuery(updateParkingBayDetailQuery)
            
            #finally
            db.session.commit()    
        elif(statusChange == 1):
            print("car is entering parking bay")
            updateParkingBayDetailQuery = ParkingBayDetail.query.filter_by(rowid=parkingBayId).first()
            updateParkingBayDetailQuery.parking_bay_status = statusChange
            # updateParkingBayDetailQuery = update(ParkingBayDetail).where(ParkingBayDetail.rowid==parkingBayId).values(parking_bay_status = statusChange)
            # executeQueryUpdateParkingBayDetail = createConnectionAndExecuteQuery(updateParkingBayDetailQuery)
            
            # try if something breaks roll back
            entry = ParkingBayTimestamp(parking_bay_id = parkingBayId,
                    parking_bay_entry_time = datetime.now())
            db.session.add(entry)
            
            # except do rollback
        
            # finally commit  
            db.session.commit() 
        return redirect("/",200)
    else:
        return '<h1>you are not allowed to access this page by this method</h1>'

if __name__ == '__main__':
    # run app in debug mode on port 5000
    # configure for publisher and subsrciber
    app.run(debug=True, port=5000)