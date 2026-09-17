#[starknet::interface]
trait INullifierRegistry<TContractState> {
    fn register_nullifier(ref self: TContractState, nullifier: felt252);
    fn is_nullifier_used(self: @TContractState, nullifier: felt252) -> bool;
}

#[starknet::contract]
mod NullifierRegistry {
    use super::INullifierRegistry;
    use starknet::storage::{Map, StoragePointerReadAccess, StoragePointerWriteAccess, StoragePathEntry};

    #[storage]
    struct Storage {
        used_nullifiers: Map<felt252, bool>,
    }

    #[abi(embed_v0)]
    impl NullifierRegistryImpl of INullifierRegistry<ContractState> {
        fn register_nullifier(ref self: ContractState, nullifier: felt252) {
            let is_used = self.used_nullifiers.entry(nullifier).read();
            assert(!is_used, 'Nullifier already used');
            self.used_nullifiers.entry(nullifier).write(true);
        }

        fn is_nullifier_used(self: @ContractState, nullifier: felt252) -> bool {
            self.used_nullifiers.entry(nullifier).read()
        }
    }
}
