# Inference in molecular population genetics

**Date**: 03/06/2026
**Domain**: statistics/computational_statistics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Finite Variance of Importance Weights Is Unproven and Standard Errors May Be Unreliable**

The authors explicitly acknowledge in Section 6.4 that they cannot prove finiteness of the variance of the importance weights for Q_θ^SD except in the special case of the infinite sites model. This is a fundamental gap: without finite variance, the central limit theorem justification for the standard errors reported throughout Section 5 (Tables 1, Figs 2–7) does not apply, and the quoted standard errors may severely underestimate true uncertainty. The paper demonstrates this problem empirically for Q_θ^GT at θ=15 in Table 1, and Fig. 12 shows dramatic discontinuities in the running mean and standard deviation for Q_θ^SD at θ=15, confirming that heavy-tailed weight distributions can afflict the new method as well. The paper does not provide empirical evidence of tail behavior (e.g., tail-index estimates or log-log plots of weight distributions) for the finite-alleles models in Sections 5.2–5.4. It would be helpful to either derive sufficient conditions on θ, n, and the mutation model under which finite variance is guaranteed, or to add an empirical assessment of weight-distribution tail behavior for each example—for instance by fitting a generalized Pareto distribution—and to flag explicitly which reported standard errors may be unreliable.

**Approximation Quality of π̂ Relative to π Is Unquantified and Compounded by Quadrature Error**

The efficiency argument for Q_θ^SD rests entirely on π̂(·|A_n) being a good approximation to the true conditional sampling distribution π(·|A_n), yet Proposition 1 establishes exactness only for parent-independent mutation (PIM) and for n=1 with reversible P. For all other cases—including the stepwise microsatellite model and the sequence model of Section 5.2—no bound on the approximation error ‖π̂(·|A_n) − π(·|A_n)‖ is provided analytically or empirically, and no analysis shows how the approximation degrades as θ increases, n grows, or P departs from PIM. This approximation is further degraded by the Gaussian quadrature used in Appendix A, which employs only s=4 quadrature points; the authors themselves note that 'in some cases the approximation to π̂(·|·) obtained through this procedure is rather rough,' yet no sensitivity analysis varying s is provided. Because the IS estimator's variance depends directly on how close Q_θ^SD is to the optimal Q_θ^*, an unquantified approximation error means the reported efficiency gains cannot be attributed specifically to the theoretical construction versus the quadrature approximation. It would be helpful to report the approximation error of π̂ versus π for the specific models tested, assess sensitivity of likelihood estimates to the number of quadrature points, and characterize when the approximation is expected to be reliable.

**Simulation Benchmarks Are Too Narrow to Support General Efficiency Claims**

The paper's central claim that Q_θ^SD 'typically' improves efficiency by 'several orders of magnitude' is supported by a small number of examples: one simulated sequence dataset (n=10, Section 5.2), one likelihood surface example (n=50, Section 5.3), one simulated microsatellite sample (n=9, Section 5.4), and one infinite sites dataset (Section 5.5). No systematic exploration of how efficiency gains vary with θ, n, or departure from PIM is presented. The 'several orders of magnitude' characterization is drawn from a regime where Q_θ^GT fails catastrophically (θ=10, 15), making the comparison favorable by construction; at θ=2 the two methods perform comparably. The driving value θ_0 was chosen close to the true θ in all examples, further favoring IS methods. Critically, the θ=15 case in Table 1 shows that Q_θ^SD can itself fail badly—with standard error underestimated by nearly two orders of magnitude using 20,000 samples—yet this is not reflected in the summary efficiency claim. It would be helpful to present a grid of results over (θ, n) values, including cases where both methods perform adequately and cases where the driving value is deliberately misspecified, to give a calibrated picture of when efficiency gains are modest versus dramatic.

**Driving-Value Dependence and Reference Likelihood Reliability Are Inadequately Addressed**

