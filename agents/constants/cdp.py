from cdp import *



Cdp.configure(api_key_name, api_key_private_key)

def fetch_wallet(wallet_id: str):
    fetched_wallet = Wallet.fetch(wallet_id)
    fetched_wallet.load_seed("my_seed.json")
    return fetched_wallet

def create_token(givenwallet, name, symbol, initial_supply):
    """
    Create a new ERC-20 token.
    
    Args:
        name (str): The name of the token
        symbol (str): The symbol of the token
        initial_supply (int): The initial supply of tokens
    
    Returns:
        str: A message confirming the token creation with details
    """
    deployed_contract = givenwallet.deploy_token(name, symbol, initial_supply)
    deployed_contract.wait()
    return f"Token {name} ({symbol}) created with initial supply of {initial_supply} and contract address {deployed_contract.contract_address}", deployed_contract.contract_address