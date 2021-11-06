from community.models import Community, Contract, CommunalCanvas, Message
from rest_framework import serializers


class ContractSerializer(serializers.ModelSerializer):
    address = serializers.CharField(max_length=256)

    class Meta:
        model = Contract
        fields = ['id', 'address', 'balance', 'contract_type', 'block_number', 'block_timestamp']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['token_identifier', 'message', 'created', 'community']


class CommunalCanvasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunalCanvas
        fields = ['id', 'image']


class CommunitySerializer(serializers.ModelSerializer):
    contract = ContractSerializer(read_only=True)
    communal_canvas = CommunalCanvasSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Community
        fields = [
            'id', 'slug', 'symbol', 'name', 'description', 'website', 'opensea',
            'twitter', 'discord', 'etherscan', 'contract', 'communal_canvas',
            'messages'
        ]
