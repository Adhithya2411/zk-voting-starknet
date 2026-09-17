use zk_voting_starknet::commitment_registry::{ICommitmentRegistryDispatcher, ICommitmentRegistryDispatcherTrait};
use snforge_std::{declare, ContractClassTrait};

fn deploy_registry() -> ICommitmentRegistryDispatcher {
    let contract = declare("CommitmentRegistry").unwrap();
    let (contract_address, _) = contract.deploy(@ArrayTrait::new()).unwrap();
    ICommitmentRegistryDispatcher { contract_address }
}

#[test]
fn test_set_and_get_merkle_root() {
    let registry = deploy_registry();
    let new_root = 123456789;
    
    registry.set_merkle_root(new_root);
    
    let fetched_root = registry.get_merkle_root();
    assert(fetched_root == new_root, 'Merkle root mismatch');
}
