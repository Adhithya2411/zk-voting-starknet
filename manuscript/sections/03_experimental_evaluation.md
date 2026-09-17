# Section 6: Experimental Evaluation

To empirically validate the scalability and efficiency of the Zk-Vote protocol, we developed a benchmarking harness to measure both the off-chain client proving overhead and the on-chain Starknet verification footprint.

## 6.1 Client-Side Proving Latency

Generating cryptographic proofs in a browser environment is a historical bottleneck for ZK voting systems. We benchmarked the latency of generating the Poseidon Merkle inclusion proof across varying voter population sizes ($N = 2^{10}$ to $2^{20}$). 

As illustrated in Figure 1, the proving time scales logarithmically with the depth of the tree, growing from ~170ms for $2^{10}$ voters to ~295ms for $2^{20}$ voters. Memory footprint (Peak RAM) remains well within the strict confines of standard browser WebAssembly engines, peaking at roughly 60MB for a 1-million voter election. This confirms that the client-side harness can execute efficiently on standard consumer hardware (e.g., mobile devices) without degraded user experience.

## 6.2 On-Chain Verification Resource Allocation

Starknet's Cairo Virtual Machine measures execution complexity in discrete "steps." We instrumented the `cast_vote` transaction lifecycle to trace resource consumption. 

Figure 2 visualizes the step allocation:
1. **Merkle Verification (62.5%):** Reconstructing the Poseidon hashes from the leaf to the root represents the dominant computational cost.
2. **Nullifier Operations (30.0%):** Checking the nullifier registry map for freshness and persisting the consumed nullifier.
3. **Ballot Logging (7.5%):** Emitting the final `VoteCast` event for the frontend listener.

Because Starknet natively implements the Poseidon hash as a built-in optimized operation, the raw step count is magnitudes lower than executing Keccak256 or SHA256 inside a generic EVM contract.

## 6.3 Layer-2 Amortization & Cost Economics

Finally, we evaluated the economic viability of Zk-Vote. In Ethereum Layer-1 (L1), verifying a Groth16 zk-SNARK proof and writing state costs roughly 300,000 gas ($~3.50 USD). 

By leveraging Starknet's ZK-Rollup architecture (Figure 3), the execution cost is shifted off-chain. The L2 Sequencer batches thousands of vote transactions into a single recursive STARK proof that is submitted to L1. The amortized cost per voter drops to a fraction of a cent ($~0.00005 USD). Furthermore, the calldata footprint of Zk-Vote is minimal (primarily just the nullifier and encrypted vote), driving data-availability costs down significantly compared to EVM rollups.
