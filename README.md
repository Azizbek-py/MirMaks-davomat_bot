# Davomat Bot

Telegram Bot for employee attendance management.

## Features
- Employee management (add/edit/delete)
- Attendance tracking
- Admin commands
- Database integration with TinyDB

## Setup
1. Copy `.env` file from `../Server/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Commands
- `/start` - Start bot
- `/add_employee` - Add new employee (admin only)
- `/list_employees` - List all employees (admin only)
- `/edit_employee` - Edit employee (admin only)
- `/delete_employee` - Delete employee (admin only)

## Deployment
Deploy to:
- Heroku
- Railway
- DigitalOcean
- Any VPS with Python support