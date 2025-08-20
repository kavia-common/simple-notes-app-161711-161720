#!/bin/bash
cd /home/kavia/workspace/code-generation/simple-notes-app-161711-161720/backend_django
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