The IS estimator uses a single driving value θ_0 for all estimates of the likelihood surface (equation 12), and Section 6.1 acknowledges that this causes the estimated curve to be 'artificially peaked' about θ_0. The paper cites Stephens (1999) showing infinite variance for the Fluctuate scheme when θ > 2θ_0, but does not establish whether an analogous variance inflation affects Q_θ^SD at extreme θ/θ_0 ratios, nor does it provide guidance on choosing θ_0 or on how far from θ_0 the likelihood surface estimates remain reliable. Discussant Mau explicitly raises the absence of such guidance, and the authors' reply acknowledges the issue without resolving it. Compounding this, the paper treats estimates from 10^7 samples of Q_θ^SD as ground-truth reference values, yet the factor-of-less-than-2 reduction in standard error between 20,000 and 10^7 samples at θ=15 demonstrates that even the long-run estimates may be unreliable as benchmarks. Bridge sampling is mentioned as a remedy in Section 6.1 but is not implemented or evaluated. It would be helpful to state explicitly the range of θ/θ_0 ratios for which Q_θ^SD has demonstrably finite variance, to validate reference likelihoods against an independent method for small cases, and to demonstrate bridge sampling on at least one example with deliberately misspecified θ_0.

**MCMC Comparisons Lack Rigorous Convergence Verification and May Reflect Suboptimal Tuning**

The comparisons with Fluctuate (Section 5.3) and micsat (Section 5.4) rely on MCMC runs whose convergence is not rigorously verified: no effective sample sizes, Gelman-Rubin diagnostics, or multiple-chain comparisons are reported. Discussants Kuhner and Beerli independently show that combining 10 runs with different driving values substantially improves the MCMC result (Fig. 9), a strategy the paper does not incorporate into its comparison. For the NSE microsatellite data (Section 5.4), the authors concede that 'further investigation suggested that the curve obtained by using micsat is more accurate' than their own IS estimate—a concession that is not adequately explained and that complicates the efficiency narrative. The informal distinction between 'constrained' problems (where IS is claimed to be superior) and 'less constrained' problems (where MCMC has an advantage) is never operationalized into a criterion a practitioner could apply before choosing a method. It would be helpful to standardize MCMC comparisons using multiple independent chains with published convergence criteria, to acknowledge that IS advantages in some examples may partly reflect suboptimal MCMC tuning, and to provide a formal or empirical characterization of the constrained/unconstrained distinction.

**Model Assumptions Are Presented Without Assessment of Robustness or Bias Under Violation**

The entire inferential framework rests on the Kingman coalescent under neutrality, constant population size, no recombination, and a fully specified mutation matrix P. These assumptions are introduced in Section 2 as simplifications but their consequences for validity of θ estimates under misspecification are not examined anywhere in the main paper. The real-data application (NSE Y-chromosome microsatellite data, Section 5.4) involves human populations from Nigeria, Sardinia, and East Anglia, for which population structure, demographic expansion, and possible selection are almost certainly present; the paper presents likelihood surfaces for θ on this dataset without any assessment of interpretability under model misspecification. The authors' reply to discussant Stephens acknowledges that 'robustness is likely to be a serious problem' for real genetics data, yet this caveat appears only in the reply. Agreement between Q_θ^SD and micsat on the NSE data confirms only computational consistency, not inferential validity, if the underlying model is misspecified. It would be helpful to add a paragraph in Section 6 identifying the most critical assumptions, describing qualitatively how violations would bias θ estimates (e.g., population expansion inflating θ̂; positive selection at linked sites reducing it), and pointing to diagnostics or robustness checks that practitioners should apply.

**Single-population constant-size coalescent applied to geographically structured NSE data**

Assumption: The coalescent model underlying all inference assumes a single, randomly mating population of constant size N, with exchangeable sampling from stationarity (Sections 2 and 3). Data: The NSE dataset consists of 60 Y-chromosome haplotypes drawn from three geographically and genetically distinct populations — Nigeria, Sardinia, and East Anglia. These subpopulations have different effective sizes, migration histories, and demographic trajectories, violating both the constant-size and panmictic assumptions. Consequence: Applying a single-θ, single-population model to structured data conflates within-population coalescence times with between-population divergence times. The resulting θ estimate absorbs both mutation rate and population structure effects, and the likelihood surface reflects a composite parameter rather than a clean estimate of scaled mutation rate. The paper follows Wilson and Balding (1998) in this treatment but offers no sensitivity analysis or acknowledgment of the potential bias. It would be helpful to note explicitly that the θ estimated from the NSE data should be interpreted cautiously as a population-average quantity, and readers might note that a structured-coalescent extension (as mentioned in Section 6.2 for future work) would be the appropriate model for this dataset.

