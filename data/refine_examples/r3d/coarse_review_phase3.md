# Regression Discontinuity Design with Distribution-Valued Outcomes

**Date**: 03/04/2026
**Domain**: statistics/causal_inference
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Asymptotic Equivalence and Monotonicity Conditions**

Theorem 4 claims the Fréchet estimator shares the asymptotic distribution of the local polynomial estimator, relying on the Hadamard derivative of the projection operator equaling the identity. Readers might note that this condition holds strictly only when the true conditional mean quantile function is strictly monotone and interior to the function space. At boundary points where monotonicity constraints bind, the derivative becomes a projection operator, potentially altering the asymptotic variance structure relied upon for uniform confidence bands. It would be helpful to add an assumption requiring strict monotonicity of the conditional mean quantile function or characterize the asymptotic distribution when monotonicity constraints bind at some quantiles.

**Bandwidth Selection Consistency and Assumptions**

There is an internal tension between the claim that the Fréchet estimator fits the quantile curve with a single bandwidth and Assumption K2, which specifies a bandwidth structure allowing quantile-specific scaling functions. This discrepancy affects reproducibility and the validity of uniform asymptotic results that depend on the bandwidth structure. It would be helpful to either revise Assumption K2 to specify a constant scaling factor for the Fréchet estimator or clarify that the 'single bandwidth' refers to the baseline parameter while allowing scaling factors that converge to constants.

**Multiplier Bootstrap Validity for Functional Outcomes**

Algorithm 1 employs a multiplier bootstrap for uniform inference, estimating residuals using first-stage local polynomial estimates. The proof of bootstrap validity cites existing literature but does not explicitly verify that this residual estimation method preserves asymptotic correctness for the functional outcome setting, particularly regarding two-stage sampling variability. Readers might note that improper residual estimation can lead to undercoverage of uniform confidence bands if first-stage error is of the same order as bootstrap approximation error. It would be helpful to add a lemma showing that the residual estimation error is negligible uniformly over the quantile process or specify conditions on the first-stage smoothing relative to the main estimator.

**Simulation Design and Estimand Comparability**

The simulation results claim standard quantile RDD is biased and inconsistent by comparing R3D to the Q-RDD estimator, yet these methods target different population quantities such as underlying average quantile functions versus observed quantile function jumps. Demonstrating bias in this manner is tautological given the differing estimands and does not establish R3D's superiority for practical applications. It would be helpful to redesign the simulations to show Q-RDD fails to consistently estimate its own target in the grouped-data setting or provide explicit welfare justification for why the R3D estimand is more policy-relevant.

**Identification Assumptions and Empirical Validity Checks**

The identification strategy relies on continuity assumptions for the average quantile function and first-stage treatment probability, yet standard RDD validity checks are omitted in the empirical application. The gubernatorial election analysis lacks McCrary density tests, covariate balance tables, and falsification tests at placebo cutoffs adapted for distribution-valued outcomes. Readers might note that without these checks, it is difficult to assess whether estimated discontinuities reflect causal effects or pre-existing differences, particularly given the difficulty in testing continuity assumptions with functional outcomes. It would be helpful to add a subsection presenting density test results, balance tables for key covariates, and balance tests for pre-treatment distributional characteristics to validate the identification assumptions.

**Wasserstein Barycenter Interpretation vs. Local Polynomial Weights**

The paper claims the Fréchet estimator (Section 2.5.2) computes a 'weighted central tendency' (Wasserstein barycenter) using local polynomial weights. However, Wasserstein barycenters are mathematically defined as minimizers of weighted squared distances with non-negative weights to ensure convexity and existence in the space of probability measures. Local polynomial weights (Section 2.5.1) can be negative. While the projection algorithm remains computationally valid, the theoretical interpretation as a Wasserstein barycenter fails when weights are negative, as the optimization problem is no longer convex. This contradicts the claim in Proposition A-3 that the estimator coincides with the local Fréchet regression estimator under the stated assumptions without qualifying the weight constraints.

**Independence Assumption vs. Spatial Correlation in Motivating Examples**

