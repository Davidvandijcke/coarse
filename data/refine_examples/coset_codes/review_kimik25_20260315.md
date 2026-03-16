# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/14/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a geometric framework for coset coding that unifies the algebraic structure of binary convolutional codes with the geometric properties of lattice partitions Λ/Λ′. It introduces fundamental parameters such as redundancy ρ and informativity κ to characterize trellis codes, derives coding gain formulas based on lattice density, and catalogs specific code constructions (Classes I-VIII) that achieve known optimal performance bounds. The work establishes connections between the depth of lattice partitions and the complexity of trellis representations, aiming to provide a systematic approach to constructing and analyzing signal constellations for bandwidth-efficient modulation.

Below are the most important issues identified by the review panel.

**Ambiguous definition of fundamental volume for non-linear trellis codes**

The paper defines the fundamental volume of a trellis code as V(ℂ) = V(Λ₀), where Λ₀ is the 'time-zero lattice' comprising 2ᵏ cosets of Λ′, and applies the formula V(Λ₀) = 2⁻ᵏV(Λ′) derived from Lemma 1. However, the paper asserts that Λ₀ 'ordinarily' forms a lattice without establishing sufficient conditions, and the decomposition of ℂ₀ as a Cartesian product Λ₀ × Λ₀ × ⋯ assumes a lattice structure that may not hold for non-linear labelings. Since the fundamental coding gain formula γ(ℂ) = 2⁻ρ(ℂ)d²ₘᵢₙ(ℂ) relies critically on this volume calculation, it would be helpful to either restrict the definition to linear trellis codes where the coset representatives form a group under addition modulo Λ′, or provide a generalized volume definition that does not require Λ₀ to be a lattice.

**Unsupported assumption of universal distance-invariance**

In Section IV-B, the paper states that 'All codes in this paper are distance-invariant' without verifying that the specific constructions presented in Classes I-VIII (Section VI) employ regular labelings. While regular labelings are known to ensure distance-invariance, the paper does not demonstrate that this property holds for the general coset code construction ℂ(Λ/Λ′; C), particularly when non-linear labelings are used. It would be helpful to verify that the catalogued codes indeed use regular labelings, or to qualify the error coefficient results and performance comparisons in Section VII as applying specifically to the all-zero sequence or to linear codes only.

**Insufficient justification for binary partition chains (Lemma 2)**

Lemma 2 claims that any partition of binary lattices admits an Ungerboeck labeling—a nested chain of two-way partitions—but assumes without proof that the quotient group Λ/Λ′ is an elementary abelian 2-group and that intermediate sets in the chain remain lattices. For general binary lattices, the quotient may be cyclic (e.g., ℤ/4ℤ), and constructing such chains requires showing that all intermediate Λₖ are discrete subgroups. It would be helpful to provide a complete proof that such chains exist with all intermediate sets being binary lattices, or clarify that the lemma applies only when Λ/Λ′ is elementary abelian, particularly since the general framework in Section I-C suggests applicability to broader group structures.

**Conflation of linear and non-linear properties in geometric classification**

The paper treats the fundamental coding gain and related parameters as 'purely geometric' determinants of the partition Λ/Λ′ and encoder C, yet the geometric interpretation of redundancy ρ and informativity κ relies on the lattice structure of linear codes. When C is non-linear or uses non-linear labelings, the resulting trellis code may not form a lattice, and the equivalence in Lemma 5 between ℂ(Λ/Λ′; C) and codes based on ℤᴺ/2ℤᴺ may not preserve the distance spectrum. It would be helpful to clarify the necessary and sufficient conditions on the labeling c(a) for the code to be linear, distinguish these from conditions ensuring only distance-invariance, and caution that the geometric classification applies rigorously only when the overall code maintains a lattice structure.

**Inconsistencies in depth parameter notation and calculations**

The paper exhibits inconsistencies in the application of depth parameters across tables and definitions. Table III lists the partition D₄/RD₄ as having depth μ = 2, which appears inconsistent with the invariance of depth under scaled orthogonal transformations established in Section II-C, given that D₄ has depth μ = 1. Additionally, Table I uses the symbol μ (complex ϕ-depth) for real lattices such as D₄ and E₈ without distinguishing it from the real 2-depth m defined in Section II-E, creating ambiguity when translating between real and complex representations. It would be helpful to correct the depth entries for rotated lattice partitions in Table III and to clearly distinguish between complex depth μ and real depth m in Table I to maintain consistency with the definitions in Section II-E.

