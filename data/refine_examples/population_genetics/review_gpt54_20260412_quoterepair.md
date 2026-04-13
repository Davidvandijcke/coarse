# Inference in molecular population genetics

**Date**: 04/12/2026
**Domain**: statistics/biostatistics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper has a strong central idea: recasting existing coalescent likelihood algorithms as importance sampling and using time reversal to motivate a better proposal. The main concerns are not about whether this idea is interesting, but whether the empirical evidence and theoretical support are broad enough for the paper’s larger claims about efficiency, reliability, and general applicability across molecular population-genetic settings.

Theorem 1 and the resulting proposal construction are the paper’s main strengths, and the paper does a good job connecting genealogical structure to Monte Carlo design. The empirical sections also make a persuasive case that the new sampler can outperform the canonical Griffiths-Tavare proposal on several stylized examples. What is less convincing is the jump from those examples to broad claims about reliable inference in practical settings, especially when Monte Carlo diagnostics, model robustness, and fairness of method comparisons are all only partially developed.

**Approximate proposal is justified too weakly outside special cases**

The central methodological move is the replacement of the exact conditional sampling distribution \(\pi(\cdot\mid A_n)\) in Theorem 1, equations (15), by the approximation \(\hat\pi(\cdot\mid A_n)\) in Definition 1, equation (17), yielding the operational proposal in equation (25). But the paper proves exactness only for parent-independent mutation and for the \(n=1\) reversible case in Proposition 1(a)-(b), plus a consistency-style property in Proposition 1(d). There is no bound showing that \(\hat\pi\) is close to \(\pi\) in the regimes that matter for the applications, nor any result linking that closeness to variance reduction of the resulting IS weights. That gap matters because the headline contribution is not just a new valid sampler, but a sampler that is said to be much more efficient in realistic non-PIM settings. A stronger revision would add either theoretical error control for the substitution \(\pi\to\hat\pi\), or a systematic simulation study showing when the approximation is accurate and when it breaks down as mutation rates, sample sizes, and mutation matrices vary.

**Monte Carlo reliability is acknowledged as fragile but not resolved**

The paper is candid that the importance weights may be highly skewed and that finite variance is not guaranteed; see Section 5, especially the discussion preceding Section 5.1, Section 5.2, and Section 20 on diagnostics. That honesty is welcome, but it leaves a major hole in the paper’s inferential claims because many likelihood surface estimates are then supported mainly by repeated runs and informal visual stability checks rather than a validated error analysis. In Section 5 the authors explicitly state that they "have not performed the larger scale simulation studies that are necessary to obtain accurate estimates of Monte Carlo errors," yet the abstract and Section 17 still speak in broad terms about substantial gains in efficiency and accuracy. This matters because an IS method can look excellent precisely in cases where rare, unobserved weights dominate the true variance, and the paper itself gives examples of this pathology. The paper would be much stronger if it turned Section 20 from a speculative diagnostics discussion into an actual validation exercise, with repeated-run coverage studies, effective sample size behavior, and explicit failure cases for both the old and new proposals.

**Comparisons with competing MCMC methods are not controlled enough to support broad conclusions**

The comparison with existing MCMC methods in Sections 5.3 and 5.4 is informative, but it is not designed tightly enough to sustain the paper’s broader framing about when IS or MCMC is preferable. For `Fluctuate`, the chains are short by modern standards for such rough likelihood surfaces, and the reported behavior is highly sensitive to the driving value and seed; for `micsat`, Section 5.4 explicitly says the default tuning parameters were used and that the MCMC scheme could likely be improved. In the larger NSE example the paper then finds, by its own account, that the MCMC curve "is more accurate," which cuts against the stronger efficiency narrative in the abstract and Section 17. Readers are therefore left unsure whether the reported differences reflect deeper advantages of the sampling representation, or simply unequal tuning effort and unequal use of diagnostics across methods. A revision should either narrow the claims about IS versus MCMC, or provide a more controlled benchmark with comparable tuning, multiple independent runs for every method, and a common metric that includes both CPU time and Monte Carlo error at matched accuracy.

