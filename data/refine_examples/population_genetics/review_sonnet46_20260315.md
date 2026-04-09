# Inference in molecular population genetics

**Date**: 03/16/2026
**Domain**: statistics/computational_statistics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a new importance sampling (IS) scheme, Q_θ^SD, for estimating the likelihood surface of the population-scaled mutation rate θ under the Kingman coalescent with general mutation models. The proposal distribution is constructed by approximating the true conditional sampling distribution π(·|A_n) via a closed-form approximation π̂, derived from a particle representation of the Fleming–Viot diffusion. The method is compared empirically against existing IS (Griffiths–Tavaré) and MCMC (Fluctuate, micsat) approaches on several small population genetics datasets, with reported efficiency gains of several orders of magnitude in constrained settings such as the infinite-sites model.

Below are the most important issues identified by the review panel.

**Finite Variance of Importance Weights Is Unproven in the Main Application Settings**

Section 6.4 explicitly acknowledges that the authors could not prove finiteness of the variance of the IS weights under Q_θ^SD except for the infinite-sites model, where the number of possible histories is finite. This is a fundamental gap: without finite variance, the central limit theorem invoked throughout Section 5 to justify standard error calculations does not apply, and the reported standard errors in Table 1 and Figures 2–7 may severely underestimate true uncertainty. The paper simultaneously warns about this problem—noting that sample variance can severely underestimate true variance, as observed for the Griffiths–Tavaré scheme at θ=15—and continues to report standard errors as if they were reliable across all examples. The proposed diagnostic of fitting a generalized Pareto distribution to the weight tail is described only as 'promising on initial investigation' and is never actually applied to any of the reported examples. It would be helpful to either derive sufficient conditions on the mutation model and sample size under which finite variance holds for Q_θ^SD, or to apply the extreme-value diagnostic systematically to each example, clearly demarcating which reported standard errors are trustworthy and which are not.

**Approximation Quality of π̂ Relative to π Is Uncharacterized Outside Special Cases**

The entire IS scheme rests on substituting the tractable approximation π̂(·|A_n) for the intractable true conditional sampling distribution π(·|A_n). Proposition 1 establishes exactness only for parent-independent mutation (PIM) and for n=1 with reversible P, but provides no quantitative bound on the approximation error ‖π̂(·|A_n) − π(·|A_n)‖ in the general case, nor any analysis of how this error propagates into IS weight variance. For the stepwise microsatellite and two-nucleotide sequence models that constitute the main applications, the approximation is further degraded by a Gaussian quadrature step in Appendix A using only s=4 quadrature points, which the paper itself describes as 'rather rough' in some cases. The efficiency gains of several orders of magnitude are therefore empirically demonstrated only on a small set of examples and cannot be guaranteed to persist for different mutation matrices, larger samples, or higher mutation rates. It would be helpful to add at least an empirical characterization—for example, by comparing π̂ against numerically computed π for small examples—of how approximation quality degrades as a function of θ, sample size, and departure from PIM, and to identify regimes where Q_θ^SD might degrade or fail.

**Driving-Value Dependence and Its Effect on the Likelihood Surface Are Not Quantified or Remedied**

The proposal distribution Q_θ^SD is optimized for a fixed driving value θ_0, and Section 6.1 acknowledges that IS methods based on a single driving value will tend to underestimate the relative likelihood for θ far from θ_0, producing an artificially peaked likelihood curve. The paper cites Stephens (1999) to establish that the Fluctuate/MCMC-I estimator has infinite variance for θ > 2θ_0 regardless of sample size n—a result disputed by Felsenstein in the discussion and supported only by a two-page conference abstract without a reproduced proof. Analogously, no conditions are derived for when Q_θ^SD's weights have infinite variance under the fixed-θ_0 estimator (equation 12), and no empirical demonstration confirms that the estimated likelihood surfaces in Figures 2–5 are stable across the full θ range shown. The examples in Section 5 appear to use well-chosen driving values in hindsight, and discussant Mau explicitly flags the absence of guidance on selecting θ_0. Bridge sampling is mentioned as a remedy in Section 6.1 but is not implemented in any example. It would be helpful to either implement bridge sampling in at least one example, or to provide a quantitative criterion—such as a bound on the coefficient of variation of weights as a function of |θ − θ_0|—that practitioners can use to select θ_0 and assess reliability of the resulting likelihood curve.

