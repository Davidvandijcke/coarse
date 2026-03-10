# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/09/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Minimum Squared Distance Formula for Mod-4 Lattices Requires a Missing Rigorous Step**

In Section II-G, the minimum squared distance of a real mod-4 decomposable lattice is stated as d²_min(Λ) = min[16, 4d_H(C₁), d_H(C₀)] for Λ = 4Z^N + 2C₁ + C₀. The proof sketch considers the three cases where the lowest nonzero coefficient index is 0, 1, or 2 separately, but does not explicitly address the simultaneous case where both a₀ ≠ 0 and a₁ ≠ 0. The key step—that ‖2a₁ + a₀‖² ≥ d_H(C₀)—holds because coordinates of 2a₁ are even and those of a₀ are odd, so no coordinate-wise cancellation can occur; however, this parity argument is not stated in the paper. Additionally, the analogous formula for indecomposable cases (e.g., Λ₂₄ and H₂₄, flagged with primes in Table I) is asserted without a separate derivation, yet these lattices appear as benchmarks in Section VII. It would be helpful to add a brief parity-based argument for the decomposable case and to either provide the distance argument for indecomposable lattices or explicitly flag which entries in Tables I–II depend on results deferred to Part II.

**Fundamental Coding Gain Metric Conflates Asymptotic and Finite-Constellation Regimes Without Adequate Qualification**

The paper's central performance metric γ(C) = 2^{−ρ(C)} d²_min(C) is derived from an asymptotic argument (N-sphere volume scaling as n → ∞) and explicitly omits the shape gain γ_s, which can reach 1.53 dB asymptotically and varies with constellation size n and boundary geometry. Despite this, the comparative rankings in Section VII—including the claim that Ungerboeck codes remain the benchmark and the folk theorem about state counts—are stated as if they apply to practical finite-size systems. For codes with very different normalized redundancies ρ (e.g., ρ = 1/8 for 16-dimensional Wei codes versus ρ = 2 for one-dimensional Ungerboeck codes), the constellation expansion factor 2^ρ differs by 2^{15/8}, which can substantially alter the practical power budget at any finite constellation size. Readers might note that for high-dimensional codes such as Barnes–Wall lattice codes, γ_s differences between code classes sharing the same γ(C) could affect the rankings shown in Fig. 12. It would be helpful to either bound the error introduced by ignoring γ_s for each code class, or to restrict comparative claims in Section VII to regimes where the omission is demonstrably negligible (e.g., by stating a minimum constellation size for which the asymptotic approximation is accurate to within 0.1 dB).

**Effective Coding Gain Rule of Thumb Lacks Derivation and Is Applied Inconsistently Across Code Classes**

Section V introduces the rule that every factor-of-two increase in the normalized error coefficient Ñ₀ costs approximately 0.2 dB in effective coding gain γ_eff, and this rule is applied uniformly throughout Tables IV–XI and the comparative discussion of Section VII. No derivation or citation is provided; the rule implicitly assumes a nearest-neighbor union-bound approximation that can be off by several tenths of a dB when higher-order coefficients Ñ₁ and Ñ₂ are large. Higher-order coefficients are tabulated only for Ungerboeck-type codes (Table V), while for Wei codes (Table VII), Calderbank–Sloane codes (Table IX), and all generic Classes I–VIII (Table XI), γ_eff is either omitted or computed from Ñ₀ alone—even when Ñ₀ is flagged as very large (e.g., Ñ₀ = 1692 for the 16-state D₁₆/H₁₆ Class V code). The conclusion in Section VII that 'trellis codes are better than lattice codes' in effective coding gain rests on this incomplete and inconsistently applied accounting. It would be helpful to either derive the 0.2 dB rule from a specific channel model and error-rate target, extend the higher-order coefficient analysis to all code classes, or qualify the comparative conclusions as contingent on the single-neighbor approximation.

**Regularity of Labelings for Mod-4 and Higher-Depth Partitions Is Asserted Without Complete Verification**

Section IV-C states that 'regular labelings (although not necessarily regular Ungerboeck labelings) exist for all partitions used in all the codes covered in this paper,' and lists three sufficient conditions (linearity, Ungerboeck distance bound holding with equality, Cartesian product structure). Condition (a) covers mod-2 partitions cleanly via Lemma 6, but partitions such as D₄/2D₄, E₈/RE₈, D₈⊥/RE₈, H₁₆/Λ₁₆, and D₁₆/H₁₆—used in Classes I–VIII and appearing in Tables VII–XI—are mod-4 or depth-3 partitions that do not obviously satisfy any of the three listed conditions. Since distance-invariance of the trellis code, and hence the validity of the error coefficient N₀(C) as a well-defined uniform quantity, rests on regularity, the error coefficient calculations for these higher-depth partitions are implicitly conditional on an unverified claim. It would be helpful to either provide explicit regular labeling constructions for each partition class used, extend the regularity lemma to cover mod-4 and higher-depth cases, or identify precisely which entries in Tables VII–XI depend on regularity results deferred to Part II and note that dependency explicitly.

