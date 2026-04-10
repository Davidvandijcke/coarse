# Inference in molecular population genetics

**Date**: 03/13/2026
**Domain**: statistics/population_genetics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper proposes a new importance sampling (IS) method for estimating likelihoods under the coalescent with mutation. The core idea is to approximate the optimal IS proposal distribution by substituting an approximation π̂ for the unknown conditional sampling probabilities π. The method is demonstrated to improve efficiency over existing IS and MCMC approaches in several simulation studies, particularly for models like the infinite sites model. However, the theoretical and empirical validation of the key approximation, the scope of comparisons with alternative methods, and the robustness and scalability of the approach are not fully addressed.

Below are the most important issues identified by the review panel.

**Unverified quality and theoretical guarantees for the core approximation π̂**

The method's efficiency hinges on the approximation π̂(β|A_n) to the true conditional sampling probability π(β|A_n). While Proposition 1 shows π̂ equals π for parent-independent mutation and n=1, no general theoretical bounds on the approximation error are provided for other mutation models. The justification remains heuristic, and the performance claims ('several orders of magnitude improvement') depend entirely on this approximation being accurate. Readers might note that without a systematic analysis of the discrepancy between π̂ and π across a spectrum of models (e.g., stepwise mutation, asymmetric rates) or parameter ranges (e.g., high θ), the claim that Q_θ^SD is a 'practicable approximation' to the optimal proposal is unsupported. It would be helpful to include a simulation study quantifying this approximation error in tractable scenarios or to characterize the conditions under which the approximation is expected to be reliable.

**Incomplete and potentially unfair comparison with MCMC methods**

The paper positions IS as superior for 'constrained' problems while stating MCMC has an advantage for 'less constrained' ones, but the term 'constrained' is never formally defined. The comparative assessment appears based on a limited set of examples and may not reflect state-of-the-art MCMC implementations. Crucially, the MCMC comparisons (e.g., with FLUCTUATE) do not include rigorous convergence diagnostics (e.g., effective sample sizes, Gelman-Rubin statistics), so observed poor performance could stem from inadequate chain length or mixing rather than a fundamental limitation. The analysis also attributes MCMC inaccuracies to using a fixed driving value θ0, an implementation choice, without comparing against methods that jointly sample θ and the genealogy. To strengthen the claim, the authors should define 'constrained' empirically, ensure MCMC benchmarks are properly converged, and include a broader range of MCMC algorithms in the comparison.

**Lack of robustness analysis under model misspecification**

The methodology is developed under strict standard coalescent assumptions (constant population size, neutrality, no recombination, known mutation model). The paper briefly mentions extensions but does not test the robustness of inference when these assumptions are violated—a common scenario with real data. The behavior of the approximation π̂ and the resulting likelihood estimates under demographic changes (e.g., bottlenecks), selection, or recombination is unknown. Performance gains demonstrated under the true model might degrade or lead to biased estimates under misspecification. It would be helpful to include simulation studies where data are generated under a more complex model (e.g., population expansion) but analyzed assuming the simple model, to quantify the sensitivity and potential fragility of the proposed method.

**Scalability concerns and insufficient computational complexity analysis**

Efficiency is demonstrated on moderate-sized examples (n ≤ 60, type spaces like 2^10), but scalability to large genomic datasets is not evaluated. The cost of calculating π̂ scales with the size of the type space E (k^l for multi-locus models). While Appendix A presents a quadrature method to avoid a naive O(k^l) calculation, its accuracy and computational cost for large l (long sequences) or large k (e.g., microsatellite alleles) are not assessed. The claim that backward transition probabilities 'may be efficiently approximated' for the challenging NSE dataset is not substantiated with timing results or complexity analysis. For the method to be applicable to modern genomic studies, readers need a discussion of computational bottlenecks (e.g., computing M^(n) matrices) and an analysis of how runtime and memory scale with increasing sample size n and number of loci l.

**Underdeveloped diagnostics for importance sampling reliability**

