# Coset Codes—Part I: Introduction and Geometrical Classification

**Date**: 03/04/2026
**Domain**: computer_science/information_theory
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Reliance on Infinite Lattice Properties for Finite Constellations**

The paper derives fundamental coding gain and error coefficients based on infinite lattice properties, such as fundamental volume and kissing number, assuming spherical boundaries that do not hold for practical rectangular or shaped constellations. This overlooks significant shaping loss and boundary effects where points have fewer neighbors, systematically overstating power efficiency and mispredicting bit-error rates, particularly in low-dimensional or moderate-size implementations. The analysis must incorporate shaping gain factors, differentiate between inner and boundary error coefficients, or provide explicit bounds on performance loss due to finite truncation to ensure theoretical gains match achievable efficiency.

**Unverifiable Decoding Complexity Characterization**

The complexity analysis focuses on trellis decoding states while deferring the computationally intensive lattice quantization step to a companion paper, despite quantization dominating costs for high-dimensional lattices like Leech or Barnes-Wall. By presenting complexity values without algorithmic specifications or binary operation counts within this text, the claims remain unverifiable and risk classifying computationally prohibitive codes as implementable. The framework must include explicit complexity models for the lattice quantization step and sufficient algorithmic detail to allow independent validation of the performance-complexity trade-offs.

**Non-Constructive Proof for Lattice Labelings**

Lemma 2 proves the existence of Ungerboeck labelings for binary lattice partitions via induction but fails to provide a constructive method for generating the required generator matrices. This leaves the practical implementation of the encoder structure ambiguous, as existence does not guarantee structural simplicity or efficient mapping logic. To validate the claim that these are practical constructive techniques, the authors must provide constructive algorithms for labelings with explicit bounds on mapping complexity, ensuring the framework can be systematically applied to all claimed code classes.

**Inconsistency Between Claimed Generality and Binary Focus**

The abstract asserts that practically all known constructive coding techniques can be characterized as coset codes, yet the rigorous mathematical development is heavily concentrated on binary lattices with only descriptive mentions of ternary or phase-modulated extensions. Geometric parameter definitions like fundamental volume and coding gain lack equivalent rigorous formulations for non-Euclidean groups, making cross-category comparisons mathematically inconsistent. The authors should either restrict claims to lattice-type codes or define equivalent geometric metrics for non-Euclidean groups to substantiate the universality of the framework.

**Sensitivity to Channel Non-Idealities**

Geometric parameters such as minimum squared distance and error coefficient are treated as sufficient statistics for performance prediction under an ideal Additive White Gaussian Noise (AWGN) channel, ignoring phase jitter, carrier frequency offset, and nonlinearities relevant to band-limited channels. These impairments can dominate performance in real-world implementations, rendering the distance-based metrics less predictive. The paper should explicitly state the AWGN assumption as a limitation and discuss the sensitivity of the proposed geometric parameters to common channel non-idealities to clarify practical applicability.

**Reliance on Asymptotic Metrics Without Finite-System Validation**

The paper defines Fundamental Coding Gain using infinite lattice parameters (Section II.C), explicitly acknowledging the approximation holds only 'for large n'. However, the stated methodology (Outline, Section I.D) intends to categorize specific trellis codes (which are finite-dimensional and use finite constellations) using this metric as the primary performance measure. This creates a mismatch between the theoretical assumption of infinite lattice constellations and the reality of finite energy systems, where shaping losses and error coefficients cause deviations from the asymptotic gain. Consequently, the theoretical gains may not accurately predict the actual performance of the finite codes being classified, and no empirical methodology or finite-size corrections are described to validate these metrics.

**Status**: [Pending]

---

## Detailed Comments (20)

### 6. Non-Constructive Labeling Proof [CRITICAL]

**Status**: [Pending]

**Quote**:
> If # A, then a vector gk exists in A that is not in A k + l but has order 2 modA,+

**Feedback**:
Lemma 2 proves existence via induction but provides no constructive algorithm for generating generator matrices. Provide constructive algorithms with explicit bounds on mapping complexity to validate practical implementation claims.

---

### 1. Infinite Lattice Assumption for Finite Constellations

**Status**: [Pending]

**Quote**:
> suppose we form a 2^n-point N-dimensional constellation by taking all points in an N-dimensional lattice A (or a coset of A) that lie within an...

**Feedback**:
The analysis assumes infinite lattice properties apply directly to finite constellations bounded by an N-sphere. This overlooks boundary effects and shaping loss, potentially overstating power efficiency. Incorporate shaping gain factors or provide explicit bounds on performance loss due to finite truncation.

---

### 2. Fundamental Coding Gain Definition Ambiguity

**Status**: [Pending]

**Quote**:
> The fundamental coding gain of the coset code is denoted by y(C) and is defined by two elementary geometrical parameters

**Feedback**:
This definition relies on fundamental volume, which is well-defined for infinite lattices but ambiguous for finite constellations. Clarify that this metric assumes cubic shaping or infinite extent, as finite boundaries alter the effective volume and power.

---

### 4. Binary Lattice Focus vs. Claimed Generality

**Status**: [Pending]

**Quote**:
> Since these codes are based on partitions of binary lattices, we begin with an introduction to such lattices in Section II

**Feedback**:
The abstract claims generality for 'practically all known constructive coding techniques,' yet the rigorous development is restricted to binary lattices. Restrict claims to lattice-type codes or define equivalent geometric metrics for non-Euclidean groups to substantiate universality.

---

### 5. Undefined Distance Measure for General Groups

**Status**: [Pending]

**Quote**:
> p, with some distance measure between elements of S,

**Feedback**:
The generalization to arbitrary groups lacks specification of required distance properties. Define whether the metric must be Euclidean or translation-invariant to ensure the applicability of coding gain formulas to non-lattice groups.