**Standard errors derived from IS weight variance are reported despite unproven finite-variance property**

Assumption: The asymptotic normality argument used to justify reporting standard errors as σ̂/√M (Section 5, opening paragraphs) requires that the distribution of importance weights has finite variance σ². Data/implementation: The paper explicitly states it cannot prove finite variance of the weights for the general case — only for the infinite sites model where the history space is finite (Section 6.4). In Table 1 at θ=15, the standard error from 20,000 samples of Q^SD severely underestimates the true variability (the ratio of standard errors between the long and short runs changes by less than a factor of 2 rather than the expected √500 ≈ 22). Consequence: In cases where the weight distribution has a heavy tail, the reported standard errors can give a misleadingly precise impression of accuracy, as the paper itself demonstrates for Q^GT at θ=15 but which may also affect Q^SD in harder problems. The proposed generalized Pareto diagnostic (Section 6.4) is described as promising but not actually applied to any of the reported examples. It would be helpful to apply the Pareto tail diagnostic to at least one example, or to flag all reported standard errors with the caveat that they may be underestimates when the effective sample size is small relative to M.

**Status**: [Pending]

---

## Detailed Comments (25)

### 1. Efficiency Claim 'Several Orders of Magnitude' Overstated for Full Parameter Range

**Status**: [Pending]

**Quote**:
> Our approach substantially outperforms existing IS algorithms, with efficiency typically improved by several orders of magnitude.

**Feedback**:
The paper's own Table 1 shows that at θ=2 both methods perform comparably (standard errors of 1.35×10⁻⁶ vs 4.01×10⁻⁸, roughly a factor of 30, not 'several orders of magnitude'), while the dramatic gains appear only at θ=10 and θ=15 where Q_θ^GT fails catastrophically. The word 'typically' implies this is the common case across the parameter space tested, but the paper's examples are concentrated in the high-θ regime where the baseline breaks down. A more accurate characterization would restrict the 'several orders of magnitude' claim to high-mutation-rate regimes and note that at lower θ the methods are more comparable.

---

### 2. NSE Accuracy Concession Contradicts Efficiency Narrative Without Mechanistic Explanation

**Status**: [Pending]

**Quote**:
> Further investigation (more runs of each method) suggested that the curve obtained by using `micsat` is more accurate.

**Feedback**:
This concession — that micsat outperforms Q_θ^SD on the paper's only real-data example even with 2.5 million IS samples versus 10,000 MCMC samples — directly contradicts the efficiency narrative established for the simulated microsatellite data. No mechanistic explanation is offered for the reversal. It is not clear whether the failure reflects degraded quadrature approximation quality in the 5-locus product space, a poorly chosen driving value, or some other factor. It would be helpful to append a mechanistic explanation noting which aspect of the 5-locus NSE problem causes the IS approach to underperform.

---

### 3. Dual Use of n in Transition Probability Equation (1) Creates Notational Collision

**Status**: [Pending]

**Quote**:
> where $n$ is the number of chromosomes in $H_{i-1}$ and $n_{\alpha}$ is the number of chromosomes of type $\alpha$ in $H_{i-1}$.

**Feedback**:
Throughout the paper n denotes the fixed sample size, but equation (1) redefines n locally as the current chromosome count in H_{i-1}, which ranges from 1 to n. This creates a direct collision: substituting n=1 into the split probability gives (n_α/1)×((1−1)/(1−1+θ))=0, assigning zero probability to the mandatory first split from the MRCA. Algorithm 1 already uses k for the current line count; replacing n and n_α in equation (1) with k and k_α respectively would eliminate the collision and make clear that the formula applies for k≥2.

---

### 4. Topology Count Formula Counts Labeled Histories, Not Topologies

**Status**: [Pending]

**Quote**:
> there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees

**Feedback**:
The formula n!(n−1)!/2^{n−1} counts labeled histories (ordered sequences of coalescence events), not distinct tree topologies. For n=4: labeled histories = 4!×3!/2³ = 24×6/8 = 18, while distinct rooted labeled topologies = 15. These differ, confirming the formula counts ranked histories. The paper's use of 'topologies' is therefore imprecise and may mislead readers about the combinatorial structure of the problem. Rewrite as 'there are n!(n−1)!/2^{n−1} different possible labeled histories (ranked topologies) for the underlying trees.'

