import json
import time
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
from routes.workflow_routes import router as workflow_router
from routes.stream_routes import router as stream_router
from solcx import compile_source, install_solc
install_solc(version='latest')


# Initialize the FastAPI app
app = FastAPI()

# Load environment variables from the .env file
load_dotenv(override=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Start time tracking
start_time = time.time()

# Include workflow router
app.include_router(workflow_router, prefix="/workflow", tags=["Workflow"])
app.include_router(stream_router, prefix="/stream", tags=["Stream"])

# Root endpoint
@app.get("/testcontract")
def read_root():
    test_deployment()
    return {"message": "Test contract deployment successful!"}


def test_deployment():
    solstring = "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n\nimport \"@openzeppelin/contracts/token/ERC721/ERC721.sol\";\nimport \"@openzeppelin/contracts/access/Ownable.sol\";\nimport \"@openzeppelin/contracts/utils/Counters.sol\";\n\ncontract RideLoyaltyNFT is ERC721, Ownable {\n    using Counters for Counters.Counter;\n    Counters.Counter private _tokenIdCounter;\n\n    struct Milestone {\n        uint256 rideCount;\n        string rewardDescription;\n    }\n\n    mapping(address => uint256) public rideCounts;\n    mapping(address => uint256[]) public customerNFTs;\n    mapping(uint256 => Milestone) public milestones;\n    mapping(uint256 => bool) public redeemedNFTs;\n\n    event NFTMinted(address indexed customer, uint256 indexed tokenId, string uri);\n    event NFTTransferred(address indexed from, address indexed to, uint256 indexed tokenId);\n    event NFTBurned(address indexed customer, uint256 indexed tokenId);\n\n    modifier useNFTURI() {\n        string memory uri = \"https://ai-image-store.s3.ap-south-1.amazonaws.com/Apple%20Nature's%20trickster%20with%20hidden%20intentions%2C%20enticing%20yet%20acidic.-abad324f.webp\";\n        _;\n    }\n\n    constructor() ERC721(\"RideLoyaltyNFT\", \"RLNFT\") {}\n\n    function setMilestone(uint256 milestoneId, uint256 rideCount, string memory rewardDescription) external onlyOwner {\n        milestones[milestoneId] = Milestone(rideCount, rewardDescription);\n    }\n\n    function recordRide(address customer) external onlyOwner {\n        rideCounts[customer]++;\n        checkMilestones(customer);\n    }\n\n    function checkMilestones(address customer) internal {\n        for (uint256 i = 0; i < _tokenIdCounter.current(); i++) {\n            if (rideCounts[customer] == milestones[i].rideCount && !redeemedNFTs[i]) {\n                mintNFT(customer);\n            }\n        }\n    }\n\n    function mintNFT(address customer) internal useNFTURI {\n        uint256 tokenId = _tokenIdCounter.current();\n        _tokenIdCounter.increment();\n        _safeMint(customer, tokenId);\n        customerNFTs[customer].push(tokenId);\n        string memory uri = \"https://ai-image-store.s3.ap-south-1.amazonaws.com/Apple%20Nature's%20trickster%20with%20hidden%20intentions%2C%20enticing%20yet%20acidic.-abad324f.webp\";\n        _setTokenURI(tokenId, uri);\n        emit NFTMinted(customer, tokenId, uri);\n    }\n\n    function transferNFT(address from, address to, uint256 tokenId) external {\n        require(_isApprovedOrOwner(_msgSender(), tokenId), \"Caller is not owner nor approved\");\n        _transfer(from, to, tokenId);\n        emit NFTTransferred(from, to, tokenId);\n    }\n\n    function burnNFT(uint256 tokenId) external {\n        require(_isApprovedOrOwner(_msgSender(), tokenId), \"Caller is not owner nor approved\");\n        require(!redeemedNFTs[tokenId], \"NFT already redeemed\");\n        redeemedNFTs[tokenId] = true;\n        _burn(tokenId);\n        emit NFTBurned(msg.sender, tokenId);\n    }\n\n    function getCustomerNFTs(address customer) external view returns (uint256[] memory) {\n        return customerNFTs[customer];\n    }\n}\n"

    # with open("contracts/RideLoyaltyNFT.sol", "w") as f:
    #     f.write(solstring)

    compiled_sol = compile_source(
        solstring,
        output_values=['abi', 'bin']
    )
    print(compiled_sol)

    # Save the compiled contract to a file
    with open("contracts/compiled_contract.json", "w") as f:
        f.write(json.dumps(compiled_sol))