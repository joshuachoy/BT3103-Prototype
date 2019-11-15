# Project name: Panduh by Team Pikachu (BT3103)
Description: A free and comprehensive platform to learn Python’s Pandas library through real-word business problems faced by a multitude of industries. 

1. [ AWS S3 Set-up. ](#s3)
2. [ AWS IAM Set-up. ](#iam)
3. [ AWS Lambda Set-up. ](#lambda)

<a name="s3"></a>
## 1. AWS S3 Set-up --> Store html, javascript, css, data and pandas library file
#### Go to S3 services.
a. Create a bucket of a particular region (remember this region as you will need it later).</br>
b. Go to "Permissions" of this bucket:</br>
&nbsp;&nbsp;&nbsp;&nbsp; i. Ensure that all checkboxes are "off" in "Block public access". </br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Ensure that you have the following code in "Bucket policy". Please replace *yourBucketName* with the current bucket name. </br>
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::yourBucketName/*"
        }
    ]
}
```
c. Upload pandas_xlrd_3.7.zip (can be found in repo) into current bucket. </br>
d. After uploading, click onto the file and copy the *Object URL*. </br>

<a name="iam"></a>
## 2. AWS IAM Set-up.
#### Go to IAM services.
a. Go to "Policies":</br>
&nbsp;&nbsp;&nbsp;&nbsp; i. Create policy. </br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Choose S3 services and select *all S3 actions* and *all resources*. </br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Choose DynamoDB services and select *all actions* and *all resources*. </br>
&nbsp;&nbsp;&nbsp;&nbsp; iv. Choose CloudWatch Log services and select *all actions* and *all resources*. </br>
&nbsp;&nbsp;&nbsp;&nbsp; v. Give your policy a name, then create policy. </br>
b. Go to "Roles":</br>
&nbsp;&nbsp;&nbsp;&nbsp; i. Select type of trusted entity: AWS service </br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Select service: Lambda </br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Click on "Next: Permissions". </br>
&nbsp;&nbsp;&nbsp;&nbsp; iv. Select the policy that was created earlier. </br>
&nbsp;&nbsp;&nbsp;&nbsp; v. Proceed on to create role. </br>

<a name="lambda"></a>
## 3. AWS Lambda Set-up.
#### Go to lambda services and ensure that you are in the same region as before.
a. Create function:</br>
&nbsp;&nbsp;&nbsp;&nbsp; i. Give your lambda function a name. </br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Runtime: Python3.7 </br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Execution role -> Use an existing role -> Select the one you have created earlier. </br>
&nbsp;&nbsp;&nbsp;&nbsp; iv. Add trigger -> API Gateway -> Create a new API -> Security: "Open" </br>
&nbsp;&nbsp;&nbsp;&nbsp; v. Click "Layers" -> Add a layer -> Give your layer a name. -> Upload a file from Amazon S3. -> Paste the link that was copied in Step 1. -> Runtime: Python3.7 -> Add layer to lambda function. </br>
b. Go to "Basic settings" and set 5min as Timeout.</br>
c. You can now use the following code to import pandas. </br>
```
import pandas as pd
```
