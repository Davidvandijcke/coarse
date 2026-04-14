# Coset Codes

**Date**: 04/13/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper is strongest as a unifying viewpoint and weakest when it moves from representation to exhaustive classification and comparative judgment. The main problems are not small algebra slips; they sit at the level of scope, invariants, and what the tables are allowed to prove.

The central idea is genuinely useful: recasting lattice codes and trellis-coded modulation schemes as coset codes gives the literature a common language and makes several geometric parameters comparable. The lattice primer and the large catalog of partitions are also valuable reference material. The concern is that the paper's biggest claims are broader than the arguments that are actually supplied in Part I.

**The classification claim is broader than the proved design space**

The Abstract and Section I-B say that practically all known good constructive coding techniques for band-limited channels can be characterized as coset codes, and Section VI says the eight generic classes come from "all possible choices" of three binary characteristics. Later, Section III quietly narrows the actual search space to partitions appearing in Fig. 9 with depths no greater than four and orders no greater than 2^12. Those are not the same claim. The paper never states a theorem that the surveyed partitions and classes exhaust the relevant family of binary lattice or trellis-code constructions, and phase-modulated, ternary, hexagonal, and other nonbinary examples are mostly deferred or bracketed off in Section I-C. This matters because the main contribution is framed as a geometrical classification, not just a convenient re-description of familiar examples. The revision should either prove an exhaustion result for a clearly delimited class of codes, or scale back the framing so the paper is presented as a unifying framework plus a curated list of useful families.

**The fundamental volume of a trellis code is introduced heuristically**

