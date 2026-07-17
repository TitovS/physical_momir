#!/bin/bash

# Install script for Physical Momir on Raspberry Pi

# Copy service file to systemd
sudo cp momir.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable momir.service

# Start the service
sudo systemctl start momir.service

echo "Installation complete!"
echo "To check status: sudo systemctl status momir.service"
echo "To view logs: sudo journalctl -u momir.service -f"
