# 01 — Research Synthesis

## 1. Current Baseline

For large balanced semiprimes, the General Number Field Sieve (GNFS) remains the central classical baseline. The 2020 RSA-250 factorization used CADO-NFS and roughly 2,700 reference CPU core-years, with most effort in sieving and a smaller but still large sparse-linear-algebra stage.

This matters for experimental design: a new method need not immediately beat a full GNFS record. It can first demonstrate superiority on one bottleneck or a different scaling curve on controlled sizes.

---

## 2. Why Polynomial/Representation Search is Legitimate

NFS performance depends strongly on polynomial quality. Brian Murphy's work formalized polynomial-quality metrics and showed that polynomial selection changes downstream smoothness yield. Later work continued improving generation, size optimization, root optimization, and lattice-based selection.

This creates a natural modern research seam:
* The evaluation signal is quantitative;
* Candidate representations can be generated automatically;
* The final result can be tested empirically rather than accepted on proxy score alone.

A modern evolutionary system can therefore search a broader programmatic space than conventional parameter tuning while remaining grounded by exact downstream evaluation.

---

## 3. Tensor-Network Schnorr Revival

A March 2026 Physical Review A paper, *“Integer factorization via tensor-network Schnorr's sieving,”* revisits Schnorr-style factoring by mapping the combinatorial optimization stage to a tensor-network treatment. The authors report factorization of RSA-like semiprimes up to 100 bits and numerical scaling studies through 130 bits. They explicitly state that the present method is limited by a high-order polynomial resource scaling and does not threaten contemporary deployed RSA.

The importance to this project is methodological, not cryptanalytic:
* An older mathematical route was reopened by a newer computational substrate;
* The system exposes several tunable stages rather than one monolithic algorithm;
* Small-bit experiments are cheap enough for automated search;
* Exact factor verification makes evaluation unambiguous.

Track A begins by reproducing a simplified version of this seam.

---

## 4. Partial-Factor Recovery

Coppersmith-style small-root methods establish a powerful bridge: for balanced RSA moduli, sufficiently many known high or low bits of one prime factor can make complete recovery polynomial-time. Later work generalizes partial-key exposure to more fragmented patterns.

This suggests reframing the search objective:  
Instead of demanding $N \to p$, Track C asks whether we can achieve:
$$N \longrightarrow \text{useful constraints on } p \longrightarrow \text{exact lattice recovery}$$

The crucial experimental danger is leakage. A benchmark must allow the evaluator to know the hidden prime while preventing the proposer from seeing it.

---

## 5. SAT and Constraint Formulations

Integer factorization can be reduced to Boolean satisfiability. Published work shows that such reductions are useful experimentally, but large semiprimes have not been competitive with specialized factoring algorithms.

That is not evidence that every constraint formulation is exhausted. It is evidence that naïve or conventional multiplication encodings do not remove the core difficulty.

Track D therefore treats encoding structure as the object of search:
* Carry organization;
* Block size;
* Redundant representations;
* Decomposition graph;
* Auxiliary variables;
* Solver-specific structure;
* Optional tensor-network contraction of the same graph.

The target metric is not merely “fewer clauses.” It is lower empirical solve complexity and, secondarily, lower graph-structural complexity.

---

## 6. AI-Guided Algorithm Discovery

AlphaEvolve demonstrates a useful architecture for this problem class: generative models propose program changes; automated evaluators score them; an evolutionary system preserves and mutates stronger candidates. Google DeepMind reports successful use across algorithm optimization and mathematical construction problems.

The key lesson is architectural:
> *AI is most defensible here when it searches a machine-verifiable design space, not when it is asked to intuit prime factors.*

The project therefore keeps the LLM out of truth adjudication.

---

## 7. What Has Changed Technologically

Several historical “not worth trying” judgments may deserve re-evaluation because:
* Vectorized CPUs and GPUs make enormous candidate evaluation cheap;
* Modern SAT/SMT and lattice libraries are dramatically stronger;
* Tensor-network software has matured;
* Open-source NFS implementations provide a high-quality baseline and reusable stages;
* AI code generation makes broad implementation-space search affordable;
* Evolutionary agent loops can operate continuously against exact metrics;
* Storage is cheap enough to retain all raw results and compare failed branches later.

None of these facts imply a breakthrough. Together they lower the cost of exploring dead ends correctly.

---

## 8. Research Priority Order

1. Reproduce controls and baselines;
2. Reproduce the smallest credible Track A behavior;
3. Build Track B's exact candidate-validity and yield evaluator;
4. Build Track C's sealed partial-information benchmark;
5. Build Track D's baseline multiplication encoding;
6. Only then turn on autonomous mutation.

This order maximizes the chance that AI exploration optimizes a real scientific signal rather than a broken harness.
