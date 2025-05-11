import os
import json
from web3 import Web3
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MultiChainProvider:
    """Multi-chain provider for the Learn & Earn platform"""

    def __init__(self):
        """Initialize multi-chain support"""
        # Configure supported chains
        self.chains = {
            "gnosis": {
                "rpc_url": os.environ.get(
                    "CONNECTION_CONFIGS_CONFIG_GNOSIS_LEDGER_RPC"
                ),
                "chain_id": 100,  # Gnosis Chain ID
                "token_address": os.environ.get(
                    "CONNECTION_CONFIGS_CONFIG_LEARN_TOKEN_ADDRESS"
                ),
                "nft_address": os.environ.get(
                    "CONNECTION_CONFIGS_CONFIG_NFT_BADGE_ADDRESS"
                ),
                "explorer": "https://gnosisscan.io",
            },
            "rootstock": {
                "rpc_url": os.environ.get("CONNECTION_CONFIGS_CONFIG_ROOTSTOCK_RPC"),
                "chain_id": 30,  # Rootstock Chain ID
                "token_address": os.environ.get(
                    "CONNECTION_CONFIGS_CONFIG_ROOTSTOCK_TOKEN_ADDRESS"
                ),
                "nft_address": os.environ.get(
                    "CONNECTION_CONFIGS_CONFIG_ROOTSTOCK_NFT_ADDRESS"
                ),
                "explorer": "https://explorer.rootstock.io",
            },
        }

        # Validate configuration
        for chain, config in self.chains.items():
            if not config["rpc_url"]:
                logger.warning(f"{chain} RPC URL not configured")
            if not config["token_address"]:
                logger.warning(f"{chain} token address not configured")
            if not config["nft_address"]:
                logger.warning(f"{chain} NFT address not configured")

        # Initialize web3 providers
        self.providers = {}
        for chain, config in self.chains.items():
            if config["rpc_url"]:
                try:
                    self.providers[chain] = Web3(Web3.HTTPProvider(config["rpc_url"]))
                    logger.info(f"Connected to {chain} at {config['rpc_url']}")
                except Exception as e:
                    logger.error(f"Failed to connect to {chain}: {e}")

    def get_web3(self, chain="gnosis"):
        """Get Web3 provider for specified chain"""
        if chain not in self.providers:
            raise ValueError(f"Chain {chain} not supported or not configured")
        return self.providers[chain]

    def get_chain_config(self, chain="gnosis"):
        """Get configuration for specified chain"""
        if chain not in self.chains:
            raise ValueError(f"Chain {chain} not supported")
        return self.chains[chain]

    def get_agent_key(self, chain="gnosis"):
        """Get agent private key for the specified chain"""
        # For now, using the same key for all chains
        # In production, you might want different keys per chain
        key_path = Path("/agent_key/ethereum_private_key.txt")
        if not key_path.exists():
            raise FileNotFoundError("Agent private key not found")
        return key_path.read_text().strip()

    def get_explorer_url(self, chain="gnosis", tx_hash=None):
        """Get block explorer URL for the transaction"""
        base_url = self.chains[chain]["explorer"]
        if tx_hash:
            return f"{base_url}/tx/{tx_hash}"
        return base_url


def get_web3_provider(chain="gnosis"):
    """Get Web3 provider for specified chain"""
    if chain == "gnosis":
        rpc_url = os.environ.get("CONNECTION_CONFIGS_CONFIG_GNOSIS_LEDGER_RPC")
    elif chain == "rootstock":
        rpc_url = os.environ.get("CONNECTION_CONFIGS_CONFIG_ROOTSTOCK_RPC")
    else:
        raise ValueError(f"Unsupported chain: {chain}")

    if not rpc_url:
        raise ValueError(
            f"{chain.capitalize()} RPC URL not found in environment variables"
        )
    return Web3(Web3.HTTPProvider(rpc_url))


def get_agent_key():
    """Get agent private key from file"""
    key_path = Path("/agent_key/ethereum_private_key.txt")
    if not key_path.exists():
        raise FileNotFoundError("Agent private key not found")
    return key_path.read_text().strip()


def verify_transaction_on_chain(tx_hash, requirements, chain="gnosis"):
    """Verify a transaction on-chain based on requirements"""
    provider = MultiChainProvider().get_web3(chain)

    try:
        # Get transaction
        tx = provider.eth.get_transaction(tx_hash)
        tx_receipt = provider.eth.get_transaction_receipt(tx_hash)

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

        return {
            "verified": True,
            "explorer_url": MultiChainProvider().get_explorer_url(chain, tx_hash),
        }
    except Exception as e:
        return {"verified": False, "reason": str(e)}


def issue_token_reward(wallet_address, amount, chain="gnosis"):
    """Issue token rewards to a user on specified chain"""
    chain_provider = MultiChainProvider()
    web3 = chain_provider.get_web3(chain)
    chain_config = chain_provider.get_chain_config(chain)
    private_key = chain_provider.get_agent_key(chain)

    account = web3.eth.account.from_key(private_key)

    # Get token address for the specified chain
    token_address = chain_config["token_address"]
    if not token_address:
        raise ValueError(f"Token address not configured for chain {chain}")

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
            "chainId": chain_config["chain_id"],
        }
    )

    # Sign and send transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash_hex = web3.to_hex(tx_hash)

    return {
        "success": True,
        "tx_hash": tx_hash_hex,
        "amount": amount,
        "chain": chain,
        "explorer_url": chain_provider.get_explorer_url(chain, tx_hash_hex),
    }


def mint_nft_badge(wallet_address, badge_data, chain="gnosis"):
    """Mint NFT badge for user achievement on specified chain"""
    chain_provider = MultiChainProvider()
    web3 = chain_provider.get_web3(chain)
    chain_config = chain_provider.get_chain_config(chain)
    private_key = chain_provider.get_agent_key(chain)

    account = web3.eth.account.from_key(private_key)

    # Get NFT address for the specified chain
    nft_address = chain_config["nft_address"]
    if not nft_address:
        raise ValueError(f"NFT address not configured for chain {chain}")

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
            "chainId": chain_config["chain_id"],
        }
    )

    # Sign and send transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash_hex = web3.to_hex(tx_hash)

    return {
        "success": True,
        "tx_hash": tx_hash_hex,
        "token_uri": token_uri,
        "chain": chain,
        "explorer_url": chain_provider.get_explorer_url(chain, tx_hash_hex),
    }


# Add model updates for multi-chain support
def update_models_for_multichain():
    """
    This function represents the changes needed to update models.py
    to support multi-chain wallet addresses and transactions
    """
    # Example model changes (to be implemented in models.py)
    """
    # Add to User model:
    wallet_addresses = models.JSONField(default=dict)  # Store addresses by chain
    preferred_chain = models.CharField(max_length=20, default="gnosis")
    
    # Add to UserTask model:
    reward_chain = models.CharField(max_length=20, default="gnosis")
    reward_tx_hash = models.CharField(max_length=66, null=True, blank=True)
    
    # Add to Task model:
    supported_chains = models.JSONField(default=list)  # List of supported chains
    chain_specific_data = models.JSONField(default=dict)  # Chain-specific requirements
    """
    pass
