# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/13/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a unified framework for coset codes on band-limited AWGN channels, showing that a wide range of known coded modulation schemes—including Ungerboeck trellis codes, Wei multidimensional codes, and Calderbank–Sloane lattice codes—can be characterized as coset codes defined by binary lattice partitions and linear binary encoders. The framework introduces a systematic taxonomy of eight generic code classes (I–VIII) organized by partition type, encoder rate, and constraint length, and evaluates each class using fundamental coding gain γ and error coefficient Ñ₀. The paper concludes that the identified classes cover the practically important design space and that significantly better codes are unlikely to be found within this framework.

Below are the most important issues identified by the review panel.

**Asymptotic Coding Gain as Primary Metric Obscures Finite-SNR Performance and Creates Inconsistent Comparisons**

Throughout Sections IV–VII, the fundamental coding gain γ(C) is treated as the definitive performance metric, with the error coefficient Ñ₀ corrected only via a rule of thumb that every factor-of-two increase in Ñ₀ costs roughly 0.2 dB. This heuristic is stated without derivation, without specifying the target error rate range over which it is valid, and without acknowledging its dependence on the slope of the Q-function approximation at a particular operating point. The paper's own Table V shows cases where Ñ₁ or Ñ₂ dominates (starred entries), meaning γ_eff computed from Ñ₀ alone can be misleading—for example, the 128-state Ungerboeck Z²/2RZ² code (Ñ₀ = 344) versus the 128-state Pottie–Taylor code (Ñ₀ = 8) at the same d²_min. More critically, the paper explicitly declines to compute γ_eff for lattice codes because 'our rule of thumb is questionable when the number of nearest neighbors is so high,' yet uses the same rule to compare trellis codes against each other and against lattice codes indirectly—an asymmetric application that biases the conclusion that trellis codes outperform lattice codes. For Class V and VI codes with Ñ₀ in the hundreds or thousands, the single-term correction is insufficient to characterize practical performance. It would be helpful to either derive a more principled bound on the effective coding gain penalty (e.g., via the explicit union bound), apply it consistently to both lattice and trellis codes, extend the analysis to include at least Ñ₁ for all code classes, or explicitly restrict performance comparisons in Section VII to the asymptotic regime.

**The Eight-Class Taxonomy Is Not Shown to Be Exhaustive or Mutually Exclusive, Yet Supports a Strong Optimality Claim**

Section VI introduces eight code classes (I–VIII) defined by three binary choices—partition type (single vs. two-level chain), encoder rate (k/2k vs. k/(k+1)), and constraint length (k vs. 2k)—and presents them as a systematic enumeration of the design space. However, no argument is given that these eight combinations cover all practically important structures, nor that the classes are disjoint. The paper itself notes that the two-state Class I and Class V codes coincide, and that the four-state Class II and Class VI D₄/RD₄ codes are identical. The classification also excludes rate-k/(k+r) encoders with r > 1, multi-level partition chains of depth greater than two, non-uniform memory structures, and encoders exploiting the full automorphism group of the partition lattice. The claim in Section VII that 'there is little likelihood of finding significantly better codes' rests implicitly on this classification being comprehensive—a claim that is not formally established. It would be helpful to either prove a completeness result for the taxonomy, verify that each known code from Section V falls into exactly one class or is provably outside the framework, or explicitly restrict the scope of the optimality conclusion to the structural families actually enumerated.

**Coding Gain Baseline Is Not Uniformly Appropriate Across Code Dimensions, Conflating Shape Gain with Coding Gain**

