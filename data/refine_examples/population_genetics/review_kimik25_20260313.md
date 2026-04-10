# Inference in molecular population genetics

**Date**: 03/13/2026
**Domain**: statistics/population_genetics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper develops an importance sampling framework for computing likelihoods in coalescent models with general mutation mechanisms, introducing a proposal distribution $Q_\theta^{\mathrm{SD}}$ that approximates the optimal sampling distribution via matrix-analytic calculations of conditional probabilities $\hat{\pi}$. The authors demonstrate substantial efficiency improvements over existing methods for finite sites and stepwise mutation models, though theoretical guarantees regarding finite variance and proposal optimality are established only for parent-independent mutation scenarios. Applications to microsatellite and sequence data illustrate the method's performance on small-scale problems, while acknowledging computational constraints that limit extension to larger genomic datasets.

Below are the most important issues identified by the review panel.

**Finite Variance Guarantees and Standard Error Reliability**

The paper acknowledges that analytical proof of finite variance for the importance sampling weights remains unavailable for general mutation models beyond the infinite sites case. Without guaranteed finite variance, the central limit theorem invoked for standard error estimation may not hold, particularly when weight distributions exhibit heavy tails. Figure 12 illustrates that empirical variance estimates can severely underestimate true variance under high skewness, yet the method continues to report standard errors without theoretical justification for their validity in models such as microsatellites or finite sequences. It would be helpful to establish sufficient conditions for finite variance under general mutation matrices, or alternatively to implement defensive mixture components or weight truncation schemes that enforce finite variance across all parameter values.

**Proposal Approximation Error for Non-Parent-Independent Mutation**

Proposition 1 establishes that the approximation $\hat{\pi}(\cdot|A_n)$ equals the true conditional distribution only under parent-independent mutation (PIM), yet the primary applications employ stepwise and finite sites models that violate this assumption. The paper does not quantify the approximation error or establish bounds on variance inflation when mutation models deviate from PIM, leaving the efficiency gains theoretically unsubstantiated for these biologically relevant scenarios. Readers might note that without error bounds, the proximity of the proposed proposal to the optimal distribution $Q_\theta^*$ remains unclear for general mutation mechanisms. It would be helpful to derive bounds on the approximation error $|\hat{\pi} - \pi|$ for general mutation matrices and quantify how this propagates to the variance of the importance weights.

**State Space Truncation and Boundary Effects**

The implementation for microsatellite data artificially truncates the type space to $E = \{0, 1, \ldots, 19\}$ with reflecting boundary conditions, violating the infinite support assumption of the standard coalescent and altering the stationary distribution of the mutation process. For alleles near the boundaries, this introduces systematic bias that is not captured by reported standard errors. It would be helpful to quantify the truncation error analytically or demonstrate that boundary effects are negligible for the specific datasets analyzed, or alternatively to implement an exact method with proper boundary conditions that preserves the stationary distribution.

**Convergence Diagnostics for Heavy-Tailed Weight Distributions**

While Section 6.4 identifies that standard diagnostics including effective sample size and coefficient of variation fail when importance weights are highly skewed, the proposed remedy using extreme value theory is not implemented or validated. Consequently, practitioners lack reliable stopping criteria to determine when sufficient samples have been drawn, risking severely biased estimates with misleadingly small reported standard errors without detection. It would be helpful to implement and validate the generalized Pareto distribution diagnostic suggested in Section 6.4, or to require reporting of robust diagnostics such as $M_{\mathrm{eff}} = (\sum w_i)^2 / \sum w_i^2$ alongside standard errors to warn users when weight skewness compromises estimate reliability.

**Computational Scalability and Approximation Error**

