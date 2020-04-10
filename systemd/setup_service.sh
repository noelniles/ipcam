#!/bin/bash
SYSD_PATH=/etc/systemd/system/
sudo cp ibeach.service $SYSD_PATH
sudo cp ibeach-notifier@.service $SYSD_PATH

sudo systemctl daemon-reload
sudo systemctl start ibeach-notifier@.service
sudo systemctl start ibeach.service

sudo systemctl status ibeach-notifier@.service
sudo systemctl status ibeach.service