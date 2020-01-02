# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'postgresql://jlu@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Use a secure, unique and absolutely secret key for signing the data
CSRF_SESSION_KEY = "secret"
