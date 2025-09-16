# stellar_utils.py (CORRIGIDO)

import os
from stellar_sdk import (
    Server,
    Keypair,
    Network,
    TransactionBuilder,
    SorobanServer,
    Account
)
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.soroban.types import Address, Symbol, Vec, I128, U64, U32

# --- Configuração ---
HORIZON_SERVER_URL = "https://horizon-testnet.stellar.org"
SOROBAN_RPC_URL = "https://soroban-testnet.stellar.org:443"
NETWORK_PASS = Network.TESTNET_NETWORK_PASSPHRASE

server = Server(HORIZON_SERVER_URL)
soroban_server = SorobanServer(SOROBAN_RPC_URL)

# --- Chaves e Contrato (Melhor prática para o Hackathon) ---
ADMIN_SECRET = os.getenv("PLATFORM_ADMIN_SECRET")
if not ADMIN_SECRET:
    raise ValueError("PLATFORM_ADMIN_SECRET não encontrado no .env")

ADMIN_KEYPAIR = Keypair.from_secret(ADMIN_SECRET)

CONTRACT_WASM_PATH = os.getenv("CONTRACT_WASM_PATH")



def deploy_contract(
    admin: Address,
    entry_fee: int,
    payout_rules: list[int],
    deadline: int,
    min_participants: int
) -> str:
    """
    Faz o deploy completo (Upload + Create + Initialize) de um novo contrato de competição.
    Esta versão faz o upload do WASM a cada execução.
    Retorna o ID (endereço) do novo contrato.
    """
    source_account = server.load_account(ADMIN_KEYPAIR.public_key)
    
    # --- Etapa 1: Upload do WASM ---
    print("🚀 Etapa 1/3: Fazendo upload do WASM do contrato...")
    tx_upload = TransactionBuilder(source_account, NETWORK_PASS, base_fee=100_000) \
        .append_upload_contract_wasm_op(wasm=CONTRACT_WASM_PATH) \
        .build()

    prepared_upload = soroban_server.prepare_transaction(tx_upload)
    prepared_upload.sign(ADMIN_KEYPAIR)
    sent_upload = soroban_server.send_transaction(prepared_upload)

    # Espera a confirmação para pegar o wasm_hash
    while True:
        tx_status = soroban_server.get_transaction(sent_upload.hash)
        if tx_status.status != "PENDING":
            break

    # Valida se a transação foi bem-sucedida antes de prosseguir
    if tx_status.status != "SUCCESS":
        raise Exception(f"Transação de upload do WASM falhou: {tx_status.result_xdr}")

    wasm_hash = tx_status.result_xdr.v3.results[0].tr.upload_contract_wasm_result.success.hex()
    print(f"✅ WASM Uploaded. Hash: {wasm_hash}")


    # --- Etapa 2: Criar o Contrato a partir do Hash do WASM ---
    print("\n🚀 Etapa 2/3: Criando o contrato a partir do hash...")
    tx_create = TransactionBuilder(source_account, NETWORK_PASS, base_fee=100_000) \
        .append_create_contract_op(wasm_hash=bytes.fromhex(wasm_hash)) \
        .build()
    
    prepared_create = soroban_server.prepare_transaction(tx_create)
    prepared_create.sign(ADMIN_KEYPAIR)
    sent_create = soroban_server.send_transaction(prepared_create)

    # Espera a confirmação para pegar o contract_id
    while True:
        tx_status = soroban_server.get_transaction(sent_create.hash)
        if tx_status.status != "PENDING":
            break
            
    if tx_status.status != "SUCCESS":
        raise Exception(f"Transação de criação do contrato falhou: {tx_status.result_xdr}")

    contract_id = tx_status.result_xdr.v3.results[0].tr.invoke_host_fn_result.success.address.contract_id.hex()
    print(f"✅ Contrato criado. ID: {contract_id}")
    

    # --- Etapa 3: Inicialização do Contrato ---
    print("\n🚀 Etapa 3/3: Inicializando o contrato...")
    tx_init = TransactionBuilder(source_account, NETWORK_PASS, base_fee=100_000) \
        .append_invoke_contract_function_op(
            contract_id=contract_id,
            function_name="initialize",
            parameters=[
                admin,
                I128(entry_fee),
                Vec([U32(p) for p in payout_rules]),
                U64(deadline),
                U32(min_participants)
            ]
        ).build()

    prepared_init = soroban_server.prepare_transaction(tx_init)
    prepared_init.sign(ADMIN_KEYPAIR)
    sent_init = soroban_server.send_transaction(prepared_init)
    print(f"✅ Transação de inicialização enviada. Hash: {sent_init.hash}")

    return contract_id


def build_join_tx_xdr(participant_public_key: str, username: str, contract_id: str) -> str:
    """
    Constrói a transação para o usuário entrar na competição, com o footprint correto.
    Retorna o XDR da transação para o frontend assinar.
    """
    # Validação: Verifica se a conta do participante existe na rede
    try:
        participant_account = server.load_account(participant_public_key)
    except NotFoundError:
        raise ValueError("A conta do participante não existe na testnet. Ela precisa ser criada e receber XLM primeiro.")

    # Constrói a transação sem taxa e sem sequence number
    tx = TransactionBuilder(participant_account, NETWORK_PASS, base_fee=100_000) \
        .append_invoke_contract_function_op(
            contract_id=contract_id,
            function_name="join",
            parameters=[
                Address.from_string(participant_public_key),
                Symbol(username)
            ],
            # A autorização (e o pagamento da taxa) vem do participante
            source=participant_public_key 
        ).build()

    print("Simulando transação de 'join' para obter o footprint...")
    prepared_tx = soroban_server.prepare_transaction(tx)
    
    # Retorna a transação pronta para ser assinada, em formato XDR
    return prepared_tx.to_xdr()


def invoke_distribute_prizes(contract_id: str, leaderboard: list[str]) -> str:
    """
    Chama a função de distribuir prêmios. Assinada pelo admin da plataforma.
    """
    source_account = server.load_account(ADMIN_KEYPAIR.public_key)

    tx = TransactionBuilder(source_account, NETWORK_PASS, base_fee=100_000) \
        .append_invoke_contract_function_op(
            contract_id=contract_id,
            function_name="distribute_prizes",
            parameters=[
                Vec([Symbol(user) for user in leaderboard])
            ]
        ).build()

    print("Simulando transação de 'distribute_prizes'...")
    prepared_tx = soroban_server.prepare_transaction(tx)
    prepared_tx.sign(ADMIN_KEYPAIR)
    
    sent_tx = soroban_server.send_transaction(prepared_tx)
    print(f"✅ Payout iniciado para o contrato {contract_id}. Hash: {sent_tx.hash}")
    
    return sent_tx.hash