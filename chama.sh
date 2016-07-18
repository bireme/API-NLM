#!/bin/bash

NOW=$(date +"%Y%m%d")
HOME=/bases/api-nlm/app

cd $HOME/src

nohup python3 ProcessLog.py &> $HOME/nohup/${NOW}.out &

cd -
