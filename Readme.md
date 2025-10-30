# DVPN Control Panel

## Description

A web portal for a Decentralized VPN (DVPN) service. The application simplifies network participation by allowing users to create and join groups. Once in a group, the portal provides them with the necessary IP/configuration details to connect via their DVPN client, facilitating real-time peer-to-peer connections.

## Key Features

- **Real-time Peer API**: Uses Socket.IO to broadcast peer availability, IPs, and connection details to all members of a group as users come online or go offline. A REST-like endpoint is also available for polling peer lists.

- **Full CRUD Functionality**: Implemented complete Create, Read, Update, and Delete operations for managing user groups and their members (create, join, leave, delete group, remove member).

- **Brute-Force Attack Protection**: Integrated Django-Axes to automatically monitor and block suspicious login attempts, securing user accounts from brute-force attacks on the web interface.

- **ORM & Data Integrity**: Uses the built-in Django ORM to manage the database, ensuring data integrity for user-group relationships and IP assignments.

## Tech Stack

- **Backend**: Django, Python-Socket.IO
- **Async**: Eventlet
- **Security**: Django-Axes
- **Database**: SQLite (default), easily configurable for MariaDB/PostgreSQL
- **Frontend**: HTML, CSS, JavaScript (AJAX/Fetch)
- **Static Files**: Whitenoise

## Screenshots

*(Placeholder: Add your screenshots here)*

![Login Page](one.png)
![Dashboard](two.png)

## Installation & Setup

Follow these steps to get your local development environment running.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name/vpn_project
```

### 2. Create and Activate a Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install all required packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Configuration

You must configure the project by creating a `.env` file and editing `settings.py`.

#### A. Create `.env` File

In the `vpn_project` root directory (alongside `manage.py`), create a file named `.env`. This file is used to provide download links on the homepage.

Add the following variables, pointing to your client executable paths:

```env
# .env
WIN_MODULE_PATH=/path/to/your/module.exe
LINUX_MODULE_PATH=/path/to/your/module.bin
DVPN_ARM_LATEST_PATH=/path/to/dvpn-arm
DVPN_AMD_LATEST_PATH=/path/to/dvpn-amd
DVPN_UBUNTU_LATEST_PATH=/path/to/dvpn.deb
DVPN_WINDOWS_LATEST_PATH=/path/to/dvpn.exe
```

#### B. Edit `vpn_project/settings.py`

**⚠️ You must change these values for production:**

- **SECRET_KEY**: Replace `'Your-Secret-Key-Here'` with a new, randomly generated secret key
- **DEBUG**: Set to `False` for production. For development, you can set it to `True`
- **ALLOWED_HOSTS**: Add your domain or IP address  
  Example: `ALLOWED_HOSTS = ["dvpn.yuniversia.eu", "127.0.0.1"]`
- **CSRF_TRUSTED_ORIGINS**: Add your site's origin  
  Example: `CSRF_TRUSTED_ORIGINS = ['https://dvpn.yuniversia.eu']`
- **DATABASES** *(Optional)*: The default is SQLite. You can replace this with your production database (MariaDB, PostgreSQL, etc.)

### 5. Run Database Migrations

This will create the database tables for users, groups, and other models.

```bash
python manage.py migrate
```

### 6. Create a Superuser

This allows you to access the Django admin panel at `/admin/`.

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

This gathers all static files (CSS, JS) into one directory for Whitenoise to serve.

```bash
python manage.py collectstatic
```

## Running the Application

This project uses an ASGI setup to handle both standard Django requests and Socket.IO connections.

**⚠️ Do not use `python manage.py runserver` for development**, as it will not run the Socket.IO server.

Instead, use an ASGI server like `uvicorn`:

```bash
# Run the development server with auto-reload
uvicorn vpn_project.asgi:application --host 127.0.0.1 --port 8000 --reload
```

You can now access the application at **http://127.0.0.1:8000**

## Support

*(Add support/contact information here)*