---

### 15. Leech Lattice Indecomposability Claim

**Status**: [Pending]

**Quote**:
> ate. The Leech lattice A,, is an example of a fundamentally indecomposable mod-4 lat

**Feedback**:
This significant claim is stated without proof or reference. Provide a citation or brief justification to substantiate the Leech lattice's fundamental indecomposability.

---

### 17. Complexity Analysis Deferral

**Status**: [Pending]

**Quote**:
> ].) Section 111 summarizes those results from part I1 most relevant to this p

**Feedback**:
Critical complexity analysis is deferred to Part II without specifying which results are essential for Part I. Include explicit complexity models for the lattice quantization step here to allow validation of performance-complexity trade-offs.

---

### 19. Infinite Partition Chain Index Justification

**Status**: [Pending]

**Quote**:
> There is then an infinite chain G/+G/+2G/+3G/+4G/. . . of two-way partition

**Feedback**:
The text asserts the chain consists of two-way partitions without proving the index is always 2. Provide a brief justification that |eta^k G / eta^{k+1} G| = 2 to strengthen mathematical rigor.

---

### 20. G-Lattice Module Condition Proof

**Status**: [Pending]

**Quote**:
> It is so if and only if X E A implies iX E A;

**Feedback**:
The 'if and only if' claim regarding G-lattices is stated without proof. Demonstrate that i lambda in Lambda implies (a+bi) lambda in Lambda to validate the module condition over Gaussian integers.

---

### 3. Total Coding Gain Approximation Limits [MINOR]

**Status**: [Pending]

**Quote**:
> is approximately equal to the ratio of the normalized second moment [7] of an N-cube to that of the region of N-space in which the constellation is contained).

**Feedback**:
This approximation holds for large constellations where boundary effects are negligible. For small dimensions or aggressive shaping, specify the limits of this approximation to prevent performance prediction errors.

---

### 7. Rotation Operator Matrix Definition [MINOR]

**Status**: [Pending]

**Quote**:
> The most important scaled orthogonal transformation for our purposes is the rotation operator R, defined by the 2 x 2

**Feedback**:
The matrix provided is not a pure rotation matrix (determinant is -2, not 1). Describing it as a 'rotation operator' is mathematically inaccurate; correct the terminology to 'scaled orthogonal transformation' or adjust the matrix.

---

### 8. Rotation Operator Scaling Claim [MINOR]

**Status**: [Pending]

**Quote**:
> 2 (the rotation operator R always doubles norms, in any number of dimension

**Feedback**:
The claim that R 'always doubles norms, in any number of dimensions' requires clarification on how R is extended to higher dimensions. Rigorously define the N-dimensional extension to support this general property.

---

### 9. D4 Coding Gain Calculation Garbling [MINOR]

**Status**: [Pending]

**Quote**:
> us 0, is denser than Z or Z4 by a factor of 2112 (or 1.51 dB). T

**Feedback**:
The text contains OCR garbling ('2112' instead of 2^{1/2}) which obscures the calculation. Correct the text and explicitly link the dB conversion to the power gain formula for verification.

---

### 10. Normalized Redundancy Notation Ambiguity [MINOR]

**Status**: [Pending]

**Quote**:
> where p( A ) is the normalized redundancy (per two dimensions) of A, p ( A ) = r ( A ) / N,

**Feedback**:
The definition of N is ambiguous (real vs. complex dimension). Explicitly state whether N refers to the complex dimension to avoid miscalculation of the normalized redundancy.

---

### 11. Constellation Expansion Factor Precision [MINOR]

**Status**: [Pending]

**Quote**:
> We therefore say that the constellation expansion factor is 2'(") in 2N dimensions,

**Feedback**:
The text claims the volume is 'approximately' 2^{r(A)} times larger, but this depends on the shaping region. Define the expansion factor precisely in terms of fundamental volumes rather than approximate finite constellation volumes.

---

### 12. Partition Order Notation Error [MINOR]

**Status**: [Pending]

**Quote**:
> * then the partition A/A' has order 2, for some integer K .*

**Feedback**:
The text displays '2,' which appears to be an OCR error for 2^K. Correct this notation error to standard exponential notation to ensure the mathematical statement regarding partition order is readable.

---

### 13. Ungerboeck Distance Bound Typos [MINOR]

**Status**: [Pending]

**Quote**:
> then J(h - h'1I2 2 diin(Ak),

**Feedback**:
The inequality contains multiple typographical errors ('J', '1I2', 'diin') that obscure the Ungerboeck distance bound. Correct to standard notation (e.g., ||lambda - lambda'||^2 >= d_min^2(A_k)) for clarity.

---

### 14. Decomposable Lattice Definition Invariance [MINOR]

**Status**: [Pending]

**Quote**:
> then we say that A is decomposable.

**Feedback**:
The definition relies on the existence of a specific set of generators but does not state if this property is invariant under basis change. Clarify whether decomposability is a property of the lattice itself or the specific generator choice.

---

### 16. Incomplete Sentence in Decomposition Section [MINOR]

**Status**: [Pending]

**Quote**:
> However, the lattices that are useful in

**Feedback**:
The section ends with an incomplete sentence, suggesting a truncation error. Complete the sentence to ensure crucial qualifications regarding the decomposability of non-mod-2 complex lattices are included.

---

### 18. Gaussian Integer Primes List Accuracy [MINOR]

**Status**: [Pending]

**Quote**:
> primes of G, in order of increasing norm, are 1+i, 2 i, 3,. ., with norms 2,5,9, . . . . We

**Feedback**:
The list contains OCR errors ('2 i,') obscuring the Gaussian integer primes. Correct the notation to ensure the list of primes and their norms is mathematically verifiable.

---
