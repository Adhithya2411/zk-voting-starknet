use starknet::ContractAddress;
use snforge_std::{declare, ContractClassTrait, DeclareResultTrait, start_cheat_caller_address, stop_cheat_caller_address};
use voting::{IVotingSystemDispatcher, IVotingSystemDispatcherTrait, ElectionState};
use core::poseidon::PoseidonTrait;
use core::hash::HashStateTrait;

/// Helper function to deploy the contract and return the dispatcher
fn setup_election() -> (IVotingSystemDispatcher, ContractAddress) {
    let admin: ContractAddress = 'admin'.try_into().unwrap();
    
    let contract = declare("VotingSystem").unwrap().contract_class();
    let mut calldata = array![admin.into()];
    let (contract_address, _) = contract.deploy(@calldata).unwrap();
    
    (IVotingSystemDispatcher { contract_address }, admin)
}

// ==========================================
// TEST 1: Core Setup & State Transitions
// ==========================================
#[test]
fn test_deployment_and_setup() {
    let (voting_system, admin) = setup_election();
    
    assert(voting_system.get_election_state() == ElectionState::Setup(()), 'Initial state should be Setup');
    assert(voting_system.get_admin() == admin, 'Admin should be set correctly');
    
    start_cheat_caller_address(voting_system.contract_address, admin);
    voting_system.set_merkle_root(0x123);
    voting_system.start_election();
    stop_cheat_caller_address(voting_system.contract_address);
    
    assert(voting_system.get_election_state() == ElectionState::Active(()), 'State should be Active');
}

// ==========================================
// TEST 2 & 3: ZK Voting & Double Vote Prevention
// ==========================================
#[test]
#[should_panic(expected: ('Nullifier already used', ))]
fn test_valid_vote_and_double_vote_panic() {
    let (voting_system, admin) = setup_election();
    let voter: ContractAddress = 'voter'.try_into().unwrap();

    let leaf = 0x1111;
    let proof_element = 0x2222;
    let valid_root = PoseidonTrait::new().update(leaf).update(proof_element).finalize(); 
    
    start_cheat_caller_address(voting_system.contract_address, admin);
    voting_system.set_merkle_root(valid_root);
    voting_system.start_election();
    stop_cheat_caller_address(voting_system.contract_address);

    start_cheat_caller_address(voting_system.contract_address, voter);
    
    let mut proof = array![proof_element];
    let nullifier = 0x9999;
    
    voting_system.cast_vote(leaf, proof.clone(), nullifier, 0x01);
    voting_system.cast_vote(leaf, proof, nullifier, 0x02);
    
    stop_cheat_caller_address(voting_system.contract_address);
}

// ==========================================
// TEST 4: State Machine Enforcement
// ==========================================
#[test]
#[should_panic(expected: ('Election is not active', ))]
fn test_vote_only_in_active_state() {
    let (voting_system, admin) = setup_election();
    let voter: ContractAddress = 'voter'.try_into().unwrap();
    
    start_cheat_caller_address(voting_system.contract_address, admin);
    voting_system.set_merkle_root(0xCCCC);
    stop_cheat_caller_address(voting_system.contract_address);
    
    // Election is still in Setup phase. Attempting to vote should panic.
    start_cheat_caller_address(voting_system.contract_address, voter);
    let mut proof = array![0x8888];
    voting_system.cast_vote(0x7777, proof, 0x9999, 0x01);
}

// ==========================================
// TEST 5: Role-Based Access Control (Merkle)
// ==========================================
#[test]
#[should_panic(expected: ('Only admin can call this', ))]
fn test_non_admin_cannot_set_merkle_root() {
    let (voting_system, _) = setup_election();
    let malicious_user: ContractAddress = 'hacker'.try_into().unwrap();
    
    start_cheat_caller_address(voting_system.contract_address, malicious_user);
    voting_system.set_merkle_root(0xDEAD);
}

// ==========================================
// TEST 6: Role-Based Access Control (State)
// ==========================================
#[test]
#[should_panic(expected: ('Only admin can call this', ))]
fn test_non_admin_cannot_start_election() {
    let (voting_system, _) = setup_election();
    let malicious_user: ContractAddress = 'hacker'.try_into().unwrap();
    
    start_cheat_caller_address(voting_system.contract_address, malicious_user);
    voting_system.start_election();
}