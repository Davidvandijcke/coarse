# Coset Codes-Part I: Introduction and Geometrical Classification

**Date**: 3/3/2026, 8:59:20 PM
**Domain**: Example
**Taxonomy**: Demo
**Filter**: Active comments

---

## Overall Feedback

Here are some high-level reactions to the text.


**Outline**

The paper proceeds in a logical sequence, moving from historical context to specific geometric definitions. First, it establishes the general framework of coset codes defined by a lattice partition $\Lambda/\Lambda'$ and a binary encoder $C$. Second, it provides a self-contained primer on lattice theory, specifically focusing on binary lattices and their decomposition. Third, it applies this framework to classify specific lattice families (such as Barnes-Wall) and trellis codes. The final sections are intended to compare these schemes in terms of performance versus complexity.


**Broadness of the central classification**

The introduction states that "practically all" constructive coding techniques for band-limited channels can be modeled as coset codes. Readers generally expect such sweeping universality to be supported by explicit mappings for the major families of existing codes, such as the multidimensional TCM schemes of Wei or the Calderbank–Sloane codes. Currently, the text focuses heavily on the 4-state Ungerboeck code and Barnes-Wall lattices. It would be helpful to either include specific parameterizations for the other major families to demonstrate the framework's universality or, alternatively, to align the introductory claims with the specific subset of lattice codes fully detailed in the text.


**Distinguishing synthesis from new results**

The manuscript combines a synthesis of existing lattice theory (referencing Construction A, Barnes-Wall lattices, and work by Calderbank and Sloane) with a new unifying perspective. Because the exposition is so seamless, it is occasionally difficult to distinguish the synthesis of known mathematics from the novel contributions of this specific paper. A distinct subsection itemizing which definitions, structural lemmas, and complexity comparisons are original to this work would help the audience appreciate the specific theoretical advances being made here.


**The predictive value of fundamental coding gain**

The framework evaluates schemes primarily via the fundamental coding gain $\gamma(\mathbb{C}) = 2^{-\rho(\mathbb{C})} d_{\min}^2(\mathbb{C})$. While the text categorizes shaping gain as "peripheral," relying solely on $\gamma$ leaves a gap between the geometric classification and practical modem performance. Readers looking for concrete engineering trade-offs might look for analytical bounds or simulations that link the $\gamma$-ordering to error rates or capacity gaps at finite SNRs. Clarifying whether the classification is intended only for asymptotic, infinite-lattice behavior or for practical operation would resolve this ambiguity.


**Precision in the proposed taxonomy**

