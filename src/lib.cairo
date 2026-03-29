use starknet::ContractAddress;

/// Election State Machine
#[derive(Copy, Drop, PartialEq, Serde, starknet::Store)]
enum ElectionState {
    #[default]
    Setup: (),
    Active: (),
    Ended: (),
}

/// Voting System Interface
#[starknet::interface]
trait IVotingSystem<TContractState> {
    /// Get current election state
    fn get_election_state(self: @TContractState) -> ElectionState;
    
    /// Get the current admin address
    fn get_admin(self: @TContractState) -> ContractAddress;
    
    /// Set merkle root for eligible voters (admin only, Setup phase only)
    fn set_merkle_root(ref self: TContractState, root: felt252);
    
    /// Transition from Setup to Active (admin only)
    fn start_election(ref self: TContractState);
    
    /// Transition from Active to Ended (admin only)
    fn end_election(ref self: TContractState);
    
    /// Cast a vote with merkle proof, nullifier and hidden vote (Active phase only)
    fn cast_vote(ref self: TContractState, leaf: felt252, proof: Array<felt252>, nullifier: felt252, hidden_vote: felt252);
}

/// Voting System Smart Contract
#[starknet::contract]
mod VotingSystem {
    use super::{ElectionState, IVotingSystem, ContractAddress};
    use starknet::get_caller_address;
    use core::poseidon::PoseidonTrait;
    use core::hash::HashStateTrait;
    use starknet::storage::{Map, StoragePointerReadAccess, StoragePointerWriteAccess, StoragePathEntry};

    #[storage]
    struct Storage {
        admin: ContractAddress,
        election_state: ElectionState,
        merkle_root: felt252,
        used_nullifiers: Map<felt252, bool>,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        ElectionStarted: ElectionStarted,
        ElectionEnded: ElectionEnded,
        VoteCasted: VoteCasted,
    }

    #[derive(Drop, starknet::Event)]
    struct ElectionStarted {}

    #[derive(Drop, starknet::Event)]
    struct ElectionEnded {}

    #[derive(Drop, starknet::Event)]
    struct VoteCasted {
        nullifier: felt252,
        hidden_vote: felt252,
    }

    #[constructor]
    fn constructor(ref self: ContractState, admin: ContractAddress) {
        self.admin.write(admin);
        self.election_state.write(ElectionState::Setup(()));
    }

    #[abi(embed_v0)]
    impl VotingSystemImpl of IVotingSystem<ContractState> {
        fn get_election_state(self: @ContractState) -> ElectionState {
            self.election_state.read()
        }

        fn get_admin(self: @ContractState) -> ContractAddress {
            self.admin.read()
        }

        fn set_merkle_root(ref self: ContractState, root: felt252) {
            self._assert_only_admin();
            let current_state = self.election_state.read();
            assert(current_state == ElectionState::Setup(()), 'Merkle root Setup only');
            
            self.merkle_root.write(root);
        }

        fn start_election(ref self: ContractState) {
            self._assert_only_admin();
            let current_state = self.election_state.read();
            assert(current_state == ElectionState::Setup(()), 'Election already started');
            
            self.election_state.write(ElectionState::Active(()));
            self.emit(Event::ElectionStarted(ElectionStarted {}));
        }

        fn end_election(ref self: ContractState) {
            self._assert_only_admin();
            let current_state = self.election_state.read();
            assert(current_state == ElectionState::Active(()), 'Election not active');
            
            self.election_state.write(ElectionState::Ended(()));
            self.emit(Event::ElectionEnded(ElectionEnded {}));
        }

        fn cast_vote(ref self: ContractState, leaf: felt252, proof: Array<felt252>, nullifier: felt252, hidden_vote: felt252) {
            let current_state = self.election_state.read();
            assert(current_state == ElectionState::Active(()), 'Election is not active');
            
            let is_valid_proof = self._verify_merkle_proof(leaf, proof);
            assert(is_valid_proof, 'Invalid Merkle Proof');
            
            let already_voted = self.used_nullifiers.entry(nullifier).read();
            assert(!already_voted, 'Nullifier already used');
            
            self.used_nullifiers.entry(nullifier).write(true);
            self.emit(Event::VoteCasted(VoteCasted { nullifier, hidden_vote }));
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _assert_only_admin(self: @ContractState) {
            let caller = get_caller_address();
            let admin = self.admin.read();
            assert(caller == admin, 'Only admin can call this');
        }

        fn _verify_merkle_proof(self: @ContractState, leaf: felt252, proof: Array<felt252>) -> bool {
            let mut current_hash = leaf;
            let stored_root = self.merkle_root.read();
            
            let mut i = 0;
            loop {
                if i >= proof.len() {
                    break;
                }
                
                let proof_element = *proof.at(i);
                
                let current_hash_u256: u256 = current_hash.into();
                let proof_element_u256: u256 = proof_element.into();
                
                // Ensure consistent ordering: smaller value first
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