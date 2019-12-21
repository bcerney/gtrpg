#!/usr/bin/env bash

set -x

export FLASK_APP=gtrpg.py

docker build -t gtrpg:latest -f app/Dockerfile .

docker run -it --net host gtrpg:latest bash