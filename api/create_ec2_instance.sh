#!/bin/bash

# Get the instance name from the command-line argument
instance_name="$1"

# Create the instance with the specified name
aws ec2 run-instances --image-id ami-02961c77ad6fba369 --instance-type t2.micro --key-name backend_key --security-group-ids sg-0e736a527a444bf6b --subnet-id subnet-08cf40d9e368a3524 --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$instance_name}]" > /dev/null 2>&1

# Print a message to the console indicating that the instance creation has finished
echo "EC2 instance creation complete"
