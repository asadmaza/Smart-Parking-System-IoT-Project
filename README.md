# Group3-CITS5506-2023
Repository for Group 3 Course CITS5506 2023 Second Semester

## To Do List
### raspberry Script
    - adjust the input from manual typing to read from a sensor

### web application    
    - Create a function to subscribe from mqtt aws iot core and change the state of the webapp(sqlite.db) whenever a car is entering and exiting the parking bay and publish back as a feedback from webapp
    - Create a function to publish to mqtt aws iot core whenever a parking bay is reserved from the webapp and subscribe to check for feedback from the raspberry pi
    - Create a scheduler function that runs every minute to check if there's an expiring reserved bay and publish to raspberry pi
    
    -- Nice to Have --
    - Create input validation for the booking form
    - Change the web UI to accommodate for camera streaming on the situation of the parking bay
    - Send email to customer whenever a parking bay is reserved from the webapp
    - Apply best practice such as separate config

## How to run
1. create a new virtual environment
    python3 -m venv venv
2. activate environment
    > on macOS/Linux
        venv/bin/activate
    > on windows
        venv\Scripts\activate.bat
3. install requirement
    pip install -r requirements.txt
4. run the web app
    cd webApplication
    flask --app index run

## How to create local db for testing or maybe funsies
1. install sqlite3
2. cd to webApplicatoin/databaseStruct
3. run
    sqlite3 mockIoTDB.db < initdb.sql 
4. run to populate the mock data to the database
    cat insertToDetail.sql | sqlite3 mockIoTDB.db