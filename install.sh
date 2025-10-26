#!/bin/bash
# Installation script for the trading_ai_project

set -e # Exit immediately if a command exits with a non-zero status.

echo "Starting installation..."

# Install TA-Lib C library
echo "Installing TA-Lib C library..."
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
echo "TA-Lib C library installed successfully."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "Python dependencies installed successfully."

# Verify installation
echo "Verifying installation..."
python3 verify_install.py
echo "Installation verified successfully."
