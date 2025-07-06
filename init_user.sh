clear
python -m backend.scripts.init_users
echo "User initialization completed. You can now start the backend server."
echo "To start the backend server, run: uvicorn backSend.main:app --reload"