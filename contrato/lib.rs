#![no_std]
use soroban_sdk::{
    contract, contractimpl, contracttype, token, Address, Env, Map, Symbol, Vec,
};

#[contracttype]
#[derive(Clone)]
pub enum DataKey {
    Admin,
    EntryFee,
    PayoutRules,
    Participants,
    IsActive,
    Deadline,
    MinParticipants,
    XlmWrapper, // endereço do token wrapper XLM (Address)
    Pool,       // saldo do pool (i128)
}

#[contract]
pub struct CompetitionContract;

#[contractimpl]
impl CompetitionContract {
    // initialize agora recebe o endereço do wrapper XLM
    pub fn initialize(
        env: Env,
        admin: Address,
        entry_fee: i128,
        payout_rules: Vec<u32>,
        deadline: u64,
        min_participants: u32,
        xlm_wrapper: Address,
    ) {
        if env.storage().instance().has(&DataKey::Admin) {
            panic!("Contract already initialized");
        }

        env.storage().instance().set(&DataKey::Admin, &admin);
        env.storage().instance().set(&DataKey::EntryFee, &entry_fee);
        env.storage().instance().set(&DataKey::PayoutRules, &payout_rules);
        env.storage().instance().set(&DataKey::Participants, &Map::<Symbol, Address>::new(&env));
        env.storage().instance().set(&DataKey::IsActive, &true);
        env.storage().instance().set(&DataKey::Deadline, &deadline);
        env.storage().instance().set(&DataKey::MinParticipants, &min_participants);
        env.storage().instance().set(&DataKey::XlmWrapper, &xlm_wrapper);
        env.storage().instance().set(&DataKey::Pool, &0_i128); // pool começa em 0
    }

    pub fn join(env: Env, participant: Address, username: Symbol) {
        participant.require_auth();

        let is_active: bool = env.storage().instance().get(&DataKey::IsActive).unwrap();
        if !is_active {
            panic!("Competition is closed");
        }

        let entry_fee: i128 = env.storage().instance().get(&DataKey::EntryFee).unwrap();

        // pega endereço do wrapper salvo no storage
        let xlm_wrapper_address: Address = env.storage().instance().get(&DataKey::XlmWrapper).unwrap();
        let token_client = token::Client::new(&env, &xlm_wrapper_address);

        // transfer do participante para o contrato
        token_client.transfer(&participant, &env.current_contract_address(), &entry_fee);

        // atualiza mapa de participantes
        let mut participants: Map<Symbol, Address> =
            env.storage().instance().get(&DataKey::Participants).unwrap();
        if participants.contains_key(username.clone()) {
            panic!("Username already registered");
        }

        participants.set(username, participant);
        env.storage().instance().set(&DataKey::Participants, &participants);

        // incrementa pool
        let mut pool: i128 = env.storage().instance().get(&DataKey::Pool).unwrap();
        pool = pool + entry_fee;
        env.storage().instance().set(&DataKey::Pool, &pool);
    }

    pub fn withdraw(env: Env, participant_address: Address) {
        participant_address.require_auth();

        let is_active: bool = env.storage().instance().get(&DataKey::IsActive).unwrap();
        if !is_active {
            panic!("Competition is not active");
        }

        let mut participants: Map<Symbol, Address> = env.storage().instance().get(&DataKey::Participants).unwrap();
        let entry_fee: i128 = env.storage().instance().get(&DataKey::EntryFee).unwrap();

        // busca username correspondente ao endereço
        let mut username_to_remove: Option<Symbol> = None;
        for (username, address) in participants.iter() {
            if address == participant_address {
                username_to_remove = Some(username);
                break;
            }
        }

        if let Some(username) = username_to_remove {
            participants.remove(username);
            env.storage().instance().set(&DataKey::Participants, &participants);

            let xlm_wrapper_address: Address = env.storage().instance().get(&DataKey::XlmWrapper).unwrap();
            let token_client = token::Client::new(&env, &xlm_wrapper_address);

            token_client.transfer(&env.current_contract_address(), &participant_address, &entry_fee);

            // decrementa pool
            let mut pool: i128 = env.storage().instance().get(&DataKey::Pool).unwrap();
            pool = pool - entry_fee;
            env.storage().instance().set(&DataKey::Pool, &pool);
        } else {
            panic!("Participant not found");
        }
    }

    pub fn distribute_prizes(env: Env, leaderboard: Vec<Symbol>) {
        let admin: Address = env.storage().instance().get(&DataKey::Admin).unwrap();
        admin.require_auth();

        env.storage().instance().set(&DataKey::IsActive, &false);

        let participants: Map<Symbol, Address> = env.storage().instance().get(&DataKey::Participants).unwrap();
        let payout_rules: Vec<u32> = env.storage().instance().get(&DataKey::PayoutRules).unwrap();
        let contract_address = env.current_contract_address();

        // usa pool armazenado em storage (evita depender de ledger API)
        let mut total_prize_pool: i128 = env.storage().instance().get(&DataKey::Pool).unwrap();

        let xlm_wrapper_address: Address = env.storage().instance().get(&DataKey::XlmWrapper).unwrap();
        let token_client = token::Client::new(&env, &xlm_wrapper_address);

        let mut pool_rank: u32 = 0;

        for username in leaderboard.iter() {
            if pool_rank >= payout_rules.len() {
                break;
            }

            if let Some(winner_address) = participants.get(username) {
                let payout_percentage = payout_rules.get(pool_rank).unwrap();
                // payout_percentage é em basis points (ex.: 2500 = 25.00%)
                let payout_amount = (total_prize_pool * payout_percentage as i128) / 10000;

                if payout_amount > 0 {
                    token_client.transfer(&contract_address, &winner_address, &payout_amount);
                    // diminui pool
                    total_prize_pool = total_prize_pool - payout_amount;
                }
                pool_rank += 1;
            }
        }

        // atualiza pool no storage
        env.storage().instance().set(&DataKey::Pool, &total_prize_pool);
    }

    pub fn refund_all(env: Env) {
        let is_active: bool = env.storage().instance().get(&DataKey::IsActive).unwrap();
        if !is_active {
            panic!("Competition is not active");
        }

        let deadline: u64 = env.storage().instance().get(&DataKey::Deadline).unwrap();
        let min_participants: u32 = env.storage().instance().get(&DataKey::MinParticipants).unwrap();
        let participants: Map<Symbol, Address> = env.storage().instance().get(&DataKey::Participants).unwrap();
        let entry_fee: i128 = env.storage().instance().get(&DataKey::EntryFee).unwrap();
        let current_timestamp = env.ledger().timestamp();

        if current_timestamp > deadline && participants.len() < min_participants {
            // Fecha a competição
            env.storage().instance().set(&DataKey::IsActive, &false);

            // Prepara o cliente do token
            let xlm_wrapper_address = Address::from_string(
                &"CDLZXA64VFPATL2I4QN5VTO762U2AF2L66ZNFP3H34N3G45B3SGH4YTR"
            );
            let token_client = token::Client::new(&env, &xlm_wrapper_address);
            let contract_address = env.current_contract_address();

            // Envia o refund para todos os participantes
            for (_username, participant_address) in participants.iter() {
                token_client.transfer(
                    &contract_address,
                    &participant_address,
                    &entry_fee
                );
            }
        } else {
            panic!("Refund conditions not met");
        }
    }

}
