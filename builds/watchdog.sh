#!/bin/bash
# Watchdog for WebPilot and EvalHub backends
# Checks every 60 seconds, restarts if down

while true; do
  # WebPilot (8901)
  if ! curl -s -o /dev/null -w "" --max-time 5 http://localhost:8901/api/pages 2>/dev/null; then
    echo "[$(date)] WebPilot down, restarting..."
    cd /root/clawd/builds/webpilot/backend && nohup python main.py > /tmp/webpilot.log 2>&1 &
    sleep 3
  fi

  # EvalHub (8900)
  if ! curl -s -o /dev/null -w "" --max-time 5 http://localhost:8900/api/datasets 2>/dev/null; then
    echo "[$(date)] EvalHub down, restarting..."
    cd /root/clawd/builds/evalhub/backend && nohup python main.py > /tmp/evalhub.log 2>&1 &
    sleep 3
  fi

  sleep 60
done
