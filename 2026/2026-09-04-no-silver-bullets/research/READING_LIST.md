# Research Reading List

## Core References

### 1. Tensor Networks & Lattice Factoring
* **Reference**: Marco Tesoro, Ilaria Siloi, Daniel Jaschke, Giuseppe Magnifico, Simone Montangero. *Integer factorization via tensor-network Schnorr's sieving.* Physical Review A 113, 032418 (11 March 2026). DOI: [10.1103/PhysRevA.113.032418](https://doi.org/10.1103/PhysRevA.113.032418).
* **Relevance**: Modern computational substrate applied to Schnorr-style lattice factorization; demonstrations up to 100 bits and scaling analysis through 130 bits.

### 2. Record-Scale Number Field Sieve
* **Reference**: Fabrice Boudot, Pierrick Gaudry, Aurore Guillevic, Nadia Heninger, Emmanuel Thomé, Paul Zimmermann. *Comparing the difficulty of factorization and discrete logarithm: a 240-digit experiment.* 2020.
* **Relevance**: State-of-the-art GNFS implementation (CADO-NFS) and empirical cost analysis on RSA-240 and RSA-250.

### 3. Polynomial Selection & Smoothness
* **Reference**: Brian Antony Murphy. *Polynomial Selection for the Number Field Sieve Integer Factorisation Algorithm.* PhD thesis, Australian National University, 1999.
* **Relevance**: Formalization of polynomial quality, $\alpha$ and $E$ smoothness metrics; theoretical foundation for why algebraic representation changes relation yields.
* **Reference**: Shi Bai. *Polynomial selection for the number field sieve.* PhD thesis, Australian National University, 2011.
* **Relevance**: Root optimization, size optimization, and modern lattice-based polynomial generation.

### 4. Partial Information & Small Roots
* **Reference**: Don Coppersmith. *Small solutions to polynomial equations, and low exponent RSA vulnerabilities.* Journal of Cryptology, 1997.
* **Relevance**: Rigorous small-root lattice methods recovering full prime factors from partial MSB/LSB knowledge.
* **Reference**: *Improved Results on Factoring General RSA Moduli with Partial Key Exposure.* (Survey & extensions, 2018).
* **Relevance**: Mathematical bounds on non-contiguous and fragmented partial factor exposure.

### 5. Constraint Encodings & SAT Solvers
* **Reference**: Michele Mosca, Sebastian R. Verschoor. *Factoring semi-primes with (quantum) SAT-solvers.* Scientific Reports 12, 7982 (2022).
* **Relevance**: Direct reduction of integer multiplication to SAT; benchmarks and empirical complexity barriers.

### 6. Automated Algorithm Discovery
* **Reference**: Alexander Novikov et al. *AlphaEvolve: A coding agent for scientific and algorithmic discovery.* 2025 / 2026.
* **Relevance**: Architecture for code mutation with exact machine-verifiable evaluation and evolutionary selection.

---

## Analytical Reading Questions

For each research paper explored:
1. What mathematical representation of factoring is employed?
2. Where is the computational bottleneck located?
3. Which parameter choices were historically hand-designed or chosen by rule of thumb?
4. Which stage now possesses a cheap, machine-verifiable evaluator?
5. Which assumptions were driven by legacy hardware or memory constraints?
6. Which components can be systematically explored via automated search?
7. What minimal synthetic benchmark would falsify the idea quickly?