Section IV-B builds the whole trellis-code geometry on the time-zero lattice Λ0 and says that Λ0 is "ordinarily" a lattice and that it is "reasonable to define" V(C) = V(Λ0). The later formulas for γ(C), including V(C) = 2^{-k}V(Λ') = 2^r V(Λ) and γ(C) = 2^{-ρ(C)} d_min^2(C), are then used throughout the paper as if they were established invariants. That is too loose for a paper whose comparison tables and Section VII conclusions depend on those identities. The gap is larger for nonlinear or merely regular trellis codes, because the argument passes through equivalence classes modulo C_t rather than a standard lattice quotient and does not show that the resulting notion of density is independent of initialization or labeling choices. Without a theorem here, the paper's basic performance measure for trellis codes is partly a definition rather than a derived property. A revision should state precise hypotheses under which Λ0 exists as a lattice, prove the volume identities under those hypotheses, and mark any remaining cases as heuristic.

**Distance-invariance and regular labeling are asserted faster than they are proved**

Section IV-B says that all codes in the paper are distance-invariant, and Section IV-C says that regular labelings exist for all partitions used in the paper. Yet many of the later minimum-distance and error-coefficient calculations depend on exactly those facts, especially in Tables V-XI and in the generic class constructions of Section VI. For several important families, including the special E8 / R*E8 / 2E8 construction in Section VI and many of the useful partitions summarized in Table III, the paper does not actually display the labeling or prove that the Ungerboeck distance bound holds with equality when that equality is needed. That omission matters because d_min^2(C) and N0 are the quantities driving almost every comparison. A reader is therefore asked to accept a large amount of the classification by analogy rather than by construction. The fix is straightforward: give explicit labeling theorems for each partition family used in the tables, or narrow the claims to the subsets for which regularity and distance-invariance are shown.

**The strongest comparative claims rest on a rough effective-gain heuristic**

Section V introduces "effective coding gain" through a rule of thumb that each doubling of the error coefficient costs about 0.2 dB, while also admitting that higher-distance neighbors matter and that some of the underlying coefficients are unpublished. Section VII then uses that same device to make some of the paper's most sweeping judgments: trellis codes are better than lattice codes on effective gain versus complexity, Ungerboeck codes remain the benchmark, and a "folk theorem" ties coding gain to state complexity. That is more than the heuristic can carry. The paper never derives the 0.2 dB adjustment from a bound, never applies a uniform published error analysis across the listed families, and explicitly notes that the measure is doubtful for lattices with very large kissing numbers. As a result, the editorial conclusions in Section VII are on a weaker footing than the geometric statements earlier in the paper. The revision should either recast those conclusions as informed conjecture or replace the rule of thumb with a formal union-bound or asymptotic analysis based on published spectra for the same code set.

**Complexity comparisons are tied to one decoder model rather than to the code families themselves**

Tables II and III define normalized decoding complexity through the trellis-based algorithms of Part II, and Section VII treats those numbers as if they were intrinsic properties of the code classes being compared. But Section III also says that if RΛ / RΛ' or φΛ / φΛ' is easier to decode than Λ / Λ', the simpler realization is the one reported. That means the quoted complexity is already partly a property of the chosen implementation route rather than of the abstract partition. Lemma 5 creates another problem: it proves representational equivalence to codes over G^N / φ^μ G^N or Z^N / 2^m Z^N, but it does not preserve decoding complexity in any obvious way. This matters because several of the paper's headline takeaways are about performance versus complexity, not just about distance and redundancy. The paper should therefore separate "geometric code parameters" from "complexity under the Part II decoder" and avoid general superiority claims unless it can show that the ranking is stable across reasonable realizations.

**Part I relies too heavily on Part II for claims presented as settled here**

Section I-D says that Part I and Part II may be read independently, but the backbone of Section III is a summary of Part II results, and many key quantities in Tables II and III are accepted by reference rather than derived here. The dependence shows up again in Lemma 2, in the discussion of useful partitions and decoder complexity, and in repeated statements that the needed proof or construction appears in Part II. That leaves the paper in an awkward position: it makes broad classification and comparison claims in Part I, yet many of the building blocks needed to verify those claims are not actually available inside this manuscript. For a top-tier theory paper, that weakens both completeness and refereeability. The revision should either restate the key Part II facts as formal propositions in Part I, with short proofs or derivations, or narrow the claims in Part I so they do not outrun what is established on the page.

**Only the two-dimensional case is worked through**

The paper gives a detailed walkthrough for the four-state two-dimensional Ungerboeck code, but the main contribution is the claimed unification of higher-dimensional trellis codes through lattice partitions. Once the discussion moves to $D_4$, $E_8$, $H_{16}$, and the Wei and Calderbank-Sloane families, the reader mostly gets tables and summary formulas rather than a full derivation from the general framework. That leaves a gap in intuition and verification, because the interesting part of the paper is not that $Z^2/2Z^2$ fits the framework, but that the same machinery is supposed to organize the multidimensional cases. A complete version should work through one genuinely higher-dimensional example from start to finish. A natural choice is the eight-state GCS code on $Z^4/2Z^4$ or the 16-state Wei code on $Z^4/RD_4$: specify the partition, the labeling, the convolutional encoder, the time-zero lattice, and then derive $d_{\min}^2$, $\gamma$, $N_0$, and the quoted decoding complexity from the general lemmas.

**Section VI lacks explicit new code constructions**

Section VI is where the paper is supposed to show that the coset-code viewpoint does more than repackage the existing literature, yet the eight new classes are presented almost entirely as templates. The encoder schematics and parameter counts are suggestive, but for most classes the paper never writes down a concrete nontrivial member with an explicit circuit $T$, a specific partition, and a full branch labeling. That matters because the Section VII discussion treats these classes as evidence for broad design conclusions, not as loose existence claims. Without one spelled-out instance, it is hard to tell which classes produce genuinely realizable new codes and which just mimic the parameter profile of known examples. The revision should add at least one full representative that is not merely the old Ungerboeck four-state code in new notation. For example, the author could specify a Class VIII code on $Z^8/D_8/E_8$ or a Class V code on $H_{16}/\Lambda_{16}$, give the exact encoder outputs and coset representatives, and verify the claimed $d_{\min}^2$ and $N_0$ by direct path analysis.

**State-gain folk theorem needs bounded evidence**

The discussion section goes beyond classification and makes a real editorial claim: roughly two states buy 1.5 dB, four buy 3 dB, 16 buy 4.5 dB, and 256 buy 6 dB if one insists on a small error coefficient. That is an interesting claim, but the paper does not show that it is more than a pattern in a curated list of constructions. There is no bounded converse, and there is no exhaustive search in any natural family that would show the nearby gaps are real. This matters because the benchmark status of the Ungerboeck and Wei codes is one of the paper's headline takeaways. A convincing version needs at least one domain where the search is demonstrably broad enough to support the conclusion. One sensible addition would be an exhaustive search over all noncatastrophic rate-1/2 and rate-2/3 encoders up to 16 or 64 states for partitions such as $Z^2/4Z^2$, $Z^4/2Z^4$, and $Z^8/E_8$, or else a bound showing that no code in a specified depth-$\le 4$ binary-partition family can exceed the quoted $d_{\min}^2$ at a given state complexity and redundancy.

**No decoder walk-through for a nontrivial code**

The paper repeatedly says that coset codes can be compared by coding gain, decoding complexity, and constellation expansion, but it never gives an end-to-end decoding example outside the simplest two-dimensional setting. The complexity tables tell the reader how many operations the Part II decoder uses, yet they do not show what the actual branch-metric computation looks like for a higher-dimensional partition such as $D_4/RD_4$, $Z^8/E_8$, or $E_8/RE_8$. That missing step matters because implementability is one of the paper's selling points, and in these codes the hard part is often the nearest-coset stage rather than the Viterbi recursion itself. A reader can accept the abstract formulas and still not know how to decode one of the new constructions. The revision should therefore include one full decoder walkthrough for a representative multidimensional code. A good choice would be the 16-state Wei code based on $Z^4/RD_4$ or the eight-state $E_8/RE_8$ code: show how a received vector is mapped to the closest point in each coset, how those metrics feed the trellis decoder, and how the quoted operation count is assembled.

**Recommendation**: major revision. The unifying coset-code viewpoint is interesting and likely worth publishing, but the paper's central claims about classification scope, trellis-code geometry, and performance-versus-complexity are not yet established with the precision the paper itself promises. A revision that tightens the scope, proves the trellis invariants, and clearly separates theorem-level results from heuristic comparisons would materially strengthen the manuscript.

**Key revision targets**:

1. State and prove the exact scope of the classification, or rewrite the Abstract, Sections I and VII, and Section VI so they describe a unifying framework plus selected families rather than an exhaustive geometrical classification.
2. Turn Section IV-B into a formal theorem establishing when the fundamental volume V(C) is well defined for a trellis code and when the identities V(C) = 2^{-k}V(Λ') = 2^rV(Λ) and γ(C) = 2^{-ρ(C)} d_min^2(C) are valid.
3. Provide explicit regular labelings and distance-invariance proofs for every partition family used in Tables III and XI, including the special constructions invoked in Section VI, or restrict the tables to cases where those properties are proved.
4. Rework Section VII so any claim based on effective coding gain or decoder complexity is either supported by a formal published analysis or clearly labeled as heuristic engineering judgment.
5. Import the indispensable structural results from Part II into Part I, at least in proposition form, so the main tables and comparison claims can be checked from this paper alone.

**Status**: [Pending]

---

## Detailed Comments (11)

### 1. Dual Formula Fails As Stated

**Status**: [Pending]

**Quote**:
> If $\Lambda$ is a decomposable $N$-dimensional complex binary lattice of depth $\mu$, with code formula
>
> $$
> \Lambda = \phi^ {\mu} \boldsymbol {G} ^ {N} + \phi^ {\mu - 1} C _ {\mu - 1} + \dots + C _ {0},
> $$
>
> then its dual lattice $\Lambda^{\perp}$ is a decomposable complex binary lattice of depth $\mu$, with code formula
>
> $$
> \Lambda^ {\perp} = \phi^ {\mu} \boldsymbol {G} ^ {N} + \phi^ {\mu - 1} C _ {0} ^ {\perp} + \dots + C _ {\mu - 1} ^ {\perp}
> $$

**Feedback**:
This does not hold as stated. A concrete counterexample is $\mu=3$, $N=2$, and $C_0=C_1=C_2=\{(0,0),(1,1)\}$. Then $\Lambda=\phi^3 G^2+\phi^2C+\phi C+C$ is the set of pairs with $x_1-x_2\in \phi^3G$, whereas orthogonality modulo $\phi^3$ gives $\Lambda^{\perp}=\{(y_1,y_2):y_1+y_2\in \phi^3G\}$. Those are different lattices: for instance, $(1,1)$ lies in the displayed formula but not in the actual dual because $2\notin \phi^3G$. The dual-code rule needs either a missing sign or conjugation convention, or a narrower hypothesis.

---

### 2. Depth Replaces Redundancy In The Gain Formula

**Status**: [Pending]

**Quote**:
> This last expression is the simplest and shows that we need to know only the minimum squared distance $d_{\min}^2(\mathbb{C})$ and the normalized redundancy $\mu(\mathbb{C})$ to compute the fundamental coding gain $\gamma(\mathbb{C}) = 2^{-\mu(\mathbb{C})}d_{\min}^2(\mathbb{C})$, where the normalized redundancy is simply the sum of the normalized redundancies of the code $C$ and the lattice $\Lambda$.

**Feedback**:
The equations immediately above give $\gamma(\mathbb{C})=2^{-\rho(\mathbb{C})}d_{\min}^2(\mathbb{C})$, with total normalized redundancy $\rho(\mathbb{C})=\rho(C)+\rho(\Lambda)$. Replacing $\rho$ by depth $\mu$ changes the value. Take $\Lambda=G$, $\Lambda'=\phi G$, and a one-state rate-1 encoder: then $V(\mathbb{C})=1$ and $d_{\min}^2(\mathbb{C})=1$, so $\gamma(\mathbb{C})=1$, while the quoted formula gives $2^{-1}$. This sentence should use $\rho(\mathbb{C})$, not $\mu(\mathbb{C})$.

---

### 3. Coset Selection Needs A Power-Of-Two Quotient

**Status**: [Pending]

**Quote**:
> when  $\Lambda$  and  $\Lambda'$  are binary lattices, the order of the partition is a power of 2, say  $2^{k + r}$

**Feedback**:
The last sentence is only justified when $|\Lambda/\Lambda'|=2^{k+r}$. That is true for the binary-lattice cases treated in the paper, but not for a general lattice partition. A simple counterexample is $\Lambda=\mathbb{Z}^2$ and $\Lambda'=3\mathbb{Z}\times \mathbb{Z}$, where the quotient has three cosets, so a binary output word cannot index them one-to-one. The fix is to state the power-of-two assumption here, or to say more generally that a coset code uses an encoder together with a labeling, with the paper then specializing to binary partitions and binary encoders.

---

### 4. The Radius Scaling Has The Wrong Sign

**Status**: [Pending]

**Quote**:
> The volume of the sphere must then be about $2^n V(\Lambda)$ for large $n$. For the integer lattice $Z^N$, the volume of such a sphere must be about $2^n$. The ratio of the radii of the two spheres is thus about $V(\Lambda)^{-1/N}$ (this dimensional argument in fact holds for constellation boundaries of any shape).

**Feedback**:
The exponent sign is reversed. If $c_N r_{\Lambda}^N\approx 2^nV(\Lambda)$ and $c_N r_Z^N\approx 2^n$, then $(r_{\Lambda}/r_Z)^N\approx V(\Lambda)$, so $r_{\Lambda}/r_Z\approx V(\Lambda)^{1/N}$. The next sentence about power gain already matches that corrected scaling, so this looks like a local algebra slip rather than a deeper problem.

---

### 5. Redundancy Is Defined Against The Wrong Ambient Lattice

**Status**: [Pending]

**Quote**:
> The redundancy $r(\Lambda)$ of a binary lattice $\Lambda$ is defined as the binary logarithm of $|Z^{N} / \Lambda|$, so that $|Z^{N} / \Lambda| = 2^{r(\Lambda)}$.

**Feedback**:
This definition works for real lattices, but the same subsection immediately uses $r(\Lambda)$ for complex lattices and quotients of $G^N$. For a genuinely complex lattice such as $\Lambda=G$, $|Z^N/\Lambda|$ is not the ambient quotient at all. The definition should split the two settings: $r(\Lambda)=\log_2[Z^N:\Lambda]$ in the real case, and $r(\Lambda)=\log_2[G^N:\Lambda]$ in the complex case, or else refer explicitly to the corresponding real lattice throughout.

---

### 6. Lemma 2 Misidentifies The Quotient

**Status**: [Pending]

**Quote**:
> Thus the $2^{K}$ binary linear combinations $\{\sum a_{k}\mathbf{g}_{k}\}$ of the generators $\mathbf{g}_{k}$ are a system of coset representatives $[\Lambda_{k} / \Lambda_{k + 1}]$ for the partition $\Lambda_{k} / \Lambda_{k + 1}$

**Feedback**:
This cannot be right as written. Each partition $\Lambda_k/\Lambda_{k+1}$ is two-way, so it has two cosets, not $2^K$. The construction produces $2^K$ representatives for the full quotient $\Lambda/\Lambda'$. Changing the displayed quotient to $\Lambda/\Lambda'$ would make the count line up with the argument.

---

### 7. The Convolutional-Code Scalar Field Is Stated Too Strongly

**Status**: [Pending]

**Quote**:
> It follows that a convolutional code is a vector space over
>
> the field of binary formal power series $f(D), f_{i} \in \{0,1\}$; the dimension of this vector space is $k$, and any codeword $a(D)$ can be written as $a(D) = \sum_{j} f_{j}(D) g_{j}(D)$

**Feedback**:
Two distinct issues are compressed here. Because sequences may start at a negative time, the natural ambient object is a Laurent series, not an ordinary formal power series. And $\mathbb{F}_2[[D]]$ is a ring, not a field. As written, the algebraic statement should be a module over the binary power-series ring unless the paper wants a larger field and states the needed closure assumptions explicitly.

---

### 8. The Coding-Gain Interpretation Uses The Wrong Reference Lattice

**Status**: [Pending]

**Quote**:
> \Lambda)$. For all of these lattices, the minimum squared distance $d_{\mathrm{min}}^2(\Lambda)$ is equal to $2^\mu$; it follows that the fundamental coding gain is given by $\gamma(\Lambda) = 2^{\mu - \rho} = 2^\kappa$. (This expression for the fundamental coding gain has the following interpretation: both $\Lambda$ and $\phi^n G^N$ have the same minimum squared distance $2^\mu$, but $\Lambda$ is the union of $2^{k(\Lambda)}$ cosets of $\phi^n G^N$ and is therefore $2^{k(\Lambda)}$ times as dense as $\phi^n G^N$ in $2N$-space.

**Feedback**:
The reference lattice should be $\phi^{\mu}G^N$, not $\phi^nG^N$. For a principal sublattice $\Lambda(r,n)$ the depth is $\mu=n-r$, so $d_{\min}^2(\phi^{\mu}G^N)=2^{\mu}$. Using $\phi^nG^N$ only works in the Barnes-Wall case $r=0$. The interpretation is fine once that exponent is corrected.

---

### 9. The Density Relation Is Reversed

**Status**: [Pending]

**Quote**:
> The partitions that we will use are generally those with $\Lambda'$ at least as dense as $\Lambda$, depths no greater than four, and orders no greater than $2^{12}$.

**Feedback**:
For a partition $\Lambda/\Lambda'$, Lemma 1 gives $V(\Lambda')=|\Lambda/\Lambda'|V(\Lambda)$. So whenever the index exceeds one, the sublattice $\Lambda'$ is less dense, not more dense. The sentence should say that $\Lambda'$ is no denser than $\Lambda$, or simply speak in terms of larger fundamental volume rather than density.

---

### 10. One Comparison Identity Substitutes The Wrong Distance

**Status**: [Pending]

**Quote**:
> prime})$ (if any). Relative to $\gamma (\Lambda) = 2^{-\rho (\Lambda)}d_{\min}^{2}(\Lambda^{\prime})$, the gain $\gamma (\mathbb{C})$ is greater by the distance gain factor of $d_{\min}^{2}(\mathbb{C}) / d_{\min}^{2}(\Lambda)$, offset by a power loss of $2^{-\rho (C)}$ due to constellation