For sequence data where the type space grows exponentially with length, exact calculation of $\hat{\pi}$ via matrix inversion becomes infeasible, necessitating Gaussian quadrature approximations that the authors describe as 'rather rough.' The paper does not characterize the propagation of these approximation errors into final likelihood estimates or establish computational limits regarding sequence length and sample size where the method remains viable, restricting applicability to modern genomic datasets. It would be helpful to provide a formal computational complexity analysis of the $\hat{\pi}(\cdot|\cdot)$ calculation and demonstrate the method's performance on larger datasets, or to develop sparse matrix approximations that avoid the $O(k^{2l})$ storage requirements.

**Parameter Sensitivity and Numerical Stability**

The proposal distribution $Q_{\theta_0}^{\mathrm{SD}}$ depends on a driving value $\theta_0$, and its efficiency degrades when the true parameter differs from this value, yet the paper provides limited guidance on selecting $\theta_0$ when the true parameter is unknown. Additionally, the matrix inversion $(I - \lambda_n P)^{-1}$ and proposal ratios become numerically unstable as mutation rates approach zero, where the geometric series converges slowly and denominators approach zero. It would be helpful to develop methods for combining estimates from multiple driving values to ensure coverage across the parameter space, and to provide stability conditions or safeguards for parameter values near the boundary of the parameter space.

**Status**: [Pending]

---

## Detailed Comments (18)

### 1. Orders of magnitude claim inconsistent with demonstrated results

**Status**: [Pending]

**Quote**:
> Our approach substantially outperforms existing IS algorithms, with efficiency typically improved by several orders of magnitude.

**Feedback**:
Section 5.2 demonstrates variance reductions of approximately 289-500x (2.5-2.7 orders of magnitude) for θ = 2.0 and θ = 10.0, while for θ = 15.0 standard errors change by less than a factor of 2 between runs. Readers might note that "several" typically implies three or more in scientific usage. It would be helpful to revise the claim to "up to approximately 2.5 orders of magnitude" or "two to three orders of magnitude" to align the abstract with the specific numerical results.

---

### 2. Equation (1) transition probabilities invalid for initial state

**Status**: [Pending]

