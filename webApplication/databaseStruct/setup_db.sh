#!/bin/bash
sqlite3 mockIoT.db < initdb.sql 
cat insertToDetail.sql | sqlite3 mockIoT.db