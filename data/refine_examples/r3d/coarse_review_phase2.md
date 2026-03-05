# Regression Discontinuity Design with Distribution-Valued Outcomes

**Date**: 03/04/2026
**Domain**: statistics/causal_inference
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Hierarchical Variance Structure and Bootstrap Validity**

The proposed multiplier bootstrap and asymptotic theory treat observations as i.i.d. draws (Assumption L1), ignoring the hierarchical data structure where treatment is assigned at the group level and outcomes are estimated from within-group subsamples. This oversight fails to capture two-level variance (between-group vs. within-group sampling variation) and correlation within groups, risking significant undercoverage of confidence bands. Additionally, the validity of the uniform bands relies on unverified VC-type conditions for the weighted empirical process. To address this, modify Algorithm 1 to draw group-level multipliers or aggregate residuals to the group level, incorporate within-group sampling variance into the asymptotic theory, and provide simulation evidence demonstrating empirical coverage rates across varying sample sizes and bandwidths.

**Identification Assumption Verification and Continuity Bias**

Assumption I1 requires the average quantile function to be continuous at the cutoff, but this is threatened by discontinuities in within-group sample sizes (n_i) which induce artificial jumps in empirical quantile precision, biasing treatment effect estimates. Furthermore, the empirical application lacks standard RDD validity checks, such as McCrary density tests for running variable manipulation and covariate balance tests adapted for distributional outcomes. Without these, the causal interpretation is vulnerable to sorting and pre-existing discontinuities. Fix: Add a formal pre-test procedure (e.g., placebo cutoff tests), include density discontinuity tests and distributional balance checks in Section 4.2, and theoretically address bias from heterogeneous n_i by weighting observations or adding continuity assumptions on sample sizes.

**Bandwidth Selection and Smoothness Heterogeneity**

The paper applies scalar RDD bandwidth rates (h → 0, nh^2 → ∞) to functional outcomes without theoretical justification that these remain optimal for distribution-valued data. Moreover, using a single IMSE-optimal bandwidth across all quantiles assumes homogeneous smoothness, which likely fails in the tails. This is critical because the main empirical finding of 'income reductions at the top' relies on the 85th-95th percentiles, precisely where a single bandwidth may oversmooth and distort effects. Fix: Provide theoretical justification for scalar bandwidth rates in the functional setting or derive new rates, and conduct a sensitivity analysis using quantile-specific bandwidths to verify that tail effects persist under optimization for local smoothness.

**Fréchet Estimator Asymptotic Equivalence and Monotonicity**

Theorem 4 claims the Fréchet estimator has the same asymptotic distribution as the local polynomial estimator, relying on the Hadamard derivative of the projection operator equaling the identity. This holds only if the true quantile function is strictly increasing; if flat regions exist (common in income data), the derivative is not the identity, invalidating the equivalence claim. There is also a logical tension between the estimator's purpose (preventing quantile crossing via projection) and the equivalence claim (which requires the constraint to be inactive asymptotically). Fix: Add an explicit assumption that true average quantile functions are strictly increasing, or modify Theorem 4 to characterize the asymptotic distribution when monotonicity fails, and include a lemma proving the probability of crossing vanishes under specific smoothness conditions.

**Sensitivity to Distributional Metric Choice**

The Fréchet estimator relies on the 2-Wasserstein distance, which equates the Fréchet mean to the average quantile function. However, the choice of metric implicitly weights different parts of the distribution and determines the definition of 'average,' potentially driving the heterogeneity findings and the equality-efficiency trade-off conclusion. The paper provides no robustness checks against alternative metrics (e.g., L2 on CDFs, Kolmogorov-Smirnov, energy distance) that might capture different aspects of distributional change. Fix: Add a robustness section comparing LAQTE estimates under at least one alternative metric and discuss whether the substantive conclusions regarding inequality and efficiency are dependent on the 2-Wasserstein specification.

**Fully Observed Distributions Assumption vs. Sampled Reality**

