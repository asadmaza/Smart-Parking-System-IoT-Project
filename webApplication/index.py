from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from sqlalchemy import select, create_engine, update
import os
import json
import boto3
from datetime import datetime, date, time

file_path = os.path.abspath(os.getcwd())+"/databaseStruct/mockIoT.db"

dynamo_client = boto3.client('dynamodb')
db = SQLAlchemy()
scheduler = APScheduler()
myMQTTClient = AWSIoTMQTTClient("aji_laptop")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + file_path

# Topic const
INIT_BAY_STATE = "INIT_BAY_STATE"
BAY_STATUS_CHANGE_FROM_DEVICE = "BAY_STATUS_CHANGE_FROM_DEVICE"
FEEDBACK_TO_DEVICE_FROM_CHANGING_STATUS = "FEEDBACK_TO_DEVICE_FROM_CHANGING_STATUS" # maybe publish to this
SEND_BAY_CHANGE_STATUS_WHEN_RESERVED = "SEND_BAY_CHANGE_STATUS_WHEN_RESERVED" # publish to this
SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED = "SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED" # publish to this
FEEDBACK_FROM_DEVICE_WHEN_BAY_IS_RESERVED = "FEEDBACK_FROM_DEVICE_WHEN_BAY_IS_RESERVED" 

# Global Variable for waiting state
feedbackWaitingControl = False

def customCallback(client, userdata, message):
    print(message.topic)
    if(message.topic == BAY_STATUS_CHANGE_FROM_DEVICE):
        print("Received a bay status change from device : ")
        print(message.payload.decode("utf-8"))
        statusChangeFromDevice(message.payload.decode("utf-8"))
    # if(message.topic == FEEDBACK_FROM_DEVICE_WHEN_BAY_IS_RESERVED):
    #     print("Received a feedback message from device : ")
    #     print(message.payload.decode("utf-8"))
    #     # To-Do -> change the feedbackWaitingControl to True
    elif(message.topic == INIT_BAY_STATE):
        print("Received a feedback message from device : ")
        print(message.payload.decode("utf-8"))
        giveinitialBayState()

# AWS IoT client setup

myMQTTClient.configureEndpoint("a30y98prchbi0n-ats.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials(os.path.abspath(os.getcwd())+"/aws-certif/root-CA.crt",
                                      os.path.abspath(os.getcwd())+"/aws-certif/aji_laptop.private.key",
                                      os.path.abspath(os.getcwd())+"/aws-certif/aji_laptop.cert.pem")

# Confirm MQTT Connection
myMQTTClient.connect()
myMQTTClient.subscribe(BAY_STATUS_CHANGE_FROM_DEVICE, 1, customCallback)
# myMQTTClient.subscribe(FEEDBACK_FROM_DEVICE_WHEN_BAY_IS_RESERVED, 1, customCallback)
myMQTTClient.subscribe(INIT_BAY_STATE, 1, customCallback)

db.init_app(app)
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
    is_expired = db.Column(db.Integer, nullable=False)

@app.route("/")
def homePage():
    # Check IP validation, if ip address for admin then show navbar to go to statistics and camera stream
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
        bayStatus = {parking_bay:2}
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Update timestamp here
        message = json.dumps({"timestamp": timestamp, "data": bayStatus})
        myMQTTClient.publish(SEND_BAY_CHANGE_STATUS_WHEN_RESERVED, json.dumps(message), 1)
        # Maybe not do this as well To-Do -> wait for a feedback from the raspberry pi via subscriber by doing a while loop the condition is in the feedbackWaitingControl in global variable, 

        getParkingBayDetail = select(ParkingBayDetail).where(ParkingBayDetail.parking_bay_name==parking_bay)
        queryResult = createConnectionAndExecuteQuery(getParkingBayDetail)
        for row in queryResult:
            parkingBayId = int(row.rowid)
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
                booking_exit_time = exitDate,
                is_expired = 0)
        db.session.add(entry)

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

# function for checking the db each minutes to check for expiring reservation but the bay is not filled(status=1)
@scheduler.task('cron', id='resettingExpiredBay', minute='*')
def resettingExpiredBay():
    with scheduler.app.app_context():
        getBookingDetail = select(BookingParkingBay).where(BookingParkingBay.booking_exit_time<datetime.now()).where(BookingParkingBay.is_expired==0)
        queryResultBookingDetail = createConnectionAndExecuteQuery(getBookingDetail)
        for row in queryResultBookingDetail:
                bookingId = int(row.rowid)
                parkingBayId = row.parking_bay_id
                
                updateExpiredParkingBayDetail = ParkingBayDetail.query.filter_by(rowid=parkingBayId).first()
                updateExpiredParkingBayDetail.parking_bay_status = 0

                updateExpiredBookingDetail = BookingParkingBay.query.filter_by(rowid=bookingId).first()
                updateExpiredBookingDetail.is_expired = 1

                bayStatus = {updateExpiredParkingBayDetail.parking_bay_name:0}
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Update timestamp here
                message = json.dumps({"timestamp": timestamp, "data": bayStatus})
                myMQTTClient.publish(SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED, json.dumps(message), 1)
                
                db.session.commit()

    return redirect("/",200)

