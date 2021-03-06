from rsa import DecryptionError
from web3 import exceptions
import socketio
import rsa
from aiohttp import web
from utils import *


class Key:  # A class associated with RSA.
    __slots__ = 'private_key', 'public_key', "public_key_string"

    def __init__(self):
        with open('private.key', mode='rb') as privateFile:
            keyData = privateFile.read()
            self.private_key = rsa.PrivateKey.load_pkcs1(keyData)

        with open('public.key', mode='rb') as publicFile:
            keyData = publicFile.read()
            self.public_key_string = keyData.decode('utf-8')
            self.public_key = rsa.PublicKey.load_pkcs1(keyData)

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using public key.

        :return: Encrypted data
        """
        return rsa.encrypt(data, self.public_key)

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data using private key.

        :return: Decrypted data
        """
        return rsa.decrypt(data, self.private_key)


key = Key()

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

w3.eth.default_account = ehrAccount

sidDict = {}  # Stores socket id to send reply.

ipfsSocket = socketio.Client()


@sio.event
async def upload_request(sid, data):  # Called by user
    """
    Called by a user. Set user's permission in blockchain and return public key for the user to encrypt data.

    :param sid: Socket id
    :param data: {info: {timestamp}, sig: signature}
    """
    userAddress = recover(data["info"], data["sig"])
    try:
        ehr.functions.upload(userAddress).transact()
        await sio.emit('upload_request_result', {'result': True, 'public': key.public_key_string}, room=sid)
        printLog("upload", {'address': userAddress, 'result': True})
        sidDict[userAddress] = sid
    except exceptions.ContractLogicError as err:
        # The user isn't registered or doesn't have data(CID).
        await sio.emit('upload_request_result', {'result': False, 'err': str(err)}, room=sid)
        printLog("upload", {'address': userAddress, 'result': False, 'err': str(err)})


@sio.event
async def upload_result(sid, data):
    """
    Called by a ipfs server. Receive encrypted data and user's address and return result to the user.

    :param sid: Socket id
    :param data: {result: boolean, info: {address, timestamp, cid if result is true or err}, sig: signature}
    """
    info = json.loads(data["info"])
    userSid = sidDict[info["address"]]
    isSuccess = False

    if data["result"]:
        _ipfsAccount = recover(data["info"], data["sig"])
        if _ipfsAccount == ipfsAccount:
            try:
                (names, cids) = info["results"]
                for i in range(len(names)):
                    cids[i] = key.encrypt(cids[i].encode('utf-8'))
                ehr.functions.updateUploadingResult(info["address"], names, cids).transact()
            except (OverflowError, exceptions.ContractLogicError) as err:
                # The message is too big to encrypt it or a transaction error.
                await sio.emit('upload_result', {'result': False, 'err': str(err)}, room=userSid)
                del sidDict[info["address"]]
                printLog('upload_result', {'result': False, 'err': str(err)})
                return
            isSuccess = True

    if isSuccess:
        await sio.emit('upload_result', {'result': True}, room=userSid)
        printLog('upload_result', {'result': True})
    else:
        await sio.emit('upload_result', {'result': False, 'err': info["err"]}, room=userSid)
        printLog('upload_result', {'result': False, 'err': info["err"]})
    del sidDict[info["address"]]


@sio.event
async def retrieve_request(sid, data):
    """
    Called by a user. Receive target address and get cid using user and target address.
    Send message to ipfs server for getting encrypted data.

    :param data: {info: {target: target address, timestamp}, sig: signature}
    """
    if not ipfsSocket.connected:
        ipfsSocket.connect('http://127.0.0.1:8088')

    info = json.loads(data["info"])
    userAddress = recover(data["info"], data["sig"])
    targetAddress = info["target"]
    try:
        encryptedCids = ehr.functions.retrieve(info["target"], userAddress, info["names"]).call()
        cids = []
        print(info["names"])
        for encryptedCid in encryptedCids:
            if encryptedCid == b'':
                continue
            cids.append(key.decrypt(encryptedCid).decode('utf-8'))
        info = {'cids': cids, 'names': info["names"], 'timestamp': timestamp(), 'address': userAddress}
        info_json, sig = sign(info, ehrAccount)
        ipfsSocket.emit('retrieve', {'result': True, 'info': info_json, 'sig': sig})
        sidDict[userAddress] = sid
        ehr.functions.retrieveResult(targetAddress, userAddress, False).transact()
        printLog('retrieve', {'address': userAddress, 'result': True})
    except exceptions.ContractLogicError as err:
        # The user isn't registered or doesn't have data(CID) or the data user has penalty.
        await sio.emit('retrieve_request_result', {'result': False, 'err': str(err)}, room=sid)
        ehr.functions.retrieveResult(info["target"], userAddress, True).transact()
        printLog('retrieve', {'address': userAddress, 'result': False, 'err': str(err)})


