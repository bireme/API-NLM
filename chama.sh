#!/bin/bash

NOW=$(date +"%Y%m%d")
HOME=/bases/api_nlm/app

cd $HOME/src

nohup python3 ProcessLog.py &> $HOME/nohup/${NOW}.out &

cd -
