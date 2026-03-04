# Regression Discontinuity Design with Distribution-Valued Outcomes

**Date**: 03/04/2026
**Domain**: statistics/causal_inference
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Internal Contradiction in Fréchet Estimator Bandwidth Derivation**

All three reviewers identify a critical theoretical inconsistency regarding the bandwidth selection for the Fréchet estimator. Section 3 explicitly states that no closed-form asymptotic MSE exists because Taylor expansions are not well-defined in the space of distributions, yet Appendix A-4.2.2 derives IMSE-optimal bandwidths using explicit bias and variance terms reliant on asymptotic equivalence with local polynomial estimators. This circular reasoning undermines the theoretical foundation; the paper must either provide valid functional Taylor expansions in Wasserstein space or reclassify the bandwidth selection as a heuristic validated by simulation rather than theory.

**Unverified Within-Group Sample Size Requirements**

The panel consistently flags Assumption Q1, which requires within-group empirical quantile estimators to converge faster than the across-group rate (√nh), as inadequately addressed in both theory and practice. The empirical application uses state-level data with dramatic variation in family counts (e.g., 204 effective state observations vs. 230,340 family observations), risking noisy quantile estimates that propagate bias into the second-stage RDD. The paper must specify minimum within-group sample size (ni) requirements and demonstrate these are met, or provide sensitivity analysis showing how estimator performance degrades when Q1 is violated.

**Invalid Hadamard Differentiability Assumption for Discrete Outcomes**

Theoretical validity of the multiplier bootstrap (Theorem 3) relies on the projection mapping being Hadamard differentiable with an identity derivative, which holds only if limit quantile functions are strictly increasing. However, the empirical income data likely contains discrete components (top-coding, rounding, zeros) that create flat regions in the CDF, violating strict monotonicity and invalidating the functional delta method argument. The paper should add robustness results for non-strictly-increasing quantile functions, explicitly assume positive continuous densities, or acknowledge that uniform confidence bands are incorrect for realistic income distributions.

**Missing Empirical RDD Validity and Manipulation Tests**

The empirical application employs a close-election RDD at the state-governor level but fails to report standard validity checks such as McCrary density tests or covariate balance tests for the state-level running variable. Without demonstrating continuity of the running variable density and covariates at the cutoff, the local randomization assumption underlying the R3D identification strategy remains unsupported, particularly given potential latent group heterogeneity between states that narrowly elect different parties. The authors must add density continuity tests and discuss why manipulation is unlikely in this specific electoral context.

**Underdeveloped Fuzzy RDD Identification Conditions**

The extension to fuzzy RDD (Section 2.5.3, Lemma 3) relies on untestable assumptions regarding complier status interacting with distribution-valued outcomes, specifically the 'zero-measure indefinites' assumption (Assumption I5) which is neither clearly defined nor verifiable. The identification argument does not establish whether monotonicity holds uniformly across all quantiles or if different distribution parts have different complier populations. The paper should explicitly define Assumption I5, clarify when fuzzy R3D is necessary versus sharp R3D, and provide testable implications for complier distribution assumptions in the functional outcome setting.

**Unsubstantiated Claims of Standard Quantile RDD Inconsistency**

The paper motivates the new method by claiming standard quantile RDD is biased and inconsistent, but the simulation evidence (Section 4.1) primarily demonstrates inference problems (artificially tight confidence bands) rather than point estimate inconsistency. The theoretical argument for why standard quantile RDD fails is not formally proven, and simulations are limited to two DGPs. The authors should clarify whether the inconsistency refers to biased point estimates or invalid inference, provide direct bias comparisons, and add a formal proposition showing under what conditions the standard estimator converges to a different limit.

**Variance Underestimation Due to Within-Group Sampling Assumption**

The theoretical framework (Section 2 & 3 main) assumes that group-level distributions $Y_i$ are 'fully observed' (Section 2.1), implying zero within-group estimation error for quantiles $Q_{Y_i}(q)$. However, the motivating examples (e.g., test scores in schools, wages in firms) and typical empirical applications involve finite within-group samples. The paper relegates the correction for within-group sampling noise to an extension (Section 3.3.1). If the main confidence bands (Section 3) are applied to data with finite within-group sizes without this extension, the standard errors will fail to account for the variance introduced by estimating $Q_{Y_i}(q)$, leading to underestimated uncertainty and invalid inference.

**Lack of Manipulation Checks for Group-Level Running Variables**

Assumption I2 posits a continuous, non-manipulated density for the running variable $X$ ($f_X$ differentiable, no manipulation). The motivating examples include 'vote share' and 'poverty rate', which are group-level variables known to be susceptible to manipulation (e.g., counties manipulating poverty rates, close elections). The provided methodology does not describe specific robustness checks (e.g., McCrary test, donut RD, covariate balance) tailored to verify I2 in these high-risk group-level contexts. Relying on I2 without empirical verification in settings prone to manipulation creates a risk that the local randomization assumption is violated, biasing the treatment effect estimates.

**Status**: [Pending]

---

## Detailed Comments (12)

### 2. Theoretical Contradiction in Fréchet Bandwidth Justification [CRITICAL]

**Status**: [Pending]

**Quote**:
> For the Fr´echet estimator in Section 2.5.2, no such closed-form expression for the asymp totic MSE exists, because the Taylor expansions it relies on is not well-defined in the space of distributio

