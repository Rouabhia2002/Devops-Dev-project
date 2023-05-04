#!/bin/bash

# Get the instance name from the command-line argument
instance_name="$1"

# Create the instance with the specified name
aws ec2 run-instances --image-id ami-05eb678ed1ab021c7 --instance-type t2.micro --key-name my-keypair --security-group-ids sg-070be575d7da48fdb --subnet-id subnet-0b8f061b6fb04d463 --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$instance_name}]"

# Print a message to the console indicating that the instance creation has finished
echo "EC2 instance creation complete"