**Real-data examples lean on biological assumptions that are too strong for the claims being made**

Section 3 sets up the inferential framework under neutrality, panmixia, no recombination over the region of interest, and often a simple mutation model with known \(P\). Those assumptions are serviceable for a methodological paper, but the real-data applications in Sections 5.4 and 5.5 do not do enough to show that the conclusions are stable when the assumptions are strained. The NSE microsatellite example pools samples from Nigeria, Sardinia, and East Anglia, which makes population structure an obvious concern, yet the analysis is still framed under a single randomly mating population model with common mutation behavior across loci. Likewise, the stepwise microsatellite model and the infinite-sites assumption are both treated as if they mainly affect implementation, when in practice they can change the genealogy-likelihood connection in ways that matter for inference on \(\theta\). This matters because the paper’s framing is about inference in molecular population genetics, not just about a computational trick under idealized textbook models. At minimum, the revision should make the scope much narrower in the abstract and conclusions, and add sensitivity analyses showing how the main real-data likelihood surfaces shift under alternative mutation or population-structure assumptions.

**The infinite-sites extension is introduced by analogy rather than derived with the same rigor as the main method**

The paper’s most rigorous development is for countable type spaces with a stationary mutation chain, culminating in Theorem 1 and Proposition 2. In Section 5.5, however, the infinite-sites model moves to an uncountable type space, loses reversibility, and drops back to an argument "by analogy with proposition 2" rather than a derivation parallel to equations (15) and (25). The authors acknowledge that technical challenges are not insurmountable but then proceed with a heuristic sampler whose efficiency is demonstrated empirically rather than justified from the target conditional distribution. That is a substantial shift, because the paper presents the infinite-sites case as one of its applications and uses it to support the broader claim that the new IS viewpoint extends naturally to important data types. The fix is straightforward conceptually: either supply a theorem for the infinite-sites proposal with its support and weight formula made explicit, or label Section 5.5 much more clearly as a heuristic adaptation whose correctness is only at the level of a valid IS construction, not an approximation closely tied to the optimal proposal.

**Implementation shortcuts in high-dimensional sequence and multilocus settings are not validated adequately**

Appendix A is doing a lot of work for the sequence and multilocus applications, because the exact matrices implied by equations (18) and (19) are computationally infeasible when the state space is large. The workaround uses an exponential-time representation, Gaussian quadrature with \(s=4\) points, and finite approximations to the matrices in equation (32), after which the paper states that the approximation to \(\hat\pi(\cdot\mid\cdot)\) can be "rather rough" but still yields a consistent IS estimator. Consistency of the estimator is not the main issue here; efficiency is. A rough approximation may be formally valid yet still distort the proposal enough to erase the very variance gains that motivate the method, and the paper does not isolate how much of the reported performance depends on the Appendix A approximation error. A revision should report approximation diagnostics for Appendix A itself, for example by comparing quadrature settings or exact calculations on smaller state spaces, so readers can separate the proposal idea from the numerical shortcut used to implement it.

**No tractable worked example of the optimal proposal**

The paper characterizes the optimal backward kernel in Theorem 1, but readers never see that kernel worked out in a concrete non-PIM model where exact calculations are still feasible. That leaves the main conceptual contribution a bit abstract: one can read the formula, yet not learn what the time-reversal argument actually implies in a fully specified population-genetic example. This matters because the paper is selling more than an algorithmic tweak; it is claiming a new way to think about coalescent likelihood computation. A natural addition would be a small finite-state mutation model, such as a three-allele reversible chain or a two-site binary sequence model with \(n=2\) or \(n=3\), for which \(\pi(\cdot\mid A_n)\), \(q^*_{\theta}\), \(q^{\mathrm{GT}}_{\theta}\), and \(q^{\mathrm{SD}}_{\theta}\) can all be computed exactly by enumeration. Then the paper could show, for one observed configuration, how the optimal kernel shifts probability mass toward genealogies that the Griffiths-Tavar\'e sampler neglects, and how closely the Stephens-Donnelly approximation tracks that exact benchmark.

