#!/bin/bash
# Launch redis
redis-cli shutdown
sleep 1
redis-server &