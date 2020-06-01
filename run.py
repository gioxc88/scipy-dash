from app import app
server = app.server  # the Flask app
if __name__ == "__main__":
    app.run_server(debug=True)