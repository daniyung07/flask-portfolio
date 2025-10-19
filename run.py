# run.py

from app import create_app
# Also import db for database initialization commands
from app import db

# 1. Create the application instance
app = create_app()

# You still need this to run the application!
if __name__ == '__main__':
    # You may need to run db.create_all() inside app context once more if you moved the models
    with app.app_context():
        db.create_all()
    app.run(debug=False)