---

### 5. Swapped Geometric Factors in Proof of Property (c) of Proposition 1

**Status**: [Pending]

**Quote**:
> \hat {\pi} (\beta | A _ {n}) = \sum_ {\alpha \in E} \sum_ {m = 0} ^ {\infty} \frac {n _ {\alpha}}{n} \left(\frac {\theta}{n + \theta}\right) ^ {m} \frac {n}{n + \theta} (P ^ {m}) _ {\alpha \beta}. \tag {17}

**Feedback**:
Definition 1 writes the geometric weights as (θ/(n+θ))^m × (n/(n+θ)), i.e., continuation probability θ/(n+θ) raised to power m, times stopping probability n/(n+θ). The proof of property (c) rewrites this as (n/(n+θ))^m × (θ/(n+θ)), swapping the two factors. Setting λ_n = θ/(n+θ), the correct expansion is (1−λ_n)(λ_n P)^m = (n/(n+θ))(θ/(n+θ))^m P^m, consistent with Definition 1. The final result M^(n) = (1−λ_n)(I−λ_n P)^{−1} is correct, but the intermediate displayed line in the proof has the two factors transposed relative to equation (17).

---

### 6. Proof of Proposition 2 Applies Equation (22) Without Stating the Substituted Sample Size

**Status**: [Pending]

**Quote**:
> From equation (22) we have
> 
> $$
> 1 = \sum_{\beta \in E} \frac{\hat{\pi}(\beta | H_i - \alpha)}{\hat{\pi}(\alpha | H_i - \alpha)} \left( \frac{\theta}{n - 1 + \theta} P_{\beta \alpha} + \frac{n_{\alpha} - 1}{n - 1 + \theta} \right).

**Feedback**:
Equation (22) is stated for a configuration with n chromosomes and n_α of type α. In the proof of Proposition 2 it is applied to H_i minus α, which has n−1 chromosomes with n_α−1 of type α, yielding denominators n−1+θ and n_α−1. The paper writes 'From equation (22) we have' without stating that the substitution n→n−1 and n_α→n_α−1 is being made, so readers expecting n and n_α to refer to H_i will be confused. Adding the clarification 'applying equation (22) to H_i minus α, which has n−1 chromosomes with n_α−1 of type α' before the displayed equation would make the substitution explicit.

---

### 7. Systematic Underestimation Claim for Finite-Variance Skewed Weights Is Imprecise

**Status**: [Pending]

**Quote**:
> even assuming finite variance (which is not guaranteed) the distribution of the weights may be so highly skewed that, even for very large $M$, $\sigma^2$ is (with high probability) underestimated by $\hat{\sigma}^2$, and/or the normal asymptotic theory does not apply.

**Feedback**:
When weights have finite variance σ², the sample variance σ̂² is a consistent estimator of σ² by the law of large numbers (requiring only E[w²]<∞), so for large M, σ̂² does NOT systematically underestimate σ² with high probability — the bias vanishes asymptotically. The genuine concern is that convergence of σ̂² to σ² is slow when E[w⁴] is large or infinite, making the standard error unreliable at practical sample sizes. The claim as written conflates finite-sample slow convergence with a persistent asymptotic bias. Rewrite 'even for very large M, σ² is (with high probability) underestimated by σ̂²' as 'even for moderately large M, σ̂² may converge slowly to σ² when the fourth moment of the weights is large, causing the standard error to be unreliable for practical sample sizes.'

---

### 8. Factor of 17 vs Expected 22 at θ=10 Treated as 'Reasonably Accurate' Without Qualification

**Status**: [Pending]

**Quote**:
> For $\theta = 2.0$ and $\theta = 10.0$ the changes in the estimated standard error (by factors of about 21 and 17 respectively) between the long and short runs for $Q_{\theta}^{\mathrm{SD}}$ suggest that these standard errors are being estimated reasonably accurately.