The paper acknowledges that the IS weight distribution can be highly skewed, making standard error estimates unreliable and complicating decisions about run length. The proposed diagnostics—monitoring weight statistics and modeling the upper tail with extreme value theory—are speculative and not implemented or validated. For example, in Table 1, the standard error from Q_SD for θ=15 did not decrease as expected with more samples, indicating potential variance underestimation. Without robust, practical diagnostic tools, users cannot confidently assess the accuracy of their likelihood estimates. It would be helpful to develop and demonstrate a concrete diagnostic protocol, such as using multiple independent runs, reporting effective sample sizes, or applying and validating the proposed extreme value approach on the challenging examples presented.

**Inadequate treatment of practical data complexities like ascertainment bias and missing data**

The method conditions on the observed data A_n but does not address how to handle common real-data issues such as ascertainment bias (e.g., SNP discovery panels) or missing genotypes. Section 6.2 states that accommodating such designs is 'straightforward' in IS schemes but provides no details or examples. In practice, accounting for ascertainment is non-trivial and can significantly affect parameter estimates. The lack of a concrete methodology or demonstration for these scenarios limits the method's practical utility. The paper should either provide a clear implementation strategy for incorporating missing data and ascertainment bias—perhaps by modifying the likelihood or proposal distribution—or explicitly state these as limitations requiring future work, supported by a simulation example illustrating the consequences of ignoring them.

**Status**: [Pending]

---

## Detailed Comments (24)

### 1. Inconsistent mutation rate scaling in coalescent approximation

**Status**: [Pending]

**Quote**:
> Conditionally on the genealogical tree and the type of the MRCA, types change along different branches of the tree as independent continuous time Markov chains with rate  $\theta / 2 = N\mu / \nu^2$  and transition matrix  $P$  (see for example Donnelly and Tavaré (1995)).

**Feedback**:
The stated mutation rate in coalescent time units is ambiguous. For a haploid Wright–Fisher model (ν²=1), the standard coalescent mutation parameter is θ = Nμ, giving a mutation rate per lineage of θ. The given rate θ/2 corresponds to the diploid scaling θ = 2Nμ. Since the paper focuses on haploid models, this inconsistency could propagate into later formulas. It would be helpful to explicitly define θ = 2Nμ/ν² and state that the mutation rate per lineage is θ/2, or adjust the rate to θ if using haploid scaling.

---

### 2. Missing definition of π_θ(A_n|H) in missing-data formulation

**Status**: [Pending]

**Quote**:
> Writing
> 
> $$
> L(\theta) = \pi_{\theta}(A_n) = \int \pi_{\theta}(A_n|\mathcal{H}) \, P_{\theta}(\mathcal{H}) \, \mathrm{d}\mathcal{H}, \tag{4}
> $$
> 
> and noting that $\pi_{\theta}(A_n|\mathcal{H})$ is easily calculated (using equations (2)), suggests viewing this as a missing data, or data augmentation, problem with $\mathcal{H}$ being the missing data.

**Feedback**:
The text references 'equations (2)' for calculating π_θ(A_n|H), but these equations are not provided in the section. Without the definition of π_θ(A_n|H), readers cannot verify the claim that it is 'easily calculated'. This creates a gap in the methodological exposition. It would be helpful to include the relevant equations from Section 2 here or provide a clear cross-reference.

---

### 3. Incorrect naive estimator equation

**Status**: [Pending]

**Quote**:
> Expression (4) suggests a naive estimator of $L(\theta)$:<!-- PAGE BREAK -->Molecular Population Genetics 611
> 
> $$
> L(\theta) = \pi_{\theta}(A_n) \approx \frac{1}{M} \sum_{i=1}^{M} \pi_{\theta}(A_n | \mathcal{H}^{(i)}) \tag{5}
> $$
> 
> where $\mathcal{H}^{(1)}, \ldots, \mathcal{H}^{(M)}$ are independent samples from $P_{\theta}(\mathcal{H})$.

**Feedback**:
Equation (5) incorrectly presents a naive estimator. The left-hand side is the exact likelihood L(θ), but the right-hand side is an approximation. Moreover, the notation L(θ) = π_θ(A_n) ≈ ... uses the same symbol L(θ) on both sides, which is confusing. The estimator should be written as Ģ(θ) = (1/M) Σ π_θ(A_n | H^{(i)}), with a note that this is impracticable because π_θ(A_n | H) is zero for almost all H drawn from P_θ(H).

---

### 4. Missing definition of F(B_j) and chain dynamics in Griffiths-Tavaré recursion

