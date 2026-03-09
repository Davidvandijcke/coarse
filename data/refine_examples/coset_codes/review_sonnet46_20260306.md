# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/06/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper presents a unified framework for constructive coding techniques on band-limited channels, organizing lattice codes and trellis-coded modulation schemes under the common umbrella of 'coset codes.' The authors define fundamental coding gain via a normalized redundancy formula, introduce an eight-class taxonomy of binary trellis codes based on Barnes-Wall lattice partitions, and compare known codes (Ungerboeck, Wei, GCS, and others) within this framework. The main results include a systematic performance-complexity comparison showing that trellis codes with moderate state counts achieve better effective coding gain than lattice codes, and that coding gains of 6 dB require on the order of 256 states.

**Coding Gain Formula Conflates Two Normalizations and Lacks Verification for Dense-Lattice Base Codes**

The fundamental coding gain γ(C) = 2^{−ρ(C)} d²_min(C) is used both as a gain over an uncoded Z^N reference and as a gain relative to the sublattice Λ', yet these two interpretations coincide only when Λ = Z^N. For CS-type codes built on E_8 or D_4, the redundancy ρ(C) = ρ_encoder + ρ(Λ) must account for the constellation expansion of Λ relative to Z^N, but the paper does not explicitly verify that this double-counting is handled consistently when comparing CS codes (ρ = 5/4, including ρ(E_8) = 1) against Wei codes (ρ = 1/4 for Z^8/E_8). Additionally, the formula implicitly assumes that constellation expansion power cost equals exactly 2^{ρ(C)}, which holds only asymptotically for large, uniformly distributed constellations; for one-dimensional codes with expansion factor 4 versus two-dimensional codes with factor 2, the approximation error may differ materially at practical constellation sizes. It would be helpful to add a worked example in Section IV-B verifying that γ(C) gives identical values under both the Λ-relative and Z^N-relative interpretations for at least one CS-type code, and to bound the asymptotic approximation error for the specific constellation sizes used in each code class.

**Effective Coding Gain Rule of Thumb Is Unjustified, Inconsistently Applied, and Drives the Key Comparative Conclusion**

The rule that 'every factor of two increase in the error coefficient reduces the coding gain by about 0.2 dB' is stated without derivation, without citation, and without specification of the SNR range or error rate at which it applies. It is applied uniformly across codes whose error coefficients Ñ_0 span three orders of magnitude (from 4 to over 16,000), yet the paper simultaneously declines to compute γ_eff for lattice codes on the grounds that 'our rule of thumb is questionable when the number of nearest neighbors is so high.' This asymmetric treatment is the direct basis for Conclusion 2 of Section VII—that trellis codes dominate lattice codes in effective performance—making that conclusion methodologically circular: the rule is applied where it favors trellis codes and withheld where it would penalize them less severely. For codes like the 8-state E_8/RE_8 CS code with Ñ_0 = 764, the correction could easily exceed 1 dB, making the rule unreliable precisely where it matters most. It would be helpful to either derive the 0.2 dB/factor-of-two rule from a union bound at a specified operating point, apply a consistent metric (even if approximate) to both lattice and trellis codes, or reframe Conclusion 2 as a conjecture supported by qualitative reasoning rather than a finding supported by tabulated data.

**Minimum Squared Distance Claims for Class III and IV Codes Rest on an Unverified Partition Property**

The analysis of Class III codes based on E_8/RE_8/2E_8 in Section VI invokes the existence of an 'alternative partition E_8/R*E_8/2E_8' such that the coset representatives [R*E_8/2E_8] simultaneously serve as coset representatives for E_8/RE_8. This non-trivial geometric property of E_8 is asserted without proof, with a forward reference to Part II. The correctness of d²_min(C) = 16 for the 16-state Class III code depends entirely on this assertion: without it, merging paths could have distance only d²_min(RE_8) = 8 rather than 16, reducing the claimed coding gain from 6.02 dB to 4.52 dB. The same structural property underlies the Class IV d²_min analysis. Since Part I is stated to be independently readable, this gap is significant: the headline coding gain values for these code classes are conditional on results proven only in Part II. It would be helpful to either include the key lemma about R*E_8 in Part I or to clearly flag that the coding gain values for Class III and IV codes are conditional on a specific result in Part II, with a precise forward reference to the relevant lemma.

**Eight-Class Taxonomy Is Not Shown to Be Exhaustive or Non-Overlapping**

