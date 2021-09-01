import ipfshttpclient as Ipfs
import socketio
from aiohttp import web
from utils import *


sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

serverSocket = socketio.Client()
# Run server(EHRs manager) first before run ipfs server so that server socket can be connected.
serverSocket.connect('http://127.0.0.1:8080')

ipfs = Ipfs.connect()

w3.eth.default_account = ipfsAccount


@sio.event
def upload(sid, data):  # called by user
    """
    Called by a user. Upload data to ipfs and return cid and data owner's address to the EHRs manager.

    :param sid: socket id
    :param data: {info: {timestamp}, data: encrypted data, sig: signature}
    """
    userAddress = recover(data["info"], data["sig"])
    if ehr.functions.getPermission(userAddress).call():
        # A ipfs.add() accepts only file.
        names = []
        cids = []
        for name, encryptedData in getInfo(data):
            with open('temp.txt', 'wb') as f:
                f.write(encryptedData)
            cid = ipfs.add('temp.txt')
            names.append(name)
            cids.append(cid.encode('utf-8'))

        info = {'results': (names, cids), 'address': userAddress, 'timestamp': timestamp()}
        result = True
    else:
        info = {'address': userAddress, 'timestamp': timestamp(), 'err': Errors.noPermissionError}
        result = False

    info_json, sig = sign(info, ipfsAccount)
    serverSocket.emit('upload_result', {'result': result, 'info': info_json, 'sig': sig})
    printLog("upload", {'address': userAddress, 'result': result, "timestamp": timestamp()})
    # user -> EHRm -> SC -> EHRm -> user -> IPFS -CID-> [EHRm -> user]


def getInfo(data):
    nameList = data["names"]
    dataList = data["data"]
    for i in range(len(nameList)):
        yield nameList[i], dataList[i]


@sio.event
async def retrieve(sid, data): # called by server
    """
    Called by a server. Retrieve data using cid and return data to EHRs manager.

    :param sid: socket id
    :param data: {info: {cid: cid, timestamp}, sig: signature}
    """
    _ehrAccount = recover(data["info"], data["sig"])
    if _ehrAccount == ehrAccount:
        info = json.loads(data["info"])
        encrypted_data = ipfs.cat(info["cid"])
        info = {'timestamp': timestamp(), 'address': info["address"]}
        # Caution: json.dumps doesn't accept bytes as the value of the dictionary
        # Split info and data because the data is bytes.
        info_json, sig = sign(info, ipfsAccount)
        serverSocket.emit('retrieve_result', {'info': info_json, 'sig': sig, 'data': encrypted_data})
        printLog("retrieve", {'timestamp': timestamp()})


if __name__ == '__main__':
    web.run_app(app, port=8088)
