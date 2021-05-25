#!/bin/bash

if [ ! -d venv ]; then
	echo "Installing virtual env"
  python3 -m venv venv 
	source venv/bin/activate
	pip3 install -r requirements.txt
else
	echo "Virtual env already exist, exiting"
fi