Assumption I2 and the multiplier bootstrap procedure (Algorithm 1) rely on the i.i.d. sampling of aggregate units $(X_i, Y_i)$. However, the motivating examples (e.g., Example 3: distance to border; Example 2: school votes) inherently involve spatial or contextual correlation between units (neighboring counties or schools). The provided inference methodology uses i.i.d. multipliers and does not account for between-group correlation (only within-group correlation is addressed via aggregation). If the empirical implementation follows these examples without spatially robust inference, the uniform confidence bands will be invalid due to violated independence assumptions, leading to over-rejection of null hypotheses.

**No-Manipulation Assumption vs. Lack of Diagnostic in Methodology**

Assumption I2 (Density at threshold) explicitly posits no manipulation of the running variable, which is critical for identification (Lemma 1). One of the primary motivating examples (Example 2) involves election margins, a context known for high manipulation risk. However, the described methodology (Algorithm 1, Section 2.7) focuses on bandwidth selection and bootstrap inference without including a manipulation test (e.g., McCrary density test). The implementation proceeds to estimate treatment effects without a mechanism to verify the validity of the core identification assumption, creating a risk of applying the method in settings where the RDD design is invalid.

**Status**: [Pending]

---

## Detailed Comments (20)

### 1. Asymptotic Equivalence and Monotonicity Conditions

**Status**: [Pending]

**Quote**:
> Theorem 4 claims the Fréchet estimator shares the asymptotic distribution of the local polynomial estimator, relying on the Hadamard derivative of the projection operator equaling the identity.

**Feedback**:
Readers might note that this condition holds strictly only when the true conditional mean quantile function is strictly monotone and interior to the function space. At boundary points where monotonicity constraints bind, the derivative becomes a projection operator, potentially altering the asymptotic variance structure relied upon for uniform confidence bands. It would be helpful to add an assumption requiring strict monotonicity of the conditional mean quantile function or characterize the asymptotic distribution when monotonicity constraints bind at some quantiles.

---

### 2. Bandwidth Selection Consistency and Assumptions

**Status**: [Pending]

**Quote**:
> There is an internal tension between the claim that the Fréchet estimator fits the quantile curve with a single bandwidth and Assumption K2, which specifies a bandwidth structure allowing quantile-specific scaling functions.

**Feedback**:
This discrepancy affects reproducibility and the validity of uniform asymptotic results that depend on the bandwidth structure. It would be helpful to either revise Assumption K2 to specify a constant scaling factor for the Fréchet estimator or clarify that the 'single bandwidth' refers to the baseline parameter while allowing scaling factors that converge to constants.

---

### 3. Identification Assumptions and Empirical Validity Checks

**Status**: [Pending]

**Quote**:
> The identification strategy relies on continuity assumptions for the average quantile function and first-stage treatment probability, yet standard RDD validity checks are omitted in the empirical application.

**Feedback**:
The gubernatorial election analysis lacks McCrary density tests, covariate balance tables, and falsification tests at placebo cutoffs adapted for distribution-valued outcomes. Without these checks, it is difficult to assess whether estimated discontinuities reflect causal effects or pre-existing differences. It would be helpful to add a subsection presenting density test results, balance tables for key covariates, and balance tests for pre-treatment distributional characteristics to validate the identification assumptions.

---

### 4. Wasserstein Barycenter Interpretation vs. Local Polynomial Weights

**Status**: [Pending]

**Quote**:
> The paper claims the Fréchet estimator (Section 2.5.2) computes a 'weighted central tendency' (Wasserstein barycenter) using local polynomial weights.

**Feedback**:
Wasserstein barycenters are mathematically defined as minimizers of weighted squared distances with non-negative weights to ensure convexity and existence in the space of probability measures. Local polynomial weights (Section 2.5.1) can be negative. While the projection algorithm remains computationally valid, the theoretical interpretation as a Wasserstein barycenter fails when weights are negative, as the optimization problem is no longer convex. It would be helpful to qualify the weight constraints in Proposition A-3.

---

### 5. Independence Assumption vs. Spatial Correlation in Motivating Examples

**Status**: [Pending]

**Quote**:
> Assumption I2 and the multiplier bootstrap procedure (Algorithm 1) rely on the i.i.d. sampling of aggregate units $(X_i, Y_i)$.