**Feedback**:
The coding gain of $\Lambda$ is $2^{-\rho(\Lambda)}d_{\min}^2(\Lambda)$, not $2^{-\rho(\Lambda)}d_{\min}^2(\Lambda')$. The surrounding algebra already uses the correct ratio $d_{\min}^2(\mathbb{C})/d_{\min}^2(\Lambda)$. Leaving $d_{\min}^2(\Lambda')$ in this sentence breaks the identity unless $\Lambda$ and $\Lambda'$ happen to have the same minimum distance.

---

### 11. Lemma 6 Needs A Hypothesis On The Superlattice

**Status**: [Pending]

**Quote**:
> ulo $\Lambda'$).
>
> **Lemma 6**: If $\Lambda'$ is a mod-2 lattice, $C$ is a $2^r$-state, rate-$k / (k + r)$ convolutional code and the labeling map $c(a)$ is linear modulo $\Lambda'$, then a trellis code $\mathbb{C}(\Lambda / \Lambda'; C)$ is the set of all sequences of integer $N$-tuples that are congruent modulo 2 to one of the words in a $2^r$-state rate- $[N - r(\mathbb{C})] / N$ convolutional code $C'$. The redundancy

**Feedback**:
The conclusion is too broad unless $\Lambda$ is also assumed to be a mod-2 lattice. One can take $\Lambda'=D_2$ and let $\Lambda$ be the lattice obtained by adjoining the coset $(1/2,1/2)+D_2$; the labeling is linear modulo $\Lambda'$, but the resulting trellis symbols are not integer tuples. The proof itself invokes the reduction to a partition of $Z^N/2Z^N$, and that step needs both lattices to lie in the binary mod-2 setting.

---
