# from concurrent.futures import thread
import numpy as np
import cv2
import time
import os
import random
import sys
import boto3
import threading
from collections import Counter

aws_access_key_id='AKIAZBFZGODZZKFI4SWH'
aws_secret_access_key='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'
REGION_NAME='us-east-1'
ENDPOINT_URL = 'https://sqs.us-east-1.amazonaws.com'
SQS_URL = 'https://sqs.us-east-1.amazonaws.com/621011169523/LambdaResp'


s3 = boto3.resource(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
    )

sqs = boto3.client('sqs', 
	aws_access_key_id= aws_access_key_id,
	aws_secret_access_key=aws_secret_access_key,
	endpoint_url=ENDPOINT_URL,
	region_name=REGION_NAME)

def upload_to_s3_input_bucket(s3, bucket_name, image_name, image_source) :
    s3.Object(bucket_name, image_name).upload_file(Filename=image_source)


fps = 24
width = 160
height = 160
video_codec = cv2.VideoWriter_fourcc("D", "I", "V", "X")

name="videosFolder"
folderName=name

name = os.path.join(os.getcwd(), str(name))
print("ALl logs saved in dir:", name)
if not os.path.isdir(name):
    os.mkdir(name)

timeMap=Counter()

def mssgResp():

	while (True) :
		response = sqs.receive_message(
	        QueueUrl=SQS_URL,
	        MaxNumberOfMessages=10,
	        MessageAttributeNames=[
	            'Messages'
	        ],
	    )

		if 'Messages' in response :
			currt=time.time()
			for msg in response['Messages']:
				imgName,personName,personMajor,personDegree=msg['Body'].split(",")
				print("The ", imgName[:-4], " person recognized: ",personName,", ",personMajor,", ",personDegree)
				print("Latency: ",str(currt-float(timeMap[imgName[:-4]])))
				sqs.delete_message(
                    QueueUrl = SQS_URL,
                    ReceiptHandle = msg['ReceiptHandle']
                )

def vidCap():
    cap = cv2.VideoCapture(0)
    ret = cap.set(3, 160)
    ret = cap.set(4, 160)
    cur_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    video_file_count = 1
    video_file = os.path.join(name, str(video_file_count) + ".avi")
    print(video_file.replace("\\","\\\\"))
    print("Capture video saved location : {}".format(video_file))

    video_writer = cv2.VideoWriter(video_file, video_codec, fps, (int(cap.get(3)), int(cap.get(4))))

    start = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            if time.time() - start > 0.5:
                cv2.imwrite(str(video_file_count)+".png",frame)
                upload_to_s3_input_bucket(s3, 'rpiframes', str(video_file_count)+".png", os.getcwd()+"/"+str(video_file_count)+".png")
                timeMap[str(video_file_count)]=str(time.time())
                start = time.time()
                video_file_count += 1
                video_file = os.path.join(name, str(video_file_count) + ".avi")
                video_writer = cv2.VideoWriter(video_file, video_codec, fps, (int(cap.get(3)), int(cap.get(4))))

            video_writer.write(frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                return
        else:
            break

    for i in range(1,video_file_count+1):
        upload_to_s3_input_bucket(s3, 'rpivideos', str(i)+".avi", os.getcwd()+"/"+folderName+"/"+str(i)+".avi")      

    cap.release()
    cv2.destroyAllWindows()

# creating threads
t1 = threading.Thread(target=vidCap, name='t1')
t2 = threading.Thread(target=mssgResp, name='t2')  

# starting threads
t1.start()
t2.start()

# wait until all threads finish
t1.join()
t2.join()
