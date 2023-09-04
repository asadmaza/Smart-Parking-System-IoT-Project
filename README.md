# Group3-CITS5506-2023
Repository for Group 3 Course CITS5506 2023 Second Semester

## To Do List
### raspberry Script
    - make a fake function to do post function, the target is localhost webapp

### web application    
    - make function to actually receive the post request
    - make simple html to display the bay status and number of available parking space
    - make a function to do CRUD to database

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
