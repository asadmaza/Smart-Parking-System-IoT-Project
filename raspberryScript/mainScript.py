import requests

url = 'http://localhost:5000/receiveStatusChange' #move this to config file



# initiate parking bay dictionary
# parkingBayId : status
# status definition
freeSpace = 0
occupiedSpace = 1
reservedSpace = 2
parkingBay = { # will change to read each initial space status based on csv which contains which bay is reserved and which is not
                "A1":freeSpace,
                "A2":freeSpace,
                "A3":reservedSpace
            }

while(True):
    statusChangeInput = input("input the bay name and status to : ") #Change this to actual sensor read
    arrayOfInput = statusChangeInput.split("-")
    status = int(arrayOfInput[1])
    if(parkingBay[arrayOfInput[0]] != status):
        jsonData = {
            "parkingName" : arrayOfInput[0],
            "statusChange" : status
        }
        x = requests.post(url, json = jsonData)
        print(x.text)
        parkingBay[arrayOfInput[0]] = status
