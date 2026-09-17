use zk_voting_starknet::nullifier_registry::{INullifierRegistryDispatcher, INullifierRegistryDispatcherTrait};
use snforge_std::{declare, ContractClassTrait};

fn deploy_nullifier_registry() -> INullifierRegistryDispatcher {
    let contract = declare("NullifierRegistry").unwrap();
    let (contract_address, _) = contract.deploy(@ArrayTrait::new()).unwrap();
    INullifierRegistryDispatcher { contract_address }
}

#[test]
fn test_register_nullifier() {
    let registry = deploy_nullifier_registry();
    let nullifier = 999888777;
    
    // Initially not used
    let is_used_init = registry.is_nullifier_used(nullifier);
    assert(!is_used_init, 'Should not be used initially');
    
    // Register it
    registry.register_nullifier(nullifier);
    
    // Check it's used
    let is_used_after = registry.is_nullifier_used(nullifier);
    assert(is_used_after, 'Should be used after register');
}

#[test]
#[should_panic(expected: ('Nullifier already used',))]
fn test_double_register_panic() {
    let registry = deploy_nullifier_registry();
    let nullifier = 111222333;
    
    registry.register_nullifier(nullifier);
    // This should panic
    registry.register_nullifier(nullifier);
}
