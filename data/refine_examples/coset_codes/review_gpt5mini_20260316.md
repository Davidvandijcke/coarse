# A. History

**Date**: 03/16/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper compares trellis-based coded-modulation constructions to lattice codes by developing geometric performance metrics (fundamental volume, d_min, and a normalized fundamental coding gain γ) and by mapping many trellis constructions to lattice-partition descriptions so their gains and decoding complexities can be compared. It proposes augmented encoder constructions to relate trellis codes to group-partition codes and uses those relations plus a heuristic "effective coding gain" correction and normalized decoder-operation counts to rank designs. The main empirical conclusion is that, under the paper's complexity and ML-decoding assumptions, many trellis codes provide superior effective coding gain per decoding cost compared to the lattice codes surveyed. Readers might note that several key algebraic, probabilistic, and algorithmic hypotheses that underpin these identities and comparisons are not stated explicitly and that some central adjustments (notably the 0.2 dB heuristic) are used without formal justification.

Below are the most important issues identified by the review panel.

**Missing formal hypotheses and proofs for volume and normalization equalities**

Several central equalities (Lemma 1: V(Λ') = |Λ/Λ'| V(Λ), and the trellis-code fundamental-volume identity V(𝒞)=V(Λ0) / the relation V(Λ0)=2^{-k}V(Λ')) are presented without the precise technical hypotheses needed for them to hold. It would be helpful to state explicitly that Λ and Λ' are full-rank N-dimensional lattices (finite-index subgroup), fundamental regions are measurable, and that the trellis constructions are time-invariant and distance-invariant (or otherwise satisfy ergodic/time-average limits) when invoking density/volume equalities. Readers might note that these assumptions are used repeatedly to derive γ(·) and populate the numerical tables; without them the normalization (and hence every downstream numerical gain) can be invalid in degenerate or pathological cases. Suggested fixes: add precise hypotheses at each lemma, supply a short formal proof or citation to standard lattice-theory results for Lemma 1, and give a stated proposition (with assumptions such as noncatastrophic encoder, time-invariance/ergodicity, and full-rank Λ0) proving V(𝒞)=V(Λ0) and the 2^{-k} scaling; where the result does not hold, explicitly exclude or treat those cases.

**Insufficient constructive conditions for augmented encoders, linearity and Ungerboeck labelings**

Claims that any trellis code on Λ/Λ' can be implemented by an augmented convolutional encoder C' with the same number of states (Lemma 5) and that mod‑2 partitions with linear labelings yield a binary convolutional equivalent (Lemma 6) lack the algebraic and structural constraints needed to make them universally true. It would be helpful to specify when the packed coset-selection mapping is time-invariant and realizable without state expansion — e.g., require explicit choices of coset representatives and that the labeling c(·) be a group homomorphism (or give a precise regular-labeling definition) — and to give a concrete state assignment and transition map showing how C' attains the stated state-count. Readers might note that when these conditions fail (non-homomorphic labeling, locally linear labelings, or indecomposable lattices) the augmented encoder may need additional memory or nonconvolutional structure and the d_min mapping to a binary Hamming distance can break. Suggested fixes: replace informal lemmas with precise constructive statements: (a) list exact algebraic conditions on c(·) and representative selection that guarantee time-invariance and state-count preservation, (b) provide an explicit encoder construction (generator matrices or shift-register description) and, where relevant, an upper bound on state expansion when conditions fail, and (c) for Ungerboeck/decomposable constructions give an algorithm (or reference) to choose generators g_k and mark lattices where decomposability/equality in the distance bound may not hold.

**Heuristic 'effective coding gain' adjustment needs formal error-probability justification**

The paper adjusts geometric coding gains with a rule of thumb that every factor-of-two increase in the nearest-neighbor multiplicity reduces coding gain by ≈0.2 dB (at error rates ~10^{-6}); this heuristic is used to form γ_eff values that drive many comparisons and conclusions. It would be helpful to replace or substantially qualify this heuristic by deriving an explicit union-bound (or saddlepoint) approximation that shows how N0, N1, … and SNR determine error probability and how those translate into a dB-equivalent penalty, or alternatively to present representative Monte Carlo / analytic BER/FER curves for key codes and SNRs to validate the rule. Readers might note the correction depends strongly on operating SNR and the higher-order distance spectrum, so using a single-number adjustment can misrank designs. Suggested fixes: derive and present a principled approximation linking γ_eff to the first few distance-spectrum coefficients and the SNR regime of interest, annotate tables/figures with the SNR/error-rate assumptions, and, where exact multiplicities are known, report γ_eff obtained from the union bound or show simulated performance to justify the heuristic.

**Complexity accounting, decoder model, and robustness assumptions are underspecified**

Decoding-complexity comparisons (N_D, ~N_D in Tables II–III and Fig. 12) and practicality claims rest on an implicit ML trellis-decoding model, a particular per-branch operation count, and an AWGN channel; the paper does not state a complete cost model (arithmetic vs memory, traceback delay, quantization) nor does it show provable bounds relating N_D to lattice/encoder parameters. It would be helpful to state the exact decoding architecture and cost model up front (per-branch add/compare counts, memory scaling, traceback length), give pseudocode or a complexity theorem bounding N_D in terms of N, |Λ/Λ'|, k, ν and the chosen algorithm, and annotate tables with these assumptions so comparisons are reproducible. Readers might note that suboptimal decoders (reduced-state Viterbi, sequential/sphere decoding) and channel impairments (fading, phase/noise, synchronization errors) can change both complexity and relative performance; current conclusions claiming trellis superiority mix assumptions across constructions and are fragile without sensitivity analysis. Suggested fixes: include a clear complexity model, give upper/lower bounds or empirical variability ranges for N_D (or refer precisely to Part II results), and add a short subsection comparing performance/complexity under representative suboptimal decoders and simple channel impairments or otherwise qualify claims to the AWGN+ML setting.

**Asymptotic metrics are not tied sufficiently to finite-dimension/finite-length performance**

The paper frequently invokes asymptotic measures (Hermite parameter, fundamental coding gain γ) and claims about families of lattices, but it does not systematically show how those asymptotic or per-dimension gains translate into performance for the finite-dimensional constellations and block lengths of practical interest. It would be helpful to include finite-constellation analyses: truncated union bounds, finite-sphere-packing bounds, or representative BER/FER simulations for the main lattices and trellis codes at typical block lengths and SNRs so readers can see whether asymptotic advantages are realized in practice. Readers might note that boundary effects, shaping, and decoding latency can negate asymptotic gains at practical sizes; without explicit finite-length treatment, recommendations about preferring one family over another are hard to apply. Suggested fixes: add a section (or appendix) with finite-length bounds or simulation results for selected entries in the tables, or give explicit conditions (block length, rate, SNR range) under which the asymptotic γ values are expected to be predictive.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Labeling / coset-selection map is underspecified

**Status**: [Pending]

**Quote**:
> A coset code is defined by a lattice partition $\Lambda / \Lambda'$ and by a binary encoder $C$ that selects a sequence of cosets of the lattice $\Lambda'$. The fundamental coding gain of a coset code, as well as other important parameters such as the error coefficient, the decoding complexity, and the constellation expansion factor, are purely geometric parameters determined by $C$ and $\Lambda / \Lambda'$.

**Feedback**:
It would be helpful to make explicit the labeling map that associates encoder outputs to cosets (or to coset representatives). Introduce a mapping c: A -> Λ/Λ' (or to a fixed representative set R ⊂ Λ) and state whether C emits coset indices or representative points. Specify whether representative selection is fixed/time-invariant (per time step) or allowed to vary with time. Add one short paragraph describing how the choice of representatives affects downstream geometric quantities (distance spectrum, multiplicities) and give a canonical choice (e.g., coset leaders of minimum norm) or state that a fixed choice is assumed throughout so formulas are unambiguous.

---

### 2. Decoding complexity is implementation-dependent, not purely geometric

**Status**: [Pending]

**Quote**:
> The fundamental coding gain of a coset code, as well as other important parameters such as the error coefficient, the decoding complexity, and the constellation expansion factor, are purely geometric parameters determined by $C$ and $\Lambda / \Lambda'$.

**Feedback**:
Readers might note that decoding complexity depends on encoder realization, trellis/state assignment, and the chosen decoding algorithm, not only on the abstract partition. It would be helpful to rephrase this sentence to separate geometric invariants (d_min, volume, multiplicities) from implementation-dependent costs. When reporting complexity numbers, state the exact decoding cost model (per-branch add/compare counts, state count, traceback length) and indicate which encoder realization (state assignment / trellis) was used to obtain the quoted complexity.

---

### 3. Encoder model (block vs convolutional, memory) is not specified

**Status**: [Pending]

**Quote**:
> A coset code is defined by a lattice partition $\Lambda / \Lambda'$ and by a binary encoder $C$ that selects a sequence of cosets of the lattice $\Lambda'$. The fundamental coding gain of a coset code, as well as other important parameters such as the error coefficient, the decoding complexity, and the constellation expansion factor, are purely geometric parameters determined by $C$ and $\Lambda / \Lambda'$.

**Feedback**:
It would be helpful to state explicitly whether C is modeled as a block encoder, a convolutional encoder (with memory ν and state count 2^ν), or a generic source process. Add a one-sentence definition of the encoder model (e.g., rate k/(k+r), memory ν for convolutional encoders) and annotate statements that link r, ν and state counts so the intended meaning is verifiable and the mapping from encoder parameters to trellis size is clear.

---

### 4. Lemma 1 (volume identity) needs full-rank/finite-index hypotheses

**Status**: [Pending]

**Quote**:
> **Lemma 1:** If $\Lambda'$ is a sublattice of $\Lambda$ of order $|\Lambda / \Lambda'|$, then $V(\Lambda') = |\Lambda / \Lambda'| V(\Lambda)$.

**Feedback**:
Readers might note this identity requires both lattices to be full-rank (same real dimension) and the index |Λ:Λ'| to be finite. It would be helpful to restate Lemma 1 as: let Λ and Λ' be full-rank n-dimensional lattices with finite index m = [Λ:Λ']; then V(Λ') = m·V(Λ). Add the constructive proof (partition a fundamental region of Λ' into m translates of a fundamental region of Λ) or cite a standard lattice-theory reference. If the paper later relies on this identity for non-full-rank or infinite-index cases, explicitly exclude or treat those cases.

---

### 5. Two-stage decoding claim requires AWGN/Euclidean-ML qualification

**Status**: [Pending]

**Quote**:
> Finally, in decoding, the first operation can always be to determine the best signal point in each subset and its metric; after that step, decoding depends again only on the fundamental code structure determined by the first two encoding operations.

**Feedback**:
It would be helpful to state the assumption under which this two-stage decoder is optimal: specifically, a memoryless AWGN channel with symbolwise Euclidean-ML metrics (or any channel where the per-subset nearest-point suffices for ML ordering). Add a qualifying sentence that this two-stage strategy may be suboptimal for channels with memory, colored noise, or mismatched metrics where intra-subset soft information can affect the decision.

---

### 6. Heuristic γ_eff adjustment lacks explicit formula and worked example

**Status**: [Pending]

**Quote**:
> Note: if $\Lambda/\Lambda'$ is a partition, then so is $R\Lambda/R\Lambda' \simeq \phi\Lambda/\phi\Lambda'$; if it is simpler to decode $R\Lambda/R\Lambda'$ than $\Lambda/\Lambda'$, the lesser $\tilde{N}_D$ is given.) The final column gives $\tilde{N}_D/|\Lambda/\Lambda'|$, to show that $\tilde{N}_D$ is approximated by $\alpha|\Lambda/\Lambda'|$, where $\alpha$ is a small number in the range from one to six.

**Feedback**:
Readers might note the paper applies a heuristic 'effective coding gain' penalty (≈0.2 dB per factor-2 multiplicity) but does not provide a reproducible formula for γ_eff. It would be helpful to (a) state the explicit formula used to compute γ_eff from γ and neighbor multiplicities (or give a precise citation if taken from prior work), and (b) include one worked numeric example showing all computation steps from distance-spectrum coefficients to the γ_eff value reported in a table. This will make the table entries reproducible and allow readers to assess sensitivity to the assumed SNR/error-rate regime.

---

### 7. Viterbi branch-count uses r instead of encoder memory ν

**Status**: [Pending]

**Quote**:
> (For each unit of time, for each of the $2^{\nu}$ states, the Viterbi algorithm requires $2^k$ additions and a comparison of $2^k$ numbers, or $2^k - 1$ binary comparisons, so that its complexity is $\beta 2^{k + r}$, where $\beta = 2 - 2^{-k}$, and $2^{k + r}$ is the number of branches per stage of the trellis, which is the measure of complexity used by Ungerboeck [21], following Wei [11].)

**Feedback**:
Readers might note a mismatch in the exponent: the per-stage number of branches is 2^k per state times 2^ν states, giving total ≈ β·2^{k+ν}, not β·2^{k+r} unless ν = r. It would be helpful to correct the exponent (replace r by ν where appropriate), or explicitly state the modelling assumption that sets ν = r, and show the short arithmetic that leads to β·2^{k+ν} branches per stage so readers can verify the complexity claim.

---

### 8. Algebraic formulation misstates scalar domain and 'dimension' terminology

**Status**: [Pending]

**Quote**:
> (It follows that a convolutional code is a vector space over
> 
> the field of binary formal power series $f(D), f_{i} \in \{0,1\}$; the dimension of this vector space is $k$, and any codeword $a(D)$ can be written as $a(D) = \sum_{j} f_{j}(D) g_{j}(D)$, where the $g_{j}(D), 1 \leq j \leq k$, are a set of $k$ generator sequences that form a generator matrix $G$; see [20].)

**Feedback**:
It would be helpful to correct the algebraic language: the ring of binary formal power series F2[[D]] is not a field (D is not invertible). Either (a) adopt the Laurent-series model F2((D)) for bi-infinite sequences and then the scalar domain is a field and 'dimension k' is appropriate, or (b) treat causal convolutional codes as a free module of rank k over the ring F2[[D]] and replace 'dimension' with 'rank'. State clearly which convention you use before invoking linear-algebraic facts and adjust the wording ('field'→'ring' or specify Laurent series) and 'dimension'→'rank' where appropriate.

---

### 9. R matrix is orientation-reversing, not a pure rotation

**Status**: [Pending]

**Quote**:
> The most important scaled orthogonal transformation for our purposes is the rotation operator $R$, defined by the $2 \times 2$ matrix
> 
> $$
> R \triangleq \left( \begin{array}{cc} 1 & 1 \\ 1 & -1 \end{array} \right).
> $$
> 
> $R\mathbb{Z}^2$ is a version of $\mathbb{Z}^2$ obtained by rotating $\mathbb{Z}^2$ by $45^\circ$ and scaling by $2^{1/2}$ and is also illustrated in Fig. 4.

**Feedback**:
It would be helpful to be precise: write R = √2·Q with Q orthogonal and det(Q) = −1, so Q reverses orientation (a reflection composed with a 45° rotation), rather than calling it a pure rotation. Change wording from 'rotating by 45°' to 'a scaled orthogonal map (reflection+rotation) by 45° with scaling √2' and note det(Q) = −1 to avoid misleading readers about orientation.

---

### 10. Block R construction: clarify ambient dimension and quantifiers

**Status**: [Pending]

**Quote**:
> We can define a $2N$-dimensional rotation operator by letting $R$ operate on each pair of coordinates in a $2N$-tuple; with a slight abuse of notation, we denote by $R$ any such rotation operator. For instance, in four dimensions,
> 
> $$
> R \triangleq \left( \begin{array}{cccc} 1 & 1 & 0 & 0 \\ 1 & -1 & 0 & 0 \\ 0 & 0 & 1 & 1 \\ 0 & 0 & 1 & -1 \end{array} \right).
> $$
> 
> Note that $R^2 = 2I$ for any $N$, where $I$ is the identity operator in $2N$ dimensions, so that $R^2\Lambda = 2\Lambda$ for any real $2N$-dimensional lattice $\Lambda$.

**Feedback**:
Readers might be confused by the quantifier 'for any N'. It would be helpful to fix an integer m ≥ 1, set the ambient real dimension to 2m, and state that R is the block-diagonal matrix with m copies of the 2×2 block so that R^2 = 2I_{2m}. Make the dependence of I and Λ on the ambient dimension explicit to avoid conflating multiple uses of N.

---

### 11. Equality φΛ_c = RΛ_r needs explicit real-block mapping

**Status**: [Pending]

**Quote**:
> If $\Lambda = \Lambda^{*} - \mathrm{i.e.}$, if $\lambda \in \Lambda$ implies $\lambda^{*} \in \Lambda$, where $\lambda^{*}$ is the complex conjugate of $\lambda$ — as will be true for all lattices to be considered here, then $\phi \Lambda_{c} = R \Lambda_{r}$. The difference is slight, but we regard multiplication by the complex scalar $\phi$ as fundamentally a more natural operation than rotation by $R$.

**Feedback**:
It would be helpful to add the explicit 2×2 real matrix for multiplication by φ (for example, for φ = 1+i, M_φ = [[1,-1],[1,1]]), show the identification map C^N ≅ R^{2N}, and give the short matrix calculation or permutation/reflection that relates M_φ to R (or to a conjugate of R). This single matrix computation will make the asserted equality transparent to readers.

---

### 12. Scope of conjugation-invariance assumption should be explicit

**Status**: [Pending]

**Quote**:
> If $\Lambda = \Lambda^{*} - \mathrm{i.e.}$, if $\lambda \in \Lambda$ implies $\lambda^{*} \in \Lambda$, where $\lambda^{*}$ is the complex conjugate of $\lambda$ — as will be true for all lattices to be considered here, then $\phi \Lambda_{c} = R \Lambda_{r}$.

**Feedback**:
Readers might note the phrase 'as will be true for all lattices to be considered here' overreaches unless the paper restricts its class of lattices. It would be helpful to state explicitly that from this point forward the paper restricts attention to complex lattices with Λ = Λ* (closed under conjugation), or else list and justify the specific lattices used later that satisfy this property.

---

### 13. Ambiguous convention for dimension N in r(Λ) and ρ(Λ)

**Status**: [Pending]

**Quote**:
> The redundancy $r(\Lambda)$ of a binary lattice $\Lambda$ is defined as the binary logarithm of $|Z^{N} / \Lambda|$, so that $|Z^{N} / \Lambda| = 2^{r(\Lambda)}$. In view of the corollary to Lemma 1, the fundamental volume of a binary lattice is therefore $V(\Lambda) = 2^{r(\Lambda)}$, and the fundamental coding gain is
> 
> $$
> \gamma (\Lambda) = 2 ^ {- \rho (\Lambda)} d _ {\min } ^ {2} (\Lambda)
> $$
> 
> where $\rho(\Lambda)$ is the normalized redundancy (per two dimensions) of $\Lambda$, $\rho(\Lambda) = r(\Lambda)/N$, where $2N$ is the dimension of $\Lambda$ as a real lattice, or $N$ is the dimension of $\Lambda$ as a complex lattice.

**Feedback**:
Readers might be confused by switching N between real and complex conventions. It would be helpful to fix a clear convention: introduce n as the real dimension and define r(Λ)=log2|Z^n/Λ|. Then define the normalized redundancy per two real dimensions as ρ = 2·r(Λ)/n. If you prefer the complex-dimension viewpoint, state that n = 2N and thus ρ = r(Λ)/N, and be consistent in all formulas. Add a short paragraph that explains which convention is used in tables and numerical entries.

---

### 14. Ambient lattice must be specified when giving index formulas

**Status**: [Pending]

**Quote**:
> The order of $\Lambda / 2^{m}Z^{2N}$ is $2^{2Nm - r(\Lambda)}$, and the order of $\Lambda / \phi^{u}G^{N}$ is $2^{Nu - r(\Lambda)}$.

**Feedback**:
It would be helpful to state which ambient integer or Gaussian lattice is used to define r(Λ) (for example, r(Λ)=log2|Z^{2N}/Λ| or r(Λ)=log2|G^N/Λ|), because the exponents differ by factors of two otherwise. Add an explicit sentence immediately before these formulas explaining the ambient lattice used and how r(Λ) was computed so the presented exponents are unambiguous.

---

### 15. Ungerboeck representative-count conflates quotient levels

**Status**: [Pending]

**Quote**:
> Thus the $2^{K}$ binary linear combinations $\{\sum a_{k}g_{k}\}$ of the generators $g_{k}$ are a system of coset representatives $[\Lambda_{k} / \Lambda_{k + 1}]$ for the partition $\Lambda_{k} / \Lambda_{k + 1}$ (this is a special case of a general result for groups of order $2^{K}$ — binary groups—discussed in part II). In the coding context, we call such a labeling an Ungerboeck labeling.

**Feedback**:
Readers might note a counting mismatch: 2^K combinations give representatives for Λ/Λ' (the full K-level quotient), whereas a single step quotient Λ_k/Λ_{k+1} should have exactly 2 representatives. It would be helpful to rewrite this passage to distinguish levels: state that 2^K representatives index Λ/Λ', that Λ_k/Λ' has 2^{K-k} representatives, and that each adjacent quotient Λ_k/Λ_{k+1} has 2 representatives. Correct the text to avoid conflating the full multi-level quotient with a single two-way quotient and, if useful, add a short illustrative example for K=3.

---
