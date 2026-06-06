# 🌟 She Can Foundation - Web Application

A modern Flask-based CRUD application for **She Can Foundation**, an NGO dedicated to empowering women and creating opportunities for those from underprivileged communities.

**Live Demo:** [https://she-can-foundation-1g33.onrender.com](https://she-can-foundation-1g33.onrender.com)

## 🎯 About She Can Foundation

She Can Foundation is a registered NGO (under Indian Society Act 1860) committed to:

- **Empowering Women** - Providing education, training, and skill development
- **Gender Equality** - Breaking barriers and creating equitable opportunities
- **Community Support** - Offering healthcare, crisis support, and economic development
- **Social Impact** - Collaborating with organizations to create sustainable change

> *Transforming lives one woman at a time* 💪

## ✨ Features

### 📱 Public Platform
- **Home Page** - Welcome and mission overview
- **About Section** - Learn about our foundation's work
- **Certification Program** - Showcase completed certificates
- **Donation Portal** - Easy ways to contribute and support our cause

### 🔐 User System
- Secure signup and login with **hashed password encryption**
- Account authentication and session management
- Logout functionality with session cleanup

### 🛠️ Admin Dashboard
- Comprehensive admin panel for program management
- **Create** new foundation programs
- **Read** program details and statistics
- **Update** existing programs and information
- **Delete** outdated or inactive programs
- User management and role assignment

### 💾 Database
- Local **SQLite** development database
- Production-ready **PostgreSQL** on Render
- Automatic schema management

## 📁 Project Structure

```
she_can_foundation/
├── app.py              # Main Flask application & route registration
├── config.py           # Environment & configuration settings
├── extensions.py       # Database initialization & helpers
├── models.py           # Database schema & ORM models
├── routes.py           # Public, auth, dashboard & admin routes
├── validators.py       # Form validation logic
├── requirements.txt    # Python dependencies
└── templates/          # HTML templates (public & admin)
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/praaannnav-star/she_can_foundation.git
cd she_can_foundation

# Install dependencies
python -m pip install -r requirements.txt
```

### Run Locally

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Set Up Admin Account

**Option 1: Create via Web Interface**
- Sign up for a new account on the website
- The first account created automatically becomes the admin

**Option 2: Create via CLI**
```bash
# For Windows PowerShell
$env:DATABASE_URL=""
flask --app app create-admin

# For Linux/Mac
export DATABASE_URL=""
flask --app app create-admin
```

## 🗄️ Database Configuration

### Development (SQLite)
By default, the app uses SQLite for local development.

### Production (PostgreSQL)
Set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/she_can_foundation"
```

## 📦 Dependencies

Key packages used:
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM for database operations
- **Werkzeug** - Password hashing and security utilities
- **Python-dotenv** - Environment variable management

See `requirements.txt` for complete list.

## 🔒 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Session-based authentication
- ✅ Admin role-based access control
- ✅ Form validation on both client and server side
- ✅ CSRF protection

## 📝 Routes Overview

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Homepage |
| `/about` | GET | About page |
| `/certificate` | GET | Certificates |
| `/donate` | GET | Donation page |
| `/signup` | GET, POST | User registration |
| `/login` | GET, POST | User authentication |
| `/logout` | POST | End session |
| `/dashboard` | GET | User dashboard |
| `/admin` | GET | Admin panel |
| `/admin/programs` | GET, POST | Manage programs |

