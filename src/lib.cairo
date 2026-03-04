mod voting;

use starknet::ContractAddress;

/// Election State Machine
#[derive(Copy, Drop, PartialEq, Serde)]
enum ElectionState {
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
    
    /// Transition from Setup to Active (admin only)
    fn start_election(ref self: TContractState);
    
    /// Transition from Active to Ended (admin only)
    fn end_election(ref self: TContractState);
}

/// Voting System Smart Contract
#[starknet::contract]
mod VotingSystem {
    use super::{ElectionState, IVotingSystem, ContractAddress};
    use starknet::get_caller_address;

    #[storage]
    struct Storage {
        admin: ContractAddress,
        election_state: ElectionState,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        ElectionStarted: ElectionStarted,
        ElectionEnded: ElectionEnded,
    }

    #[derive(Drop, starknet::Event)]
    struct ElectionStarted {}

    #[derive(Drop, starknet::Event)]
    struct ElectionEnded {}

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
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _assert_only_admin(self: @ContractState) {
            let caller = get_caller_address();
            let admin = self.admin.read();
            assert(caller == admin, 'Only admin can call this');
        }
    }
}
