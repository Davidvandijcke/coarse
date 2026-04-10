# Inference in molecular population genetics

**Date**: 03/13/2026
**Domain**: statistics/computational_statistics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper proposes a new importance sampling (IS) estimator, Q_SD, for computing the likelihood of population genetic data under the coalescent with mutation. The method constructs an efficient proposal distribution by approximating the optimal conditional sampling distribution π(·|A_n) using a closed-form approximation π-hat derived from the stationary distribution of the mutation process. Empirical comparisons against the Griffiths–Tavaré IS scheme (Q_GT) and MCMC-based competitors (Fluctuate, micsat) across several mutation models suggest that Q_SD achieves substantially lower variance per sample and faster computation, though the paper acknowledges unresolved theoretical gaps and scope limitations.

Below are the most important issues identified by the review panel.

**Unresolved Finite-Variance Guarantee for the Core IS Estimator**

Section 6.4 explicitly acknowledges that the authors 'could not prove finiteness of the variance of our weights, except in the special case of the infinite sites model where the number of possible histories is finite.' This is a fundamental gap: without finite variance, the central limit theorem invoked in Section 5 to justify standard error reporting does not apply, and the standard errors quoted throughout Tables 1 and Figures 2–5 may be systematically misleading. The paper simultaneously warns readers that standard errors can 'seriously underestimate' uncertainty and criticizes Q_GT for producing unreliable standard errors due to heavy-tailed weight distributions, while admitting the same theoretical deficiency applies to Q_SD in general non-PIM, non-infinite-sites settings such as the microsatellite stepwise model. The generalized Pareto diagnostic suggested in Section 6.4 is described as 'promising on initial investigation' but is never actually applied to any example in the main text. It would be helpful to either provide sufficient conditions on the mutation model and sample size under which finite variance can be guaranteed, or to apply the GPD tail-fitting procedure to at least one example and report the resulting confidence interval alongside the standard IS standard error, so practitioners can assess which reported standard errors are trustworthy.

**Computational Comparisons Are Not on an Equal-Time Footing**

The paper's central efficiency claims conflate statistical efficiency per sample with total computational cost per unit time. In Section 5.2, Q_SD and Q_GT are compared at equal sample counts (20,000), but the Figure 3 caption reveals that 10,000 samples from Q_GT take approximately 330 seconds while 10,000 samples from Q_SD take approximately 30 seconds—a factor of 11 difference in per-sample cost. At equal wall-clock time, Q_GT would produce roughly 11 times as many samples, which could substantially close the apparent efficiency gap. Similarly, Figure 4 compares 10,000 IS samples against 10,000 MCMC iterations without accounting for the fact that MCMC iterations are not equivalent to IS samples in computational cost or information content, and no effective sample sizes for the MCMC runs are reported. The paper does not present any comparison normalized to equal CPU time, nor does it decompose the claimed 'several orders of magnitude' improvement (Abstract) into contributions from (a) a better proposal distribution and (b) cheaper per-sample cost. A fair comparison requires either holding total CPU time constant or explicitly reporting variance × cost per sample as the efficiency metric.

**Approximation Quality of π-hat Is Validated Only for Special Cases**

The entire IS scheme rests on substituting the approximation π-hat(·|A_n) for the intractable optimal π(·|A_n) in equation (15)/(25). Proposition 1 establishes that π-hat equals π exactly only for parent-independent mutation (PIM) and for n=1 with reversible P. For the general non-PIM cases that constitute the main application domain—sequence data with non-symmetric mutation matrices (Section 5.2) and microsatellites with the stepwise model (Section 5.4)—no bound on |π-hat − π| is provided as a function of θ, n, or the structure of P, and no simulation study directly compares π-hat to π computed by alternative means. The residual underestimation at θ=15 in Table 1 even for Q_SD, and the concession in Section 5.4 that micsat appears more accurate than Q_SD for the NSE data, are both consistent with the approximation degrading at larger θ or n, but this is not investigated. It would be helpful to include, for at least one non-PIM example, a direct comparison of π-hat against π computed by brute force on a small problem, to establish that the approximation is the operative mechanism for efficiency gains and to characterize when it may degrade.

**The Driving-Value Problem for Likelihood Curve Estimation Is Acknowledged but Not Resolved**

