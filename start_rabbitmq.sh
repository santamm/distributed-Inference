#!/bin/bash
# Launch RabbitMQ server
rabbitmqctl shutdown
sleep 1  
rabbitmq-server &