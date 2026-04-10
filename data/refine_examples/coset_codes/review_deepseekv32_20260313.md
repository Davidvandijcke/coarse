# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/13/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper proposes a geometrical framework for classifying and analyzing coset codes, particularly those based on binary lattice partitions, for band-limited Gaussian channels. It defines key parameters like fundamental coding gain and normalized decoding complexity, and uses these to compare various known code families (e.g., Ungerboeck, Wei, Calderbank-Sloane) as well as new generic classes. The main result is a unified characterization suggesting that trellis codes often offer a better performance-complexity trade-off than lattice codes, culminating in an empirical 'folk theorem' relating coding gain to decoder state complexity.

Below are the most important issues identified by the review panel.

**Ambiguous and Non-Rigorous Foundation for Key Definitions**

The paper's core analytical framework relies on definitions and derivations that lack formal rigor. The definition of the fundamental volume V(ℂ) for an infinite-dimensional trellis code sequence is not standard and lacks a measure-theoretic foundation, yet it underpins the central performance metric, the fundamental coding gain γ(ℂ). Furthermore, Lemma 5's claim of equivalence between trellis codes and codes based on the integer lattice partition is overstated, as it only establishes a set equivalence while ignoring crucial differences in decoding complexity and error performance. The 'Ungerboeck distance bound' is applied without explicitly stating its critical condition—that coset representatives must be minimal-norm vectors—which risks overstating the minimum distance for some constructions.

**Overstated Scope and Universality of the Binary Lattice Framework**

The paper claims its coset code framework based on binary lattice partitions captures 'practically all known good constructive coding techniques,' but this universality is not substantiated. The analysis is explicitly restricted to binary lattices, with only cursory mentions of other important classes like phase-modulated (PSK) or ternary codes. The classification also systematically covers only 'decomposable' lattices, acknowledging that notable indecomposable lattices (e.g., the Leech lattice) exist. This creates a significant scope limitation: the presented geometrical classification is not comprehensive, and the paper does not justify why the binary lattice restriction is sufficient or discuss the potential performance trade-offs of this class compared to alternatives.

**Inconsistent and Heuristic Performance Metrics Undermine Comparisons**

The performance comparisons in the paper rely on inconsistently applied and heuristically justified metrics. The 'effective coding gain' γ_eff adjusts the fundamental gain by an ad-hoc rule (0.2 dB penalty per factor of two in error coefficient) that is presented without derivation or citation, and its universal applicability is questionable. This rule is applied to trellis codes but not to lattice codes, creating an internal bias in the conclusion that trellis codes are superior. Furthermore, the normalized decoding complexity metric Ñ_D is used extensively in tables and plots, but its calculation is opaque, referenced to algorithms in another paper without justification for why it is the appropriate basis for comparison across different code dimensionalities and structures.

**Incomplete Treatment of Shaping and Practical System Performance**

The paper deliberately focuses on 'fundamental coding gain' γ(C) and dismisses the 'total coding gain' γ_tot(C), which includes shaping gain, as peripheral and confusing. This is a major limitation because shaping gain (up to 1.53 dB) is a critical component of practical system design with finite constellations and power constraints. By decoupling code structure from constellation shaping, the performance comparisons (e.g., in Tables and Figure 12) may not reflect the actual realized gain of implemented codes. The paper should explicitly acknowledge that γ(C) is a theoretical invariant for comparing code structures under its simplified model, and that γ_tot(C) is ultimately the relevant metric for system performance.

**Unsubstantiated Claims Regarding Capacity and Code Optimality**

The paper makes strong, aspirational claims that are not supported within its analysis. It states that coset codes 'seem to provide a general approach... that approach channel capacity,' but it provides no connection between the geometrical parameters (γ(C), ρ(C)) and the Shannon limit, nor any discussion of spectral efficiency or achievable rates. Additionally, the 'folk theorem' relating coding gain to decoder state complexity is presented as an empirical observation without any information-theoretic or combinatorial justification, misleadingly elevating it to a theoretical principle. The paper also concludes that 'little improvement has been achieved over Ungerboeck's original results' without backing this with a systematic code search or known bounds, leaving the optimality of the presented codes an open question.

**Insufficient Discussion of Decoding Assumptions and Channel Model Limitations**

