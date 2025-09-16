#![no_std]
use soroban_sdk::{
    contract, contractimpl, contracttype, Address, Env, Vec, BytesN, Symbol, IntoVal
};

// Enumeração para as chaves de armazenamento da fábrica.
#[contracttype]
#[derive(Clone)]
pub enum DataKey {
    Admin,
    WasmHash,
    Competitions,
}

#[contract]
pub struct CompetitionFactory;

#[contractimpl]
impl CompetitionFactory {
    pub fn initialize(env: Env, admin: Address, wasm_hash: BytesN<32>) {
        if env.storage().instance().has(&DataKey::Admin) {
            panic!("Factory already initialized");
        }
        env.storage().instance().set(&DataKey::Admin, &admin);
        env.storage().instance().set(&DataKey::WasmHash, &wasm_hash);
        env.storage().instance().set(&DataKey::Competitions, &Vec::<Address>::new(&env));
    }

    pub fn create_competition(
        env: Env,
        comp_admin: Address,
        entry_fee: i128,
        payout_rules: Vec<u32>,
        deadline: u64,
        min_participants: u32,
    ) -> Address {
        let wasm_hash: BytesN<32> = env.storage().instance().get(&DataKey::WasmHash).unwrap();

        let mut competitions: Vec<Address> =
            env.storage().instance().get(&DataKey::Competitions).unwrap();
        let salt = BytesN::from_array(&env, &[competitions.len() as u8; 32]);

        let new_contract_address = env
            .deployer()
            .with_current_contract(salt)
            .deploy_v2(wasm_hash, ());

        // Call initialize function using raw contract invocation
        let _ = env.invoke_contract::<()>(
            &new_contract_address,
            &Symbol::new(&env, "initialize"),
            (comp_admin, entry_fee, payout_rules, deadline, min_participants).into_val(&env),
        );

        competitions.push_back(new_contract_address.clone());
        env.storage().instance().set(&DataKey::Competitions, &competitions);

        new_contract_address
    }

    pub fn get_competitions(env: Env) -> Vec<Address> {
        env.storage().instance().get(&DataKey::Competitions).unwrap()
    }
}