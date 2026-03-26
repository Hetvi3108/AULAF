# AULAF

# AU Lost & Found Management System

## Project Overview

The **AU Lost & Found Management System** is a web-based application designed to help students and staff at Ahmedabad University report, search, and recover lost items efficiently. The system provides a centralized platform to manage lost and found items with proper tracking and verification.


## 🎯 Features

* 🔐 User Registration (AU email only)
* 🔑 Login & Logout system
* 📸 Report Found Items with image upload
* 📋 View Lost & Found Items
* 📍 Select submission type (Desk / Finder)
* 📦 Track item status (Collected / Not Collected)
* 🧑‍💼 Admin and Staff management
* ⚠️ Complaint handling system (future scope)
* 💬 Chat with finder (future scope)

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Django (Python)
* **Database:** SQLite
* **Tools:** VS Code, Figma (for UI design)

---

## 🗂️ Project Structure

```
au_lostfound/
│
├── manage.py
├── db.sqlite3
├── items/                # Main app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│
├── au_lostfound/         # Project settings
│   ├── settings.py
│   ├── urls.py
│
├── media/                # Uploaded images
└── static/               # CSS & JS files
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```
git clone <your-repo-link>
```

### 2. Navigate to project

```
cd au_lostfound
```

### 3. Create virtual environment

```
python -m venv .venv
```

### 4. Activate virtual environment

```
.venv\Scripts\activate
```

### 5. Install dependencies

```
pip install django pillow
```

### 6. Run migrations

```
python manage.py migrate
```

### 7. Run the server

```
python manage.py runserver
```

### 8. Open in browser

```
http://127.0.0.1:8000
```

---

## 👤 User Roles

### 🎓 Student

* Register/Login
* Report found items
* View items
* Claim items (future)

### 🧑‍💼 Staff

* Manage desk submissions
* Update item status

### 🛠️ Admin

* Manage users
* Verify claims
* Handle complaints

---

## 📊 System Modules

* Authentication Module
* Item Management Module
* User Management Module
* Database Module

---

## 🔮 Future Scope

* 🤖 AI-based item matching
* 📱 Mobile application
* 🔔 Real-time notifications
* 🎤 Voice/chat interaction
* 🔗 Integration with university database

---

## 📷 Screens / UI

* Login Page
* Dashboard
* Report Item Page
* Profile Page

---

## 👨‍💻 Contributors

* Hetvi Shah
* (Add your teammates)

---

## 📄 License

This project is developed for academic purposes.

---

## ⭐ Notes

* Only **@ahduni.edu.in** emails are allowed for registration
* Images are stored in the `media/` folder
* Django admin panel available at `/admin`

---


