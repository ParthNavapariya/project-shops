import os
import sys
import glob
import site

# Automatically load local venv site-packages if running with system python
_VENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')
if os.path.exists(_VENV_PATH):
    for _sp in glob.glob(os.path.join(_VENV_PATH, 'lib', 'python*', 'site-packages')):
        if _sp not in sys.path:
            site.addsitedir(_sp)

from app import app
from models import db
from seed_data import seed_database

def initialize():
    with app.app_context():
        print(f"Connecting to database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        db.create_all()
        print("Database schema verified / created successfully!")
        seed_database()
        print("Database initialization and seeding completed!")

if __name__ == '__main__':
    initialize()
