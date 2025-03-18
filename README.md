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

![EC2 Setup Screenshot](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/299dc88284a851cd663b8dc34873f99a8bbac62c/images/ec2%20creation.jpg)

---

## 🔔 Step 2: Set Up an SNS Topic
1. Navigate to **SNS Dashboard** → Click **Create Topic**
2. Choose **Standard Topic**
3. Set **Topic Name**: `EC2-Reboot-Alerts`
4. Click **Create Topic**
5. Click **Create Subscription** → Configure:
   - **Protocol**: Lambda
   - **Endpoint**: Your Email-id and also (We will link the Lambda function later)
6. Click **Create Subscription**

![SNS topic and subscription creation](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/d6f354a3ca903b2411a53846060d4ad416f40336/images/1.jpg)
![SNS topic and subscription creation](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/d6f354a3ca903b2411a53846060d4ad416f40336/images/2.jpg)

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

![CloudWatch Alarm setup](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/d6f354a3ca903b2411a53846060d4ad416f40336/images/6.jpg)

![CloudWatch Alarm setup](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/d6f354a3ca903b2411a53846060d4ad416f40336/images/5.jpg)

---

## 🔑 Step 4: Create an IAM Role for Lambda
1. Navigate to **IAM Dashboard** → Click **Roles** → **Create Role**
2. Choose **Trusted Entity**: Lambda
3. Attach policies:
   - `AmazonEC2FullAccess`
   - `AWSLambdaBasicExecutionRole`
   - `AmazonSNSFullAccess`
   - `AmazonCloudWatchFullAccess`
   - `AmazonCloudWatchV2FullAccess`
       
4. **Role Name**: `Lambda-EC2-Reboot-Role`
5. Click **Create Role**

![IAM Role for Lambda](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/d6f354a3ca903b2411a53846060d4ad416f40336/images/policies.jpg)

---

## ⚡ Step 5: Create a Lambda Function
1. Navigate to **Lambda Dashboard** → Click **Create Function**
2. Choose **Author from Scratch**
3. Set:
   - **Function Name**: `EC2-Reboot-Function`
   - **Runtime**: Python 3.9
   - **IAM Role**: `Lambda-EC2-Reboot-Role`
4. Click **Create Function**

![Lambda Function](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/d6f354a3ca903b2411a53846060d4ad416f40336/images/3.jpg)

5. After creating the Lambda function, navigate to SNS Topics, create a new subscription in ITSM EC2-Reboot-Alerts, and set the endpoint as the Lambda ARN.

![SNS for Lambda](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/d6f354a3ca903b2411a53846060d4ad416f40336/images/sns%20lambda.jpg)


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

![Lambda layer](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/36f5e3385a33c7c6113b671522d8b87056b465ff/images/lambda%20layer.jpg)


---

## 🔁 Step 7: Configure Lambda Triggers from SNS
1. Open **Lambda Function** → Click **Add Trigger**
2. Select **SNS**
3. Choose **EC2-Reboot-Alerts** topic
4. Click **Add**

![Lambda Trigger](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/b63c3c075c97d1fe9d283f2655c6ba3ca3c54880/images/lambda%20sns%20trigger.jpg)


---

## 📝 Lambda Function Code


![Lambda function code](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/50282657d7f66a7a3b961e5362c8bfc79dbe5e6f/images/lambda%20function%20code.jpg)

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

![CloudWatch Alarm test](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/2b6351bf9390cfbb9c2ccdc4f83f2e9c5c5e785a/images/graph%20test.jpg)

![SNS Mail test](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/50282657d7f66a7a3b961e5362c8bfc79dbe5e6f/images/mail.jpg)


---

## ✅ Step 9: Verifying Execution
- **CloudWatch Logs**: Check if Lambda executed successfully
- **EC2 State Changes**: Verify instance restarted
- **Application Status**: Ensure Nginx is accessible

![CloudWatch Logs](https://github.com/Chinmaykota/Automating-EC2-Reboot-Using-CloudWatch-Alarms-SNS-and-Lambda-/blob/2b6351bf9390cfbb9c2ccdc4f83f2e9c5c5e785a/images/logs.jpg)


---

## 🧹 Step 10: Cleanup (Optional)
To remove all resources:
- **Delete** Lambda function
- **Delete** SNS topic
- **Delete** CloudWatch alarm
- **Terminate** EC2 instance


---

## 🎯 Conclusion
By following this guide, you can **automate EC2 instance reboot** based on **CloudWatch alarms**, ensuring **proactive monitoring and self-healing capabilities**. 🚀
