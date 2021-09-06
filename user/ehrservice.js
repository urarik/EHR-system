var Web3 = require("web3");
var web3 = new Web3(
  new Web3.providers.HttpProvider("http://127.0.0.1:7545")
);
var crypto = require("crypto");
var buffer = require("buffer").Buffer;
const io = require("socket.io-client");
const EHRSocket = io.connect("http://localhost:8080");
const IpfsSocket = io.connect("http://localhost:8088");
var i  = 0;
getAddress = async function (accountNum) {
  accounts = await web3.eth.getAccounts();
  return accounts[accountNum];
};

send_message = function (info, accountNum, type) {
  //Called by a user.
  //Sends message to EHRs manager for uploading, retrieving, granting permission, getting log.
  //info: depends on the type.
  //accountNum: account number of the ganache accounts.
  //type: "upload", "retrieve", "grant_permission", "get_log"
  var sig;
  info.timestamp = Date.now();
  info_json = JSON.stringify(info);

  web3.eth.getAccounts().then((result) => {
    web3.eth.sign(info_json, result[accountNum]).then((result) => {
      sig = result;
      var detail = {
        info: info_json,
        sig: sig,
      };
      console.log(detail);
      EHRSocket.emit(type, detail);
    });
    //eth.sign vs eth.personal.sign
    //https://ethereum.stackexchange.com/questions/25601/what-is-the-difference-between-web3-eth-sign-web3-eth-accounts-sign-web3-eth-p/25610
  });
};

EHRSocket.on("upload_request_result", (data) => {
  //Receives public key if the request is accepted and sends data to a ipfs server.
  //data: {result: boolean, public if result is true or err}
  var sig;

  if (data["result"] == false)
    document.getElementById("upload-result-text").innerText =
      data["err"];
  else {
    var info = {};
    var index = 1;

    [1, 2, 3].forEach((i) => {
      var fr = new FileReader();
      fr.onload = function (progressEvent) {
        var fileName = fr.name;
        info[fileName] = progressEvent.target.result;
        if (index == 3) {
          var accountNum = document.getElementById("num").value;
          sendHealthData(info, accountNum, data["public"]);
          return;
        }
        index++;
      };
      var input = document.getElementById("file" + i);
      if (input.files.length != 0) {
        var file = input.files[0];
        fr.name = document.getElementById('data'+i).value;
        fr.readAsBinaryString(file);
      } else index++;
    });
  }
});

async function sendHealthData(info, accountNum, publicKey) {
  //Receives data and encrypt data using public key.
  //Sends encrypted data to ipfs server.
  //info: health data to be encrypted.
  //accountNum: account number of the ganache accounts.
  //publicKey: EHRs manager's public key.
  var sig;
  var timestamp = Date.now().toString();
  var encryptedDataList = [], nameList = [];
  for(const key in info) {
    var encryptedData = crypto.publicEncrypt(
      {
        key: publicKey,
        oaepHash: "sha256",
        padding: crypto.constants.RSA_PKCS1_PADDING,
      },
      buffer.from(info[key])
    );
    nameList.push(key);
    encryptedDataList.push(encryptedData);
  }

  var accounts = await web3.eth.getAccounts();
  //sign allows only string. 1. sign with only timestamp 2. sign with string(encrypted data(byte array))
  var sig = await web3.eth.sign(timestamp, accounts[accountNum]);
  var detail = {
    info: timestamp,
    names: nameList,
    data: encryptedDataList,
    sig: sig,
  };
  IpfsSocket.emit("upload", detail);
}

EHRSocket.on("upload_result", (data) => {
  //Receives upload result or err message if failed.
  if (data["result"])
    document.getElementById("upload-result-text").innerText =
      "Success!";
  else
    document.getElementById("upload-result-text").innerText =
      data["err"];
});

EHRSocket.on("get_data_name_result", (data) => {
  if(data["result"]) {
    var type = data["type"];
    var dataList = data["data"];
    var div = document.getElementById('div_'+type);
    while(div.firstChild){ //clear
      div.removeChild(div.firstChild);
    }

    for(var i=0; i < dataList.length; ++i) {
      var checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.id = 'chk'+type+i;
      var span = document.createElement('span');
      span.innerHTML = dataList[i];
      span.id = 'span_'+type+i;
      div.appendChild(span);
      div.appendChild(checkbox);
    }
  }
  else {
    console.log(type)
    var type = data["type"] + '-result-text';
    document.getElementById(type).innerText = data["err"];          
  }

});

EHRSocket.on("retrieve_request_result", (data) => {
  //Receives requested data with json formatted.
  if (data["result"]) {
    var text = "";
    var data = data["data"];
    for(var i = 0; i < data.length; ++i){
      text += data[i][0] + "\n";
      text += data[i][1];
      text += "\n\n";
    }
    document.getElementById("retrieve-result-text").innerText = text;
  } else{
    console.log(document.getElementById("retrieve-result-text"))
    document.getElementById("retrieve-result-text").innerText = data["err"];
  }
});

EHRSocket.on("grant_result", (data) => {
  //Receives permission setting result or err message if failed.
  if (data["result"])
    document.getElementById("grant-result-text").innerText = "Success!";
  else
    document.getElementById("grant-result-text").innerText = data["err"];
});

EHRSocket.on("log_result", (data) => {
  //Receives logs or err message if failed.
  if (data["result"]) {
    var logString = "";
    console.log(data["msg"]);
    data["msg"].forEach((element) => (logString += element + "\n"));
    document.getElementById("log-text").innerText = logString;
  } else document.getElementById("log-text").innerText = data["err"];
});