# Zero-Knowledge Voting System on Starknet

A fully decentralized, anonymous voting smart contract built for the Starknet ecosystem. This project leverages Zero-Knowledge (ZK) cryptography, specifically Merkle Trees and Poseidon hashing, to allow users to verify their voting eligibility without exposing their identity on-chain.

## 🏗️ Architecture & Core Features

This smart contract was developed in modern **Cairo (v2.16.0)** and is structured around three core architectural pillars:

### 1. State Machine & Role-Based Access Control (RBAC)
The election follows a strict, cryptographically enforced lifecycle:
* **`Setup`**: The designated Admin sets the Merkle Root containing all eligible voters.
* **`Active`**: The election begins, and users can submit their zero-knowledge proofs to cast votes.
* **`Ended`**: The election is finalized, and no further state changes can occur.
* **Security**: Only the Admin address can transition states or alter the Merkle root, protected by `_assert_only_admin()` checks.

### 2. Zero-Knowledge Proof Verification (Merkle Trees)
Instead of storing a public list of eligible addresses, the contract only stores a single `merkle_root`. 
* Voters generate a Merkle Proof off-chain.
* The contract verifies the proof on-chain using Starknet's native, highly efficient **Poseidon Hash** algorithm.
* The contract enforces strict array dereferencing and `u256` type conversions to ensure cryptographic ordering during hash reconstruction.

### 3. Double-Spend Prevention (Nullifier Registry)
To prevent the "double voting" problem inherent in anonymous systems, the contract utilizes a Cryptographic Nullifier.
* When a valid vote is cast, its unique `nullifier` is permanently recorded in a Starknet `Map`.
* Any subsequent attempt to use the same nullifier instantly triggers a transaction panic (`'Nullifier already used'`), ensuring the principle of "one person, one vote."

## 🛠️ Tech Stack
* **Language**: Cairo (v2.16.0)
* **Package Manager**: Scarb (v2.16.0)
* **Testing Framework**: Starknet Foundry (`snforge` v0.57.0)

## 🧪 Testing Suite
The repository includes a comprehensive, 100% passing integration test suite validating all core security mechanisms. 

Tests cover:
* Contract deployment and initial state validation.
* Successful zero-knowledge vote casting.
* Prevention of double-voting (Nullifier collision panics).
* Rejection of votes cast outside the `Active` phase.
* Strict RBAC enforcement for Admin-only functions.

### How to Run the Tests
Ensure you have the Rust toolchain and Starknet Foundry installed, then execute:
```bash
snforge test