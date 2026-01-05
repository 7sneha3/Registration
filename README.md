# User Sign Up Application

A full-stack application with React frontend and Django backend for user registration with email confirmation.

## Features

- User registration form with validation
- Email confirmation sent upon successful registration
- MongoDB database (MySQL alternative available)
- Modern, responsive UI
- RESTful API

## Tech Stack

- **Frontend**: React 18
- **Backend**: Django 4.2 + Django REST Framework
- **Database**: MongoDB (default) or MySQL
- **Email**: SMTP (Gmail compatible)

## Project Structure

```
.
├── backend/                 # Django backend
│   ├── signup_project/     # Django project settings
│   ├── users/              # User app with signup API
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── App.js
│   ├── public/
│   └── package.json
└── README.md
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Create .env file (see env.example.txt)
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Configuration

Copy `backend/env.example.txt` to `backend/.env` and fill in your values:
- MongoDB connection string
- Email credentials (Gmail App Password)
- Django SECRET_KEY

## Deployment

See `DEPLOYMENT.md` for detailed deployment instructions.

## License

MIT