**Efficiency Comparisons Are Conducted on Small, Constrained Problems That Favor the Proposed IS Method**

All quantitative comparisons in Section 5 use very small samples (n ≤ 60 chromosomes, sequences of length 10–20 sites, at most 5 microsatellite loci) that the authors themselves describe as 'relatively small problems.' The paper argues in Section 6.1 that IS has an advantage in constrained settings with few possible tree topologies, yet the only larger and less-constrained example—the NSE microsatellite dataset (Section 5.4, n=60, 5 loci)—is precisely the case where micsat outperforms Q_θ^SD. The efficiency gains of 'several orders of magnitude' claimed in the abstract are thus demonstrated only in the regime most favorable to IS. No simulation study varies sample size, sequence length, or number of loci systematically to characterize where the crossover between IS and MCMC efficiency occurs, and no asymptotic argument or empirical scaling analysis addresses how weight variance grows with problem dimension. Readers might note that the efficiency ordering between IS and MCMC methods could reverse for the genome-scale datasets the paper motivates in its introduction, and it would be helpful to include at least one moderately large example or an informal scaling analysis to bound the practical scope of the claimed efficiency improvements.

**MCMC Convergence Assessment for Competing Methods Is Insufficient to Support Comparative Claims**

The paper's comparisons with Fluctuate and micsat rely on running those programs 'according to published general guidelines,' and no formal convergence diagnostics—such as Gelman–Rubin R̂ across independent chains or effective sample size per unit time—are reported for any MCMC run. For Fluctuate in Figure 2(c), chains of 50,000 and 1,000,000 iterations give different and apparently biased likelihood surfaces, attributed to poor mixing; however, discussants Kuhner and Beerli demonstrate that combining 10 runs with different driving values in MIGRATE recovers agreement with Q_θ^SD (Figure 9), suggesting the comparison in Figure 2(c) reflects a suboptimal rather than a representative MCMC implementation. The comparison is therefore potentially unfair to the MCMC competitors. It would be helpful to either report formal convergence diagnostics for all MCMC comparisons, or to explicitly state that comparisons are made at equal computational cost rather than at convergence, and to include the multi-run MIGRATE result as a baseline so that efficiency claims reflect optimized rather than default implementations of competing methods.

**Model Assumptions Are Rarely Satisfied in Practice and Their Violation Is Not Assessed**

The entire framework assumes the standard neutral Kingman coalescent with constant population size, no recombination within the locus, exchangeable offspring, and a known mutation matrix P. The practical consequences of violating these assumptions for likelihood estimates and parameter inferences are never examined in the paper. Notably, the NSE Y-chromosome data (Section 5.4) come from three geographically structured populations (Nigeria, Sardinia, East Anglia), directly violating the panmixia assumption; the stepwise mutation model truncated to {0,...,19} repeats introduces boundary artifacts whose effect on the likelihood is unquantified; and P is treated as known throughout, even though discussant D.A. Stephens correctly notes that P typically contains unknown evolutionary parameters. The authors' reply concedes that 'robustness of likelihood procedures…is likely to be a serious problem,' but this admission appears only in the discussion response rather than in the paper itself. Additionally, the infinite-sites IS scheme in Section 5.5 is constructed by analogy with Proposition 2 rather than derived from Theorem 1, and the mutation process is noted to be non-reversible, invalidating the property underpinning the π̂ ≈ π approximation for n=1. It would be helpful to include at least a sensitivity analysis showing how estimated likelihood surfaces shift under moderate model misspecification, and to clearly delineate the infinite-sites extension as a heuristic with unknown theoretical guarantees.

**Status**: [Pending]

---

## Detailed Comments (16)

### 1. Topology Count Formula Counts Labeled Histories, Not Topologies

**Status**: [Pending]

**Quote**:
> For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
The formula n!(n-1)!/2^{n-1} counts labeled histories (ranked topologies), not distinct tree topologies. For n=4: n!(n-1)!/2^{n-1} = 24·6/8 = 18, which matches the number of labeled histories, while the number of distinct rooted labeled topologies for n=4 is 15. It would be helpful to rewrite as 'there are n!(n-1)!/2^{n-1} different possible labeled histories (ranked topologies) for the underlying trees' to avoid conflating the two counts, since the distinction matters for interpreting the combinatorial complexity argument.

