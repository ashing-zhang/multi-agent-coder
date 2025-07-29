@echo off

cd backend
pip install -r requirements.txt
cd ..

python test_workflow.py

pause