**No repeated parameter-recovery study for \(\theta\)**

The applications show that the new sampler can estimate likelihood curves more stably on a handful of datasets, but they stop short of demonstrating end-to-end inferential performance for the parameter the paper says it targets. In a methods paper on likelihood-based inference, readers will want to know whether the improved likelihood approximation actually yields better estimation of \(\theta\), not only prettier curves. A single simulated dataset per setting cannot answer that, especially in a field where the likelihood itself can be flat or irregular. The missing piece is a repeated simulation study under the models already used in Sections 5.2-5.4: generate, say, 100 datasets at fixed \(\theta\) values under the binary-sequence model in equation (28) and the stepwise microsatellite model, then report bias, spread, and interval coverage for the MLE or a likelihood-based confidence set using \(Q^{\mathrm{SD}}\), \(Q^{\mathrm{GT}}\), and the relevant MCMC competitor. That would show whether the several-orders-of-magnitude efficiency gain translates into more reliable inference rather than only lower Monte Carlo noise for one example.

**Driving-value choice is left without an implementation recipe**

The paper repeatedly emphasizes practical guidance, yet it never gives a concrete procedure for choosing the driving value \(\theta_0\) or for combining information across several \(\theta_0\) values when one proposal is inadequate over the full likelihood surface. That omission is important because the usefulness of equations (12) and the relative-likelihood comparisons depends directly on this choice, and the paper itself notes that estimators can become misleading away from the driving value. As written, a practitioner learns that the issue exists but not how to handle it in an actual analysis. A complete methods paper should include at least one operational workflow: for example, a short pilot run on a coarse grid of \(\theta_0\in\{0.5,1,2,4,8,16\}\), followed by bridge-sampling or weighted combination of the proposals near the high-likelihood region, with the resulting combined curve compared against any single-\(\theta_0\) run. Showing this on the sequence example of Fig. 2 or the microsatellite example of Fig. 5 would directly support the paper's claim to offer practical insight into when these Monte Carlo schemes can be trusted.

**Recommendation**: major revision. The paper has a real methodological contribution, especially in its characterization of the optimal proposal and in showing why the canonical Griffiths-Tavare sampler can fail badly. But the current version overreaches relative to the evidence: Monte Carlo reliability is not established rigorously, comparisons with competing methods are only partly controlled, and several biologically important applications rely on untested modeling assumptions or heuristic extensions.

**Key revision targets**:

1. Provide stronger support for the substitution of \(\hat\pi(\cdot\mid A_n)\) for \(\pi(\cdot\mid A_n)\), either through theoretical error bounds or a systematic simulation study mapping where the approximation succeeds and fails.
2. Add a serious Monte Carlo validation section with repeated-run experiments, diagnostics for weight degeneracy, and empirical coverage or stability checks for estimated likelihood surfaces and standard errors.
3. Rework the MCMC comparisons so they are genuinely comparable across methods, including tuning, multiple seeds, matched computational budgets, and matched accuracy criteria.
4. Either derive the infinite-sites proposal with the same rigor as the countable-state-space case or explicitly downgrade Section 5.5 to a heuristic extension and narrow the associated claims.
5. Add robustness analysis for the real-data examples, especially sensitivity to mutation-model choice, population structure, and the assumption of no recombination or common mutation behavior across loci.

**Status**: [Pending]

---

## Detailed Comments (10)

### 1. Mutation Law Double-Counts Self-Transitions

**Status**: [Pending]

**Quote**:
> Independently of all other events, the genetic type of each progeny of a chromosome of type α ∈ E is α with probability 1 - μ, and β ∈ E with probability μP_{αβ}, i.e. mutations occur at rate μ per chromosome per generation, according to a Markov chain with transition matrix P.