---

### 2. Efficiency Claim 'Several Orders of Magnitude' Overstated in Abstract

**Status**: [Pending]

**Quote**:
> Our approach substantially outperforms existing IS algorithms, with efficiency typically improved by several orders of magnitude. The new method also compares favourably with existing MCMC methods in some problems, and less favourably in others

**Feedback**:
The abstract claims efficiency is 'typically improved by several orders of magnitude,' but Section 5.4 explicitly shows that for the NSE microsatellite dataset (n=60, 5 loci) micsat outperforms Q_θ^SD. The several-orders-of-magnitude gains are demonstrated only in small, constrained problems. Using 'typically' while the one larger real-data example shows the opposite ordering misrepresents the scope of the evidence. It would be helpful to rewrite as 'with efficiency improved by several orders of magnitude in the constrained problems examined, though gains vary substantially with problem size and mutation model,' and to clarify that the orders-of-magnitude claim applies to the IS-vs.-IS (Griffiths–Tavaré) comparison rather than IS-vs.-MCMC.

---

### 3. Stopping Rule in Algorithm 1 May Silently Discard Mutations at Count n

**Status**: [Pending]

**Quote**:
> Step 3: if there are fewer than $n + 1$ lines in the ancestry return to step 2. Otherwise go back to the last time at which there were $n$ lines in the ancestry and stop.

**Feedback**:
The stopping rule triggers when the line count reaches n+1 and then returns to the last state with n lines. Since mutations do not change the line count, consecutive mutation events can occur at count n before the next split triggers the stop. The algorithm as written discards all mutation events at count n after the last split, because it goes back to 'the last time at which there were n lines.' If such mutations are discarded, the marginal distribution of H_0 may differ from the claimed sampling distribution π_θ(A_n). It would be helpful to add a clarifying sentence after Step 3 explaining whether mutations at count n between the last split and the stopping time are incorporated or discarded, and why the resulting distribution is correct.

---

### 4. Unqualified Claim That Reusing Single IS Function Is More Efficient

**Status**: [Pending]

**Quote**:
> Expression (9) could be used to estimate the likelihood independently for many different values of $\theta$, using samples from a different IS function $Q_{\theta}$ for each value of $\theta$. However, it appears to be more efficient to reuse samples from a single IS function.

**Feedback**:
The claim that reusing samples from a single IS function Q_{θ_0} is more efficient is stated without qualification, but the paper itself acknowledges in Section 6.1 that IS weights can have infinite variance for θ far from θ_0. The efficiency comparison depends critically on how far θ ranges from θ_0 and the tail behavior of the weight distribution. It would be helpful to rewrite as 'when the likelihood surface is evaluated over a narrow range of θ near θ_0, it can be more efficient to reuse samples from a single IS function Q_{θ_0}; for θ far from θ_0 the variance of estimator (12) may be substantially larger or even infinite (see Section 6.1),' since the unqualified claim is contradicted by the paper's own later analysis.

---

### 5. Point Estimate Discrepancy at θ=15.0 for Q_θ^SD Understates Severity of Bias

**Status**: [Pending]

**Quote**:
> In contrast, between the long and short runs for $Q_{\theta}^{\mathrm{SD}}$ with $\theta = 15.0,$ the change in the estimated standard error is less than a factor of 2, indicating that (at least for the short run) the standard error severely underestimates the standard deviation in this case.

**Feedback**:
The text focuses on the SE ratio but does not note that the point estimates themselves are also substantially inconsistent. From Table 1, the short run gives 4.74 × 10⁻¹² and the long run gives 5.37 × 10⁻¹², a difference of 0.63 × 10⁻¹². With the long-run SE of 8.08 × 10⁻¹⁴, the two estimates differ by approximately 7.8 long-run standard errors—a statistically significant discrepancy demonstrating that the short-run point estimate is biased downward, not merely imprecise. It would be helpful to note that 'the point estimates themselves differ by approximately 0.63 × 10⁻¹² (about 7.8 long-run standard errors), confirming that the short-run estimate is substantially biased downward, not merely imprecise.'

