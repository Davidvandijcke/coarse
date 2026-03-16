# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/13/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a unified framework for coset codes on band-limited channels, characterizing trellis and lattice codes as coset selections from chains of binary lattice partitions. Using the fundamental coding gain γ(C) and normalized error coefficient Ñ₀ as primary figures of merit, the paper introduces eight generic code classes (I–VIII) defined by partition type, encoder rate, and constraint length, and systematically catalogs known codes—including Ungerboeck, Calderbank–Sloane, Wei, and GCS-type codes—within this taxonomy. The main results are comparative performance and complexity tables (Tables IV–XI) and the conclusion that trellis codes outperform lattice codes and that Ungerboeck codes remain the benchmark, with the framework claimed to subsume 'practically all known good constructive coding techniques for band-limited channels.'

Below are the most important issues identified by the review panel.

**Asymptotic Coding Gain as the Sole Performance Metric Obscures Practical Rankings and Is Applied Inconsistently**

Throughout Sections IV–VII, the fundamental coding gain γ(C) is treated as the primary figure of merit, yet this quantity is strictly valid only at infinite SNR. The 'rule of thumb' that every factor-of-two increase in Ñ₀ costs approximately 0.2 dB is applied selectively: it is used to compute γ_eff for Ungerboeck-type codes in Table V but is explicitly withheld for lattice codes and several Class V/VI entries in Table XI where error coefficients are noted as very large or are entirely missing. For codes with dramatically different error coefficients—such as the 256-state Ungerboeck code (Ñ₀ = 4) versus the Class I Λ₁₆/RΛ₁₆ code (Ñ₀ unspecified but large)—the asymptotic ranking can reverse at operational SNRs of 10–15 dB. Furthermore, a significant fraction of entries in Tables VII, VIII, and XI have blank error coefficient entries (e.g., the 32-state Wei D₈⁺/RE₈ code, the 16-state Class VII Z⁸/E₈ and Z¹⁶/H₁₆ codes), so the Section VII conclusion that 'it takes 256 states to get 6 dB with a reasonably small error coefficient' is not fully supported by the evidence presented. It would be helpful to either apply the effective-gain correction uniformly, provide bounds on missing Ñ₀ values from lattice weight distributions, and state explicitly the SNR range over which the γ(C) rankings are reliable.

**Key Distance Claims for Class III, IV, and VIII Codes Rely on Unproved Partition-Structural Properties Deferred to Part II**

In Section VI, the minimum squared distance analysis for Class III codes invokes the existence of an 'alternative partition E₈/R*E₈/2E₈' such that the coset representatives [R*E₈/2E₈] simultaneously serve as coset representatives for E₈/RE₈—a non-trivial structural property of the E₈ lattice that is asserted without proof and forwarded to Part II. The d²_min calculation for the 16-state Class III E₈/RE₈/2E₈ code, specifically the claim that d²_min(C) = d²_min(2E₈) = 16 rather than the a priori lower bound of 3d²_min(E₈) = 24, depends critically on this property. Similarly, the Class IV distance claim d²_min(C) = 4d²_min(Λ) rests on an additional assertion about path differences at the merging point that is not independently verified. Since these entries appear in Table XI and drive the comparative conclusions of Section VII, readers relying solely on Part I cannot verify the most important distance values. It would be helpful to either include a self-contained proof of the coset-representative compatibility lemma in Part I, or to flag the affected Table XI entries explicitly as conditional on results proved only in Part II.

**The Eight-Class Geometrical Classification Is Neither Proved Exhaustive Nor Mutually Exclusive, Limiting Its Claimed Universality**

