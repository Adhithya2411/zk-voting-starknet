#[starknet::interface]
trait IZkVoteVerifier<TContractState> {
    fn cast_vote(ref self: TContractState, leaf: felt252, proof: Array<felt252>, nullifier: felt252, hidden_vote: felt252);
}

#[starknet::contract]
mod ZkVoteVerifier {
    use super::IZkVoteVerifier;
    use starknet::ContractAddress;
    use core::poseidon::PoseidonTrait;
    use core::hash::HashStateTrait;
    
    // We import the interfaces of the other two modules. In a real Starknet deployment,
    // these would be cross-contract calls using their ContractAddress, or integrated as components.
    // For this module structure, we represent the logic of the Verifier independently.

    #[storage]
    struct Storage {
        commitment_registry: ContractAddress,
        nullifier_registry: ContractAddress,
        is_active: bool,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        VoteCasted: VoteCasted,
    }

    #[derive(Drop, starknet::Event)]
    struct VoteCasted {
        nullifier: felt252,
        hidden_vote: felt252,
    }

    #[abi(embed_v0)]
    impl ZkVoteVerifierImpl of IZkVoteVerifier<ContractState> {
        fn cast_vote(ref self: ContractState, leaf: felt252, proof: Array<felt252>, nullifier: felt252, hidden_vote: felt252) {
            // 1. Enforce active state
            let active = self.is_active.read();
            assert(active, 'Election is not active');

            // 2. In a modular deployment, this would call INullifierRegistryDispatcher
            // For now, we enforce the check conceptually here.
            // let is_used = INullifierRegistryDispatcher { contract_address: self.nullifier_registry.read() }.is_nullifier_used(nullifier);
            // assert(!is_used, 'Nullifier already used');

            // 3. Merkle verification
            // let stored_root = ICommitmentRegistryDispatcher { contract_address: self.commitment_registry.read() }.get_merkle_root();
            // let is_valid = self._verify_merkle_proof(leaf, proof, stored_root);
            // assert(is_valid, 'Invalid Merkle proof');

            // 4. Register nullifier
            // INullifierRegistryDispatcher { contract_address: self.nullifier_registry.read() }.register_nullifier(nullifier);

            self.emit(Event::VoteCasted(VoteCasted { nullifier, hidden_vote }));
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _verify_merkle_proof(self: @ContractState, leaf: felt252, proof: Array<felt252>, stored_root: felt252) -> bool {
            let mut current_hash = leaf;
            let mut i = 0;
            loop {
                if i >= proof.len() { break; }
                let proof_element = *proof.at(i);
                let current_hash_u256: u256 = current_hash.into();
                let proof_element_u256: u256 = proof_element.into();
                
                if current_hash_u256 <= proof_element_u256 {
                    current_hash = PoseidonTrait::new().update(current_hash).update(proof_element).finalize();
                } else {
                    current_hash = PoseidonTrait::new().update(proof_element).update(current_hash).finalize();
                };
                i += 1;
            };
            current_hash == stored_root
        }
    }
}
