import os
from web3 import Web3
from web3.constants import MAX_INT, HASH_ZERO
from web3.middleware import (geth_poa_middleware, construct_sign_and_send_raw_middleware)
from web3.gas_strategies.time_based import fast_gas_price_strategy
from dotenv import load_dotenv

load_dotenv()

redeem_positions_abi = """[{"constant":false,"inputs":[{"name":"collateralToken","type":"address"},{"name":"parentCollectionId","type":"bytes32"},{"name":"conditionId","type":"bytes32"},{"name":"indexSets","type":"uint256[]"}],"name":"redeemPositions","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]"""

def main():
    pk = os.getenv("PK")
    rpc_url = os.getenv("RPC_URL") 

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(pk))
    w3.eth.default_account = w3.eth.account.from_key(pk).address
    w3.eth.set_gas_price_strategy(fast_gas_price_strategy)

    print(f"Starting...")
    print(f"Wallet: {w3.eth.default_account}")

    usdc_address = w3.to_checksum_address("0x2791bca1f2de4661ed88a30c99a7a9449aa84174")
    ctf_address = w3.to_checksum_address("0x4d97dcd97ec945f40cf65f87097ace5ea0476045")

    ctf = w3.eth.contract(ctf_address, abi=redeem_positions_abi)
    condition_id = "0x..."
    try:
        txn_hash_bytes = ctf.functions.redeemPositions(
            usdc_address, # The collateral token address
            HASH_ZERO, # The parent collectionId, always bytes32(0) for Polymarket markets  
            condition_id, # The conditionId of the market
            [1, 2], # The index set used by Polymarket for binary markets
        ).transact()
        txn_hash = w3.to_hex(txn_hash_bytes)
        print(f"Redeem transaction hash: {txn_hash}")
        w3.eth.wait_for_transaction_receipt(txn_hash)
        print("Redeem complete!")

    except Exception as e:
        print(f"Error redeeming Outcome Tokens : {e}")
        raise e

    print("Done!")


main()
