#!/bin/bash
SYSD_PATH=/etc/systemd/system/
sudo cp ibeach.service $SYSD_PATH
sudo cp ibeach-email.service $SYSD_PATH

sudo systemctl daemon-reload
sudo systemctl start ibeach-email.service
sudo systemctl start ibeach.service

sudo systemctl status ibeach-email.service
sudo systemctl status ibeach.service