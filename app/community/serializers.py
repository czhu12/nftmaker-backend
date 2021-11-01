from community.models import Community, Contract, CommunalCanvas
from rest_framework import serializers


class ContractSerializer(serializers.ModelSerializer):
    address = serializers.CharField(max_length=256)
    class Meta:
        model = Contract
        fields = ['id', 'address', 'balance', 'contract_type', 'block_number']


class CommunalCanvasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunalCanvas
        fields = ['id', 'image']


class CommunitySerializer(serializers.ModelSerializer):
    contract = ContractSerializer(read_only=True)
    communal_canvas = CommunalCanvasSerializer(read_only=True)
    class Meta:
        model = Community
        fields = ['id', 'slug', 'name', 'description', 'website', 'opensea', 'twitter', 'discord', 'etherscan', 'contract', 'communal_canvas']