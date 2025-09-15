import os
from dotenv import load_dotenv
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError

HORIZON_SERVER = Server("https://horizon-testnet.stellar.org")
PLATFORM_SECRET = os.getenv("PLATFORM_SECRET_KEY")
PLATFORM_KEYPAIR = Keypair.from_secret(PLATFORM_SECRET)

NETWORK_PASS = Network.TESTNET_NETWORK_PASSPHRASE


# stellar_utils.py (continuação)

def create_competition_pool(entry_fee: float, payout_rules: dict) -> str:
    """
    Cria uma nova conta Stellar para servir como pool da competição.
    
    Args:
        entry_fee (float): Valor da inscrição.
        payout_rules (dict): Dicionário com as regras. Ex: {"1": 0.5, "2": 0.3}
        
    Returns:
        str: A chave pública (endereço) da nova conta/pool.
    """
    pool_keypair = Keypair.random()
    pool_public_key = pool_keypair.public_key
    
    print(f"Criando nova pool com endereço: {pool_public_key}")

    # Pega a conta da plataforma para ser a fonte da transação
    platform_account = HORIZON_SERVER.load_account(PLATFORM_KEYPAIR.public_key)

    tx_builder = TransactionBuilder(
        source_account=platform_account,
        network_passphrase=NETWORK_PASS,
        base_fee=100  # Taxa base em stroops
    )

    # 1. Operação para criar a conta da pool com 2 XLM iniciais
    tx_builder.append_create_account_op(
        destination=pool_public_key,
        starting_balance="2" # Saldo inicial para a conta existir e cobrir taxas
    )

    # 2. Operações para gravar as regras na conta da pool
    tx_builder.append_manage_data_op(name="entry_fee", value=str(entry_fee))
    for position, percentage in payout_rules.items():
        key = f"payout_{position}"
        value = str(percentage)
        tx_builder.append_manage_data_op(name=key, value=value)
    
    # Constrói e assina a transação
    transaction = tx_builder.build()
    transaction.sign(PLATFORM_KEYPAIR) # Assinado pela conta da plataforma
    transaction.sign(pool_keypair)     # Assinado pela chave da nova pool

    try:
        response = HORIZON_SERVER.submit_transaction(transaction)
        print("Transação de criação da pool submetida com sucesso!")
        print(f"Hash: {response['hash']}")
        # IMPORTANTÍSSIMO: Guarde a chave secreta da pool em um local seguro (DB ou cofre)
        # Para o hackathon, você pode simplesmente guardá-la em um dicionário em memória ou no DB.
        # db.save_pool_secret(pool_public_key, pool_keypair.secret)
        return pool_public_key
    except Exception as e:
        print(f"Erro ao criar a pool: {e}")
        return None
    