Sections 5.3 and 6.1 acknowledge that using a single driving value θ_0 causes the IS estimator to underestimate the likelihood for θ far from θ_0, because Q_{θ_0}^SD becomes an increasingly poor proposal as |θ − θ_0| grows. The authors cite Stephens (1999) showing infinite variance for the Fluctuate weights when θ > 2θ_0, and their reply to discussants confirms this result extends to Q_SD regardless of sample size. Yet the NSE example in Section 5.4 uses θ_0 = 8.0 over a range θ ∈ [0, 20], which spans the infinite-variance regime, and all likelihood curves in Figures 2–5 are estimated from a single driving value. Bridge sampling is suggested as a remedy in Section 6.1 but is never implemented or evaluated. No analogous diagnostic to Figure 12 (which appears only in the discussion reply) is shown for Q_SD curves in the main paper, leaving open whether the apparently well-behaved Q_SD curves are genuinely accurate or merely less visibly distorted. Practical guidance for choosing θ_0 and assessing the reliability of the resulting likelihood curve is absent, which is a significant gap for practitioners.

**Scope of Validation Is Narrow and the One Realistic Example Favors MCMC**

All theoretical development assumes a constant-size, randomly mating, neutral population under the standard Kingman coalescent, and Section 6.2's discussion of extensions to varying population size, structured populations, recombination, and selection is entirely prospective. The paper's abstract claims the method 'substantially outperforms existing IS algorithms' and 'compares favourably with existing MCMC methods,' but three of the four empirical examples use small, simulated datasets where IS is expected to excel because the history space is tightly constrained. The one larger, realistic example—the NSE microsatellite dataset with 60 individuals at 5 loci (Section 5.4)—is the only case where the authors concede that micsat appears more accurate than Q_SD, precisely the regime (larger n, multi-locus) where MCMC has a structural advantage. Furthermore, the NSE dataset comprises samples from Nigeria, Sardinia, and East Anglia—geographically separated populations for which the panmixia assumption is almost certainly violated—yet no discussion of the expected direction or magnitude of bias in θ estimates under population structure is provided. A more systematic characterization of the crossover point between IS and MCMC dominance, varying n and the number of loci, would be needed to support the claim that 'both IS and MCMC methods have a continuing role to play.'

**MCMC Competitor Comparisons Use Inadequately Tuned Implementations**

The comparisons with Fluctuate in Figure 2(c) and with micsat in Figures 4–5 are used to support claims about IS versus MCMC performance, but the MCMC runs use default or short chain lengths that the paper itself acknowledges are insufficient. Kuhner and Beerli's discussion contribution demonstrates that combining 10 independent Fluctuate runs at different driving values with Geyer's reverse logistic regression produces a curve consistent with Q_SD, suggesting the apparent superiority of Q_SD in Figure 2(c) reflects poor MCMC tuning rather than an inherent MCMC limitation. The paper explicitly notes 'there are many ways in which our use of the MCMC scheme could be improved' (Section 5.4) but does not attempt to optimize competitor methods before comparing them. Comparative performance claims should be based on well-tuned implementations of all methods—including the multi-chain strategy that Kuhner and Beerli show resolves the discrepancy—or the limitations of the comparison should be stated as a primary caveat rather than a footnote. Similarly, the robustness of θ inference to mutation model misspecification (P treated as known throughout, despite discussant Stephens raising this concern and the authors conceding it is 'likely to be a serious problem') is never examined via simulation, leaving practitioners without guidance on the sensitivity of conclusions to this assumption.

**Status**: [Pending]

---

## Detailed Comments (21)

### 1. Topology Count Formula Counts Labeled Histories, Not Topologies

**Status**: [Pending]

**Quote**:
> For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
The formula n!(n-1)!/2^{n-1} counts labeled histories (ranked genealogies), not distinct tree topologies. For n=4: labeled histories = 4! times 3!/2^3 = 18, while distinct rooted binary topologies = (2*4-3)!! = 5. Rewrite 'different possible topologies for the underlying trees' as 'different possible labeled histories (ranked genealogies) for the underlying trees,' because the formula counts ranked coalescence orderings, not unranked topologies.

---

### 2. Cardinality Conflated with Dimensionality of Missing Data Space

**Status**: [Pending]