**Status**: [Pending]

**Quote**:
> The first such method in this context was developed by Griffiths and Tavaré (1994a). They showed that by finding recursions for probabilities of interest the likelihood could be written in the form
> 
> $$
> L(\theta) = \pi_{\theta}(A_n) = E \left\{ \prod_{j=0}^{\tau} F(B_j) \,\Big| \, B_0 = A_n \right\} \tag{6}
> $$
> 
> where $B_0, B_1, \ldots, B_\tau$ is a particular set-valued Markov chain stopped the first time $\tau$ that it has cardinality 1.

**Feedback**:
The notation F(B_j) and the transition probabilities of the Markov chain B_j are not defined in this section, making equation (6) and the subsequent description of the Monte Carlo method ambiguous. Readers unfamiliar with Griffiths and Tavaré (1994a) cannot understand what is being simulated. It would be helpful to define F(B_j) (e.g., the probability of the event that transitions the chain from B_j to B_{j-1}) and specify the chain's transition probabilities, or provide a precise citation.

---

### 5. Algebraic error in derivation of mutation and coalescence probabilities

**Status**: [Pending]

**Quote**:
> From equation (22) we have
> 
> $$
> 1 = \sum_{\beta \in E} \frac{\hat{\pi}(\beta | H_i - \alpha)}{\hat{\pi}(\alpha | H_i - \alpha)} \left( \frac{\theta}{n - 1 + \theta} P_{\beta \alpha} + \frac{n_{\alpha} - 1}{n - 1 + \theta} \right).
> $$
> 
> Thus
> 
> $$
> \begin{array}{l}
> \frac{n_{\alpha}}{n} = \sum_{\beta \in E} \frac{\hat{\pi}(\beta | H_i - \alpha)}{\hat{\pi}(\alpha | H_i - \alpha)} \left( \frac{\theta}{n - 1 + \theta} \frac{n_{\alpha}}{n} P_{\beta \alpha} + \frac{n_{\alpha}}{n} \frac{n_{\alpha} - 1}{n - 1 + \theta} \right) \\
> = \sum_{\beta \in E} \frac{\hat{\pi}(\beta | H_i - \alpha)}{\hat{\pi}(\alpha | H_i - \alpha)} C^{-1} \frac{\theta}{2} n_{\alpha} P_{\beta \alpha} + \frac{1}{\hat{\pi}(\alpha | H_i - \alpha)} C^{-1} \binom{n_{\alpha}}{2} \\
> = p_{\mathrm{m}}(\alpha) + p_{\mathrm{c}}(\alpha). \quad \square
> \end{array}
> $$

**Feedback**:
The step from the first to the second equality in the 'Thus' array is not clearly justified and omits the factor 1/π̂(α|H_i - α) in the second term. The correct derivation should show: (n_α/n) * (n_α-1)/(n-1+θ) = [n_α(n_α-1)]/[n(n-1+θ)] = (2 * binom(n_α,2))/(2C) = binom(n_α,2)/C. Multiplying by 1/π̂(α|H_i - α) yields the term in the final line. The presentation is confusing and could lead readers to think the algebra is wrong.

---

### 6. Incomplete proof for property (b) (reversibility, n=1)

**Status**: [Pending]

**Quote**:
> Proof of property (b). Consider the coalescence tree which describes the ancestry of two sampled chromosomes (labelled 1 and 2), and denote by $m_1$ and $m_2$ respectively the number of mutations between the MRCA and chromosomes 1 and 2. It follows from the reversibility of $P$ that at stationarity, conditionally on $m_1$ and the type $\alpha_1$ of chromosome 1, the type of the MRCA is $\beta$ with probability $(P^{m_1})_{\alpha_1\beta}$. Conditionally on the type $\gamma$ of the MRCA, and $m_2$, the type of chromosome 2 is $\beta$ with probability $(P^{m_2})_{\gamma\beta}$. Thus, conditionally on $\alpha_1$, $m_1$ and<!-- PAGE BREAK -->M. Stephens and P. Donnelly
> 
> $m_{2}$, the type of chromosome 2 is $\beta$ with probability $(P^{m_1 + m_2})_{\alpha_1\beta}$. The result follows from the fact that $m_{1} + m_{2}$ is geometric with parameter $\theta /(1 + \theta)$, independently of $\alpha_{1}$.

