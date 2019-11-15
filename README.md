# Project name: Panduh by Team Pikachu (BT3103)
Description: A free and comprehensive platform to learn Python’s Pandas library through real-word business problems faced by a multitude of industries. 

Below are some steps to take in order to deploy our website. 
- Note that Steps 1 to 3 are to be completed before forking our project from Github.
- Note that you would need to activate your GitHub Actions prior to forking. This would ensure the correct setup in AWS environment. 


1. [ AWS S3 Set-up. ](#s3)
2. [ AWS IAM Set-up. ](#iam)
3. [ AWS Lambda Set-up. ](#lambda)
4. [ Edit template.yaml file from GitHub. ](#yaml) 
5. [Upload all files onto S3 Bucket.](#updateFiles)
6. [Update links on Lambda function.](#updateLinks)
7. [Making Changes to .HTML File.](#changesHTML)
8. [Making Changes to lambda_function.py File.](#changesLambda)

# Setting Up 
<a name="s3"></a>
## 1. AWS S3 Set-up.
**To store files needed -> .html .css .js & data csv file & pandas library** 
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
**Policy will be used to form connection between different AWS services**
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
<a name="yaml"></a>
## 4. Edit template.yaml file from Github
Lines 21-29
<pre>Resources:
  <b>PandaFunction</b>:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: industries/lambda_functions
      Handler: lambda_function.lambda_handler
      Runtime: python3.7
      Layers: 
        - arn:aws:lambda:us-east-1:<b>895200778545</b>:layer:<b>pandas_layer</b>:<b>1</b>      
</pre>
a. Change from: <b>PandaFunction</b> to the name of your own AWS Lambda Function</br>
b. Change from: <b>895200778545</b> to the user's AWS Account No.</br>
c. Change from: <b>pandas_layer</b> to the name of the created AWS Lambda Layer</br>
d. Change from: <b>1</b> to the version number of the created AWS Lambda Layer</br>

<a name="uploadFiles"></a>
## 5. Upload all files onto S3 Bucket
a. After forking the repo and editing template.yaml, upload all files onto S3 Bucket created previously</br>
&nbsp;&nbsp;&nbsp;&nbsp; i. Head to the S3 Bucket created previously</br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Click on *Upload*</br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Select all the files that are present on this GitHub page </br>

b. On S3 Bucket, change ALL files to allow Public access (Note: using Change All button may not be accurate)</br>
&nbsp;&nbsp;&nbsp;&nbsp; i. Click on an uploaded file that is listed on the S3 Bucket </br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Click on *Actions* -> *Make public* </br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Repeat the steps i and ii for all other files</br>


<a name="updateLinks"></a>
## 6. Update links on Lambda function 
a. Head back to the lambda function created previously
b. At line 28, replace *mylambdajosh* with the name of your S3 bucket created previously
```
obj = s3.get_object(Bucket = '<your bucket name>', Key = "short_data.csv")
```
c. At line 261, replace "mylambdajosh" with the name of your S3 bucket created previously as well
```
file_obj = s3.get_object(Bucket = '<your bucket name>', Key = "project-stock.html")
```

# Making Changes to Files
<a name="changesHTML"></a>
## 1. Making Changes to .HTML File
### 1.1 Re-upload the new .html file onto S3 Bucket
&nbsp;&nbsp;&nbsp;&nbsp; i. Head to S3 Bucket created previously </br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Click on *Upload*</br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Choose your newly updated .html file to upload it</br>

### 1.2 Making .html file publically accessible
&nbsp;&nbsp;&nbsp;&nbsp; i. Click on the file that is now listed on the S3 Bucket </br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. Click on *Actions*</br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Under *Actions* click on *Make public*</br>

### 1.3 Updating links on all other .html files
a. After uploading the edited .html file onto S3 Bucket, you would now need to change the links in all other .html files that are referencing to this newly edited .html file</br>
b. Replace the links with the S3 Object URL link of this newly added .html file</br>
&nbsp;&nbsp;&nbsp;&nbsp; i. To get the S3 Object URL link, click once on the file listed on the S3 Bucket</br>
&nbsp;&nbsp;&nbsp;&nbsp; ii. A panel will appear on the right of the screen</br>
&nbsp;&nbsp;&nbsp;&nbsp; iii. Copy the link under *Overview* -> *Object URL*</br>
```
<link rel="stylesheet" href="https://mylambdajosh.s3.amazonaws.com/css/animate.css">
```

&nbsp;&nbsp;&nbsp;&nbsp;Change from: <b>mylambdajosh.s3.amazonaws.com</b> to the name of your own <b>S3 Bucket URL</b></br>

c. If edits were made to multiple files, repeat same steps by uploading all the newly edited .html files and changing its links respectively to its S3 links

<a name="changesLambda"></a>
## 2. Making Changes to lambda_function.py File
a. There is no need to re-upload the .py file
b. Simply commit from GitHub and lambda function on AWS will be automatically updated. 
