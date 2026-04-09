# Inference in molecular population genetics

**Date**: 03/14/2026
**Domain**: statistics/population_genetics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper proposes an importance sampling (IS) method for computing likelihoods in coalescent models with general mutation structures. It introduces a conditional sampling distribution approximation and a sequential IS scheme using a "stepping stone" driving value. The main results demonstrate substantial variance reduction compared to existing IS algorithms and favorable comparisons with MCMC methods for small to moderate sample sizes.

Below are the most important issues identified by the review panel.

**Finite variance and diagnostic limitations for importance sampling weights**

The paper acknowledges in Section 6.4 that finiteness of the variance of importance sampling weights cannot be proven for general mutation models, except in the infinite sites case. Readers might note that without guaranteed finite variance, the standard error estimates reported in Tables 1 and 2 rely on the central limit theorem without theoretical justification, potentially underestimating true uncertainty as illustrated by the θ = 15.0 case where the estimate from 20,000 samples falls outside the confidence interval implied by the 10⁷ sample estimate. Additionally, the proposed extreme value theory diagnostics for highly skewed weight distributions remain speculative and empirically unvalidated within the paper. It would be helpful to establish sufficient conditions for finite variance—perhaps by restricting the class of mutation matrices in Theorem 1—or to implement and validate the extreme value theory bootstrap methods suggested in Section 6.4 to provide reliable uncertainty quantification.

**Unquantified approximation error for non-parent-independent mutation models**

The efficiency gains of the proposed importance sampling scheme rely on using π̂ (Definition 1) to approximate the conditional sampling distribution π(·|A_n). While Proposition 1 establishes that this approximation is exact only for parent-independent mutation models or when n=1, the paper provides no theoretical bounds on the approximation error for general mutation matrices, such as those used in the stepwise mutation model (Section 5.4) or the finite sites model (Section 5.2). Readers might note that without quantification of the Kullback-Leibler divergence or total variation distance between π̂ and π, the variance reduction relative to existing methods is not theoretically guaranteed for arbitrary mutation structures, despite empirical demonstrations. It would be helpful to derive bounds on the approximation error in terms of the deviation of the mutation matrix P from the parent-independent assumption, or to identify specific classes of non-parent-independent models where the approximation is guaranteed to remain accurate.

**Driving value sensitivity and lack of systematic selection methodology**

The paper proposes estimating likelihood surfaces using samples from a single driving value θ₀ (Equation 12), yet acknowledges in Section 6.1 that importance sampling efficiency degrades as θ moves away from θ₀, with related estimators exhibiting infinite variance when θ > 2θ₀. Readers might note that the paper offers no systematic procedure for selecting appropriate driving values or for determining when the distance |θ - θ₀| is sufficiently large to render estimates unreliable, as potentially illustrated by artificially peaked likelihood surfaces when using fixed driving values. While bridge sampling and path sampling are mentioned as potential remedies in the Discussion, these approaches are not implemented or validated within the main methodology, leaving practitioners without guidance for full likelihood surface estimation. It would be helpful to implement the bridge sampling or defensive mixture strategies suggested in Sections 6.1 and 6.3, or to provide explicit criteria for adaptive selection of driving values that ensure stable variance properties across the full parameter space.

**Scalability limitations and uncharacterized computational complexity**

While the paper demonstrates efficiency gains for small to moderate sample sizes, the empirical validation is limited to relatively small datasets (n ≤ 60), and no formal analysis of computational complexity is provided with respect to sample size n or sequence length L. Readers might note that calculating the approximation π̂ requires matrix inversions scaling as O(|E|³) for each n, and the Gaussian quadrature approximations for sequence data scale with the number of loci, yet the practical limits for modern genomic datasets (e.g., n > 100, L > 1000) remain uncharacterized. Given the acknowledgment in Section 6.5 that current algorithms are already at computational limits, the boundary where MCMC methods become preferable—as conjectured in Section 6.1 for larger, less constrained problems—has not been empirically determined. It would be helpful to provide explicit computational complexity bounds and to demonstrate the method's performance on larger, more realistic datasets to clarify the practical limits of applicability for modern population genetics studies.

**Robustness to model misspecification and unknown mutation parameters**