**Feedback**:
The proof sketch is incomplete. It states that m_1+m_2 is geometric with parameter θ/(1+θ) without justification. Under the coalescent, the coalescence time T for two lineages is exponential with mean 1. Given T=t, the number of mutations on each branch is Poisson with mean (θ/2)t, so m_1+m_2 given T is Poisson with mean θt. Marginalizing over T yields a geometric distribution. This standard result should be cited or briefly derived to make the proof self-contained.

---

### 7. Misleading claim about MCMC yielding only relative likelihoods

**Status**: [Pending]

**Quote**:
> In contrast with the Griffiths-Tavaré scheme described above, and the IS methods described below, these MCMC approaches give only relative, rather than absolute, likelihood surfaces (although methods such as those reviewed by Raftery (1996) may allow the likelihood itself to be computed).

**Feedback**:
This claim is misleading. The Griffiths-Tavaré IS scheme and the authors' IS scheme both estimate the likelihood up to an unknown constant (the proposal normalizing constant), yielding relative likelihoods. MCMC methods sample from the posterior P(θ|A_n); dividing by the prior gives the likelihood up to the same constant. Thus, both IS and MCMC can produce relative likelihood surfaces. The statement creates a false dichotomy. It would be helpful to clarify that both methods typically estimate the likelihood up to a constant, and that 'absolute' likelihood requires additional computation (e.g., marginal likelihood estimation).

---

### 8. Incorrect scaling factor for standard error reduction

**Status**: [Pending]

**Quote**:
> The estimated likelihood values using this larger sample were very close to those in Fig. 2(b) (data not shown), and the standard errors were smaller by about a factor of 31, suggesting that the standard errors in the smaller sample are accurately reflecting the standard deviation of the weights (they should in theory be reduced by a factor of √1000 ≈ 32).

**Feedback**:
The text incorrectly states the theoretical reduction factor. The sample sizes are 10,000 and 10,000,000, a ratio of 1000. The standard error scales as 1/√(sample size), so the expected reduction factor is √1000 ≈ 31.62, not √1000 ≈ 32. The observed factor of 31 is consistent with √1000. The phrasing 'they should in theory be reduced by a factor of √1000 ≈ 32' is ambiguous and could imply the factor is 32 rather than √1000. It would be clearer to state: 'the standard errors should be reduced by a factor of √(10,000,000/10,000) = √1000 ≈ 31.6.'

---

### 9. Ambiguous truncation boundary condition for stepwise mutation model

**Status**: [Pending]

**Quote**:
> The implementation of our IS scheme is facilitated by centring the sample distribution near 10 repeats and truncating the type space E to {0, 1, . . ., 19} by insisting that all mutations to alleles of length 0 or 19 involve the gain or loss respectively of a single repeat.

**Feedback**:
The description of the truncation boundary condition is ambiguous. 'Mutations to alleles of length 0' could mean mutations that land on allele 0 (requiring a loss from allele 1) or mutations originating from allele 0. The intended meaning is likely that when the allele is at the boundary, the mutation direction is forced to keep it within the truncated space. It would be clearer to state: 'from allele 0, a mutation can only be a gain to 1; from allele 19, a mutation can only be a loss to 18.'

---

### 10. Contradictory accuracy claim for MCMC vs IS in microsatellite example

**Status**: [Pending]

**Quote**:
> There are small but noticeable differences in the relative likelihood curves obtained by using our method and micsat. Further investigation (more runs of each method) suggested that the curve obtained by using micsat is more accurate.

**Feedback**:
This statement contradicts the earlier claim of superior efficiency for the IS method. If micsat produces a more accurate curve, then the IS method, despite using many more samples, may have a bias or higher variance. The paper does not explain how 'more accurate' was determined (e.g., comparison to a known truth or convergence diagnostics). This undermines the conclusion that 'our IS method is considerably more efficient'. The authors should reconcile this by explaining the basis for the accuracy assessment and qualifying the efficiency claim.

---

### 11. Inconsistent geometric distribution parameter in multilocus definition

**Status**: [Pending]

