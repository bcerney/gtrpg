#!/usr/bin/env bash

set -x

export FLASK_APP=py-flask-gtrpg.py

docker build -t gtrpg:latest .

docker run -it --net host gtrpg:latest bash