The theoretical development assumes a known mutation transition matrix P while treating θ as unknown, and depends critically on idealized coalescent conditions including neutral evolution, constant population size, and panmixia. Readers might note that, as discussed by D.A. Stephens in the Discussion section, mutation matrices comprise fundamental evolutionary parameters that are often unknown or estimated with error in practice, and real biological systems frequently violate neutrality through selection, bottlenecks, or population structure. Without sensitivity analysis for misspecification of P or violations of coalescent assumptions, the reliability of parameter estimates under realistic evolutionary scenarios remains unverified. It would be helpful to include a systematic assessment of inference stability under perturbations of the mutation matrix or violations of neutrality and constant population size, or to extend the methodology to jointly estimate P and θ as suggested in the authors' response.

**Consistency of comparative claims with empirical findings**

The abstract states that the proposed method "compares favourably with existing MCMC methods," yet specific empirical findings within the paper suggest this assessment may be overly broad. Readers might note that Section 5.4 explicitly concludes that for the NSE microsatellite dataset, "the curve obtained by using micsat is more accurate" than the importance sampling estimates, and Section 6.1 concedes that MCMC approaches may be preferable for "less constrained" problems with larger sample sizes. Without explicit criteria distinguishing when importance sampling versus MCMC methods are likely to perform better, the general superiority claimed in the abstract appears inconsistent with the specific limitations demonstrated empirically. It would be helpful to qualify the comparative claims in the abstract and to provide explicit criteria identifying the problem structures—such as sample size, constraint types, or mutation models—where the proposed method is expected to outperform MCMC approaches.

**Status**: [Pending]

---

## Detailed Comments (16)

### 1. Inconsistent mutation rate scaling in coalescent parameterization

**Status**: [Pending]

**Quote**:
> types change along different branches of the tree as independent continuous time Markov chains with rate $\theta / 2 = N\mu / \nu^2$ and transition matrix $P$ (see for example Donnelly and Tavaré (1995)). Throughout the paper we shall adopt the coalescent approximation as the model underlying the data.

**Feedback**:
Readers might note that the rate $\theta/2$ per lineage implies a geometric parameter $\theta/(2n+\theta)$ for the number of mutations before coalescence, whereas Definition 1 specifies the parameter as $\theta/(n+\theta)$. It would be helpful to adjust the rate definition to $\theta$ per lineage or modify Definition 1 to use $\theta/(2n+\theta)$ to maintain internal consistency with the coalescent scaling.

---

### 2. Terminology: labeled histories versus topologies

**Status**: [Pending]

**Quote**:
> For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
Readers might note that the formula $n!(n-1)!/2^{n-1}$ counts labeled histories (ranked trees), not unranked topologies, which number $(2n-3)!!$. For $n=4$, this yields 18 versus 15 respectively. It would be helpful to replace 'topologies' with 'labeled histories' to match the combinatorial expression.

---

### 3. Overgeneralized zero-probability condition for finite sites models

**Status**: [Pending]

**Quote**:
> Since $\pi_{\theta}(A_n | \mathcal{H})$ is 0 unless $\mathcal{H}$ is consistent with $A_n$, each term of the sum will be 0 with very high probability

**Feedback**:
Readers might note that this claim assumes an infinite sites mutation model where consistency is deterministic. For finite sites models (e.g., Jukes-Cantor), transition probabilities satisfy $P_{ij}(t) > 0$ for all states when $t>0$, giving positive (though small) probability to all histories. It would be helpful to qualify this statement as applying specifically to infinite sites models.

---

### 4. Boundary case $n=1$ undefined without constraint on $F$

**Status**: [Pending]

**Quote**:
> where $B_0, B_1, \ldots, B_\tau$ is a particular set-valued Markov chain stopped the first time $\tau$ that it has cardinality 1

**Feedback**:
Readers might note that when $n=1$, the chain stops immediately with $\tau=0$, reducing equation (6) to $L(\theta)=F(A_1)$. For this to yield the correct likelihood of 1, $F$ must satisfy $F(A_1)=1$. It would be helpful to add this boundary condition explicitly after equation (6) to ensure the recursion terminates correctly for all $n \geq 1$.

---

### 5. Missing absolute continuity condition for single-chain importance sampling

**Status**: [Pending]

**Quote**:
> Griffiths and Tavaré (1994a) showed how to use realizations of a single Markov chain to estimate the likelihood function.