**Decoding Complexity Metric Ñ_D Is Algorithm-Specific and Its Scaling Is Only Empirically Justified**

Throughout Tables II–XI and the discussion of Section VII, Ñ_D is defined as the number of binary operations required by the specific trellis-based algorithms of Part II, normalized per two dimensions. The paper acknowledges that this measure is 'highly implementation-dependent,' yet it serves as the primary complexity axis in Fig. 12 and underpins the folk theorem of Section VII. Several concerns compound this issue: (1) the Viterbi algorithm component is counted using a separate formula (β·2^{k+r} per state, following Wei and Ungerboeck), and it is unclear whether this is included in or added to the Ñ_D values of Table III; (2) no closed-form expression or asymptotic bound for Ñ_D as a function of partition depth μ, order |Λ/Λ'|, and dimension 2N is derived in this paper—the empirical observation that Ñ_D ≈ α|Λ/Λ'| (α ∈ [1,6]) is the only scaling result offered; and (3) for codes with large partition orders (e.g., the 128-state H₁₆/Λ₁₆ code with Ñ_D ≈ 5632), partition decoding so dominates that state count becomes nearly irrelevant, yet all codes are plotted on the same axis in Fig. 12. It would be helpful to decompose Ñ_D into its partition-decoding and Viterbi components in at least one representative table, state the asymptotic scaling of Ñ_D with a reference to the specific theorem in Part II, and bound the ratio by which alternative algorithms could change the relative rankings.

**Eight-Class Taxonomy Is Not Shown to Be Exhaustive or Mutually Exclusive**