---

### 6. Factor √500 ≈ 22 vs. Empirical Factor of 17 at θ=10.0 Left Unexplained

**Status**: [Pending]

**Quote**:
> For $\theta = 2.0$ and $\theta = 10.0$ the changes in the estimated standard error (by factors of about 21 and 17 respectively) between the long and short runs for $Q_{\theta}^{\mathrm{SD}}$ suggest that these standard errors are being estimated reasonably accurately.

**Feedback**:
The theoretical factor is √(10⁷/20000) = √500 ≈ 22.36. For θ=2.0 the empirical ratio ≈ 21 is close to 22, but for θ=10.0 the ratio ≈ 17 deviates by about 24%. The paper characterizes both as 'reasonably accurate,' but a 24% shortfall may itself indicate mild weight-distribution skewness at θ=10.0—consistent with the observation that only 9 of 20,000 GT histories contributed at this θ value. It would be helpful to note that 'the somewhat larger shortfall at θ=10.0 (factor 17 vs. expected 22) may reflect mild skewness in the weight distribution at this parameter value, consistent with the near-failure of the GT estimator there,' rather than treating both cases as equally well-behaved.

---

### 7. IS Underestimation Mechanism Conflates Skewness with Infinite Variance

**Status**: [Pending]

**Quote**:
> Since the IS function which these MCMC methods use is most efficient (in fact optimal) at $\theta_{0},$ and tends to become less efficient for $\theta$ away from $\theta_{0},$ the distribution of the importance weights tends to be more skewed for $\theta$ away from the $\theta_{0}.$ As a result such methods will tend to underestimate the relative likelihood away from $\theta_{0},$ leading to an estimated curve which is artificially peaked about this driving value

**Feedback**:
The IS estimator (equation 8) is unbiased for any fixed M as long as variance is finite—skewness alone does not imply systematic downward bias. The actual mechanism producing the artificially peaked curve is that when variance is infinite (or very large) for θ far from θ_0, the sample mean is dominated by rare large weights almost never observed in a finite run, producing a finite-sample bias. It would be helpful to rewrite 'the distribution of the importance weights tends to be more skewed...As a result such methods will tend to underestimate' as 'the variance of the importance weights tends to increase for θ away from θ_0, and when this variance is very large or infinite, the finite-sample estimator will tend to underestimate,' because skewness is a symptom, not the cause, of the underestimation.

---

### 8. Infinite Variance Claim for All n Lacks Derivation and May Contradict Coalescent Structure

**Status**: [Pending]

**Quote**:
> The result of Stephens (1999) can be extended to show that the variance of the IS weights for the Fluctuate scheme (Kuhner et al. 1998) is infinite for $\theta > 2\theta_{0},$ regardless of the value of the sample size $n.$

**Feedback**:
Under Kingman's coalescent, the IS weight involves a product over coalescence intervals: for k lineages, the interval T_k ~ Exp(k(k-1)/2). The second moment E[W²] requires E[exp(c_k T_k)], which diverges only when c_k ≥ k(k-1)/2. Since this threshold grows as k², the condition on (θ − θ_0) for divergence becomes more stringent as k (and hence n) increases, suggesting the threshold may depend on n in a way that contradicts the 'regardless of n' assertion—consistent with Felsenstein's empirical observations. It would be helpful to add a derivation of the extension from n=2 to general n, because the claim is unsubstantiated and the coalescent weight structure suggests the threshold condition may tighten with n.

---

### 9. Standard Errors Reported Despite Acknowledged CLT Inapplicability

**Status**: [Pending]

**Quote**:
> However, caution is necessary, as even assuming finite variance (which is not guaranteed) the distribution of the weights may be so highly skewed that, even for very large $M, \sigma^2$ is (with high probability) underestimated by $\hat{\sigma}^2,$ and/or the normal asymptotic theory does not apply. Despite this important caveat, we quote standard errors in some of our examples to allow a direct comparison with published estimates.