The fundamental coding gain γ(C) is defined relative to an uncoded system using Z^N constellations (Section II-C, property e), which is natural for two-dimensional QAM but becomes increasingly artificial as dimension N grows. The paper itself acknowledges (Section I-B) that the shape gain of an N-sphere over an N-cube grows with N, reaching πe/6 ≈ 1.53 dB as N → ∞, and explicitly excludes this from γ(C). When comparing, for example, a 16-dimensional Wei code (ρ = 1/8) against a two-dimensional Ungerboeck code (ρ = 1) in Fig. 12(b) and Table VII using γ alone, the 16-dimensional code benefits from a lower normalized redundancy that is partly an artifact of spreading redundancy over more dimensions rather than a genuine coding advantage. The paper acknowledges this issue briefly in Section VII (point 3) but does not adjust the comparison framework. It would be helpful to either normalize all gains to a common spectral efficiency and constellation expansion factor, or to add a column to Tables IV–XI giving the shape-gain component separately from the coding-structure component of γ, so that cross-dimensional comparisons in Fig. 12 and Section VII rest on a consistent footing.

**Decoding Complexity Figures Cannot Be Verified from Part I Alone, and the Folk Theorem Conflates Complexity Metrics**

Tables II, III, and IV–XI report normalized decoding complexity Ñ_D defined as the number of binary operations required by 'the trellis-based decoding algorithms of Part II,' but Part II is a companion paper whose algorithms are neither reproduced nor sketched in Part I. The complexity figures—for example, Ñ_D = 280 for D₈/RE₈ at order 128 and Ñ_D ≈ 3792 for Z⁸/2E₈ at order 2¹¹—cannot be verified from the material in Part I alone, yet they are central to the performance-versus-complexity comparisons of Section VII and Figure 12. Additionally, the paper notes that 'if it is simpler to decode RΛ/RΛ' than Λ/Λ', the lesser Ñ_D is given,' introducing an implicit optimization that is not systematically described; it would be helpful to clarify whether the two D₈/RE₈ entries in Table III (orders 32 and 128) represent genuinely distinct partitions or contain a typographical error, since the order is a partition invariant. Compounding this, the concluding folk theorem—'it takes two states to get 1.5 dB, four states to get 3 dB, ...'—uses encoder state count 2^ν as the complexity measure, yet the paper's own data show that a 16-state Class V code based on H₁₆/Λ₁₆ has Ñ_D ≈ 5632 while a 256-state one-dimensional Ungerboeck code has Ñ_D = 3072, making the nominally simpler code actually more complex to decode. It would be helpful to include at least a summary formula or bounding argument for Ñ_D in Part I, and to restate the folk theorem in terms of Ñ_D or qualify it to apply only within a fixed dimension and partition family.

**Linearity, Distance-Invariance, and Minimum Distance Tightness Are Asserted Rather Than Verified for Several Code Classes**

Section IV-B asserts that 'all codes in this paper are distance-invariant,' and Section IV-C states that 'regular labelings exist for all partitions used in all the codes covered in this paper.' For the mod-2 lattice case, Lemma 6 provides a rigorous proof of linearity. However, for the mod-4 and higher-depth partitions used in Classes III–VIII (e.g., E₈/RE₈, Λ₁₆/RΛ₁₆, D₄/2D₄), the paper relies on condition (b) of Section IV-C—that the Ungerboeck distance bound holds with equality—without proving this for each partition, deferring verification to Part II. If the bound does not hold with equality for some partition, the stated d²_min values in Table XI could be overestimates. A related gap appears in the minimum distance arguments for Class IV (and Class VIII) codes: the paper argues a path-distance lower bound of 5d²_min(Λ) but concludes d²_min(C) = 4d²_min(Λ) = d²_min(Λ''), which is consistent only if the parallel-transition distance is the binding constraint—yet the paper does not verify that this distance is actually achieved, nor that no path pair achieves exactly 4d²_min(Λ) through a combination of divergence and convergence. Similarly, the minimum distance formula for mod-4 decomposable lattices in Lemma 3 implicitly assumes that the minimum-norm element of a coset is the binary codeword itself, which may not hold for indecomposable or partially decomposable cases. It would be helpful to either prove the regularity and distance-tightness conditions for each partition class used in Section VI, or to clearly identify which specific cases require case-by-case verification in Part II.

**Scope of the Unification Claim Exceeds What the Formal Framework Establishes for Non-Binary and Non-Linear Structures**

