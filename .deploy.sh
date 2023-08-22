#!/bin/bash

# Update the system only if needed
if ! dpkg -l | grep -q apt; then
    apt-get update -y
fi

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev
fi

# Check if ffmpeg, libsm6, and libxext6 are installed
if ! command -v ffmpeg &> /dev/null; then
    apt-get install -y ffmpeg
fi

if ! dpkg -l | grep -q libsm6; then
    apt-get install -y libsm6
fi

if ! dpkg -l | grep -q libxext6; then
    apt-get install -y libxext6
fi

# Cleanup
apt-get clean 
apt-get autoremove

flask db upgrade

gunicorn main:application -b 0.0.0.0:8000
