# Section 5: Comparative Analysis

Table 1 summarizes the architectural paradigms of Zk-Vote in comparison to prominent decentralized voting protocols.

### Table 1: Protocol Comparison

| Protocol | Cryptographic Primitive | Trusted Setup | Proof System | Verification Layer | Quantum Resistance |
|----------|-------------------------|---------------|--------------|--------------------|--------------------|
| **Zk-Vote (Ours)** | **Deterministic Nullifier** | **None** | **ZK-STARK** | **Starknet L2 (Cairo)** | **Post-Quantum Candidate** |
| Semaphore | zk-SNARK Identity | Required (Groth16/Plonk) | zk-SNARK | Ethereum L1 (EVM) | Vulnerable |
| MACI | EVM Anti-Collusion | None | None (Public Key Crypto) | Ethereum L1 (EVM) | Vulnerable |
| Vocdoni | Custom Sidechain | None | zk-SNARK (Circom) | Vocdoni L1 | Vulnerable |

### Discussion

#### 5.1 Proof System Selection
Zk-Vote utilizes ZK-STARKs over the ubiquitous zk-SNARKs used by Semaphore. This decision yields two primary academic benefits:
1. **Trusted Setup Elimination:** STARKs rely solely on collision-resistant hash functions (e.g., Poseidon, Blake2b), completely bypassing the toxic waste problem associated with SNARK trusted setups.
2. **Post-Quantum Security:** Unlike elliptic-curve cryptography (ECC) which is theoretically vulnerable to Shor's algorithm on a quantum computer, STARKs are currently considered quantum-resistant.

#### 5.2 Verification Environment Constraints
Executing a Groth16 verification on the EVM (e.g., Semaphore) costs approximately 250,000 to 300,000 gas. Given Ethereum's block limits, this places a hard upper bound on voting throughput. 
By migrating verification to Starknet's Cairo VM, Zk-Vote offloads the computational heavy lifting to an execution layer specifically optimized for polynomial evaluation and algebraic operations. As demonstrated in our benchmarks (Section 6), this drastically reduces the per-voter cost footprint.

#### 5.3 Deterministic Nullification vs Anti-Collusion
While MACI (Minimum Anti-Collusion Infrastructure) provides strong bribery resistance by allowing voters to override their previous votes, it requires a trusted centralized coordinator to tally the results and execute the overrides. Zk-Vote trades anti-collusion properties for absolute decentralization. By employing deterministic nullifiers, the vote tally is instantly verifiable on-chain without any central coordinator.
