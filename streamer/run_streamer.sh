#!/bin/bash

screen -S gatd-streamer-socketio -d -m forever streamer_socketio.js
screen -S gatd-streamer-tcp -d -m ./streamer_tcp.py
screen -S gatd-streamer-socketio-py -d -m ./streamer_socketio.py
screen -S gatd-streamer-socketio-py-hist -d -m ./streamer_socketio_historical.py
screen -S gatd-streamer-socketio-py-replay -d -m ./streamer_socketio_replay.py