Section 2.1 explicitly assumes that the distribution-valued outcome $Y_i$ (and its quantile function $Q_{Y_i}$) is 'fully observed' for each unit, treating it as a direct random element in Wasserstein space. However, the motivating examples in Section 2.2 (e.g., test scores within schools, wages within establishments) inherently involve observing a finite sample of individuals within each group, not the true population distribution. The estimators in Section 2.5 and inference in Algorithm 1 treat $Q_{Y_i}(q)$ as observed data without accounting for the within-group estimation error or the heteroskedasticity introduced by varying group sizes. This mismatches the theoretical assumption with the actual problem structure, potentially biasing standard errors and bandwidth selection which rely on the variance of the 'observed' outcome rather than the variance of the estimated distribution.

**Continuous Running Variable Assumption vs. Discrete Examples**

Assumption I2 (Section 2.3.2) requires the running variable $X$ to have a differentiable CDF and a well-defined PDF at the cutoff, implying continuity. However, Motivating Example 2 (Section 2.2) uses 'parent vote share' in school elections as the running variable. Vote shares are inherently discrete (determined by a finite number of voters), which violates the continuity assumption required for the local polynomial asymptotics and bias corrections derived in Section 2.7. Applying the continuous RD theory to discrete running variables without adjustment (e.g., for heaping or discreteness) risks invalidating the identification strategy and inference.

**Independence of Groups Assumption vs. Clustered Data Structures**

The setting in Section 2.1 assumes that the group-level observations $(X_i, Y_i)$ are i.i.d. draws from a joint distribution $F$. The multiplier bootstrap in Algorithm 1 respects this by resampling units $i$ independently. However, the motivating examples (counties, school districts, establishments) often exhibit spatial correlation or clustering at higher levels (e.g., schools within districts, counties within states). The methodology does not incorporate clustering of standard errors across these higher-level aggregates. If the empirical implementation applies this i.i.d. bootstrap to clustered data, the resulting uniform confidence bands will likely be too narrow, leading to over-rejection of the null hypothesis.

**Status**: [Pending]

---

## Detailed Comments (15)

### 4. LAQTE Conflated with Fréchet Mean Distribution [CRITICAL]

**Status**: [Pending]

**Quote**:
> In particular, the distribution defined by the LAQTEs has the intuitive interpretation of being the unique distribution with the lowest possible cumulative 'leastsquares' cost of transporting its probability mass into each of the underlying distributions of the individual units.

**Feedback**:
The Local Average Quantile Treatment Effect (LAQTE) is defined as the difference between average quantile functions, representing a causal effect, not a probability distribution. The Fréchet mean property (minimizing expected Wasserstein distance) applies to the average quantile function of the potential outcomes, which defines a valid distribution. The LAQTE function does not necessarily satisfy quantile function properties (e.g., monotonicity) and thus cannot be interpreted as a distribution minimizing transport cost.

---

### 9. Lemma 2 Incorrectly Claims Pointwise and Lp Error Reduction [CRITICAL]

**Status**: [Pending]

**Quote**:
> Then the projected curve ˆ Q ∗ = Π Q ( ˆ Q ) is closer to the true curve in the sense that, for each x ∈ R ,

**Feedback**:
The L_2 projection operator Π_Q onto the cone of monotone functions guarantees global norm reduction, not pointwise inequality for every x. Furthermore, quantile functions are defined on the probability domain [0, 1], not x ∈ R. Additionally, the claim that the 'no-regret' property holds in 'any L_p norm' is mathematically incorrect; an L_2 projection ensures error reduction in the L_2 norm but not necessarily in L_1 or L_∞.

---

### 10. Fuzzy Monotonicity Assumption Implies Sharp Design [CRITICAL]

**Status**: [Pending]

**Quote**:
> - I5 (Monotonicity) . lim x → 0 P ( T 1 > T 0 | X = x ) = 1 and P (Indefinites)

**Feedback**:
In a Fuzzy RDD design, the compliance rate P(T_1 > T_0) is typically strictly less than 1, allowing for always-takers and never-takers. This assumption forces the compliance rate to 1 at the cutoff, implying the first-stage denominator equals 1. This collapses the Fuzzy Wald estimator to the Sharp RD estimator, contradicting the section's premise of estimating a Fuzzy R3D model. Standard monotonicity assumptions require P(T_1 ≥ T_0) = 1 (no defiers), not strict inequality.

