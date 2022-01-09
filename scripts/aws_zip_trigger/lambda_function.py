import json

import urllib
import zipfile
import boto3
import io

s3 = boto3.client('s3')

# make a dedicated bucket for zip files
bucket = 'zipnftbucket'

# nft bucket
nft_bucket = "nftbucketcelina"

def lambda_handler(event, context):
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        putObjects = []
        failed = False
        with io.BytesIO(obj['Body'].read()) as tf:
            tf.seek(0)
            
            with zipfile.ZipFile(tf, mode='r') as zipf:
                image_folder = [x.filename for x in zipf.infolist() if x.is_dir() and "images" in x.filename][0]
                image_files = [x for x in zipf.infolist() if x.filename.startswith(image_folder)  and x.filename.endswith((".png", ".gif", ".jpeg", ".jpg"))]
               
                metadata_folder = [x.filename for x in zipf.infolist() if x.is_dir() and "metadata" in x.filename][0]
                metadata_files_names = [x.filename for x in zipf.infolist() if x.filename.startswith(metadata_folder) and x.filename.split('/')[-1].isdigit()]
                
                # check that all the images have metadata
                for image in image_files:
                    name = image.filename.split("/")[-1].split(".")[0]
                    if metadata_folder + name not in metadata_files_names:
                        failed = True
    
                if failed == False:
                    metadata_files = [x for x in zipf.infolist() if x.filename.startswith(metadata_folder) and x.filename.split('/')[-1].isdigit()]
                
                    for file in image_files:
                        fileName = file.filename
                        # file name should be a number and we should do validation here
                        putFile = s3.put_object(Bucket=nft_bucket, Key=fileName, Body=zipf.read(file))
                        putObjects.append(putFile)
                    
                    for file in metadata_files:
                        fileName = file.filename
                        # file name should be a number and we should do validation here
                        putFile = s3.put_object(Bucket=nft_bucket, Key=fileName, Body=zipf.read(file))
                        putObjects.append(putFile)


            # delete zip file after unzip
            if len(putObjects) > 0:
                deletedObj = s3.delete_object(Bucket=bucket, Key=key)
                print('deleted zip file')

            if failed:
                failedJson = {}
                failedJson['error'] = "images need their corresponding metadata file"
                responseObject = {}
                responseObject['statusCode'] = 200
                responseObject['headers'] = {}
                responseObject['headers']['Content-Type'] = 'application/json'
                responseObject['body'] = json.dumps(failedJson)
                return responseObject

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