Section VI introduces eight code classes (I–VIII) defined by three binary characteristics—partition type, encoder rate, and constraint length—and presents them as a systematic taxonomy, but neither mutual exclusivity nor collective exhaustiveness is established. The paper itself notes that two-state Class I and Class V codes coincide, that four-state Class II and Class VI codes overlap for D_4/RD_4, and that the four-state Ungerboeck code appears in multiple classes. The classification is also restricted to unit-memory and two-unit-memory encoders and to Barnes-Wall partition families, leaving unclear whether codes with irregular trellis structures, non-Barnes-Wall partitions, rate-k/(k+r) encoders with r > 1, or multi-level partition chains of depth greater than two are excluded by design or by oversight. The Abstract's claim that the framework captures 'practically all known good constructive coding techniques' is therefore not fully substantiated by the classification alone. It would be helpful to either state explicitly that the classification is illustrative rather than exhaustive, define the design space being partitioned, and verify that the eight classes tile it without overlap.

**Decoding Complexity Metric Depends Entirely on Unverified Part II Algorithms and May Obscure True Implementation Costs**

The normalized decoding complexity Ñ_D used throughout Tables II–XI and Fig. 12 is defined as the number of binary operations required by 'the trellis-based decoding algorithms of Part II,' with all algorithmic details deferred to the companion paper. Readers cannot verify the Ñ_D values in Table III (e.g., 5 for Z^4/D_4, 30 for D_8/E_8) or assess whether the complexity measure is appropriate without access to Part II, which means the comparative conclusions of Section VII—including the claim that 'complexity increases only modestly as we go from lattice code to Class I to Class II to Class IV'—cannot be independently evaluated. Additionally, the Viterbi and partition-decoding components of Ñ_D scale differently with the number of states: Viterbi cost grows linearly with 2^s while partition decoding cost is fixed per time step, so the conclusion about modest complexity growth may be an artifact of which component dominates in each comparison. It would be helpful to include a self-contained description of the complexity model and a derivation of Ñ_D for at least one representative partition, and to report the Viterbi and partition-decoding components separately so that the scaling behavior can be assessed.

**Validity of d²_min-Based Performance Predictions Is Not Scoped for High-Dimensional Codes with Large Kissing Numbers**

The entire performance framework of Section IV-B defines coding gain through d²_min and treats the error coefficient Ñ_0 as a secondary correction, but for high-dimensional codes in Classes V–VIII and for lattices like Λ_{16} and Λ_{32}, kissing numbers are enormous (e.g., Ñ_0 = 5084 for H_{32}, 9180 for Λ_{32} in Table II) and the gap between d²_min and the next shell distance may be small. In such cases, the union bound on error probability is dominated not by the nearest-neighbor term but by contributions from multiple distance shells, and the d²_min-based coding gain can be a poor predictor of actual performance at any practical SNR. The paper acknowledges this concern qualitatively but does not quantify the SNR range over which the nearest-neighbor approximation is valid for each code class. Conclusions such as 'it takes 256 states to get 6 dB' implicitly assume that 6 dB of d²_min gain translates to 6 dB of actual SNR gain, which may not hold for codes with Ñ_0 in the thousands. It would be helpful to identify, for each code class, the approximate SNR threshold below which the nearest-neighbor approximation breaks down, so that the performance comparisons in Tables IV–XI and Fig. 12 are properly scoped.

**Status**: [Pending]

---

## Detailed Comments (25)

### 1. Power Cost Explanation Conflates Encoder Redundancy with Total Redundancy

**Status**: [Pending]

**Quote**:
> This translates into an average power cost of a factor of $2^{\rho(C)}$ (or $\rho(C) \cdot 3.01$ dB), which is reflected in the formula for the fundamental coding gain $\gamma(\mathbb{C})$ just given.

**Feedback**:
The constellation expansion factor is $2^{\rho(C)}$ (encoder redundancy only), but the coding gain formula uses $\rho(\mathbb{C}) = \rho(C) + \rho(\Lambda)$. These coincide only when $\rho(\Lambda)=0$, i.e., $\Lambda = Z^N$. For CS-type codes built on $E_8$ (where $\rho(E_8)=1$), the power cost of constellation expansion is $2^{\rho(C)}$, while the additional $2^{-\rho(\Lambda)}$ factor in the gain formula accounts for the density advantage of $\Lambda$ over $Z^N$. The current text conflates these two contributions, making it appear the entire $2^{-\rho(\mathbb{C})}$ penalty arises from constellation expansion alone. It would be helpful to rewrite as: 'This translates into an average power cost of $2^{\rho(C)}$ due to constellation expansion; the additional factor $2^{-\rho(\Lambda)}$ accounts for the power efficiency of $\Lambda$ relative to $Z^N$, so the total normalization is $2^{-\rho(\mathbb{C})}$.'

