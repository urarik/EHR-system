import eth_account
from web3 import exceptions
from utils import w3, ehr, ehrAccount, ipfsAccount, adminAccount

w3.eth.default_account = adminAccount
# transact() vs call()
# https://stackoverflow.com/questions/61716597/decode-the-return-value-from-a-smart-contract-with-web3-py
# https://ethereum.stackexchange.com/questions/765/what-is-the-difference-between-a-transaction-and-a-call/770#770


def addUser():
    print("type [address role(owner/user)]")
    address, role = input().split()
    if role == 'owner' or role == 'user':
        try:
            ehr.functions.addUser(address, role).transact()
            _role = ehr.functions.users(address).call()[1]
        except exceptions.ContractLogicError as err:
            print("Fail! " + err)
            return
        if role == _role:
            print("success!")
            return
    print("fail!")


def delUser():
    print("type address")
    address = input()
    try:
        ehr.functions.deleteUser(address).transact()
        _role = ehr.functions.users(address).call()[1]
        if not _role == '':
            print("fail!")
            return
        else:
            print("success!")
    except exceptions.ContractLogicError:
        print("fail!")


def delPenalty():
    print("type address")
    address = input()
    try:
        ehr.functions.setPenalty(address, False).transact()
        _isPenalty = ehr.functions.users(address).call()[3]
        if _isPenalty:
            print("fail!")
            return
        else:
            print("success!")
    except exceptions.ContractLogicError:
        print("fail!")


if __name__ == '__main__':
    while True:
        print("1. add user  2. del user  3. del penalty 4. view waiting list  5. confirm registration request")
        n = input()
        if n == '1':
            addUser()
        elif n == '2':
            delUser()
        elif n == '3':
            delPenalty()