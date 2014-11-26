#!/bin/bash
export APP_PATH=/var/www/ci.posix.me
cd $APP_PATH
source $APP_PATH/.venv/bin/activate
$APP_PATH/.venv/bin/python $APP_PATH/run.py