**Quote**:
> According to definition 1, a draw from $\hat{\pi}(\cdot|A_n)$ for this model may be made by choosing a chromosome from $A_n$ uniformly at random, and then applying $m$ mutations to this chromosome (each of which involves choosing a locus uniformly and changing the type at that locus according to $P$), where $m$ is geometrically distributed with parameter $l\theta/(n+l\theta)$.

**Feedback**:
The geometric parameter appears incorrect. For a multilocus model with l loci, the total mutation rate per chromosome is lθ/2. The probability that the next event backwards is a mutation (rather than coalescence) is (lθ/2) / (lθ/2 + n/2) = lθ/(lθ + n). The denominator should be lθ + n, not n + lθ (order does not matter), but the parameter should be lθ/(lθ + n). The given parameter lθ/(n + lθ) is algebraically equivalent, but the standard form matches the single-locus case when l=1: θ/(θ + n). The text should use the form lθ/(lθ + n) for consistency with Definition 1.

---

### 12. Inconsistent Poisson mean in multilocus equivalence derivation

**Status**: [Pending]

**Quote**:
> It follows from elementary properties of Poisson processes that this is equivalent to drawing a time $t$ from an exponential distribution with rate parameter 1, and then applying $m_i$ mutations to locus $i$ ($i=1, \ldots, l$), where the $m_i$ are independent and Poisson distributed with mean $\theta t/n$, and the mutations at each locus are governed by transition matrix $P$.

**Feedback**:
The mean of the Poisson distribution for m_i is stated as θ t/n. However, from the coalescent model, the mutation rate per lineage per locus is θ/2. The expected number of mutations at a given locus on a single lineage over time t is (θ/2) t. The factor 1/n is not justified. The equivalence claimed between the geometric mutation process and independent Poissons with mean θ t/n is not mathematically correct as stated. The mean should be (θ/2) t, or the time t should be drawn from a different exponential distribution. This inconsistency affects the subsequent integral approximation (31).

---

### 13. Missing clarification on quadrature weight function

**Status**: [Pending]

**Quote**:
> The integral in equation (31) may be approximated by using Gaussian quadrature (see for example Evans (1993)):
> 
> $$
> \hat{\pi}(\beta|A_n) = \sum_{\alpha \in A_n} \sum_{i=1}^{s} \frac{n_{\alpha}}{n} w_i F_{\alpha_1\beta_1}^{(\theta,t_i,n)} \cdots F_{\alpha_l\beta_l}^{(\theta,t_i,n)} \tag{33}
> $$
> 
> where $t_1, \ldots, t_s$ are the quadrature points, and $w_1, \ldots, w_s$ are the corresponding quadrature weights.

**Feedback**:
The quadrature approximation in equation (33) uses weights w_i but does not specify the weight function. The integral in (31) is ∫_0^∞ exp(-t) g(t) dt, so the quadrature should be for the weight function exp(-t) on (0,∞). The text should clarify that t_i and w_i are the points and weights for this specific weight function, to avoid confusion with other quadrature rules.

---

### 14. Incorrect recursion equation for general mutation matrix

**Status**: [Pending]

**Quote**:
> The set of equations obtained by considering the first event back in the coalescent process is
> 
> $$p(n) = \frac{\theta}{n + \theta - 1} \left\{ \sum_{\alpha = 1}^d \sum_{\beta = 1}^d \frac{n_{\beta} + 1 - \delta_{\alpha \beta}}{n} p(n + e_{\beta} - e_{\alpha}) \right\} + \frac{n - 1}{n + \theta - 1} \sum_{\{\alpha : n_{\alpha} > 0\}} \frac{n_{\alpha} - 1}{n - 1} p(n - e_{\alpha}) . \tag{34}$$

**Feedback**:
Equation (34) appears to be specific to the parent-independent mutation (PIM) model, where P_{αβ} = π_β. For a general mutation matrix P, the term inside the braces should involve (n_α/n) P_{αβ}, not (n_β+1-δ_{αβ})/n. Since the section describes the original Griffiths-Tavaré method, which works for general mutation matrices, presenting the PIM-specific form without clarification could mislead readers. It would be helpful to either present the general form or note that this is the PIM case.

---

### 15. Unsubstantiated claim about MCMC mixing advantage with joint parameter updates

**Status**: [Pending]

