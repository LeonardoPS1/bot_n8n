#!/bin/bash
PROJECT_DIR="/opt/claudio-bot"
REPO_DIR="$PROJECT_DIR/external-templates"
INDEX_FILE="$PROJECT_DIR/community_index.json"
LOG_FILE="$PROJECT_DIR/indexing.log"

echo "Cleanup old repo at $(date)" > $LOG_FILE
rm -rf $REPO_DIR

echo "Cloning repo (no-checkout)..." >> $LOG_FILE
git clone --no-checkout --depth 1 https://github.com/nusquama/n8nworkflows.xyz.git $REPO_DIR >> $LOG_FILE 2>&1

cd $REPO_DIR
echo "Configuring sparse-checkout..." >> $LOG_FILE
git sparse-checkout init --cone >> $LOG_FILE 2>&1
# We want metadata.json and workflow.json in every folder under workflows/
git sparse-checkout set workflows >> $LOG_FILE 2>&1

echo "Performing checkout..." >> $LOG_FILE
git checkout >> $LOG_FILE 2>&1

echo "Checking if files exist..." >> $LOG_FILE
# Find some workflow.json files to confirm
find workflows -name "workflow.json" | head -n 10 >> $LOG_FILE

echo "Running indexing script..." >> $LOG_FILE
cd $PROJECT_DIR
$PROJECT_DIR/venv/bin/python3 index_community_workflows.py $REPO_DIR $INDEX_FILE >> $LOG_FILE 2>&1

echo "Finished at $(date)" >> $LOG_FILE
