import os
import json
from web3 import Web3
import requests
from pathlib import Path


def get_web3_provider():
    """Get Web3 provider from environment variables"""
    rpc_url = os.environ.get("CONNECTION_CONFIGS_CONFIG_GNOSIS_LEDGER_RPC")
    if not rpc_url:
        raise ValueError("RPC URL not found in environment variables")
    return Web3(Web3.HTTPProvider(rpc_url))


def get_agent_key():
    """Get agent private key from file"""
    key_path = Path("/agent_key/ethereum_private_key.txt")
    if not key_path.exists():
        raise FileNotFoundError("Agent private key not found")
    return key_path.read_text().strip()


def verify_transaction_on_chain(tx_hash, requirements):
    """Verify a transaction on-chain based on requirements"""
    web3 = get_web3_provider()

    try:
        # Get transaction
        tx = web3.eth.get_transaction(tx_hash)
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)

        # Check if transaction exists and was successful
        if not tx or not tx_receipt:
            return {"verified": False, "reason": "Transaction not found"}

        if tx_receipt.status != 1:
            return {"verified": False, "reason": "Transaction failed"}

        # Check specific requirements if any
        if (
            "to_address" in requirements
            and tx.to.lower() != requirements["to_address"].lower()
        ):
            return {"verified": False, "reason": "Wrong recipient address"}

        # For checking specific contract interactions, decode logs if needed
        # This is a simplified implementation

        return {"verified": True}
    except Exception as e:
        return {"verified": False, "reason": str(e)}


def issue_token_reward(wallet_address, amount):
    """Issue token rewards to a user"""
    web3 = get_web3_provider()
    private_key = get_agent_key()
    account = web3.eth.account.from_key(private_key)

    # Load token contract
    token_address = os.environ.get("CONNECTION_CONFIGS_CONFIG_LEARN_TOKEN_ADDRESS")
    if not token_address:
        raise ValueError("Token address not found in environment variables")

    # Simple ERC20 ABI for transfer function
    abi = [
        {
            "inputs": [
                {"name": "recipient", "type": "address"},
                {"name": "amount", "type": "uint256"},
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        }
    ]

    token_contract = web3.eth.contract(address=token_address, abi=abi)

    # Prepare transaction
    tx = token_contract.functions.transfer(
        wallet_address,
        web3.to_wei(amount, "ether"),  # Convert to token decimals if different
    ).build_transaction(
        {
            "from": account.address,
            "gas": 100000,
            "gasPrice": web3.eth.gas_price,
            "nonce": web3.eth.get_transaction_count(account.address),
            "chainId": web3.eth.chain_id,
        }
    )

    # Sign and send transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return {"success": True, "tx_hash": web3.to_hex(tx_hash), "amount": amount}


def mint_nft_badge(wallet_address, badge_data):
    """Mint NFT badge for user achievement"""
    web3 = get_web3_provider()
    private_key = get_agent_key()
    account = web3.eth.account.from_key(private_key)

    # Load NFT contract
    nft_address = os.environ.get("CONNECTION_CONFIGS_CONFIG_NFT_BADGE_ADDRESS")
    if not nft_address:
        raise ValueError("NFT address not found in environment variables")

    # Simplified NFT ABI for minting
    abi = [
        {
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "tokenURI", "type": "string"},
            ],
            "name": "mintBadge",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function",
        }
    ]

    nft_contract = web3.eth.contract(address=nft_address, abi=abi)

    # Upload metadata to IPFS (simplified)
    # In a real implementation, you'd use a service like nft.storage
    token_uri = f"ipfs://badge/{badge_data['id']}"

    # Prepare transaction
    tx = nft_contract.functions.mintBadge(wallet_address, token_uri).build_transaction(
        {
            "from": account.address,
            "gas": 200000,
            "gasPrice": web3.eth.gas_price,
            "nonce": web3.eth.get_transaction_count(account.address),
            "chainId": web3.eth.chain_id,
        }
    )

    # Sign and send transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return {"success": True, "tx_hash": web3.to_hex(tx_hash), "token_uri": token_uri}
