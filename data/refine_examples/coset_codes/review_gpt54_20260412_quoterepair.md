# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 04/12/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper has a strong unifying idea: viewing lattice and trellis constructions through lattice partitions and cosets. The main weakness is that the paper presents this as a geometrical classification, but many of the classification, equivalence, and performance-ranking claims are only argued informally, deferred to Part II, or supported by examples and tables rather than theorem-level statements.

The paper does succeed in giving readers a common language for Ungerboeck, Wei, Calderbank-Sloane, and lattice-based constructions, and that perspective is genuinely useful. The tables and worked examples make the framework concrete. What is missing is the level of rigor needed to justify the title's stronger claim of a geometrical classification rather than an organized survey with some new constructions.

**The paper does not prove that the proposed classification is exhaustive or structurally complete**

The title and abstract promise a "geometrical classification," and Section VI goes so far as to introduce Classes I-VIII as if they cover the relevant design space. But the paper never states a theorem identifying the exact scope of the classification or proving necessary and sufficient conditions for a coset code to belong to one of these classes. Section VI instead restricts attention to constructions built from a small menu of partition ratios, code rates, and memory patterns, then treats the resulting list as a broad taxonomy. That is a useful design catalog, but it is not the same as a classification in the mathematical sense. This matters because several of the paper's headline claims, especially in Sections VI-VII, rely on the reader accepting that the code families under comparison are the right families to compare. The revision should either narrow the claim and present the paper as a unifying framework plus illustrative families, or add a theorem that states the scope precisely and proves that the taxonomy is exhaustive within that scope.

**Equivalence and distinctness of code classes are left informal, so the taxonomy risks relabeling the same constructions**

A recurring theme in Sections IV-VI is that many codes are "equivalent" to one another under reinterpretation of the partition, augmentation of the encoder, or use of a different lattice description. Lemma 5 is the main formal tool for this, yet the paper never gives a clear equivalence relation for when two coset codes should count as the same object for classification purposes. As a result, the eight classes in Section VI do not read as eight demonstrably distinct classes; some are explicit duplicates in small parameter settings, and several known codes reappear in multiple guises. The paper itself notes overlaps, for example Class I versus Class V for small k, Class II versus Class VI in certain cases, and many depth-2 constructions being equivalent to GCS-type codes by Lemma 6. Without invariants that distinguish classes, the taxonomy can overstate novelty by turning representation changes into new categories. A stronger version would define equivalence formally, identify invariants preserved under that equivalence, and then state which classes are genuinely distinct and which are merely different realizations of the same underlying code family.

**Core structural claims depend too heavily on Part II and on sketches rather than full arguments**

The paper repeatedly says it can be read independently, but several of its main claims are deferred to Part II or only sketched in Part I. Examples include Lemma 2 in Section II-F, the decoding-complexity claims summarized in Tables II and III, the partition-distance statements used in Section IV, and the special lattice facts needed for classes such as the Section VI discussion of the alternative partition \(E_8/R^*E_8/2E_8\). Section VII then draws broad conclusions about coding gain, error coefficient, and complexity from those deferred ingredients. For an introductory survey this would be acceptable, but for a paper claiming a systematic classification it leaves too much of the logical load outside the present manuscript. The dependence on unpublished sources and private communications in Sections V and the tables makes this problem sharper, because some comparative claims cannot be checked from the paper itself. The fix is straightforward: either move the strongest classification and comparison claims to a combined treatment with Part II, or restate here the exact propositions from Part II that are needed and give enough proof detail that the reader can verify the framework without chasing external documents.

**Several formulas in the core parameter section are misstated, which weakens confidence in the later comparisons**