**Feedback**:
This offspring law is not normalized if diagonal entries of P are allowed, and later the paper explicitly allows P_{\alpha\alpha}>0. As written, type α is reached through both the no-mutation term and the mutation term, so the total mass becomes 1+\mu P_{\alpha\alpha}. The sentence should distinguish β=α from β\neq α, for example by stating that the offspring type is α with probability 1-\mu+\mu P_{\alpha\alpha} and β\neq α with probability \mu P_{\alpha\beta}.

---

### 2. Metropolis-Hastings Needs the Full Target Kernel

**Status**: [Pending]

**Quote**:
> . If $\mathcal{T}$ represents missing data for which $\pi_{\theta}(A_n | \mathcal{T})$ is (relatively) easy to calculate, then it is straightforward to use the Metropolis–Hastings algorithm to construct a Markov chain with stationary distribution $P_{\theta}(\mathcal{T} |

**Feedback**:
This skips one ingredient. Metropolis-Hastings needs the posterior kernel P_{\theta}(\mathcal{T},A_n)=\pi_{\theta}(A_n\mid\mathcal{T})P_{\theta}(\mathcal{T}) up to proportionality, not only the conditional likelihood term \pi_{\theta}(A_n\mid\mathcal{T}). The sentence would be correct if it said that the joint density, or equivalently the posterior kernel, is easy to evaluate.

---

### 3. Equation (7) Needs a Support Condition

**Status**: [Pending]

**Quote**:
>
>
> $$
> \begin{aligned}
> \frac{L(\theta)}{L(\theta_0)} &= \frac{ \int P_{\theta}(\mathcal{T}, A_n) \, \mathrm{d}\mathcal{T} }{P_{\theta_0}(A_n)} \\
> &= \int \frac{ P_{\theta}(\mathcal{T}, A_n) }{P_{\theta_0}(\mathcal{T}, A_n)} \, P_{\theta_0}(\mathcal{T} | A_n) \, \mathrm{d}\mathcal{T} \\
> &\approx \frac{1}{M} \sum_{i=1}^{M} \frac{ P_{\theta}(A_n, \mathcal{T}^{(i)}) }{P_{\theta_0}(A_n, \mathcal{T}^{(i)})}, \tag{7}
> \end{aligned}
> $$

**Feedback**:
The identity is valid only when histories with positive mass under P_{\theta}(\mathcal{T},A_n) also lie in the support of P_{\theta_0}(\mathcal{T},A_n). Without that, the ratio is undefined on part of the target support and the displayed integral misses positive contributions. A short support assumption after the formula would fix this cleanly.

---

### 4. Equation (12) Also Requires Common Support

**Status**: [Pending]

**Quote**:
> it appears to be more efficient to reuse samples from a single IS function. This is in theory straightforward: for any fixed $\theta_0$ we have
>
> $$
> L (\theta) \approx \frac {1}{M} \sum_ {i = 1} ^ {M} \pi_ {\theta} \left(A _ {n} \mid \mathcal {H} ^ {(i)}\right) \frac {P _ {\theta} \left(\mathcal {H} ^ {(i)}\right)}{Q _ {\theta_ {0}} \left(\mathcal {H} ^ {(i)}\right)}, \tag {12}
> $$

**Feedback**:
Reusing one proposal across values of \theta is not automatic. The representation behind (12) needs Q_{\theta_0}(\mathcal H)>0 whenever \pi_{\theta}(A_n\mid\mathcal H)P_{\theta}(\mathcal H)>0 for the parameter values being explored. That condition is stronger than the single-\theta support condition used earlier, and it should be stated here.

---

### 5. NSE Example Uses an Inconsistent State-Space Dimension

**Status**: [Pending]

**Quote**:
> on). Following Wilson and Balding (1998), the loci are each assumed to mutate independently at the same rate,  $\theta /2$ , according to the stepwise model of mutation. The type space is large ( $E = \{0,1,\dots,19\}^3$ ) but the required backward transition probabilities may be efficiently approximated by the computational methods described in

**Feedback**:
This does not match the preceding data description, which says the sample is typed at five microsatellite loci. Under the truncation used in this section, the joint type space should be \{0,1,\ldots,19\}^5, not \{0,1,\ldots,19\}^3. Since the dimension drives the computational scale of the example, this should be corrected explicitly.