**Quote**:
> Further, we believe that MCMC methods II (see Section 3) which move around the parameter space (i.e. that allow θ to vary in the cases that we consider here) will tend to mix better over tree space and are an efficient method of performing either Bayesian or likelihood inference for the parameters, concentrating computational effort on regions with reasonable support from the data (this advantage becoming more marked when the dimension of the parameter space is higher).

**Feedback**:
The claim that MCMC methods which jointly update θ and the tree mix better over tree space is not supported by evidence in the paper and may be incorrect. Mixing over tree space depends on the proposal distribution for tree updates, not on whether θ is fixed or jointly sampled. The paper's own examples show efficient IS with fixed θ, and no comparison is made to joint MCMC schemes. Without a demonstration, this is an unsubstantiated conjecture. It would be more accurate to state that joint updates may improve efficiency for parameter inference, not necessarily tree mixing.

---

### 16. Unsubstantiated claim about extreme value procedure for weight diagnostics

**Status**: [Pending]

**Quote**:
> A possible procedure, which appears promising on initial investigation, is to model the distribution of the weights by using distributions developed in extreme value theory for highly skewed distributions (this idea has been suggested independently by Shephard(2000)). In particular we propose fitting a generalized Pareto distribution (see Davison and Smith (1990) for example) to the weights above some threshold, and using a parametric bootstrap to estimate confidence intervals for the mean of the weights (i.e. the estimate of the likelihood). Although this procedure may be inexact, it should better represent the uncertainty in the estimate than any current method that we are aware of.

**Feedback**:
The claim that fitting a generalized Pareto distribution (GPD) to the upper tail of the importance weights 'should better represent the uncertainty in the estimate than any current method that we are aware of' is speculative and lacks justification. Extreme value theory provides asymptotic justification for i.i.d. sequences, but its applicability to importance weights from this sequential algorithm is not established. The statement 'appears promising on initial investigation' suggests exploratory analysis, but no results are presented. Without evidence or a reference, the claim is unsubstantiated. The authors should either provide a citation or preliminary results, or tone down the claim to reflect its hypothetical nature.

---

### 17. Inconsistent claim about method applicability to larger data sets

**Status**: [Pending]

**Quote**:
> methods described in the paper are becoming routinely used by biologists for much larger data sets, and in some more complex settings.

**Feedback**:
This claim appears to contradict the paper's own assessment of scalability limitations. The paper demonstrates the method on moderate-sized examples (n ≤ 60) and acknowledges computational bottlenecks, but does not provide evidence that the methods are routinely used on 'much larger data sets' or in more complex settings. This creates an internal inconsistency between the optimistic claim here and the technical limitations discussed elsewhere. It would be more accurate to state that the methods show promise for larger data sets, though further development is needed to address scalability challenges.

---

### 18. Vague definition of 'constrained' genetic structure

**Status**: [Pending]

**Quote**:
> In problems in which the genetic structure is ‘constrained' (in a sense which will become clearer later) IS seems competitive with, or superior to, these MCMC approaches. The latter seem to have an advantage for less constrained problems.

**Feedback**:
The term 'constrained' is used to qualitatively compare IS and MCMC but is not defined, even with a promise that it will become clearer later. Throughout the paper, 'constrained' is not formally defined, which leaves the comparison ambiguous. The reader is left to infer meaning from examples, which is insufficient for a methodological claim. It would be helpful to at least hint at what 'constrained' means (e.g., problems with low mutation rate, small type space, or strong genealogical correlations) or reference the later sections where the concept is illustrated.

---

### 19. Unsubstantiated claim about 'several orders of magnitude' improvement

**Status**: [Pending]

**Quote**:
> Our new approach is most naturally compared with the original method of Griffiths and Tavaré. It represents a substantial improvement in efficiency (typically by several orders of magnitude) and accuracy.

**Feedback**:
The claim of 'several orders of magnitude' improvement in efficiency and accuracy is a quantitative performance statement that should be substantiated within the introduction. At this point, no evidence has been provided. While later sections present empirical comparisons, the introduction makes this strong claim without qualification. This could be misinterpreted as a universal guarantee rather than a result demonstrated under specific models and parameter ranges shown later. To avoid overstatement, qualify the claim by noting that the improvement is demonstrated in subsequent sections under specific models.

---

### 20. Incorrect factor for standard error reduction in Table 1 analysis