---

### 11. Bootstrap Process Independent of Multipliers in Algorithm 1 [CRITICAL]

**Status**: [Pending]

**Quote**:
> Form estimate of limiting process ˆ G R3D ,b ( q j ) = ˆ m + , ( ⊕ ) ,p ( q j ) -ˆ m -, ( ⊕ ) ,p ( q j ).

**Feedback**:
Step 11 lies inside the bootstrap loop (Steps 6-12), but the right-hand side uses estimates computed in Step 2 (outside the bootstrap loop). Consequently, the bootstrap process is identical for all b, and the multipliers drawn in Step 7 are never utilized, rendering the bootstrap degenerate. Additionally, Step 14 uses index b after the loop closes, and the interval [q,q] in the test statistic is zero-length.

---

### 14. Fréchet Estimator Asymptotic Equivalence and Monotonicity [CRITICAL]

**Status**: [Pending]

**Quote**:
> Theorem 4 claims the Fréchet estimator has the same asymptotic distribution as the local polynomial estimator, relying on the Hadamard derivative of the projection operator equaling the identity.

**Feedback**:
This equivalence holds only if the true quantile function is strictly increasing; if flat regions exist (common in income data), the derivative is not the identity, invalidating the equivalence claim. Add an explicit assumption that true average quantile functions are strictly increasing, or modify Theorem 4 to characterize the asymptotic distribution when monotonicity fails, and include a lemma proving the probability of crossing vanishes under specific smoothness conditions.

---

### 1. Table 1 Subcategory Percentages Exceed Total

**Status**: [Pending]

**Quote**:
> |                           | Economics   | Political Science   |
> |---------------------------|-------------|---------------------|
> | Any R3D (%)               | 37.9        | 32.3                |
> | Disaggregated (%)         | 25.8        | 15.1                |
> | Aggregated (%)            | 19.7        | 19.4                |

**Feedback**:
Mathematical inconsistency: If 'Any R3D' represents papers with either disaggregated OR aggregated data, and these subcategories are mutually exclusive, then Any R3D should equal Disaggregated + Aggregated. For Economics: 25.8 + 19.7 = 45.5%, but Any R3D shows 37.9%. For Political Science: 15.1 + 19.4 = 34.5%, but Any R3D shows 32.3%. The subcategory sums exceed the total category, indicating a calculation error or overlapping categories contrary to the table note.

---

### 2. Card and Krueger Study Design Mischaracterization

**Status**: [Pending]

**Quote**:
> Card and Krueger (2000) studied the effect of a minimum wage increase ( T ) in New Jersey on wages, employment, and prices in fast food restaurants, comparing establishments on either side of the border with Pennsylvania. The running variable here is distance to the border ( X ) .

**Feedback**:
Card and Krueger (1994/2000) is a canonical Difference-in-Differences study, not a Regression Discontinuity Design based on distance to the border. They compared state-level aggregates before and after the policy change, not local variation around a geographic cutoff using distance as a running variable. Presenting this as an RDD example is factually incorrect and undermines the motivating evidence.

---

### 5. Proposition 1 Quantile Index Domain Mismatch

**Status**: [Pending]

**Quote**:
> Proposition 1 (Smooth average vs. discontinuous observed quantile functions) . Fix q ∈ (0 , 1) .

**Feedback**:
The proposition header restricts the quantile index q to the open interval (0, 1), but part (ii) of the proposition claims the result holds for 'q ∈ [0 , 1]'. Quantiles at the boundaries 0 and 1 correspond to the infimum and supremum of the support and often require distinct assumptions (e.g., bounded support) not stated here, making the extension to the closed interval mathematically unsupported by the stated premises.

---

### 6. Q-RDD Estimand Misidentified as Distribution Function

**Status**: [Pending]

**Quote**:
> The Q-RDD on the other hand, aims to estimate a fixed distribution function.

