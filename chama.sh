#!/bin/bash

NOW=$(date +"%Y%m%d")
HOME=/bases/api-nlm/app

nohup python3 $HOME/ProcessLog.py &> ${NOW}.out &
