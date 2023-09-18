#!/bin/bash

# install python dependencies
cd ..
python3 -m venv venv
venv/bin/activate
pip install -r requirements.txt

# setup db
cd webApplication/databaseStruct
./setup_db.sh
