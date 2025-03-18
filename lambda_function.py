import boto3
import os
import time
import requests  # Required for application health check

# AWS Clients
ec2 = boto3.client('ec2')
sns = boto3.client('sns')

# Environment Variables
INSTANCE_ID = os.getenv('INSTANCE_ID')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')  # SNS topic for alerts
APP_URL = os.getenv('APP_URL')  # Application URL to check

def get_instance_state(instance_id):
    """Check the current state of the EC2 instance."""
    try:
        response = ec2.describe_instance_status(InstanceIds=[instance_id])
        for status in response.get('InstanceStatuses', []):
            return status['InstanceState']['Name']
        return "unknown"
    except Exception as e:
        print(f"Error getting instance status: {e}")
        return "error"

def send_sns_notification(subject, message):
    """Send an SNS notification."""
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"SNS Notification Sent: {subject}")
    except Exception as e:
        print(f"Error sending SNS notification: {e}")

def reboot_ec2_instance(instance_id):
    """Reboot the EC2 instance."""
    try:
        ec2.reboot_instances(InstanceIds=[instance_id])
        print(f"Reboot command sent to EC2 instance: {instance_id}")
        return True
    except Exception as e:
        print(f"Error sending reboot command: {e}")
        return False

def check_application_status(url):
    """Check if the application (Nginx) is running by sending an HTTP request."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"Application is running. Status Code: {response.status_code}")
            return True
        else:
            print(f"Application check failed. Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error checking application status: {e}")
        return False

def lambda_handler(event, context):
    try:
        print("Received Event:", event)

        if not INSTANCE_ID or not SNS_TOPIC_ARN or not APP_URL:
            return {
                'statusCode': 400,
                'body': 'Error: Missing environment variables (INSTANCE_ID, SNS_TOPIC_ARN, APP_URL)'
            }

        # Extract CloudWatch Alarm name
        alarm_name = event.get('alarmName', 'Unknown')
        print(f"Triggered by CloudWatch Alarm: {alarm_name}")

        metric_type = "CPU Utilization" if "CPU" in alarm_name else "Memory Utilization"

        # Step 1: Get instance current state before reboot
        initial_state = get_instance_state(INSTANCE_ID)
        print(f"Instance {INSTANCE_ID} current state before reboot: {initial_state}")

        if initial_state not in ["running", "pending"]:
            return {
                'statusCode': 400,
                'body': 'Error: Instance is not in a rebootable state'
            }

        # Step 2: Reboot the EC2 instance
        if not reboot_ec2_instance(INSTANCE_ID):
            send_sns_notification(f"ITSM EC2 Reboot Failed - {metric_type}",
                                  f"Failed to reboot instance {INSTANCE_ID}. Immediate manual intervention required.")
            return {
                'statusCode': 500,
                'body': 'Error: Failed to send reboot command'
            }

        # Step 3: Wait for the instance to come back online
        print("Waiting for instance to come back online...")
        reboot_success = False

        for attempt in range(12):  # Retry for up to 60 seconds (12 retries * 5s wait)
            time.sleep(5)
            current_state = get_instance_state(INSTANCE_ID)
            print(f"Attempt {attempt + 1}: Current instance state: {current_state}")

            if current_state == "running":
                reboot_success = True
                break

        if not reboot_success:
            send_sns_notification(f"ITSM EC2 Restart Failed - {metric_type}",
                                  f"Instance {INSTANCE_ID} failed to reboot. Manual restart required.")
            return {
                'statusCode': 500,
                'body': 'Error: Instance did not restart'
            }

        # Step 4: Wait for services to start, then check if the application is running
        print("Waiting 30 seconds for the application to start...")
        time.sleep(30)

        if check_application_status(APP_URL):
            print(f"Instance {INSTANCE_ID} rebooted successfully and application is running.")
            return {
                'statusCode': 200,
                'body': 'EC2 reboot successful and application is running'
            }
        else:
            send_sns_notification(f"ITSM EC2 Application Down - {metric_type}",
                                  f"Instance {INSTANCE_ID} rebooted but application is NOT running. Immediate action required.")
            return {
                'statusCode': 500,
                'body': 'Error: Application is not running after reboot'
            }

    except Exception as e:
        send_sns_notification("ITSM EC2 Restart Failed - Urgent Attention Needed",
                              f"Unexpected error in Lambda function: {str(e)}. Manual intervention required.")
        return {
            'statusCode': 500,
            'body': f'Unexpected Error: {str(e)}'
        }