**Status**: [Pending]

**Quote**:
> We can use the standard errors from the long run of $Q_{\theta}^{\mathrm{SD}}$ to check whether the standard errors for the shorter run accurately reflect the standard deviation of the importance weights. If they do then the longer run should result in standard errors which are smaller by a factor of $\sqrt{500} \approx 22$. For $\theta = 2.0$ and $\theta = 10.0$ the changes in the estimated standard error (by factors of about 21 and 17 respectively) between the long and short runs for $Q_{\theta}^{\mathrm{SD}}$ suggest that these standard errors are being estimated reasonably accurately.

**Feedback**:
The expected scaling factor is √(10^7 / 20000) = √500 ≈ 22.36. The observed factor for θ=10.0 is about 17, which is notably lower than √500, suggesting the short-run standard error may be an underestimate. The claim that this suggests 'reasonably accurate' estimation is too strong for θ=10.0. It would be more accurate to state that for θ=2.0 the factor is close to √500, but for θ=10.0 the discrepancy indicates possible underestimation of variability in the short run.

---

### 21. Missing acknowledgment of non-PIM model in asymmetric mutation example

**Status**: [Pending]

**Quote**:
> The transition matrix governing mutations at each position was
> 
> $$
> P = \left( \begin{array}{cc} 0.5 & 0.5 \\ 0.1 & 0.9 \end{array} \right). \tag{28}
> $$
> 
> Note that this model has $2^{10}$ different alleles, and so the calculation of the quantities $\hat{\pi}(\beta | A_n)$ using equations (18) and (19) appears to be computationally daunting.

**Feedback**:
The mutation matrix P is asymmetric, so this is a parent-dependent mutation model (not parent-independent). The method's approximation π̂ is exact only for parent-independent mutation (PIM). For this asymmetric model, the accuracy of π̂ is not theoretically guaranteed, and the efficiency gains demonstrated rely on the approximation being good in practice. The section does not acknowledge that this is a non-PIM model, which is a key context for interpreting the results. Readers might incorrectly assume the method is exact for all models. Add a sentence noting that this is a non-PIM model and the results demonstrate the approximation's efficacy.

---

### 22. Ambiguous reference to 'remark 2' in discussion of computational properties

**Status**: [Pending]

**Quote**:
> Many of them were very much more computationally intensive than the scheme that we presented here (which benefits considerably from the computationally convenient properties discussed in remark 2) and none of them produced a consistent improvement in efficiency, even when efficiency was measured per iteration and took no account of the amount of computation required.

**Feedback**:
The text refers to 'remark 2' but no such remark is provided in the section text. This creates ambiguity for the reader trying to understand which computational properties are being referenced. The authors should either define the remark in this section or provide a clear cross-reference (e.g., section and equation numbers) to the specific properties, such as those in Proposition 1 and equation (23).

---

### 23. Inconsistent notation for probability of data given history in discussion

**Status**: [Pending]

**Quote**:
> the factor $\pi_{\theta}(A_{n}|\mathcal{H}^{(i)})$ in estimator (9)

**Feedback**:
Throughout the paper, the likelihood given a history is denoted P_θ(A_n | H), not π_θ(A_n | H). For example, in equation (9), the estimator is (1/M) Σ_{i=1}^M P_θ(A_n | H^{(i)}) / Q_θ(H^{(i)}). The notation π_θ(·|·) is reserved for conditional sampling distributions (e.g., π(β | A_n)). Using π_θ(A_n | H^{(i)}) here is inconsistent with the paper's own notation and could cause confusion. This appears to be a typographical error.

---

### 24. Tautological equation in derivation of π̂

**Status**: [Pending]

**Quote**:
> and so $\hat{\pi} = \hat{\pi}$.

**Feedback**:
The equation 'π̂ = π̂' is a tautology and appears to be an OCR or typesetting error. In context, the preceding text discusses the matrix M^(n) and states that M^(n) = (1 - λ_n)(I - λ_n P)^{-1}, and then concludes 'and so π̂ = π̂.' This is nonsensical. Based on the surrounding material, the intended conclusion is likely that the derived form of M^(n) leads to the explicit formula for π̂(β|A_n) given earlier (e.g., equation (22)). The tautology should be replaced with a meaningful statement.

---
