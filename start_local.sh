#!/bin/bash
# Launch RabbitMQ server
echo "Starting RabbitMQ server...."
./start_rabbitmq.sh
sleep 5
# Launch redis
echo
echo "Starting Redis server...."
./start_redis.sh
sleep 5
echo
echo "Launch celery..."	
# launch celery 
./start_celery.sh
sleep 10
tail celery.log
# launch  gunicorn
echo
echo "launch gunicorn..."
./start_api.sh
sleep 5
tail gunicorn.err
#tail ~/gunicorn.log
# ngrok to expose ports
# remove old tunnel
#sudo -H -u protago bash -c "ps auxww | grep 'ngrok http 8000' | grep -v grep | awk '{print \$2}' | xargs kill -9"
#echo "Starting tunnel on port 8000...."
#sleep 2
#sudo -H -u protago bash -c 'nohup /home/protago/ngrok http 8000 --log=stdout > ~/ngrok.log &'
#sleep 2
#sudo -H -u protago bash -c "tail  ~/ngrok.log"