**Feedback**:
The expected reduction factor is √(10⁷/20000) = √500 ≈ 22.4. For θ=2 the observed factor of ~21 is within 6% of expectation. For θ=10, from Table 1: 2.53×10⁻¹¹/1.50×10⁻¹² ≈ 16.9, which is about 25% below the expected 22.4 — a non-trivial departure that could indicate mild weight-distribution skewness even at θ=10. The text treats both cases identically as 'reasonably accurate,' but the θ=10 shortfall is at least suggestive of some tail behavior. The text should note that the θ=10 factor falls ~25% short of √500 ≈ 22 and qualify 'reasonably accurately' with a caveat that mild skewness may already be present at this value.

---

### 9. Q_θ^SD Point Estimates at θ=15 Are Statistically Inconsistent Across Run Lengths

**Status**: [Pending]

**Quote**:
> |  15.0 | 2.41 × 10⁻¹⁹ (1.89 × 10⁻¹⁹) | 4.74 × 10⁻¹² (1.39 × 10⁻¹³) | 5.37 × 10⁻¹² (8.08 × 10⁻¹⁴)  |

**Feedback**:
The 20,000-sample Q_θ^SD estimate (4.74×10⁻¹²) and the 10⁷-sample estimate (5.37×10⁻¹²) differ by 6.3×10⁻¹³. Dividing by the long-run standard error of 8.08×10⁻¹⁴ gives a discrepancy of approximately 7.8 long-run standard errors. The text acknowledges that the short-run standard error is unreliable at θ=15, but does not note that the point estimates themselves are discrepant by several long-run standard errors, confirming that the short-run estimate is not only imprecisely measured but also biased downward due to missed large weights. Adding a sentence noting this discrepancy would strengthen the diagnostic argument.

---

### 10. sqrt(1000) Approximated as 32 Rather Than 31.6

**Status**: [Pending]

**Quote**:
> the standard errors were smaller by about a factor of 31, suggesting that the standard errors in the smaller sample are accurately reflecting the standard deviation of the weights (they should in theory be reduced by a factor of $\sqrt{1000} \approx 32$).

**Feedback**:
√1000 = 10√10 = 31.623, which rounds to 32 only by rounding up. In context, the authors use the proximity of the observed factor (31) to the theoretical value as a validation argument. Writing ≈32 makes the agreement appear slightly worse (31 vs 32, ~3% discrepancy) when in fact the agreement is excellent (31 vs 31.6, ~2% discrepancy). Rewrite '√1000 ≈ 32' as '√1000 ≈ 31.6' for accuracy.

---

### 11. PIM Matrix in Equation (29) Makes Comparison Best-Case for Q_θ^SD Without Disclosure

**Status**: [Pending]

**Quote**:
> $$
> P = \left( \begin{array}{cc} 0.5 & 0.5 \\ 0.5 & 0.5 \end{array} \right). \tag{29}
> $$

**Feedback**:
The mutation matrix in equation (29) has identical rows, which is precisely the parent-independent mutation (PIM) condition under which Proposition 1 guarantees π̂(·|A_n) = π(·|A_n) exactly, making Q_θ^SD the exact optimal proposal. The efficiency gain shown in Fig. 2 therefore reflects the best-case scenario for Q_θ^SD, not a general result. A sentence after equation (29) noting that this matrix satisfies PIM and that Proposition 1 therefore guarantees exactness of the proposal would give readers an accurate picture of the theoretical guarantees underlying this example.

---

### 12. IS Estimator Finite-Sample Underestimation Conflated with Asymptotic Bias

**Status**: [Pending]

**Quote**:
> the distribution of the importance weights tends to be more skewed for $\theta$ away from the $\theta_0$. As a result such methods will tend to underestimate the relative likelihood away from $\theta_0$, leading to an estimated curve which is artificially peaked about this driving value

**Feedback**:
IS estimators are unbiased in expectation under standard regularity conditions, so systematic underestimation does not follow directly from weight skewness alone. What follows is higher variance and, in finite samples, a higher probability that the estimator falls below its expectation because rare large-weight genealogies are missed. This is a finite-sample phenomenon that depends on M, not an inherent asymptotic property. Rewrite 'As a result such methods will tend to underestimate the relative likelihood away from θ_0' as 'As a result, in finite samples, such methods will tend to underestimate the relative likelihood away from θ_0, because rare large-weight genealogies are likely to be missed' to make clear this is a finite-sample phenomenon, not an asymptotic bias.

---

### 13. IS Function Described as 'Optimal' at Driving Value, Contradicting Approximation Framework