**Feedback**:
Readers might note that estimating $L(\theta)$ for varying $\theta$ from a single chain run at $\theta_0$ requires importance sampling, which demands absolute continuity ($P_\theta \ll P_{\theta_0}$). If mutation paths have zero probability under $\theta_0$ but positive probability under $\theta$, the weights are undefined. It would be helpful to add the condition that the single chain must dominate the target measures for all $\theta$ considered.

---

### 6. Undefined relationship between $\pi_{\theta}$ and $P_{\theta}$ notations

**Status**: [Pending]

**Quote**:
> If $\mathcal{T}$ represents missing data for which $\pi_{\theta}(A_n | \mathcal{T})$ is (relatively) easy to calculate, then it is straightforward to use the Metropolis–Hastings algorithm to construct a Markov chain with stationary distribution $P_{\theta}(\mathcal{T} | A_n)$.

**Feedback**:
Readers might note that the text uses $\pi_{\theta}$ for the conditional likelihood of observed data but $P_{\theta}$ for joint and conditional probabilities without clarifying whether these denote the same measure. It would be helpful to state explicitly that $\pi_{\theta}(A_n|\mathcal{T}) \equiv P_{\theta}(A_n|\mathcal{T})$ and that $P_{\theta}(\mathcal{T})$ denotes the coalescent prior.

---

### 7. Kernel density estimation variance with autocorrelated MCMC samples

**Status**: [Pending]

**Quote**:
> The posterior density is most easily estimated by smoothing a sample $\theta^{(1)}, \ldots, \theta^{(M)}$ from the Markov chain, although potentially more efficient methods exist (see for example Chen (1994)).

**Feedback**:
Readers might note that for autocorrelated MCMC samples, the variance of the kernel density estimator satisfies $\text{Var}(\hat{f}_h(\theta)) \approx \frac{f(\theta)R(K)}{M}(1 + 2\sum_{k=1}^\infty \rho(k))$, inflating uncertainty by a factor of $M/\text{ESS}$. Standard bandwidth selectors assuming independence may undersmooth. It would be helpful to note that autocorrelation inflates variance and that bandwidth selection should account for dependence or thinning should be applied.

---

### 8. Boundary bias in kernel smoothing for constrained parameter spaces

**Status**: [Pending]

**Quote**:
> The posterior density is most easily estimated by smoothing a sample $\theta^{(1)}, \ldots, \theta^{(M)}$ from the Markov chain

**Feedback**:
Readers might note that standard kernel smoothing with symmetric kernels applied to $\theta \in \mathbb{R}^+$ suffers from boundary bias at $\theta \approx 0$ because mass is placed outside the support. When divided by the prior to obtain relative likelihood, this bias propagates. It would be helpful to specify that boundary-corrected methods (e.g., log-transformation or reflection kernels) should be employed for strictly positive parameters.

---

### 9. Variance inflation in relative likelihood estimation near prior tails

**Status**: [Pending]

**Quote**:
> an estimate of the relative likelihood surface for $\theta$ may be obtained by estimating the posterior density and dividing by the prior density

**Feedback**:
Readers might note that constructing $\hat{L}(\theta) \propto \hat{p}(\theta|A_n)/p(\theta)$ yields variance $\text{Var}(\hat{L}(\theta)) \approx \sigma^2(\theta)/p(\theta)^2$ by the delta method, which diverges as $p(\theta) \to 0$. This can produce spurious peaks in tail regions. It would be helpful to caution that the estimator has high variance where the prior is small and that regularization should be considered.

---

### 10. Non-standard notation for joint density using intersection symbol

**Status**: [Pending]

**Quote**:
> \pi_{\theta}(A_n | \mathcal{H}) \frac{P_{\theta}(\mathcal{H})}{P_{\theta}(\mathcal{H} | A_n)} = \frac{P_{\theta}(\mathcal{H} \cap A_n)}{P_{\theta}(\mathcal{H} | A_n)}

**Feedback**:
Readers might note that $P_{\theta}(\mathcal{H} \cap A_n)$ uses the intersection symbol for the joint density of random variables, which is non-standard; $P_{\theta}(\mathcal{H}, A_n)$ is conventional. It would be helpful to add a clarifying footnote that $\cap$ denotes the joint density $\pi_\theta(A_n|\mathcal{H})P_\theta(\mathcal{H})$.

---

