from flask import Flask, render_template, request, redirect
from flask_apscheduler import APScheduler
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os
import json
import boto3
from datetime import datetime, date, time

dynamo_client = boto3.client("dynamodb")
scheduler = APScheduler()
myMQTTClient = AWSIoTMQTTClient("aji_laptop")
app = Flask(__name__)

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
    if(message.topic == BAY_STATUS_CHANGE_FROM_DEVICE):
        print("Received a bay status change from device : ")
        statusChangeFromDevice(message.payload.decode("utf-8"))
    elif(message.topic == INIT_BAY_STATE):
        print("Received a feedback message from device : ")
        giveinitialBayState()

# AWS IoT client setup
myMQTTClient.configureEndpoint("a30y98prchbi0n-ats.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials(os.path.abspath(os.getcwd())+"/aws-certif/root-CA.crt",
                                      os.path.abspath(os.getcwd())+"/aws-certif/aji_laptop.private.key",
                                      os.path.abspath(os.getcwd())+"/aws-certif/aji_laptop.cert.pem")

# Confirm MQTT Connection
myMQTTClient.connect()
myMQTTClient.subscribe(BAY_STATUS_CHANGE_FROM_DEVICE, 1, customCallback)
myMQTTClient.subscribe(INIT_BAY_STATE, 1, customCallback)

scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

trusted_proxies = ('127.0.0.1')

def giveinitialBayState():
    # To-Do -> implement this function
    # query and get all the parking bay detail
    # publish to the raspberry pi
    arrayOfParkingBay = []

    dynamoDBQuery = dynamo_client.scan(TableName="parking_bay_detail2")
    # need to check if the request success or not
    for x in dynamoDBQuery["Items"]:
        parkingBayName = ""
        parkingBayType = 0
        parkingBayStatus = 0
        for y in x:
            if( y == "parking_bay_name"):
                parkingBayName = x[y]["S"]
            elif( y == "parking_bay_type"):
                parkingBayType = int(x[y]["N"])
            elif( y == "parking_bay_status"):
                parkingBayStatus = int(x[y]["N"])

        parkingBayData = {
            "parkingBayName":parkingBayName,
            "status": parkingBayStatus,
            "parkingType" : parkingBayType
        }

        arrayOfParkingBay.append(parkingBayData)

    result = {
        "message":sorted(arrayOfParkingBay, key=lambda d: d["parkingBayName"])
    }
    myMQTTClient.publish(INIT_BAY_STATE, json.dumps(result), 1)  

    return redirect("/", 200)

@app.route("/")
def homePage():
    # Check IP validation, if ip address for admin then show navbar to go to statistics and camera stream
    arrayOfParkingBay = []
    totalAvailableParkingBay = 0

    dynamoDBQuery = dynamo_client.scan(TableName="parking_bay_detail2")
    # need to check if the request success or not
    for x in dynamoDBQuery["Items"]:
        parkingBayName = ""
        parkingBayType = 0
        parkingBayStatus = 0
        for y in x:
            if( y == "parking_bay_name"):
                parkingBayName = x[y]["S"]
            elif( y == "parking_bay_type"):
                parkingBayType = int(x[y]["N"])
            elif( y == "parking_bay_status"):
                parkingBayStatus = int(x[y]["N"])
        if (parkingBayStatus == 0):
            totalAvailableParkingBay = totalAvailableParkingBay + 1

        parkingBayData = {
            "parkingBayName":parkingBayName,
            "status": parkingBayStatus,
            "parkingType" : parkingBayType
        }

        arrayOfParkingBay.append(parkingBayData)

    result = {
        "availableSpace":totalAvailableParkingBay,
        "perBay":sorted(arrayOfParkingBay, key=lambda d: d["parkingBayName"])
    }

    return render_template("homePage.html", result=result)