**Feedback**:
However, the motivating examples (e.g., Example 3: distance to border; Example 2: school votes) inherently involve spatial or contextual correlation between units. The provided inference methodology uses i.i.d. multipliers and does not account for between-group correlation. If the empirical implementation follows these examples without spatially robust inference, the uniform confidence bands will be invalid due to violated independence assumptions. It would be helpful to address this potential correlation structure.

---

### 6. Table 1 Percentage Calculation Error

**Status**: [Pending]

**Quote**:
> Table 1: R3D-Like Settings in Top Journals (2014-2024) ... Any R3D (%) | 37.9 | 32.3 ... Disaggregated (%) | 25.8 | 15.1 ... Aggregated (%) | 19.7 | 19.4

**Feedback**:
The subcategory percentages do not sum to the total: for Economics, 25.8% + 19.7% = 45.5%, but Any R3D is listed as 37.9%. For Political Science, 15.1% + 19.4% = 34.5%, but Any R3D is 32.3%. If these subcategories are mutually exclusive as the note suggests, they should sum to Any R3D. It would be helpful to clarify whether these categories overlap or correct the calculation.

---

### 7. Frandsen et al. Uniform Confidence Bands Claim

**Status**: [Pending]

**Quote**:
> Frandsen et al. (2012) first developed the framework for quantile RD and derived uniform convergence results, though they did not derive uniform confidence bands.

**Feedback**:
Readers might note that Frandsen et al. (2012) is widely cited for establishing uniform inference procedures, including confidence bands, for quantile treatment effects in RDD. It would be helpful to verify the specific inference results in that paper before stating they lacked uniform bands, as this is a key contribution of their work. Distinguishing the specific type of bands or coverage properties would clarify the true novelty gap relative to existing quantile RD methods.

---

### 8. Section Ordering Creates Logical Dependency

**Status**: [Pending]

**Quote**:
> Before presenting two consistent estimators for these LAQTEs, I briefly discuss the distinction between my R3D setting and the classical quantile RD setting of Frandsen et al. (2012). I conclude providing an overview of the statistical inference tools developed in Section 3

**Feedback**:
Referencing inference tools in Section 3 before the estimators are defined in Section 2 creates a logical dependency loop. Typically, inference theory relies on the estimators being defined first. It would be helpful to verify the section numbering to ensure the inference tools are presented after the estimators they analyze, or update the cross-reference if Section 3 is intended to follow this section.

---

### 9. Treatment Assignment Equation Mismatch

**Status**: [Pending]

**Quote**:
> Then, denote by T ∈ { 0 , 1 } the treatment status. I assume that T is a monotonic function of X such that, $$\hat{\mathcal{E}}_1(y, t, x, q) = \left(Q_Y(q) - \tilde{E}[Q_Y(q) \mid X=x]\right) 1\left(|x/h_1(q)| \leq 1\right)$$

**Feedback**:
The text states that treatment T is a function of X such that the displayed equation holds, but the equation defines an error term dependent on outcome quantiles, not the treatment status T. In a sharp RDD, the treatment assignment rule is typically T = 1{X ≥ c}. It would be helpful to replace this equation with the explicit treatment assignment rule to ensure the definition of T matches the subsequent explanation that treatment is assigned deterministically when X crosses the threshold.

---

### 10. Scalar Variance Notation Inconsistency

**Status**: [Pending]

**Quote**:
> In addition, let µ = E [ X ] and Σ = var( X ) with Σ positive definite.

**Feedback**:
The text explicitly defines X as a scalar variable (X ∈ ℝ) in the first paragraph. Consequently, the variance var(X) is a scalar value σ², not a matrix Σ. The property positive definite applies to matrices; for a scalar variance, the correct condition is positive (i.e., σ² > 0). It would be clearer to write σ² = var(X) with σ² > 0 to avoid inconsistency if later derivations rely on matrix algebra.

---

### 11. Quantile Function Definition Mismatch

**Status**: [Pending]

