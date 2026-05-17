#!/bin/bash

start=${1:-0}
interval=${2:-2}
sudo python3 clevo_backlight.py off

for (( i=start; i<$start+10; i++ )); do
  echo "idx $i"
  sudo python3 clevo_backlight.py key "$i" 255 0 0
  sleep $interval
done