@app.route("/bookingForm/<string:parking_bay>", methods=["GET","POST"])
def bookingForm(parking_bay):
    if request.method == "GET":
        result = {
            "pickedParkingBay":parking_bay
        }
        return render_template("bookingForm.html", result=result)
    if request.method == "POST":
        fullName = request.form["fname"]
        email = request.form["email"]
        phoneNumber = request.form["phnumber"]
        plateNumber = request.form["pnumber"]
        timeOut = request.form["tOut"]

        print("a bay is being reserved")
        bayStatus = {parking_bay:2}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Update timestamp here
        message = json.dumps({"timestamp": timestamp, "data": bayStatus})

        myMQTTClient.publish(SEND_BAY_CHANGE_STATUS_WHEN_RESERVED, json.dumps(message), 1)

        splitTimeOut = timeOut.split(":")
        today = date.today()
        exitDate = datetime(today.year, today.month, today.day, int(splitTimeOut[0]), int(splitTimeOut[1]))

        responseUpdateBayDetail = dynamo_client.update_item(
            TableName="parking_bay_detail2",
            Key={
                "parking_bay_name": {
                    "S": parking_bay
                }
            },
            AttributeUpdates={
                "parking_bay_status": {
                    "Value": {
                        "N": "2"
                    },
                    "Action": "PUT"
                }
            },
        )

        # need to check if the request success or not
        print(responseUpdateBayDetail)
        
        responsePutLog = dynamo_client.put_item(
            TableName="parking_bay_log",
            Item={
                "UUID" : {
                    "S": str(timestamp)
                },
                "parking_bay_name": {
                    "S": parking_bay
                },
                "parking_bay_entry_time": {
                    "S": ""
                },
                "parking_bay_exit_time": {
                    "S": ""
                },
                "parking_bay_total_minutes": {
                    "N": "0"
                },
                "customer_full_name": {
                    "S": fullName
                },
                "customer_email": {
                    "S": email
                },
                "customer_phone_number": {
                    "S": str(phoneNumber)
                },
                "customer_plate_number": {
                    "S": plateNumber
                },
                "booking_entry_time": {
                    "S": str(timestamp) 
                },
                "booking_exit_time": {
                    "S": str(exitDate)
                },
                "is_booking_expired": {
                    "N": "0"
                },
                "is_bay_booked": {
                    "N": "1"
                },
            }
        )

        # need to check if the request success or not
        print(responsePutLog)

        result = {
            "pickedParkingBay":parking_bay,
            "fname":fullName,
            "email":email,
            "phnumber":phoneNumber,
            "pnumber":plateNumber,
            "tIn":timestamp,
            "tOut":timeOut,
        }
        
        return render_template("bookingFormSuccess.html", result=result) 

