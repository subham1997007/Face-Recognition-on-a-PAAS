# from boto3 import client as boto3_client
# import face_recognition
# import pickle
# from unittest import result
import os
import boto3
import subprocess
# import botocore

AWS_ACCESS_KEY_ID="AKIAZBFZGODZZKFI4SWH"
AWS_SECRET_ACCESS_KEY="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"
AWS_REGION_NAME="us-east-1"
endpoint_url = 'https://sqs.us-east-1.amazonaws.com'
sqs = boto3.client('sqs', aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
			endpoint_url=endpoint_url, region_name=AWS_REGION_NAME)

def face_recognition_handler(event, context):	
	bucket_name = event['Records'][0]['s3']['bucket']['name']
	key = event['Records'][0]['s3']['object']['key']

	s3_client = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	path_l="/tmp/"
	file_path=path_l+key
	s3_client.download_file(bucket_name, key, file_path)
	
	predicted_class = subprocess.Popen(['python3.8', 'eval_face_recognition.py', '--img_path', f'{file_path}'], stdout=subprocess.PIPE)
	predicted_class.wait()
	output = predicted_class.stdout.read()
	output=str(output,"utf-8")
	# print(output)
	output=output.split("\n")
	nametoFetch=output[-2].split(".png, ")[1][:-1]
	# print("hello")
	nameIDmap={"Harsh":3,"Dhruval":1,"Kenil":2}
	# print(nametoFetch)
	dbclient = boto3.resource('dynamodb',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	response = dbclient.Table('Student_Info').get_item(Key={"Id":nameIDmap[nametoFetch],"Name":nametoFetch.lower()})
	
	#send resp to sqs
	mssgToSend=key+","+response['Item']["Name"]+","+response['Item']["Major"]+","+response['Item']["Year"]
	queue_url="https://sqs.us-east-1.amazonaws.com/621011169523/LambdaResp"
	sqs.send_message(QueueUrl=queue_url,MessageBody=(mssgToSend))

	print(mssgToSend)

	return output
	# print(predicted_class)
