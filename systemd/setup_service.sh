#!/bin/bash
SYSD_PATH=/etc/systemd/system/
sudo cp notify@.service $SYSD_PATH
sudo cp ibeach.service $SYSD_PATH
sudo systemctl daemon-reload

sudo systemctl start ibeach.service
sudo systemctl status ibeach.service