**Quote**:
> We note though that for all potential data augmentation strategies the dimension of the space in which the missing data live will be enormous. For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
The number of discrete elements in a space (cardinality) is not the same as its dimension. For a fixed topology, branch lengths contribute 2n-2 continuous dimensions, so the genealogy space combines a large discrete component with high-dimensional continuous branch lengths. Rewrite 'the dimension of the space in which the missing data live will be enormous' as 'the space in which the missing data live is enormous, combining a large number of discrete labeled histories with high-dimensional continuous branch lengths, making naive Monte Carlo integration over H impractical,' because the current phrasing conflates cardinality with dimensionality.

---

### 3. Lower Bound of Required M Inconsistent with Impracticability Claim

**Status**: [Pending]

**Quote**:
> each term of the sum will be 0 with very high probability, and reliable estimation will require values of $M$ (in the range $10^6 - 10^{100}$ for the examples that we consider here) which are too large for the method to be practicable.

**Feedback**:
M = 10^6 is well within reach of modern computers and is routinely used in Monte Carlo studies. If the lower end of this range suffices for some examples, the naive estimator would be practicable for those cases, contradicting the blanket conclusion. The range spanning 94 orders of magnitude suggests examples vary enormously in difficulty. It would be helpful to specify, for at least one concrete example, how the required M was estimated and which examples require M near the upper end of the range, because as stated the lower bound of 10^6 does not support the impracticability conclusion.

---

### 4. Function F(B_j) Left Undefined in the Griffiths-Tavare Scheme

**Status**: [Pending]

**Quote**:
> This leads to a natural Monte Carlo approximation for $L(\theta)$: simply evaluate the expectation above by repeatedly simulating the chain started from $A_n$, and averaging the realized values of $\Pi_{j=0}^{\tau} F(B_j)$ across the simulated realizations of the chain.

**Feedback**:
The function F(B_j) appearing in this equation is never defined in this section, leaving the central mathematical object of the Griffiths-Tavare scheme opaque. Without this definition, readers cannot verify that the product correctly represents L(theta), nor can they understand why the product of these factors yields the likelihood. The dependence of F on theta is also suppressed, which matters because the subsequent paragraph discusses reusing a single chain across multiple theta values. Rewrite the sentence to define F explicitly, e.g., 'where F(B_j) = F_theta(B_j) is [the explicit recursion weight],' so that the basis for multi-theta reuse is transparent.

---

### 5. Intermediate Step in Likelihood Derivation Uses Inconsistent Probability Notation

**Status**: [Pending]

**Quote**:
> = \frac {P _ {\theta} (\mathcal {H} \cap A _ {n})}{P _ {\theta} (\mathcal {H} \mid A _ {n})} = \pi_ {\theta} \left(A _ {n}\right) = L (\theta),

**Feedback**:
The numerator P_theta(H intersect A_n) treats A_n and H as events in the same probability space, but A_n is observed data and H is missing data (random), so the joint event H intersect A_n is not well-defined under the paper's own conventions distinguishing pi_theta from P_theta. The correct intermediate step should read P_theta(A_n, H) / P_theta(H|A_n), and by Bayes' theorem this equals P_theta(A_n) = L(theta). The final result is correct, but the intersection notation conflicts with the paper's own probability conventions. Rewrite the intermediate step as P_theta(A_n, H) / P_theta(H|A_n) = P_theta(A_n) = L(theta).

---

### 6. Mutation Probability Calculation Uses n-1 Instead of k-1 Subscripts

**Status**: [Pending]

**Quote**:
> = \frac {\pi \left(\alpha_ {1} , \dots , \alpha_ {n - 1} , \beta\right) \delta \theta P _ {\beta \alpha} / 2}{\pi \left(\alpha_ {1} , \dots , \alpha_ {n - 1} , \alpha\right)} + o (\delta)

**Feedback**:
The proof sets up the particle model with k lineages at time t, so the configuration is a vector of length k written as (alpha_1, ..., alpha_{k-1}, alpha). However, the first displayed line uses subscript n-1, writing pi(alpha_1,...,alpha_{n-1},beta) and pi(alpha_1,...,alpha_{n-1},alpha), whereas the surrounding text consistently uses k for the number of lineages. Since k is the running variable decreasing from n to 1, and the proof has not set k=n at this point, the subscript n-1 should be k-1 throughout. The inconsistency is made visible by the second line, which correctly reverts to A_k notation. Rewrite pi(alpha_1,...,alpha_{n-1},beta) and pi(alpha_1,...,alpha_{n-1},alpha) as pi(alpha_1,...,alpha_{k-1},beta) and pi(alpha_1,...,alpha_{k-1},alpha) respectively.

