import boto3
config ={
    "bucket": "dev20-carvi-s3-iot-ap-northeast-2-topic-backup",
    'StartingToken':None
}

AWS_ACCESS = 'AKIAICFM4F6PFMZG4JKQ'
AWS_SECRET = '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'
bucketName = 'raspberry22-backup'

session = boto3.Session(aws_access_key_id = AWS_ACCESS ,aws_secret_access_key = AWS_SECRET)
client = session.client('s3')

directory = 'C:/RasberryPi_CarVi/GPS/'
filenames = [os.path.basename(x) for x in glob.glob(str(directory) + '*{}.txt'.format(tripStart))]

for f in filenames:
    client.upload_file(directory+f, bucketName, f)
    
    
    
''' Use 'boto'
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os, glob

AWS_ACCESS = 'AKIAICFM4F6PFMZG4JKQ'
AWS_SECRET = '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'
conn = S3Connection(AWS_ACCESS,AWS_SECRET)
bucketName = 'raspberry22-backup'
#tripStart = 'DATA'

def uploadS3(bucketName, tripStart):    
    #conn.create_bucket(bucket_name = 'raspberry22-backup')
    bucket = conn.get_bucket(bucketName)
    directory = 'C:/RasberryPi_CarVi/GPS/'
    filenames = [os.path.basename(x) for x in glob.glob(str(directory) + '*{}.txt'.format(tripStart))]
    
    for f in filenames:
        k = Key(bucket)
        k.key = f
        k.set_contents_from_filename(directory + f)
        print("Uploading to S3 bucket %s" %(bucket))
'''
