## Introduction
This project is about the EHR system implementation. The overall structure is based on Blockchain for Secure EHRs Sharing of Mobile Cloud Based E-Health Systems by Dinh C. Nguyen, Pubudu N. Pathirana, Ming Ding, Aruna Seneviratne.

## Sequence diagram
  \<upload\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131285888-bfb93207-b02a-4795-b484-9a242785575e.png"/><br/><br/>
  \<retrieve\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131285891-122ff0f7-a3f9-4dda-9fc2-e7cb3c0e2091.png"/>

## Environment
### Program language
* EHRs manager (main server), ipfs server : python.
* client-side web : js.
* smart contract : solidity.

### Run environment
* Ganache + Remix
* The role of accounts[3], [4] and [9] are fixed. Accounts[3] for EHRs manager , accounts[4] for ipfs server and accounts[9] for admin. You can change the role by modifying server/utils.py, admin/utils.py and ipfs/utils.py
* After deploying the contract, modify address.txt and abi.tex if it is necessary.

## Result
\<upload\><br/><br/>
You can upload file to ipfs.
<img width="80%" src="https://user-images.githubusercontent.com/81351772/132211878-f9546ba9-fe96-4d9c-ab58-2e0ce89b266f.png"/><br/><br/>
\<grant permission\><br/><br/>
You can load files you uploaded and then grant permission to target user for each file.
<img width="80%" src="https://user-images.githubusercontent.com/81351772/132211881-51f8ced7-ff85-4799-bb9b-d8a0879a9ec6.png"/><br/><br/>
\<retrieve\><br/><br/>
You can see data names allowed by owner and then see the contents you checked.
<img width="80%" src="https://user-images.githubusercontent.com/81351772/132211885-b54abeec-64a7-4974-9ca0-0dade0d40a1a.png"/><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/132211888-b91fc251-6ec4-42dd-9bb4-c4e4dd6ee1f4.png"/><br/><br/>
\<log\><br/><br/>
You can see upload logs, retrieve logs and unaccepted retrieve logs.
<img width="80%" src="https://user-images.githubusercontent.com/81351772/132211883-f46432cf-cca4-44b4-b430-b5826b404db3.png"/><br/><br/>