Section VI introduces eight generic code classes (I–VIII) defined by three binary characteristics—partition type, encoder rate, and constraint length—and claims they 'round out the picture' of coset code design. However, the paper does not prove that these classes are exhaustive over the space of binary coset codes with the stated structural constraints, nor that they are mutually exclusive. Several overlaps are noted informally (Class I and Class V coincide for k = 1; Class II and Class VI coincide for the four-state D₄/RD₄ code; Class IV recovers the four-state Ungerboeck code), but these are treated as coincidences rather than as evidence of a partially redundant taxonomy. The boundary between Wei-type codes (Section V) and Classes V/VI is described only informally, and several codes appear in multiple tables without a systematic resolution. Codes with constraint lengths greater than 2k or encoder rates other than k/2k and k/(k+1) are excluded without justification. It would be helpful to provide a formal decision tree or set of necessary and sufficient conditions that assigns any given (Λ/Λ', C) pair to a unique class, to verify that known codes map injectively into the taxonomy, and to state explicitly whether the classification is intended to be illustrative or exhaustive.

**Fundamental coding gain formula treats constellation shaping as fully separable, but boundary effects are not always negligible**

The paper's central formula γ(C) = 2^{−ρ(C)} · d²_min(C) (Section I-B and Section IV-B) is derived under the assumption that the constellation expansion power cost is exactly 2^{ρ(C)} per two dimensions, which in turn rests on the premise that the signal constellation is large enough and regular enough that the volume-to-power relationship V(Λ)^{2/N} accurately represents average power. The paper explicitly acknowledges this by defining γ_tot(C) = γ(C) · γ_s and noting that γ_s = 1 only when the constellation boundary is a hypercube. For finite constellations with non-cubic boundaries—including the 'cross' 64-point constellation shown in Fig. 3(b)—γ_s ≠ 1 and the formula for γ(C) no longer equals the total coding gain. The paper's stated position is that γ_s is 'peripheral' and that focusing on γ(C) 'clarifies' comparisons. Readers might note, however, that when comparing codes across different dimensions N, the shape gain γ_s scales as roughly π e/6 ≈ 1.53 dB in the limit N → ∞, so the gap between γ(C) and γ_tot(C) grows with dimensionality. The comparative tables (Tables IV–XI) report only γ(C), meaning that the apparent advantage of higher-dimensional codes (e.g., the 16-dimensional Wei codes with ρ = 1/8) is partly offset by a larger shape-gain deficit that is not reflected in the tabulated figures. It would be helpful to note explicitly, at least in the discussion of Table VII and the folk theorem of Section VII, that the dimensional trend in shape gain could narrow the practical performance gap between low- and high-dimensional codes.

**Distance-invariance is asserted for all codes but relies on regularity of the labeling, which is verified only case-by-case**

Section IV-B defines distance-invariance and states 'All codes in this paper are distance-invariant,' grounding this on the regularity of the labeling (Section IV-C). Regularity is then established under three sufficient conditions (linearity of the labeling, Ungerboeck distance bound holding with equality, or Cartesian-product structure). For the non-linear trellis codes—particularly the mod-4 and higher-depth codes such as those based on RE_8/2E_8 or Λ_16/RΛ_16—the paper does not explicitly verify which of the three conditions applies. For example, the Class III code based on E_8/RE_8/2E_8 relies on the existence of an 'alternative partition E_8/R*E_8/2E_8' (Section VI, Class III discussion) whose coset representatives simultaneously serve both levels of the chain; this is a non-trivial structural claim whose proof is deferred to Part II. If the Ungerboeck distance bound does not hold with equality at every level of the chain for these partitions, the labeling may fail to be regular, and the distance-invariance claim—and hence the validity of the error-coefficient formula N_0(C)—would need re-examination. It would be helpful to either state explicitly which regularity condition covers each code family in Tables VIII–XI, or to add a forward reference to the specific Part II result that establishes regularity for the mod-4 and depth-3/4 cases.

**Status**: [Pending]

---

## Detailed Comments (23)

### 1. Shape Gain Omission Not Flagged in Comparative Tables

**Status**: [Pending]

**Quote**:
> The total coding gain $\gamma_{\text{tot}}(\mathcal{C})$ is the product of the fundamental coding gain $\gamma(\mathcal{C})$ with the shape gain $\gamma_s$ of the finite constellation

**Feedback**:
The paper's central metric γ(C) = 2^{−ρ}d²_min omits γ_s, which reaches up to πe/6 ≈ 1.53 dB as N → ∞. The abstract and Section I-B present γ(C) as the definitive comparative figure without noting that higher-dimensional codes (e.g., 16-dimensional Wei codes with ρ = 1/8) incur a larger shape-gain deficit than lower-dimensional Ungerboeck codes (ρ = 1). Because the shape-gain deficit grows with dimensionality, the apparent advantage of high-dimensional codes in Tables IV–XI is partly offset by a factor not reflected in the tabulated figures. It would be helpful to add at least one sentence in Section VII noting that the dimensional trend in γ_s could narrow the practical performance gap between low- and high-dimensional codes, or to restrict comparative claims to regimes where the omission is demonstrably negligible.

---

### 2. Shape Gain Formula Numerator Factor (n+1) Lacks Derivation

**Status**: [Pending]

**Quote**:
> the shape gain of an $N$-sphere over an $N$-cube, which for $N$ even is $G_{\otimes} = \pi (n + 1) / [6(n!)^{1 / n}]$, where $n = N / 2$; thus $G_{\otimes} = \pi /3$ (0.20 dB) for $N = 2$, $\pi /2^{3 / 2}$ (0.46 dB) for $N = 4$, $5\pi /6(24)^{1 / 4}$ (0.73 dB) for $N = 8$

**Feedback**:
Spot-checking the formula: for N=2, n=1: π(2)/[6·1] = π/3 ✓; for N=4, n=2: π(3)/[6·√2] = π/2^{3/2} ✓; for N=8, n=4: π(5)/[6·(24)^{1/4}] = 5π/[6(24)^{1/4}] ✓. The numerical values are internally consistent. However, the standard N-sphere volume formula V_N = π^{N/2}/Γ(N/2+1) does not obviously produce the (n+1) numerator factor under the paper's normalization convention. It would be helpful to add a brief derivation or citation showing how G_⊗ = π(n+1)/[6(n!)^{1/n}] follows from the sphere-volume formula, so readers can confirm the (n+1) factor is intentional rather than a typographical variant of a different normalization.

---

### 3. R Matrix Is an Improper Rotation (Includes Reflection), Not a Pure Rotation

**Status**: [Pending]

**Quote**:
> $R\mathbb{Z}^2$ is a version of $\mathbb{Z}^2$ obtained by rotating $\mathbb{Z}^2$ by $45^\circ$ and scaling by $2^{1/2}$

**Feedback**:
The matrix R = [[1,1],[1,−1]] has determinant (1)(−1) − (1)(1) = −2, which is negative. A pure scaled rotation has positive determinant; det = −2 indicates a scaled improper rotation (rotation composed with a reflection). The algebraic property R² = 2I is unaffected, but the geometric description misleads readers about the orientation-preserving nature of the transformation. It would be helpful to rewrite 'rotating $\mathbb{Z}^2$ by $45°$ and scaling by $2^{1/2}$' as 'applying a scaled orthogonal transformation (rotation by 45° composed with a reflection) and scaling by $2^{1/2}$,' since det(R) = −2 < 0 confirms the transformation is improper.

---

### 4. Order of Partition Formula Exponent Requires Clarification of Which Lattice Each Parameter Belongs To

**Status**: [Pending]

**Quote**:
> f $\Lambda'$, $\kappa(\Lambda / \Lambda') \triangleq \kappa(\Lambda')$. It follows that the order of the partition is
> 
> $$
> \left| \Lambda / \Lambda^ {\prime} \right| = 2 ^ {N \left(\mu \left(\Lambda^ {\prime}\right) - \rho (\Lambda) - \kappa \left(\Lambda^ {\prime}\right)\right)}
> $$
> 
> where $2N$ is the dimension of $\Lambda$ as a real lattice.
> 
> ## F. Labelings of Partitions of Binary Lattices
> 
> If $

**Feedback**:
A naive reading of the exponent N(μ(Λ') − ρ(Λ) − κ(Λ')) suggests it is zero, because the paper defines μ = ρ + κ for any lattice. The key point—not stated in the text—is that the three quantities come from *different* lattices: μ(Λ') and κ(Λ') from the inner lattice Λ', and ρ(Λ) from the outer lattice Λ. Consequently the exponent equals N(ρ(Λ') − ρ(Λ)), which is positive when Λ' is denser than Λ. It would be helpful to add a sentence clarifying that μ(Λ') − κ(Λ') = ρ(Λ') by definition applied to Λ', so the exponent reduces to N(ρ(Λ') − ρ(Λ)), making the formula's dependence on the density ratio explicit.

