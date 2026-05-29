#!/bin/bash
# This script runs automatically when LocalStack is ready
# It creates the SQS queue that our services expect

echo "Creating SQS queues..."
awslocal sqs create-queue --queue-name click-events
echo "Queue created: click-events"