**Status**: [Pending]

**Quote**:
> Since the IS function which these MCMC methods use is most efficient (in fact optimal) at $\theta_0$, and tends to become less efficient for $\theta$ away from $\theta_0$

**Feedback**:
The paper's own framework (Section 4) establishes that Q_θ^SD is an approximation to the optimal IS distribution, not the optimal distribution itself — exactness holds only for PIM (Proposition 1) and n=1 with reversible P. Describing the IS function as 'in fact optimal' at θ_0 is inconsistent with this characterization. The zero-variance optimal proposal Q_θ^* requires knowing the likelihood itself. Rewrite '(in fact optimal) at θ_0' as '(approximately optimal, by design) at θ_0' to maintain consistency with the paper's own treatment of Q_θ^SD as an approximation.

---

### 14. S+1 Rooted Gene Trees Count Asserted Without Derivation and May Be Incorrect

**Status**: [Pending]

**Quote**:
> (There are $S + 1$ such rooted gene trees, where $S$ is the number of mutations in the data.)

**Feedback**:
The number of distinct rootings of an unrooted gene tree equals the number of branches. For a general unrooted binary tree with n labeled leaves there are 2n−3 branches, which need not equal S+1. For n=5 and S=5 (as in Fig. 6), a fully resolved binary tree has 2(5)−3=7 branches, not 6=S+1. The S+1 count holds specifically for the condensed gene-tree representation of Griffiths and Tavare (1994b) where each mutation corresponds to exactly one branch. A clarifying parenthetical should state that this count applies to the condensed unrooted gene tree representation, not to the full coalescent tree with n leaves.

---

### 15. Garbled Weight Notation n_{i,s} in Equation (33)

**Status**: [Pending]

**Quote**:
> \hat{\pi}(\beta|A_n) = \sum_{\alpha \in A_n} \sum_{i=1}^{s} \frac{n_{i,s}}{n} w_i F_{\alpha_1\beta_1}^{(\theta,t_i,n)} \cdots F_{\alpha_l\beta_l}^{(\theta,t_i,n)} \tag{33}

**Feedback**:
In equation (31) the weight attached to chromosome α is n_α/n, where n_α is the count of type α in A_n. Gaussian quadrature in equation (33) approximates only the integral over t; it does not alter the discrete sum over sample chromosomes. The notation n_{i,s}/n conflates the quadrature index i and the number of quadrature points s into a subscript on what should be the sample count n_α. Since i already indexes the quadrature node and s already denotes the total number of nodes, n_{i,s} has no coherent interpretation and appears to be a typographical corruption of n_α. Rewrite n_{i,s}/n as n_α/n in equation (33).

---

### 16. Parametric Bootstrap on Tail Weights Alone Cannot Directly Yield CI for Full Mean

**Status**: [Pending]

**Quote**:
> we propose fitting a generalized Pareto distribution (see Davison and Smith (1990) for example) to the weights above some threshold, and using a parametric bootstrap to estimate confidence intervals for the mean of the weights (i.e. the estimate of the likelihood).

**Feedback**:
The mean of the full weight distribution decomposes as E[W] = E[W·1(W≤u)] + E[W·1(W>u)], where only the second term is modelled by the GPD. A parametric bootstrap applied solely to the GPD-fitted tail propagates uncertainty from the tail component but ignores Monte Carlo variance in the sub-threshold component and uncertainty in the threshold u itself. The procedure as described is incomplete: it should combine the empirical mean of sub-threshold weights with the GPD-based tail mean and bootstrap both components jointly. Rewrite to specify 'combining the GPD-based tail mean with the empirical mean of sub-threshold weights, and using a parametric bootstrap over both components to estimate confidence intervals for the overall mean.'

---

### 17. IS Ascertainment Correction Omits Renormalization Factor

**Status**: [Pending]

**Quote**:
> the ascertainment effect can be accommodated by labelling every lineage which leads to any chromosome in the panel as a panel lineage and adapting both $P_{\theta}(\mathcal{H})$ and $Q_{\theta}(\mathcal{H})$ so that mutations can occur only on panel lineages.