The abstract and Section I-B claim that 'practically all known good constructive coding techniques for band-limited channels can be characterized as coset codes,' and Section VII concludes that 'there is little likelihood of finding significantly better codes.' Both claims are implicitly conditioned on the AWGN channel with Euclidean distance as the sole metric and on restriction to binary (mod-2 or mod-4) lattice partitions with linear binary encoders. The paper briefly mentions in Section I-C that phase-modulated codes, ternary codes, and nonlinear codes exist but defers their treatment to companion papers—including a Part III listed as 'in preparation, 1989' that was never published. The formal framework of Sections II–VI is restricted entirely to binary lattice partitions, and Lemma 5 establishes equivalence only within this binary class. Furthermore, the paper notes that 'these code constructions rely very little on the linearity properties of the groups' and that 'the codes so constructed are often not linear,' yet the distance analysis throughout (Lemmas 3, 4, 6, and the class descriptions in Section VI) relies on linearity to establish distance-invariance and compute d²_min. For fading channels, burst-noise channels, or channels requiring rotational invariance, the Euclidean distance metric and coding gain hierarchy can change substantially, and codes suboptimal under AWGN may become superior. It would be helpful to add explicit scope statements to the abstract and to the conclusions of Section VII limiting the classification and optimality claims to the AWGN setting with binary lattice partitions, and to more carefully delineate which results apply only to linear binary coset codes.

**Status**: [Pending]

---

## Detailed Comments (19)

### 1. Abstract universality claim broader than binary-encoder definition supports

**Status**: [Pending]

**Quote**:
> Practically all known good constructive coding techniques for band-limited channels, including lattice codes and various recently proposed trellis-coded modulation schemes, can be characterized as coset codes. A coset code is defined by a lattice partition $\Lambda / \Lambda'$ and by a binary encoder $C$ that selects a sequence of cosets of the lattice $\Lambda'$.

**Feedback**:
The opening universality claim covers 'practically all known good constructive coding techniques,' yet the definition in the very next sentence restricts to a binary encoder C. The paper's own Section I-C acknowledges that phase-modulated, ternary, and nonlinear codes exist and are not covered by this binary-encoder definition. It would be helpful to qualify the first sentence with '(primarily for AWGN channels with binary lattice partitions)' and to rewrite 'a binary encoder C' as 'an encoder C (typically binary)' so that the scope of the claim matches the scope of the formal framework.

---

### 2. Error coefficient described as 'purely geometric' but depends on encoder C

**Status**: [Pending]

**Quote**:
> The fundamental coding gain of a coset code, as well as other important parameters such as the error coefficient, the decoding complexity, and the constellation expansion factor, are purely geometric parameters determined by $C$ and $\Lambda / \Lambda'$.

**Feedback**:
The phrase 'purely geometric' is misleading for the error coefficient Ñ₀ and decoding complexity Ñ_D: both depend on the combinatorial trellis structure of the specific encoder C, not on the partition geometry alone. The paper's own Table V illustrates this—the 128-state Ungerboeck Z²/2RZ² code has Ñ₀ = 344 while the Pottie–Taylor code at the same d²_min and partition has Ñ₀ = 8. Rewrite 'are purely geometric parameters determined by C and Λ/Λ'' as 'are parameters determined by the geometry of Λ/Λ' and the combinatorial structure of the encoder C.'

---

### 3. R labeled 'rotation operator' but has determinant −2, making it an improper transformation

**Status**: [Pending]

**Quote**:
> The most important scaled orthogonal transformation for our purposes is the rotation operator $R$, defined by the $2 \times 2$ matrix
> 
> $$
> R \triangleq \left( \begin{array}{cc} 1 & 1 \\ 1 & -1 \end{array} \right).
> $$
> 
> $R\mathbb{Z}^2$ is a version of $\mathbb{Z}^2$ obtained by rotating $\mathbb{Z}^2$ by $45^\circ$ and scaling by $2^{1/2}$