**Quote**:
> p _ {\theta} \left(H _ {i} \mid H _ {i - 1}\right) = \left\{ \begin{array}{l l} \frac {n _ {\alpha}}{n} \frac {\theta}{n - 1 + \theta} P _ {\alpha \beta} & \text{if } H _ {i} = H _ {i - 1} - \alpha + \beta , \\ \frac {n _ {\alpha}}{n} \frac {n - 1}{n - 1 + \theta} & \text{if } H _ {i} = H _ {i - 1} + \alpha , \\ 0 & \text{otherwise}, \end{array} \right. \tag {1}

**Feedback**:
Substituting n = 1 into equation (1) yields a split probability of \frac{n_\alpha}{1} \cdot \frac{0}{0+\theta} = 0, contradicting Algorithm 1 Step 1 where the initial single lineage splits deterministically with probability 1. It would be helpful to specify that the Markov transition probabilities in equation (1) apply for n \geq 2, while the initial transition from the MRCA (n=1) to the first bifurcation (n=2) is a deterministic split occurring with probability 1.

---

### 3. Terminology: topologies versus labeled histories

**Status**: [Pending]

**Quote**:
> For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
The formula $n!(n-1)!/2^{n-1}$ evaluates to \prod_{k=2}^n \binom{k}{2}, which is the exact count of labeled histories (ranked phylogenetic trees) specifying both the branching pattern and the temporal ordering of coalescence events. In standard phylogenetic terminology, "topology" refers to the unranked branching pattern only, counted by $(2n-3)!! = (2n-2)!/(2^{n-1}(n-1)!)$. For $n=4$, the authors' formula yields $4! \cdot 3!/2^3 = 18$, whereas there are only $5!! = 15$ unranked topologies. It would be helpful to replace "topologies" with "labeled histories" or add a clarifying note that the count includes the ranking of internal nodes.

---

### 4. Undefined function F in likelihood representation

**Status**: [Pending]

**Quote**:
> L(\theta) = \pi_{\theta}(A_n) = E \left\{ \prod_{j=0}^{\tau} F(B_j) \,\Big| \, B_0 = A_n \right\} \tag{6}

**Feedback**:
The function $F$ appearing in equation (6) is not defined within this section. Without knowing whether $F(B_j)$ represents a Radon-Nikodym derivative (ratio of target to proposal transition probabilities), a conditional sampling probability, or another quantity, readers cannot verify the identity $L(\theta) = E[\prod F(B_j)]$. It would be helpful to define $F(B_j)$ explicitly as the ratio of the transition probability under the target model with parameter $\theta$ to the transition probability under the proposal Markov chain, evaluated at state $B_j$.

---

### 5. Unspecified probability measure for expectation

**Status**: [Pending]

**Quote**:
> L(\theta) = \pi_{\theta}(A_n) = E \left\{ \prod_{j=0}^{\tau} F(B_j) \,\Big| \, B_0 = A_n \right\} \tag{6}

**Feedback**:
The expectation operator $E$ in equation (6) does not specify the probability measure under which it is taken. This ambiguity is critical because the subsequent text discusses using "realizations of a single Markov chain to estimate the likelihood function" across different values of $\theta$, which implies that the expectation must be under a $\theta$-independent reference measure $Q$ (importance sampling), with $F$ incorporating the Radon-Nikodym derivative $dP_{\theta}/dQ$. It would be helpful to clarify the measure by rewriting equation (6) as: $L(\theta) = E_{Q} \left\{ \prod_{j=0}^{\tau} F_{\theta}(B_j) \,\Big| \, B_0 = A_n \right\}$ where $Q$ denotes the probability measure induced by the proposal chain.

---

### 6. Independence assumption in MCMC density estimation

**Status**: [Pending]

**Quote**:
> The posterior density is most easily estimated by smoothing a sample $\theta^{(1)},\ldots ,\theta^{(M)}$ from the Markov chain

**Feedback**:
Standard kernel smoothing methods for density estimation assume independent and identically distributed (i.i.d.) samples. MCMC samples are inherently autocorrelated, and naive application of standard smoothing techniques to correlated samples can produce biased variance estimates and inconsistent density estimates. While consistent estimation is possible under geometric ergodicity with appropriate bandwidth selection, the text does not acknowledge the dependence structure or the need for thinning or specialized methods. It would be helpful to add 'after thinning to reduce autocorrelation or using methods accounting for dependence structure' after 'Markov chain' to ensure the validity of the density estimation approach.

---

### 7. Support condition sufficient but not necessary

**Status**: [Pending]

**Quote**:
> If $Q_{\theta}(\cdot)$ is any distribution on ancestries whose support includes $\{\mathcal{H}\colon \pi_{\theta}(A_n|\mathcal{H}) > 0\}$, then equation (4) may be rewritten as

**Feedback**:
Re-deriving the importance sampling identity confirms that the stated support condition is sufficient but stronger than necessary. The importance sampling estimator (9) is unbiased when $Q_{\theta}$ dominates the target measure $P_{\theta}(\mathcal{H})\pi_{\theta}(A_n|\mathcal{H})$, meaning $Q_{\theta}(\mathcal{H}) > 0$ whenever $P_{\theta}(\mathcal{H})\pi_{\theta}(A_n|\mathcal{H}) > 0$. The paper's condition requires coverage of $\{\mathcal{H}\colon \pi_{\theta}(A_n|\mathcal{H}) > 0\}$ regardless of $P_{\theta}(\mathcal{H})$, which is strictly larger than necessary when $P_{\theta}(\mathcal{H}) = 0$. Furthermore, for equation (12) with fixed driving value $\theta_0$, validity for $L(\theta)$ requires $Q_{\theta_0}$ to dominate $P_{\theta}(\mathcal{H})\pi_{\theta}(A_n|\mathcal{H})$ for all $\theta$ of interest. It would be helpful to rewrite the support condition as 'whose support includes the support of $P_{\theta}(\mathcal{H})\pi_{\theta}(A_n|\mathcal{H})$' to be technically precise.

---

### 8. Finite variance condition for reused importance sampling

**Status**: [Pending]

**Quote**:
> where $\mathcal{H}^{(1)},\ldots ,\mathcal{H}^{(M)}$ are independent samples from $Q_{\theta_0}(\cdot)$. This approach is due to Griffiths and Tavaré (1994a), which refers to $\theta_0$ as the 'driving value' of $\theta$.

**Feedback**:
While equation (12) provides an unbiased estimator of $L(\theta)$ under the absolute continuity condition, the text omits the necessary condition for finite variance. For the importance sampling estimator $\hat{L}(\theta) = \frac{1}{M}\sum_{i=1}^M \pi_{\theta}(A_n|\mathcal{H}^{(i)})P_{\theta}(\mathcal{H}^{(i)})/Q_{\theta_0}(\mathcal{H}^{(i)})$ to have finite variance, the second moment must exist: $E_{Q_{\theta_0}}[(\pi_{\theta}(A_n|\mathcal{H})P_{\theta}(\mathcal{H})/Q_{\theta_0}(\mathcal{H}))^2] < \infty$. This requires that $Q_{\theta_0}$ has sufficiently heavy tails to dominate $P_{\theta}\pi_{\theta}$ in the $L^2$ sense, not merely in support. When $\theta$ differs from $\theta_0$, the ratio $P_{\theta}/Q_{\theta_0}$ may have heavy tails leading to infinite variance and unreliable estimates despite unbiasedness. It would be helpful to add after equation (12): 'This estimator has finite variance provided $E_{Q_{\theta_0}}[(P_{\theta}(\mathcal{H})\pi_{\theta}(A_n|\mathcal{H})/Q_{\theta_0}(\mathcal{H}))^2] < \infty$, which requires $Q_{\theta_0}$ to have sufficiently heavy tails relative to $P_{\theta}$.'

---

### 9. Misstatement of CLT applicability under skewness

**Status**: [Pending]

**Quote**:
> However, caution is necessary, as even assuming finite variance (which is not guaranteed) the distribution of the weights may be so highly skewed that, even for very large $M$, $\sigma^2$ is (with high probability) underestimated by $\hat{\sigma}^2$, and/or the normal asymptotic theory does not apply.

**Feedback**:
The text correctly identifies that finite variance is required for the central limit theorem (CLT), but incorrectly suggests that high skewness invalidates the normal asymptotic theory when variance is finite. The CLT applies to i.i.d. summands with finite variance regardless of skewness; the limiting distribution is always normal. Skewness affects the rate of convergence (via Berry-Esseen bounds) and the reliability of finite-sample variance estimates, but does not invalidate the asymptotic theory itself. It would be helpful to rewrite '...and/or the normal asymptotic theory does not apply' as '...and/or the normal approximation may be poor for practically feasible sample sizes' to accurately reflect that the theory applies but convergence may be slow.

---

### 10. Incorrect boundary condition description for truncated state space

**Status**: [Pending]

**Quote**:
> The implementation of our IS scheme is facilitated by centring the sample distribution near 10 repeats and truncating the type space $E$ to $\{0, 1, \dots, 19\}$ by insisting that all mutations to alleles of length 0 or 19 involve the gain or loss respectively of a single repeat.

**Feedback**:
The description of the reflecting boundary conditions contains a logical inconsistency. If a mutation occurs to an allele of length 0, it must originate from allele 1 and involve a loss of a repeat (decreasing from 1 to 0). Conversely, a mutation to an allele of length 19 must originate from allele 18 and involve a gain of a repeat (increasing from 18 to 19). The text assigns 'gain' to mutations to allele 0 and 'loss' to mutations to allele 19, which is backwards. To implement reflecting boundaries at 0 and 19, mutations from alleles of length 0 involve a gain (to 1) and mutations from alleles of length 19 involve a loss (to 18). It would be helpful to rewrite 'mutations to alleles of length 0 or 19 involve the gain or loss respectively' as 'mutations from alleles of length 0 or 19 involve the gain or loss respectively' to correctly describe the reflecting boundary behavior.

---

### 11. Undefined notation π_θ in equation (30)

**Status**: [Pending]

**Quote**:
> Using IS as before gives
> 
> $$
> P _ {\theta} \left(A _ {n}, O\right) \approx \frac {1}{M} \sum_ {i = 1} ^ {M} \pi_ {\theta} \left(A _ {n} \mid \mathcal {H} ^ {(i)}\right) P _ {\theta} \left(O \mid \mathcal {H} ^ {(i)}\right) \frac {P _ {\theta} \left(\mathcal {H} ^ {(i)}\right)}{Q _ {\theta} \left(\mathcal {H} ^ {(i)}\right)}. \tag {30}
> $$

**Feedback**:
The symbol $\pi_{\theta}$ is used here to denote the conditional probability of the data $A_n$ given the history $\mathcal{H}^{(i)}$, but throughout the paper (e.g., Section 4, Theorem 1) $\pi(\cdot|A_n)$ denotes the predictive distribution of an additional sample given the current data. This creates notational ambiguity, as readers may confuse $\pi_{\theta}(A_n|\mathcal{H})$ with the predictive density used earlier. Furthermore, if $\mathcal{H}^{(i)}$ denotes a complete ancestral history (genealogy and mutational events), then $A_n$ is typically a deterministic function of $\mathcal{H}^{(i)}$ under the infinite sites model, making $P_{\theta}(A_n|\mathcal{H}^{(i)})$ an indicator function rather than a density. It would be helpful to define $\pi_{\theta}$ explicitly here or replace it with $P_{\theta}$ to maintain consistency with standard likelihood notation and clarify whether this represents an indicator of compatibility or a non-degenerate conditional probability.

---

### 12. Incorrect summation index in normalized weight expression

**Status**: [Pending]

**Quote**:
> the distribution with atoms of size $w_{i}/\Sigma_{i}w_{j}$ on histories $\mathcal{H}^{(i)}$ ($i=1,\ldots,M$)

**Feedback**:
The normalized weight expression contains an inconsistent summation index that renders the formula mathematically ambiguous. The notation $\Sigma_{i}w_{j}$ indicates summation over the index $i$ of the term $w_{j}$, but $w_{j}$ does not depend on $i$; consequently this evaluates to $M \cdot w_{j}$ rather than the intended total sum of weights $\sum_{k=1}^{M} w_{k}$. To correctly represent the normalized importance weight for the $i$th sample, the denominator must sum over the weight index (conventionally $j$ or $k$), not $i$. It would be helpful to rewrite '$w_{i}/\Sigma_{i}w_{j}$' as '$w_{i}/\sum_{j}w_{j}$' (or '$w_{i}/\Sigma_{j}w_{j}$') to properly denote the self-normalized importance weight $w_i / \sum_{j=1}^{M} w_j$ used to approximate the posterior distribution of $\mathcal{H}$ given $A_n$.

---

### 13. Omission of parent-independent mutation in finite variance results

**Status**: [Pending]

**Quote**:
> For example, we could not prove finiteness of the variance of our weights, except in the special case of the infinite sites model where the number of possible histories is finite.

**Feedback**:
This claim contradicts the result established in Section 5.1 for parent-independent mutation (PIM) models. There, Proposition 1 demonstrates that the proposal distribution $Q_{\theta}^{\mathrm{SD}}$ equals the optimal proposal distribution $Q_{\theta}^{*}(\mathcal{H}) = P_{\theta}(\mathcal{H}|A_n)$, which implies that the IS estimator (9) has zero variance ('Thus our IS estimator (9) should have zero variance and give the exact value for the likelihood, which in fact it does'). Since zero variance is finite, the authors have indeed proven finiteness of variance for PIM models, not solely for the infinite sites model. It would be helpful to revise the quoted text to acknowledge that variance is also finite (and in fact zero) for parent-independent mutation models, or to qualify that the statement applies specifically to non-PIM models where $Q_{\theta}^{\mathrm{SD}}$ differs from the optimal proposal.

---

### 14. Ambiguity regarding scope of fully efficient methods

**Status**: [Pending]

**Quote**:
> The availability in simple settings of fully efficient methods provides a useful yardstick for comparison.

**Feedback**:
Initially, this passage appears to claim that the methods described in this paper are fully efficient (i.e., provide zero-variance estimators) in simple settings, which would provide a benchmark for other methods. However, reviewing the results in Section 5.1 and Proposition 1, the zero-variance property is proven only for parent-independent mutation (PIM) models. For the microsatellite (stepwise mutation) and finite-sites sequence data applications discussed in Sections 5.2 and 5.5, the proposal distribution $Q_{\theta}^{\mathrm{SD}}$ is explicitly an approximation to the optimal distribution $Q_{\theta}^{*}$, and the importance sampling estimator does not have zero variance. Without qualification, the phrase 'fully efficient methods' may mislead readers into believing the methods achieve full efficiency for all the genetic models considered in the applications, rather than only for the PIM case. This ambiguity matters because it affects the interpretation of the 'yardstick'—readers might incorrectly assume the variance properties demonstrated for PIM extend to the complex models used in the examples. It would be helpful to rewrite 'The availability in simple settings of fully efficient methods' as 'The availability of fully efficient methods for parent-independent mutation (PIM) models' or add the parenthetical ' (specifically, those with parent-independent mutation)' after 'simple settings' to clarify that full efficiency is restricted to this specific class of mutation models and does not apply to the stepwise or finite-sites models discussed in the applications.

---

### 15. Specification of Gaussian quadrature type for integral approximation

**Status**: [Pending]

**Quote**:
> The integral in equation (31) may be approximated by using Gaussian quadrature (see for example Evans (1993)):

**Feedback**:
The integral in equation (31) takes the form $\int_0^\infty e^{-t} f(t) \, dt$ where $f(t) = \prod_{j=1}^l F_{\alpha_j\beta_j}^{(\theta,t,n)}$. This specific form, with weight function $e^{-t}$ over the domain $[0, \infty)$, corresponds exactly to Gauss-Laguerre quadrature. While 'Gaussian quadrature' is technically correct as an umbrella term, explicitly specifying Gauss-Laguerre would prevent readers from incorrectly applying other variants (e.g., Gauss-Hermite for $(-\infty, \infty)$ with $e^{-t^2}$ weight, or Gauss-Legendre for finite intervals) that are designed for different weight functions and integration domains. It would be helpful to rewrite 'Gaussian quadrature' as 'Gauss-Laguerre quadrature' to clarify the specific numerical method required for this integral form.

---

### 16. Ambiguity in geometric distribution parameterization

**Status**: [Pending]

**Quote**:
> where $m$ is geometrically distributed with parameter $l\theta/(n+l\theta)$

**Feedback**:
The equivalence claimed between the geometric mutation count and the Poisson process representation depends critically on the parameterization of the geometric distribution. Under the standard statistical convention where $M \sim \text{Geom}(p)$ denotes $P(M=m) = (1-p)^m p$ for $m=0,1,2,\ldots$ with mean $(1-p)/p$, the derivation from the Poisson representation yields $P(M=m) = \frac{n}{n+l\theta}\left(\frac{l\theta}{n+l\theta}\right)^m$. This corresponds to a geometric distribution with success probability $p = n/(n+l\theta)$, not $l\theta/(n+l\theta)$. The text's stated parameter $l\theta/(n+l\theta)$ is only correct under the non-standard parameterization $P(M=m) = p^m(1-p)$. It would be helpful to add a clarifying note stating that the parameterization used is $P(M=m) = [l\theta/(n+l\theta)]^m \cdot [n/(n+l\theta)]$ (i.e., the 'continuation probability' is $l\theta/(n+l\theta)$).

---

### 17. Missing mutation transition matrix in recursion (34)

**Status**: [Pending]

**Quote**:
> p(\mathbf{n}) = \frac{\theta}{n + \theta - 1} \left\{ \sum_{\alpha = 1}^{d} \sum_{\beta = 1}^{d} \frac{n_{\beta} + 1 - \delta_{\alpha \beta}}{n} p(\mathbf{n} + \mathbf{e}_{\beta} - \mathbf{e}_{\alpha}) \right\} + \frac{n - 1}{n + \theta - 1} \sum_{\{ \alpha : n_{\alpha} > 0 \}} \frac{n_{\alpha} - 1}{n - 1} p(\mathbf{n} - \mathbf{e}_{\alpha}). \tag{34}

**Feedback**:
Equation (34) appears to omit the mutation transition matrix $P$ from the mutation term. In the general Markov mutation model defined in Section 2, where $P_{\beta\alpha}$ denotes the probability of mutating from type $\beta$ to type $\alpha$, the probability of a mutation event from $\beta$ to $\alpha$ occurring as the first event back in time is $\frac{n_\beta}{n}\frac{\theta}{n+\theta-1}P_{\beta\alpha}$. Consequently, the recursion should include the factor $P_{\beta\alpha}$ within the double summation. The correct form is: $p(\mathbf{n}) = \frac{\theta}{n+\theta-1}\sum_{\alpha=1}^d\sum_{\beta=1}^d \frac{n_\beta+1-\delta_{\alpha\beta}}{n}P_{\beta\alpha}p(\mathbf{n}+\mathbf{e}_\beta-\mathbf{e}_\alpha) + \frac{n-1}{n+\theta-1}\sum_{\{\alpha:n_\alpha>0\}}\frac{n_\alpha-1}{n-1}p(\mathbf{n}-\mathbf{e}_\alpha)$. Without $P_{\beta\alpha}$, the equation is only valid for parent-independent mutation where $P_{\beta\alpha}=\pi_\alpha$ and the factor can be separated, or for the trivial case of no mutation ($P=I$), which would contradict the presence of $\theta>0$. It would be helpful to rewrite the mutation term in equation (34) to include $P_{\beta\alpha}$ inside the summation over $\alpha$ and $\beta$.

---

### 18. Missing conditions for stopping time and integrability

**Status**: [Pending]

**Quote**:
> where $B_0, B_1, \ldots, B_\tau$ is a particular set-valued Markov chain stopped the first time $\tau$ that it has cardinality 1.

**Feedback**:
The representation (6) and the subsequent Monte Carlo approximation require that the stopping time $\tau$ is almost surely finite ($P(\tau < \infty) = 1$) and that the product is integrable ($E[\prod_{j=0}^{\tau} |F(B_j)|] < \infty$). Without these conditions, the expectation may be undefined or the Monte Carlo estimator may fail to converge. For example, if the Markov chain has a recurrent communicating class with cardinality greater than 1, then $\tau = \infty$ with positive probability, rendering the product undefined. Similarly, if $F(B_j) > 1$ and $\tau$ has heavy tails, the expectation could be infinite. It would be helpful to add the explicit assumptions after the definition of $\tau$: 'Assume that $P(\tau < \infty) = 1$ and that $E[\prod_{j=0}^{\tau} |F(B_j)|] < \infty$ to ensure the expectation exists and the Monte Carlo estimator is strongly consistent.'

---