---

### 2. Inline Editorial Correction Left in Published Text

**Status**: [Pending]

**Quote**:
> This suggests that we shall want to choose a code partition chain $C_{\mu - 1} / C_{\mu - 2} / \dots / C_0$ for which the Hamming distances are in the ratio $2 / 4 / \dots$ (Wait, corrected to $1:2:4 \dots$).

**Feedback**:
Working through the minimum squared distance formula $d_{\min}^2 = \min[2^\mu, 2^{\mu-1}d_H(C_{\mu-1}), \ldots, d_H(C_0)]$, the terms are equalized when $d_H(C_j) \propto 2^j$, giving the ratio $d_H(C_0):d_H(C_1):\cdots = 1:2:4:\cdots$. The parenthetical '(Wait, corrected to $1:2:4\dots$)' is an unedited authorial note confirming the original ratio '$2/4/\ldots$' was wrong. This should be cleaned up to read simply 'the Hamming distances are in the ratio $1:2:4:\dots$'.

---

### 3. Dual Lattice Code Formula Index Reversal Not Explicitly Stated

**Status**: [Pending]

**Quote**:
> then its dual lattice $\Lambda^{\perp}$ is a decomposable complex binary lattice of depth $\mu$, with code formula
> 
> $$
> \Lambda^ {\perp} = \phi^ {\mu} \mathbf {G} ^ {N} + \phi^ {\mu - 1} C _ {0} ^ {\perp} + \dots + C _ {\mu - 1} ^ {\perp}
> $$
> 
> where $C_j^\perp$ is the dual code to $C_j$.

**Feedback**:
The formula reverses the index order: in $\Lambda$ the coefficient of $\phi^{\mu-1}$ is $C_{\mu-1}$, while in $\Lambda^\perp$ it is $C_0^\perp$. The prose 'where $C_j^\perp$ is the dual code to $C_j$' implies a same-index correspondence, contradicting the displayed formula. Verifying with $E_8$ ($\mu=2$, $C_1=(4,3,2)$, $C_0=(4,1,4)$): the formula gives $\Lambda^\perp = \phi^2 G^4 + \phi C_0^\perp + C_1^\perp = \phi^2 G^4 + \phi(4,3,2) + (4,1,4) = E_8$, confirming the index reversal is correct in the formula but the prose is misleading. It would be helpful to rewrite as 'where the code at level $j$ in $\Lambda^\perp$ is $C_{\mu-1-j}^\perp$, the dual of $C_{\mu-1-j}$ in $\Lambda$.'

---

### 4. Exponent Typesetting Error in Partition Index Formula

**Status**: [Pending]

**Quote**:
> $|\Lambda' / \phi^{\mu} G^{N}| = 2[k(\Lambda')]$

**Feedback**:
The expression '$2[k(\Lambda')]$' reads as '$2$ times $k(\Lambda')$' rather than '$2$ to the power $k(\Lambda')$'. All other partition indices in the same sentence use exponential notation: $|G^N/\Lambda| = 2^{r(\Lambda)}$, $|\Lambda/\Lambda'| = 2^{k+r}$, and the product must equal $|G^N/\phi^\mu G^N| = 2^{N\mu}$. The bracket should be a superscript. Rewrite as $|\Lambda' / \phi^{\mu} G^{N}| = 2^{k(\Lambda')}$.

---

### 5. Final Coding Gain Formula Uses μ Where Derivation Establishes ρ

**Status**: [Pending]

**Quote**:
> This last expression is the simplest and shows that we need to know only the minimum squared distance $d_{\min}^2(\mathbb{C})$ and the normalized redundancy $\mu(\mathbb{C})$ to compute the fundamental coding gain $\gamma(\mathbb{C}) = 2^{-\mu(\mathbb{C})}d_{\min}^2(\mathbb{C})$, where the normalized redundancy is simply the sum of the normalized redundancies of the code $C$ and the lattice $\Lambda$.

