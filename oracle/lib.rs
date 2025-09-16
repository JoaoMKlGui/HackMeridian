#![no_std]
use soroban_sdk::{
    contract, contractimpl, contracttype, symbol_short, Address, Env, Symbol, Vec,
};

const MAX_ENTRIES: u32 = 256;

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Admin,
    Feed(Symbol),       // snapshots por feed_key
    FeedLastTs(Symbol), // último timestamp aceito por feed_key (freshness)
}

#[derive(Clone)]
#[contracttype]
pub struct Entry {
    pub username: Symbol, // deve bater com o username cadastrado na pool
    pub rank: u32,        // 1,2,3...
}

#[derive(Clone)]
#[contracttype]
pub struct Snapshot {
    pub tournament_id: u64,
    pub ts: u64,             // ledger timestamp
    pub entries: Vec<Entry>, // ordenado por rank
}

#[contract]
pub struct OracleContract;

#[contractimpl]
impl OracleContract {
    pub fn initialize(env: Env, admin: Address) {
        if env.storage().instance().has(&DataKey::Admin) {
            panic!("Oracle already initialized");
        }
        env.storage().instance().set(&DataKey::Admin, &admin);
    }

    /// Publica ou atualiza o snapshot para um feed_key específico.
    /// Apenas o admin pode publicar (pode ser uma conta multisig).
    pub fn publish(env: Env, feed_key: Symbol, tournament_id: u64, entries: Vec<Entry>) {
        // --- Auth ---
        let admin: Address = env.storage().instance().get(&DataKey::Admin).unwrap();
        admin.require_auth();

        // --- Sanidade básica ---
        let n = entries.len();
        if n == 0 {
            panic!("empty entries");
        }
        if n > MAX_ENTRIES {
            panic!("entries too large");
        }

        // --- Validar ordenação e contiguidade dos ranks e usernames únicos ---
        // Regras:
        // - rank deve começar em 1 e seguir contíguo até n (1..=n)
        // - entries deve estar ordenado por rank (estritamente crescente)
        // - usernames devem ser únicos
        // Obs: Vec de soroban_sdk não oferece HashSet; checamos duplicatas O(n^2), ok para n pequeno.
        for i in 0..n {
            let e_i: Entry = entries.get_unchecked(i);
            let expected_rank: u32 = (i + 1) as u32;
            if e_i.rank != expected_rank {
                panic!("ranks must be contiguous starting at 1");
            }
            // username não vazio: Symbol internamente pode ser vazio; evitamos.
            // (Opcional: adapte sua regra de "vazio" conforme sua origem de dados)
            if e_i.username.to_string().is_empty() {
                panic!("empty username");
            }
            // duplicatas
            for j in (i + 1)..n {
                let e_j: Entry = entries.get_unchecked(j);
                if e_i.username == e_j.username {
                    panic!("duplicate username");
                }
                if e_j.rank <= e_i.rank {
                    panic!("entries must be strictly sorted by rank asc");
                }
            }
        }

        // --- Freshness: impedir retrocesso de timestamp por feed ---
        let now = env.ledger().timestamp();
        let last_ts_key = DataKey::FeedLastTs(feed_key.clone());
        if let Some(last_ts) = env.storage().instance().get::<_, u64>(&last_ts_key) {
            if now < last_ts {
                panic!("stale snapshot (timestamp moved backwards)");
            }
        }

        // --- Persistência ---
        let snap = Snapshot {
            tournament_id,
            ts: now,
            entries,
        };
        env.storage()
            .instance()
            .set(&DataKey::Feed(feed_key.clone()), &snap);
        env.storage()
            .instance()
            .set(&last_ts_key, &now);

        // --- Evento (útil p/ indexadores e debug) ---
        // Tópico: ("oracle", "publish", feed_key)
        env.events().publish(
            (symbol_short!("oracle"), symbol_short!("publish"), feed_key),
            (tournament_id, now),
        );
    }

    /// Recupera o snapshot mais recente para o feed_key.
    pub fn get_leaderboard(env: Env, feed_key: Symbol) -> Snapshot {
        env.storage()
            .instance()
            .get(&DataKey::Feed(feed_key))
            .expect("feed not found")
    }
}