---

### 5. Order of φ^μ G Sublattice Uses Ambiguous Exponent Notation

**Status**: [Pending]

**Quote**:
> More generally, $\phi^{\mu}G$ is a sublattice of $G$ of order $|\phi|^2\mu = 2^\mu$

**Feedback**:
The expression '|φ|^2μ' is ambiguous: it can be parsed as (|φ|^2)·μ = 2μ (a product) rather than the intended |φ|^{2μ} = 2^μ (a power). The intended quantity is the squared norm of φ^μ, i.e., |φ^μ|^2 = (|φ|^2)^μ = 2^μ, consistent with Lemma 1's statement that the order of G/gG is |g|^2. It would be helpful to rewrite '|φ|^2\mu = 2^\mu' as '|\phi^\mu|^2 = 2^\mu' to unambiguously express the norm of φ^μ.

---

### 6. Lemma 2 Uses Approximate Equality '≈' Where Exact Equality Is Required

**Status**: [Pending]

**Quote**:
> Then there is a sequence of lattices $\Lambda_0 = \Lambda$, $\Lambda_1, \dots, \Lambda_K \approx \Lambda'$

**Feedback**:
The lemma statement uses '$\Lambda_K \approx \Lambda'$' (approximate equality) rather than '$\Lambda_K = \Lambda'$' (exact equality). The proof sketch explicitly states '$\Lambda_K = \Lambda'$ is certainly such a lattice,' confirming the construction requires exact equality. Using '≈' weakens the lemma to an approximate relationship, which is mathematically insufficient for the partition chain to be well-defined. It would be helpful to rewrite '$\Lambda_K \approx \Lambda'$' as '$\Lambda_K = \Lambda'$' in the lemma statement. (Note: this may be an OCR artifact, but it constitutes a mathematical error in the text as presented.)

---

### 7. Coset Representatives Notation Conflates Full Partition with Individual Two-Way Sub-Partition

**Status**: [Pending]

**Quote**:
> Thus the $2^{K}$ binary linear combinations $\{\sum a_{k}\mathbf{g}_{k}\}$ of the generators $\mathbf{g}_{k}$ are a system of coset representatives $[\Lambda_{k} / \Lambda_{k + 1}]$ for the partition $\Lambda_{k} / \Lambda_{k + 1}$

