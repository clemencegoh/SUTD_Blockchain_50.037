#!/usr/bin/env bash

# start trusted server
python $PWD"/trustedServer.py" &

# start MinerApp
python $PWD"/minerApp.py" &

# start MinerApp2
python $PWD"/minerApp2.py"

# start SPVclientApp
#python $PWD"/SPVApp.py"