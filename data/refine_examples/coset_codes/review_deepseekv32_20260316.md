# A. History

**Date**: 03/16/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper presents a geometrical framework for classifying trellis codes based on binary lattice partitions. It introduces eight new generic code classes and analyzes their performance using parameters like fundamental coding gain and error coefficient. The main result is a synthesis of known and new constructions, leading to an empirical observation about the relationship between the number of trellis states and achievable coding gain.

Below are the most important issues identified by the review panel.

**Ambiguous and non-rigorous definition of fundamental volume for trellis codes**

Multiple reviewers note that the definition of the fundamental volume V(ℂ) for a trellis code in Section IV-B is problematic. It is defined as the volume of the 'time-zero lattice' Λ₀, justified by an intuitive argument about the Cartesian product Λ₀ × Λ₀ × ... filling space. However, this is a heuristic volumetric argument for an infinite-dimensional object, not a rigorous definition analogous to that for finite-dimensional lattices. The paper does not prove that this definition yields a volume measure consistent with the scaling and invariance properties required for the coding gain formula γ(ℂ) = d_min²(ℂ) / V(ℂ)^{2/N} to be meaningful. Since the entire performance comparison framework rests on γ(ℂ), this foundational issue should be addressed by grounding V(ℂ) in the asymptotic point density of code sequences or by providing a more rigorous derivation of the coding gain formula.

**Unsubstantiated claims and incomplete proofs for key lemmas and parameters**

