#!/bin/bash
# Specify the user's home directory
USER_HOME=${USER_HOME:-"/home/$USER"}
# Specify the name of your git project folder
PROJECT_FOLDER=${PROJECT_FOLDER:-"security-camera-privacy-mask"}
# Specify the name of your virtual environment
VENV=${VENV:-".venv"}

# Change to the user's home directory + project directory
cd $USER_HOME/$PROJECT_FOLDER || exit

# Step 1: Perform a git pull
old_head=$(git rev-parse HEAD)
git pull origin master
new_head=$(git rev-parse HEAD)

# Check if new files were pulled
if [[ $old_head != $new_head ]]; then
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
