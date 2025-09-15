import os
from dotenv import load_dotenv
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError

HORIZON_SERVER = Server("https://horizon-testnet.stellar.org")
PLATFORM_SECRET = os.getenv("PLATFORM_SECRET_KEY")
PLATFORM_KEYPAIR = Keypair.from_secret(PLATFORM_SECRET)

NETWORK_PASS = Network.TESTNET_NETWORK_PASSPHRASE