**Feedback**:
The authors explicitly acknowledge two compounding reliability problems: finite variance is not guaranteed (so the CLT foundation may be absent), and even when finite variance holds, sample variance systematically underestimates true variance under heavy-tailed weights. The proposed GPD diagnostic (Section 6.4) is described as 'promising on initial investigation' but is never applied to any example in Section 5. A blanket caveat followed by unrestricted reporting leaves readers unable to identify which specific table entries or figures are most affected. It would be helpful to add a sentence specifying which examples or parameter regimes are most susceptible to the underestimation problem so readers can identify which comparisons carry the greatest uncertainty.

---

### 10. CLT Applied to IS Estimator Without Clarifying Whether It Is Normalized or Unnormalized

**Status**: [Pending]

**Quote**:
> For the IS schemes, assuming that the distribution of the weights has finite variance $\sigma^2,$ then (by the central limit theorem) the estimator (8) is asymptotically normal with variance $\sigma^2 / M.$ A natural measure of the variability is then given by the standard error $\hat{\sigma} / \sqrt{M},$ where $\hat{\sigma}^2$ is the sample variance of the $M$ weights.

**Feedback**:
The formula σ²/M is correct for an unnormalized IS estimator (a simple sample mean of weights), but self-normalized (ratio) IS estimators have asymptotic variance requiring a delta-method expansion: Var(W_i f(x_i) − L̂ W_i)/M, not simply Var(W_i)/M. It is not clear from the text whether estimator (8) is normalized or unnormalized. It would be helpful to add a clarification after 'asymptotically normal with variance σ²/M' specifying which form is used, and if the estimator is a ratio estimator, to provide the corrected asymptotic variance formula.

---

### 11. Ventura Variance Reduction Factor Phrasing Is Ambiguous and Potentially Inverted

**Status**: [Pending]

**Quote**:
> Its asymptotic variance is $(1 - \rho_{\theta}^{2})^{-1}$ times smaller than that of expression (12), where typically $\rho_{\theta}^{2} = \mathrm{corr}^{2}\{l_{\theta}(\mathcal{H}^{(i)}), w_{\theta}^{\prime (i)}\}$ is large since $\hat{Q}_{\theta}\doteq Q_{\theta}^{\mathrm{SD}}$ implies $l_{\theta}(\mathcal{H}^{(i)})\propto w_{\theta}^{\prime (i)}.$

**Feedback**:
Standard control variate theory gives new variance = (1 − ρ²) × old variance, a reduction by factor (1 − ρ²) ∈ (0,1). Writing the new variance is '(1 − ρ²)⁻¹ times smaller' is ambiguous: if 'X times smaller' means new = old/X, then new = (1−ρ²)·old, which is correct; but if read as new = old·(1−ρ²)⁻¹, the variance would be larger. Since ρ² is described as 'large' (close to 1), (1−ρ²)⁻¹ >> 1, making the phrasing especially prone to misreading as a large increase. It would be helpful to rewrite as '$(1 - \rho_{\theta}^{2})$ times that of expression (12)' to unambiguously state the standard control variate reduction factor.

---

### 12. Conclusion That micsat Is More Accurate Is Unsupported by Reported Evidence

**Status**: [Pending]

**Quote**:
> There are small but noticeable differences in the relative likelihood curves obtained by using our method and micsat. Further investigation (more runs of each method) suggested that the curve obtained by using micsat is more accurate.

**Feedback**:
This conclusion is stated without any supporting evidence in the section. The 'further investigation' is not described, quantified, or shown in any figure or table. Fig. 5(c) shows the combined 2.5-million-sample IS curve alongside a single 10,000-sample micsat curve, but no long reference run from either method is presented as ground truth. Moreover, the IS estimate uses 500,000 samples per run while the micsat comparison uses only 10,000 samples, making the comparison asymmetric in computational effort. It would be helpful to rewrite as 'Further investigation suggested that the IS estimate has not fully converged for this larger dataset; a definitive comparison of accuracy would require a longer reference run from at least one method,' and to add the specific evidence from the 'further investigation.'

---

### 13. Computational Time Comparison Is Asymmetric: Nominal vs. Effective Sample Size

**Status**: [Pending]

**Quote**:
> A comparison of the accuracy and variability of the estimated relative likelihood surfaces, together with a consideration of the computer time required to produce these results (see the caption of Fig. 4), suggests that for this problem our IS method is considerably more efficient than micsat, although there are many ways in which our use of the MCMC scheme could be improved