---

### 7. Sample Variance Underestimation Claim Conflates Bias with Median Behavior

**Status**: [Pending]

**Quote**:
> caution is necessary, as even assuming finite variance (which is not guaranteed) the distribution of the weights may be so highly skewed that, even for very large $M$, $\sigma^2$ is (with high probability) underestimated by $\hat{\sigma}^2$, and/or the normal asymptotic theory does not apply.

**Feedback**:
The sample variance sigma-hat-squared is an unbiased estimator of sigma-squared whenever sigma-squared is finite, i.e., E[sigma-hat-squared] = sigma-squared for all M >= 2. The correct phenomenon is a median-underestimation effect: for highly right-skewed weight distributions, the distribution of sigma-hat-squared is itself extremely right-skewed, so the median of sigma-hat-squared lies far below sigma-squared, even though the mean equals sigma-squared. Rewrite 'sigma-squared is (with high probability) underestimated by sigma-hat-squared' as 'the median of sigma-hat-squared lies well below sigma-squared, so that sigma-hat-squared underestimates sigma-squared with high probability even though E[sigma-hat-squared] = sigma-squared,' to correctly characterize the statistical phenomenon and avoid implying sigma-hat-squared is a biased estimator.

---

### 8. Factor-of-17 Ratio Inconsistent with Reasonably Accurate SE Claim for theta=10.0

**Status**: [Pending]

**Quote**:
> For $\theta = 2.0$ and $\theta = 10.0$ the changes in the estimated standard error (by factors of about 21 and 17 respectively) between the long and short runs for $Q_{\theta}^{\mathrm{SD}}$ suggest that these standard errors are being estimated reasonably accurately.

**Feedback**:
The expected ratio under accurate SE estimation is sqrt(500) approximately 22.4. For theta=2.0 the observed ratio of about 21 is within 5% of 22.4, genuinely 'reasonably accurate.' For theta=10.0 the observed ratio of about 17 is 25% below 22.4, implying the short-run SE underestimates the true standard deviation by a similar factor. Grouping both values as 'reasonably accurate' obscures that Q_SD already shows signs of SE underestimation at theta=10.0. Rewrite to distinguish the two cases: 'For theta=2.0 the factor of about 21 is close to the expected sqrt(500) approximately 22, suggesting accurate SE estimation. For theta=10.0 the factor of about 17 is noticeably below 22, indicating some underestimation even for Q_SD at this value of theta.'

---

### 9. Short-Run Q_SD Point Estimate at theta=15.0 Is Severely Biased, Not Merely Imprecise

**Status**: [Pending]

**Quote**:
> In contrast, between the long and short runs for $Q_{\theta}^{\mathrm{SD}}$ with $\theta = 15.0$, the change in the estimated standard error is less than a factor of 2, indicating that (at least for the short run) the standard error severely underestimates the standard deviation in this case.

**Feedback**:
The text focuses exclusively on SE underestimation but does not note that the short-run point estimate itself is substantially biased relative to the long-run estimate. If the discrepancy between the short-run and long-run point estimates is many multiples of the short-run standard error, this confirms that weight skewness affects both the point estimate and its reported uncertainty at theta=15.0, a more serious problem than SE underestimation alone. Add a sentence quantifying the ratio of the point-estimate discrepancy to the short-run SE, confirming that the short-run Q_SD estimate at theta=15.0 is not merely imprecise but substantially biased downward relative to the long-run result.

---

### 10. Claim That Fluctuate Underestimates Likelihood Away from Driving Value Attributes Wrong Mechanism

**Status**: [Pending]

**Quote**:
> the surfaces obtained still tended to underestimate the relative likelihood away from the driving values used, thus giving a false impression of the tightness and/or position of the peak of the likelihood surface, presumably because $P_{\theta_{0}}(\tilde{\mathcal{Q}}|A_{n})$ is a poor approximation to $P_{\theta}(\tilde{\mathcal{Q}}|A_{n})$ in this range.

