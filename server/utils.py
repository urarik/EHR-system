import json
import string

import eth_account
from web3 import Web3, Account, HTTPProvider
import datetime

with open("../address.txt", "r") as f:
    contractAddress = f.read()
with open("../abi.txt", "r") as f:
    abi = f.read()


w3 = Web3(HTTPProvider('http://localhost:7545'))
ehr = w3.eth.contract(address=contractAddress, abi=abi)
accounts = w3.eth.get_accounts()
ehrAccount = accounts[3]
ipfsAccount = accounts[4]
adminAccount = accounts[9]


class Errors:
    noPermissionError = "The user has no permission for uploading!"
    noLogError = "There are no logs!"

    @staticmethod
    def noMatchTypeError(logType):
        return f"{logType} is not supported!"

    class NoElementError(Exception):
        def __init__(self):
            super().__init__('There is no data granted permission from the owner or the owner doesn\'t have a data.')


def timestamp():
    return datetime.datetime.now().timestamp()


def sign(info: object, account):
    """
    :return: info as json formatted string, signature
    """
    info_json = json.dumps(info)
    sig = w3.eth.sign(account, text=info_json)
    return info_json, sig


def recover(text, sig):
    """
    :return: address used to sign.
    """
    info_hash = eth_account.messages.defunct_hash_message(text=text)
    return Account.recoverHash(info_hash, signature=sig)


def printLog(type: string, content: dict):
    """
    Prints log.
    """
    print(type)
    for key, value in content.items():
        print(str(key) + ": " + str(value))
    print()
