# Group3-CITS5506-2023
Repository for Group 3 Course CITS5506 2023 Second Semester

# Final Code to Use in Presentation and Vide
1. webApplication/indexAlternate.py
2. 8. RPI Local Script/integration_scriptV3.py

## To Do List
### raspberry Script
    - make a v4 of asad's local script that actually 
        1. publish to the aws iot core topic
        2. subscribe to the aws iot core topic
        3. init the bay states by publish a message to the topic and waiting for the appropriate response

### web application    
    - going to assume the booking entry time is always from right now until designated booking exit time
    - going to assume the reserved bay is only for people who make reservation beforehand
    - if a reservation is expired, then the bay will return to the state of can be reserved and customer needs to reserved it first before park their car in it
    
    
    -- Nice to Have --
    - Create input validation for the booking form
    - Change the web UI to accommodate for camera streaming on the situation of the parking bay
    - Send email to customer whenever a parking bay is reserved from the webapp
    - Apply best practice such as separate config

### Potential Improvement
#### Web application side
    - safeguard from racing condition
    - implement payment method
    - user account implementation
    

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

## How to contribute
If you are interested to do one of the function that's in the web application section please do this first
1. make a new branch from this aji_branch or main branch if this is already merged
    git checkout -b "<insert branch name>" - format the branch name like yourName_what_you_are_trying_to_do
2. make your changes
3. test it
4. stage and commit your work
    git add . -> do this in the Group3...... folder
    git commit -m "<insert commit message>"
5. push to your branch
    git push origin <branch_name>
6. create a pull request

# Feel free to DM if you have anything to ask
