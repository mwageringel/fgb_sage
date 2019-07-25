#!/bin/bash
set -ev
# patch is needed for sage-apply-patches
sudo apt-get update && sudo apt-get install -y patch

cp -r $APP_DIR fgb_sage && cd fgb_sage && ls -la
sage --version

sage setup.py test
sage -pip install --upgrade --no-index -v --user .
