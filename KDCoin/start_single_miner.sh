#!/usr/bin/env bash

# start trusted server
python $PWD"/trustedServer.py" &

# start MinerApp
python $PWD"/minerApp.py" &