**Feedback**:
The preceding display equations establish $\gamma(\mathbb{C}) = 2^{-\rho(\mathbb{C})}d_{\min}^2(\mathbb{C})$ where $\rho(\mathbb{C}) = \rho(C) + \rho(\Lambda)$. The symbol $\mu(\mathbb{C}) = \mu(\Lambda')$ denotes the depth of the partition, not the redundancy. For $Z^2/2Z^2$, depth $\mu=2$ while redundancy $\rho=1$, so these differ by a factor of two. Calling $\mu(\mathbb{C})$ the 'normalized redundancy' in the final formula contradicts the established notation. Rewrite as '$\gamma(\mathbb{C}) = 2^{-\rho(\mathbb{C})}d_{\min}^2(\mathbb{C})$, where the normalized redundancy $\rho(\mathbb{C}) = \rho(C) + \rho(\Lambda)$.'

---

### 6. Viterbi Complexity Formula Uses 2^{k+r} Instead of 2^{k+s}

**Status**: [Pending]

**Quote**:
> for each of the $2^s$ states, the Viterbi algorithm requires $2^k$ additions and a comparison of $2^k$ numbers, or $2^k - 1$ binary comparisons, so that its complexity is $\beta 2^{k + r}$, where $\beta = 2 - 2^{-k}$, and $2^{k + r}$ is the number of branches per stage of the trellis, which is the measure of complexity used by Ungerboeck [21], following Wei [11].)

**Feedback**:
Summing over all $2^s$ states, each requiring $2^k$ additions and $2^k-1$ comparisons, gives total Viterbi cost per stage $= \beta \cdot 2^{k+s}$. For multi-memory encoders ($s > r$) this differs from $\beta \cdot 2^{k+r}$. Verifying against Table IV for the 8-state $Z^2/2RZ^2$ code ($s=3$, $k=2$, $r=1$, partition cost $Q=8$): $\tilde{N}_D = 8 + 1.75 \times 2^5 = 8 + 56 = 64$ (table: 64 ✓). Every multi-memory entry is consistent with $\beta \cdot 2^{k+s}$, not $\beta \cdot 2^{k+r}$. Rewrite '$\beta 2^{k+r}$' as '$\beta 2^{k+s}$' and '$2^{k+r}$ is the number of branches per stage' as '$2^{k+s}$ is the total number of branches per stage.'

---

### 7. 128-State 2D Z²/2RZ² Complexity Value 902 Should Be 904

**Status**: [Pending]

**Quote**:
> | 2 | $Z^2$ | $2RZ^2$ | 128 | 2/3 | 1 | 8 | 4 | 6.02 | 344 | 902 |

**Feedback**:
Using the verified formula $\tilde{N}_D = Q + \beta \cdot 2^{k+s}$ with $Q=8$, $\beta=1.75$, $k=2$, $s=7$: $\tilde{N}_D = 8 + 1.75 \times 512 = 8 + 896 = 904$. All other entries in the $Z^2/2RZ^2$ block are consistent with this formula (16-state: 120, 32-state: 232, 64-state: 456, 256-state: 1800, 512-state: 3592). The value 902 appears to be a typographical error; rewrite as 904.

---

### 8. 64-State D₄/RD₄ Table Entry Contradicts Note's Corrected d²_min

**Status**: [Pending]

**Quote**:
> | 4 | $D_4$ | $RD_4$ | 64 | 3/4 | 1 | 8 | 4 | 6.02 | 828 | 512 | 4.48 |

**Feedback**:
The 'Note added in proof' explicitly states that Chow found $d_{\min}^2 = 6$ (not 8) for this code, with $\tilde{N}_0 = 16$ (not 828). Recomputing: $\gamma = 2^{-1} \times 6 = 3$, giving $10\log_{10}(3) = 4.77$ dB; $\gamma_{\text{eff}} = 4.77 - 0.2\log_2(16/4) = 4.77 - 0.40 = 4.37$ dB, matching the note's stated 4.37 dB exactly. The main table entry's $\gamma = 4$ and 6.02 dB are therefore incorrect per the paper's own note. The row should be updated to $d_{\min}^2=6$, $\gamma=3$, dB$=4.77$, $\tilde{N}_0=16$, $\gamma_{\text{eff}}=4.37$ dB.

---

### 9. Redundancy ρ=1/2 Appears Inconsistent with Rate 4/5 in N=4 Without Stated Convention

**Status**: [Pending]

**Quote**:
> | 4 | $Z^4$ | $2D_4$ | 128 | 4/5 | 1/2 | 6 | $6/2^{1/2}$ | 6.28 | 728 | 2040 | 4.77 |