The text aims to categorize "known types of coset codes" and systematize them. However, without explicit $(\Lambda/\Lambda', C)$ descriptions for the broader set of industry-standard codes mentioned in the introduction, the work risks looking like a partial survey rather than a definitive classification. Providing precise definitions for the "generic classes" introduced later would allow experts to use the framework to locate any given practical scheme within the design space.


**Self-containment relative to Part II**

Several key structural arguments—particularly regarding redundancies, partition chains, and decoding complexity—rely on results cited from the "to appear" companion paper (Part II). Since the taxonomy and performance claims hinge on these lattice parameters, the current text forces the reader to accept certain premises on faith. Incorporating the essential proofs or theorems directly into this manuscript would ensure the classification is rigorous and verifiable on its own terms.

**Status**: [Pending]

---

## Detailed Comments (19)

### 1. Minimum distance argument for Class VI codes

**Status**: [Pending]

**Quote**:
> Furthermore, it ensures that if the input sequence has a finite number of nonzero $\boldsymbol{x}_{t}$, then the encoder outputs are nonzero at at least three different times: once when the sequence begins, once at some inter-
mediate time when $T$ has a nonzero output, and once when the last nonzero input finally leaves the encoder. Consequently, the minimum distance between two distinct paths is at least $3 d_{\min }^{2}(\Lambda)$, so that the minimum distance of the code is $d_{\text {min }}^{2}(\mathbb{C})=d_{\text {min }}^{2}\left(\Lambda^{\prime}\right)=2 d_{\text {min }}^{2}(\Lambda)$

**Feedback**:
The minimum-distance argument for Class VI codes relies on the statement that any finite-weight input sequence produces encoder outputs that are nonzero in at least three time instants, leading to a path-distance lower bound of $3 d_{\min}^2(\Lambda)$. It is not clear how this follows from property b) of circuit $T$ ("no infinite input sequence produces a finite output sequence"), and for the simple example $T$ given in the Class V section (output $(\boldsymbol{x}_{t-1},0)$) this three-output property appears to fail. For that $T$, an input impulse on a coordinate other than the first produces nonzero outputs only at two times. In that case the generic lower bound on the distance between distinct paths is only $2 d_{\min}^2(\Lambda)$, so it is not established that path distances are strictly greater than $d_{\min}^2(\Lambda') = 2 d_{\min}^2(\Lambda)$, nor that the error coefficient is necessarily equal to that of $\Lambda'$. This part of the Class VI discussion would benefit from either a more restrictive, explicit condition on $T$ that guarantees the three-output property, or a revised argument that justifies the stated minimum distance and error coefficient.

---

### 2. Inconsistency in Decoding Complexity Calculation

**Status**: [Pending]

**Quote**:
> N_{D} is the number of decoding operations using the trellis-based decoding algorithms of the partition \Lambda / \Lambda^{\prime} whose complexity is given in Table III, followed by a conventional Viterbi algorithm for the convolutional code, and \tilde{N}_{D}=2 N_{D} / N is the decoding complexity per two dimensions. (For each unit of time, for each of the 2^{\nu} states, the Viterbi algorithm requires 2^{k} additions and a comparison of 2^{k} numbers, or 2^{k}-1 binary comparisons, so that its complexity is \beta 2^{k+\nu}, where \beta=2-2^{-k}, and 2^{k+\nu} is the number of branches per stage of the trellis, which is the measure of complexity used by Ungerboeck [21], following Wei [11].)

**Feedback**:
The definition immediately before Table IV states that $N_D$ is the sum of the complexity of decoding the partition $\Lambda/\Lambda'$ (from Table III) and the complexity of the Viterbi algorithm, with $\tilde N_D = 2 N_D / N$ as the normalized figure. For the two-dimensional Ungerboeck codes, the reported $\tilde N_D$ values are consistent with this rule: they equal the sum of the Table III partition complexity and the Viterbi complexity, normalized as described.

For the one-dimensional Ungerboeck codes based on $Z/4Z$, however, the tabulated $\tilde N_D$ values appear to equal the Viterbi complexity alone (i.e., $2 \beta 2^{k+\nu}/N$ with $k=1$), with no additional term that could be attributed to decoding the partition $Z/4Z$. Since $Z/4Z$ is not listed in Table III, it is unclear whether its partition complexity has been deliberately neglected, treated as negligible, or handled by a different convention.

This discrepancy between the stated definition of $N_D$ and the way the 1D entries of Table IV are actually computed can make it difficult for a reader to reproduce the numbers and to understand exactly what operations are being counted. It would be helpful either to clarify explicitly that, for the one-dimensional $Z/4Z$ codes, $N_D$ intentionally includes only the Viterbi component, or to revise the table so that the 1D entries consistently incorporate the partition-decoding complexity as defined.

---

### 3. Clarity of argument for mod-4 lattice structure

**Status**: [Pending]

**Quote**:
> For a further refinement, let $\Lambda_{e}$ be the set of all points in $\Lambda$ whose coordinates are all even. Then $\Lambda_{e}$ is a lattice, a sublattice of $\Lambda$, with $\boldsymbol{4} \boldsymbol{Z}^{N}$ as a sublattice, so $\Lambda / \Lambda_{e} / \boldsymbol{4} \boldsymbol{Z}^{N}$ is a partition chain, and there is a coset decomposition of the form $\Lambda=\boldsymbol{4} \boldsymbol{Z}^{N}+\left[\Lambda_{e} / \boldsymbol{4} \boldsymbol{Z}^{N}\right]+\left[\Lambda / \Lambda_{e}\right]$. The lattice $\Lambda_{e}$ is clearly a mod-2 lattice scaled by a factor of 2 ; consequently, $\Lambda_{e}=4 \boldsymbol{Z}^{N}+2 C$, where $C$ is a binary ( $N, K^{\prime}$ ) code for some $K^{\prime}$, by Lemma 3; in other words, the coset representatives $\left[\Lambda_{e} / \boldsymbol{4} \boldsymbol{Z}^{N}\right]$ may be taken as $2 C$, or $\left\{2 \sum a_{k} \boldsymbol{g}_{k}\right\}$, where the $\boldsymbol{g}_{k}$ constitute a set of $K^{\prime}$ binary generators for the code $C$. Thus we may take $K^{\prime}$ of the generators to be $2 \boldsymbol{g}_{k}, 1 \leq k \leq K^{\prime}$, and we may write

$$
\Lambda=4 \boldsymbol{Z}^{N}+2 C+\left\{\sum a_{k} \boldsymbol{g}_{k}\right\}
$$

where the $\boldsymbol{g}_{k}, K^{\prime}+1 \leq k \leq K$, are $N$-tuples of integers modulo 4 that are not all even, such that $\left\{\sum a_{k} \boldsymbol{g}_{k}\right\}$ is a system of coset representatives $\left[\Lambda / \Lambda_{e}\right]$. The generators $\left\{2 \boldsymbol{g}_{k}, K^{\prime}+1 \leq k \leq K\right\}$ generate a lattice $\Lambda^{\prime}$ that is a sublattice of $\Lambda_{e}$, whose elements are congruent to $2 \boldsymbol{c}^{\prime}$ modulo 4, where $c^{\prime}$ is a codeword in a binary ( $N, K-K^{\prime}$ ) block code $C^{\prime}$ that is a subcode of the code $C$, so $K-K^{\prime} \leq K^{\prime}$.

**Feedback**:
In the paragraph beginning "For a further refinement, let $\Lambda_e$ be the set of all points in $\Lambda$ whose coordinates are all even," the transition from the generators $2g_k$ for $k>K'$ to the statement about a binary subcode $C'\subset C$ is quite compressed. The text asserts that the lattice generated by $\{2g_k,\,K'+1\le k\le K\}$ has elements congruent to $2c'$ modulo 4 for $c'$ in an $(N,K-K')$ code $C'$ that is a subcode of $C$, but it does not spell out how $C'$ is defined from $C$ or why it must be nested.

Because $\Lambda_e=4\boldsymbol{Z}^N+2C$ has already been established, the intended reasoning is that each $2g_k\in\Lambda_e$ must satisfy $2g_k\equiv 2c'_k\pmod{4}$ for some $c'_k\in C$, and the binary code $C'$ is the subcode of $C$ generated by these $c'_k$. Making this map from $\Lambda_e$ to $C$ explicit, and then noting that the image of the sublattice $\Lambda'\subset\Lambda_e$ under this map is a subcode $C'\subset C$, would more clearly justify the subcode relationship. Adding one or two sentences along these lines would align this real mod‑4 argument with the more explicit complex mod‑2 argument given later in Lemma 4 and make the structure of general mod‑4 lattices easier to follow.

---

### 4. Undefined notation for the dual of a Barnes-Wall lattice

**Status**: [Pending]

**Quote**:
> Thus $\Lambda(n, n)^{\perp}=\boldsymbol{G}^{N} \simeq \boldsymbol{Z}^{2 N}, \Lambda(0, n)^{\perp}= \Lambda(n)$, and $\Lambda(n-1, n)^{\perp}, n \geq 1$, is the dual $D_{N}^{\perp}$ of the checkerboard lattice $D_{N}$, with code formula $D_{N}^{\perp}=\phi \boldsymbol{G}^{N}+ \mathrm{RM}(0, n)=\phi \boldsymbol{G}^{N}+(N, 1, N)$, where $N=2^{n}$ and $(N, 1, N)$ is the repetition code of length $N$.

**Feedback**:
The sentence listing special cases of the duals of the principal sublattices includes the identity
$\Lambda(0, n)^{\perp}= \Lambda(n)$. The notation $\Lambda(n)$, with a single argument, is not defined elsewhere in the paper; the family is consistently denoted $\Lambda(r, n)$, and Barnes–Wall lattices themselves are written as $\Lambda(0, n)$ (or with subscripts such as $\Lambda_{16}$). Moreover, just above, you have shown that $\Lambda(0, n)$ is self-dual, and the general dual code formula specialized to $r=0$ reproduces the original code formula for $\Lambda(0, n)$. In this context, it appears that the right-hand side should read $\Lambda(0, n)$, and that "$\Lambda(n)$" is a typographical slip introducing undefined notation and an apparent contradiction with the stated self-duality. Clarifying or correcting this identity would prevent possible confusion.

---

### 5. Path enumeration for Class V error coefficient

**Status**: [Pending]

**Quote**:
> The coefficient of $N_{\Lambda}^{2}$ follows from the observation that in the code trellis, starting from a given zero state and ending at some later zero state, there are $2^{k}-1$ nonzero paths of length $2,2^{k-1}-1$ nonzero paths of length 3 , and so forth, up to $2-1=1$ nonzero path of length $k+1$, so that the total number of nonzero paths is $2^{k+1}-k-2$ (this is generally true for any noncatastrophic rate- $k /(k+1)$ encoder; see Forney [26]).

**Feedback**:
The derivation of the coefficient of $N_{\Lambda}^{2}$ in the Class V error coefficient is not very transparent from the description of the encoder in Fig. 13(d). As written, the sentence reads as though "nonzero paths" means all paths in the state diagram that start and end in the zero state with no intermediate zero states. If one models the state as the previous $k$‑bit input block, a straightforward counting argument then gives $(2^k-1)^{L-1}$ such input sequences of length $L$, which does not match the claimed pattern $2^k-1,2^{k-1}-1,\dots,2-1$ for $L=2,\dots,k+1$.

It would help if you could clarify precisely what class of rate‑$k/(k+1)$ encoders is being considered in this counting (e.g., whether $T$ is assumed memoryless and the state is exactly $x_{t-1}$, or whether you are invoking a particular canonical realization from [26]), and what exactly is meant by "nonzero paths" (distinct zero‑state error events in the code trellis, as opposed to arbitrary nonzero input or state sequences). A brief reminder of the relevant result from [26], or a more specific pointer into that reference, would make it easier for the reader to see why the factor $2^{k+1}-k-2$ is appropriate here.

---

### 6. Incorrect example for γ=3 codes in Discussion

**Status**: [Pending]

**Quote**:
> There is a nearby cluster of codes that achieve $\gamma=3$ ( 4.77 dB ), with either $\mu=3, \rho=1$ and $d_{\min }^{2}=6$, or $\mu=4$, $\rho=2$ and $d_{\text {min }}^{2}=12$; e.g., the 16- and 32-state two-dimensional Ungerboeck codes, the 16-state CS/Eyuboglu codes, or the 16 -state Class III and Class VII codes.

**Feedback**:
In the quoted sentence, the 16‑state Class III code is cited as an example of a code that "achieve[s] $\gamma=3$ (4.77 dB)." This appears inconsistent with the parameters given earlier in the paper. According to Table XI, the only 16‑state Class III instance is the $N=8$ code based on the partition $E_8/2E_8$, with normalized redundancy $\rho=2$ and $d_{\min}^2=16$, so its fundamental coding gain is $\gamma = 2^{-2}\cdot 16 = 4$ (6.02 dB), not 3. The $N=4$ Class III code based on $D_4/2D_4$ has $d_{\min}^2=6$ and $\rho=3/2$, giving $\gamma = 3/\sqrt{2} \approx 2.12$ (3.27 dB), but this is a 4‑state code, not 16‑state. Thus none of the tabulated Class III constructions lies at $\gamma=3$, even though the 16‑state Class VII example in the same sentence (based on $D_8^{\perp}/RE_8$) does. It would be helpful to correct or clarify this part of the Discussion so that the listed examples of $\gamma=3$ codes align with the parameters in Table XI.

---

### 7. Definition of fundamental volume and redundancy in the Introduction

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> The fundamental coding gain of the coset code is denoted by $\gamma(\mathbb{C})$ and is defined by two elementary geometrical parameters: the minimum squared distance $d_{\text {min }}^{2}(\mathbb{C})$ between signal point sequences in $\mathbb{C}$ and the fundamental volume $V(\mathbb{C})$ per $N$ dimensions, which is equal to $2^{r(\mathbb{C})}$ where the redundancy $r(\mathbb{C})$ is equal to the sum of the redundancy $r(C)$ of the encoder $C$ and the redundancy $r(\Lambda)$ of the lattice $\Lambda$. In fact,

$$
\gamma(\mathbb{C})=2^{-\rho(\mathbb{C})} d_{\min }^{2}(\mathbb{C})
$$

where the normalized redundancy $\rho(\mathbb{C})$ (per two dimensions) is equal to $2 r(\mathbb{C}) / N$.

**Feedback**:
At first the statement that the "fundamental volume $V(\mathbb{C})$ per $N$ dimensions … is equal to $2^{r(\mathbb{C})}$ where … $r(\mathbb{C})$ is equal to … $r(\Lambda)$ of the lattice $\Lambda$" made me think this relation was being asserted in full generality, even though the notion of lattice redundancy $r(\Lambda)$ had not yet been defined. Then I understood from Sections II.E and III.B that $r(\Lambda)$ is introduced specifically for binary lattices, with $V(\Lambda)=2^{r(\Lambda)}$ under the normalization $V(\mathbb{Z}^N)=1$, and that $V(\mathbb{C})=2^{r(\mathbb{C})}$ is a consequence of these later results in that restricted setting.

To avoid any momentary ambiguity, it might help if this introductory paragraph signaled more explicitly that the formula $V(\mathbb{C})=2^{r(\mathbb{C})}$ (and the appearance of $r(\Lambda)$) rely on the binary-lattice framework developed in Section II, or if a brief forward reference to the later definition of $r(\Lambda)$ were added here.

---

### 8. Role of algebraic structure in the coset code framework

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> In general, these code constructions rely very little on the linearity properties of the groups (e.g., lattices, sublattices) on which they are based, and the codes so constructed are often not linear, particularly the trellis codes. The essential properties of these sets seem to be their partition structure and related distance properties, which of course were the basis for Ungerboeck's constructions via 'mapping by set partitioning.' The primary benefit of starting with sets that are groups seems to be that their subgroups naturally induce useful partitions via coset decompositions.

**Feedback**:
At first the sentence "these code constructions rely very little on the linearity properties of the groups … on which they are based" made me wonder whether this was meant to downplay the importance of the underlying group structure itself, which is clearly required to define coset partitions. Then I understood from the continuation ("the codes so constructed are often not linear") and from the surrounding discussion that the intended contrast is between linear-code structure (in the usual coding sense) and the partition/distance properties that actually drive performance.

To make this distinction immediately transparent, it might still help to indicate more explicitly what notion of "linearity" is meant here—e.g., linearity of the resulting codes over GF(2) versus the more basic group axioms that enable coset decompositions—so that readers do not conflate the two when interpreting this paragraph.

---

### 9. Description of coset representatives in Sec. II.F

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Thus the $2^{K}$ binary linear combinations $\left\{\sum a_{k} \boldsymbol{g}_{k}\right\}$ of the generators $\boldsymbol{g}_{k}$ are a system of coset representatives $\left[\Lambda_{k} / \Lambda_{k+1}\right]$ for the partition $\Lambda_{k} / \Lambda_{k+1}$ (this is a special case of a general result for groups of order $2^{K}-$ binary groups-discussed in part II).

**Feedback**:
The sentence

"Thus the $2^{K}$ binary linear combinations $\{\sum a_k \boldsymbol{g}_k\}$ of the generators $\boldsymbol{g}_k$ are a system of coset representatives $[\Lambda_k / \Lambda_{k+1}]$ for the partition $\Lambda_k / \Lambda_{k+1}$ …"

appears inconsistent with the definitions just given. Each intermediate quotient $\Lambda_k / \Lambda_{k+1}$ is explicitly two‑way, so any system of coset representatives for such a partition should contain exactly two vectors, whereas the set $\{\sum a_k \boldsymbol{g}_k\}$ has $2^K$ elements. 

Reading Lemma 2 immediately below makes the intended structure clear: for each $k$, the pair $\{a_k \boldsymbol{g}_k, a_k\in\{0,1\}\}$ serves as representatives for the two-way partition $\Lambda_k / \Lambda_{k+1}$, and the $2^K$ combinations $\{\sum a_k \boldsymbol{g}_k\}$ form a system of representatives for the overall partition $\Lambda / \Lambda'$. To avoid the cardinality mismatch, it would be helpful to correct this sentence so that the role of the $2^K$ combinations is associated with the full partition $\Lambda / \Lambda'$ rather than with a single two-way quotient $\Lambda_k / \Lambda_{k+1}$.

---

### 10. Notation for a lattice in Table III

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> TABLE III
Useful Lattice Partitions
| Λ | $\Lambda^{\prime}$ | $2 N$ | $\left\|\Lambda / \Lambda^{\prime}\right\|$ | $\mu$ | $\kappa$ | $\rho$ | $d_{\text {min }}^{2}(\Lambda)$ | $d_{\text {min }}^{2}\left(\Lambda^{\prime}\right)$ | $\tilde{N}_{D}$ | $\tilde{N}_{D} /\left\|\Lambda / \Lambda^{\prime}\right\|$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
...
| $D_{8}^{1}$ | $R E_{8}$ | 8 | 32 | 3 | 1 | 3/4 | 2 | 8 | 88 | 2.75 |
...

**Feedback**:
The lattice labeled $D_8^1$ in Table III does not seem to be defined anywhere in the paper or in Tables I–II. However, all the numerical parameters in that row (index 32, depth 3, $\kappa=1$, $\rho=3/4$, $d_{\min}^2(\Lambda)=2$, $d_{\min}^2(\Lambda')=8$) match exactly what one obtains for the partition $D_8^{\perp}/R E_8$, where $D_8^{\perp}$ is the dual of the checkerboard lattice $D_8$ as defined in Section II‑H. It would be helpful to correct the notation in Table III from $D_8^1$ to $D_8^{\perp}$ (or otherwise define $D_8^1$ explicitly) so that the table is consistent with the earlier dual‑lattice notation and with the subsequent discussion of the $D_8^{\perp}/R E_8$ partition in Section V.

---

### 11. Inconsistent encoder description for Class II codes

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Let $\Lambda / \Lambda^{\prime}$ again be a $2^{2 k}$-way lattice partition with $d_{\text {min }}^{2}\left(\Lambda^{\prime}\right)=2 d_{\text {min }}^{2}(\Lambda)$. Let $C$ be a rate- $1 / 2,2^{2 k}$-state convolutional encoder as shown in Fig. 13(b), with $k$ information bits entering in each time unit, two units of memory, and $2 k$ output bits, $k$ representing the inputs one time unit earlier, and $2 k$ representing the mod- 2 sum of the current inputs with those two time units earlier, which together select one of the $2^{2 k}$ cosets of $\Lambda^{\prime}$.

**Feedback**:
Statement "$2k$ output bits, $k$ representing the inputs one time unit earlier, and $2k$ representing the mod‑2 sum of the current inputs with those two time units earlier" seemed to imply a total of $3k$ bits rather than $2k$ output bits. After checking Fig. 13(b) and the surrounding discussion, it is clear that there are two $k$‑bit output groups: one equal to the previous input vector and the other equal to the mod‑2 sum of the current input with that two time units earlier. It would help to adjust the wording so that it is explicit that the $2k$ outputs consist of these two $k$‑bit groups, and thus avoid the impression that an extra $2k$‑bit component is present.

---

### 12. Parameter mismatch for lattice X_32 in Discussion

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Note also that the lattices $X_{24}$ and $X_{32}$ achieve $\gamma=2^{3 / 2}(4.52 \mathrm{~dB})$ and $\gamma=2^{13 / 8}(4.89 \mathrm{~dB})$ with 8 and 16 states, respectively, but with $\mu=2, \rho=1 / 2$ and $d_{\min }^{2}=4$, like the Wei codes.

**Feedback**:
In the Discussion paragraph comparing $X_{24}$ and $X_{32}$ to Wei's codes, the normalized redundancy is stated as $\rho = 1/2$ for both lattices. According to Table II and the code formulas, $X_{24}$ has $\rho = 1/2$ but $X_{32}$ has $\rho = 3/8$, while both have $\mu = 2$ and $d_{\min}^2 = 4$. It would be good to adjust this sentence so that the value of $\rho$ quoted for $X_{32}$ is consistent with Table II.

---

### 13. Decoding complexity as a geometric parameter

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> The fundamental coding gain of a coset code, as well as other important parameters such as the error coefficient, the decoding complexity, and the constellation expansion factor, are purely geometric parameters determined by $C$ and $\Lambda / \Lambda^{\prime}$.

**Feedback**:
Statement that "the decoding complexity … [is a] purely geometric parameter" initially made me think you were putting complexity on exactly the same footing as quantities like $d_{\min}^2$ and $V(\mathbb{C})$, derived directly from the Euclidean embedding of the code. Then I understood from Sections I‑D, III, and V that you are working with a specific complexity measure tied to canonical trellis/partition ML decoders, so that once $C$ and $\Lambda/\Lambda'$ are fixed (and $C$ is taken in minimal form), the corresponding decoding complexity is indeed an intrinsic parameter of the code, just like $d_{\min}^2$ and $N_0$.

Because "purely geometric" is used earlier in a more narrow sense (distances, volumes, densities), it might be helpful in the abstract to slightly soften or qualify this wording when referring to decoding complexity, e.g. by indicating that complexity is an intrinsic algorithmic parameter determined by $(C,\Lambda/\Lambda')$ rather than a geometric invariant in the strict sense. This would reduce the chance that readers interpret the phrase more literally than you intend.

---

### 14. Mismatch in coset decomposition formulas

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> A partition chain induces a multiterm coset decomposition chain, with a term corresponding to each partition; e.g., if $\Lambda / \Lambda^{\prime} / \Lambda^{\prime \prime}$ is a partition chain, then

$$
\Lambda=\Lambda^{\prime \prime}+\left[\Lambda^{\prime} / \Lambda^{\prime \prime}\right]+\left[\Lambda / \Lambda^{\prime}\right]
$$

meaning that every element of $\Lambda$ can be expressed as an element of $\Lambda^{\prime \prime}$ plus a coset representative from $\left[\Lambda^{\prime} / \Lambda^{\prime \prime}\right]$ plus a coset representative from $\left[\Lambda / \Lambda^{\prime}\right]$. For example, the chain $\boldsymbol{Z} / \mathbf{2} \boldsymbol{Z} / \mathbf{4 Z} / \cdots$ leads to the standard binary representation of an integer $m$ :

$$
m=a_{0}+2 a_{1}+4 a_{2}+\cdots
$$

where $a_{0}, a_{1}, a_{2}, \cdots \in\{0,1\}$, and $a_{0}$ specifies the coset in the partition $\boldsymbol{Z} / 2 \boldsymbol{Z}, 2 a_{1}$ specifies the coset in the partition $2 \boldsymbol{Z} / 4 \boldsymbol{Z}$, and so forth. That is,

$$
\boldsymbol{Z}=[\boldsymbol{Z} / 2 \boldsymbol{Z}]+[2 \boldsymbol{Z} / 4 \boldsymbol{Z}]+[4 \boldsymbol{Z} / 8 \boldsymbol{Z}]+\cdots
$$

**Feedback**:
At first the multi-term formula
$\Lambda = \Lambda'' + [\Lambda'/\Lambda''] + [\Lambda/\Lambda']$
made me expect that every example of a partition chain decomposition would show an explicit "base lattice" term. Then, in the integer example for the chain $\boldsymbol{Z}/2\boldsymbol{Z}/4\boldsymbol{Z}/\cdots$, the expression
\[
\boldsymbol{Z} = [\boldsymbol{Z}/2\boldsymbol{Z}] + [2\boldsymbol{Z}/4\boldsymbol{Z}] + [4\boldsymbol{Z}/8\boldsymbol{Z}] + \cdots
\]
involves only coset-representative sets, and no obvious analogue of the $\Lambda''$ term. After reading more carefully, it is clear that here the chain is infinite and its intersection is the trivial lattice $\{0\}$, so the "finest" sublattice term is just $\{0\}$ and can be omitted without effect; this reconciles the two views. Still, it might help some readers if you briefly noted in the text that, for the integer chain, the limiting sublattice is $\{0\}$, which is why the binary expansion can be written purely as a sum of coset representatives.

---

### 15. Description of the Ungerboeck encoder in Sec. IV.A

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> For example, the four-state Ungerboeck code shown in Figs. 2 and 3 uses the four-state rate-1/2 convolutional code whose encoder and trellis diagram are illustrated in Fig. 10. Contrary to convention, the encoder is shown in coset code form, using the partition ( $2,2,1$ )/ $(2,1,2) /(2,0, \infty)$ of binary codes of length 2 . Let $\boldsymbol{g}_{0}$ be a coset representative for the nonzero coset in the partition $(2,2) /(2,1)$, e.g., $\boldsymbol{g}_{0}=[10]$, and let $\boldsymbol{g}_{1}$ be the coset representative for the nonzero coset in the partition $(2,1) /(2,0)$, i.e., $\boldsymbol{g}_{1}=[11]$.

**Feedback**:
Statement "Contrary to convention, the encoder is shown in coset code form, using the partition (2,2,1)/(2,1,2)/(2,0,∞) of binary codes of length 2" initially made me wonder whether the convolutional encoder $C$ itself was being characterized as a coset code. However, the following sentences make clear that what is being constructed is the labeling map $c(a)$: $g_0$ and $g_1$ are coset representatives for the short block-code partition chain, and $c(a)=a_0 g_0 + a_1 g_1$ maps the encoder output bits to coset representatives, while $C$ remains a conventional four-state rate-1/2 convolutional code as in Fig. 10. To avoid any momentary ambiguity about what is meant by "encoder" here, it might help to say explicitly that it is the labeling (or overall coset-code encoder) that is being shown in coset code form, rather than the internal convolutional encoder $C$ itself.

---

### 16. Incorrect formula for lattice coding gain

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Relative to $\gamma(\Lambda)=2^{-\rho(\Lambda)} d_{\text {min }}^{2}\left(\Lambda^{\prime}\right)$, the gain $\gamma(\mathbb{C})$ is greater by the distance gain factor of $d_{\text {min }}^{2}(\mathbb{C}) / d_{\text {min }}^{2}(\Lambda)$, offset by a power loss of $2^{-\rho(C)}$ due to constellation expansion.

**Feedback**:
The sentence "Relative to $\gamma(\Lambda)=2^{-\rho(\Lambda)} d_{\min }^{2}(\Lambda')$…" appears to contain a notational slip. Earlier, and throughout the paper, the fundamental coding gain of a binary lattice is defined as $\gamma(\Lambda)=2^{-\rho(\Lambda)} d_{\min }^{2}(\Lambda)$, and this is the expression that is used in the displayed formulas immediately before and after this sentence. To keep the narrative statement consistent with those equations and with the general definition, the factor inside $d_{\min}^2(\cdot)$ here should be $\Lambda$, not $\Lambda'$. As written, this single prime does not alter any subsequent derivation (since the correct form is used in the formulas), but changing it would remove a small potential source of confusion.

---

### 17. Incomplete premise in Lemma 6

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Lemma 6: If $\Lambda^{\prime}$ is a mod-2 lattice, $C$ is a $2^{\nu}$-state, rate- $k /(k+r)$ convolutional code and the labeling map $\boldsymbol{c}(\boldsymbol{a})$ is linear modulo $\Lambda^{\prime}$, then a trellis code $\mathbb{C}\left(\Lambda / \Lambda^{\prime} ; C\right)$ is the set of all sequences of integer $N$-tuples that are congruent modulo 2 to one of the words in a $2^{\nu}$-state rate-$[N-r(\mathbb{C})] / N$ convolutional code $C^{\prime}$.

**Feedback**:
At first the premise of Lemma 6, which only assumes that $\Lambda'$ is a mod‑2 lattice, made me think that $\Lambda$ might be allowed to be an arbitrary lattice, so that the conclusion about "sequences of integer $N$‑tuples" and the appeal to Lemma 5 would require stronger local hypotheses. Then I understood from the beginning of Section IV that, throughout this section, both $\Lambda$ and $\Lambda'$ are assumed to be binary lattices (hence integer lattices), and that the extra requirement in Lemma 6 is only that $\Lambda'$ be mod‑2 so that the reduction to the partition $\boldsymbol{Z}^N/2\boldsymbol{Z}^N$ applies.

Given that global setup, the logic and conclusion of Lemma 6 are sound. However, because the sentence just before the lemma speaks of "the important case where $\Lambda/\Lambda'$ is a partition of mod‑2 binary lattices" while the lemma statement itself mentions only $\Lambda'$ being mod‑2, it may be helpful to align the wording. Explicitly reminding the reader in or near the lemma that $\Lambda$ is a binary lattice (as per the section‑wide assumption) would make the statement more self‑contained and avoid any momentary doubt about whether further conditions on $\Lambda$ are intended.

---

### 18. Parameter comparison between Wei code and X24 lattice

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Of all the codes we have considered, a few stand out as "special." The four-state two-dimensional Ungerboeck code is certainly in this category because it is the unique code with $\gamma=2$ and $\tilde{N}_{0}=4$ and because of its symmetries and close relationship to the special lattice $E_{8}$. As mentioned before, the 256 -state one-dimensional Ungerboeck code is also special because it is a code with $\gamma=4$ and $\tilde{N}_{0}=4$, which makes it the trellis cousin of the very special lattice $\Lambda_{24}$. The 16-state four-dimensional Wei code is the single code that most clearly improves on the Ungerboeck-type codes; note that it has the same parameters as the lattice $X_{24}$.

**Feedback**:
At first the sentence "note that it has the same parameters as the lattice $X_{24}$" made me think that all listed quantities for the 16-state four-dimensional Wei code and $X_{24}$ were being claimed equal, including dimension, number of states, and error coefficient, which they clearly are not. Then I understood from the following parenthetical about $\Lambda_{16}$, and by checking Tables II and VII, that "same parameters" here is meant in the more specific sense of the geometric parameters $(\mu,\rho,d_{\min}^2,\gamma)$, for which the Wei code and $X_{24}$ do coincide. Because other readers may also initially read "parameters" more broadly, it could help to say explicitly which parameters are intended in this comparison, to avoid any momentary confusion when cross-checking the tables.

---

### 19. Unclear reference to "last three codes"

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> They also consider the following: Ungerboeck-type codes based on partitions $\boldsymbol{Z} / \mathbf{4} \boldsymbol{Z}, \boldsymbol{Z}^{2} / 2 \boldsymbol{Z}^{2}$ and $\boldsymbol{Z}^{2} / 2 R \boldsymbol{Z}^{2}$, but without improvement over Ungerboeck either in fundamental coding gain $\gamma$ or in error coefficient $\tilde{N}_{0}$, except for the $\nu=6$ case also found by Pottie and Taylor; the GCS-type code based on the partition $\boldsymbol{Z}^{4} / 2 \boldsymbol{Z}^{4}$, as previously mentioned; and codes using the nonbinary two-dimensional hexagonal lattice $A_{2}$, for which the results are not particularly encouraging. The last three codes appear to be equivalent to the aforementioned translation of Wei's $\boldsymbol{Z}^{8} / E_{8}$ codes.

**Feedback**:
At first the phrase "The last three codes appear to be equivalent to the aforementioned translation of Wei's $\boldsymbol{Z}^{8} / E_{8}$ codes" made me think it was referring to the three code families just enumerated in the parenthesis (Ungerboeck-type 1D/2D codes, the GCS-type $\boldsymbol{Z}^4/2\boldsymbol{Z}^4$ code, and the $A_2$ codes), which would be inconsistent dimensionally with the 8-dimensional Wei codes. Then I understood from Tables VII and IX, together with the earlier remark about translating Wei's $\boldsymbol{Z}^8/E_8$ codes to $E_8/R E_8$, that "the last three codes" is intended to denote the last three 8-dimensional $E_8/R E_8$ entries in Table IX (those with $2^\nu = 16, 32, 64), which are indeed equivalent to those translations. It might still help some readers if the intended antecedent of "the last three codes" were identified more explicitly.

---
