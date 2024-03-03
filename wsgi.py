from main import main

if __name__ == "__main__":
    main.run(debug=True)
else:
    from gunicorn.app.wsgiapp import run
    run()