#!/bin/bash
python src/api.py > /dev/null 2>&1 &
sleep 2
python src/server.py