**Feedback**:
The partition Λ_k/Λ_{k+1} is a two-way partition with exactly 2 cosets, not 2^K. The 2^K binary linear combinations are coset representatives for the full partition Λ/Λ' = Λ_0/Λ_K, not for the individual two-way sub-partition Λ_k/Λ_{k+1}. The sentence immediately preceding correctly states that {a_k g_k, a_k ∈ {0,1}} (only 2 elements) are representatives for Λ_k/Λ_{k+1}. It would be helpful to rewrite '$2^{K}$ binary linear combinations $\{\sum a_{k}\mathbf{g}_{k}\}$ … are a system of coset representatives $[\Lambda_{k} / \Lambda_{k + 1}]$ for the partition $\Lambda_{k} / \Lambda_{k + 1}$' as '$2^{K}$ binary linear combinations $\{\sum a_{k}\mathbf{g}_{k}\}$ … are a system of coset representatives $[\Lambda / \Lambda']$ for the full partition $\Lambda / \Lambda'$'.

---

### 8. Minimum Squared Distance Formula for Mod-4 Lattice Omits Parity Argument for Mixed Case

**Status**: [Pending]

**Quote**:
> because, on the one hand, there are $N$-tuples in $4Z^{N}$ of norm 16, in $2C_{1}$ of norm $4d_{H}(C_{1})$ and in $C_0$ of norm $d_H(C_0)$; on the other hand, if $\lambda \equiv 2a_{1} + a_{0}\bmod 4$ and $a_0\neq \mathbf{0}$, then $\| \lambda \| ^2\geq d_H(C_0)$

**Feedback**:
The lower bound ‖λ‖² ≥ d_H(C_0) for the case a_0 ≠ 0 is stated without explaining why the 2a_1 term cannot cancel the a_0 contribution. The essential parity argument is: coordinates of 2a_1 are even and coordinates of a_0 are odd (since a_0 is a binary codeword viewed as a {0,1}-vector), so in each nonzero coordinate of a_0 the combined value 2(a_1)_i + (a_0)_i is odd and hence nonzero, contributing at least 1 to the squared norm. Thus ‖2a_1 + a_0‖² ≥ d_H(C_0). This parity argument is the essential step that prevents coordinate-wise cancellation but is not stated in the paper. It would be helpful to add a sentence after 'then ‖λ‖² ≥ d_H(C_0)' explaining that coordinates of 2a_1 are even and those of a_0 are odd, so no cancellation can occur.

---

### 9. Subcode Condition C_0 ⊆ C_1 in Lemma 4 Proof Is Compressed Without Modular Arithmetic

**Status**: [Pending]

**Quote**:
> Since $\Lambda$ is a $G$-lattice, $\lambda \in \Lambda$ implies $\phi \lambda \in \Lambda$. Therefore, $C_0$ must be a subcode of $C_1$.

**Feedback**:
The one-line argument does not show the modular arithmetic needed to conclude C_0 ⊆ C_1. For λ ≡ c_0 (mod φ) with c_0 ∈ C_0 (taking c_1 = 0), we have φλ ≡ φc_0 (mod φ²). For φλ ∈ Λ we need φλ ≡ φc_1' + c_0' (mod φ²) for some c_1' ∈ C_1, c_0' ∈ C_0. Since φλ ≡ φc_0 (mod φ²), we need c_0' = 0 and c_1' = c_0, requiring c_0 ∈ C_1, establishing C_0 ⊆ C_1. It would be helpful to add after 'Therefore, $C_0$ must be a subcode of $C_1$' the derivation: 'Specifically, if λ ≡ c_0 (mod φ) with c_0 ∈ C_0, then φλ ≡ φc_0 (mod φ²), so membership of φλ in Λ requires c_0 ∈ C_1.'

---

### 10. Inconsistent Exponent Variable 'n' vs 'μ' in Dual Lattice Verification

**Status**: [Pending]

**Quote**:
> This proposition may be verified by noting that $C_0^\perp / \dots / C_{n-1}^\perp$ is a code partition chain, that every generator $\phi^{\mu - j - 1} \pmb{g}_j^\perp$ of $\Lambda^\perp / \phi^n \pmb{G}^N$ is orthogonal mod $\phi^u$ to every generator $\phi^{j'} \pmb{g}_{j'}$ of $\Lambda / \phi^n \pmb{G}^N$

**Feedback**:
Throughout Section II-H the partition depth is consistently denoted μ, and the base lattice is φ^μ G^N. However, this verification sentence uses 'n' for the exponent in φ^n G^N and 'u' for the modulus φ^u, both of which appear to be typographic variants of μ. The chain should have μ levels (indices 0 through μ−1), so C_{n−1}^⊥ should be C_{μ−1}^⊥, and the modulus should be φ^μ. It would be helpful to rewrite 'C_0^⊥/…/C_{n−1}^⊥ … Λ^⊥/φ^n G^N … Λ/φ^n G^N … mod φ^u' as 'C_0^⊥/…/C_{μ−1}^⊥ … Λ^⊥/φ^μ G^N … Λ/φ^μ G^N … mod φ^μ' for consistency with the rest of the section.

---

### 11. State Count 2^r Conflicts with Constraint Length 2^ν Definition

**Status**: [Pending]

**Quote**:
> A trellis diagram for a $2^{r}$-state, rate-$k / (k + r)$ convolutional code is an extended state transition diagram for the encoder that generates $C$.

**Feedback**:
Two sentences earlier the encoder is defined as having 2^ν states, where ν is the overall constraint length (number of binary memory elements). The phrase '2^r-state' reuses r as the state-count exponent, but r is already defined as the redundancy in the rate expression k/(k+r). For the four-state Ungerboeck code: k=1, r=1 (rate 1/2), ν=2 memory elements, giving 2^ν = 4 states. If '2^r-state' meant 2^1 = 2 states, the description would be wrong. It would be helpful to rewrite 'A trellis diagram for a $2^{r}$-state, rate-$k / (k + r)$ convolutional code' as 'A trellis diagram for a $2^{\nu}$-state, rate-$k / (k + r)$ convolutional code' to avoid conflating redundancy with constraint length.

---

### 12. Incorrect Intermediate Expression for V(C) in Coding Gain Derivation

**Status**: [Pending]

**Quote**:
> Since $V(\mathbb{C}) = V(\Lambda_0) = 2^{-k(C)}V(\Lambda') = 2^{k+r}V(\Lambda') = 2^{r(C)}V(\Lambda)$

**Feedback**:
The third expression in the chain is written as 2^{k+r}V(Λ'), which has the wrong sign in the exponent and is dimensionally inconsistent with the preceding term 2^{−k}V(Λ'). The correct chain is V(Λ_0) = 2^{−k}V(Λ') = 2^r V(Λ), using V(Λ') = 2^{k+r}V(Λ) so that 2^{−k}·2^{k+r}V(Λ) = 2^r V(Λ). The intermediate step 2^{k+r}V(Λ') is larger than 2^{−k}V(Λ') by a factor of 2^{2k+r} and should not appear in this chain. It would be helpful to rewrite the chain as 'V(C) = V(Λ_0) = 2^{−k(C)}V(Λ') = 2^{r(C)}V(Λ)', dropping the spurious 2^{k+r}V(Λ') term.

