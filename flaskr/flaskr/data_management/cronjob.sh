#! /bin/bash
cd ~/public_html/brdo
. venv/bin/activate
cd flaskr/data_management

python daily_job.py