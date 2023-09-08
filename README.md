# Group3-CITS5506-2023
Repository for Group 3 Course CITS5506 2023 Second Semester

## To Do List
### raspberry Script
    - adjust the input from manual typing to read from a sensor

### web application    
    - make a pretty webapp rather than a simple one
    - apply best practice such as separate config

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