**Feedback**:
The authors attribute underestimation to P_{theta_0}(Q-tilde|A_n) being a poor approximation to P_{theta}(Q-tilde|A_n), but the immediately following sentence reveals the actual mechanism: Stephens has recently shown that for theta > 2*theta_0 the estimator has infinite variance. Infinite variance is a precise, stronger statement than 'poor approximation': the sample mean of weights is not a consistent estimator in the usual sense, and systematic underestimation is a consequence of the heavy-tailed weight distribution. The word 'presumably' further weakens the causal claim. Rewrite 'presumably because P_{theta_0}(Q-tilde|A_n) is a poor approximation to P_{theta}(Q-tilde|A_n) in this range' as 'because, as shown by Stephens, the IS weights have infinite variance for theta > 2*theta_0, causing the sample mean to systematically underestimate the true likelihood ratio in this regime.'

---

### 11. Incomplete Reference Stephens (199) Missing Year

**Status**: [Pending]

**Quote**:
> (In fact Stephens (199) has recently shown that for $\theta > 2\theta_{0}$ the estimator has infinite variance.)

**Feedback**:
The citation 'Stephens (199)' is missing the final digit(s) of the publication year, making it an unresolvable reference. This is a substantive theoretical result used to explain the poor performance of Fluctuate and extended in the discussion reply to Q_SD itself. The reference list must contain a complete entry so readers can locate and verify this claim. Rewrite '(In fact Stephens (199) has recently shown...' with the correct four-digit year restored, and ensure the corresponding References entry is complete.

---

### 12. Conclusion Softens Proven Infinite-Variance Result to May Be Extremely Challenging

**Status**: [Pending]

**Quote**:
> In principle IS methods based on a driving value of $\theta$ will tend to share this undesirable property, as designing a single IS function $Q_{\theta_{0}}$ which is universally efficient for all $\theta$ may be extremely challenging.

**Feedback**:
The discussion reply confirms that the infinite-variance result for Fluctuate can be extended to show that the variance of the IS weights is infinite for theta > 2*theta_0 regardless of sample size, and the authors state this applies to Q_SD as well. The phrase 'may be extremely challenging' misrepresents a proven impossibility as a practical difficulty. Rewrite 'designing a single IS function Q_{theta_0} which is universally efficient for all theta may be extremely challenging' as 'designing a single IS function Q_{theta_0} which is universally efficient for all theta is provably impossible: the variance of IS weights is infinite for theta > 2*theta_0, a result that applies to Q_SD as well as to the Fluctuate scheme,' because the discussion reply confirms this stronger result.

---

### 13. IS Underestimation Claim Conflates Infinite Variance with Skewness

**Status**: [Pending]

**Quote**:
> Since the IS function which these MCMC methods use is most efficient (in fact optimal) at $\theta_{0}$, and tends to become less efficient for $\theta$ away from $\theta_{0}$, the distribution of the importance weights tends to be more skewed for $\theta$ away from the $\theta_{0}$. As a result such methods will tend to underestimate the relative likelihood away from $\theta_{0}$, leading to an estimated curve which is artificially peaked about this driving value

**Feedback**:
IS estimators of the form (1/M) times the sum of w_i are unbiased in expectation for any proposal with adequate support, regardless of skewness. The actual mechanism for underestimation is that when weights have infinite variance (for theta > 2*theta_0 in Fluctuate), the sample mean is dominated by rare large values almost certainly unobserved in a finite run. This is a finite-sample phenomenon driven by infinite variance, not a consequence of skewness per se. Rewrite 'the distribution of the importance weights tends to be more skewed for theta away from theta_0. As a result such methods will tend to underestimate' as 'the variance of the importance weights tends to increase, and may become infinite, for theta away from theta_0. As a result, in any finite run, such methods will tend to underestimate,' because the distinction between infinite variance and mere skewness is critical for understanding when the estimator fails.

---

### 14. Q_SD Shares Driving-Value Problem but Range of Finite-Variance theta Is Never Established

**Status**: [Pending]

**Quote**:
> In principle IS methods based on a driving value of $\theta$ will tend to share this undesirable property, as designing a single IS function $Q_{\theta_{0}}$ which is universally efficient for all $\theta$ may be extremely challenging. Although this did not appear to cause major problems for our method in the examples considered here, we note that methods which combine the results of more than one IS function, such as bridge sampling (see for example Gelman and Meng (1998)) would produce more reliable results.

