import os

# Get env Variables from the docker file for prod or dev.
# dotenv_path = Path(os.environ["ENV_FILE_PATH"])
# load_dotenv(dotenv_path=dotenv_path)

AUTH_STATUS_LINK = os.getenv("AUTH_STATUS_LINK", "DEFAULT_VALUE")

# STAGING CREDS
MONGO_DB_LINK = os.getenv("MONGO_DB_LINK", "DEFAULT_VALUE")
MONGO_TRANSACTIONAL_DB_LINK = os.getenv("MONGO_TRANSACTIONAL_DB_LINK", "DEFAULT_VALUE")

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "DEFAULT_VALUE")
SENDGRID_API_KEY = os.getenv("SENDGRID_CREDENTIAL", "DEFAULT_VALUE")