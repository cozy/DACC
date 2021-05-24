#!/bin/bash

if [ ! -d venv ]; then
	echo "Installing virtual env"
	mkdir venv
	virtualenv -p python3 venv
	source venv/bin/activate
	pip3 install -r requirements.txt
else
	echo "Virtual env already exist, exiting"
fi
