#!/bin/bash

# Get instance name as parameter
INSTANCE_NAME=$1

# Get instance ID from the name
INSTANCE_ID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$INSTANCE_NAME" --query "Reservations[].Instances[].InstanceId" --output text)

# Terminate the instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