**Unaddressed limitations for indecomposable lattices**

While the paper acknowledges that certain lattices such as the Leech lattice Λ₂₄ are 'fundamentally indecomposable,' the geometric classification in Section III and the generic code constructions in Section VI rely almost exclusively on decomposable lattices with code formulas involving Reed-Muller codes. The paper does not specify which results—such as partition distance bounds, duality relations, or trellis decoding algorithms—remain valid for indecomposable lattices, nor does it provide a framework for classifying coset codes based on such lattices. It would be helpful to explicitly state that the geometric classification and construction methods are restricted to decomposable binary lattices, or to extend the theoretical framework to address the indecomposable case.

**Status**: [Pending]

---

## Detailed Comments (14)

### 1. Unqualified claim of purely geometric coding gain

**Status**: [Pending]

**Quote**:
> The fundamental coding gain of a coset code, as well as other important parameters such as the error coefficient, the decoding complexity, and the constellation expansion factor, are purely geometric parameters determined by $C$ and $\Lambda / \Lambda'$.

**Feedback**:
It would be helpful to qualify this claim by restricting it to linear trellis codes. The fundamental volume $V(\mathbb{C})$ equals $V(\Lambda_0)$, where the formula $V(\Lambda_0) = 2^{-k}V(\Lambda')$ (Lemma 1) holds only if the time-zero lattice $\Lambda_0$ forms a lattice. This requires the labeling map $c(a)$ to be linear modulo $\Lambda'$ so that coset representatives form a group. For non-linear labelings, $\Lambda_0$ is not a lattice and $V(\mathbb{C})$ is not well-defined as a geometric property of the partition alone.

---

### 2. Volume formula assumes binary lattice property

**Status**: [Pending]

**Quote**:
> The fundamental coding gain of the coset code is denoted by $\gamma(\mathbb{C})$ and is defined by two elementary geometrical parameters: the minimum squared distance $d_{\mathrm{min}}^2(\mathbb{C})$ between signal point sequences in $\mathbb{C}$ and the fundamental volume $V(\mathbb{C})$ per $N$ dimensions, which is equal to $2^{r(\mathbb{C})}$ where the redundancy $r(\mathbb{C})$ is equal to the sum of the redundancy $r(C)$ of the encoder $C$ and the redundancy $r(\Lambda)$ of the lattice $\Lambda$.

**Feedback**:
It would be helpful to add the qualification that this volume formula applies when $\Lambda$ is a binary lattice. The claim that $V(\mathbb{C}) = 2^{r(\mathbb{C})}$ relies on the property that $V(\Lambda) = 2^{r(\Lambda)}$, which holds specifically for binary lattices (as established in Section II-E). For non-binary lattices (e.g., $A_2$, $E_8$ scaled differently), $V(\Lambda)$ is not necessarily a power of 2, and $r(\Lambda)$ may not satisfy $V(\Lambda) = 2^{r(\Lambda)}$.

---

### 3. Inconsistent coding gain calculation for lattice X_32

**Status**: [Pending]

**Quote**:
> Note also that the lattices $X_{24}$ and $X_{32}$ achieve $\gamma = 2^{3/2}$ (4.52 dB) and $\gamma = 2^{13/8}$ (4.89 dB) with 8 and 16 states, respectively, but with $\mu = 2, \rho = 1/2$ and $d_{\min}^2 = 4$, like the Wei codes.

**Feedback**:
It would be helpful to correct the coding gain for $X_{32}$ to $\gamma = 2^{3/2}$ (4.52 dB). The text claims that $X_{32}$ achieves $\gamma = 2^{13/8}$ while simultaneously specifying $\rho = 1/2$ and $d_{\min}^2 = 4$. However, the fundamental coding gain is defined as $\gamma = d_{\min}^2 / 2^{\rho}$. Substituting the stated values yields $\gamma = 4 / 2^{1/2} = 2^{3/2} \approx 2.828$ (4.52 dB), not $2^{13/8} \approx 3.08$ (4.89 dB). To achieve $\gamma = 2^{13/8}$ with $\rho = 1/2$ would require $d_{\min}^2 = 2^{17/8} \approx 4.36$, which contradicts the explicit statement that $d_{\min}^2 = 4$.

---

### 4. Incorrect sublattice in D4 partition chain example

**Status**: [Pending]

**Quote**:
> For example, since $Z^4 / D_4 / R Z^4 \simeq \mathbb{G}^2 / D_4 / \phi \mathbb{G}^2$ is a partition chain, $D_4$ is a mod-2 binary lattice with depth $\mu = 1$.

**Feedback**:
It would be helpful to correct the final element of the chain to $\phi^2 \mathbb{G}^2$. For the real lattice $D_4$ with 2-depth $m=1$, the sublattice $2Z^4$ has index $|Z^4/2Z^4| = 16$, and since $|Z^4/D_4| = 2$, the index $|D_4/2Z^4| = 8$. Under the correspondence where $2^m Z^{2N} \simeq \phi^{2m} \mathbb{G}^N$, the sublattice $2Z^4$ corresponds to $\phi^2 \mathbb{G}^2$, not $\phi \mathbb{G}^2$. The lattice $\phi \mathbb{G}^2$ has index $|\mathbb{G}^2/\phi \mathbb{G}^2| = 4$, yielding $|D_4/\phi \mathbb{G}^2| = 2$, which does not match the required index of 8.

---

### 5. Incorrect partition reference for 2^K coset representatives

**Status**: [Pending]

**Quote**:
> Thus the $2^K$ binary linear combinations $\{\sum a_k \mathbf{g}_k\}$ of the generators $\mathbf{g}_k$ are a system of coset representatives $[\Lambda_k / \Lambda_{k+1}]$ for the partition $\Lambda_k / \Lambda_{k+1}$

**Feedback**:
It would be helpful to correct the partition reference to $\Lambda / \Lambda'$. The set $\{\sum_{k=0}^{K-1} a_k \mathbf{g}_k\}$ contains $2^K$ distinct elements, whereas the partition $\Lambda_k / \Lambda_{k+1}$ is two-way (order 2) and thus has only 2 cosets. The $2^K$ linear combinations actually form a system of coset representatives for the full partition $\Lambda / \Lambda'$ (the $2^K$ cosets of $\Lambda'$ in $\Lambda$), not for the intermediate two-way partitions.

---

### 6. Dual partition chain equated to incorrect lattice

**Status**: [Pending]

**Quote**:
> Similarly, $Z^{2N} \simeq \Lambda(n, n)^{\perp} / \Lambda(n-1, n)^{\perp} / \cdots / \Lambda(0, n)^{\perp} = \Lambda(0, n)$ is a partition chain of $2^n$-dimensional complex lattices of depths $0/1/ \cdots /n$ and with distances $1/2/ \cdots /2^n$

**Feedback**:
It would be helpful to remove "$= \Lambda(0, n)$" and correct the terminal element. Since $\Lambda(n, n) \simeq Z^{2N}$, the dual chain begins with $Z^{2N}$ and descends to $\Lambda(0, n)^{\perp}$ (the dual of $\Lambda(0, n)$), not to $\Lambda(0, n)$ itself. Furthermore, equating a chain to a single lattice is notationally inconsistent with the standard use of "/" to separate elements in a partition chain.

---

### 7. Index formula fails for negative and zero integers

**Status**: [Pending]

**Quote**:
> More generally, for any $m \in \mathbb{Z}$, the lattice $mZ^N$ of all $N$-tuples of integer multiples of $m$ is a sublattice of $Z^N$ of order $m^N$

**Feedback**:
It would be helpful to restrict the formula to non-zero integers and use absolute value. For $m = -1$ and $N = 1$, the lattice $(-1)Z = Z$, so the index $[Z : Z] = 1$, but $m^N = (-1)^1 = -1$, which is impossible for a cardinality. For $m = 0$, the lattice $0Z^N = \{0\}$ has infinite index in $Z^N$, whereas $m^N = 0$. The correct formula for the index is $|m|^N$ when $m \neq 0$.

---

### 8. Inconsistent definition of dimension parameter N

**Status**: [Pending]

**Quote**:
> where $\rho(\Lambda)$ is the normalized redundancy (per two dimensions) of $\Lambda, \rho(\Lambda) = r(\Lambda) / N$, where $2N$ is the dimension of $\Lambda$ as a real lattice, or $N$ is the dimension of $\Lambda$ as a complex lattice.

**Feedback**:
It would be helpful to resolve the inconsistent usage of $N$. The parameter $N$ is defined here as half the real dimension (or the complex dimension), yet in the alternative form of Lemma 5, the text states that "$N$ is the dimension of $\Lambda$ or $\Lambda'$ as real lattices," implying $N$ represents the full real dimension in that context. This creates ambiguity for the normalized redundancy $\rho(\Lambda) = r(\Lambda)/N$ and the rate expressions in Lemma 5.

---

### 9. Dimension notation inconsistency in Lemma 5 alternative form

**Status**: [Pending]

**Quote**:
> An alternative form of Lemma 5 is as follows. If the 2-depth of $\Lambda'$ is $m$, then $\mathbb{C}(\Lambda / \Lambda'; C)$ is equivalent to a code $\mathbb{C}(Z^N / 2^m Z^N; C')$ based on the partition $Z^N / 2^m Z^N$, where $C'$ is a $2^v$-state, rate-$[N m - r - r(\Lambda)] / Nm$ convolutional code, and $N$ is the dimension of $\Lambda$ or $\Lambda'$ as real lattices. The proof is essentially the same. Indeed, if $\mu$ is even, $\mu = 2m$, then the partition $Z^{2N} / \Lambda / \Lambda' / 2^m Z^{2N}$ is the same as $\mathbb{G}^N / \Lambda / \Lambda' / \phi^\mu \mathbb{G}^N$, and the augmented encoder $C'$ is the same;

**Feedback**:
It would be helpful to use consistent dimension notation. The alternative form explicitly defines $N$ as the real dimension of $\Lambda$, yet the proof uses $Z^{2N}$ and $\mathbb{G}^N$ interchangeably, where the exponent $2N$ indicates that $N$ is being treated as the complex dimension (since $\mathbb{G}^N \cong Z^{2N}$ as real lattices). If $N$ were the real dimension as claimed, the partition should be $Z^N / 2^m Z^N$ and the isomorphism would involve $\mathbb{G}^{N/2}$, creating a factor of 2 discrepancy.

---

### 10. Undefined geometric parameters for general group coset codes

**Status**: [Pending]

**Quote**:
> More generally, a coset code $\mathbb{C}(S / T; C)$ can be defined whenever $S$ is some set of discrete elements that forms an algebraic group, with some distance measure between elements of $S, T$ is a subgroup of $S$ such that the quotient group $S / T$ has finite order $|S / T|$, and $C$ is an appropriate code whose codewords select sequences of cosets of $T$ in the partition $S / T$.

**Feedback**:
It would be helpful to clarify the scope of the geometric parameters. The fundamental volume $V(\Lambda)$ and the coding gain formula $\gamma = 2^{-\rho} d_{\min}^2$ used earlier rely on the lattice generator matrix determinant, which requires $S$ to be a free $\mathbb{Z}$-module (lattice). For finite groups like PSK constellations or general discrete groups without a lattice structure, these geometric parameters are not defined. Readers might note that the section does not clarify whether the performance analysis is intended to apply only to lattice-based coset codes.

---

### 11. Incorrect orthogonality claim in proof sketch

**Status**: [Pending]

**Quote**:
> This proposition may be verified by noting that $C_0^\perp / \dots / C_{\mu-1}^\perp$ is a code partition chain, that every generator $\phi^{\mu-j-1} g_j^\perp$ of $\Lambda^\perp / \phi^n \mathbb{G}^N$ is orthogonal mod $\phi^\mu$ to every generator $\phi^{j'} g_{j'}$ of $\Lambda / \phi^n \mathbb{G}^N$, and that the dimensions are such that the informativity of $\Lambda^\perp$ is equal to the redundancy of $\Lambda$ and vice versa.

**Feedback**:
It would be helpful to remove the incorrect claim about pairwise orthogonality between generators. The claim that every generator of $\Lambda^\perp / \phi^\mu \mathbb{G}^N$ is orthogonal modulo $\phi^\mu$ to every generator of $\Lambda / \phi^\mu \mathbb{G}^N$ is false. For example, with $\mu=2$, $N=2$, and appropriate codes, the inner product of specific generators can be 1, which is not in $\phi^2\mathbb{G}=2\mathbb{Z}[i]$. The correct property is that generators of $\Lambda^\perp$ are orthogonal to the entire lattice $\Lambda$, not pairwise to each generator of $\Lambda$.

---

### 12. Class II minimum distance bound contradiction

**Status**: [Pending]

**Quote**:
> Because the distance between paths is at least $d_{\min}^2(\Lambda)$ when they diverge, $d_{\min}^2(\Lambda)$ when they merge, and $d_{\min}^2(\Lambda)$ in some other time unit, the distance between distinct paths is at least $3 d_{\min }^2(\Lambda)$. Thus $d_{\min }^2(\mathbb{C})=d_{\min }^2\left(\Lambda^{\prime}\right)=2 d_{\min }^2(\Lambda)$

**Feedback**:
It would be helpful to correct the lower bound to $2d_{\min}^2(\Lambda)$. The text derives a lower bound of $3d_{\min}^2(\Lambda)$ based on the Class II encoder's memory-2 structure (divergence, intermediate, and merge contributions). However, it immediately concludes that $d_{\min}^2(\mathbb{C}) = 2d_{\min}^2(\Lambda)$. Since $3d_{\min}^2(\Lambda) > 2d_{\min}^2(\Lambda)$ for any nontrivial lattice, the lower bound contradicts the final value. Table XI confirms that Class II codes achieve $d_{\min}^2 = 2d_{\min}^2(\Lambda)$, indicating that the minimum-weight error events actually span only two time units.

---

### 13. Typographical error: ϕ^n should be ϕ^μ in code formula

**Status**: [Pending]

**Quote**:
> If $\Lambda$ is a decomposable $N$-dimensional complex binary lattice of depth $\mu$, with code formula
> $$
> \Lambda=\phi^n \mathbb{G}^N+\phi^{\mu-1} C_{\mu-1}+\cdots+C_0,
> $$
> then its dual lattice $\Lambda^\perp$ is a decomposable complex binary lattice of depth $\mu$, with code formula
> $$
> \Lambda^{\perp}=\phi^\mu \mathbb{G}^N+\phi^{\mu-1} C_0^{\perp}+\cdots+C_{\mu-1}^{\perp}
> $$

**Feedback**:
It would be helpful to correct the symbol $n$ to $\mu$ in the first code formula. The symbol $n$ in the first code formula is undefined and inconsistent with the depth parameter $\mu$. For a binary lattice of depth $\mu$, the base lattice must be $\phi^\mu \mathbb{G}^N$ to ensure $\Lambda / \phi^\mu \mathbb{G}^N$ is a finite abelian group. The dual formula correctly uses $\phi^\mu \mathbb{G}^N$, confirming that $n$ is a typographical error for $\mu$.

---

### 14. Typo in Class V error coefficient formula explanation

**Status**: [Pending]

**Quote**:
> The coefficient of $N_0^2$ follows from the observation that in the code trellis, starting from a given zero state and ending at some later zero state, there are $2^k - 1$ nonzero paths of length 2, $2^{k-1} - 1$ nonzero paths of length 3, and so forth, up to $2 - 1 = 1$ nonzero path of length $k + 1$, so that the total number of nonzero paths is $2^{k+1} - k - 2$

**Feedback**:
It would be helpful to correct the subscript in 'coefficient of $N_0^2$' to $N_{\Lambda}^2$. The formula for the multiplicity is given as $N_0 = N_{\Lambda'} + (2^{k+1} - k - 2) N_{\Lambda}^2$. The explanatory text refers to 'The coefficient of $N_0^2$', but the coefficient $(2^{k+1} - k - 2)$ multiplies $N_{\Lambda}^2$ (the square of the number of points at minimum distance in a nonzero coset of $\Lambda'$), not $N_0^2$ (the square of the total multiplicity).

---