**Feedback**:
The correct likelihood for an ascertained site requires conditioning on the event that the mutation falls on a panel lineage: L_correct ∝ P_θ(A_n, mutation on panel lineage | H) / P_θ(mutation on panel lineage | H). The denominator — the fraction of total branch length belonging to panel lineages — varies across histories H^(i) and cannot be absorbed into a common constant. When both P_θ and Q_θ are modified identically by zeroing out non-panel mutations, the IS weights w_i = P_θ(H^(i))/Q_θ(H^(i)) remain unchanged from the unascertained case, so the ascertainment correction has not actually been applied. The IS weight for each history H^(i) should be multiplied by 1/f_panel(H^(i)), where f_panel(H^(i)) is the proportion of total branch length on panel lineages, to correctly condition on the ascertainment event.

---

### 18. MCMC Support-Traversal Claim Conflates Discrete and Continuous Cases

**Status**: [Pending]

**Quote**:
> any converged Markov chain Monte Carlo (MCMC) scheme for $p(\theta, \mathcal{H}|A_{n})$ has, theoretically, traversed the support of the posterior and, in particular, visited all $\mathcal{H}$ such that

**Feedback**:
When the history space H includes continuous coalescence times (as in the coalescent), an ergodic MCMC chain visits a measure-zero subset of the support in finite time. The ergodic theorem guarantees that time averages converge to space averages, but not that every point in the support is visited. Consequently, summing over distinct H values visited by the chain would miss the vast majority of the support and yield a severely biased approximation to L(θ). The argument would be valid only if H were a finite discrete space. Rewrite 'visited all H such that p(A_n|θ,H)p(H|θ)p(θ)>0' as 'visited regions of positive posterior probability with frequency proportional to their posterior mass' to accurately reflect what ergodicity guarantees.

---

### 19. Finite-Sum Approximation of F Matrices Lacks Truncation Rule; Matrix Exponential Available

**Status**: [Pending]

**Quote**:
> The matrices $F^{(\theta,t_i,n)}$ given by equation (32) may each be approximated by a finite sum with a large number of terms (these matrices need only be found once for any particular problem).

**Feedback**:
Equation (32) defines F as an infinite series in powers of (θt/n). No truncation criterion, error bound, or term count is given. For large θ or large t_i, the Poisson mean θt_i/n can be large and the series converges slowly, making 'a large number of terms' vague and potentially inadequate. Readers might note that F^{(θ,t,n)} is the matrix exponential of (θt/n)(P−I), so equation (32) is the Taylor series of that matrix exponential, which can be evaluated to machine precision using standard algorithms without truncation error. Rewrite 'approximated by a finite sum with a large number of terms' as 'computed as the matrix exponential exp((θt_i/n)(P−I)), which equals the series in equation (32) and can be evaluated to machine precision using standard algorithms.'

---

### 20. Invariance Property Invoked but Truncation Breaks It

**Status**: [Pending]

**Quote**:
> Under this mutation model the joint distribution of sample configurations is invariant under the addition of any fixed number of repeats to each sampled allele (Moran, 1975).

**Feedback**:
The invariance property holds for the untruncated stepwise model on the integers, but the immediately following truncation to E={0,1,...,19} with reflecting boundaries at 0 and 19 breaks translation invariance because the boundary conditions are not themselves translation-invariant. The authors acknowledge this only indirectly ('This truncation will make little difference to the likelihood of samples whose allele lengths are not too close to these boundaries'), without noting that the cited invariance property no longer applies to the truncated model. A sentence clarifying that the invariance applies to the untruncated model and that the truncation is an approximation that breaks exact invariance would prevent readers from incorrectly applying the invariance property to the implemented model.

---

### 21. Inconsistent Driving-Value Notation θ_0 vs η_0 Within Section 5.4

**Status**: [Pending]

**Quote**:
> Fig. 4 shows a comparison of estimated relative likelihood surfaces obtained by using our proposal distribution $Q_{\theta_0=10.0}^{\mathrm{SD}}$ and by using an MCMC scheme developed by Wilson and Balding (1998)

