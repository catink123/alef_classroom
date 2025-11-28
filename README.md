# Alef Classroom

A modern educational platform for teachers and students built with Django and Material Design.

## Features

- User authentication and profiles
- Classroom management
- Assignment creation and submission
- Student progress tracking
- Responsive Material Design UI

## Prerequisites

- Python 3.13+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd alef-classroom
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
cd alef_classroom
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.prod` to `.env` and update with your settings:

```bash
cp .env.prod .env
```

Edit `.env` with your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=1  # Set to 0 for production
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database (SQLite - no additional configuration needed)
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create superuser (admin account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Collect static files (production only)

For production deployment:

```bash
python manage.py collectstatic --noinput --settings=core.settings_prod
```

### 8. Run the development server

```bash
python manage.py runserver 0.0.0.0:8000
```

The application will be available at `http://localhost:8000`

## Development vs Production

### Development Mode

Set `DEBUG=1` in `.env`:

```bash
python manage.py runserver 0.0.0.0:8000
```

### Production Mode

Set `DEBUG=0` in `.env` and use production settings:

```bash
export DJANGO_SETTINGS_MODULE=core.settings_prod
python manage.py runserver 0.0.0.0:8000
```

Or the `.env` file will automatically set this if `DJANGO_SETTINGS_MODULE=core.settings_prod` is configured.

For production with a proper WSGI server (recommended):

```bash
pip install gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --settings=core.settings_prod
```

## Project Structure

```
alef_classroom/
├── accounts/              # User authentication and profiles
├── assignment/            # Assignment management
├── classroom/             # Classroom management
├── core/                  # Django project settings
├── static/                # CSS, JavaScript, images
├── templates/             # HTML templates
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Management Commands

### Database Operations

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell
```

### Static Files

```bash
# Collect static files (production)
python manage.py collectstatic --noinput --settings=core.settings_prod
```

## Configuration

### Environment Variables

- `SECRET_KEY`: Django secret key (keep this secret in production)
- `DEBUG`: Set to 1 for development, 0 for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames
- `DJANGO_SETTINGS_MODULE`: Settings module to use (auto-loaded from .env)

### Database

The application uses SQLite by default. The database file is stored at `alef_classroom/db.sqlite3`.

### Static Files

- Development: Served automatically by Django
- Production: Use WhiteNoise middleware or configure a web server (nginx/Apache)

## Security Considerations

1. **Secret Key**: Generate a strong secret key for production
2. **Debug Mode**: Always set `DEBUG=0` in production
3. **ALLOWED_HOSTS**: Configure proper hostnames for your domain
4. **HTTPS**: Use HTTPS in production (configure in web server)
5. **Environment Variables**: Never commit `.env` files to version control

## Cleaning Up

### Clear Python cache

```bash
# Remove all __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} +

# Remove all .pyc files
find . -type f -name "*.pyc" -delete
```

### Clear media files

```bash
# Remove all uploaded media
rm -rf alef_classroom/media/*
```

### Clear logs

```bash
# Remove all log files
rm -rf alef_classroom/logs/*
```

### Clear collected static files

```bash
# Remove collected static files (will be regenerated on next collectstatic)
rm -rf alef_classroom/staticfiles/*
```

### Reset database (delete all data)

```bash
# Delete the database file
rm alef_classroom/db.sqlite3

# Run migrations to recreate the schema
python manage.py migrate

# Create a new superuser
python manage.py createsuperuser
```

### Full cleanup (everything above)

```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf alef_classroom/media/*
rm -rf alef_classroom/logs/*
rm -rf alef_classroom/staticfiles/*
rm alef_classroom/db.sqlite3
python manage.py migrate
python manage.py collectstatic --noinput --settings=core.settings_prod
python manage.py createsuperuser
```

## Troubleshooting

### Static files not loading

1. Ensure you've run `collectstatic` for production
2. Check that `STATIC_URL` and `STATIC_ROOT` are configured correctly
3. Verify file permissions on static files directory

### Database errors

1. Ensure migrations are up to date: `python manage.py migrate`
2. Check database file permissions
3. Verify database file location in settings

### Port already in use

If port 8000 is already in use, specify a different port:

```bash
python manage.py runserver 0.0.0.0:8001
```

## Support

For issues and questions, check the logs and review this documentation.

## License

[Add your license here]
