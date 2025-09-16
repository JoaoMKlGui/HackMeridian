import os
from dotenv import load_dotenv
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError

HORIZON_SERVER = Server("https://horizon-testnet.stellar.org")
PLATFORM_SECRET = os.getenv("PLATFORM_SECRET_KEY")
PLATFORM_KEYPAIR = Keypair.from_secret(PLATFORM_SECRET)

NETWORK_PASS = Network.TESTNET_NETWORK_PASSPHRASE


# stellar_utils.py (continuação)

def create_competition_pool(entry_fee: float, payout_rules: list) -> Keypair | None:
    """
    Cria uma nova conta Stellar para servir como pool da competição.
    
    Args:
        entry_fee (float): Valor da inscrição.
        payout_rules (list): Lista de prêmios por posição.
        
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
    for i, percentage in enumerate(payout_rules):
        key = f"payout_{i}"
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

        return pool_keypair
    
    except Exception as e:
        print(f"Erro ao criar a pool: {e}")
        return None
    
def monitor_pool_payments(pool_address: str, participants_db: dict):
    """
    Escuta por pagamentos e popula o "banco de dados" em memória.
    """
    print(f"Iniciando monitoramento para a pool: {pool_address}")
    
    # Inicializa o dicionário para esta pool se ele não existir
    if pool_address not in participants_db:
        participants_db[pool_address] = {}
    
    cursor = 'now'
    for payment in HORIZON_SERVER.payments().for_account(pool_address).cursor(cursor).stream():
        if payment['to'] == pool_address:
            try:
                tx_hash = payment['transaction_hash']
                tx = HORIZON_SERVER.transactions().transaction(tx_hash).execute()
                memo = tx.get('memo')
                
                if memo and tx.get('memo_type') == 'text':
                    username = memo
                    stellar_address = payment['from']
                    
                    participants_db[pool_address][username] = stellar_address
                    
                    print("--- Participante Validado! ---")
                    print(f"  Pool: {pool_address[:10]}...")
                    print(f"  Username (do Memo): {username}")
                    print(f"  Endereço Stellar: {stellar_address[:10]}...")
                    print(f"  DB atualizado: {participants_db[pool_address]}")
            except Exception as e:
                print(f"Erro ao processar pagamento recebido: {e}")


def execute_payout(pool_address: str, pool_secret: str, leaderboard: list[str], participants_db: dict):
    """
    Executa o payout baseado em um leaderboard de usernames.

    Args:
        pool_address (str): Endereço da pool.
        pool_secret (str): Chave secreta da pool.
        leaderboard (list[str]): Lista ordenada de usernames dos vencedores.
        participants_db (dict): O nosso "banco de dados" em memória.
    """
    # 1. Carrega a conta da pool e pega as informações necessárias
    pool_keypair = Keypair.from_secret(pool_secret)
    pool_account = HORIZON_SERVER.load_account(pool_address)
    
    # Pega o saldo total para calcular os prêmios
    total_prize_pool = 0
    for balance in pool_account.balances:
        if balance.asset_type == 'native':
            # Subtrai a reserva mínima para não gastar o saldo base
            total_prize_pool = float(balance.balance) - (1 + 0.5 * len(pool_account.data))
            break

    # Pega as regras de payout gravadas on-chain
    payout_rules = {key: float(value.decode('utf-8')) for key, value in pool_account.data.items()}

    # Pega o mapa de username -> endereço para esta pool específica
    paid_users_map = participants_db.get(pool_address, {})

    # 2. Constrói a transação
    tx_builder = TransactionBuilder(
        source_account=pool_account,
        network_passphrase=NETWORK_PASS,
        base_fee=100
    ).set_timeout(30)

    print("--- Calculando Payouts ---")
    payouts_sent = 0

    for i, username in enumerate(leaderboard):
        position = str(i) # Posição no placar (0, 1, 2...)
        
        # VERIFICA SE O USERNAME DO LEADERBOARD PAGOU A INSCRIÇÃO
        if username in paid_users_map:
            payouts_sent += 1
            winner_address = paid_users_map[username]
            payout_percentage = payout_rules.get(f"payout_{position}", 0)
            payout_amount = total_prize_pool * payout_percentage

            if payout_amount > 0:
                print(f"  - Posição {position}: {username} ({winner_address[:10]}...) recebe {payout_amount:.7f} XLM")
                tx_builder.append_payment_op(
                    destination=winner_address,
                    asset=Asset.native(),
                    amount=f"{payout_amount:.7f}" # Formata com 7 casas decimais
                )

    if payouts_sent == 0:
        print("Nenhum vencedor encontrado na lista de participantes pagos. Nenhum payout a ser feito.")
        return None

    # 3. Assina e envia a transação
    transaction = tx_builder.build()
    transaction.sign(pool_keypair)
    
    try:
        response = HORIZON_SERVER.submit_transaction(transaction)
        print("Transação de Payout submetida com sucesso!")
        return response['hash']
    except Exception as e:
        print(f"Erro ao executar payout: {e}")
        return None
