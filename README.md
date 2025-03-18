# Automating EC2 Reboot Using CloudWatch Alarms, SNS, and Lambda

## 📌 Introduction
This guide explains how to automatically reboot an EC2 instance when a CloudWatch alarm is triggered. The alarm sends notifications to an SNS topic, which then triggers a Lambda function to reboot the instance and check if the application (Nginx) is running.

---

## 🔧 Prerequisites
- **AWS Account** with necessary permissions
- **EC2 instance** (Amazon Linux 2)
- **IAM permissions** to manage EC2, SNS, CloudWatch, and Lambda
- **Python 3.9+ installed locally** for Lambda Layer packaging (if using requests module)

---

## 🛠 Step 1: Create an EC2 Instance
1. Log in to **AWS Management Console**
2. Navigate to **EC2 Dashboard** → Click **Launch Instance**
3. Configure as follows:
   - **AMI**: Amazon Linux 2
   - **Instance Type**: t2.micro (Free Tier Eligible)
   - **IAM Role**: Assign an appropriate role (we will create one later)
   - **Enable Public IP** if needed
4. Click **Launch**

📸 *Insert screenshot of EC2 instance creation here*

---

## 🔔 Step 2: Set Up an SNS Topic
1. Navigate to **SNS Dashboard** → Click **Create Topic**
2. Choose **Standard Topic**
3. Set **Topic Name**: `EC2-Reboot-Alerts`
4. Click **Create Topic**
5. Click **Create Subscription** → Configure:
   - **Protocol**: Lambda
   - **Endpoint**: (We will link the Lambda function later)
6. Click **Create Subscription**

📸 *Insert screenshot of SNS topic and subscription creation here*

---

## ⏰ Step 3: Create a CloudWatch Alarm
1. Navigate to **CloudWatch Dashboard** → Click **Alarms** → **Create Alarm**
2. **Select EC2 Metrics** → Choose your EC2 instance
3. Choose **CPUUtilization**
4. Set conditions:
   - **Threshold Type**: Static
   - **Threshold**: Greater than 80% for 5 minutes
5. **Set Actions** → Choose **SNS Topic** → Select `EC2-Reboot-Alerts`
6. Click **Create Alarm**

📸 *Insert screenshot of CloudWatch Alarm setup here*

---

## 🔑 Step 4: Create an IAM Role for Lambda
1. Navigate to **IAM Dashboard** → Click **Roles** → **Create Role**
2. Choose **Trusted Entity**: Lambda
3. Attach policies:
   - `AmazonEC2FullAccess`
   - `AWSLambdaBasicExecutionRole`
   - `AmazonSNSFullAccess`
4. **Role Name**: `Lambda-EC2-Reboot-Role`
5. Click **Create Role**

📸 *Insert screenshot of IAM Role creation here*

---

## ⚡ Step 5: Create a Lambda Function
1. Navigate to **Lambda Dashboard** → Click **Create Function**
2. Choose **Author from Scratch**
3. Set:
   - **Function Name**: `EC2-Reboot-Function`
   - **Runtime**: Python 3.9
   - **IAM Role**: `Lambda-EC2-Reboot-Role`
4. Click **Create Function**

📸 *Insert screenshot of Lambda function creation here*

---

## 📂 Step 6: Add Lambda Layers (If Using Requests Module)
1. Open **Terminal/PowerShell** → Run:
   ```sh
   mkdir requests-layer && cd requests-layer
   mkdir python
   pip install requests -t python/
   zip -r layer.zip python/
   ```
2. Go to **Lambda Console** → Click **Layers** → **Create Layer**
3. Upload `layer.zip` and click **Create**
4. Add this layer to your Lambda function

📸 *Insert screenshot of Lambda Layer addition here*

---

## 🔁 Step 7: Configure Lambda Triggers from SNS
1. Open **Lambda Function** → Click **Add Trigger**
2. Select **SNS**
3. Choose **EC2-Reboot-Alerts** topic
4. Click **Add**

📸 *Insert screenshot of Lambda trigger configuration here*

---

## 📝 Lambda Function Code
```python
import boto3
import os
import time
import requests

ec2 = boto3.client('ec2')
sns = boto3.client('sns')

INSTANCE_ID = os.getenv('INSTANCE_ID')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
APP_URL = os.getenv('APP_URL')

def get_instance_state(instance_id):
    response = ec2.describe_instance_status(InstanceIds=[instance_id])
    for status in response.get('InstanceStatuses', []):
        return status['InstanceState']['Name']
    return "unknown"

def reboot_ec2_instance(instance_id):
    ec2.reboot_instances(InstanceIds=[instance_id])
    return True

def lambda_handler(event, context):
    if get_instance_state(INSTANCE_ID) == "running":
        reboot_ec2_instance(INSTANCE_ID)
        return {'statusCode': 200, 'body': 'Reboot triggered successfully'}
    return {'statusCode': 400, 'body': 'Instance not in running state'}
```
📸 *Insert screenshot of Lambda function code here*

---

## 🛠 Step 8: Testing the Setup
1. Simulate high CPU usage:
   ```sh
   stress --cpu 2 --timeout 300
   ```
2. Check CloudWatch **Alarms**
3. Verify **SNS notifications**
4. Check **Lambda execution logs**
5. Validate **EC2 reboot**

📸 *Insert screenshots of testing here*

---

## ✅ Step 9: Verifying Execution
- **CloudWatch Logs**: Check if Lambda executed successfully
- **EC2 State Changes**: Verify instance restarted
- **Application Status**: Ensure Nginx is accessible

📸 *Insert screenshot of verification here*

---

## 🧹 Step 10: Cleanup (Optional)
To remove all resources:
- **Delete** Lambda function
- **Delete** SNS topic
- **Delete** CloudWatch alarm
- **Terminate** EC2 instance

📸 *Insert screenshot of cleanup steps here*

---

## 🎯 Conclusion
By following this guide, you can **automate EC2 instance reboot** based on **CloudWatch alarms**, ensuring **proactive monitoring and self-healing capabilities**. 🚀
