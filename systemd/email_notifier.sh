#!/bin/bash
PYTHON_EXE=/home/pi/venv/ipcam/bin/python3
APP=/home/pi/git/ipcam/src/notifier.py
$PYTHON_EXE $APP \
    --email          "pilikia.ibeach@gmail.com" \
    --username       "pilikia.ibeach@gmail.com" \
    --keyring_system 'ibeach-email'             \
    --smtp           'smtp.gmail.com:587'       \
    --sms_gateways   'nniles@oceanit.com'       \
    --service        'ibeach'
