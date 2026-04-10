# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/13/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper presents a systematic framework for constructing coset codes based on lattice partitions, classifying eight generic families (Classes I-VIII) of geometrically uniform trellis codes with multilevel structure. It develops analytical expressions for fundamental coding gain, minimum squared distance, and error coefficients under assumptions of distance-invariance and regular labeling, applying these to both decomposable mod-4 lattices and specific high-dimensional constructions. The work compares the performance and complexity of these trellis codes against lattice codes, claiming superior coding gains for certain state complexities, though these results depend on geometric uniformity assumptions that may not hold for all partition chains or nonlinear labelings.

Below are the most important issues identified by the review panel.

**Ambiguous Fundamental Volume Definition and Unverified Regularity Assumptions**

The definition of the fundamental volume $V(\mathbb{C})$ in Section IV-B relies on the time-zero lattice $\Lambda_0$ being a lattice and assumes a Cartesian product isomorphism $\mathbb{C}_0 \cong \Lambda_0 \times \Lambda_0 \times \dots$ that lacks rigorous justification in the infinite-dimensional sequence space topology. For nonlinear trellis codes—which the framework explicitly includes—$\Lambda_0$ may not form a lattice, rendering the application of Lemma 1 invalid and the volume formula $V(\mathbb{C}) = 2^{-k}V(\Lambda')$ technically unsound. Furthermore, the paper asserts that all codes are distance-invariant without verifying that the specific labeling constructions for Classes I-VIII satisfy the regularity conditions required for this property, particularly for decomposable mod-4 lattices where carry operations may break regularity. It would be helpful to either restrict the volume formula to linear/regular codes with proven geometric uniformity or provide rigorous conditions under which the Cartesian product decomposition preserves density for nonlinear labelings.

**Conditional Validity of Class III and VII Minimum Distance Bounds**

The paper claims that Class III and VII codes achieve $d_{\min}^2(\mathbb{C}) = 3d_{\min}^2(\Lambda)$ based on the Ungerboeck distance bound for partition chains with distances in ratio 1:2:4, but this treats a lower bound as a definitive value. The specific example of $E_8/RE_8/2E_8$ in Section VI reveals that an alternative partition $E_8/R^*E_8/2E_8$ is required to achieve the predicted distance, and the actual minimum distance can exceed $3d_{\min}^2(\Lambda)$ (reaching $4d_{\min}^2(\Lambda)=16$ rather than 12) when coset representatives do not align geometrically at merging points. Readers might note that the general classification does not specify the additional constraints on partition chains beyond distance ratios that are necessary to guarantee the bound is met, leaving the taxonomy incomplete for partitions involving indecomposable lattices or complex Barnes-Wall structures.

**Unverified Geometric Uniformity in High-Dimensional Error Coefficients**

The error coefficient formulas for generic code classes (e.g., $N_0 = N_{\Lambda'} + (2^k-1)N_{\Lambda}^2$ for Class I) assume that every nonzero coset of $\Lambda'$ contains the same number $N_{\Lambda}$ of points at minimum distance and that minimum-distance paths are restricted to specific diverge-remerge configurations. This geometric uniformity assumption holds for regular labelings but has not been verified for the specific multidimensional partitions used in high-dimensional codes, such as $D_{16}/H_{16}$, $H_{16}/\Lambda_{16}$, or complex Barnes-Wall lattice partitions where kissing number geometry varies between cosets. It would be helpful to clarify that these formulas assume geometric uniformity and either restrict them to verified symmetric partitions or provide general formulas accounting for coset-dependent multiplicities and alternative minimum-distance error events.

**Theoretical Gaps in Lattice Decomposability and Depth Definitions**

The framework for mod-4 binary lattices assumes decomposability into code formulas $\Lambda = 4\mathbb{Z}^N + 2C_1 + C_0$, yet important lattices like the Leech lattice $\Lambda_{24}$ are fundamentally indecomposable and are included in Table I only with ad-hoc notation without systematic construction methods. Additionally, the relationship between real 2-depth $m$ and complex $\phi$-depth $\mu$ introduces ambiguity, as the text states that a real lattice with 2-depth $m$ has $\phi$-depth $2m$ or $2m-1$, creating uncertainty when calculating partition orders. Readers might also note ambiguity in dual lattice definitions for odd $\phi$-depths, where the alternative real definition yields a rotated version $R\Lambda^\perp$ rather than the complex definition's $\Lambda^\perp$, creating inconsistency when applying duality to partition chains. It would be helpful to standardize the depth conventions and provide systematic methods for handling indecomposable lattices within the same framework.

**Incomplete Noncatastrophicity Proofs for Multi-Level Classes**

The paper asserts that Class V and VI codes are noncatastrophic based on properties of a linear circuit $T$, but provides a complete proof only for the specific example where $T$ outputs $(\mathbf{x}_{t-1}, 0)$. For the general case, the claim that no infinite input sequence generates a finite output sequence is asserted for any $T$ satisfying properties (a) and (b), but no proof is given that these properties are sufficient to prevent catastrophic error propagation in the multi-level lattice partition context. Since catastrophicity depends on the interaction between encoder memory and coset labeling for the two-level partitions used in Classes V-VIII, it would be helpful to complete the proof for the general circuit $T$ or restrict the noncatastrophic claims to the specific verified constructions.

**Misleading Complexity Comparisons Between Lattice and Trellis Codes**

Section VII compares lattice codes and trellis codes using 'number of states' as a common metric, but this conflates fundamentally different computational resources. For lattice codes, complexity $\tilde{N}_D$ measures operations for closest-point search in a finite region, while for trellis codes, it measures Viterbi algorithm operations per decoded bit. The comparison of the 256-state one-dimensional Ungerboeck code with lattice $\Lambda_{32}$ (which has $2^{32}$ states in the trellis sense) obscures that 'states' in lattice codes represent cosets in a partition chain rather than encoder memory elements. It would be helpful to separate the discussion of state complexity (constraint length) from decoding complexity (operations per dimension) when comparing code families to avoid creating an apples-to-oranges comparison that obscures actual implementation differences.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Decoding complexity mischaracterized as geometric parameter

**Status**: [Pending]

**Quote**:
> The fundamental coding gain of a coset code, as well as other important parameters such as the error coefficient, the decoding complexity, and the constellation expansion factor, are purely geometric parameters determined by $C$ and $\Lambda / \Lambda'$

**Feedback**:
It would be helpful to distinguish geometric parameters (such as fundamental coding gain and error coefficient) from decoding complexity, which measures algorithmic effort such as the number of trellis states or operations per decoded bit rather than intrinsic geometric properties. Readers might note that conflating these concepts obscures the distinction between code structure and implementation cost.

---

### 2. Index formula for integer sublattices allows non-positive indices

**Status**: [Pending]

**Quote**:
> More generally, for any $m \in \mathbb{Z}$, the lattice $mZ^{N}$ of all $N$-tuples of integer multiples of $m$ is a sublattice of $Z^{N}$ of order $m^{N}$

**Feedback**:
It would be helpful to restrict $m$ to positive integers and replace $m^N$ with $|m|^N$. For negative $m$ (e.g., $m = -2$ with $N = 1$), the index is $2$, not $-2$. Additionally, for $m = 0$, the index is infinite rather than zero.

---

### 3. Exponent notation ambiguity in sublattice order formula

**Status**: [Pending]

**Quote**:
> More generally, $\phi^{\mu}G$ is a sublattice of $G$ of order $|\phi|^2\mu = 2^\mu$

**Feedback**:
It would be helpful to rewrite $|\phi|^2\mu$ as $(|\phi|^2)^\mu$ or $|\phi|^{2\mu}$ to denote exponentiation. The current notation parses as multiplication $(|\phi|^2) \cdot \mu = 2\mu$, which contradicts the claimed equality $2^\mu$.

---

### 4. Incorrect quotient specification in coset partition chain

**Status**: [Pending]

**Quote**:
> $\phi a_1$ specifies the coset of $\phi^2 G$ in the partition $\phi G / \phi^3 G$

**Feedback**:
It would be helpful to correct '$\phi G / \phi^3 G$' to '$\phi G / \phi^2 G$'. The partition $\phi G / \phi^3 G$ has index $|\phi|^4 = 4$, corresponding to a 4-way partition, whereas the digit $a_1 \in \{0,1\}$ selects between only 2 possibilities. The term $\phi a_1$ determines the coset in the 2-way partition $\phi G / \phi^2 G$ of index $|\phi|^2 = 2$.

---

### 5. Dimension notation inconsistency in real binary lattice definition

**Status**: [Pending]

**Quote**:
> A real $N$-dimensional lattice $\Lambda$ is a binary lattice if it is an integer lattice that has $2^{m}Z^{N}$ as a sublattice for some $m$

**Feedback**:
It would be helpful to specify 'real $2N$-dimensional lattice' to maintain consistency with the complex dimension convention used throughout the section. Subsequent formulas such as $|\Lambda/2^m\mathbb{Z}^{2N}| = 2^{2Nm - r(\Lambda)}$ explicitly use real dimension $2N$, suggesting that $N$ in this definition refers to complex dimension elsewhere.

---

### 6. Incorrect generalization of D4 properties to Dk

**Status**: [Pending]

**Quote**:
> For example, the depth of $D_{k}$ is 1, its redundancy and informativity are both equal to 1, and its normalized redundancy and informativity are both equal to $1/2$

**Feedback**:
It would be helpful to change '$D_{k}$' to '$D_{4}$' to correct the example. For $D_k$, the informativity is $k(\Lambda) = N\mu - r = (k/2)(1) - 1 = k/2 - 1$, which equals 1 only when $k=4$. Similarly, the normalized redundancy $\rho = r/N = 1/(k/2) = 2/k$ equals $1/2$ only for $k=4$.

---

### 7. Coset representatives incorrectly attributed to two-way partition

**Status**: [Pending]

**Quote**:
> Thus the $2^{K}$ binary linear combinations $\{\sum a_{k}\mathbf{g}_{k}\}$ of the generators $\mathbf{g}_{k}$ are a system of coset representatives $[\Lambda_{k} / \Lambda_{k + 1}]$ for the partition $\Lambda_{k} / \Lambda_{k + 1}$

**Feedback**:
It would be helpful to correct the partition reference to '$[\Lambda / \Lambda']$ for the partition $\Lambda / \Lambda'$'. The partition $\Lambda_k/\Lambda_{k+1}$ is a two-way partition of order 2, which requires exactly 2 coset representatives, whereas the $2^K$ binary linear combinations form a complete set of representatives for the full $2^K$-way partition $\Lambda/\Lambda'$.

---

### 8. Barnes-Wall lattice distance progression error

**Status**: [Pending]

**Quote**:
> with distances $1/2/\cdots/2^n$ (for short)

**Feedback**:
It would be helpful to revise the distance progression to $1/2/\cdots/2^{n-1}$. The minimum squared distance of the densest Barnes-Wall lattice $\Lambda(n,n)$ in dimension $2^n$ is $2^{n-1}$, not $2^n$. For example, $\Lambda(3,3) = E_8$ has $d^2_{\min}=4=2^2$, and $\Lambda(4,4)=\Lambda_{16}$ has $d^2_{\min}=8=2^3$, consistent with the pattern $2^{n-1}$.

---

### 9. Isomorphism symbol misuse for partition chain

**Status**: [Pending]

**Quote**:
> $Z^{2N} \simeq \Lambda(n,n) / \Lambda(n-1,n) / \cdots / \Lambda(0,n)$ is a partition chain

**Feedback**:
It would be helpful to replace $\simeq$ with $\supseteq$ or state that $\Lambda(0,n) = \mathbb{Z}^{2N}$ is the coarsest lattice in the chain. The notation $\Lambda(n,n) / \cdots / \Lambda(0,n)$ represents a sequence of nested sublattice inclusions (a partition chain), not an algebraic object isomorphic to $\mathbb{Z}^{2N}$.

---

### 10. Lemma 6 rate formula inconsistency with partition index

**Status**: [Pending]

**Quote**:
> rate- $[N - r(\mathbb{C})] / N$ convolutional code $C'$

**Feedback**:
It would be helpful to correct the rate to $k/N$ where $k = r(\Lambda') - r(\Lambda) - r$ represents the information bits per $N$-tuple. The stated rate $[N - r(\mathbb{C})]/N$ implies $k = N - r - r(\Lambda)$, which equates to the partition-derived value only if $r(\Lambda') = N$. This equality does not hold for general lattices (e.g., when $\Lambda$ is a proper sublattice of $\mathbb{Z}^N$), creating an internal inconsistency in the lemma statement.

---

### 11. Lemma 5 complex rate formula exceeds unity

**Status**: [Pending]

**Quote**:
> rate-$[k + k(\Lambda')] / N\mu$ convolutional code

**Feedback**:
It would be helpful to correct the rate to $[N\mu - r - r(\Lambda)]/N\mu$ to match the real-case formula. The numerator $k + k(\Lambda')$ can exceed $N\mu$ since $k(\Lambda') \approx N\mu - r(\Lambda')$ and $k$ (information bits from the convolutional code) is independent, potentially yielding a rate greater than 1. Additionally, the notation $k(\Lambda')$ (informativity) is not defined in the text.

---

### 12. Typographical dimension mismatch N' versus N

**Status**: [Pending]

**Quote**:
> $\mathbb{C}(G^{N} / \phi^{\mu}G^{N'};C')$ based on the partition $G^{N} / \phi^{\mu}G^{N}$

**Feedback**:
It would be helpful to replace $N'$ with $N$ for consistency. The partition is explicitly defined using $G^N / \phi^\mu G^N$ (dimension $N$), whereas the code notation introduces $N'$ without definition. Since $N$ represents the dimension of $\Lambda$ throughout the section, the $N'$ appears to be a typographical error.

---

### 13. Unstated assumption in distance equality for coset representatives

**Status**: [Pending]

**Quote**:
> It is easy to see that the minimum squared distance between code sequences corresponding to distinct paths in the trellis is the minimum Hamming distance between sequences $c(D)$ of coset representatives and thus is equal to $d_H(C) = 5$

**Feedback**:
It would be helpful to clarify that this equality relies on the specific property that $d_{\min}^2(\mathbb{Z}^2/2\mathbb{Z}^2) = 1$. For general partitions $\Lambda/\Lambda'$, the relationship is $d_{\min}^2 \geq d_H(C) \cdot d_{\min}^2(\Lambda/\Lambda')$. Readers might note that the text assumes a normalized partition distance without explicitly stating this constraint.

---

### 14. Inconsistent bit accounting in Lemma 6 proof sketch

**Status**: [Pending]

**Quote**:
> In the augmented encoder, the $(k + r)$-tuple $a$ and the uncoded bits $a'$ specify a coset of $2Z^{N}$ in the partition $Z^{N} / 2Z^{N}$, which may be specified by a binary $N$-tuple $c'(a, a')$

**Feedback**:
It would be helpful to correct the bit accounting to specify $N - r(\Lambda')$ uncoded bits. For the augmented encoder to achieve the stated rate, the uncoded bits $a'$ must satisfy $|a'| = N - r(\Lambda')$. The text suggests $|a'| = N - (k+r) = N - r(\Lambda') + r(\Lambda)$, which understates the number of uncoded bits by $r(\Lambda)$.

---

### 15. Incorrect formula for maximum sublattice distance

**Status**: [Pending]

**Quote**:
> The codes achieve increasing $d_{\mathrm{min}}^2$ as the number $2^e$ of states increases from 4 to 512, up to the maximum possible value of $d_{\mathrm{min}}^2(\Lambda') = 2^k$

**Feedback**:
It would be helpful to replace '$2^k$' with the actual minimum squared distance of $\Lambda'$. For the one-dimensional codes with $\Lambda' = 4\mathbb{Z}$, the minimum squared distance is 16, whereas $k=1$ gives $2^k=2$. For two-dimensional codes with $\Lambda' = 2R\mathbb{Z}^2$, the distance is 8, whereas $k=2$ gives $2^k=4$. The maximum distance is determined by the geometry of $\Lambda'$ itself, not by the parameter $k$.

---
