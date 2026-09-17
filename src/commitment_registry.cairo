#[starknet::interface]
trait ICommitmentRegistry<TContractState> {
    fn set_merkle_root(ref self: TContractState, root: felt252);
    fn get_merkle_root(self: @TContractState) -> felt252;
}

#[starknet::contract]
mod CommitmentRegistry {
    use super::ICommitmentRegistry;
    use starknet::ContractAddress;

    #[storage]
    struct Storage {
        merkle_root: felt252,
    }

    #[abi(embed_v0)]
    impl CommitmentRegistryImpl of ICommitmentRegistry<ContractState> {
        fn set_merkle_root(ref self: ContractState, root: felt252) {
            self.merkle_root.write(root);
        }

        fn get_merkle_root(self: @ContractState) -> felt252 {
            self.merkle_root.read()
        }
    }
}
