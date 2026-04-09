#!/bin/bash
PROJECT_DIR="/opt/claudio-bot"
REPO_DIR="$PROJECT_DIR/external-templates"
INDEX_FILE="$PROJECT_DIR/community_index.json"
LOG_FILE="$PROJECT_DIR/indexing.log"

cd $PROJECT_DIR
echo "Starting indexing at $(date)" > $LOG_FILE

# Ensure venv python is used
PYTHON="$PROJECT_DIR/venv/bin/python3"

$PYTHON index_community_workflows.py $REPO_DIR $INDEX_FILE >> $LOG_FILE 2>&1

echo "Finished indexing at $(date)" >> $LOG_FILE
