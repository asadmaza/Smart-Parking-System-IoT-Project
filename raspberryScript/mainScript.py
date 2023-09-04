import requests

url = 'localhost:5000/receiveStatusChange'



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
    print(arrayOfInput[0])
    print(arrayOfInput[1])
    print(parkingBay[arrayOfInput[0]])
    if(arrayOfInput[1] == 'freeSpace'):
        status = 0
    elif(arrayOfInput[1] == 'occupiedSpace'):
        status = 1
    elif(arrayOfInput[1] == 'reservedSpace'):
        status = 2
    if(parkingBay[arrayOfInput[0]] != status):
        postObject = {
                        'targetSpace':arrayOfInput[0],
                        'targetStatus':status,
                    }
        print(postObject)