**Feedback**:
With rate $k/(k+r) = 4/5$ and $N=4$ real dimensions, the encoder contributes 1 redundant bit per 4-dimensional symbol. Under the paper's convention $\rho = 2r/N$ (redundancy per two dimensions), $\rho = 2 \times 1/4 = 1/2$, which matches the table. However, this convention is not restated at this point in the paper, and a reader applying $\rho = r/N$ (per real dimension) would obtain $\rho = 1/4$, giving $\gamma = 6/2^{1/4} \approx 5.05$ (7.03 dB), inconsistent with the tabulated 6.28 dB. The analogous $N=8$ row (rate 4/5, $\rho=1/4$) is consistent with $\rho = 2/8 = 1/4$. It would be helpful to add a column header footnote confirming that $\rho$ is measured per two real dimensions throughout all tables.

---

### 10. Class III d²_min=16 Depends on Unverified R*E₈ Partition Property

**Status**: [Pending]

**Quote**:
> For the $E_8 / RE_8 / 2E_8$ code, we use the fact that there exists an alternative partition $E_8 / R^*E_8 / 2E_8$, where $R^*E_8$, like $RE_8$, is a version of $E_8$ with $d_{\min}^2 = 8$, such that the system of coset representatives $[R^*E_8 / 2E_8]$ is also a system of coset representatives for $E_8 / RE_8$ (see part II); this ensures that $d_{\min}^2 = 8$ when paths merge as well as when they diverge, so that $d_{\min}^2(\mathbb{C}) = d_{\min}^2(2E_8) = 16$.

**Feedback**:
The correctness of $d_{\min}^2(\mathbb{C}) = 16$ for the 16-state Class III code depends entirely on this non-trivial geometric property of $E_8$, which is asserted without proof and deferred to Part II. Without it, merging paths could have distance only $d_{\min}^2(RE_8) = 8$, reducing the claimed coding gain from 6.02 dB to 4.52 dB—a difference of 1.5 dB. Since Part I is stated to be independently readable, this gap is significant: the headline coding gain for Class III $E_8/RE_8/2E_8$ is conditional on a result proven only in Part II. It would be helpful to either include the key lemma about $R^*E_8$ in Part I or clearly flag that the 6.02 dB figure is conditional on a specific result in Part II.

---

### 11. Effective Coding Gain Rule of Thumb Applied Asymmetrically Between Trellis and Lattice Codes

**Status**: [Pending]

**Quote**:
> We have not even given an effective coding gain $\gamma_{\mathrm{eff}}$ for lattice codes because our rule of thumb is questionable when the number of nearest neighbors is so high.

**Feedback**:
The 0.2 dB per factor-of-two rule is applied to trellis codes with $\tilde{N}_0$ spanning three orders of magnitude (4 to 764 for the CS $E_8/RE_8$ 8-state code), yet withheld from lattice codes on the grounds that their error coefficients are 'so high.' For the 8-state CS code with $\tilde{N}_0 = 764$, the correction would be $0.2 \times \log_2(764/4) \approx 1.5$ dB—making the rule unreliable precisely where it is still applied. This asymmetric treatment directly supports Conclusion 2 of Section VII that trellis codes dominate lattice codes, making that conclusion methodologically circular. It would be helpful to either derive the rule from a union bound at a specified operating point, apply a consistent metric to both code classes, or reframe Conclusion 2 as a conjecture.

---

### 12. Decoding Complexity Ñ_D Defined by Unverifiable Part II Algorithms

**Status**: [Pending]

**Quote**:
> the number of binary operations required by the trellis-based decoding algorithms of part II to determine the closest element of each of the $|\Lambda/\Lambda'|$ cosets of $\Lambda'$ in the partition $\Lambda/\Lambda'$ to an arbitrary point $r$ in $2N$-space.

**Feedback**:
All $\tilde{N}_D$ values in Tables II–XI and the comparative conclusions of Section VII rest on algorithms defined only in Part II. Readers of Part I in isolation cannot verify entries such as $\tilde{N}_D = 5$ for $Z^4/D_4$ or $\tilde{N}_D = 30$ for $D_8/E_8$, nor assess whether the Viterbi and partition-decoding components scale consistently. The paper's own stated goal is that Part I 'may be read independently,' which is contradicted by this dependency. It would be helpful to include a self-contained description of the complexity model and a derivation of $\tilde{N}_D$ for at least one representative partition in Section III.

---

### 13. Time-Zero Lattice Λ₀ 'Ordinarily a Lattice' Claim Is Unverified

**Status**: [Pending]

**Quote**:
> Ordinarily, $\Lambda_0$ is a lattice, which we call the time-zero lattice.