**Feedback**:
The paper concedes Q_SD shares the driving-value pathology, yet never establishes whether the infinite-variance threshold theta > 2*theta_0 applies to Q_SD or whether Q_SD has a wider finite-variance range. The NSE example uses theta_0 = 8.0 over theta in [0, 20], which would span the infinite-variance regime if the 2*theta_0 threshold applies. The phrase 'did not appear to cause major problems' is informal and unsupported by any diagnostic. Add a sentence specifying either (a) the range of theta relative to theta_0 for which Q_SD weights have finite variance, or (b) an explicit acknowledgment that this range is unknown, so readers can assess whether the NSE likelihood curves in Figures 4-5 are reliable across their full displayed range.

---

### 15. Count of Rooted Gene Trees Should Be S, Not S+1

**Status**: [Pending]

**Quote**:
> the likelihood for the data is the probability of the unrooted gene tree, which is the sum of the probabilities associated with each possible rooted gene tree. (There are  $S + 1$  such rooted gene trees, where  $S$  is the number of mutations in the data.)

**Feedback**:
Under the infinite sites model, each mutation labels a distinct edge of the unrooted gene tree. An unrooted tree with S mutations has exactly S edges, and rooting is equivalent to choosing an edge on which to place the root, giving exactly S rooted gene trees, not S+1. One obtains S+1 only if a stem edge is added by convention, but that is not a property of the unrooted tree itself. Readers might note that Griffiths and Tavare (1994b, 1995) define the unrooted gene tree as having S edges for S mutations, consistent with S rooted versions. Rewrite '(There are S+1 such rooted gene trees)' as '(There are S such rooted gene trees)' or add an explicit explanation of the stem-edge convention if S+1 is intentional.

---

### 16. Biased Truncation Conflated with Unbiased Rejection Control

**Status**: [Pending]

**Quote**:
> It may then be fruitful to apply the rejection control ideas of Liu et al. (1999), in which unpromising trees would be discarded before reaching the MRCA, with appropriate modifications of the weights of the undiscarded trees. (This is a more sophisticated version of the strategy of discarding trees with too many mutations which was used by Griffiths and Tavaré (1994a) and Nielsen (1997).)

**Feedback**:
Rejection control (Liu et al., 1999) discards low-weight particles at intermediate steps and compensates by upweighting survivors, preserving unbiasedness. By contrast, the Griffiths-Tavare/Nielsen strategy discards trees without any compensating weight correction, introducing systematic bias. These are not 'more' and 'less' sophisticated versions of the same idea: they differ in a fundamental property, namely unbiasedness. Rewrite the parenthetical as: 'Unlike rejection control, which preserves unbiasedness through weight correction, the strategy of Griffiths and Tavare (1994a) and Nielsen (1997) discards trees without compensating weight adjustments, introducing a bias whose magnitude depends on the fraction of probability mass in the discarded histories.'

---

### 17. Truncated Type Space Boundary Condition Alters the Stepwise Model Non-Trivially

**Status**: [Pending]

**Quote**:
> The implementation of our IS scheme is facilitated by centring the sample distribution near 10 repeats and truncating the type space $E$ to $\{0, 1, \dots , 19\}$ by insisting that all mutations to alleles of length 0 or 19 involve the gain or loss respectively of a single repeat. This truncation will make little difference to the likelihood of samples whose allele lengths are not too close to these boundaries.

**Feedback**:
The boundary condition makes allele 0 a reflecting boundary (forced +1 mutation) and allele 19 a reflecting boundary (forced -1 mutation), changing the stationary distribution of the mutation chain from the standard stepwise model. Interior alleles have symmetric plus-or-minus 1 transitions, but boundary alleles do not, yielding a uniform stationary distribution on {0,...,19} rather than the infinite-lattice stepwise model's stationary distribution. The claim that 'this truncation will make little difference' is plausible qualitatively but unquantified. It would be helpful to report the range of allele lengths in the NSE dataset and confirm the boundary distance is sufficient, because without this the truncation adequacy claim is unverified for the harder example.

---

### 18. Geometric Parameter in Multi-Locus Definition Inconsistent with Section 4 Definition 1

**Status**: [Pending]