**Feedback**:
The author claims no closed-form MSE exists, yet Appendix A-4.2.2 derives IMSE-optimal bandwidths using explicit bias and variance terms via asymptotic equivalence. This circular reasoning undermines the theoretical foundation; either provide valid Taylor expansions or reclassify bandwidth selection as heuristic.

---

### 8. Hadamard Differentiability Requirement for Discrete Outcomes [CRITICAL]

**Status**: [Pending]

**Quote**:
> edly, my results leverage the fact that Fr´echet regression in 2-Wasserstein space is an L^{2} projection of the local polynomial estimator onto the space of quantile functions.

**Feedback**:
Inference (Theorem 3) requires the projection mapping to be Hadamard differentiable, which is violated if limit quantile functions are not strictly increasing (e.g., discrete data). Explicitly assume positive continuous densities or acknowledge invalidity for realistic income distributions.

---

### 10. Bandwidth Rate Requirement Contradiction [CRITICAL]

**Status**: [Pending]

**Quote**:
> The_ _baseline_ _bandwidth_ h = _hn_ _satisfies_ _h →_ 0 _,_ nh^{2}

**Feedback**:
Assumption K2 requires nh^{2p+3} → 0 (undersmoothing), but the text states this accommodates rates 'slower than h = n^{-1/5}'. For MSE-optimal bandwidth h ∝ n^{-1/(2p+3)}, the term converges to a constant, not zero. Resolve this contradiction.

---

### 12. Variance Underestimation Due to 'Fully Observed' Assumption [CRITICAL]

**Status**: [Pending]

**Quote**:
> 'fully observed'

**Feedback**:
Section 2.1 assumes group-level distributions are 'fully observed', implying zero within-group estimation error. However, empirical applications involve finite within-group samples. Applying main confidence bands without correction leads to underestimated uncertainty and invalid inference.

---

### 1. Factual Error: Frandsen et al. (2012) Uniform Confidence Bands

**Status**: [Pending]

**Quote**:
> es. Frandsen et al. (2012) first developed the framework for quantile RD and derived uniform convergence results, though they did not derive uniform confidence b

**Feedback**:
This claim is factually incorrect. Frandsen, Frölich, and Melly (2012, Econometrica) explicitly derive uniform confidence bands for quantile treatment effects in RDD (Section 4, Theorem 2). This misrepresentation unfairly diminishes prior work to overstate novelty.

---

### 6. Impossible Inequality in Neighborhood Definition

**Status**: [Pending]

**Quote**:
> nd let c _<_ 0 _<_ c . Also, define _Yc_ := _{Y_ ( ω ) : ω _∈_ Ω

**Feedback**:
The text defines the neighborhood using 'c < 0 < c', which is mathematically impossible for a single scalar c. It should be 'c̲ < 0 < c̄' (lower and upper bounds), as confirmed by the use of [c̲, c̄] in Assumption L3.

---

### 7. Overstatement of Standard Quantile RDD Inconsistency

**Status**: [Pending]

**Quote**:
> d, in what follows, the quantile RD estimator is shown to be biased and inconsistent in the R3D setting, both theoretically and in simulations. Se

**Feedback**:
Simulation evidence primarily demonstrates inference problems (undercovering), not fundamental inconsistency of the point estimator. Standard quantile RDD remains consistent under correct specification. Clarify whether 'inconsistency' refers to inference failure under misspecification.

---

### 9. Logical Error in Continuity Assumption Comparison

**Status**: [Pending]

**Quote**:
> wise unrestricted. Indeed, while I1 is consistent with the common approach of averaging the outcome variable at the level of the aggregate unit and then estimating a standard RD, the continuity assumption in Frandsen et al. (2012) is not: there would be no random variation

**Feedback**:
This reasoning is flawed. Standard RD relies on continuity of E[Y|X], while Y retains variance. Similarly, Frandsen et al. (2012) rely on continuity of the conditional quantile function, which does not imply zero variance or deterministic averages.

---

### 11. Untestable Fuzzy RDD Assumption I5

**Status**: [Pending]

**Quote**:
> 'zero-measure indefinites' assumption (Assumption I5)

**Feedback**:
Assumption I5 is neither clearly defined nor verifiable. The identification argument does not establish whether monotonicity holds uniformly across all quantiles or if different distribution parts have different complier populations. Explicitly define I5 and provide testable implications.

---

### 3. Inconsistent Cutoff Notation in Density Assumption I2 [MINOR]

**Status**: [Pending]

**Quote**:
> (Density at threshold) **.** _FX_ ( x ) _is_ _differentiable_ _at_ c _and_ 0 _<_

**Feedback**:
In Assumption I2, the cutoff is denoted as 'c', but throughout Section 2 (Equation 1, Assumption I1, Lemma 1), the cutoff is explicitly set to 0. For consistency with Lemma 1 ('lim x→0'), the assumption should state differentiability at 0.

---

### 4. Typo in Counterfactual Distribution Description [MINOR]

**Status**: [Pending]

**Quote**:
> e he counterfactual distribution functions Y _[t]_ are drawn from a class of normal distributions

**Feedback**:
There is a typographical error: 'he' should be 'the'. This appears in the paragraph following Proposition 1 in Section 2.3.2.

---

### 5. Incorrect Variance Notation for Scalar Running Variable [MINOR]

**Status**: [Pending]

**Quote**:
> n addition, let µ = E [ X ] and Σ = var( X ) with Σ positive defi

**Feedback**:
X is defined as a scalar-valued running variable (X ∈ R). For a scalar, variance is a real number, and 'positive definite' is reserved for covariance matrices. The condition should simply be Σ > 0.

---
