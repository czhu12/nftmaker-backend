from django import forms
from community.models import Contract

class ConnectContractWithProject():
    def __init__(self, contract_address, project) -> None:
        self.contract_address = contract_address
        self.project = project

    def execute(self):
        try:
            contract = Contract.objects.get(
                address=self.contract_address)
        except Contract.DoesNotExist:
            contract = Contract(address=self.contract_address)
            contract.save()
        self.project.contract = contract
        self.project.save()