#![no_std]
use soroban_sdk::{contract, contractimpl, symbol_short, vec, token, Address, Env, Map, Symbol, Vec};

#[derive(Clone)]
#[contract]
pub enum DataKey {
    Admin,
    EntryFee,
    PayoutRules,
    Participants,
    IsActive,
    Deadline,
    MinParticipants,
}

#[contract]
pub struct CompetitionContract;

#[contractimpl]
impl CompetitionContract {
    pub fn initialize(
        env: Env, 
        admin: Address, 
        entry_fee: i128, 
        payout_rules: Vec<u32>,
        deadline: u64,
        min_participants: u32,
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
    }

    pub fn join(env: Env, participant: Address, username: Symbol) {
        participant.require_auth();

        let is_active: bool = env.storage().instance().get(&DataKey::IsActive).unwrap();
        if !is_active {
            panic!("Competition is closed");
        }

        let mut participants: Map<Symbol, Address> = env.storage().instance().get(&DataKey::Participants).unwrap();
        if participants.contains_key(username.clone()) {
            panic!("Username already registered");
        }
        participants.set(username, participant);
        env.storage().instance().set(&DataKey::Participants, &participants);
    }

    pub fn withdraw(env: Env, participant_address: Address) {
        participant_address.require_auth();

        let is_active: bool = env.storage().instance().get(&DataKey::IsActive).unwrap();
        if !is_active {
            panic!("Competition is not active");
        }

        let mut participants: Map<Symbol, Address> = env.storage().instance().get(&DataKey::Participants).unwrap();
        let entry_fee: i128 = env.storage().instance().get(&DataKey::EntryFee).unwrap();

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

            let xlm_wrapper_address = Address::from_string(
                &"CDLZXA64VFPATL2I4QN5VTO762U2AF2L66ZNFP3H34N3G45B3SGH4YTR"
            );
            let token_client = token::Client::new(&env, &xlm_wrapper_address);

            token_client.transfer(
                &env.current_contract_address(),
                &participant_address,
                &entry_fee
            );
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
        let total_prize_pool = env.ledger().get_balance(&contract_address);
        let mut pool_rank: u32 = 0;

        for username in leaderboard.iter() {
            if pool_rank >= payout_rules.len() {
                break;
            }

            if let Some(winner_address) = participants.get(username) {
                let payout_percentage = payout_rules.get(pool_rank).unwrap();
                let payout_amount = (total_prize_pool * payout_percentage as i128) / 10000;

                if payout_amount > 0 {
                    let xlm_wrapper_address = Address::from_string(
                        &"CDLZXA64VFPATL2I4QN5VTO762U2AF2L66ZNFP3H34N3G45B3SGH4YTR"
                    );
                    let token_client = token::Client::new(&env, &xlm_wrapper_address);

                    token_client.transfer(
                        &contract_address,
                        &winner_address,
                        &payout_amount
                    );
                }
                pool_rank += 1;
            }
        }
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
            env.storage().instance().set(&DataKey::IsActive, &false);

            let KEEPER_REWARD: i128 = 1_000_000;
            let caller = env.invoker();
            let xlm_wrapper_address = Address::from_string(
                &"CDLZXA64VFPATL2I4QN5VTO762U2AF2L66ZNFP3H34N3G45B3SGH4YTR"
            );
            let token_client = token::Client::new(&env, &xlm_wrapper_address);
            let contract_address = env.current_contract_address();
            
            token_client.transfer(&contract_address, &caller, &KEEPER_REWARD);

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