@sio.event
async def retrieve_result(sid, data):
    """
    Called by a ipfs server. Receive encrypted data and return original data to the user.

    :param data: {info: {timestamp, address: user address}, sig: signature, data: encrypted data}
    """
    _ipfsAddress = recover(data["info"], data["sig"])
    if _ipfsAddress == ipfsAccount:
        info = json.loads(data["info"])
        try:
            encryptedDataList, names = data["data"]
            originalDataList = []
            for i, encryptedData in enumerate(encryptedDataList):
                originalData = key.decrypt(encryptedData).decode('utf-8')
                originalData = originalData.replace("\\", "")[1:-1]
                originalDataList.append([names[i], originalData])

            await sio.emit('retrieve_request_result', {'result': True, 'data': originalDataList},
                           room=sidDict[info["address"]])
            printLog('retrieve_result', {'result': True})

        except DecryptionError as err:
            await sio.emit('retrieve_request_result', {'result': False, 'err': str(err)},
                           room=sidDict[info["address"]])
            printLog('retrieve_result', {'result': False, 'err': str(err)})

        del sidDict[info["address"]]


@sio.event
async def get_data_name(sid, data):
    userAddress = recover(data["info"], data["sig"])
    info = json.loads(data["info"])
    try:
        if info["type"] == 'grant':
            dataList = ehr.functions.getDataNamesGrant(userAddress).call()
        else:
            dataList = ehr.functions.getDataNamesRetrieve(info["target"], userAddress).call()
            dataList = dataList[0:indexOf('', dataList)]
        if len(dataList) == 0:
            raise Errors.NoElementError
        await sio.emit('get_data_name_result', {'result': True, 'type': info["type"], 'data': dataList})
        printLog('get_data_name_result', {'result': True})

    except (exceptions.ContractLogicError, Errors.NoElementError) as err:
        await sio.emit('get_data_name_result', {'result': False, 'type': info["type"], 'err': str(err)})
        printLog('get_data_name_result', {'result': False, 'type': info["type"], 'err': str(err)})


@sio. event
async def grant_permission(sid, data):
    """
    Called by a user. Receive target address(data user) and grant permission to this.
    Return result to the user.

    :param data: {info: {target: target address, timestamp}, sig: signature}
    """
    userAddress = recover(data["info"], data["sig"])
    try:
        info = json.loads(data["info"])
        ehr.functions.grantPermission(userAddress, info["target"], info["names"]).transact()
        await sio.emit('grant_result', {'result': True}, room=sid)
        printLog('grant_permission', {'address': userAddress, 'result': True})
    except exceptions.ContractLogicError as err:
        await sio.emit('grant_result', {'address': userAddress, 'result': False, 'err': str(err)}, room=sid)
        printLog('grant_permission', {'address': userAddress, 'result': True})


@sio.event
async def get_log(sid, data):  # Called by user
    """
    Called by a user. Get log from blockchain and return results to the user.

    :param data: {info:{timestamp, type: log type}, sig: signature}
    """
    userAddress = recover(data["info"], data["sig"])
    info = json.loads(data["info"])
    if info["type"] == "upload":
        logFilter = ehr.events.DataAdded.createFilter(fromBlock=0, argument_filters={'userAddress': userAddress})
    elif info["type"] == "retrieve":
        logFilter = ehr.events.DataResult.createFilter(fromBlock=0, argument_filters={'to': userAddress})
    elif info["type"] == "penalty":
        logFilter = ehr.events.PenaltyResult.createFilter(fromBlock=0, argument_filters={'to': userAddress})
    else:
        await sio.emit({'result': False, 'err': Errors.noMatchTypeError(info["type"])}, room=sid)
        printLog('get_log', {'address': userAddress, 'result': False, 'err': Errors.noMatchTypeError(info["type"])})
        return

    entries = logFilter.get_all_entries()
    entryStrings = []
    for entry in entries:
        entryStr = ""
        for entryKey in entry:
            entryStr += entryKey + ": " + str(entry[entryKey]) + "\n"
        entryStrings.append(entryStr)

    if len(entryStrings) != 0:
        await sio.emit('log_result', {'result': True, 'msg': entryStrings}, room=sid)
        printLog('get_log', {'address': userAddress, 'result': True})
    else:
        await sio.emit('log_result', {'result': False, 'err': Errors.noLogError}, room=sid)
        printLog('get_log', {'address': userAddress, 'result': False, 'err': Errors.noLogError})


if __name__ == '__main__':
    web.run_app(app)
