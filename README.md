# 🗳️ Zero-Knowledge Voting System on Starknet

**Course:** BCSE324L - Blockchain Implementation & Seminar
**Platform:** Starknet (Cairo v2.16.0)

---

## 🌟 Project Overview

This project is a decentralized, privacy-preserving voting application. By leveraging Zero-Knowledge (ZK) STARKs and Merkle Tree structures, it allows eligible voters to cast ballots anonymously. The system ensures that while the validity of a vote is cryptographically proven, the identity of the voter remains decoupled from their selection.

### The Problem

Traditional electronic voting systems often force a trade-off between **privacy** (anonymity) and **integrity** (preventing double-voting).

### The Solution

By using a **Cryptographic Nullifier** and **on-chain Merkle Verification**, this system achieves both. Voters prove they belong to an "Eligible Set" without revealing who they are, while the blockchain ensures no single "Identity Commitment" can vote twice.

---

## 🚀 Why Starknet (Cairo)?

Per the course requirements to avoid Ethereum/EVM-based solutions, Starknet was selected for the following strategic reasons:

- **ZK-Native Infrastructure:** Starknet is a ZK-Rollup. Unlike general-purpose chains, its Virtual Machine (Cairo VM) is specifically optimized for generating and verifying algebraic proofs.

- **Computational Efficiency:** We utilize the **Poseidon Hash**, which is significantly more gas-efficient for ZK-STARKs than standard Keccak or SHA-256 hashes used in EVM.

- **Account Abstraction (AA):** Starknet's native AA allows for complex voting logic to be handled at the protocol level, enabling a smoother "Sign & Cast" user experience via Argent X.

---

## 🏗️ Technical Architecture

### 1. Cryptographic Proof System

The system utilizes a **Merkle Tree** architecture to manage voter eligibility:

- **Membership Proof:** Eligible voter addresses are hashed into a Merkle Tree. Only the Merkle Root is stored on-chain.
- **Verification:** During the `cast_vote` call, the contract reconstructs the path from the provided leaf to the root. If the hashes match, the vote is authenticated.

### 2. Double-Voting Prevention (Nullifiers)

To maintain anonymity, we do not track *who* voted. Instead, we track a **Nullifier** — a deterministic, unique hash generated during the voting process.

- Once a nullifier is used, it is added to a persistent `Map` on-chain.
- Any attempt to reuse a nullifier results in an immediate transaction revert: `'Nullifier already used'`.

### 3. Election State Machine

The contract enforces a strict operational lifecycle:

| State | Description |
|-------|-------------|
| **Setup** | Admin initializes the election parameters and the Merkle Root. |
| **Active** | The window where `cast_vote` is enabled. |
| **Ended** | Permanent state where no further ballots can be cast, ensuring finality. |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Smart Contract | Cairo v2.16.0 (Starknet) |
| Frontend | Django (Python 3.10) & Vanilla JS |
| Wallet Integration | Argent X (Starknet Sepolia) |
| Development Tools | Scarb, Starkli, Starknet Foundry (`snforge`) |

---

## 🧪 Testing & Verification

The project includes a **100% passing test suite** using Starknet Foundry.

### Running Local Tests

```bash
# Compile the contract
scarb build

# Run the cryptographic verification tests
snforge test
```

### Test Cases Covered

- ✅ Successful ZK-Proof authentication.
- ✅ Rejection of unauthorized (non-admin) state changes.
- ✅ Validation of the Nullifier registry (Double-vote prevention).
- ✅ State-transition enforcement (Voting only allowed in Active phase).

---

## 🖥️ Live Demo Instructions (Sepolia Testnet)

To run the full-stack application locally:

**1. Start the Backend:**
```bash
python manage.py runserver
```

**2. Access the Dashboard:**
Navigate to `http://127.0.0.1:8000/api/voting/`

**3. Connect Wallet:**
Use the **Argent X** browser extension.
> ⚠️ Note: Ensure the wallet is set to the **Sepolia Testnet**.

**4. Cast Ballot:**
Select a candidate. The frontend will generate the required cryptographic parameters and prompt a wallet signature.

**5. Verify on Starkscan:**
Upon success, a transaction hash will be provided. You can verify the execution live on the Starknet block explorer.

---

## 👥 Team Information

| Field | Details |
|-------|---------|
| **Name** | Adhithya Singa Narendran |
| **Registration Number** | 23BKT0146 |
| **Branch** | CSE (Blockchain Technology) |
| **Institution** | Vellore Institute of Technology (VIT), Vellore |