---

### 6. The Standard-Error Check Misreads the θ=2.0 Row

**Status**: [Pending]

**Quote**:
> ssion of the accuracy of the algorithm.
>
> We can use the standard errors from the long run of $Q_{\theta}^{\mathrm{SD}}$ to check whether the standard errors for the shorter run accurately reflect the standard deviation of the importance weights. If they do then the longer run should result in standard errors which are smaller by a factor of $\sqrt{500} \approx 22$. For $\theta = 2.0$ and $\theta = 10.0$ the changes in the estimated standard error (by factors of about 21 and 17 respectively) between the long and short runs for $Q_{\theta}^{\mathrm{SD}}$ suggest that these standard errors are being estimated reasonably accurately. In con

**Feedback**:
The arithmetic for \theta=2.0 does not support this sentence. Table 1 reports standard errors 4.01\times10^{-8} and 1.87\times10^{-8}, which differ by a factor of about 2.1, not 21. The \theta=10.0 case is broadly consistent with the stated check, but the \theta=2.0 case is not and should not be cited as supporting evidence.

---

### 7. Panel Ascertainment Is Not Equivalent to “Any Panel Lineage”

**Status**: [Pending]

**Quote**:
> For the IS schemes that we have considered, assuming the infinite sites mutation model, the ascertainment effect can be accommodated by labelling every lineage which leads to any chromosome in the panel as a panel lineage and adapting both P_{θ}(ℋ) and Q_{θ}(ℋ) so that mutations can occur only on panel lineages.

**Feedback**:
This condition is too weak for SNP discovery in a panel. Under the infinite-sites model, a retained site must be polymorphic in the panel, so the mutation must fall on a branch whose panel descendants form a nonempty proper subset of the panel. A mutation ancestral to all panel chromosomes is on a panel lineage, but it makes the panel monomorphic and would not be ascertained. The support restriction should reflect panel polymorphism, not only ancestry to at least one panel sample.

---

### 8. The Proposed GPD Diagnostic Needs Existence Conditions

**Status**: [Pending]

**Quote**:
> In particular we propose fitting a generalized Pareto distribution (see Davison and Smith (1990) for example) to the weights above some threshold, and using a parametric bootstrap to estimate confidence intervals for the mean of the weights (i.e. the estimate of the likelihood).

**Feedback**:
A mean-based interval from a generalized Pareto tail is meaningful only under explicit shape restrictions. If the fitted tail index is at least 1, the fitted tail mean does not exist; if it lies in [1/2,1), the mean exists but the variance does not. Since this section is already about possibly infinite-variance weights, the text should say what will be reported in those cases rather than presenting the bootstrap as uniformly available.

---

### 9. The Tree Count Refers to Histories, Not Topologies

**Status**: [Pending]

**Quote**:
> For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
This count is not the number of rooted labeled binary tree topologies. It is the standard count of labeled histories, where the order of coalescence events is included. The number of rooted labeled binary topologies is (2n-3)!!. The distinction matters because the sentence uses the count as evidence about the size of the topology space.

---

### 10. Equation (33) Uses the Wrong Summation Index

**Status**: [Pending]

**Quote**:
> $$
> \hat{\pi}(\beta|A_n) = \sum_{\alpha \in A_n} \sum_{i=1}^{l} \frac{n_\alpha}{n} w_i F_{\alpha_1\beta_1}^{(\theta,t_i,n)} \cdots F_{\alpha_l\beta_l}^{(\theta,t_i,n)} \tag{33}
> $$
>
> where $t_1, \ldots, t_s$ are the quadrature points, and $w_1, \ldots, w_s$ are the corresponding quadrature weights.

**Feedback**:
The inner sum should run over quadrature nodes, not loci. As written, the formula sums i=1,\ldots,l even though the nodes and weights are defined for i=1,\ldots,s. The display should also use an approximation sign rather than equality, since it is introducing the quadrature approximation to (31).

---