# function to subscribe the mqtt topic and change the status accordingly (when a car is entering a valid bay, when a car is exiting a non-reserved bay, 
# when a car is entering a reserved bay, when a car is exiting a reserved bay)
def statusChangeFromDevice(messagePayload):
    with app.app_context():
        json_object = json.loads(messagePayload)
        timeStamp = json_object["timestamp"]
        timeStampDateObject = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S")
        dataDictionary = json_object["data"]
        for i in dataDictionary:
            parkingName = i
            statusChange = dataDictionary[i]["state"]
        getParkingBayDetail = select(ParkingBayDetail).where(ParkingBayDetail.parking_bay_name==parkingName) #change to actual variable from the message payload
        queryResult = createConnectionAndExecuteQuery(getParkingBayDetail)
        for row in queryResult:
            parkingBayId = int(row.rowid)
            parkingName = row.parking_bay_name
        if(statusChange == 0):
            print("car is exiting parking bay")
            latestParkingBayTimestamp = select(ParkingBayTimestamp).where(ParkingBayTimestamp.parking_bay_id==parkingBayId).order_by(ParkingBayTimestamp.parking_bay_entry_time.desc()).limit(1)
            executeQueryFindLatestParkingStamp = createConnectionAndExecuteQuery(latestParkingBayTimestamp)
            # create exception when no data is found
            for row in executeQueryFindLatestParkingStamp:
                timeStampRowid = row.rowid
                parkingBayId = row.parking_bay_id
                entryTime = row.parking_bay_entry_time
            exitTime = timeStampDateObject
            totalDuration = exitTime-entryTime
            secondsInDay = 24 * 60 * 60
            totalMinutes = (totalDuration.days * secondsInDay + totalDuration.seconds) / 60

            updateParkingBayTimestampQuery = ParkingBayTimestamp.query.filter_by(rowid=timeStampRowid).first()
            updateParkingBayTimestampQuery.parking_bay_exit_time = exitTime
            updateParkingBayTimestampQuery.parking_bay_total_minutes = totalMinutes

            updateParkingBayDetailQuery = ParkingBayDetail.query.filter_by(rowid=parkingBayId).first()
            updateParkingBayDetailQuery.parking_bay_status = statusChange
            
            db.session.commit()

        elif(statusChange == 1):
            print("car is entering parking bay")
            updateParkingBayDetailQuery = ParkingBayDetail.query.filter_by(rowid=parkingBayId).first()
            
            if(updateParkingBayDetailQuery.parking_bay_status == 2):
                updateParkingBayDetailQuery.parking_bay_status = statusChange
                updateBookingDetail = BookingParkingBay.query.filter_by(BookingParkingBay.parking_bay_id==parkingBayId).filter_by(BookingParkingBay.is_expired==0).first()
                updateBookingDetail.is_expired = 1
            
            elif(updateParkingBayDetailQuery.parking_bay_status == 0):
                updateParkingBayDetailQuery.parking_bay_status = statusChange

            entry = ParkingBayTimestamp(parking_bay_id = parkingBayId, parking_bay_entry_time = timeStampDateObject)
            db.session.add(entry)
            
            db.session.commit() 

        return redirect("/",200)

def giveinitialBayState():
    # To-Do -> implement this function
    # query and get all the parking bay detail
    # publish to the raspberry pi
    parking_bays = ParkingBayDetail.query.all()

    bay_states = {}
    for row in parking_bays:
        bay_states[row.parking_bay_name] = row.parking_bay_status

    message = {"bay_states": bay_states}
    myMQTTClient.publish(INIT_BAY_STATE, json.dumps(message), 1)  

    return redirect("/", 200)

@app.route("/2")
def homePage2():
    # Check IP validation, if ip address for admin then show navbar to go to statistics and camera stream
    arrayOfParkingBay = []
    totalAvailableParkingBay = 0
    
    dynamoDBQuery = dynamo_client.scan(TableName='parking_bay_detail2')
    for x in dynamoDBQuery['Items']:
        parkingBayName = ''
        parkingBayType = 0
        parkingBayStatus = 0
        for y in x:
            if( y == 'parking_bay_name'):
                parkingBayName = x[y]['S']
            elif( y == 'parking_bay_type'):
                parkingBayType = int(x[y]['N'])
            elif( y == 'parking_bay_status'):
                parkingBayStatus = int(x[y]['N'])
        if (parkingBayStatus == 0):
            totalAvailableParkingBay = totalAvailableParkingBay + 1

        parkingBayData = {
            'parkingBayName':parkingBayName,
            'status': parkingBayStatus,
            'parkingType' : parkingBayType
        }

        arrayOfParkingBay.append(parkingBayData)

    result = {
        'availableSpace':totalAvailableParkingBay,
        'perBay':sorted(arrayOfParkingBay, key=lambda d: d['parkingBayName'])
    }

    return render_template('homePage.html', result=result)

if __name__ == '__main__':
    try:
        app.run(debug=True, port=5000)

    except KeyboardInterrupt:
        print("Terminating and cleaning up")
        db.session.close()
        myMQTTClient.disconnect()