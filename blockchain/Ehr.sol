pragma solidity ^0.8.7;

contract EHR {
    address[] waitingList; //회원가입 대기자
    address private admin;
    address private ehrManager;
    address private ipfs;
    bytes32 constant emptyStringBytes = keccak256(bytes(""));
    bytes constant emptyBytes = "0x0";

    event UserAdded(address userAddress, string userRole);
    event UserRemoved(address userAddress);
    event DataAdded(address indexed userAddress, uint time);
    event DataResult(address indexed to, address _from, uint time);
    event PenaltyResult(address indexed to, address _from, uint time);

    struct User {
        bytes cid;
        string role;
        bool isUploading;
        bool isPenalty;
    }
    mapping(address => User) public users;
    mapping(address => mapping(address => bool)) ACL;

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

    function getWaitingList() public view onlyAdmin returns(address[] memory) {
        return waitingList;
    }

    function registerConfirm(uint index, string memory _userRole, bool is_approved) public onlyAdmin {
        if(is_approved) users[waitingList[index]] = User("", _userRole, false, false);
        waitingList[index] = waitingList[waitingList.length-1];
        waitingList.pop();
    }

    function addUser(address userAddress, string memory userRole) public onlyAdmin returns(User memory){
        users[userAddress] = User("", userRole, false, false);
        emit UserAdded(userAddress, userRole);
        return users[userAddress];
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
    function updateUploadingResult(address dataOwner, bytes memory _cid) public onlyManager {
        users[dataOwner].cid = _cid;
        users[dataOwner].isUploading = false;
        emit DataAdded(dataOwner, block.timestamp);
    }

    function retrieve(address dataOwner, address dataUser) public view isExist(dataOwner) isExist(dataUser) onlyManager returns(bytes memory) {
        require(users[dataUser].isPenalty == false, "The data user has penalty!");
        require(keccak256(users[dataOwner].cid) != keccak256(emptyBytes), "data owner doesn't have a data.");
        
        if(ACL[dataOwner][dataUser] != false || dataOwner == dataUser) {
            return users[dataOwner].cid;
        }
        else{
            revert("data owner didn't grant permission to data user.");
        }
    }
    function retrieveResult(address dataOwner, address dataUser, bool _isPenalty) public onlyManager {
        if(_isPenalty){
            emit PenaltyResult(dataOwner, dataUser, block.timestamp);
            users[dataUser].isPenalty = true;    
        } else
            emit DataResult(dataOwner, dataUser, block.timestamp);
    }

    function grantPermission(address dataOwner, address dataUser) public isExist(dataOwner) isExist(dataUser) onlyManager {
        ACL[dataOwner][dataUser] = true;
    }
    function setPenalty(address user, bool _isPanelty) public isExist(user) onlyAdmin {
        users[user].isPenalty = _isPanelty;   
    }

}
