from app import app

if __name__ == "__main__":
    from gunicorn import app as application
    application.run(debug=True)