Several critical claims lack rigorous justification. Lemma 5's assertion of equivalence between trellis codes is too strong without clarifying the equivalence relation and may obscure structural insights. Lemma 6's formula d_min²(ℂ) = min[4, d_H(C')] for mod-2 trellis codes assumes an isometric property between Hamming and Euclidean distances that is not proven. Furthermore, the derivations of minimum distance (d_min²) and error coefficient (N₀) for the eight new code classes in Section VI rely on informal bounding arguments and assumptions about labelings and partition uniformity. The paper does not provide general theorems guaranteeing these bounds hold with equality for the specific constructions, nor does it verify the uniformity of coset properties (e.g., that all nonzero cosets have the same number of minimum-norm points) for the listed partitions. These gaps undermine the reliability of the stated performance parameters in Tables IV–XI.

**Inconsistent and confusing handling of real versus complex lattice frameworks**

The paper shifts between real and complex viewpoints for defining key parameters like depth (μ), redundancy (ρ), and duality, leading to potential confusion. For instance, the translation between real 2-depth (m) and complex φ-depth (μ) is given as μ = 2m or 2m-1, but the rationale for choosing between these is not always clear. The duality discussion in Section II-H presents two alternative definitions for the dual of a real lattice, which coincide only for even φ-depth, affecting properties like self-duality. The paper does not consistently specify which definition is primary for subsequent code constructions. This inconsistency complicates the application of definitions throughout the paper and could lead to misinterpretation of code tables and partition properties, especially for odd-depth lattices.

**Overstated claims of classification exhaustiveness and practical relevance**

The paper's title and abstract position it as providing a 'geometrical classification,' and Section VII proposes a 'folk theorem' linking states to coding gain (e.g., two states for 1.5 dB). This theorem is presented as a conclusion but is essentially an empirical observation from the surveyed codes, not a proven theoretical limit. There is no discussion of fundamental limits (e.g., sphere-packing bounds) to validate this trend, nor is it established that the presented classes I-VIII combined with known codes form an exhaustive set. Furthermore, the performance analysis focuses almost exclusively on the fundamental coding gain γ(ℂ), which ignores shaping gain and boundary loss. This dismissal is a significant limitation for practical applications with finite constellations, where boundary loss can be substantial, especially for low-dimensional codes. The claims should be tempered and clearly presented as observed trends, with open questions and practical limitations highlighted.

**Logical gaps in connecting the framework to derived code classes and key examples**

The logical connection between the high-level coset code framework (Sections I-IV) and the eight new code classes (Section VI) is not fully established. The classes are introduced based on binary characteristics, but the rationale for selecting these particular combinations is not explained from first principles (e.g., optimization criteria). They appear as clever constructions rather than systematic deductions from the theory. Additionally, a key example—the Barnes-Wall lattices in Section III—is presented via a code formula but is not explicitly derived as a coset code C(G^N/φⁿG^N; C) within the paper's framework. This leaves a gap in the systematic, unifying presentation. The paper would be stronger if it outlined a design philosophy that naturally leads to the new classes and demonstrated how central examples fit explicitly into the proposed construction method.

**Status**: [Pending]

---

## Detailed Comments (22)

### 1. Incomplete Lemma 4 statement

**Status**: [Pending]

**Quote**:
> Lemma 4: An $N$-dimensional complex $G$-lattice $\Lambda$ is a mod-2 binary lattice if and only if it is the set of all Gaussian integer $N$-tuples that are congruent modulo $\phi^2$ to an $N$-tuple of the form $\phi c_1 + c_0$, where $c_1$ is a codeword in a binary $(N, K)$ code $C_1$, and $c_0$ is a codeword in a binary $(N, J - K)$ code $C_0$ which is a subcode of $C_1$. The redundancy of $\Lambda$ is $r(\Lambda) = 2N - J$, and its minimum squared distance is

**Feedback**:
The lemma statement is incomplete; it cuts off before giving the formula for minimum squared distance. For consistency with Lemma 3 for real lattices, the distance should be $d_{\min}^2(\Lambda) = \min[2, d_H(C_1), d_H(C_0)]$. Complete the lemma by adding: 'and its minimum squared distance is $d_{\min}^2(\Lambda) = \min[2, d_H(C_1), d_H(C_0)]$, where $d_H$ denotes Hamming distance.'

---

### 2. Incorrect citation for Forney et al. paper

**Status**: [Pending]

**Quote**:
> A simple four-dimensional scheme of Gallager was presented by Forney et al. in [1], and a similar scheme was discovered independently by Calderbank and Sloane [10].

**Feedback**:
Reference [1] is earlier cited as Shannon's original work, so it cannot also be the Forney et al. paper. This is a concrete cross-reference error. Rewrite the sentence as: 'A simple four-dimensional scheme of Gallager was presented by Forney et al. in [14], and a similar scheme was discovered independently by Calderbank and Sloane [10].' and update the bibliography accordingly.

---

### 3. Incorrect minimum squared distance for 1PSK

**Status**: [Pending]

**Quote**:
> Although the minimum squared distances within these constellations are somewhat different from those in lattice partitions (e.g., 0.152/0.586/2/4/∞ for these constellations, compared to 1/2/4/8/16 for the comparable two-dimensional lattice partition $Z^2 / RZ^2 / 2Z^2 / 2RZ^2 / 4Z^2$), similar constructions to those presented here often yield good phase-

**Feedback**:
The minimum squared distance within a one-point constellation (1PSK) is 0, not ∞. Using ∞ creates an asymmetric comparison with the lattice partition chain ending at 4Z^2 with distance 16. Rewrite the list as '0.152/0.586/2/4/0' because the minimum squared distance within a single point is zero.

---

### 4. Incorrect sublattice claim for RZ^2

**Status**: [Pending]

**Quote**:
> The points in $R\mathbb{Z}^2$ are a subset of the points in $\mathbb{Z}^2$, meaning that $R\mathbb{Z}^2$ is a sublattice of $\mathbb{Z}^2$.

**Feedback**:
$R\mathbb{Z}^2$ is not a sublattice of $\mathbb{Z}^2$ because, for example, $(1,0) \in \mathbb{Z}^2$ cannot be expressed as $(x+y, x-y)$ with integer $x,y$. $R\mathbb{Z}^2$ is a sublattice of the index-2 sublattice of $\mathbb{Z}^2$ consisting of points with even coordinate sum. Rewrite as: 'The points in $R\mathbb{Z}^2$ are a subset of the points in $\mathbb{Z}^2$ with even coordinate sum, meaning that $R\mathbb{Z}^2$ is a sublattice of that index-2 sublattice of $\mathbb{Z}^2$.'

---

### 5. Norm doubling claim for rotation operator R is incorrect

**Status**: [Pending]

**Quote**:
> For example, $RZ^2$ is a version of $Z^2$ with $d_{\min}^2 = 2$ (the rotation operator $R$ always doubles norms, in any number of dimensions).

**Feedback**:
A pure rotation operator preserves norms; it cannot double them. The lattice with $d_{\min}^2=2$ is a scaled version, e.g., generated by basis vectors (1,1) and (1,-1) with scaling factor $\sqrt{2}$. Rewrite the parenthetical as: '(here $R$ denotes a rotation combined with a scaling by $\sqrt{2}$, which doubles norms).'

---

### 6. Imprecise characterization of D4 coset

**Status**: [Pending]

**Quote**:
> The order of the partition $Z^4 / D_4$ is two, because $Z^4$ is the union of $D_4$ and its coset $D_4 + (1,0,0,0)$ (the set of all integer 4-tuples with an odd number of odd coordinates or, equivalently, with odd norm).

**Feedback**:
The description of the coset is imprecise. $D_4$ consists of integer 4-tuples with even coordinate sum. The coset $D_4 + (1,0,0,0)$ gives vectors with odd coordinate sum. The equivalence to 'odd number of odd coordinates' or 'odd norm' is not accurate. Rewrite as: 'because $Z^4$ is the union of $D_4$ (all integer 4-tuples with even coordinate sum) and its coset $D_4 + (1,0,0,0)$ (all integer 4-tuples with odd coordinate sum).'

---

### 7. Inconsistent depth parameter in generator orthogonality

**Status**: [Pending]

**Quote**:
> that every generator $\phi^{\mu - j - 1} \pmb{g}_j^\perp$ of $\Lambda^\perp / \phi^n \pmb{G}^N$ is orthogonal mod $\phi^\mu$ to every generator $\phi^{j'} \pmb{g}_{j'}$ of $\Lambda / \phi^n \pmb{G}^N$

**Feedback**:
The depth parameter is $\mu$, but the denominator lattices are written as $\phi^n \pmb{G}^N$ with an undefined symbol $n$. This is a typographical error. The correct statement should refer to $\Lambda^\perp / \phi^{\mu} \pmb{G}^N$ and $\Lambda / \phi^{\mu} \pmb{G}^N$. Rewrite the quoted text accordingly.

---

### 8. Table I contains inconsistent complex code formula for H_32

**Status**: [Pending]

**Quote**:
> |  (1,4) | $H_{32}$ | 32 | 3 | $4Z^{32} + 2(32,31,2) + (32,16,8)$ | $\phi^{5}G^{16} + \phi^{2}(16,15,2) + \phi(16,11,4) + (16,5,8)$  |

**Feedback**:
For $\Lambda(1,4)$, the complex depth $\mu = n-r = 3$, so the leading term in the complex code formula should be $\phi^{3} G^{16}$, not $\phi^{5}$. The exponent 5 appears to be a misprint. Correct the entry to: $\phi^{3} G^{16} + \phi^{2}(16,15,2) + \phi(16,11,4) + (16,5,8)$.

---

### 9. Missing closing parenthesis in definition of K(r,n)

**Status**: [Pending]

**Quote**:
> Recall that the Reed-Muller code $\mathrm{RM}(r,n)$, $0\leq n$, $0\leq r\leq n$, is a code of length $N = 2^n$, minimum distance $d_H = 2^{n - r}$, and with $K(r,n) = \sum_{0\leq j\leq r}C_{nj}$ information bits, where $C_{nj}$ is the combinatorial coefficient $(n!)/[(j!)((n - j)!)]$;

**Feedback**:
The expression $(n!)/[(j!)((n - j)!)]$ is missing a closing parenthesis after $(n - j)!$. It should be $(n!)/[(j!)((n - j)!)]$. This is a minor typographical error that should be corrected for precision.

---

### 10. Inconsistent column label $d^2_{max}$(Λ') in Table III

**Status**: [Pending]

**Quote**:
> TABLE III USEFUL LATTICE PARTITIONS
> 
> |  Λ | Λ' | 2N | |Λ/Λ'| | μ | κ | ρ | $d^2_{min}$(Λ) | $d^2_{max}$(Λ') | $\hat{N}_D$ | $\hat{N}_D/|\Lambda/\Lambda'|$  |

**Feedback**:
The column labeled '$d^2_{max}$(Λ')' is non-standard; it likely should be '$d^2_{\min}(\Lambda')$', the minimum squared distance of the sublattice $\Lambda'$, which is relevant for code performance. The current label could mislead readers. Rewrite the header as '$d^2_{\min}(\Lambda')$' and verify the entries correspond to known $d_{\min}^2$ values.

---

### 11. Inconsistent calculation of effective coding gain

**Status**: [Pending]

**Quote**:
> |  4 | $Z^{4}$ | $2D_{4}$ | 128 | 4/5 | 1/2 | 6 | $6/2^{1/2}$ | 6.28 | 728 | 2040 | 4.77  |

**Feedback**:
The effective coding gain $\gamma_{\text{eff}}$ (dB) appears inconsistent with the standard formula $\gamma_{\text{eff}} \approx \gamma - (10/N) \log_{10}(\hat{N}_0)$. For N=4, $\gamma=6.28$ dB, $\hat{N}_0=728$, the penalty is $(10/4)\log_{10}(728)\approx 7.16$ dB, giving $\gamma_{\text{eff}} \approx -0.88$ dB, not 4.77 dB. Either the formula used is different or the values are erroneous. Provide the specific formula used for $\gamma_{\text{eff}}$ or correct the calculation.

---

### 12. Ambiguity in the parameter ρ definition in tables

**Status**: [Pending]

**Quote**:
> |  N | Λ | Λ' | $2^e$ | k/(k+r) | ρ | $d^{2}_{min}$ | γ | dB | $\hat{N}_{0}$ | $\hat{N}_{D}$ | $\gamma_{eff}$(dB)  |

**Feedback**:
The column header 'ρ' is not defined in the table caption or surrounding text. Its meaning (e.g., redundancy per dimension, total redundancy, or code rate redundancy) is ambiguous, and the values do not consistently match any obvious formula. Add a caption or footnote defining ρ explicitly, e.g., 'ρ = r(ℂ)/N, the normalized redundancy of the trellis code' or 'ρ = 1 - (k/(k+r)), the code rate redundancy', and verify the entries.

---

### 13. Inconsistent notation for convolutional code rate in Lemma 6

**Status**: [Pending]

**Quote**:
> **Lemma 6**: If $\Lambda'$ is a mod-2 lattice, $C$ is a $2^r$-state, rate-$k / (k + r)$ convolutional code and the labeling map $c(a)$ is linear modulo $\Lambda'$, then a trellis code $\mathbb{C}(\Lambda / \Lambda'; C)$ is the set of all sequences of integer $N$-tuples that are congruent modulo 2 to one of the words in a $2^r$-state rate- $[N - r(\mathbb{C})] / N$ convolutional code $C'$.

**Feedback**:
The rate expression $[N - r(\mathbb{C})]/N$ is likely incorrect. From the construction, $C'$ has $k + r(\Lambda)$ input bits per $N$ output bits, so its rate should be $(k + r(\Lambda))/N$. Using $r(\mathbb{C}) = r + r(\Lambda)$, this equals $(r(\mathbb{C}) - r + r(\Lambda))/N$, which simplifies to $(k + r(\Lambda))/N$ only if $k = N - r(\mathbb{C}) - r(\Lambda)$? There is no justification for the given expression. Rewrite the rate of $C'$ as $(k + r(\Lambda))/N$ or provide a derivation.

---

### 14. Define $d_H(C')$ in Lemma 6

**Status**: [Pending]

**Quote**:
> The redundancy of $\mathbb{C}$ is $r(\mathbb{C}) = r + r(\Lambda)$, and its minimum squared distance is $d_{\min}^2(\mathbb{C}) = \min[4, d_H(C')]$.

**Feedback**:
The notation $d_H(C')$ is used without definition. From context, $C'$ is a binary convolutional code, so $d_H(C')$ should denote its minimum Hamming distance (free distance). To ensure clarity, add a definition immediately after its first use: 'where $d_H(C')$ is the minimum Hamming distance (free distance) of the binary convolutional code $C'$.'

---

### 15. Unclear equivalence to partition $Z^N/2Z^N$ in Lemma 6 proof sketch

**Status**: [Pending]

**Quote**:
> By the extension of Lemma 5, $\mathbb{C}$ is equivalent to a code based on the partition $Z^{N} / 2Z^{N}$, where the augmented encoder $C'$ has $N$ output bits and redundancy $r(C') = r + r(\Lambda)$.

**Feedback**:
The sketch invokes 'the extension of Lemma 5' without explanation or reference. Readers may not know what conditions guarantee equivalence. Briefly outline the equivalence: because $\Lambda'$ is a mod-2 lattice, Lemma 3 implies $\Lambda = 2Z^N + C_\Lambda$ and $\Lambda' = 2Z^N + C_{\Lambda'}$; the partition $\Lambda/\Lambda'$ can be mapped to $Z^N/2Z^N$ via a linear labeling. Add a sentence to clarify.

---

### 16. Regular labeling condition (c) may not hold for all Cartesian products

**Status**: [Pending]

**Quote**:
> c) if $\Lambda$ and $\Lambda'$ are $N$-fold Cartesian products $\Lambda^N$ and $(\Lambda')^N$, and the labeling for $\Lambda^N / (\Lambda')^N$ is the $N$-fold Cartesian product of a regular labeling for $\Lambda / \Lambda'$, e.g., when the partition is $G^N / \phi^3 G^N$ or $Z^N / 4Z^N$.

**Feedback**:
For a Cartesian product labeling, the mod-2 sum of two $N$-tuple labels is another $N$-tuple, not a single bit. The definition of regularity would need to be generalized to 'function only of the component-wise mod-2 sum' for condition (c) to hold. Without clarification, the claim is ambiguous. Rewrite condition (c) to specify component-wise regularity.

---

### 17. Missing definition of time-zero lattice for trellis codes

**Status**: [Pending]

**Quote**:
> Define $\mathbb{C}_t$ as the set of all code sequences that start at time $t$ or later. By time-invariance, all such sets are isomorphic to each other and to a particular such set, say $\mathbb{C}_0$. How- <!-- PAGE BREAK --> IEEE TRANSACTIONS ON INFORMATION THEORY, VOL. 34, NO. 5, SEPTEMBER 1988

**Feedback**:
The definition of the time-zero lattice $\Lambda_0$ is incomplete and cut off by a page break. Readers need a clear definition: $\Lambda_0$ is the projection of $\mathbb{C}_0$ onto the time-zero coordinates, and by time-invariance it is a lattice. Rewrite the passage to explicitly define $\Lambda_0$ and its role in the volume calculation $V(\Lambda_0) = 2^{-k}V(\Lambda')$.

---

### 18. Inconsistent notation for convolutional code rate in Section IV-A

**Status**: [Pending]

**Quote**:
> A trellis code is a coset code $\mathbb{C}(\Lambda / \Lambda'; C)$ as shown in Fig. 1, where $C$ is a rate-$k / (k + r)$ convolutional code. In this paper $C$ will always be a binary convolutional code, and $\Lambda$ and $\Lambda'$ binary lattices, generally mod-2 or mod-4.

**Feedback**:
The notation uses $r$ both for the number of redundant bits in the convolutional code rate $k/(k+r)$ and for the number of states $2^r$. For a rate-1/2 code with 4 states, this would imply $r=1$ for the rate but $r=2$ for the states, causing confusion. Define $C$ as a rate-$k/n$ binary convolutional code with constraint length $\nu$, so that the trellis has $2^\nu$ states and each branch label is an $n$-bit tuple.

---

### 19. Missing definition of labeling function c(a)

**Status**: [Pending]

**Quote**:
> The codewords in a rate-$k / (k + r)$ convolutional code may be expressed as sequences $(a_{i}, a_{i+1}, \dots)$ of binary $(k + r)$-tuples $a_{j}$, which serve as labels that select cosets $\Lambda' + c(a_{j})$ of $\Lambda'$ in the partition $\Lambda / \Lambda'$.

**Feedback**:
The function $c(a)$ mapping a binary $(k+r)$-tuple to a coset representative is not defined. For the construction to be well-defined, $c$ must be a bijection between $\{0,1\}^{k+r}$ and a set of coset representatives modulo $\Lambda'$, and for linearity, it should be linear modulo $\Lambda'$. Add a sentence: 'The labeling function $c: \{0,1\}^{k+r} \to \Lambda$ assigns to each label $a$ a coset representative $c(a)$ such that the cosets $\{\Lambda' + c(a)\}$ are distinct and partition $\Lambda$.'

---

### 20. Incorrect algebraic structure of convolutional code

**Status**: [Pending]

**Quote**:
> It follows that a convolutional code is a vector space over
> 
> the field of binary formal power series $f(D), f_{i} \in \{0,1\}$; the dimension of this vector space is $k$, and any codeword $a(D)$ can be written as $a(D) = \sum_{j} f_{j}(D) g_{j}(D)$, where the $g_{j}(D), 1 \leq j \leq k$, are a set of $k$ generator sequences that form a generator matrix $G$; see [20].

**Feedback**:
The set of binary formal power series forms a ring, not a field (e.g., $D$ has no multiplicative inverse). A convolutional code is a module over this ring, not a vector space. The dimension $k$ refers to the rank as a free module. Rewrite as: 'It follows that a convolutional code is a module over the ring of binary formal power series; the module has rank $k$, and any codeword $a(D)$ can be written as $a(D) = \sum f_j(D) g_j(D)$, where the $g_j(D), 1 \le j \le k$, are a set of $k$ generator sequences that form a generator matrix $G$.'

---

### 21. Unjustified Hamming distance bound for four-state code

**Status**: [Pending]

**Quote**:
> The minimum Hamming distance of this code (taking the outputs as $c(a)$) is five, because the distance between distinct paths is at least two where they diverge, two where they merge, and one somewhere in between.

**Feedback**:
The reasoning sums minimum distances over disjoint segments (2+2+1) to lower bound total Hamming distance, but this assumes the differences occur in distinct coordinate sets, which is not guaranteed for a two-branch error event. The distance could be 4. Without the generator matrix, the claim of distance 5 cannot be verified. Either provide the generator to confirm distance 5 or adjust the claim to 'at least four'.

---

### 22. Missing error coefficient for Wei code in Table VII

**Status**: [Pending]

**Quote**:
> |  16 | $Z^{16}$ | $H_{16}$ | 32 | 4/5 | 1/8 | 4 | $2^{15/8}$ | 5.64 |  | 228 |   |

**Feedback**:
The table has blank entries for $\hat{N}_0$ and $\gamma_{\mathrm{eff}}$(dB). Blanks may mislead readers into thinking the values are zero or missing. Add a note in the caption or a sentence in the text: 'Blank entries indicate that the error coefficient $\hat{N}_0$ was not computed or is unknown.'

---