**Quote**:
> Further, I will write Q Y ( q ) for the function mapping the cdf Y to quantiles, $$\check{\alpha}_{\pm,s}(q) = \arg \min_{\alpha \in \mathbb{R}^{s+1}} \sum_{i=1}^n \delta_i^{\pm} K\left(\frac{X_i}{h_{k,n}^0}\right) \left[Q_{Y_i}(q) - \alpha^\top r_s\left(\frac{X_i}{h_{k,n}^0}\right)\right]^2$$

**Feedback**:
The text introduces the notation Q_Y(q) as the quantile function mapping, but the displayed equation defines α̌_{±,s}(q), which is a local polynomial coefficient estimator. The equation does not define Q_Y(q); rather, it uses Q_{Y_i}(q) as an observed input in the objective function. Separating these definitions would prevent confusion between the population quantity and the estimator.

---

### 12. Card and Krueger Methodology Mischaracterization

**Status**: [Pending]

**Quote**:
> In another seminal article, Card and Krueger (2000) studied the effect of a minimum wage increase ( T ) in New Jersey on wages, employment, and prices in fast food restaurants, comparing establishments on either side of the border with Pennsylvania. The running variable here is distance to the border ( X ) .

**Feedback**:
Card and Krueger (1994/2000) employed a difference-in-differences design comparing state-level aggregates, not a regression discontinuity design utilizing distance to the border as a continuous running variable. Attributing this specific RD methodology to their work misrepresents the identification strategy of the cited study, which relied on parallel trends rather than continuity at a cutoff. It would be helpful to either cite a study that explicitly employs a geographic RDD or rephrase this example to clarify that the R3D framework could be applied to a similar setting.

---

### 13. Frandsen Continuity Assumption Mischaracterization

**Status**: [Pending]

**Quote**:
> Second, as mentioned, the quantile continuity assumption required for the identification of the estimator in Frandsen et al. (2012) is highly restrictive in the R3D setting, requiring that two units that are both close to the threshold have essentially identical distributions.

**Feedback**:
It appears there may be a misunderstanding of the continuity assumption in Frandsen et al. (2012), which posits continuity of the conditional quantile function rather than identical outcomes for units with similar running variables. Standard regression discontinuity designs, including quantile extensions, explicitly allow for individual-level heterogeneity and noise conditional on the running variable. It would be helpful to revise this comparison to highlight that the key distinction lies in the outcome space (distribution-valued versus scalar) rather than the presence of residual variation.

---

### 14. Former/Latter Inconsistency in Weighted Approaches

**Status**: [Pending]

**Quote**:
> The literature has taken two approaches for estimating average treatment effects in the grouped data setting considered in this paper: 1) aggregate to the group (firm) level and fit a local polynomial regression on the group averages; 2) fit a local polynomial regression directly on the disaggregated (employee) data, while clustering the standard errors at the group (firm) level (Bartalotti and Brummet, 2017). The former approach estimates a weighted average treatment effect

**Feedback**:
Readers might note an inconsistency between the description of the two approaches in the opening sentences and the later clarification regarding the estimands. The text identifies approach 1 as aggregating to the group level and approach 2 as using disaggregated data, yet states the former estimates a weighted average treatment effect. Standard RDD theory indicates that the pooled disaggregated approach yields the weighted estimand while aggregation yields the unweighted one. It would be helpful to replace former with latter in the second sentence to align with the list order.

---

### 15. Undefined Indicator Notation in Estimator Definition

**Status**: [Pending]

**Quote**:
> where e 0 is the first standard basis vector, K ( x ) a kernel function, δ ± i := 1 { X i ⩾ &lt; c } , and r p ( x ) := (1 , x, x 2 , . . . , x p ).

**Feedback**:
The definition of the indicator variable δ ± i contains a syntax error with the combined inequality ⩾ &lt;. In standard regression discontinuity designs, separate indicators are required for the treatment and control sides, typically defined as δ⁺_i = 1{X_i ≥ c} and δ⁻_i = 1{X_i < c}. As written, the condition is mathematically undefined and prevents the reader from implementing the estimator. It would be helpful to rewrite this definition to explicitly distinguish the two limits around the cutoff c.

---

### 16. Bias Correction Equivalence Interpretation

**Status**: [Pending]