### 11. Incorrect reference to $\pi$ instead of $\hat{\pi}$ in Remark 1

**Status**: [Pending]

**Quote**:
> Property (e) provides a characterization of $\pi$ which is, in some more general settings not considered in this paper, more amenable to generalization than definition 1.

**Feedback**:
Readers might note that Property (e) characterizes the approximation $\hat{\pi}$ from Definition 1 (with transition matrix depending on $n_\alpha/n$), not the exact conditional probability $\pi$. It would be helpful to replace 'characterization of $\pi$' with 'characterization of $\hat{\pi}$' to accurately reflect that the property concerns the approximating distribution.

---

### 12. Ambiguous condition for rooted tree sampling

**Status**: [Pending]

**Quote**:
> To allow a comparison with published estimates, we modified our IS function to analyse rooted trees, by adding to conditions (a) and (b) above a condition that no mutation can occur backwards in time from the type of the MRCA.

**Feedback**:
Readers might note that the condition 'no mutation can occur backwards in time from the type of the MRCA' is ambiguous because the MRCA is the ultimate ancestor. It would be helpful to clarify that this means mutations from the MRCA type are forbidden, effectively fixing the root type as ancestral.

---

### 13. Notational inconsistency between driving value $\theta$ and $\theta_0$

**Status**: [Pending]

**Quote**:
> In principle IS methods based on a driving value of $\theta$ will tend to share this undesirable property, as designing a single IS function $Q_{\theta_0}$ which is universally efficient for all $\theta$ may be extremely challenging.

**Feedback**:
Readers might note that the text refers to 'a driving value of $\theta$' but subsequently defines the proposal as $Q_{\theta_0}$, creating ambiguity about whether the driving value is fixed or variable. It would be helpful to replace 'driving value of $\theta$' with 'driving value of $\theta_0$' to maintain consistency with the fixed parameter notation.

---

### 14. Confusion between peeling algorithm and sampling typed ancestry

**Status**: [Pending]

**Quote**:
> The effect of the non-varying sites could then be taken into account by the factor $\pi_{\theta}(A_n|\mathcal{H}^{(i)})$ in estimator (9), which could be calculated by the peeling algorithm (to do this it would be necessary to apply IS to the full typed ancestry $\mathcal{A}$ of the sample).

**Feedback**:
Readers might note that the peeling algorithm analytically sums over internal node types in $\mathcal{A}$, avoiding explicit sampling of $\mathcal{A}$, whereas applying IS to $\mathcal{A}$ requires explicit sampling. These are distinct strategies. It would be helpful to rewrite the parenthetical to state that peeling requires summing over internal nodes, not that IS must be applied to $\mathcal{A}$.

---

### 15. Missing validity condition for GPD-based bootstrap

**Status**: [Pending]

**Quote**:
> In particular we propose fitting a generalized Pareto distribution (see Davison and Smith (1990) for example) to the weights above some threshold, and using a parametric bootstrap to estimate confidence intervals for the mean of the weights (i.e. the estimate of the likelihood).

**Feedback**:
Readers might note that the generalized Pareto distribution has finite mean only when the shape parameter $\xi < 1$. If $\xi \geq 1$, the mean is infinite and the parametric bootstrap for the likelihood estimate is invalid. It would be helpful to add that the procedure assumes $\hat{\xi} < 1$, and that $\hat{\xi} \geq 1$ indicates infinite mean weights rendering the estimator unreliable.

---

### 16. Invalid MCMC-based likelihood approximation claim

**Status**: [Pending]

**Quote**:
> Thus an approximation to $L(\theta)$ that utilizes the summation over (distinct) $H$s visited by the Markov chain is available; such an approximation would be valid for all $\theta$, and thus gives a complete summary of $L(\theta)$.

**Feedback**:
Readers might note that MCMC samples from the posterior $p(\theta,\mathcal{H}|A_n)$, not the prior $p(\mathcal{H}|\theta)$ required for direct integration of $L(\theta)$. Valid estimation requires importance sampling weights $p(A_n|\theta,\mathcal{H})p(\mathcal{H}|\theta)/p(A_n|\theta_0,\mathcal{H})p(\mathcal{H}|\theta_0)$, not simple summation. It would be helpful to revise the claim to acknowledge the need for importance sampling reweighting and the increasing variance with distance from $\theta_0$.

---
