#!/bin/bash
# Launch RabbitMQ server
rabbitmqctl shutdown
sleep 1  
rabbitmq-server &

# Inspecting queues
rabbitmqctl list_queues name messages messages_ready messages_unacknowledged

# Finding the number of workers currently consuming from a queue:
rabbitmqctl list_queues name consumers