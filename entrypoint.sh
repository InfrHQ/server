#!/bin/bash
export FLASK_APP=main.py
flask db migrate
flask db upgrade
flask user_blueprint create-owner
gunicorn main:application -b 0.0.0.0:8000