The analysis of decoding complexity and the performance-complexity trade-offs rests on unexamined assumptions. The complexity metric Ñ_D is derived from specific 'trellis-based decoding algorithms' referenced in Part II, but the paper assumes these algorithms are standard or optimal without proof. More efficient decoders for some code classes could alter the complexity rankings. Furthermore, the entire framework is predicated on the AWGN channel model. The paper does not discuss the robustness of the geometrical classification or the relevance of parameters like d_min²(C) under other channel conditions (e.g., fading), which is a significant scope limitation given the claim of providing a general approach for band-limited channels.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Incorrect formula for fundamental coding gain

**Status**: [Pending]

**Quote**:
>  and the redundancy $r(\Lambda)$ of the lattice $\Lambda$. In fact,
> 
> $$
> \gamma (\mathbb {C}) = 2 ^ {- \rho (\mathbb {C})} d _ {\min } ^ {2} (\mathbb {C})
> $$
> 
> where the normalized redundan

**Feedback**:
The formula for fundamental coding gain is inconsistent with the standard definition. The standard definition is γ(ℂ) = d_min²(ℂ) / V(ℂ)^{2/N}. For binary lattices, V(ℂ) = 2^{r(ℂ)} and ρ(ℂ) = 2r(ℂ)/N, so V(ℂ)^{2/N} = 2^{ρ(ℂ)}. Therefore, the correct formula should be γ(ℂ) = d_min²(ℂ) / 2^{ρ(ℂ)}. The presented formula has the exponent sign reversed, which would propagate to numerical calculations.

---

### 2. Incorrect minimum squared distance derivation for Ungerboeck code

**Status**: [Pending]

**Quote**:
> It is easy to see that the minimum squared distance between code sequences corresponding to distinct paths in the trellis is the minimum Hamming distance between sequences $c(D)$ of coset representatives and thus is equal to $d_H(C) = 5$. However, since $d_{\min}^2(2Z^2) = 4$, the minimum squared distance of the trellis code is $d_{\min}^2(\mathbb{C}) = 4$.

**Feedback**:
The reasoning incorrectly equates Hamming distance to squared Euclidean distance. The minimum squared distance for a single branch (parallel transition) is the minimum squared distance between coset representatives of 2Z² in Z², which is 1, not 4. The overall d_min²(ℂ) should be the minimum of the squared Euclidean distance accumulated over the shortest error event and the parallel transition distance. The derivation must correctly account for the squared Euclidean distance per differing branch, not just the Hamming distance.

---

### 3. Inconsistent distance bound derivation for Class II codes

**Status**: [Pending]