**Feedback**:
The efficiency comparison in Fig. 4 is between 10,000 IS samples and 10,000 micsat posterior samples. However, IS produces weighted samples whose effective sample size (ESS) depends on weight variance, while micsat produces approximately unweighted posterior samples whose ESS depends on chain autocorrelation. The section does not report ESS for either method, so comparing '10,000 samples' conflates nominal and effective sample sizes. It would be helpful to rewrite the efficiency claim to specify that the comparison is at equal nominal sample size and note that ESS-normalized efficiency could differ substantially; alternatively, report the ESS for the IS runs shown in Fig. 4(b).

---

### 14. Rejection Control Conflated with Biased Discarding Strategy

**Status**: [Pending]

**Quote**:
> It may then be fruitful to apply the rejection control ideas of Liu et al. (1999), in which unpromising trees would be discarded before reaching the MRCA, with appropriate modifications of the weights of the undiscarded trees. (This is a more sophisticated version of the strategy of discarding trees with too many mutations which was used by Griffiths and Tavaré (1994a) and Nielsen (1997).)

**Feedback**:
In Liu et al. (1999) rejection control, a partial path is retained with probability proportional to its estimated future weight and the surviving particle's weight is inflated by the reciprocal of that retention probability, preserving unbiasedness. By contrast, Griffiths and Tavaré (1994a) and Nielsen (1997) discard trees without any compensating weight adjustment, introducing bias. These are not the same operation at different levels of sophistication: one is an unbiased variance-reduction technique and the other is a biased approximation. It would be helpful to rewrite as 'Unlike the strategy of discarding trees with too many mutations used by Griffiths and Tavaré (1994a) and Nielsen (1997)—which introduces bias by dropping trees without compensating weight adjustments—rejection control preserves unbiasedness by inflating the weights of retained trees by the reciprocal of their retention probability.'

---

### 15. Effective Sample Size Cited as Diagnostic Despite Sharing the Same Failure Mode as Sample Variance

**Status**: [Pending]

**Quote**:
> Some sensible procedures include monitoring (graphically for example) the mean and variance of the importance weights, the effective sample size (Kong et al. 1994) and the relative size of the maximum weight. However, all these methods will suffer if the sample variance of the importance weights substantially underestimates the variance of the underlying distribution

**Feedback**:
The ESS formula of Kong et al. (1994) is ESS = (Σw_i)² / Σw_i², which is itself a function of the sample variance of the normalized weights. Consequently, ESS inherits exactly the same failure mode the authors immediately identify: if the sample variance underestimates the true variance due to a heavy tail, ESS will overestimate the true effective sample size. Listing ESS as a 'sensible procedure' without flagging that it is subject to the same limitation as the variance monitor is potentially misleading. It would be helpful to rewrite 'the effective sample size (Kong et al. 1994)' as 'the effective sample size (Kong et al. 1994), which is itself based on the sample variance of the weights and therefore shares the same limitation described below.'

---

### 16. Consistency of IS Estimator Requires Full-Support Condition Not Stated for Quadrature Approximation

**Status**: [Pending]

**Quote**:
> Although in some cases the approximation to $\hat{\pi}(\cdot|\cdot)$ obtained through this procedure is rather rough, we note that in any case the IS function defined by this approximation to $\hat{\pi}(\cdot|\cdot)$ is a valid IS function in its own right, and so leads to an estimator (9) which is consistent.

**Feedback**:
Consistency of IS estimators requires that the approximate proposal assign positive probability to every history with positive probability under the true distribution. Equation (33) replaces the exact integral with a finite weighted sum at s=4 quadrature points; if for some (α, β) pair the resulting approximate F matrices yield a zero or near-zero entry where the exact F is strictly positive, the proposal can assign zero weight to certain chromosome types, violating the support condition and producing a biased rather than merely high-variance estimator. The paper acknowledges the approximation can be 'rather rough' but does not verify the support condition. It would be helpful to rewrite the consistency claim as 'leads to an estimator (9) which is consistent, provided that the approximate proposal assigns positive probability to every history with positive probability under the true distribution—a condition that should be verified for each application.'

---