**Feedback**:
det(R) = (1)(−1) − (1)(1) = −2, so R/√2 has determinant −1, making it an improper orthogonal transformation (a reflection composed with a rotation), not a pure rotation. A pure 45° rotation scaled by √2 would be [[1,−1],[1,1]] with determinant +2. The resulting lattice RZ² is geometrically correct because Z² is symmetric under the associated reflection, but calling R a 'rotation operator' is imprecise and could mislead readers who apply R to asymmetric lattices. Rewrite 'obtained by rotating Z² by 45° and scaling by 2^(1/2)' as 'obtained by applying a scaled improper orthogonal transformation (det(R/√2) = −1); since Z² is symmetric under the associated reflection, RZ² coincides with the purely rotated and scaled copy.'

---

### 4. Lemma 4 subcode dimension constraint implicit but unstated

**Status**: [Pending]

**Quote**:
> where $\mathbf{c}_1$ is a codeword in a binary $(N, K)$ code $C_1$, and $\mathbf{c}_0$ is a codeword in a binary $(N, J - K)$ code $C_0$ which is a subcode of $C_1$. The redundancy of $\Lambda$ is $r(\Lambda) = 2N - J$

**Feedback**:
For C₀ to be a subcode of C₁, the dimension of C₀ cannot exceed that of C₁, requiring J − K ≤ K, i.e., J ≤ 2K. This constraint is not stated in the lemma. The E₈ example satisfies it (K = 3, J − K = 1, so 1 ≤ 3), but a reader could attempt to apply the lemma with J > 2K, making the subcode condition impossible. Rewrite 'a binary (N, J − K) code C₀ which is a subcode of C₁' as 'a binary (N, J − K) code C₀ which is a subcode of C₁ (necessarily J − K ≤ K).'

---

### 5. Complex code formula leading exponents for H₃₂ and Λ₃₂ inconsistent with general formula

**Status**: [Pending]

**Quote**:
> |  (1,4) | H_{32} | 32 | 3 | 4Z^{32} + 2(32,31,2) + (32,16,8) | φ^{5}G^{16} + φ^{2}(16,15,2) + φ(16,11,4) + (16,5,8)  |
> |  (0,4) | Λ_{32} | 32 | 4 | 4Z^{32} + 2(32,26,4) + (32,6,16) | φ^{8}G^{16} + φ^{5}(16,15,2) + φ^{2}(16,11,4) + φ(16,5,8) + (16,1,16)  |

**Feedback**:
The general formula for Λ(r,n) gives leading exponent n−r. For H₃₂ = Λ(1,4): n−r = 3, so the leading term should be φ³G^16, not φ⁵G^16. For Λ₃₂ = Λ(0,4): n−r = 4, so the leading term should be φ⁴G^16, not φ⁸G^16; the second term should be φ³(16,15,2), not φ⁵(16,15,2). In both rows the subsequent terms are consistent with the corrected leading exponent (e.g., φ²(16,15,2) for H₃₂ matches n−r−1 = 2). Rewrite the complex code formulas as φ³G^16 + φ²(16,15,2) + φ(16,11,4) + (16,5,8) for H₃₂ and φ⁴G^16 + φ³(16,15,2) + φ²(16,11,4) + φ(16,5,8) + (16,1,16) for Λ₃₂.

---

### 6. Complex code formula for H₂₄ leading exponent inconsistent with depth-3 pattern

**Status**: [Pending]

**Quote**:
> |  — | H_{24} | 24 | 3 | 4Z^{24} + 2(24,23,2) + (24,12,8) | φ^{5}G^{12} + φ^{2}(12,11,2) + φ(12,7,4) + (12,5,8)′  |

**Feedback**:
H₂₄ is a depth-3 lattice with complex dimension N_c = 12. By the general formula, the leading φ-exponent equals the depth μ = 3, giving φ³G^12. The table gives φ⁵G^12, which is inconsistent with depth 3. The second term φ²(12,11,2) is correct only if the leading exponent is 3 (giving n−r−1 = 2). This is the same class of error as in H₃₂. Rewrite the complex code formula for H₂₄ as φ³G^12 + φ²(12,11,2) + φ(12,7,4) + (12,5,8)'.

