#!/bin/bash
# Specify the user's home directory
USER_HOME=${USER_HOME:-"/home/pi"}
# Specify the name of your git project folder
PROJECT_FOLDER=${PROJECT_FOLDER:-"security-camera-privacy-mask"}
# Specify the name of your virtual environment
VENV=${PROJECT_FOLDER:-".venv"}

# Change to the user's home directory + project directory
cd $USER_HOME/$PROJECT_FOLDER || exit

# Step 1: Perform a git pull
git pull origin master
PULL_EXIT_CODE=$?

# Check if new files were pulled
if [ $PULL_EXIT_CODE -eq 0 ]; then
  echo "Successfully pulled new files."
  # Activate the virtual environment
  source $VENV/bin/activate
  # Step 2: Run pip install
  pip install -r requirements.txt
  # Step 3: Restart a systemd service
  sudo systemctl restart $PROJECT_FOLDER.service
  # deactivate venv
  deactivate
else
  echo "No new files pulled."
fi
