from app import create_app, db
from app.models.user import User


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
