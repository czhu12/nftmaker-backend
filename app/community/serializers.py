from community.models import Community, Contract, CommunalCanvas, Message, Reply, Pixel
from rest_framework import serializers


class ContractSerializer(serializers.ModelSerializer):
    address = serializers.CharField(max_length=256)

    class Meta:
        model = Contract
        fields = ['id', 'address', 'symbol', 'balance', 'name', 'contract_type', 'block_number', 'block_timestamp']


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['id', 'token_identifier', 'body', 'created', 'message']

class MessageSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'token_identifier', 'body', 'created', 'community', 'replies']


class CommunalCanvasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunalCanvas
        fields = ['id', 'image']


class PixelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pixel
        fields = ['id', 'x', 'y', 'color', 'token_identifier', 'communal_canvas', 'created']



class CommunitySerializer(serializers.ModelSerializer):
    contract = ContractSerializer(read_only=True)
    communal_canvas = CommunalCanvasSerializer(read_only=True)

    class Meta:
        model = Community
        fields = [
            'id', 'slug', 'name', 'description', 'website', 'opensea',
            'twitter', 'discord', 'etherscan', 'contract', 'communal_canvas',
            'messages'
        ]