Section IV-B is supposed to be the clean summary of the geometric quantities that drive the whole paper, but there are at least two algebraic slips in that section. First, after defining the time-zero lattice, the text writes \(V(\mathbb{C}) = V(\Lambda_0) = 2^{-k(C)}V(\Lambda') = 2^{k+r}V(\Lambda') = 2^{r(C)}V(\Lambda)\); the middle equality is incompatible with the preceding sentence and with the intended volume interpretation. Second, in the paragraph after Lemma 5, the paper says "Relative to \(\gamma(\Lambda)=2^{-\rho(\Lambda)}d_{\min}^2(\Lambda')\)," but the lattice coding-gain formula in Section II-C depends on \(d_{\min}^2(\Lambda)\), not \(d_{\min}^2(\Lambda')\). These are not cosmetic typos, because Section IV-B is exactly where the paper ties lattice parameters, code redundancy, and coding gain together. When the foundational formulas are unstable, the comparative tables and the "folk theorem" in Section VII become harder to trust. The revision should carefully audit every formula in Sections II, IV, and the tables, and then propagate any corrections through the performance comparisons.

**The treatment of labelings is not strong enough for a paper whose constructions depend on them**

The paper rightly emphasizes in Section II-F that a partition \(\Lambda/\Lambda'\) has many possible systems of coset representatives, and later in Section IV-C it relies on regularity and distance-invariance properties of the chosen labeling. Yet the paper mostly proves existence of an Ungerboeck labeling and then moves quickly to examples, without giving a general criterion for when a labeling preserves the relevant distance structure or when two labelings should be regarded as equivalent. This is not a side issue: the minimum-distance arguments for trellis codes often depend as much on the labeling as on the partition itself. The paper even uses special-purpose assertions, such as the Section VI claim about a partition \(E_8/R^*E_8/2E_8\) with a specially compatible system of representatives, without turning them into a general construction principle. Readers are left to infer that the right labelings exist whenever needed. A stronger manuscript would give a theorem or algorithmic criterion for regularity, spell out when the Ungerboeck distance bound is tight, and state clearly which classification statements are invariant to the choice of labeling and which are not.

**The paper blurs exact geometric classification with heuristic performance ranking**

Up through Sections II-IV the framework is geometric and mostly exact: minimum distance, redundancy, depth, and partition order are the main objects. But Sections V-VII shift from exact structure to a ranking of code families using a hand-tuned effective coding gain based on the rule of thumb that each doubling of the error coefficient costs about 0.2 dB, together with decoding-complexity counts tied to the specific trellis algorithms of Part II. Section VII then states broad conclusions, including the "folk theorem" on the number of states needed to reach 1.5, 3, 4.5, 5.25, and 6 dB, as if these were general consequences of the classification. They are not. They are empirical summaries of a restricted set of constructions under a particular error approximation and a particular implementation model. This matters for framing: the conceptual contribution is the coset-code viewpoint, while the comparative ranking is much more contingent than the paper suggests. The revision should separate exact theorem-level results from heuristic design advice, and it should state the conclusions in Section VII as provisional observations about the surveyed code families rather than as near-laws of the field.

**No explicit new code constructed end to end**

The paper says the coset-code viewpoint does more than reorganize known schemes: it is supposed to suggest many extensions, and Section VI introduces eight generic classes partly on that basis. What is missing is one fully specified code that appears to be genuinely new in this framework, not just a table entry with claimed parameters. Without that, readers cannot tell whether the classification has real design bite or mainly renames existing constructions. This matters for publishability because the paper asks the reader to accept a broad unifying principle as a source of new codes, yet never walks through a nontrivial construction produced by that principle. A good fix would be to take one candidate from Table XI that is not already standard in the literature, for example a Class VI code on the partition $D_{16}/H_{16}$ or a Class VIII code on $D_8^{\perp}/RE_8$, and give the actual convolutional generator, the labeling, the trellis interpretation, and a complete derivation of $d_{\min}^2$, $\gamma$, $\tilde N_0$, and decoding complexity.

**Generic classes lack a worked multidimensional example**

The paper develops general formulas for coset codes and then lists many families, but it never carries one of the higher-dimensional constructions from start to finish in enough detail for a reader to internalize the machinery. The two-dimensional Ungerboeck example is useful, yet it is too simple to illustrate the features that drive the claimed unification of Wei and Calderbank-Sloane type schemes. Readers need one concrete multidimensional special case where the lattice partition, labeling, convolutional code, and resulting distance calculation are all written out, rather than inferred from tables. This gap matters because the main contribution is a geometric classification, and classifications in this area are judged partly by whether they make hard examples easier to compute. The natural addition is a full worked derivation for a standard benchmark such as $\mathcal C(Z^8/E_8;C)$ or $\mathcal C(E_8/RE_8;C)$: specify the partition order, an explicit labeling, the encoder outputs, the time-zero lattice, and then verify how the claimed $d_{\min}^2$ and coding gain follow.

**No general recipe for computing performance parameters**

The abstract promises that coding gain, error coefficient, decoding complexity, and constellation expansion are geometric parameters determined by $C$ and $\Lambda/\Lambda'$. In the paper itself, coding gain and redundancy are usually computable from the setup, but $N_0$ and especially decoding complexity are mostly supplied in tables or borrowed from earlier searches and Part II. What is missing is a reusable procedure that tells a reader how to obtain these quantities for a new coset code once the partition and encoder are chosen. That omission matters because the paper frames the geometry as a practical comparison tool; a framework that cannot be executed on a new example is still incomplete. The revision should add an explicit calculation template, ideally on a representative partition such as $Z^8/E_8$ or $E_8/RE_8$: show how to enumerate nearest-neighbor events in the trellis to get $N_0$, and show how the partition decoder complexity from Table III combines with Viterbi branch metrics to produce the quoted $N_D$.

**Recovery of benchmark families is not shown constructively**

The paper repeatedly says that the framework embraces all the good known codes, but the recovery of those benchmark families is mostly descriptive. Sections V and VI catalog Ungerboeck, Wei, and Calderbank-Sloane codes inside the coset notation, yet there is no single constructive proposition showing how the classical design rules arise from the lattice-coset formulation and when the old and new descriptions are exactly equivalent. That leaves a gap between the introduction's promise of unification and what is actually delivered on the page. For a classification paper, this matters because one wants to see that the new language is not just compatible with prior work, but reproduces it in a way that is checkable and useful. A strong addition would be a theorem or extended worked section taking two standard cases, say Ungerboeck's four-state $Z^2/2Z^2$ code and Wei's $Z^8/E_8$ family, and deriving them directly from the general object $\mathcal C(\Lambda/\Lambda';C)$ with the same distance formula, redundancy, and state complexity as in the original presentations.

**Recommendation**: major revision. The paper's unifying viewpoint is valuable, and many of the constructions are interesting, but the current manuscript does not yet justify its stronger claims about classification, distinctness of classes, and comparative conclusions. A revision could make this publishable by tightening the scope, repairing the core formulas, and turning the informal taxonomy into something readers can verify rigorously.

**Key revision targets**:

1. State the exact scope of the claimed classification and prove either exhaustiveness within that scope or, if that is not possible, rename the contribution as a unifying framework plus representative families rather than a full classification.
2. Define a formal equivalence relation for coset codes and use it to show which of Classes I-VIII are genuinely distinct classes and which are equivalent reformulations of the same constructions.
3. Audit and correct the parameter formulas in Sections II and IV, especially the volume and coding-gain identities, and check that Tables II-XI remain consistent after those corrections.
4. Bring into Part I the precise statements and proof ingredients now deferred to Part II that are necessary for the classification and comparison claims, including the distance and decoding-complexity results used later in the paper.
5. Provide a theorem or explicit criterion for when a labeling is regular or distance-preserving, and identify which results are invariant to labeling choice versus which require special labelings.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Finite base-φ expansion is not valid as stated

**Status**: [Pending]

**Quote**:
> In analogy to the chain $Z / 2Z / 4Z / \dots$, this chain suggests a complex binary representation of a Gaussian integer $g$:
>
> $$
> g = a _ {0} + \phi a _ {1} + \phi^ {2} a _ {2} + \dots
> $$
>
> where $a_0, a_1, a_2, \dots \in \{0,1\}$

**Feedback**:
This positional expansion does not hold for every Gaussian integer with digits restricted to $\{0,1\}$. A concrete counterexample is $g=i$: modulo $\phi$, one has $i\equiv 1$, and then $(i-1)/\phi=i$, so the same remainder repeats and the expansion does not terminate. The quotient chain supports a $\phi$-adic decomposition, but not a finite base-$\phi$ representation of every element of $G$ with digits $\{0,1\}$. The text should be narrowed to an infinite $\phi$-adic decomposition, or the digit set and representation claim should be changed.

---

### 2. Barnes-Wall self-duality sentence is misstated

**Status**: [Pending]

**Quote**:
> Thus $\Lambda(n,n)^{\perp} = G^{N} \simeq Z^{2N}$, $\Lambda(0,n)^{\perp} = \Lambda(n)$, and $\Lambda(n-1,n)^{\perp}, n \geq 1$, is the dual $D_N^{\perp}$ of the checkerboard lattice $D_N$

**Feedback**:
The middle identity conflicts with the displayed dual formula and with the earlier statement that $\Lambda(0,n)$ is self-dual. Setting $r=0$ in the formula for $\Lambda(r,n)^\perp$ reproduces the original code formula of $\Lambda(0,n)$ term by term. This should read $\Lambda(0,n)^\perp=\Lambda(0,n)$, not $\Lambda(n)$.

---

### 3. One Table III partition row is inconsistent with the paper's own counting rules

**Status**: [Pending]

**Quote**:
> |  D8 | RE8 | 8 | 32 | 3 | 1 | 3/4 | 2 | 8 | 88 | 2.75  |
> |  D8 | RE8 | 8 | 128 | 3 | 1 | 1/4 | 2 | 8 | 280 | 2.2  |

**Feedback**:
The first of these two rows cannot be right. Earlier tables give $r(D_8)=1$ and $r(E_8)=4$; applying $R$ in eight real dimensions adds 4 to the redundancy, so $r(RE_8)=8$. Then $|D_8/RE_8|=2^{8-1}=128$, not 32. The partition-level redundancy should also be $\rho(\Lambda)=\rho(D_8)=1/4$, not $3/4$. The 32-way row should be removed or corrected, because it does not match the paper's own volume and index formulas.

---

### 4. Trellis state count uses the wrong parameter

**Status**: [Pending]

**Quote**:
> A trellis diagram for a $2^{r}$-state, rate-$k / (k + r)$ convolutional code is an extended state transition diagram for the encoder that generates $C$. For each time $t$, it has $2^{\nu}$ nodes, or states, representing the possible states at time $t$.

**Feedback**:
The state count is determined by the constraint length $\nu$, not by the redundancy parameter $r$. The preceding paragraph says explicitly that an encoder with $\nu$ memory elements has $2^{\nu}$ states, so the phrase "$2^r$-state" does not fit the derivation that follows. The sentence should say "$2^{\nu}$-state."

---

### 5. The general group construction needs normality, not just a subgroup

**Status**: [Pending]

**Quote**:
> More generally, a coset code $\mathbb{C}(S / T;C)$ can be defined whenever $S$ is some set of discrete elements that forms an algebraic group, with some distance measure between elements of $S$, $T$ is a subgroup of $S$ such that the quotient group $S / T$ has finite order $|S / T|$

**Feedback**:
This is correct for the abelian examples used later, but it is too broad as a general statement. A subgroup gives a partition into cosets, but $S/T$ is a quotient group only when $T$ is normal. For example, in $S_3$ with $T=\{e,(12)\}$, the cosets exist but the product of cosets is not well defined. The statement should either require $T$ to be normal or avoid calling $S/T$ a quotient group in the non-normal case.

---

### 6. The modulus examples need a positivity assumption on $m$

**Status**: [Pending]

**Quote**:
> As another example, if $m$ is any integer, the lattice $mZ$ of integer multiples of $m$ is a sublattice of $Z$. The partition $Z / mZ$ is the partition of the integers into $m$ equivalence classes modulo $mZ$ (modulo $m$), and the order of the partition is $m$.

**Feedback**:
The Euclidean-division argument used here works only for positive $m$. If $m=-2$, then $mZ=2Z$ and the quotient has 2 classes, not $-2$; if $m=0$, then $0Z=\{0\}$ and $Z/0Z$ is infinite. The same issue carries into the later $mZ^N$ example. The text should say "if $m$ is a positive integer" wherever the quotient size and remainder representatives are used.

---

### 7. The binary expansion claim is too broad for $\mathbb Z$

**Status**: [Pending]

**Quote**:
> For example, the chain $Z / 2Z / 4Z / \cdots$ leads to the standard binary representation of an integer $m$:
>
> $$
> m = a_0 + 2a_1 + 4a_2 + \cdots
> $$
>
> where $a_0, a_1, a_2, \dots \in \{0,1\}$

**Feedback**:
As written, this treats every integer as an infinite sum of nonnegative powers of 2 with digits in $\{0,1\}$. That is not true in the ordinary integers: negative integers are excluded, and an actually infinite sum does not converge in $\mathbb Z$. What the argument does justify is the usual finite binary expansion for each nonnegative integer. Narrowing the claim that way would fix the point.

---

### 8. The $\phi$-depth discussion drops the $G$-lattice hypothesis

**Status**: [Pending]

**Quote**:
> If $\Lambda$ is a $2N$-dimensional real binary lattice, then the corresponding $N$-dimensional complex lattice is also a complex binary lattice (if it is a $G$-lattice), and vice versa, since $2^{m}Z^{2N} \simeq \phi^{2m}G^{N} \subset \phi^{2m-1}G^{N}$. So we may speak of the $\phi$-depth of a real $2N$-dimensional binary lattice. A real $2N$-dimensional binary lattice with 2-depth $m$ has $\phi$-depth $2m$ or $2m-1$

**Feedback**:
The parenthetical condition matters, but it disappears in the next sentence. Not every real binary lattice is a $G$-lattice under the chosen complex identification. For instance, $\mathbb Z\times 2\mathbb Z$ is binary of 2-depth 1, but it is not closed under multiplication by $i$, so the paper's complex-depth language does not apply to it. The conclusion should be restricted to real binary lattices that are also $G$-lattices.

---

### 9. Lemma 2 identifies the wrong quotient for the full set of representatives

**Status**: [Pending]

**Quote**:
> Thus the $2^{K}$ binary linear combinations $\{\sum a_{k}\mathbf{g}_{k}\}$ of the generators $\mathbf{g}_{k}$ are a system of coset representatives $[\Lambda_{k} / \Lambda_{k + 1}]$ for the partition $\Lambda_{k} / \Lambda_{k + 1}$

**Feedback**:
This cannot be right as written. Each quotient $\Lambda_k/\Lambda_{k+1}$ is two-way, so it has only 2 cosets, not $2^K$. The $2^K$ sums are the representatives for the full partition $\Lambda/\Lambda'$. The sentence should be corrected accordingly, because the current indexing makes the conclusion impossible once $K>1$.

---

### 10. The proof of Lemma 4 skips the actual addition argument

**Status**: [Pending]

**Quote**:
> To show that $\Lambda$ is a $G$-lattice, we must show that if $\lambda_1, \lambda_2 \in \Lambda$, then $\lambda_1 + \lambda_2 \in \Lambda$, and also if $\lambda \in \Lambda$, then $-\lambda \in \Lambda$ and $i\lambda \in \Lambda$. The first two propositions follow immediately from $2\lambda \equiv \mathbf{0} \bmod \phi^2$.

**Feedback**:
The negation step is immediate, but closure under addition is not. One needs to compute that if $\lambda_t\equiv \phi c_1^{(t)}+c_0^{(t)} \pmod{\phi^2}$ for $t=1,2$, then $\lambda_1+\lambda_2\equiv \phi(c_1^{(1)}\oplus c_1^{(2)})+(c_0^{(1)}\oplus c_0^{(2)}) \pmod{\phi^2}$, using $2\equiv 0 \pmod{\phi^2}$. Then linearity of $C_1$ and $C_0$ gives closure. This is a short fix, but the present proof jumps over the key step.

---

### 11. The checkerboard lattice is indexed by the wrong real dimension

**Status**: [Pending]

**Quote**:
> The lattice $\Lambda(n - 1, n)$, $n \geq 1$, is the "checkerboard lattice" $D_N$, with code formula $D_N = \phi \pmb{G}^N + \mathrm{RM}(n - 1, n) = \phi \pmb{G}^N + (N, N - 1, 2)$

**Feedback**:
This disagrees with the paper's own examples. When $n=1$, the displayed formula gives $\phi G^2+(2,1,2)$, which the text elsewhere identifies as $D_4$, not $D_2$. Since $G^N$ has real dimension $2N$, the lattice here is $D_{2N}$. The indexing should be corrected to match the construction and Table I.

---

### 12. One Table I row has the wrong complex dimension

**Status**: [Pending]

**Quote**:
> |  (1,3) | H_{16} | 16 | 2 | 2Z^{16} + (16,11,4) | φ^{2}G^{4} + φ(8,7,2) + (8,4,4)  |

**Feedback**:
This complex code formula is inconsistent with the general definition just above. For $(r,n)=(1,3)$, one has $N=2^n=8$, so the leading term should be $\phi^2G^8$, not $\phi^2G^4$. As printed, the row mixes an 8-dimensional real ambient term with 16-dimensional real code parameters. The table entry should be corrected.

---

### 13. The density relation for sublattices is reversed

**Status**: [Pending]

**Quote**:
> The partitions that we will use are generally those with $\Lambda'$ at least as dense as $\Lambda$, depths no greater than four, and orders no greater than $2^{12}$.

**Feedback**:
For a partition $\Lambda/\Lambda'$, the denominator is a sublattice of the numerator. By Lemma 1, that means $V(\Lambda')=|\Lambda/\Lambda'|V(\Lambda)$, so $\Lambda'$ is less dense, not more dense, than $\Lambda$. This sentence reverses the inclusion-density relation used throughout the paper and should be fixed.

---

### 14. The branch-count formula in the decoding discussion is wrong

**Status**: [Pending]

**Quote**:
> For each unit of time, for each of the $2^{e}$ states, the Viterbi algorithm requires $2^k$ additions and a comparison of $2^k$ numbers, or $2^{k} - 1$ binary comparisons, so that its complexity is $\beta 2^{k + r}$, where $\beta = 2 - 2^{-k}$, and $2^{k + r}$ is the number of branches per stage of the trellis

**Feedback**:
The count should be states times outgoing branches per state, namely $2^e\cdot 2^k=2^{e+k}$. Using $2^{k+r}$ here is not compatible with the notation in the same paragraph, where $e$ indexes the number of states and $r$ is redundancy. The current expression would make the Viterbi term almost independent of the trellis size in Table IV, which is clearly not intended. This should be corrected to $\beta 2^{e+k}$.

---

### 15. The rotation description should mention the orientation reversal

**Status**: [Pending]

**Quote**:
> $R\mathbb{Z}^2$ is a version of $\mathbb{Z}^2$ obtained by rotating $\mathbb{Z}^2$ by $45^\circ$ and scaling by $2^{1/2}$

**Feedback**:
This is slightly imprecise. The normalized matrix $R/\sqrt{2}$ is orthogonal, but it has determinant $-1$, so it is not a pure rotation. Geometrically, it is a $45^\circ$ rotation composed with a reflection. Since the paper later notes this point in the complex-language discussion, it would be better to phrase the description here as a scaled orthogonal transformation rather than a rotation alone.

---
