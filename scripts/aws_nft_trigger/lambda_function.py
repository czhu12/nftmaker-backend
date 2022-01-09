import requests
import urllib

def lambda_handler(event, context):
    # TODO: change rare mints backend
    url = 'https://www.mockachino.com/7e9a84eb-d138-4b/nftpractice'
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    myobj = {'success': key}
    x = requests.post(url, data = myobj)
    print(myobj)