---

### 13. Redundancy Formula in Lemma 6 Proof Attributes r(Λ) to Wrong Lattice

**Status**: [Pending]

**Quote**:
> By the extension of Lemma 5, $\mathbb{C}$ is equivalent to a code based on the partition $Z^{N} / 2Z^{N}$, where the augmented encoder $C'$ has $N$ output bits and redundancy $r(C') = r + r(\Lambda)$.

**Feedback**:
From Lemma 5, the augmented encoder for a code based on Λ/Λ' has redundancy r + r(Λ'), not r + r(Λ). The augmented encoder adds r(Λ') uncoded bits to account for the redundancy of the sublattice Λ' (the output lattice). For example, if Λ = Z^N (r(Λ) = 0) and Λ' is a mod-2 sublattice with r(Λ') = r_0, the augmented encoder should have redundancy r + r_0 = r + r(Λ'), not r + 0 = r + r(Λ). It would be helpful to rewrite 'redundancy $r(C') = r + r(\Lambda)$' as 'redundancy $r(C') = r + r(\Lambda')$' to correctly attribute the lattice redundancy to the sublattice.

---

### 14. Fundamental Coding Gain Formula Written as 2^{−e}d²_min Instead of 2^{−ρ}d²_min

**Status**: [Pending]

**Quote**:
> The fundamental coding gain $\gamma$ is given by the formula $2^{-e}d_{\mathrm{min}}^2$

**Feedback**:
The paper defines γ(C) = 2^{−ρ}·d²_min where ρ is the normalized redundancy. The formula '2^{−e}d²_min' uses e (the log of the state count) as the exponent, which is not the same as ρ. Checking against Table IV: for the 8-state one-dimensional Ungerboeck code, ρ = 2 and d²_min = 10, giving γ = 2^{−2}·10 = 2.5 (≈ 3.98 dB), consistent with the tabulated value. Using e = 3 instead would give 2^{−3}·10 = 1.25, which does not match. The formula 2^{−e}d²_min is therefore incorrect as written. It would be helpful to rewrite '$2^{-e}d_{\mathrm{min}}^2$' as '$2^{-\rho}d_{\mathrm{min}}^2$'.

---

### 15. Partition Order 128 for Z^4/2D_4 Inconsistent with Index Calculation

**Status**: [Pending]

**Quote**:
> |  4 | Z^{4} | 2D_{4} | 128 | 4/5 | 1/2 | 6 | 6/2^{1/2} | 6.28 | 728 | 2040 | 4.77  |

**Feedback**:
The partition order |Z^4/2D_4| is listed as 128. Computing from first principles: V(D_4) = 2 (since |Z^4/D_4| = 2), so V(2D_4) = 2^4·V(D_4) = 32, giving |Z^4/2D_4| = V(2D_4)/V(Z^4) = 32. With encoder rate 4/5 producing 5 output bits, the partition order should be 2^5 = 32 to be consistent with the rate. A partition order of 128 = 2^7 would require 7 output bits, inconsistent with a 4/5 rate encoder. It would be helpful to verify whether the entry '128' is a typographical error for '32', and to correct the table accordingly.

---

### 16. Effective Coding Gain Rule of Thumb Applied Without Stated Baseline or Derivation

**Status**: [Pending]

**Quote**:
> In this paper, we will use the rule of thumb that every factor of two increase in the error coefficient reduces the coding gain by about 0.2 dB (at error rates of the order of $10^{-6}$); this will enable us to compute an effective coding gain $\gamma_{\mathrm{eff}}$ (in dB), normalized for the error coefficient $\tilde{N}_0$.

**Feedback**:
The 0.2 dB rule is applied uniformly throughout Tables IV–XI and the comparative discussion of Section VII, but the reference baseline Ñ₀ is never stated explicitly. Checking against Table VI (GCS code): γ = 4.52 dB, Ñ₀ = 44. If the baseline is Ñ₀ = 4 (the four-state Ungerboeck code), the penalty is 0.2·log₂(44/4) = 0.2·log₂(11) ≈ 0.69 dB, giving γ_eff ≈ 3.83 dB vs. the tabulated 3.82 dB ✓. The baseline Ñ₀ = 4 is never stated. It would be helpful to state the reference baseline Ñ₀ and the channel model (AWGN, ML decoding) from which the 0.2 dB rule is derived, so readers can assess its accuracy for codes with very large Ñ₀ (e.g., Ñ₀ = 1692 for the 16-state D₁₆/H₁₆ Class V code).

---

### 17. Regularity Claimed for All Partitions but Verified Only for Mod-2 Cases

**Status**: [Pending]

**Quote**:
> In fact, regular labelings (although not necessarily regular Ungerboeck labelings) exist for all partitions used in all the codes covered in this paper.

**Feedback**:
The three sufficient conditions for regularity listed in Section IV-C—(a) linear labeling, (b) Ungerboeck distance bound holding with equality, (c) Cartesian product structure—are verified for mod-2 lattices via Lemma 6. However, partitions such as D₄/2D₄, E₈/RE₈, H₁₆/Λ₁₆, and D₁₆/H₁₆ used in Classes I–VIII are mod-4 or depth-3 partitions that do not obviously satisfy any of the three conditions as stated. Since distance-invariance of the trellis code, and hence the validity of the error coefficient N₀(C) as a well-defined uniform quantity, rests on regularity, the error coefficient calculations for these higher-depth partitions are implicitly conditional on an unverified claim. It would be helpful to either provide explicit regular labeling constructions for each partition class used, or to add forward references to the specific Part II results that establish regularity for the mod-4 and depth-3/4 cases.

---

### 18. Coding Gain for E₈/RE₈ CS Codes: ρ = 5/4 Decomposition Not Explained in Table IX

**Status**: [Pending]

**Quote**:
> |  8 | E_{8} | RE_{8} | 8 | 3/4 | 5/4 | 8 | 2^{7/4} | 5.27 | 764 | 90 | 3.75  |

**Feedback**:
The normalized redundancy ρ = 5/4 for the E₈/RE₈ codes is not self-evident from the encoder rate k/(k+r) = 3/4 alone. The encoder contributes r_enc = 1 bit per 8 real dimensions = 1/4 per two dimensions; the partition E₈/RE₈ has order 16, contributing r(Λ) = log₂(16)/(8/2) = 1 per two dimensions; total ρ = 1/4 + 1 = 5/4. Checking: γ = 2^{−5/4}·8 = 2^{7/4} ✓ and 10·log₁₀(2^{7/4}) ≈ 5.27 dB ✓. The decomposition ρ = ρ_encoder + ρ(Λ) is the key step but is not stated in the table caption or surrounding text. Readers might note that adding a footnote to Table IX explaining ρ = r_encoder/(N/2) + r(Λ)/(N/2) for the E₈/RE₈ rows would make the ρ = 5/4 entries self-contained and consistent with the framework of Section IV-B.

---

### 19. Redundancy and Informativity of Λ(0,n) Formula Requires Verification for n ≥ 3

**Status**: [Pending]

**Quote**:
> From the properties of decomposable binary lattices and Reed-Muller codes, the redundancy and informativity of $\Lambda(0,n)$ are both equal to $n2^{n-1} = nN/2$

**Feedback**:
For n=2, N=4: k = Σ_{j=0}^{1} K(j,2) = 1+3 = 4, r = 2N_real − k = 8 − 4 = 4. So r = k = 4 = nN/2 = 2·4/2 = 4 ✓. For n=3, N=8: k = Σ_{j=0}^{2} K(j,3) = 1+4+7 = 12, r = 2N_real − k = 16 − 12 = 4 ≠ nN/2 = 3·8/2 = 12. The claim r = nN/2 appears to fail for n=3. Table II lists r(Λ_{16}) = 12 and k(Λ_{16}) = 12, which would require 2N_real = 24, but Λ_{16} is a 16-dimensional real lattice (2N_real = 16). It would be helpful to clarify whether redundancy and informativity are measured in real or complex dimensions, and to verify the formula against Table II for n ≥ 3.

---

### 20. H₁₆ Complex Code Formula in Table I Has Potentially Wrong Superscript on G

**Status**: [Pending]

**Quote**:
> (1,3) | H_{16} | 16 | 2 | 2Z^{16} + (16,11,4) | φ^{2}G^{4} + φ(8,7,2) + (8,4,4)

**Feedback**:
The general formula for Λ(r,n) as a complex G-lattice is Λ(r,n) = φ^{n−r}G^N + … where N = 2^n. For Λ(1,3): n=3, r=1, N = 2^3 = 8, so the base lattice should be G^8 (8 complex dimensions = 16 real dimensions). The table entry shows 'φ²G^4', but G^4 corresponds to N=4 (the E_8 row with n=2). Compare: the E_8 row (0,2) correctly shows 'φ²G^4' with N=4. For H_{16} with N=8, the entry should read 'φ²G^8'. It would be helpful to verify whether 'φ^{2}G^{4}' is a typographical error for 'φ^{2}G^{8}' and to correct the table if so.

---

### 21. Duplicate Rows for D₈/RE₈ Partition with Inconsistent Orders in Table III

**Status**: [Pending]

**Quote**:
> |  D8 | RE8 | 8 | 32 | 3 | 1 | 3/4 | 2 | 8 | 88 | 2.75  |
> |  D8 | RE8 | 8 | 128 | 3 | 1 | 1/4 | 2 | 8 | 280 | 2.2  |

**Feedback**:
Table III contains two rows for the partition D₈/RE₈ in dimension 2N = 8, with different orders (32 vs. 128) and different κ values (3/4 vs. 1/4). A single lattice partition Λ/Λ' has a unique order |Λ/Λ'| = V(Λ')/V(Λ), so two rows with the same Λ and Λ' cannot both be correct unless they refer to different sublattice embeddings or different encoder configurations. It would be helpful to verify which row is correct by computing |D₈/RE₈| = V(RE₈)/V(D₈) explicitly, and to relabel the other row with its correct Λ or Λ' to eliminate the apparent duplication.

---

### 22. Distance-Invariance Asserted for Mod-4 and Depth-3 Codes Without Explicit Regularity Verification

**Status**: [Pending]

**Quote**:
> All codes in this paper are distance-invariant

**Feedback**:
Section IV-B grounds the distance-invariance claim on the regularity of the labeling (Section IV-C). Regularity is established under three sufficient conditions, but for non-linear trellis codes based on mod-4 and higher-depth partitions—such as those using RE₈/2E₈ or Λ₁₆/RΛ₁₆—the paper does not explicitly state which of the three conditions applies. For example, the Class III code based on E₈/RE₈/2E₈ relies on an 'alternative partition E₈/R*E₈/2E₈' whose coset representatives simultaneously serve both levels of the chain; this is a non-trivial structural claim whose proof is deferred to Part II. If the Ungerboeck distance bound does not hold with equality at every level of the chain for these partitions, the labeling may fail to be regular. It would be helpful to either state explicitly which regularity condition covers each code family in Tables VIII–XI, or to add a forward reference to the specific Part II result that establishes regularity for the mod-4 and depth-3/4 cases.

---

### 23. Eight-Class Taxonomy Not Shown to Be Exhaustive or Mutually Exclusive

**Status**: [Pending]

**Quote**:
> In fact, regular labelings (although not necessarily regular Ungerboeck labelings) exist for all partitions used in all the codes covered in this paper.

**Feedback**:
Section VI introduces eight generic code classes (I–VIII) defined by three binary characteristics—partition type, encoder rate, and constraint length—and claims they 'round out the picture' of coset code design. However, the paper does not prove that these classes are exhaustive over the space of binary coset codes with the stated structural constraints, nor that they are mutually exclusive. Several overlaps are noted informally (Class I and Class V coincide for k = 1; Class II and Class VI coincide for the four-state D₄/RD₄ code), but these are treated as coincidences rather than as evidence of a partially redundant taxonomy. It would be helpful to provide a formal decision tree or set of necessary and sufficient conditions that assigns any given (Λ/Λ', C) pair to a unique class, and to state explicitly whether the classification is intended to be illustrative or exhaustive.

---
