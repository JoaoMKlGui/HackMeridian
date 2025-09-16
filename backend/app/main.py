from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

import stellar_utils
from stellar_sdk.soroban.types import Address

app = FastAPI(
    title="NotGambling Hackathon API",
    description="API para interagir com os contratos de competição na Stellar.",
)

competitions_db = {}

# --- MODELOS DE DADOS (PYDANTIC) ---
class CompetitionCreateRequest(BaseModel):
    entry_fee: int = Field(..., description="Taxa de entrada em stroops (1 XLM = 10_000_000 stroops)")
    payout_rules: List[int] = Field(..., description="Lista de porcentagens x100. Ex: [5000, 3000, 2000] para 50%, 30%, 20%")
    deadline: int = Field(..., description="Timestamp Unix de quando a competição se encerra para novas entradas")
    min_participants: int = Field(..., description="Número mínimo de participantes para a competição ser válida")

class JoinRequest(BaseModel):
    participant_public_key: str = Field(..., description="A chave pública Stellar (G...) do participante")
    username: str = Field(..., description="O nick do usuário no jogo (ex: CS:GO)")

class DistributeRequest(BaseModel):
    leaderboard: List[str] = Field(..., description="Lista ordenada de usernames (nicks) dos vencedores")

@app.post("/api/competitions", status_code=201)
async def create_competition(req: CompetitionCreateRequest):
    """
    Cria (deploya e inicializa) um novo contrato de competição na rede Stellar.
    Esta operação é paga e assinada pela conta Admin da plataforma.
    """
    try:
        admin_address = Address.from_string(stellar_utils.ADMIN_KEYPAIR.public_key)
        
        contract_id = stellar_utils.deploy_contract(
            admin=admin_address,
            entry_fee=req.entry_fee,
            payout_rules=req.payout_rules,
            deadline=req.deadline,
            min_participants=req.min_participants
        )
        
        # Salva no nosso "banco de dados"
        competitions_db[contract_id] = req.dict()
        
        return {
            "message": "Competição criada com sucesso!",
            "contract_id": contract_id,
            "details": req.dict()
        }
		
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar competição: {e}")

@app.get("/api/competitions")
async def get_all_competitions():
    """
    Retorna uma lista de todas as competições criadas.
    """
    return competitions_db

@app.post("/api/competitions/{contract_id}/join")
async def get_join_transaction(contract_id: str, req: JoinRequest):
    """
    Prepara e retorna a transação XDR para um usuário entrar na competição.
    O frontend deve pegar este XDR e pedir para o usuário assinar via carteira (Freighter).
    """
    if contract_id not in competitions_db:
        raise HTTPException(status_code=404, detail="Competição não encontrada.")
    
    try:
        unsigned_tx_xdr = stellar_utils.build_join_tx_xdr(
            participant_public_key=req.participant_public_key,
            username=req.username,
            contract_id=contract_id
        )
        return {"transaction_xdr": unsigned_tx_xdr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao construir transação de join: {e}")


@app.post("/api/competitions/{contract_id}/distribute")
async def distribute_prizes(contract_id: str, req: DistributeRequest):
    """
    (Endpoint do Oráculo/Admin)
    Executa o payout dos prêmios baseado no leaderboard final.
    Esta operação é paga e assinada pela conta Admin da plataforma.
    """
    if contract_id not in competitions_db:
        raise HTTPException(status_code=404, detail="Competição não encontrada.")
        
    try:
        tx_hash = stellar_utils.invoke_distribute_prizes(
            contract_id=contract_id,
            leaderboard=req.leaderboard
        )
        return {"message": "Distribuição de prêmios iniciada.", "transaction_hash": tx_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao distribuir prêmios: {e}")