Section VI introduces eight code classes (I–VIII) defined by three binary characteristics—partition type, encoder rate, and constraint length—and the paper presents these as a systematic taxonomy subsuming 'practically all known good constructive coding techniques.' However, no theorem or argument establishes that these eight combinations are exhaustive or mutually exclusive. The paper itself notes overlaps: the two-state Class V codes reduce to Class I codes, and the four-state D₄/RD₄ code appears in both Class II and Class VI. Rate-k/(k+r) encoders with r > 1 and k > 1, codes with non-uniform partition chains, and codes with multiple independent encoders (as in the Imai–Hirakawa multilevel coding framework, which is entirely absent from the paper's historical survey despite predating several catalogued schemes and mapping directly onto the partition-chain formalism) are not addressed. The broader claim in Section VII that 'there are many ways to modulate' and that complexity remains 'remarkably constant across a wide variety of codes' rests on this classification being representative, but if important structural families fall outside the eight classes, the conclusion could be premature. It would be helpful to either prove the classification covers all codes satisfying the stated constraints, explicitly address whether Imai–Hirakawa codes are subsumed, and reframe the taxonomy as a representative sample if exhaustiveness cannot be established.

**Decoding Complexity Metric Ñ_D Mixes Incommensurable Contributions and Cannot Be Independently Verified Without Part II**

Tables II, III, and XI report normalized decoding complexity Ñ_D defined as the number of binary operations required by the trellis-based algorithms of Part II, making these figures unverifiable from Part I alone. More substantively, the total Ñ_D conflates two contributions—the lattice partition decoder and the Viterbi algorithm—that use different counting conventions: the Viterbi complexity is stated as β·2^(k+r) per state per time unit, while the partition decoder complexity is approximated as α|Λ/Λ'| with α ranging over a factor of six. For codes where one component dominates by orders of magnitude (e.g., the Class VI Λ₁₆/RΛ₁₆ code with Ñ_D ≈ 2^19), the single combined figure makes it impossible to assess whether complexity is driven by the lattice decoder or the Viterbi decoder—information essential for implementation trade-off analysis. The claim in Section VII that 'decoding complexity increases slightly as we go from lattice codes to Class I to Class II to Class IV' is not adequately supported by these mixed figures. It would be helpful to report the two complexity contributions separately, provide a self-contained summary of the decoding algorithm structure sufficient to verify leading-order figures, and bound the approximation error in the α|Λ/Λ'| estimate.

**Foundational Lemmas Leave Critical Gaps That Propagate Through the Distance and Labeling Analyses**

Two foundational results carry unverified assumptions that affect the reliability of subsequent analyses. First, Lemma 2 (Section II-F), which establishes that any partition Λ/Λ' of binary lattices of order 2^K can be refined into a chain admitting a linear Ungerboeck labeling, asserts the existence of order-2 elements in each intermediate quotient group—equivalently, that these quotient groups are elementary abelian 2-groups—but defers the proof to Part II. This property is used immediately and repeatedly in Sections II-G, III, and IV; if it fails for some intermediate lattice, the entire labeling construction and associated distance bounds require revision. Second, the minimum squared distance formula d²_min(Λ) = min[16, 4d_H(C₁), d_H(C₀)] for decomposable mod-4 lattices (Section II-G) implicitly assumes that coset leaders have coordinates in {0, ±1, 2}, which may not hold for indecomposable or partially decomposable lattices. Table I entries for H₁₆, H₃₂, H₂₄, and Λ₂₄ (marked with primes indicating non-standard generators) rely on this formula, yet no separate distance argument is provided for these cases. Additionally, several complex code formulas in Table I for H₃₂ and Λ₃₂ show leading powers (φ⁸, φ⁵) that exceed the construction depth, suggesting possible typographical errors. It would be helpful to either provide self-contained proofs for both foundational results, restrict the distance formula explicitly to the decomposable case with separate arguments for primed entries, and verify the Table I formulas against the Part II derivations.

**Regularity of Labelings for Nonlinear Trellis Codes Is Assumed but Not Verified for the Specific Partition Chains Used**

Section IV-C acknowledges that trellis codes based on mod-4 or deeper partitions are generally not linear, and justifies the distance analysis by appealing to regularity of the labeling. Three sufficient conditions for regularity are listed—linearity, Ungerboeck labeling with equality in the distance bound, or Cartesian product structure—but none is verified for the specific partition chains used in Classes III–VIII, particularly two-level chains such as Z⁸/D₈/E₈ and D₈/E₈/RE₈. If the labeling for a given partition chain is not regular, the minimum squared distance calculation—which underlies all γ values in Table XI—could be incorrect, because the distance from an arbitrary code sequence to its nearest neighbor might differ from the norm of the nearest nonzero code sequence. The paper's abstract claim that 'practically all known good constructive coding techniques can be characterized as coset codes' implicitly assumes that the distance analysis is valid for all catalogued codes, but nonlinear codes that do not admit regular labelings are not addressed. It would be helpful to verify regularity explicitly for each partition chain used in Section VI, or to add regularity as a stated hypothesis of the distance claims for each class, so that the scope of the framework's validity is clearly delimited.

**Status**: [Pending]

---

## Detailed Comments (24)

### 1. Coding Gain Formula Inconsistent with Table IV Entries

**Status**: [Pending]

**Quote**:
> The fundamental coding gain $\gamma$ is given by the formula $2^{-e}d_{\mathrm{min}}^2$ and is also given in decibels.

**Feedback**:
It would be helpful to verify this formula against Table IV entries beyond the 4-state case. For the 1D 8-state code (e=3, d²_min=10): 2^(−3)×10=1.25, yet the table shows γ=2.5. For the 1D 16-state code (e=4, d²_min=11): 2^(−4)×11=0.6875, yet the table shows γ=2.75. The formula consistent with all entries appears to be γ=d²_min/2^(2ρ), where ρ is the normalized redundancy per real dimension (ρ=1/2 for 1D codes gives d²_min/2; ρ=1/2 per real dimension for 2D codes gives d²_min/2 per complex dimension). The formula 2^(−e)·d²_min coincidentally matches only when 2^e equals the correct denominator. Rewriting the formula as γ=d²_min/2^(2ρ) would make it consistent with all table entries.

---

### 2. R² = 2 Claim Contradicted by Direct Matrix Computation

**Status**: [Pending]

**Quote**:
> The correspondence is not exact because $R$ includes a reflection as well as rotation and scaling, so that $R^2 = 2$, whereas $\phi^2 = 2i$.

**Feedback**:
With R defined as the matrix [[1,−1],[1,1]], direct computation gives R²=[[0,−2],[2,0]], which acts on (a,b) as (−2b, 2a). In complex notation with z=a+bi, this is multiplication by 2i=φ². So R² and φ² correspond to the same geometric operation, contradicting the paper's stated contrast 'R²=2, whereas φ²=2i.' The actual asymmetry between R and φ occurs at the first power: R incorporates a reflection that φ does not. Readers might note that rewriting this as 'R² corresponds to multiplication by 2i=φ², so the squares agree; the asymmetry between R and φ arises at the first power, where R incorporates a reflection that φ does not' would be more accurate.

---

### 3. Incorrect φ-Exponents for H₃₂ and Λ₃₂ in Table I

**Status**: [Pending]

**Quote**:
> |  (1,4) | H_{32} | 32 | 3 | 4Z^{32} + 2(32,31,2) + (32,16,8) | φ^{5}G^{16} + φ^{2}(16,15,2) + φ(16,11,4) + (16,5,8)  |
> |  (0,4) | Λ_{32} | 32 | 4 | 4Z^{32} + 2(32,26,4) + (32,6,16) | φ^{8}G^{16} + φ^{5}(16,15,2) + φ^{2}(16,11,4) + φ(16,5,8) + (16,1,16)  |

**Feedback**:
The general formula Λ(r,n)=φ^(n−r)G^N+φ^(n−r−1)RM(n−1,n)+…+RM(r,n) requires consecutive descending exponents starting at n−r. For H₃₂=Λ(1,4): n−r=3, so the leading term must be φ³G^16, giving exponents 3,2,1,0. The table shows φ⁵G^16 with exponents 5,2,1,0—not consecutive. For Λ₃₂=Λ(0,4): n−r=4, leading term must be φ⁴G^16 (exponents 4,3,2,1,0); the table shows φ⁸G^16 with exponents 8,5,2,1,0—not consecutive. The correctly-stated E₈=Λ(0,2) row shows φ²G^4 (n−r=2), confirming the pattern. It would be helpful to rewrite H₃₂ as φ³G^16+φ²(16,15,2)+φ(16,11,4)+(16,5,8) and Λ₃₂ as φ⁴G^16+φ³(16,15,2)+φ²(16,11,4)+φ(16,5,8)+(16,1,16).

---

### 4. Incorrect Intermediate Lattice in Partition Chain Regularity Example

**Status**: [Pending]

**Quote**:
> b) if it is an Ungerboeck labeling and the Ungerboeck distance bound always holds with equality, e.g., any Ungerboeck labeling for $Z^2 / RZ^2 / 2Z^2 / 2RZ^2 = G / \phi G / \phi^3 G / \phi^3 G$;