**Quote**:
> Following Chiang et al. (2019), I build bias correction into the estimator by leveraging Remark 7 in (Calonico et al., 2014), which establishes an equivalence between explicitly bias-corrected estimators and estimators where the MSE-optimal bandwidth is chosen based on a pilot estimator of lower order

**Feedback**:
Readers might note that the description of Calonico et al. (2014) Remark 7 conflates bias correction with bandwidth selection. The cited literature proposes subtracting an explicit bias estimate to permit the use of MSE-optimal bandwidths, rather than claiming equivalence between the corrected estimator and a specific bandwidth rule. The bias-corrected estimator is algebraically distinct because it removes the leading bias term, whereas bandwidth selection alone affects the bias-variance tradeoff without eliminating the asymptotic bias. It would be helpful to clarify that the implementation involves constructing τ̂_BC = τ̂ - B̂ using the recommended bandwidths.

---

### 17. Lp Norm Contraction Property Claim

**Status**: [Pending]

**Quote**:
> The key insight from Theorem 4 below is that because the population quantity m ± ( q ) is already a valid quantile function, the projection acts as an identity operator asymptotically. In finite samples, however, it does enforce the shape constraint while also enjoying a 'no-regret' property (Lemma 2): the projected estimate is always closer to the truth than the unprojected one in any L p norm.

**Feedback**:
The section defines Π_Q as the L² projection onto the space of restricted quantile functions. By the Projection Theorem in Hilbert spaces, the inequality ‖Π_Q(Q̂) - Q₀‖₂ ≤ ‖Q̂ - Q₀‖₂ holds because Q₀ lies in the convex constraint set. However, an L² projection is not generally a contraction in L^p norms for p ≠ 2. It would be helpful to specify that the no-regret property is rigorously guaranteed in the L² norm, or provide a derivation showing why it extends to arbitrary L^p norms in this specific context.

---

### 18. Bootstrap Step 11 Ignores Multiplier Weights

**Status**: [Pending]

**Quote**:
> 11: Form estimate of limiting process ˆ G R3D ,b ( q j ) = ˆ m + , ( ⊕ ) ,p ( q j ) -ˆ m -, ( ⊕ ) ,p ( q j ).

**Feedback**:
Step 9 indicates bootstrap processes should use multiplier-weighted residuals, but Step 11 defines Ĝ_{R3D,b} using m̂_{±}, which are computed in Step 2 outside the bootstrap loop. Consequently, Ĝ_{R3D,b} is identical for all b, making the bootstrap distribution degenerate. It would be helpful to redefine Step 11 so that Ĝ_{R3D,b} incorporates the bootstrap estimates m̂*_{b} generated from the weighted residuals in Step 9, ensuring variation across b.

---

### 19. Confidence Band Center Depends on Bootstrap Iteration

**Status**: [Pending]

**Quote**:
> 14: Construct uniform bands: [ ˆ G R3D ,b ( q ) ± ( √ nh ) -1 ˆ c B n ( a, b ; λ )] for q ∈ T ∗

**Feedback**:
In Step 14, the confidence band is centered at Ĝ_{R3D,b}(q), which varies by bootstrap iteration b. Standard practice centers bands on the original estimator τ̂(q), not a bootstrap replicate. Additionally, Step 13 defines the critical value with b as an argument while aggregating over b. Readers might note that the critical value should be denoted ĉ_{B_n}(λ) and the band center should be the fixed estimate m̂₊(q) - m̂₋(q).

---

### 20. Undefined Prime Notation in Critical Value Construction

**Status**: [Pending]

**Quote**:
> where the critical values can be constructed by taking the (1 -λ )-th quantiles of { max q ∈ [ q,q ] ∣ ∣ ∣ ˆ G R / F3D ′ ( q ) ∣ ∣ ∣ } B b =1

**Feedback**:
The notation Ĝ_{R/F3D}'(q) is used here but was not defined in Algorithm 1, which uses Ĝ_{R3D,b}(q). It is not clear if the prime denotes a derivative, a bootstrap replicate, or a typo. To avoid ambiguity, it would be helpful to align this notation with Algorithm 1 (e.g., using Ĝ_{R3D,b}(q)) or explicitly define the transformation indicated by the prime symbol.

---