@scheduler.task("cron", id="resettingExpiredBay", minute="*")
def resettingExpiredBay():
    with scheduler.app.app_context():
        queryAllBayStatus = dynamo_client.scan(TableName="parking_bay_detail2")
        # need to check if the request success or not
        arrayOfParkingBay = []
        for x in queryAllBayStatus["Items"]:
            parkingBayName = ""
            parkingBayType = 0
            parkingBayStatus = 0
            for y in x:
                if( y == "parking_bay_name"):
                    parkingBayName = x[y]["S"]
                elif( y == "parking_bay_type"):
                    parkingBayType = int(x[y]["N"])
                elif( y == "parking_bay_status"):
                    parkingBayStatus = int(x[y]["N"])

            if ((parkingBayType == 2) and (parkingBayStatus == 2)):
                arrayOfParkingBay.append(parkingBayName)

        queryAllBayLog = dynamo_client.scan(TableName="parking_bay_log")
        # need to check if the request success or not

        arrayOfLog = []
        arrayOfParkingBayName = []

        for log in queryAllBayLog["Items"]:
           for y in log:
                if( y == "parking_bay_name"):
                    if log[y]["S"] in arrayOfParkingBay:
                        arrayOfLog.append(log)
                        arrayOfParkingBayName.append(log[y]["S"])
        
        for log in arrayOfLog:
            tableID = ""
            isExpired = ""
            isBooked = ""
            bookingExitTime = ""

            for y in log:
                if( y == "UUID"):
                    tableID = log[y]["S"]
                elif ( y == "is_booking_expired" ):
                    isExpired = log[y]["N"]
                elif ( y == "is_bay_booked" ):
                    isBooked = log[y]["N"]
                elif ( y == "booking_exit_time" ):
                    bookingExitTime = log[y]["S"]

            datetime_object = datetime.strptime(bookingExitTime, "%Y-%m-%d %H:%M:%S")
            
            if((isBooked == "1") and (isExpired == "0") and (datetime.now() > datetime_object)):
                responseUpdateLogDetail = dynamo_client.update_item(
                        TableName="parking_bay_log",
                        Key={
                            "UUID": {
                                "S": tableID
                            }
                        },
                        AttributeUpdates={
                            "is_booking_expired": {
                                "Value": {
                                    "N": "1"
                                },
                                "Action": "PUT"
                            }
                        },
                    )  
                
                # need to check if the request success or not
                print(responseUpdateLogDetail)

                responseUpdateBayDetail = dynamo_client.update_item(
                    TableName="parking_bay_detail2",
                    Key={
                        "parking_bay_name": {
                            "S": parkingBayName
                        }
                    },
                    AttributeUpdates={
                        "parking_bay_status": {
                            "Value": {
                                "N": "0"
                            },
                            "Action": "PUT"
                        }
                    },
                )  
                # need to check if the request success or not
                print(responseUpdateBayDetail)

                bayStatus = {}

                for bayName in arrayOfParkingBayName:
                    bayStatus[bayName] = 0

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Update timestamp here
                message = json.dumps({"timestamp": timestamp, "data": bayStatus})
                myMQTTClient.publish(SEND_BAY_CHANGE_STATUS_WHEN_RESERVATION_EXPIRED, json.dumps(message), 1)
                
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
        
        logWithSameParkingName = []

        queryParkingBayLog = dynamo_client.scan(TableName="parking_bay_log")
        # need to check if the request success or not
        for x in queryParkingBayLog["Items"]:
            logData = {}
            if ( x["parking_bay_name"]["S"] == parkingName ):
                for y in x:
                    if( y == "parking_bay_name"):
                        logData["BayName"] = x[y]["S"]
                    elif ( y == "UUID" ):
                        logData["UUID"] = x[y]["S"]
                    elif ( y == "parking_bay_entry_time" ):
                        entryTime = x[y]["S"]
                        if (entryTime == ''):
                          logData["parkingBayEntryTime"] = ''
                        else:
                          logData["parkingBayEntryTime"] = datetime.strptime(entryTime, "%Y-%m-%d %H:%M:%S")
                    elif ( y == "parking_bay_exit_time" ):
                        exitTime = x[y]["S"]
                        if (exitTime == ''):
                            logData["parkingBayExitTime"] = ''
                        else:
                            logData["parkingBayExitTime"] = datetime.strptime(exitTime, "%Y-%m-%d %H:%M:%S")
                    elif ( y == "parking_bay_total_minutes" ):
                        logData["parkingBayTotalMinutes"] = x[y]["N"]
                    elif ( y == "is_booking_expired" ):
                        logData["isBookingExpired"] = x[y]["N"]
                    elif ( y == "is_bay_booked" ):
                        logData["isBayBooked"] = x[y]["N"]  
                logWithSameParkingName.append(logData)

        if (len(logWithSameParkingName)>0):
            logWithSameParkingName = sorted(logWithSameParkingName, key=lambda d: d["UUID"], reverse=True)
            logWithSameParkingName = logWithSameParkingName[:1]
        print(logWithSameParkingName)
        if(statusChange == 0):
            print("car is exiting parking bay")

            entryTime = logWithSameParkingName[0]["parkingBayEntryTime"]
            exitTime = timeStampDateObject
            totalDuration = exitTime-entryTime
            secondsInDay = 24 * 60 * 60
            totalMinutes = (totalDuration.days * secondsInDay + totalDuration.seconds) / 60

            responseUpdateBayDetail = dynamo_client.update_item(
                TableName="parking_bay_detail2",
                Key={
                    "parking_bay_name": {
                        "S": parkingName
                    }
                },
                AttributeUpdates={
                    "parking_bay_status": {
                        "Value": {
                            "N": str(statusChange)
                        },
                        "Action": "PUT"
                    }
                },
            )

            # need to check if the request success or not
            print(responseUpdateBayDetail)

            responseUpdateLogDetail = dynamo_client.update_item(
                TableName="parking_bay_log",
                Key={
                    "UUID": {
                        "S": logWithSameParkingName[0]["UUID"]
                    }
                },
                AttributeUpdates={
                    "parking_bay_exit_time": {
                        "Value": {
                            "S": str(exitTime)
                        },
                        "Action": "PUT"
                    },
                    "parking_bay_total_minutes": {
                        "Value": {
                            "N": str(totalMinutes)
                        },
                        "Action": "PUT"
                    }
                },
            )

            print(responseUpdateLogDetail)
            # need to check if the request success or not

        elif(statusChange == 1):
            print("car is entering parking bay")
            queryParkingBayDetail = dynamo_client.scan(TableName="parking_bay_detail2")
            parkingBayType = 0
            for x in queryParkingBayDetail["Items"]:
                if ( x["parking_bay_name"]["S"] == parkingName ):
                    parkingBayType = int(x["parking_bay_type"]["N"])
            if(parkingBayType == 2):
                print("entering a booked bay")
                # update existing item (latest book log for that bay)
                bookedParkingLog = []

                queryParkingBayLog = dynamo_client.scan(TableName="parking_bay_log")
                # need to check if the request success or not

                for x in queryParkingBayLog["Items"]:
                    logData = {}
                    if ( (x["parking_bay_name"]["S"] == parkingName) and (x["is_booking_expired"]["N"] == "0") ):
                        for y in x:
                            if( y == "parking_bay_name"):
                                logData["BayName"] = x[y]["S"]
                            elif ( y == "UUID" ):
                                logData["UUID"] = x[y]["S"]
                            elif ( y == "is_booking_expired" ):
                                logData["isBookingExpired"] = x[y]["N"] 
                            elif ( y == "booking_exit_time" ):
                                bookingExitTime = x[y]["S"]
                                logData["parkingBookingExitTime"] = datetime.strptime(bookingExitTime, "%Y-%m-%d %H:%M:%S")
                        bookedParkingLog.append(logData)

                bookedParkingLog = sorted(bookedParkingLog, key=lambda d: d["parkingBookingExitTime"], reverse=True)
                bookedParkingLog = bookedParkingLog[:1]

                responseUpdateLogDetail = dynamo_client.update_item(
                    TableName="parking_bay_log",
                    Key={
                        "UUID": {
                            "S": logWithSameParkingName[0]["UUID"]
                        }
                    },
                    AttributeUpdates={
                        "is_booking_expired": {
                            "Value": {
                                "N": "1"
                            },
                            "Action": "PUT"
                        },
                        "parking_bay_entry_time": {
                            "Value": {
                                "S": str(timeStampDateObject)                            
                            },
                            "Action": "PUT"

                        },
                    },
                ) 
                print(responseUpdateLogDetail)
                # need to check if the request success or not        

            else:
                print("entering a normal bay")
                # put a new item
                responsePutLog = dynamo_client.put_item(
                    TableName="parking_bay_log",
                    Item={
                        "UUID" : {
                            "S": str(timeStampDateObject)
                        },
                        "parking_bay_name": {
                            "S": parkingName
                        },
                        "parking_bay_entry_time": {
                            "S": str(timeStampDateObject)
                        },
                        "parking_bay_exit_time": {
                            "S": ""
                        },
                        "parking_bay_total_minutes": {
                            "N": "0"
                        },
                        "customer_full_name": {
                            "S": ""
                        },
                        "customer_email": {
                            "S": ""
                        },
                        "customer_phone_number": {
                            "S": ""
                        },
                        "customer_plate_number": {
                            "S": ""
                        },
                        "booking_entry_time": {
                            "S": ""
                        },
                        "booking_exit_time": {
                            "S": ""
                        },
                        "is_booking_expired": {
                            "N": "1"
                        },
                        "is_bay_booked": {
                            "N": "0"
                        },
                    }
                )

                # need to check if the request success or not
                print(responsePutLog)

            responseUpdateBayDetail = dynamo_client.update_item(
                TableName="parking_bay_detail2",
                Key={
                    "parking_bay_name": {
                        "S": parkingName
                    }
                },
                AttributeUpdates={
                    "parking_bay_status": {
                        "Value": {
                            "N": str(statusChange)
                        },
                        "Action": "PUT"
                    }
                },
            )

        return redirect("/",200)

@app.route("/visualization")
def visualizationDashboard():
    return redirect("/",200)

@app.route("/cameraFeed")
def cameraFeedDashBoard():    
    url = "http://3.106.140.164:8081/"
    result = {
        "url":url
    }
    return render_template("cameraFeed.html", result=result)

if __name__ == "__main__":
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)

    except KeyboardInterrupt:
        print("Terminating and cleaning up")
        myMQTTClient.disconnect()