**Feedback**:
Re-deriving independently: φG has volume 2 (corresponding to RZ²), φ²G has volume 4 (corresponding to 2Z²), and φ³G has volume 8 (corresponding to 2RZ²). The correct complex rendering of Z²/RZ²/2Z²/2RZ² is therefore G/φG/φ²G/φ³G. The expression as written, G/φG/φ³G/φ³G, skips φ²G entirely and repeats φ³G as both the third and fourth terms, making the third partition φG/φ³G a two-step jump of index 4 and the final partition φ³G/φ³G trivial of index 1—both contradicting the intent of a four-level chain with two-way partitions at each step. It would be helpful to rewrite 'G/φG/φ³G/φ³G' as 'G/φG/φ²G/φ³G'.

---

### 5. Subcode Dimension Inequality K−K′ ≤ K′ Incorrectly Justified via Code C

**Status**: [Pending]

**Quote**:
> The generators $\{2g_{k}, K' + 1 \leq k \leq K\}$ generate a lattice $\Lambda'$ that is a sublattice of $\Lambda_{e}$, whose elements are congruent to $2c'$ modulo 4, where $c'$ is a codeword in a binary $(N, K - K')$ block code $C'$ that is a subcode of the code $C$, so $K - K' \leq K'$.

**Feedback**:
Re-deriving: C′ indexes cosets of 4Z^N within Λ_e. By Lemma 3 applied to Λ_e, the code associated with Λ_e/4Z^N has dimension K′. Since C′ is a subcode of that K′-dimensional code, K−K′≤K′ follows. The text instead asserts C′ is a subcode of C (the K-dimensional code for Λ/4Z^N), which yields only K−K′≤K—a trivially true but weaker statement that does not imply the stated bound K−K′≤K′. It would be helpful to rewrite 'a subcode of the code C, so K−K′≤K′' as 'a subcode of the binary (N,K′) code associated with Λ_e/4Z^N, so K−K′≤K′.'

---

### 6. 2^K Representatives Attributed to Two-Way Partition Incorrectly

**Status**: [Pending]

**Quote**:
> Thus the $2^{K}$ binary linear combinations $\{\sum a_{k}\mathbf{g}_{k}\}$ of the generators $\mathbf{g}_{k}$ are a system of coset representatives $[\Lambda_{k} / \Lambda_{k + 1}]$ for the partition $\Lambda_{k} / \Lambda_{k + 1}$

**Feedback**:
The partition Λ_k/Λ_{k+1} is explicitly stated to be two-way (2 cosets), requiring exactly 2 coset representatives indexed by a single bit a_k∈{0,1}. The sentence attributes the full set of 2^K combinations over all indices k simultaneously as representatives for this single two-way partition—when K>1, 2^K>2, so this is impossible. The 2^K combinations are in fact coset representatives for the full partition Λ/Λ′ (which has 2^K cosets), as Lemma 2's coset decomposition Λ=Λ′+{Σa_k g_k} confirms. It would be helpful to rewrite 'are a system of coset representatives [Λ_k/Λ_{k+1}] for the partition Λ_k/Λ_{k+1}' as 'are a system of coset representatives for the full partition Λ/Λ′.'

---

### 7. γ(Λ) Written with Λ′ Argument Instead of Λ

**Status**: [Pending]

**Quote**:
> Relative to $\gamma (\Lambda) = 2^{-\rho (\Lambda)}d_{\min}^{2}(\Lambda^{\prime})$, the gain $\gamma (\mathbb{C})$ is greater by the distance gain factor of $d_{\min}^{2}(\mathbb{C}) / d_{\min}^{2}(\Lambda)$, offset by a power loss of $2^{-\rho (C)}$ due to constellation expansion.

**Feedback**:
Re-deriving: γ(Λ)=d²_min(Λ)/V(Λ)^(2/N)=2^(−ρ(Λ))·d²_min(Λ). The surrounding derivation's line '=2^(−ρ(C))[d²_min(C)/d²_min(Λ)]γ(Λ)' is self-consistent only if γ(Λ) involves d²_min(Λ), not d²_min(Λ′). Writing d²_min(Λ′) in the expression for γ(Λ) contradicts both the definition and the surrounding algebra. It would be helpful to rewrite 'γ(Λ)=2^(−ρ(Λ))d²_min(Λ′)' as 'γ(Λ)=2^(−ρ(Λ))d²_min(Λ).'

---

### 8. Partition Named for φa₁ Has Order 4, Not 2

**Status**: [Pending]

**Quote**:
> where $a_0, a_1, a_2, \dots \in \{0,1\}$, and $a_0$ specifies the coset of $\phi G$ in the partition $G / \phi G$, $\phi a_1$ specifies the coset of $\phi^2 G$ in the partition $\phi G / \phi^3 G$, and so forth.

**Feedback**:
The partition φG/φ³G has order [φG:φ³G]=|det(φ³)|²/|det(φ)|²=8/2=4, requiring two bits to index. But φ·a₁ with a₁∈{0,1} takes only two values (0 and φ), indexing at most a two-way partition. The correct two-way partition at this level is φG/φ²G, which has order [φG:φ²G]=4/2=2, consistent with a single bit. The displayed coset decomposition formula immediately following is internally consistent (each bracket is a two-way partition), confirming the verbal description contains a typographical error. It would be helpful to rewrite 'φa₁ specifies the coset of φ²G in the partition φG/φ³G' as 'φa₁ specifies the coset of φ²G in the two-way partition φG/φ²G.'

---

### 9. Duplicate D₈/RE₈ Rows with Mutually Contradictory Parameters in Table III

**Status**: [Pending]

**Quote**:
> |  D8 | RE8 | 8 | 32 | 3 | 1 | 3/4 | 2 | 8 | 88 | 2.75  |
> |  D8 | RE8 | 8 | 128 | 3 | 1 | 1/4 | 2 | 8 | 280 | 2.2  |

**Feedback**:
A partition Λ/Λ′ is uniquely determined by the two lattices, so there can be only one order |D₈/RE₈|. The two rows show orders 32 and 128 respectively, and κ values 3/4 and 1/4—both of which are uniquely determined by the lattice pair. The two rows must therefore refer to different sublattices both labeled RE₈ (e.g., one is RE₈ and the other is R*E₈ or 2E₈). It would be helpful to rewrite the second row's Λ′ label to its correct lattice name and verify the order and κ values against V(Λ′)/V(D₈), because as written the two rows are mutually contradictory for a single lattice pair.

---

### 10. Table III Column Header d²max Should Be d²min

**Status**: [Pending]

**Quote**:
> |  Λ | Λ' | 2N | |Λ/Λ'| | μ | κ | ρ | d2min(Λ) | d2max(Λ') | N̂D | N̂D/|Λ/Λ'|  |

**Feedback**:
The column header 'd²max(Λ′)' appears to be a typographical error for 'd²min(Λ′)'. The tabulated values match known d²_min values throughout: for Z²/RZ², the entry is 2=d²_min(RZ²); for Z²/2Z², the entry is 4=d²_min(2Z²); for D₈/E₈, the entry is 4=d²_min(E₈). No standard notion of 'maximum squared distance' for a lattice would produce these values, and d²_min(Λ′) is the parameter used in the coding gain formula throughout the paper. It would be helpful to rewrite the column header as 'd²min(Λ′).'

---

### 11. State Count 128 Inconsistent with Rate-4/5 Encoder in Table VI

**Status**: [Pending]

**Quote**:
> |  4 | Z^{4} | 2D_{4} | 128 | 4/5 | 1/2 | 6 | 6/2^{1/2} | 6.28 | 728 | 2040 | 4.77  |
> |  8 | Z^{8} | RD_{8} | 128 | 4/5 | 1/4 | 4 | 2^{7/4} | 5.27 | 28 | 1032 | 4.71  |

**Feedback**:
For a rate-k/(k+r)=4/5 encoder, r=1 redundant bit, giving 2^r=2 trellis states—not 128. A 128-state code requires r=7, implying rate 4/11, directly contradicting the stated 4/5 rate. This inconsistency appears in both rows simultaneously. Either the state-count column uses a non-standard meaning (e.g., total encoder memory rather than 2^r), or the state counts are misattributed from a different code family. It would be helpful to either rewrite the state-count entries as '2' for both rows (consistent with r=1 for rate-4/5 codes), or add a footnote clarifying that the column denotes a quantity other than 2^r as defined in the main text.

---

### 12. Effective Coding Gain Rule of Thumb Lacks Reference Baseline Ñ₀

**Status**: [Pending]

**Quote**:
> In this paper, we will use the rule of thumb that every factor of two increase in the error coefficient reduces the coding gain by about $0.2\mathrm{dB}$ (at error rates of the order of $10^{-6}$); this will enable us to compute an effective coding gain $\gamma_{\mathrm{eff}}$ (in dB), normalized for the error coefficient $\tilde{N}_0$.

**Feedback**:
The rule converts γ to γ_eff via a 0.2 dB penalty per factor-of-two increase in Ñ₀, but the baseline reference value of Ñ₀ is never stated. Without it, no γ_eff entry in Tables V–VII can be independently verified. Back-computing from Table VII: the 8-state Z⁴/RD₄ code has Ñ₀=44 and penalty γ−γ_eff=4.52−3.82=0.70 dB, implying 3.5 doublings above baseline, so baseline Ñ₀≈44/2^3.5≈3.9. The 16-state Z⁴/RD₈ code (Ñ₀=12, penalty=0.32 dB) gives baseline≈3.9 similarly, suggesting the baseline is Ñ₀=4, but this is never stated. It would be helpful to add a sentence specifying the reference error coefficient (e.g., 'taking an uncoded reference with Ñ₀=4') so that all γ_eff values can be independently verified.

---

### 13. Lemma 4 Complex Distance Formula May Be Missing Factor of 2 for C₁ Term

**Status**: [Pending]

**Quote**:
> An $N$-dimensional complex $G$-lattice $\Lambda$ is a mod-2 binary lattice if and only if it is the set of all Gaussian integer $N$-tuples that are congruent modulo $\phi^2$ to an $N$-tuple of the form $\phi c_1 + c_0$, where $c_1$ is a codeword in a binary $(N, K)$ code $C_1$, and $c_0$ is a codeword in a binary $(N, J - K)$ code $C_0$ which is a subcode of $C_1$. The redundancy of $\Lambda$ is $r(\Lambda) = 2N - J$, and its minimum squared distance is

**Feedback**:
The construction implies the minimum squared distance formula should be min[4, 2·d_H(C₁), d_H(C₀)]. Since |φ|²=|1+i|²=2, two points differing only in the φ·c₁ component by a Hamming-weight-1 vector contribute squared distance 2, while a difference only in c₀ contributes 1. If the paper's formula omits the factor of 2 on d_H(C₁) and states min[4, d_H(C₁), d_H(C₀)], it understates the minimum distance contribution from the C₁ component. It would be helpful to verify that the stated formula is min[4, 2·d_H(C₁), d_H(C₀)] and, if the factor of 2 is absent, add it to correctly account for the norm of φ.

---

### 14. Induction Does Not Explicitly Verify Terminal Lattice Equals Λ

**Status**: [Pending]

**Quote**:
> The induction terminates when $k = 0$.

**Feedback**:
The induction constructs Λ_k as a sublattice of Λ at each step, but never explicitly verifies that the final Λ₀ equals Λ rather than a proper sublattice. The argument relies on the fact that each step doubles the index over Λ′, so after K steps |Λ₀/Λ′|=2^K=|Λ/Λ′|, forcing Λ₀=Λ. This counting argument is implicit but not stated. It would be helpful to add after 'The induction terminates when k=0' the sentence: 'At termination, |Λ₀/Λ′|=2^K=|Λ/Λ′|, so Λ₀=Λ.'

---

### 15. Approximate Equality Notation for Chain Endpoint Contradicts Proof Sketch

**Status**: [Pending]

**Quote**:
> Then there is a sequence of lattices $\Lambda_0 = \Lambda$, $\Lambda_1, \dots, \Lambda_K \approx \Lambda'$ such that $\Lambda_0 / \Lambda_1 / \dots / \Lambda_K$ is a lattice partition chain

**Feedback**:
Lemma 2 writes Λ₀=Λ (equality) but Λ_K≈Λ′ (approximate equality or isomorphism). The proof sketch then uses Λ_K=Λ′ (equality) as the base case: 'Λ_K=Λ′ is certainly such a lattice.' If ≈ denotes isomorphism rather than equality, the coset decomposition Λ=Λ′+{Σa_k g_k} requires Λ_K to literally equal Λ′ for the coset representatives to be valid. It would be helpful to rewrite 'Λ_K≈Λ′' as 'Λ_K=Λ′' in the Lemma 2 statement to match the proof sketch and the coset decomposition formula.

---

### 16. Index n vs. μ Inconsistency in Dual Partition Chain Proposition

**Status**: [Pending]

**Quote**:
> This proposition may be verified by noting that $C_0^\perp / \dots / C_{n-1}^\perp$ is a code partition chain, that every generator $\phi^{\mu - j - 1} \pmb{g}_j^\perp$ of $\Lambda^\perp / \phi^n \pmb{G}^N$ is orthogonal mod $\phi^\mu$ to every generator $\phi^{j'} \pmb{g}_{j'}$ of $\Lambda / \phi^n \pmb{G}^N$, and that the dimensions are such that the informativity of $\Lambda^\perp$ is equal to the redundancy of $\Lambda$ and vice versa.

**Feedback**:
The dual formula uses φ^μ G^N as its leading term, but the verification text writes the chain endpoint as C_{n−1}^⊥ (using n) and the quotient as Λ^⊥/φ^n G^N (using n), while the dual formula's leading term is φ^μ G^N (using μ). For a depth-μ lattice, n=μ is required but never stated. With μ=2 for E₈, the chain should be C₀^⊥/C₁^⊥ (endpoint index μ−1=1), but writing C_{n−1}^⊥ with n unspecified leaves the endpoint ambiguous. It would be helpful to rewrite 'C₀^⊥/…/C_{n−1}^⊥' as 'C₀^⊥/…/C_{μ−1}^⊥' and both instances of 'φ^n G^N' as 'φ^μ G^N' to match the dual code formula.

---

### 17. Partition Chain Distance Sequence Notation Ambiguous

**Status**: [Pending]

**Quote**:
> is a partition chain of $2^n$-dimensional complex lattices of depths $0/1/\cdots/n$ and with distances $1/2/\cdots/2^n$ (for short).

**Feedback**:
From Table I, d²_min(Λ(r,n))=2^r, so the squared distances along the chain Λ(n,n)/Λ(n−1,n)/…/Λ(0,n) are 1,2,4,…,2^n—a geometric sequence with ratio 2. The slash-separated notation '1/2/…/2^n' strongly implies an arithmetic progression (step 1), which matches neither squared distances (geometric) nor unsquared distances (1,√2,2,…,2^(n/2)) for n≥3. It would be helpful to rewrite 'with distances 1/2/…/2^n' as 'with minimum squared distances 1,2,4,…,2^n' to accurately reflect d²_min(Λ(r,n))=2^r and to distinguish the geometric progression from the arithmetic-progression reading.

---

### 18. G⁴ vs. G⁸ Discrepancy in H₁₆ Complex Code Formula in Table I

**Status**: [Pending]

**Quote**:
> |  (1,3) | H_{16} | 16 | 2 | 2Z^{16} + (16,11,4) | φ^{2}G^{4} + φ(8,7,2) + (8,4,4)  |

**Feedback**:
For Λ(1,3)=H₁₆: n=3, r=1, N=2^n=8. The general formula gives φ²G^8+φ·RM(2,3)+RM(1,3)=φ²G^8+φ(8,7,2)+(8,4,4). The table writes G^4 instead of G^8 for the leading term. Comparing with the E₈ row where n=2, N=4, and the table correctly shows G^4, the H₁₆ entry appears to have copied the wrong superscript. It would be helpful to rewrite φ²G^4 as φ²G^8 in the H₁₆ row of Table I to match N=2^3=8.

---

### 19. Rate-1/2 Label vs. Two-Bit Input Ambiguity in Encoder Description

**Status**: [Pending]

**Quote**:
> For example, the four-state Ungerboeck code shown in Figs. 2 and 3 uses the four-state rate-1/2 convolutional code whose encoder and trellis diagram are illustrated in Fig. 10.

**Feedback**:
The text calls C a rate-1/2 convolutional code while simultaneously describing a two-bit input a=(a₀,a₁) producing a 2-tuple output c(a). If both bits enter C, the rate would be 2/2=1, not 1/2. In Ungerboeck's framework, one bit (a₁) is uncoded and selects between cosets at the lower partition level, while the other (a₀) is the actual encoder input driving the rate-1/2 code. The text does not state which bit is coded vs. uncoded. It would be helpful to add after 'The two bits a=(a₀,a₁)' the clarification: 'where a₀ is the input to the rate-1/2 convolutional encoder C (with ν=2 memory elements) and a₁ is an uncoded bit that directly selects between cosets at the lower partition level.'

---

### 20. d_H=5 Argument Does Not Exclude Length-1 Diverge-Merge Paths

**Status**: [Pending]

**Quote**:
> The minimum Hamming distance of this code (taking the outputs as $c(a)$) is five, because the distance between distinct paths is at least two where they diverge, two where they merge, and one somewhere in between.

**Feedback**:
The argument 2+2+1=5 requires at least one intermediate branch between divergence and merging. For a four-state encoder with ν=2, a path diverging at time t could in principle re-merge at time t+1 (a length-1 path), contributing only 2+2=4 with no intermediate step. The text asserts 'one somewhere in between' without proving the state-transition graph forbids immediate re-merging. The result d_H=5 is classically correct for this code, but the argument has a gap. It would be helpful to add after 'one somewhere in between': 'The encoder state-transition structure visible in Fig. 10 confirms that no path can diverge from and immediately re-merge with the all-zero path in a single step, so at least one intermediate branch always exists.'

---

### 21. Equating Hamming Distance with Squared Euclidean Distance Without Justification

**Status**: [Pending]

**Quote**:
> It is easy to see that the minimum squared distance between code sequences corresponding to distinct paths in the trellis is the minimum Hamming distance between sequences $c(D)$ of coset representatives and thus is equal to $d_H(C) = 5$.

**Feedback**:
The four coset representatives are c(00)=[00], c(10)=[10], c(01)=[11], c(11)=[01]. Computing squared Euclidean distances: |[11]−[00]|²=2, yet the Hamming distance is 2. So some pairs at Hamming distance 1 have squared Euclidean distance 2, meaning the minimum squared Euclidean distance along a path of Hamming weight w could range from w to 2w. The claim d²_min=d_H(C)=5 requires verifying that the minimum-weight path achieving Hamming weight 5 uses only coset-representative differences of squared norm 1. It would be helpful to add after 'is equal to d_H(C)=5' the justification: 'since each nonzero position in the minimum-weight path contributes squared Euclidean distance exactly 1, as the relevant coset representative differences all have norm 1 in Z².'

---

### 22. Note References D₄/RD₄ Partition Absent from Table Body Without Flagging the Distinction

**Status**: [Pending]

**Quote**:
> Note added in proof: J. Chow (private communication) has obtained values of $\tilde{N}_0 = 88$ and $\gamma_{\mathrm{eff}} = 3.88$ dB for the 16-state $D_4 / RD_4$ code, and of $d_{\min}^2 = 6$, $\tilde{N}_0 = 16$, and $\gamma_{\mathrm{eff}} = 4.37$ dB for the 64-state $D_4 / RD_4$ code.

**Feedback**:
The table body lists codes based on D₄/2D₄, but the note references D₄/RD₄—a structurally different partition with d²_min=6 for the 64-state code versus d²_min=8 for the 64-state D₄/2D₄ entry. A reader could mistakenly interpret the note as correcting existing table entries. The note's γ_eff values are internally consistent (16-state: penalty=log₂(88/4)·0.2≈0.89 dB, γ_eff=4.77−0.89=3.88 dB ✓; 64-state: penalty=log₂(16/4)·0.2=0.40 dB, γ_eff=4.77−0.40=4.37 dB ✓), but the lower d²_min=6 is a substantive structural difference. It would be helpful to rewrite the note's opening as 'for the 16-state and 64-state codes based on the partition D₄/RD₄ (distinct from the D₄/2D₄ partition used in the table above).'

---

### 23. Order Formula m^N Invalid for Non-Positive m

**Status**: [Pending]

**Quote**:
> More generally, for any $m \in \mathbb{Z}$, the lattice $mZ^{N}$ of all $N$-tuples of integer multiples of $m$ is a sublattice of $Z^{N}$ of order $m^{N}$

**Feedback**:
When m=0, mZ^N is the zero vector only, so Z^N/mZ^N is isomorphic to Z^N itself (infinite), not of order 0^N=0. When m<0, mZ^N=|m|Z^N as sets, so the order is |m|^N, not m^N; for odd N and m<0, m^N is negative, which cannot be a cardinality. Additionally, the coset representative set {0,1,…,m−1} is only defined for m>0. It would be helpful to rewrite 'for any m∈Z' as 'for any positive integer m' to match the coset representative construction and ensure the order formula m^N is correct.

---

### 24. Subscript k in D_k Example Should Be 4

**Status**: [Pending]

**Quote**:
> For example, the depth of $D_{k}$ is 1, its redundancy and informativity are both equal to 1, and its normalized redundancy and informativity are both equal to $1/2$.

**Feedback**:
Re-deriving: D₄ viewed as a 2-complex-dimensional lattice (N=2) has |Z²/D₄|=2, so r(D₄)=1, ρ=1/2, k(D₄)=1, κ=1/2—matching the stated values. For D₈ (N=4): ρ=1/4 and κ=3/4, which differ. So the stated normalized values (ρ=κ=1/2) hold only for D₄. The subscript k also collides with the informativity variable k(Λ) defined just above, creating genuine ambiguity. It would be helpful to rewrite 'the depth of D_k' as 'the depth of D₄' because the stated normalized parameter values hold only for D₄ (N=2 complex dimensions) and the subscript k collides with the informativity variable defined in the same paragraph.

---