**Quote**:
> Because the distance between paths is at least $d_{\min}^2(\Lambda)$ when they diverge, $d_{\min}^2(\Lambda)$ when they merge, and $d_{\min}^2(\Lambda)$ in some other time unit, the distance between distinct paths is at least $3d_{\min}^2(\Lambda)$. Thus $d_{\min}^2(\mathbb{C}) = d_{\min}^2(\Lambda') = 2d_{\min}^2(\Lambda)$

**Feedback**:
The two statements are mathematically inconsistent: a lower bound of 3d_min²(Λ) cannot equal 2d_min²(Λ). The reasoning leading to the lower bound of 3d_min²(Λ) is unclear and does not directly yield the final claimed equality. The derivation should be corrected to show that d_min²(ℂ) = d_min²(Λ') follows logically from the code structure and the partition distances, without the contradictory intermediate step.

---

### 4. Incorrect rate formula in Lemma 5 alternative form

**Status**: [Pending]

**Quote**:
> where $C'$ is a $2^{\nu}$-state, rate-$[2Nm - r - r(\Lambda)-r(C)] / 2Nm$ convolutional code

**Feedback**:
The expression for the rate of convolutional code C' appears to subtract redundancies twice. The correct number of information bits per 2Nm dimensions should be 2Nm - r - r(Λ), where r is the redundancy of the original convolutional code C. The term r(C) is redundant; r(C) is simply r. The rate should be [2Nm - r - r(Λ)] / 2Nm.

---

### 5. Missing condition for existence of order-2 vector

**Status**: [Pending]

**Quote**:
> If $\Lambda_{k + 1} \neq \Lambda$, then a vector $\mathbf{g}_k$ exists in $\Lambda$ that is not in $\Lambda_{k + 1}$ but has order 2 mod $\Lambda_{k + 1}$, i.e., such that $\mathbf{g}_k + \mathbf{g}_k \in \Lambda_{k + 1}$ (see part II).

**Feedback**:
The existence of such a vector 𝐠_k is not guaranteed without an additional condition on the sublattice Λ_{k+1}. For the quotient group Λ/Λ_{k+1} to be a vector space over 𝔽₂, we require 2Λ ⊆ Λ_{k+1}. The proof should explicitly state that Λ_{k+1} is chosen such that 2Λ ⊆ Λ_{k+1} (or that Λ_{k+1} is a mod-2 sublattice), which ensures every non-zero element in the quotient has order 2.

---

### 6. Inconsistent definition of time-zero lattice

**Status**: [Pending]

**Quote**:
> Define two code sequences as equivalent modulo $\mathbb{C}_{t+1}$ if their first difference is at time $t$ or later. Two sequences in $\mathbb{C}_0$ are then equivalent modulo $\mathbb{C}_1$ if and only if their first element $c_0$ is the same. Let $\Lambda_0$ then be the set of all possible first elements $c_0$; that is, $\Lambda_0 = \{\lambda : \lambda \in \Lambda' + c(a_0)\}$, where $a_0$ is a possible time-zero output from the encoder $C$ given that all previous outputs were zero or, equivalently, given that the encoder starts in the zero state. There are $2^k$ such $a_0$, and thus $\Lambda_0$ is the union of $2^k$ cosets of $\Lambda'$. Ordinarily, $\Lambda_0$ is a lattice, which we call the time-zero lattice. By Lemma 1, $V(\Lambda_0) = 2^{-k}V(\Lambda')$; since $V(\Lambda') = 2^{k+r}V(\Lambda)$, we also have $V(\Lambda_0) = 2^r V(\Lambda)$.

**Feedback**:
The application of Lemma 1 requires that Λ_0 be a sublattice of Λ'. The text states 'Ordinarily, Λ_0 is a lattice,' but this is an assumption not guaranteed by the construction. For Lemma 1 to apply, the set of possible first elements must form a group (a sublattice). The condition for Λ_0 to be a sublattice (i.e., that the set of possible a_0 forms a group under addition modulo Λ') should be stated explicitly, or the claim should be qualified.

---

### 7. Ambiguous definition of linearity for labeling map

**Status**: [Pending]

**Quote**:
> A trellis code $\mathbb{C}$ has little chance of being linear unless the mapping $c(a)$ from encoder output $(k + r)$-tuples (labels) $a$ to coset representatives $c$ is linear modulo $\Lambda'$, as in Lemma 2; i.e., $c(\mathbf{a}) = \mathbf{a}G$, where $G = \{\mathbf{g}_j, 1 \leq j \leq k + r\}$ is a generator matrix of $k + r$ vectors of $\Lambda$ that span $\Lambda$, modulo $\Lambda'$.

**Feedback**:
The phrase 'span $\Lambda$, modulo $\Lambda'$' is unclear. The vectors 𝐠_j need to be linearly independent modulo Λ' to generate all distinct cosets, but they do not need to span the entire lattice Λ. To avoid confusion, clarify: 'i.e., $c(\mathbf{a}) = \mathbf{a}G$, where $G = \{\mathbf{g}_j, 1 \leq j \leq k + r\}$ is a set of vectors in Λ that are linearly independent modulo Λ' (so that the cosets Λ' + 𝐚G are all distinct).'

---

### 8. Inconsistent specification of convolutional code rates

**Status**: [Pending]

**Quote**:
> The convolutional code $C$ is either a rate-$k/2k$ code, with $|\Lambda / \Lambda'| = 2^{2k}$ or else $|\Lambda / \Lambda'| = |\Lambda' / \Lambda''| = 2^k$, or a rate-$k/(k+1)$ code, with $|\Lambda / \Lambda'| = 2^{k+1}$ or else $|\Lambda / \Lambda'| = 2$ and $|\Lambda' / \Lambda''| = 2^k$.

**Feedback**:
The description mixes different scenarios without clear separation, which could confuse readers. For clarity, separate the cases: 'The convolutional code C is either a rate-k/2k code used with a partition Λ/Λ' of order 2^{2k}, or a rate-k/(k+1) code used with a partition Λ/Λ' of order 2^{k+1}. Alternatively, for a partition chain Λ/Λ'/Λ'', we may use a rate-k/2k code where |Λ/Λ'| = |Λ'/Λ''| = 2^k, or a rate-k/(k+1) code where |Λ/Λ'| = 2 and |Λ'/Λ''| = 2^k.'

---

### 9. Incorrect minimum squared distances for PSK constellations

**Status**: [Pending]

**Quote**:
> Although the minimum squared distances within these constellations are somewhat different from those in lattice partitions (e.g., 0.152/0.586/2/4/∞ for these constellations, compared to 1/2/4/8/16 for the comparable two-dimensional lattice partition $Z^2 / RZ^2 / 2Z^2 / 2RZ^2 / 4Z^2$), similar constructions to those presented here often yield good phase-

**Feedback**:
The value ∞ for 1PSK (a 1-point constellation) is misleading, as there is no distance between distinct points. The sequence should be corrected to 0.152/0.586/2/4/— (or undefined) to accurately reflect that the 1-point case is degenerate.

---

### 10. Ambiguous definition of redundancy r(Λ) for lattice Λ

**Status**: [Pending]

**Quote**:
> the fundamental volume $V(\mathbb{C})$ per $N$ dimensions, which is equal to $2^{r(\mathbb{C})}$ where the redundancy $r(\mathbb{C})$ is equal to the sum of the redundancy $r(C)$ of the encoder $C$ and the redundancy $r(\Lambda)$ of the lattice $\Lambda$.

**Feedback**:
The term 'redundancy of the lattice Λ', denoted r(Λ), is used without a clear definition. Readers might misinterpret it as coding redundancy rather than a logarithmic volume measure. To avoid confusion, add a clarifying phrase: 'where r(Λ) is defined such that the fundamental volume of Λ is V(Λ)=2^{r(Λ)} (for binary lattices, r(Λ) is the redundancy in bits per N dimensions).'

---

### 11. Inconsistent notation for partition order

**Status**: [Pending]

**Quote**:
> The sublattice induces a partition $\Lambda / \Lambda'$ of $\Lambda$ into $|\Lambda / \Lambda'|$ cosets of $\Lambda'$, where $|\Lambda / \Lambda'|$ is the order of the partition; when $\Lambda$ and $\Lambda'$ are binary lattices, the order of the partition is a power of 2, say $2^{k + r}$, and correspondingly, the partition divides the signal constellation into $2^{k + r}$ subsets, each corresponding to a distinct coset of $\Lambda'$.

**Feedback**:
The symbols k and r are introduced ambiguously. Later, a 'rate-k/(k+r)' encoder is mentioned, and r(C) is defined as r bits per N dimensions. To improve clarity and consistency, denote the partition order as 2^K. Then state that the encoder is rate-k/K, with redundancy r(C) = K - k. This aligns with the later usage of r(C).

---

### 12. Ambiguous definition of normalized redundancy μ(ℂ)

**Status**: [Pending]

**Quote**:
> Thus if we define the normalized redundancy, informativity, and depth of the trellis code $\mathbb{C}$ as the sums of the corresponding quantities for the code $C$ and partition $\Lambda /\Lambda'$, where we regard the depth of $C$ as 0, then we get expressions analogous to those that we obtained for lattices.

**Feedback**:
Later, the text uses μ(ℂ) in the expression γ(ℂ) = 2^{-μ(ℂ)} d_min²(ℂ), but μ is typically depth, not normalized redundancy. For a lattice, ρ(Λ) = μ(Λ) - κ(Λ). The usage of μ(ℂ) interchangeably with ρ(ℂ) is misleading. The notation should be consistent: use ρ(ℂ) for normalized redundancy to avoid confusion with depth μ(ℂ).

---

### 13. Ambiguous reading order recommendation

**Status**: [Pending]

**Quote**:
> The reader who desires to read both papers in the most logical order is advised to skim this paper quickly through Section II, omitting proofs; then to read part II, with primary focus on the material relating to Barnes-Wall lattices; and then to return to the rest of this paper.

**Feedback**:
The phrase 'skim this paper quickly through Section II' could be interpreted as skimming only Section II, not Sections I and II. To avoid ambiguity, specify the exact sections: 'skim this paper quickly through Section II (i.e., Sections I and II)'.

---

### 14. Ambiguous claim about coding theorem application

**Status**: [Pending]

**Quote**:
> Another longtime proponent of lattices in communications, also in Canada, has been deBuda, who proved that the coding theorem applies to lattice codes [5].

**Feedback**:
The phrasing is ambiguous and potentially misleading. Shannon's coding theorem applies to all codes meeting its conditions. De Buda's contribution likely showed that lattice codes can achieve channel capacity under appropriate conditions. The text should clarify the actual contribution to avoid misinterpretation.

---

### 15. Inconsistent reference to companion paper

**Status**: [Pending]

**Quote**:
> A more comprehensive introduction to this family of lattices is given in the companion paper [18], hereafter referred to as part II.

**Feedback**:
The citation [18] is used for the companion paper, but the text should explicitly state that [18] is Part II to avoid ambiguity. The phrase 'hereafter referred to as part II' is clear, but adding '(Part II)' after the citation would improve clarity for readers skimming the references.

---