---

### 7. Complex code formula for H₁₆ has incorrect complex dimension superscript

**Status**: [Pending]

**Quote**:
> |  (1,3) | H_{16} | 16 | 2 | 2Z^{16} + (16,11,4) | φ^{2}G^{4} + φ(8,7,2) + (8,4,4)  |

**Feedback**:
For H₁₆ = Λ(1,3), n = 3 gives N = 2^n = 8 real dimensions and N_c = 4 complex dimensions. The leading term should therefore be φ²G^8, not φ²G^4. Every other n = 3 entry in the table (rows (3,3), (2,3), (0,3)) correctly uses G^8. The superscript 4 corresponds to n = 2 (the E₈ family). Rewrite φ²G^4 as φ²G^8 in the complex code formula for H₁₆.

---

### 8. Table III duplicate D₈/RE₈ rows have contradictory ρ values for the same lattice

**Status**: [Pending]

**Quote**:
> |  $D_8$ | $RE_8$ | 8 | 32 | 3 | 1 | 3/4 | 2 | 8 | 88 | 2.75  |
> |  $D_8$ | $RE_8$ | 8 | 128 | 3 | 1 | 1/4 | 2 | 8 | 280 | 2.2  |

**Feedback**:
Since ρ(Λ/Λ') is a fixed property of the partition, it cannot simultaneously equal 3/4 and 1/4 for the same D₈/RE₈ partition. D₈ has r = 1 in N_r = 8 real dimensions, giving ρ = 2r/N_r = 1/4, matching the second row. The partition order |Λ/Λ'| = V(Λ')/V(Λ) is also a fixed invariant; the first row's order 32 is inconsistent with the second row's order 128 for the same partition. The first row appears to represent a different partition mislabeled as D₈/RE₈. Rewrite the first row with the correct Λ label identifying which 8-dimensional lattice has r = 3 and the stated order 32.

---

### 9. Lemma 6 introduces undefined state count symbol r' for augmented code C'

**Status**: [Pending]

**Quote**:
> If $\Lambda'$ is a mod-2 lattice, $C$ is a $2^r$-state, rate-$k / (k + r)$ convolutional code and the labeling map $c(\mathbf{a})$ is linear modulo $\Lambda'$, then a trellis code $\mathbb{C}(\Lambda / \Lambda'; C)$ is the set of all sequences of integer $N$-tuples that are congruent modulo 2 to one of the words in a $2^{r'}$-state rate-$[N_r - r(\mathbb{C})] / N_r$ convolutional code $C'$. The redundancy of $\mathbb{C}$ is $r(\mathbb{C}) = r + r(\Lambda)$

**Feedback**:
The symbol r' is introduced for the state count of the augmented code C' but is never defined. Since the augmented encoder C' appends uncoded bits to the output of C without adding memory, its state space is identical to that of C, giving r' = r. A reader might infer r' = r + r(Λ) from the redundancy formula, but that would conflate redundancy with encoder memory depth. Add the explicit statement 'r' = r' immediately after introducing 2^(r') in Lemma 6, with a brief explanation that augmenting with uncoded bits does not increase encoder memory.

---

### 10. Lemma 6 redundancy formula r(C) = r + r(Λ) uses coarser lattice symbol inconsistently with Lemma 5

**Status**: [Pending]

**Quote**:
> The redundancy of $\mathbb{C}$ is $r(\mathbb{C}) = r + r(\Lambda)$, and its minimum squared distance is $d

**Feedback**:
In the trellis code C(Λ/Λ'; C), the redundancy should reflect the sublattice Λ' (which constrains output sequences), not the coarser lattice Λ. For C(Z²/2Z²; C): r(Z²) = 0, so the formula gives r(C) = r + 0 = r, omitting the 2-bit expansion from Z² to 2Z²-cosets. Lemma 5 uses r(Λ) in the same formula but in a context where Λ could refer to either lattice, creating a notational conflict. Rewrite r(C) = r + r(Λ) as r(C) = r + r(Λ') and verify consistency with the rate formula in Lemma 5.

---

### 11. Trellis state count labeled 2^r but trellis nodes correctly stated as 2^ν

**Status**: [Pending]

**Quote**:
> A trellis diagram for a $2^{r}$-state, rate-$k / (k + r)$ convolutional code is an extended state transition diagram for the encoder that generates $C$. For each time $t$, it has $2^{\nu}$ nodes, or states, representing the possible states at time $t$.

**Feedback**:
The code is labeled '2^r-state' but the trellis is immediately said to have 2^ν nodes, where ν is the overall constraint length. These are independent: r is the number of redundant output bits per time step, while ν is the total binary encoder memory. The four-state Ungerboeck example makes this concrete: it is a 'four-state rate-1/2 code,' so 2^ν = 4 (ν = 2), yet r = 1 (rate k/(k+r) = 1/2), giving 2^r = 2 ≠ 4. The two parameters coincide only when ν = r, which is not stated as an assumption. Rewrite '2^r-state' as '2^ν-state' in the trellis diagram description and add a note that the number of encoder states is 2^ν where ν is the overall constraint length.

---

### 12. Minimum Hamming distance argument proves lower bound but not tightness

**Status**: [Pending]

**Quote**:
> The minimum Hamming distance of this code (taking the outputs as $c(\mathbf{a})$) is five, because the distance between distinct paths is at least two where they diverge, two where they merge, and one somewhere in between. (This is because the difference between paths is a codeword of the $(2,1,2)$ code where they merge and diverge, and a codeword in the $(2,2,1)$ code somewhere in between; that is, we are exploiting the Ungerboeck distance bound for this code partition chain.)

**Feedback**:
The argument establishes d_H(C) ≥ 5 via the Ungerboeck distance bound (2 + 1 + 2 = 5), but does not exhibit a path pair achieving exactly distance 5, which is needed to confirm d_H(C) = 5 rather than d_H(C) > 5. The text presents the bound as a complete proof of equality. To complete the argument, one should identify a specific path that diverges from the all-zeros state, traverses one intermediate state, and remerges, producing outputs differing in exactly 5 positions. Add after the parenthetical a sentence identifying such a path pair.

---

### 13. Third coding gain expression inconsistent with binary lattice formula for general Λ'

**Status**: [Pending]

**Quote**:
> = 2 ^ {\kappa (C)} \left[ d _ {\min } ^ {2} (\mathbb {C}) / d _ {\min } ^ {2} \left(\Lambda^ {\prime}\right) \right] \gamma \left(\Lambda^ {\prime}\right) \\ = 2 ^ {\kappa (\mathbb {C})} \left[ d _ {\min } ^ {2} (\mathbb {C}) / 2 ^ {\mu (\mathbb {C})} \right]

**Feedback**:
Starting from the second line and substituting γ(Λ') = 2^(κ(Λ')−μ(Λ'))·d²_min(Λ') (the binary-lattice formula), one obtains γ(C) = 2^(κ(C)+κ(Λ')−μ(Λ'))·d²_min(C). The third line writes 2^(κ(C))·[d²_min(C)/2^(μ(C))], which requires γ(Λ') = d²_min(Λ')/2^(μ(Λ')), i.e., κ(Λ') = 0. This holds only when Λ' = φ^μ G^N (zero informativity), not for a general binary lattice Λ' with positive κ(Λ'). The paper defines κ(C) = κ(C_enc) + κ(Λ') in the following sentence, so the third line is valid only after that substitution is made explicit. Rewrite the third line as 2^(κ(C)+κ(Λ')−μ(Λ'))·d²_min(C) and note that this equals 2^(κ(C_total)−μ(C))·d²_min(C) only after substituting the combined κ.

---

### 14. Viterbi complexity formula inconsistent between one-dimensional and two-dimensional cases

**Status**: [Pending]

**Quote**:
> (For each unit of time, for each of the $2^{\nu}$ states, the Viterbi algorithm requires $2^k$ additions and a comparison of $2^k$ numbers, or $2^k - 1$ binary comparisons, so that its complexity is $\beta 2^{k + r}$, where $\beta = 2 - 2^{-k}$, and $2^{k + r}$ is the number of branches per stage of the trellis, which is the measure of complexity used by Ungerboeck [21], following Wei [11].)

**Feedback**:
For one-dimensional codes (k=1, r=1, β=1.5): β·2^(k+r)·2^ν = 1.5·4·2^ν gives N_D = 24 for 2^ν = 4, matching Table IV. For two-dimensional codes (k=2, r=1, β=1.75): the same formula gives 1.75·8·4 = 56 for the 4-state Z²/2Z² code, yet Table IV shows N_D = 16. If instead β·2^(k+r) is the total per time step (not multiplied by 2^ν), then for k=2, r=1 the Viterbi contribution is 14, and adding a partition cost of 2 gives N_D = 16—but this interpretation contradicts the 1D case where the 2^ν factor is clearly needed. The text does not resolve this inconsistency. Rewrite the complexity description to explicitly state whether β·2^(k+r) is per state or total per time step, and verify consistency with all entries in Table IV.

---

### 15. Effective coding gain rule of thumb baseline Ñ₀,ref not stated in table or text

**Status**: [Pending]

**Quote**:
> |  4 | $Z^{4}$ | $2D_{4}$ | 128 | 4/5 | 1/2 | 6 | $6/2^{1/2}$ | 6.28 | 728 | 2040 | 4.77  |
> |  8 | $Z^{8}$ | $RD_{8}$ | 128 | 4/5 | 1/4 | 4 | $2^{7/4}$ | 5.27 | 28 | 1032 | 4.71  |

**Feedback**:
Applying the paper's rule of thumb (0.2 dB per factor-of-two increase in Ñ₀) to Row 1: penalty = 0.2·log₂(728/4) = 0.2·7.51 = 1.50 dB, giving γ_eff = 6.28 − 1.50 = 4.78 dB ≈ 4.77 dB ✓. For Row 2: penalty = 0.2·log₂(28/4) = 0.2·2.81 = 0.56 dB, giving γ_eff = 5.27 − 0.56 = 4.71 dB ✓. The formula is consistent when Ñ₀,ref = 4 is used, but this baseline is not stated in the table caption or surrounding text. Readers might note that without knowing Ñ₀,ref = 4, the γ_eff column cannot be reproduced. Add a table footnote specifying 'γ_eff = γ(dB) − 0.2·log₂(Ñ₀/4) dB' and clarifying that ρ is redundancy per complex dimension.

---

### 16. Coding gain γ = 6/√2 for Z⁴/2D₄ requires complex-dimension convention for ρ, which is unstated

**Status**: [Pending]

**Quote**:
> |  4 | $Z^{4}$ | $2D_{4}$ | 128 | 4/5 | 1/2 | 6 | $6/2^{1/2}$ | 6.28 | 728 | 2040 | 4.77  |

**Feedback**:
V(2D₄) = 2⁴·V(D₄) = 16·2 = 32, so V(2D₄)^(2/N_r) = 32^(1/2) = 4√2. Using γ = 2^(−ρ)·d²_min with ρ = 1/2 (per complex dimension, N_c = 2) and d²_min = 6: γ = 2^(−1/2)·6 = 6/√2 ✓. However, under the real-dimension convention ρ = 1/4, γ = 2^(−1/4)·6 ≈ 5.05, which does not match. The table caption does not specify which convention is used. It would be helpful to add a worked example or footnote showing the intermediate computation steps that yield γ = 6/√2, confirming the complex-dimension convention for ρ.

---

### 17. Note added in proof: D₄/RD₄ γ_eff comparison lacks spectral efficiency context

**Status**: [Pending]

**Quote**:
> Note added in proof: J. Chow (private communication) has obtained values of $\tilde{N}_0 = 88$ and $\gamma_{\mathrm{eff}} = 3.88$ dB for the 16-state $D_4 / RD_4$ code, and of $d_{\min}^2 = 6, \tilde{N}_0 = 16$, and $\gamma_{\mathrm{eff}} = 4.37$ dB for the 64-state $D_4 / RD_4$ code.

**Feedback**:
The 64-state D₄/RD₄ code is claimed to have γ_eff = 4.37 dB, which is lower than the 4.48 dB shown for the 64-state D₄/2D₄ code in Table IX. This is counterintuitive if D₄/RD₄ is presented as an improvement. The two partitions have different orders (|D₄/RD₄| = 4 vs. |D₄/2D₄| = 16), leading to different ρ values at the same encoder rate k/(k+r), so the comparison may not be at equal spectral efficiency. Rewrite the note to specify the spectral efficiency ρ for each D₄/RD₄ code cited, and clarify whether the comparison is to the D₄/2D₄ entries in Table IX or to the D₄/RD₄ entries in Table VIII.

---

### 18. Dual partition chain distance sequence unverified for intermediate lattices

**Status**: [Pending]

**Quote**:
> Similarly, $Z^{2N} \simeq \Lambda(n,n)^\perp / \Lambda(n-1,n)^\perp / \cdots / \Lambda(0,n)^\perp = \Lambda(0,n)$ is a partition chain of $2^n$-dimensional complex lattices of depths $0/1/\cdots/n$ and with distances $1/2/\cdots/2^n$

**Feedback**:
The distance sequence 1/2/.../2^n requires d²_min(Λ(k,n)^⊥) = 2^(n−k) for all k. The endpoints are verifiable (Λ(n,n)^⊥ = Z^(2N) with d²_min = 1; Λ(0,n)^⊥ = Λ(0,n) self-dual with d²_min = 2^n), but the intermediate duals are never explicitly identified. The identity Λ(k,n)^⊥ = Λ(n−k,n) is needed to confirm the distance sequence but is not stated. For n = 2: Λ(1,2) = D₄, and whether D₄^⊥ = Λ(1,2) under the mod-2 dual definition is not verified. Add a sentence stating explicitly that Λ(k,n)^⊥ = Λ(n−k,n) and verifying this for at least the n = 2, k = 1 case.

---

### 19. Linearity and distance-invariance asserted globally but proved only for mod-2 partitions

**Status**: [Pending]

**Quote**:
> ; i.e., $c(\mathbf{a}) = \mathbf{a}\mathbf{G}$ [mod $\Lambda'$], where $\mathbf{G} = \{\mathbf{g}_j, 1 \leq j \leq k + r\}$ is a generator matrix of $k + r$ vectors of $\Lambda$ that span $\Lambda$, modulo $\Lambda'$. The following lemma shows that when $\Lambda / \Lambda'$ is a partition of mod-2 lattices and the labeling map is linear, $\mathbb{C}$ is linear, and indeed isomorphic to a binary convolutional code, in the same sense as a mod-2 binary lattice $\Lambda$ is isomorphic to a binary bl

**Feedback**:
Lemma 6 establishes linearity and distance-invariance only when Λ' is a mod-2 lattice. Section IV-B asserts that 'all codes in this paper are distance-invariant,' which includes Classes III–VIII based on mod-4 and deeper partitions (E₈/RE₈, D₄/2D₄, Λ₁₆/RΛ₁₆). For these partitions the group structure modulo Λ' is Z/4Z or deeper, and no analogous lemma is stated; the cross-referenced material defers this to Part II. If distance-invariance fails for any of these partitions, the d²_min values stated for the corresponding code classes in Section VI would be upper bounds rather than exact values. Add a remark after Lemma 6 identifying which code classes rely on distance-invariance results deferred to Part II, and state explicitly that the d²_min values for those classes are conditional on Part II's verification.

---
