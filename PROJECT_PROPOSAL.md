# Project Proposal: Zero-Knowledge (ZK) Proof Voting System

## 1. Team Info
* **Adhithya Singa Narendran** - Solo Developer (Full-Stack Web3 & ZK Architecture)

## 2. Selected Blockchain Platform
**Starknet (Cairo)**

*Rationale:* Starknet was selected as the foundational Layer 2 network due to its native architecture as a Validity (ZK) Rollup. By leveraging the Cairo programming language, the system achieves highly efficient on-chain cryptographic operations—specifically Poseidon hashing—which are strictly required for verifying zero-knowledge proofs securely and cost-effectively at scale.

## 3. Use Case / Problem Statement

**Problem:** Traditional blockchain voting systems expose voter choices on a public ledger, compromising privacy. Alternatively, centralized anonymous systems require trusting a central authority not to manipulate or censor the results.

**Solution:** A fully decentralized Zero-Knowledge Voting System.

**Target Audience:** Decentralized Autonomous Organizations (DAOs), university student councils, and corporate governance boards requiring cryptographically guaranteed privacy and verifiable integrity. Voters can mathematically prove their eligibility to vote without revealing their on-chain identity.

## 4. High-Level Architecture

* **Smart Contract Layer (Cairo):** A state-machine-driven Starknet contract enforcing Role-Based Access Control (RBAC) for the election administrator (Setup, Active, Ended phases).
* **Zero-Knowledge Identity Verification:** Uses an on-chain Merkle Root. Voters generate Merkle Proofs off-chain to prove inclusion in the eligible voter set without revealing their specific address.
* **Double-Spend Prevention (Nullifiers):** The contract maintains a cryptographic registry of "Nullifiers" (Map). Once a valid proof is verified, its unique nullifier is consumed, making double-voting mathematically impossible.
* **Off-Chain Prover & Frontend:** A Web3 frontend integrated with Starknet wallets (Argent X / Braavos) that generates the cryptographic proofs locally in the browser before submitting the transaction.

## 5. Timeline + Phases

* **Phase 1: Smart Contract Architecture & ZK Logic**
  * *Status:* **Completed.**
  * *Tasks:* Design Cairo 2.16 state machine, implement Poseidon hashing for Merkle verification, and create Nullifier registry.

* **Phase 2: Testnet Validation & Security Auditing**
  * *Status:* **Completed.**
  * *Tasks:* Build Foundry (`snforge`) integration suite testing RBAC panics, valid votes, and double-vote prevention. 

* **Phase 3: Off-Chain Cryptography & Prover Integration**
  * *Tasks:* Develop off-chain scripts to generate Merkle Trees from a list of eligible voters and format the ZK proofs for the Starknet transaction.

* **Phase 4: Frontend UI & Wallet Connection**
  * *Tasks:* Build the Django frontend, integrate Starknet.js for Argent/Braavos wallet connections, and finalize the end-to-end user voting flow.