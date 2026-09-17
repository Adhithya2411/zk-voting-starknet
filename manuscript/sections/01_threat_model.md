# Section 4: Formal Threat Model and Security Proof Sketches

In this section, we define the adversarial capabilities and present proof sketches demonstrating the security properties of the Zk-Vote protocol under the Starknet Layer-2 architecture. We operate in the standard cryptographic model where the adversary $\mathcal{A}$ has bounded polynomial-time computational capabilities.

## 4.1 Double-Voting Adversary

**Definition (Double-Voting Resistance):** A voting protocol is double-voting resistant if the probability that an adversary $\mathcal{A}$ can successfully cast two valid ballots tied to the same identity commitment is negligible in the security parameter $\lambda$.

**Proof Sketch:**
Our protocol enforces the generation of a deterministic nullifier defined as:
$$ \text{Nullifier}_i = \text{PoseidonHash}(\text{VoterSecret}_i, \text{ElectionID}) $$

Assume an adversary $\mathcal{A}$ attempts to submit two ballots $B_1$ and $B_2$ for the same $\text{VoterSecret}_i$. 
1. By the deterministic property of the Poseidon hash function, both submissions will independently yield $\text{Nullifier}_{B1} = \text{Nullifier}_{B2}$.
2. The Starknet Cairo contract enforces a strictly monotonic state transition in the `nullifier_registry`.
3. If $B_1$ is processed at block height $h_1$, $\text{used\_nullifiers}[\text{Nullifier}_{B1}]$ transitions from `false` to `true`.
4. When $B_2$ is processed at height $h_2 \ge h_1$, the assertion `assert(!used_nullifiers[n])` will deterministically fail. 
Thus, $\mathcal{A}$ can only bypass this if they can find a hash collision in Poseidon where $\text{Poseidon}(S_i, E) = \text{Poseidon}(S_j, E)$ for $S_i \neq S_j$. Under the standard collision-resistance assumption of Poseidon, this probability is negligible.

## 4.2 Deanonymization Attack

**Definition (Anonymity):** A voting protocol provides anonymity if no polynomial-time adversary can link a submitted ballot to a specific registered voter commitment with a probability significantly greater than $1/N$, where $N$ is the size of the eligible voter set.

**Proof Sketch:**
In standard EVM environments (e.g., Ethereum Layer-1), transaction origination (the `msg.sender`) leaks metadata. Zk-Vote leverages Starknet's native Account Abstraction (AA) to mitigate this.
1. The ballot payload $P = (\text{Nullifier}, \pi_{zk}, \text{EncVote})$ contains no identifying data. The proof $\pi_{zk}$ is a Zero-Knowledge STARK proving membership in the Merkle root without revealing the specific leaf path.
2. Under Starknet's AA, the transaction can be submitted by *any* relayer account paying the gas fee, completely decoupling the executing identity from the cryptographic voter identity. 
Therefore, unless the relayer itself is compromised and leaks IP/metadata, the on-chain payload is information-theoretically decoupled from the voter's real-world identity.

## 4.3 Front-Running and Calldata Hijacking

**Definition (Non-Malleability):** An adversary observing a pending transaction in the mempool cannot alter the vote choice or hijack the proof to cast a vote on behalf of the victim.

**Security Boundary:** 
If the proof $\pi_{zk}$ is purely a membership proof, an observer could potentially copy the valid $\pi_{zk}$ and $\text{Nullifier}$, change the `hidden_vote` parameter, and front-run the transaction with a higher gas fee. 
To prevent this, the Zk-Vote architecture conceptually binds the ballot payload to the proof. While the current implementation separates `hidden_vote` from the nullifier for simplicity in the prototype, production deployments enforce that the zero-knowledge circuit outputs a hash of the vote selection, ensuring any mutation of the calldata immediately invalidates $\pi_{zk}$.
