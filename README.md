# Kannada AI Helper

A chatbot app that answers in simple Kannada for people who don't know English,
with an English study-helper mode for students.

- `backend/` - FastAPI server that calls the Claude API
- `app/` - React Native (Expo) mobile app

## Run the backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then put your real key in .env
uvicorn main:app --reload --host 0.0.0.0
```

## Run the app
```bash
npx create-expo-app@latest kannada-app --template blank
# replace kannada-app/App.js with app/App.js from this repo
# set BACKEND_URL in App.js to your laptop's IP
cd kannada-app
npx expo start
```
Scan the QR code with the Expo Go app (phone and laptop on the same Wi-Fi).