**Feedback**:
Frandsen et al. (2012) target the discontinuity in the conditional quantile function, not a 'fixed distribution function'. Quantile RD estimates Q_{Y|X}(τ|c+) - Q_{Y|X}(τ|c-). A distribution function refers to F(y), whereas Q-RDD targets quantiles τ. This mischaracterization undermines the comparison between methods. Rewrite as 'aims to estimate a discontinuity in the conditional quantile function'.

---

### 7. Contradictory Claims on Group Level Weighting

**Status**: [Pending]

**Quote**:
> The former approach estimates a weighted average treatment effect, weighted by group size

**Feedback**:
This statement contradicts the subsequent claim that 'The strategy of first aggregating to the group level... will estimate the unweighted average treatment effect.' Both sentences refer to Approach 1 (aggregating to group level). Standard RDD theory confirms that group-level aggregation yields an unweighted ATE, while disaggregated regression yields a group-size-weighted ATE. The text likely swapped 'former' and 'latter' in the first instance.

---

### 12. Reversal of CCT Bandwidth Selection Orders

**Status**: [Pending]

**Quote**:
> Here, s is the desired order of the local polynomial regression (typically s = 1 for local linear), which is used for bandwidth selection, while estimation is done with a p -th order polynomial where p >

**Feedback**:
This contradicts the standard Calonico et al. (2014) procedure referenced. In CCT, the bandwidth h is selected to minimize the MSE of the p-th order estimator (e.g., local quadratic, p=2), which is then bias-corrected using the s-th order (e.g., local linear, s=1). The text reverses this, claiming selection is based on the lower order s. This leads to suboptimal bandwidths for the main p-th order estimator.

---

### 13. MSE Equivalence Requires L2 Convergence

**Status**: [Pending]

**Quote**:
> As a result, their mean squared errors are asymptotically equivalent.

**Feedback**:
Convergence in probability (o_p(1)) of the difference between estimators does not imply convergence of their second moments (Mean Squared Error). To claim MSE equivalence, the paper must establish L_2 convergence (i.e., E[∥difference∥^2] -> 0). Without uniform integrability or bounds ensuring the difference vanishes in mean square, the deduction that MSEs are equivalent is mathematically unsupported.

---

### 15. Fully Observed Distributions Assumption vs. Sampled Reality

**Status**: [Pending]

**Quote**:
> Section 2.1 explicitly assumes that the distribution-valued outcome $Y_i$ (and its quantile function $Q_{Y_i}$) is 'fully observed' for each unit

**Feedback**:
The motivating examples in Section 2.2 (e.g., test scores within schools, wages within establishments) inherently involve observing a finite sample of individuals within each group, not the true population distribution. The estimators in Section 2.5 and inference in Algorithm 1 treat $Q_{Y_i}(q)$ as observed data without accounting for the within-group estimation error or the heteroskedasticity introduced by varying group sizes. This mismatches the theoretical assumption with the actual problem structure, potentially biasing standard errors and bandwidth selection.

---

### 3. Notation Collision Between Space and Random Variable Y [MINOR]

**Status**: [Pending]

**Quote**:
> be the space of cumulative distribution functions (cdfs) G on R with finite variance, ∫ R x 2 d G ( x ) < ∞ . Let ( X,Y ) ∼ F be a random element with joint distribution F on R ×Y . H

**Feedback**:
The symbol Y is overloaded to denote both the metric space of CDFs (first sentence) and the random variable (second sentence). In the pair (X, Y), Y acts as the random variable, but in the product space R ×Y, Y acts as the space. This ambiguity should be resolved by using distinct notation (e.g., script Y for the space) to prevent confusion in subsequent derivations involving marginal distributions.

---

### 8. Invalid Indicator Function Syntax in Estimator Definition [MINOR]

**Status**: [Pending]

**Quote**:
> δ ± i := 1 { X i ⩾ < c }

**Feedback**:
The indicator function definition is syntactically invalid due to the sequence '⩾ <' (rendering as '>= <'). This makes the estimator undefined. It should be split into two separate indicators for the treatment and control sides, e.g., δ_i^+ := 1{X_i ≥ c} and δ_i^- := 1{X_i < c}, or use a single indicator with a side parameter.

---
