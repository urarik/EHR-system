## Introduction
This project is about the EHR system implementation. The overall structure is based on Blockchain for Secure EHRs Sharing of Mobile Cloud Based E-Health Systems by Dinh C. Nguyen, Pubudu N. Pathirana, Ming Ding, Aruna Seneviratne.

## Sequence diagram
  \<upload\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131261747-8a98fdaf-199f-4f4f-807e-27446a7d4bfb.png"/><br/><br/>
  \<retrieve\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131261748-1939742f-c63d-40aa-8c5f-b785c896fdb5.png"/>
   
## Environment
### Program language
* EHRs manager (main server), ipfs server : python.
* client-side web : js.
* smart contract : solidity.

### Run environment
* Ganache + Remix
* accounts[3] for EHRs manager and accounts[4] for ipfs server are fixed.
* After deploying the contract, modify address.txt and abi.tex.

## Result
\<upload\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131261754-431e2da7-ca6b-4066-bd65-378bee585422.png"/><br/><br/>
\<grant permission\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131261755-5b264923-0e1b-4624-aad9-adcec912048a.png"/><br/><br/>
\<retrieve\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131261757-cefa6930-057a-4758-aab8-438d167294aa.png"/><br/><br/>
\<log\><br/><br/>
<img width="80%" src="https://user-images.githubusercontent.com/81351772/131261760-510716a0-7375-4aa5-bed1-3f761d11f8ab.png"/><br/><br/>
