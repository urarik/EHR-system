pragma solidity ^0.8.7;

contract EHR {
    address private admin;
    address private ehrManager;
    address private ipfs;
    bytes32 constant emptyStringBytes = keccak256(bytes(""));
    bytes constant emptyBytes = bytes("");

    event UserAdded(address userAddress, string userRole);
    event UserRemoved(address userAddress);
    event DataAdded(address indexed userAddress, string dataName, uint time);
    event DataResult(address indexed to, address _from, uint time);
    event PenaltyResult(address indexed to, address _from, uint time);

    struct User {
        string[] dataNames;
        uint8 lastModified;
        string role;
        bool isUploading;
        bool isPenalty;
    }
    mapping(address => User) public users;
    //owner => user => data name
    mapping(address => mapping(address => mapping(string => bool))) ACL;
    mapping(address => mapping(string => bytes)) cid; //change bytes to fixed bytes?

    constructor(address _ehrManager, address _ipfs) {
        admin = msg.sender;
        ehrManager = _ehrManager;
        ipfs = _ipfs;
    }

    modifier onlyAdmin {
        require(msg.sender == admin, "You're not admin!");
        _;
    }
    modifier onlyManager {
        require(msg.sender == ehrManager, "You're not manager!");
        _;
    }
    modifier onlyIpfs {
        require(msg.sender == ipfs, "You're not ipfs!");
        _;
    }
    modifier isExist(address userAddress) {
        //https://ethereum.stackexchange.com/questions/4559/operator-not-compatible-with-type-string-storage-ref-and-literal-string
        require(keccak256(bytes(users[userAddress].role)) != emptyStringBytes, "The user is not existed!");
        _;
    }

    function addUser(address userAddress, string memory userRole) public onlyAdmin {
        User storage user = users[userAddress];
        user.isPenalty = false;
        user.isUploading = false;
        user.lastModified = 0;
        user.role = userRole;
        emit UserAdded(userAddress, userRole);
    }

    function deleteUser(address userAddress) public onlyAdmin {
        delete users[userAddress];
    }

    function upload(address dataOwner) isExist(dataOwner) public onlyManager {  
        users[dataOwner].isUploading = true;
    }
    function getPermission(address dataOwner) public view isExist(dataOwner) onlyIpfs returns(bool){
        return users[dataOwner].isUploading;
    }
    function getDataNamesGrant(address dataOwner) public view isExist(dataOwner) onlyManager returns(string [] memory) {
        return users[dataOwner].dataNames;
    }
    function getDataNamesRetrieve(address dataOwner, address dataUser) public view isExist(dataOwner) onlyManager returns(string [] memory) {
        string[] memory names = users[dataOwner].dataNames;
        string[] memory results = new string[](names.length);
        uint cnt = 0;
        for(uint i =0; i < names.length; ++i) {
            if(ACL[dataOwner][dataUser][names[i]]) results[cnt++] = names[i];
        }
        return results;
    }
    function getCid(address dataOwner, string memory name) public view returns(bytes memory) {
        return cid[dataOwner][name];
    }

    function updateUploadingResult(address dataOwner, string[] memory names, bytes[] memory cids) public onlyManager {
        if(users[dataOwner].isUploading){
            for(uint i = 0; i < names.length; ++i){
                if(keccak256(cid[dataOwner][names[i]]) == keccak256(emptyBytes)) {
                    cid[dataOwner][names[i]] = cids[i];
                    users[dataOwner].dataNames.push(names[i]);
                }
                else {
                    cid[dataOwner][names[i]] = cids[i];
                }
                emit DataAdded(dataOwner, names[i], block.timestamp);
            }
            users[dataOwner].isUploading = false;
        }
    }

    function retrieve(address dataOwner, address dataUser, string[] memory names) public view isExist(dataOwner) isExist(dataUser) onlyManager returns(bytes []memory) {
        require(users[dataUser].isPenalty == false, "The data user has penalty!");
        bytes[] memory cids = new bytes[](names.length);
        uint cnt = 0;
        for(uint i =0; i < names.length; ++i) {
            if(ACL[dataOwner][dataUser][names[i]] == false) revert("The data owner didn't grant permission to data user.");
            if(keccak256(cid[dataOwner][names[i]]) == keccak256(emptyBytes)) revert("The data owner doesn't have a data.");
            cids[cnt++] = cid[dataOwner][names[i]];
        }
        return cids;
    }
    function retrieveResult(address dataOwner, address dataUser, bool _isPenalty) public onlyManager {
        if(_isPenalty){
            emit PenaltyResult(dataOwner, dataUser, block.timestamp);
            users[dataUser].isPenalty = true;    
        } else
            emit DataResult(dataOwner, dataUser, block.timestamp);
    }

    function grantPermission(address dataOwner, address dataUser, string[] memory names) public isExist(dataOwner) isExist(dataUser) onlyManager {
        for(uint i =0; i < names.length; ++i) {
            if(keccak256(cid[dataOwner][names[i]]) == keccak256(emptyBytes)) revert("The user doesn't have a data.");
            ACL[dataOwner][dataUser][names[i]] = true;
        }
    }
    function setPenalty(address user, bool _isPanelty) public isExist(user) onlyAdmin {
        users[user].isPenalty = _isPanelty;   
    }

}
