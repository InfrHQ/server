#!/bin/bash
export FLASK_APP=main.py
flask db upgrade
flask user_blueprint create-owner
gunicorn main:application -w 2 --threads 3 -b 0.0.0.0:8000