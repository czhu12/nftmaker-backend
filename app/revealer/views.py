import boto3
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.urls.base import reverse
from web3 import Web3
from app.settings import HOST_DOMAIN, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from revealer import models
import json
S3_BUCKET_NAME = "nft-revealer"


#with open("resources/solidity/abi/IERC721Enumerable.json", "r") as f:
#    IERC721_ENUMERABLE_ABI = json.load(f)


def latest_token_id_for_contract(contract_address):
    # w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    # nft_contract = w3.eth.contract(address=nft_reveal.contract_address, abi=IERC721_ENUMERABLE_ABI)
    # transaction = nft_contract.functions.totalSupply().buildTransaction()
    # signed_txn = w3.eth.account.sign_transaction(
    #    transaction,
    #    private_key=os.environ.get('PRIVATE_KEY'),
    # )
    # response = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return 0


def s3_file(path):
    session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    s3 = session.resource("s3", region_name="us-west-1")
    obj = s3.Object(S3_BUCKET_NAME, path)

    filedata = obj.get()["Body"].read()
    return filedata


def _reveal_image(nft_reveal, token_id):
    path = "{}/images/{}.png".format(nft_reveal.slug, str(token_id))
    return s3_file(path)


def _reveal_metadata(nft_reveal, token_id):
    s3_path = str(nft_reveal.slug) + "/json/" + str(token_id)
    return json.loads(s3_file(s3_path))


def _fake_metadata(nft_revealer, token_id):
    image_url = reverse('image', kwargs={'slug': nft_revealer.slug, 'token_id': token_id})
    return {
        "dna": "45e240b0b05aa88c4f70c7e07af0e2d1d1abed1c",
        "name": "#{}".format(token_id),
        "description": "Pre-Reveal Dope Dinos",
        "image": HOST_DOMAIN + image_url,
        "edition": 0,
        "date": 1634112372805,
        "attributes": [],
        "compiler": HOST_DOMAIN,
    }


def _fake_image(nft_reveal, token_id):
    path = nft_reveal.slug + "/fake.png"
    return s3_file(path)


def metadata(request, slug, token_id):
    nft_reveal = models.NftReveal.objects.get(slug=slug)
    if nft_reveal is None:
        return HttpResponseNotFound()

    if nft_reveal.latest_token_id is None or token_id > nft_reveal.latest_token_id:
        actual_latest_token_id = latest_token_id_for_contract(
            nft_reveal.contract_address
        )
        if actual_latest_token_id != nft_reveal.latest_token_id:
            nft_reveal.latest_token_id = actual_latest_token_id
            nft_reveal.save()

    if nft_reveal.latest_token_id > token_id:
        return JsonResponse(_reveal_metadata(nft_reveal, token_id))
    else:
        return JsonResponse(_fake_metadata(nft_reveal, token_id))


def image(request, slug, token_id):
    nft_reveal = models.NftReveal.objects.get(slug=slug)
    if nft_reveal is None:
        return HttpResponseNotFound()
    if nft_reveal.latest_token_id is None or token_id > nft_reveal.latest_token_id:
        f = _fake_image(nft_reveal, token_id)
        return HttpResponse(f, content_type="image/png")
    else:
        f = _reveal_image(nft_reveal, token_id)
        return HttpResponse(f, content_type="image/png")