**Quote**:
> According to definition 1, a draw from $\hat{\pi}(\cdot|A_{n})$ for this model may be made by choosing a chromosome from $A_{n}$ uniformly at random, and then applying $m$ mutations to this chromosome (each of which involves choosing a locus uniformly and changing the type at that locus according to $P$), where $m$ is geometrically distributed with parameter $l\theta/(n+l\theta)$.

**Feedback**:
Definition 1 in Section 4 specifies the geometric parameter as theta/(n+theta) for a single-locus model. The text asserts that the multi-locus extension simply substitutes l*theta for theta, giving l*theta/(n+l*theta). However, the type space is now k^l-dimensional with a product mutation structure, and it is not immediately obvious that this substitution is valid. The appendix provides no derivation showing that the product-locus structure leads to this specific geometric parameter, nor does it cite a proposition establishing this. Add a brief derivation or explicit cross-reference to the proposition in Section 4 that justifies replacing theta with l*theta in the geometric parameter for the product-locus model, because without it the starting point of the entire appendix calculation is unverified.

---

### 19. Equivalence to Poisson-Mixture Representation Requires Explicit Parameter Verification

**Status**: [Pending]

**Quote**:
> It follows from elementary properties of Poisson processes that this is equivalent to drawing a time $t$ from an exponential distribution with rate parameter 1, and then applying $m_{i}$ mutations to locus $i$ ($i=1, \dots, l$), where the $m_{i}$ are independent and Poisson distributed with mean $\theta t/n$, and the mutations at each locus are governed by transition matrix $P$.

**Feedback**:
The PGF of a Poisson(lambda) variable mixed over t drawn from Exp(1) is 1/(1+lambda-lambda*z), which is the PGF of a geometric with parameter 1/(1+lambda). For a single locus, lambda = theta/n gives geometric parameter n/(n+theta). The total count m = sum of m_i has PGF [n/(n+theta*(1-z))]^l by independence, which is a negative binomial, not a geometric. This is not the same marginal distribution as geometric(l*theta/(n+l*theta)) unless l=1. The claim that the two sampling procedures are equivalent is therefore not elementary and the derivation should be shown explicitly, because the stated equivalence conflates the distribution of the total count with the joint distribution of per-locus counts.

---

### 20. Equation (31) Integral Limits and Normalization of the Exponential Weight Not Stated

**Status**: [Pending]

**Quote**:
> \hat{\pi}(\beta|A_n) = \sum_{\alpha \in A_n} \frac{n_\alpha}{n} \int \exp(-t) F_{\alpha_1\beta_1}^{(\theta,t,n)} \cdots F_{\alpha_l\beta_l}^{(\theta,t,n)} \, \mathrm{d}t

**Feedback**:
The integral has no explicit limits of integration. From the Poisson-mixture representation, t should range over [0, infinity) with exp(-t) as the Exp(1) density. The omission matters because the Gaussian quadrature approximation in equation (33) replaces the integral of exp(-t) times the integrand with a weighted sum, and standard Gauss-Laguerre quadrature for integrals from 0 to infinity of e^{-t} f(t) dt uses weights that already absorb the e^{-t} factor, while other rules do not. It is not stated which quadrature rule is used, so it is unclear whether exp(-t) is absorbed into the quadrature weights in equation (33) or evaluated separately. Rewrite equation (31) with explicit limits from 0 to infinity and add a sentence after equation (33) specifying the quadrature rule and clarifying whether exp(-t) is absorbed into the weights.

---

### 21. NSE Dataset Description Inconsistent Regarding UEP Data Inclusion

**Status**: [Pending]

**Quote**:
> The NSE data set analysed here and in Wilson and Balding (1998) consisted of 60 Y-chromosomes with five microsatellite loci and a single unique event polymorphism (UEP) scored for each chromosome.

**Feedback**:
The discussant describes the NSE dataset as including a UEP scored for each chromosome, but Section 5.4 of the paper describes the IS analysis without mentioning UEPs. If UEP data were included in the Wilson and Balding (1998) micsat analysis but excluded from the Stephens and Donnelly IS analysis, the two methods are not being applied to identical datasets, which would compromise the comparison described as showing 'substantive agreement.' Add a clarification specifying whether the UEP data were included in the IS analysis, because if the two methods used different subsets of the data, the reported agreement is not a valid replication.

---
