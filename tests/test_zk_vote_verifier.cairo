use zk_voting_starknet::zk_vote_verifier::{IZkVoteVerifierDispatcher, IZkVoteVerifierDispatcherTrait};
use snforge_std::{declare, ContractClassTrait};

fn deploy_verifier() -> IZkVoteVerifierDispatcher {
    let contract = declare("ZkVoteVerifier").unwrap();
    let (contract_address, _) = contract.deploy(@ArrayTrait::new()).unwrap();
    IZkVoteVerifierDispatcher { contract_address }
}

#[test]
#[should_panic(expected: ('Election is not active',))]
fn test_vote_fails_if_inactive() {
    let verifier = deploy_verifier();
    
    // By default is_active is false in storage.
    let leaf = 123;
    let mut proof = ArrayTrait::new();
    proof.append(456);
    let nullifier = 789;
    let hidden_vote = 1;
    
    verifier.cast_vote(leaf, proof, nullifier, hidden_vote);
}