**Feedback**:
In the body text and Fig. 3 caption the driving value is consistently denoted θ_0. However, in the captions of Figs. 4 and 5 the same parameter is written as η_0 (e.g., Q_{η_0=10.0}^{SD} and Q_{η_0=8.0}^{SD}). This is a direct notational inconsistency within the same section: the body text of the Fig. 4 comparison paragraph uses θ_0 while the figure caption immediately below uses η_0 for the identical object. All instances of Q_{η_0=10.0}^{SD} and Q_{η_0=8.0}^{SD} in the Fig. 4 and Fig. 5 captions should be rewritten as Q_{θ_0=10.0}^{SD} and Q_{θ_0=8.0}^{SD} to match the notation used consistently elsewhere.

---

### 22. Standard Errors Reported Despite Unproven Finite-Variance Property

**Status**: [Pending]

**Quote**:
> even assuming finite variance (which is not guaranteed) the distribution of the weights may be so highly skewed that, even for very large $M$, $\sigma^2$ is (with high probability) underestimated by $\hat{\sigma}^2$

**Feedback**:
The paper explicitly states it cannot prove finite variance of the weights for the general case — only for the infinite sites model where the history space is finite (Section 6.4). In Table 1 at θ=15, the standard error from 20,000 samples of Q^SD severely underestimates the true variability: the point estimates differ by ~7.8 long-run standard errors, and the ratio of standard errors between the long and short runs is ~1.7 rather than the expected √500 ≈ 22. The proposed generalized Pareto diagnostic (Section 6.4) is described as promising but not actually applied to any of the reported examples. It would be helpful to apply the Pareto tail diagnostic to at least one example, or to flag all reported standard errors with the caveat that they may be underestimates when the effective sample size is small relative to M.

---

### 23. 'Seven Orders of Magnitude' Understates the Actual Discrepancy at θ=15

**Status**: [Pending]

**Quote**:
> the samples from $Q_{\theta}^{\mathrm{GT}}$ underestimate the likelihood by seven orders of magnitude.

**Feedback**:
From Table 1, Q_θ^GT gives 2.41×10⁻¹⁹ while the long-run Q_θ^SD reference is 5.37×10⁻¹². The ratio is 5.37×10⁻¹²/2.41×10⁻¹⁹ ≈ 2.23×10⁷, corresponding to log₁₀(2.23×10⁷) ≈ 7.35 orders of magnitude. 'Seven orders of magnitude' is a slight understatement; 'more than seven orders of magnitude (a factor of approximately 2×10⁷)' would be more precise and more accurately conveys the severity of the failure.

---

### 24. Infinite Variance Condition for Fluctuate Stated Without Connecting to the IS Weight Mechanism

**Status**: [Pending]

**Quote**:
> (In fact Stephens (1999) has recently shown that for $\theta > 2\theta_0$ the estimator has infinite variance.)

**Feedback**:
The claim is stated as a general result but it is not clear whether it applies to the specific ratio estimator of equation (7) using the Kuhner et al. genealogy-based MCMC, or to a more general class. The preceding sentence attributes poor Fluctuate performance to approximation quality, which is a different explanation from infinite variance of IS weights — these are not equivalent. Rewrite as '(In fact Stephens (1999) has recently shown that for θ > 2θ_0 the importance weights in the Kuhner et al. estimator have infinite variance regardless of sample size n, providing a theoretical explanation for the degraded performance observed at large θ/θ_0.)' to make the connection between the theoretical result and the observed performance explicit.

---

### 25. Fig. 1 Caption History Sequence Element Counts Inconsistent with n=5

**Status**: [Pending]

**Quote**:
> for this typed ancestry, the history $\mathcal{H} = (H_{-m}, H_{-(m-1)}, \ldots, H_1, H_0)$ may be represented as $(\{C\}, \{C, C\}, \{C, T\}, \{C, C, T\}, \{C, T, T\}, \{T, T, T\}, \{T, T, T\}, \{C, T, T\}, \{C, T, T\})$

**Feedback**:
The caption states this example involves five individuals, so H_0 must contain exactly 5 genetic types. Counting elements in each listed multiset yields: 1, 2, 2, 3, 3, 3, 3, 3, 3. Only two split events appear (count increases from 1→2 and 2→3), but reaching n=5 from 1 requires exactly 4 splits. The final listed state {C,T,T} has 3 elements, not 5. The two consecutive occurrences of {T,T,T} and {C,T,T} likely suppress multiplicities. Rewriting the history sequence with all 5 elements listed explicitly at each step would allow readers to verify consistency with n=5.

---
