# Script to initialise your instance
#!/bin/bash

# Authenticating yourself
gcloud auth login --no-launch-browser
gcloud auth application-default login --no-launch-browser

python3 -m pip install --upgrade pip

git config --global user.name "<user-name>"
git config --global user.email <user-email>