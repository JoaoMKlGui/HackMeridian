import os
import json
import subprocess
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN", "")
SOROBAN_SECRET   = os.getenv("SOROBAN_SECRET", "")
ORACLE_ID        = os.getenv("ORACLE_ID", "")
NETWORK          = os.getenv("NETWORK", "testnet")
FEED_PREFIX      = os.getenv("FEED_PREFIX", "GYMRATS:CSGO")
RPC_URL          = os.getenv("SOROBAN_RPC_URL", "")  # opcional

BASE = "https://api.pandascore.co"

app = FastAPI(title="CSGO Leaderboard Publisher")

class PublishReq(BaseModel):
    tournament_id: int
    feed_suffix: str = ""      # se vazio, usa tournament_id
    limit: int = 64
    team_to_username: Dict[str, str] = {}

def fetch_standings(tournament_id: int) -> List[Dict]:
    if not PANDASCORE_TOKEN:
        raise RuntimeError("PANDASCORE_TOKEN não configurado")
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
    r = requests.get(
        f"{BASE}/tournaments/{tournament_id}/standings",
        headers=headers,
        params={"per_page": 100, "page": 1},
        timeout=30
    )
    r.raise_for_status()
    return r.json()

def to_entries(raw: List[Dict], limit: int, team_to_username: Dict[str, str]):
    ordered = sorted(raw, key=lambda x: x.get("rank", 1_000_000))
    entries = []
    for row in ordered[:limit]:
        team_name = (row.get("team") or {}).get("name") or (row.get("player") or {}).get("name") or "N/A"
        username = team_to_username.get(team_name, team_name)
        rank = int(row.get("rank", 999999))
        entries.append({"username": username, "rank": rank})
    return entries

def soroban_publish(feed_key: str, tournament_id: int, entries: List[Dict]):
    if not (SOROBAN_SECRET and ORACLE_ID):
        raise RuntimeError("SOROBAN_SECRET ou ORACLE_ID não configurados")
    args = [
        "soroban", "contract", "invoke",
        "--id", ORACLE_ID,
        "--fn", "publish",
        "--arg", json.dumps(feed_key),
        "--arg", str(int(tournament_id)),
        "--arg", json.dumps(entries),
        "--source", SOROBAN_SECRET,
        "--network", NETWORK,
    ]
    if RPC_URL:
        args += ["--rpc-url", RPC_URL]
    try:
        out = subprocess.check_output(args, stderr=subprocess.STDOUT, text=True, timeout=90)
        return out
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"invoke error: {e.output}") from e

@app.post("/publish")
def publish(req: PublishReq):
    try:
        raw = fetch_standings(req.tournament_id)
        entries = to_entries(raw, req.limit, req.team_to_username)
        feed_suffix = req.feed_suffix or str(req.tournament_id)
        feed_key = f"{FEED_PREFIX}:{feed_suffix}"
        out = soroban_publish(feed_key, req.tournament_id, entries)
        return {"ok": True, "feed_key": feed_key, "published": len(entries), "cli_output": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
