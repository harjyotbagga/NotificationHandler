#!/bin/bash

echo "activating virtual environment...."
source venv/bin/activate
echo "virtual env ready!"
echo "starting uvicorn server...."
export ENV_FILE_PATH="./.env.dev"
uvicorn app.main:app --reload