**Feedback**:
The word 'ordinarily' introduces an unexplained exception. For $\Lambda_0$ (the union of $2^k$ cosets of $\Lambda'$ indexed by time-zero encoder outputs) to be a lattice, the set of coset representatives $\{c(\mathbf{a}_0)\}$ must form a subgroup of $\Lambda/\Lambda'$. The paper does not characterize when this fails or what happens to $V(\mathbb{C})$ in that case, yet Lemma 1 ($V(\Lambda_0) = 2^{-k}V(\Lambda')$) is stated only for lattices. It would be helpful to specify the condition on $C$ under which $\Lambda_0$ is guaranteed to be a lattice and confirm that all codes in the paper satisfy this condition.

---

### 14. Eight-Class Taxonomy Not Shown to Be Exhaustive or Non-Overlapping

**Status**: [Pending]

**Quote**:
> We describe eight different classes of codes $\mathbb{C}(\Lambda / \Lambda'; C)$, based on all possible choices of the three following binary characteristics.

**Feedback**:
The paper itself notes that two-state Class I and Class V codes coincide, that four-state Class II and Class VI codes overlap for $D_4/RD_4$, and that the four-state Ungerboeck code appears in multiple classes. The classification is also restricted to unit-memory and two-unit-memory encoders and to Barnes-Wall partition families, leaving unclear whether codes with irregular trellis structures or non-Barnes-Wall partitions are excluded by design or oversight. The Abstract's claim that the framework captures 'practically all known good constructive coding techniques' is therefore not fully substantiated. It would be helpful to either state explicitly that the classification is illustrative rather than exhaustive, or verify that the eight classes tile the defined design space without overlap.

---

### 15. Folk Theorem State-Count Claims Implicitly Assume Small Error Coefficient

**Status**: [Pending]

**Quote**:
> In summary, we propose a folk theorem: it takes two states to get 1.5 dB, four states to get 3 dB, 16 states to get 4.5 dB, perhaps 64 states to get 5.25 dB, and 256 states to get 6 dB, as long as we require a reasonably small error coefficient (for trellis codes).

**Feedback**:
The folk theorem is stated for trellis codes with the qualifier 'reasonably small error coefficient,' but the paper's Conclusion 1 states 'trellis codes and lattice codes are comparable, with respect to fundamental parameters such as fundamental coding gain $\gamma$ versus number of states $2^s$.' These two statements are in tension: if lattice codes are comparable on $\gamma$ vs. $2^s$, the folk theorem should apply to them too, but the error-coefficient qualifier effectively excludes them. Readers might note that the folk theorem should either be scoped explicitly to trellis codes with $\tilde{N}_0 < 100$, or the comparison with lattice codes in Conclusion 1 should be qualified to acknowledge that lattice codes are excluded from the folk theorem's scope.

---

### 16. Typo: Both Sides of Density Comparison Use Same Symbol Λ_N^M

**Status**: [Pending]

**Quote**:
> $\Lambda_N^M$ has a greater or lesser density of points per unit volume than does $\Lambda_N^M$ according to whether $\gamma(\Lambda_N)$ is greater or less than $\gamma(\Lambda_M)$

**Feedback**:
Both sides of the comparison are written as $\Lambda_N^M$, making the sentence compare a lattice to itself. The context makes clear that the comparison is between the $M$-fold Cartesian product of an $N$-dimensional lattice $\Lambda_N$ (written $\Lambda_N^M$, living in $MN$-space) and the $N$-fold Cartesian product of an $M$-dimensional lattice $\Lambda_M$ (written $\Lambda_M^N$, also living in $MN$-space). The second occurrence of $\Lambda_N^M$ should be $\Lambda_M^N$.

---

### 17. Effective Coding Gain for 64-State Honig Code Inconsistent with 0.2 dB Rule

**Status**: [Pending]

**Quote**:
> | 64 | | 054 | 161 | 14 | 3.5 | 5.44 | 16 | *64 | 132 | 4.94 | H |

**Feedback**:
For the 64-state Honig code, $\gamma = 5.44$ dB and the dominant (starred) coefficient is $\tilde{N}_1 = 64$. Applying the stated rule of 0.2 dB per factor-of-two with reference $\tilde{N}_0 = 4$: correction $= 0.2 \times \log_2(64/4) = 0.2 \times 4 = 0.80$ dB, giving $\gamma_{\text{eff}} = 5.44 - 0.80 = 4.64$ dB. The table reports 4.94 dB, a discrepancy of 0.30 dB. Using the non-starred $\tilde{N}_0=16$ instead gives $5.44 - 0.40 = 5.04$ dB, still 0.10 dB off. The paper notes that Eyuboglu and Li use a more refined formula incorporating $\tilde{N}_1$ and $\tilde{N}_2$, but this formula is never stated, making starred entries unverifiable. It would be helpful to add a footnote stating the exact combination formula used when the dominant coefficient is starred.

---

### 18. Wei D₈⁺/RE₈ Redundancy ρ=1 Not Derivable from Information Given

**Status**: [Pending]

**Quote**:
> | 8 | $D_8^+$ | $RE_8$ | 64 | 4/5 | 1 | 8 | 4 | 6.02 | 316 | 584 | 4.76 |

**Feedback**:
For rate $k/(k+r)=4/5$ with $N=8$, the encoder contributes $\rho_{\text{encoder}} = 2 \times 1/8 = 1/4$ per two dimensions. The table shows $\rho=1$, implying $\rho(D_8^+) = 3/4$ relative to $Z^8$. By contrast, the $Z^8/E_8$ entries show $\rho=1/4$ with the same rate-3/4 encoder and $\rho(Z^8)=0$. The paper states 'Wei's lattice DE8 is here called $D_8^+$' but does not give $D_8^+$'s determinant or density relative to $Z^8$, making $\rho=1$ unverifiable from the information in this section. It would be helpful to add a row to Table II giving $\det(D_8^+)$ and $d_{\min}^2(D_8^+)$ so that $\rho(D_8^+)$ can be verified directly.

---

### 19. E₈/RE₈ Codes Show Constant d²_min Across All State Counts Without Explanation

**Status**: [Pending]

**Quote**:
> | 8 | $E_8$ | $RE_8$ | 8 | 3/4 | 5/4 | 8 | $2^{7/4}$ | 5.27 | 764 | 90 | 3.75 |

**Feedback**:
All four $E_8/RE_8$ entries list $d_{\min}^2 = 8$ regardless of the number of trellis states (8, 16, 32, 64). Since $d_{\min}^2(E_8) = 4$ and $d_{\min}^2(RE_8) = 8$, parallel transitions in the trellis are separated by only $d_{\min}^2(E_8) = 4$ unless the encoder specifically avoids them. It is not immediately clear how the 8-state code achieves $d_{\min}^2 = 8$ rather than 4. By contrast, the $Z^2$ and $D_4$ families show $d_{\min}^2$ increasing with state count. It would be helpful to add a clarifying note explaining why $d_{\min}^2$ remains 8 for all state counts in the $E_8/RE_8$ family and verifying that the 8-state code's parallel-transition distance equals 8.

---

### 20. R Is an Improper Rotation (Includes Reflection), Not a Pure Rotation

**Status**: [Pending]

**Quote**:
> $R\mathbb{Z}^2$ is a version of $\mathbb{Z}^2$ obtained by rotating $\mathbb{Z}^2$ by $45^\circ$ and scaling by $2^{1/2}$

**Feedback**:
The matrix $R = \begin{bmatrix}1&1\\1&-1\end{bmatrix}$ has $\det(R) = -2$, so $(1/\sqrt{2})R$ has determinant $-1$, making it an improper orthogonal transformation (a reflection composed with a rotation), not a pure rotation. A pure $45°$ rotation has determinant $+1$. While this does not affect the algebraic correctness of $R^2 = 2I$ or the sublattice claim, describing $R$ as 'rotating $Z^2$ by $45°$' is geometrically imprecise. Readers might note that the description should read 'rotating and reflecting $Z^2$ by $45°$' or simply 'applying the linear map $R$.'

---

### 21. Partition Order Formula: Ambiguous Dimension Variable

**Status**: [Pending]

**Quote**:
> $$
> \left| \Lambda / \Lambda^ {\prime} \right| = 2 ^ {N \left(\mu \left(\Lambda^ {\prime}\right) - \rho (\Lambda) - \kappa \left(\Lambda^ {\prime}\right)\right)}
> $$
> 
> where $2N$ is the dimension of $\Lambda$ as a real lattice.

**Feedback**:
The formula uses $N$ as the complex dimension, while the parenthetical says '$2N$ is the real dimension,' which is consistent. However, a reader who interprets $N$ in the exponent as the full real dimension would obtain a formula with the exponent doubled. Since $\rho(\Lambda) = r(\Lambda)/N$ and $\kappa(\Lambda') = k(\Lambda')/N$ are defined using $N$ as the complex dimension, the clarification should be made explicit. It would be helpful to rewrite as 'where $N$ is the complex dimension of $\Lambda$ (equivalently, $2N$ is its real dimension), consistent with the definitions of $\rho$ and $\kappa$ above.'

---

### 22. Minimum Hamming Distance Argument Omits Constraint on Minimum Path Length

**Status**: [Pending]

**Quote**:
> The minimum Hamming distance of this code (taking the outputs as $c(\mathbf{a})$) is five, because the distance between distinct paths is at least two where they diverge, two where they merge, and one somewhere in between.

**Feedback**:
The argument that $d_H = 5$ requires that diverge and merge events occur at distinct time steps with at least one intermediate step, so all three contributions (≥2 at diverge, ≥1 in between, ≥2 at merge) are present simultaneously. The argument does not explicitly rule out a two-step error event where diverge and merge are adjacent, which would give only ≥2+≥2=≥4 without the middle term. For this 4-state encoder the minimum error event spans at least 3 branches, but this follows from the encoder structure and is not stated. Readers might note that adding a sentence confirming the minimum error event length would make the $d_H=5$ argument self-contained.

---

### 23. Shape Gain Definition Is Circular

**Status**: [Pending]

**Quote**:
> $\gamma_{s}$ is defined as $\gamma_{\mathrm{tot}}(\mathbb{C}) / \gamma (\mathbb{C})$

**Feedback**:
$\gamma_s$ is defined as the ratio of $\gamma_{\text{tot}}$ to $\gamma$, but $\gamma_{\text{tot}}$ is itself introduced in the same sentence as the product of $\gamma$ and $\gamma_s$. Neither quantity has been independently defined before this point, so the ratio definition provides no independent content. The parenthetical immediately following gives the actual geometric characterization ('approximately equal to the ratio of the normalized second moment of an $N$-cube to that of the region...'). Readers might note that the geometric definition should be primary, with the product relation as a consequence.

---

### 24. GCS vs. CS Code Parameters Mixed in Table VI Without Flagging

**Status**: [Pending]

**Quote**:
> TABLE VI GCS-TYPE CODE
> 
> | $N$ | $\Lambda$ | $\Lambda'$ | $2^s$ | $k/(k+r)$ | $\rho$ | $d^{2}_{min}$ | $\gamma$ | dB | $\tilde{N}_{0}$ | $\tilde{N}_{D}$ | $\gamma_{eff}$(dB) |
> | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
> | 4 | $Z^4$ | $2Z^4$ | 8 | 3/4 | 1/2 | 4 | $2^{3/2}$ | 4.52 | 44 | 64 | 3.82 |

**Feedback**:
The surrounding text states that $\tilde{N}_0 = 44$ is the error coefficient 'for the Calderbank-Sloane (CS) version (as given in [13]),' implying the Gallager version has a different (larger) $\tilde{N}_0$. The table header says 'GCS-TYPE CODE' but mixes structural parameters from the Gallager encoder with the CS error coefficient without flagging this. Additionally, the sentence defining GCS-type codes is cut off by a page break before completing. It would be helpful to add a footnote clarifying which parameters belong to which variant and to complete the truncated definition sentence.

---

### 25. R² = 2I Acknowledgment Inconsistent with Analogy to φ² = 2i

**Status**: [Pending]

**Quote**:
> The correspondence is not exact because $R$ includes a reflection as well as rotation and scaling, so that $R^2 = 2I$, whereas $\phi^2 = 2i$.

**Feedback**:
The paper correctly notes $R^2 = 2I$ (verified: $R = \begin{bmatrix}1&1\\1&-1\end{bmatrix}$ gives $R^2 = 2I$) and $\phi^2 = 2i$ (since $\phi = 1+i$ gives $\phi^2 = 2i$). The stated reason for the discrepancy—that $R$ includes a reflection—is correct ($\det(R) = -2$, so $(1/\sqrt{2})R$ has determinant $-1$). However, the sentence implies the reflection is the sole reason $R^2 = 2I$ differs from $\phi^2 = 2i$, whereas the deeper reason is that $2I$ and $2i$ are different objects ($2I$ is a real scalar matrix, $2i$ is a complex scalar). Readers might note that the analogy is between $R$ acting on $\mathbb{R}^2$ and $\phi$ acting on $\mathbb{C}$, and the discrepancy arises because $i \neq I$ as operators, not solely because of the reflection.

---
