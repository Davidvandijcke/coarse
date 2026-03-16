# Inference in molecular population genetics

**Date**: 03/16/2026
**Domain**: unknown
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper proposes an importance-sampling (IS) proposal Q^{SD} for coalescent-based likelihood inference that approximates the conditional sampling distribution π(·|A_n) by an analytically tractable surrogate π and uses backward-time proposals to sample genealogical histories. The authors demonstrate empirically on several simulated examples that Q^{SD} can give large efficiency gains over naive IS and some MCMC implementations, and they illustrate practical implementation details (Appendix A) for multilocus/sequence models. The main result is that the π-based proposal provides a competitive, often much faster, way to estimate likelihoods for parameter inference, but the manuscript leaves open several theoretical, numerical and empirical robustness questions that affect practical reliability and scope of applicability.

Below are the most important issues identified by the review panel.

**No general finite-variance guarantees or operational safeguards for importance weights**

Multiple reviewers flagged that the manuscript lacks general sufficient conditions ensuring finite second moment of the IS weights and does not operationalize standard protective measures. It would be helpful to either (a) state and prove sufficient conditions (in terms of P, θ, n and the proposal Q) guaranteeing Var[w] < ∞ or (b) include a practical, required protocol that makes the estimator safe in routine use: defensive-mixture proposals (Hesterberg-style) with recommended ε, control variates or regression-adjusted IS, and Pareto-smoothed importance-sampling (PSIS) diagnostics with explicit decision rules (e.g. when tail-index α ≤ 0.5 trigger mixture/bridge sampling). Readers might note that without such guarantees or enforced safeguards the reported standard errors and apparent efficiency gains can be catastrophically misleading in heavy-tailed regimes; the manuscript should replace ad-hoc variance reporting with ESS, PSIS tail-index, and bootstrap or model-based intervals when reporting results.

**Re-using a single driving value θ₀ is fragile — need theory and recipes for combining proposals**

The paper promotes reusing samples from a single driving parameter θ₀ to estimate L(θ) across θ, but reviewers emphasize that variance and skewness can explode as |θ − θ₀| grows and that this fragility is central to several empirical comparisons. It would be helpful to provide (a) theoretical guidance or empirical maps quantifying the radius of reliable reweighting as a function of n, θ₀ and the mutation model, and (b) operational methods demonstrated in the experiments: mixtures of multiple Q_{θ_k}^{SD}, defensive mixtures, or bridge/path-sampling recipes (Meng & Wong / Gelman & Meng) with concrete rules for selecting θ_k grid points and mixture weights. Readers might note that when presenting likelihood curves obtained from a single θ₀, the paper should always report diagnostics (relative ESS vs θ, max-weight ratio, PSIS p-values) and, where necessary, use combined/bridged estimators to avoid severe undercoverage or misleadingly peaked curves.

**MCMC comparisons need standardized diagnostics and fair tuning (report CPU per ESS)**

Reviewers find the empirical comparisons between Q^{SD} and MCMC under-supported because MCMC runs are often short, use default tunings, and omit standard convergence diagnostics. It would be helpful for each comparative experiment to follow a prespecified MCMC protocol: tune proposals for reasonable acceptance rates, run multiple over-dispersed chains, and report Gelman–Rubin R̂, ESS for θ and representative latent summaries, autocorrelation plots, and trace plots. Comparisons should be normalized on statistical efficiency (CPU time per ESS) rather than raw wall-clock time and include third-method checks (bridge sampling, Rao–Blackwellized estimators) when IS and MCMC disagree. Readers might note that adding these diagnostics and re-running key comparisons will clarify whether observed performance gaps reflect intrinsic algorithmic differences or suboptimal MCMC tuning/termination.

**Numerical stability and error analysis for the π construction are missing**

The implementation of π relies on linear-algebra operations (I − λ_n P)^{-1} and quadrature/truncation approximations (Appendix A), yet the paper gives no condition-number estimates, error bounds or stable-algorithm recommendations. It would be helpful to add a numerical-analysis subsection that (a) gives spectral/condition-number diagnostics and recommended solver strategies (rescaling, stable linear solvers, spectral decomposition, iterative solvers with preconditioning), (b) provides error bounds or convergence diagnostics for the quadrature and truncation choices (choice of s, adaptive quadrature), and (c) studies how errors in π propagate to IS weights and the likelihood estimator (sensitivity plots or upper bounds). Readers might note that when λ_n is near 1 the matrix can be nearly singular and small numerical errors in π can produce enormous weights; the manuscript should propose stable alternatives (truncated Neumann series with remainder bounds, Tikhonov regularization, or sampling-based approximations) and report runtime/precision trade-offs on representative high-θ examples.

**Limited treatment of model misspecification (unknown P, selection, structure, recombination)**

The methods, key theorems, and approximations assume a known mutation matrix P and standard coalescent assumptions (neutrality, panmixia, no recombination), but the paper only offers qualitative remarks about robustness. It would be helpful to either extend the method to jointly handle uncertain P (e.g. estimate P alongside θ with priors or profiling) or to present a focused robustness study: simulated perturbations of P, mild population structure, simple selection, and low recombination to quantify bias, IS-weight behavior and coverage. Readers might note that practical recommendations are needed (diagnostics such as LD summaries, Tajima's D, posterior predictive checks) and guidance on when users should switch to joint estimation or model expansion because misspecification can materially change π and invalidate the approximations underlying Q^{SD}.

**No complexity / scaling analysis or large-scale experiments to support practical feasibility claims**

Several reviewers found the paper's claims of broad practical feasibility and orders-of-magnitude efficiency gains are not supported by theoretical complexity analyses or experiments on larger, realistic datasets. It would be helpful to add explicit per-sample computational complexity (big-O) and memory-growth statements as functions of n, number of loci L, state-space size |E| and sequence length, plus empirical scaling plots (runtime, ESS, memory) over these dimensions. Include representative larger-scale simulations that expose bottlenecks (inversion of large matrices, quadrature costs, recombination combinatorics) and show at least one scalable variant (blockwise IS, locus-wise marginalization, or hybrid IS–MCMC) with its runtime/ESS trade-offs. Readers might note that such analyses will make the method's practical scope and break-even regimes clear to practitioners working with genome-scale data.

**Status**: [Pending]

---

## Detailed Comments (19)

### 1. Unqualified claim of 'several orders of magnitude' improvement

**Status**: [Pending]

**Quote**:
> Our approach substantially outperforms existing IS algorithms, with efficiency typically improved by several orders of magnitude. The new method also compares favourably with existing MCMC methods in some problems, and less favourably in others, suggesting that both IS and MCMC methods have a continuing role to play in this area.

**Feedback**:
It would be helpful to qualify and substantiate the blanket claim of “several orders of magnitude” by specifying the metric, parameter regimes, and uncertainty. Readers might note that “efficiency” can mean ESS, variance per CPU, or max‑weight behaviour. Replace the global claim with quantified statements such as: report ESS per CPU (or variance reduction per CPU) with Monte Carlo error bars, state the ranges of n, θ and mutation models where large gains occur, and provide bootstrap CIs or standard errors on reported folds of improvement. Concretely, add a table/figure that shows ESS per CPU (with CIs) across θ∈[a,b] and n∈{…} and rewrite the sentence to reflect the observed numeric ranges rather than an unqualified magnitude claim.

---

### 2. Ambiguity between formal characterization and computable proposal

**Status**: [Pending]

**Quote**:
> The optimal proposal distribution for these problems can be characterized, and we exploit a detailed analysis of genealogical processes to develop a practicable approximation to it.

**Feedback**:
It would be helpful to distinguish the theoretical characterization from a closed‑form, computable proposal. Readers might note the conditional probabilities needed for the exact optimal proposal are generally unavailable in closed form. Explicitly cite the formal result (e.g. Theorem 1) and state that the characterization is formal (in terms of conditional sampling probabilities π(·|·)) while the paper develops an approximation to that object for computation. Add a short sentence clarifying which parts are descriptive/analytic and which are implemented approximately.

---

### 3. Vague statement about discussing diagnostics

**Status**: [Pending]

**Quote**:
> We offer insights into the relative advantages of each approach, and we discuss diagnostics in the IS framework.

**Feedback**:
It would be helpful to summarise which diagnostics and decision rules are considered rather than leaving this vague. Readers might note ESS, PSIS Pareto tail‑index (k or α), max‑weight ratio and CPU‑normalized metrics are the relevant diagnostics. Add a concise list in the summary linking each diagnostic to an operational action (for example: report ESS per CPU; compute PSIS k and, if k≥0.7 or α≤0.5, trigger mixture/bridge sampling or defensive mixtures with recommended ε). This tells practitioners what to expect without searching the appendix.

---

### 4. Fragility of reusing a single driving value — concrete two‑point counterexample

**Status**: [Pending]

**Quote**:
> This approach is due to Griffiths and Tavaré (1994a), which refers to $\theta_0$ as the 'driving value' of $\theta$.

**Feedback**:
It would be helpful to include a simple, explicit counterexample showing that reuse of a single proposal Q_{θ0} can produce arbitrarily large variance as θ moves away from θ0. Readers might note the following two‑point example: let H={h1,h2} with Q_{θ0}(h2)=δ≈0 while P_θ(h2)=ε>0, then w(h2)≈ε/δ and E_Q[w^2]≥ε^2/δ → ∞ as δ→0. Add this example (or an analogous minimal example) and recommend accompanying diagnostics (PSIS k, max‑weight ratio, relative ESS) or multi‑θ mixture/bridge strategies when reuse is employed.

---

### 5. Division by zero / indeterminate form in backward transition (Eq. 15)

**Status**: [Pending]

**Quote**:
> q _ {\theta} ^ {*} \left(H _ {i - 1} \mid H _ {i}\right) = \left\{ \begin{array}{l l} C ^ {- 1} \frac {\theta}{2} n _ {\alpha} \frac {\pi (\beta \mid H _ {i} - \alpha)}{\pi (\alpha \mid H _ {i} - \alpha)} P _ {\beta \alpha} & \text {if } H _ {i - 1} = H _ {i} - \alpha + \beta , \\ C ^ {- 1} \binom {n _ {\alpha}} {2} \frac {1}{\pi (\alpha \mid H _ {i} - \alpha)} & \text {if } H _ {i - 1} = H _ {i} - \alpha , \\ 0 & \text {otherwise}, \end{array} \right. \tag {15}

**Feedback**:
It would be helpful to add a standing positivity/irreducibility assumption or a concrete rule to handle 0/0 cases. Readers might note denominators like π(α|·) can be zero (for example if P is the identity, no mutation), making the expressions indeterminate. Explicitly require π(·|·)>0 for the configurations used in (15) (e.g. assume P is irreducible with P_{ab}>0 for relevant a,b), or state the limiting definition (set the backward probability to zero when the numerator is zero, or define it by a limiting argument). Add a short remark in the main text and/or before Eq. (15) so implementers know which convention/sufficient condition is in force.

---

### 6. CLT and sample‑variance statements need precise regularity

**Status**: [Pending]

**Quote**:
> However, caution is necessary, as even assuming finite variance (which is not guaranteed) the distribution of the weights may be so highly skewed that, even for very large $M$, $\sigma^2$ is (with high probability) underestimated by $\hat{\sigma}^2$, and/or the normal asymptotic theory does not apply.

**Feedback**:
It would be helpful to state the standard CLT/variance results and then specify the problematic regimes. Readers might note that if weights are i.i.d. with E[w^2]<∞ then S^2 is unbiased/consistent for σ^2 and the CLT applies; the real concern is when E[w^2]=∞ or draws are dependent. Rewrite to: (a) state the CLT and consistency under E[w^2]<∞, (b) warn that infinite second moment or strong dependence invalidates these results, and (c) refer to diagnostics (PSIS k, ESS) and defensive IS as remedies. This makes the claim precise and actionable.

---

### 7. Make 1/L(θ) Monte Carlo scaling explicit

**Status**: [Pending]

**Quote**:
> each term of the sum will be 0 with very high probability, and reliable estimation will require values of $M$ (in the range $10^6 - 10^{100}$ for the examples that we consider here) which are too large for the method to be practicable.

**Feedback**:
It would be helpful to make the 1/L(θ) scaling explicit so readers can reproduce the feasibility estimate. Readers might note the estimator in (5) is an average of Bernoulli‑like indicators with mean L(θ), so the expected number of nonzero terms among M draws is M·L(θ). To expect O(1) nonzero samples need M≈1/L(θ), and to get relative error ε need M≈(1−L(θ))/(ε^2 L(θ)). Add these formulae and a short calculation that led to the cited M ranges so practitioners can plug in their own L(θ) values.

---

### 8. Ambiguity in definition of missing data \(\mathcal{H}\) in Eq. (4)

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
It would be helpful to state exactly which representation of ℋ is intended because computational cost and variance depend on it. Readers might note options include labeled histories (ranked), unranked rooted trees with branch lengths, or fully mutation‑labeled histories. Add a sentence specifying which is used for (4) (for example: “here ℋ denotes a fully specified labeled history: rooted topology, ranking and mutation labels, so π_θ(A_n|ℋ)∈{0,1}”), and briefly note implications for state‑space size.

---

### 9. Combinatorial count (ranked vs unranked trees) ambiguous

**Status**: [Pending]

**Quote**:
> For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
It would be helpful to correct the combinatorial terminology: readers might note n!(n−1)!/2^{n−1} is the number of labeled histories (ranked trees), whereas the number of rooted binary tree topologies with n labeled leaves is (2n−3)!!. State both formulas and clarify which space is referenced in subsequent complexity claims so algorithmic scaling statements are precise.

---

### 10. Algorithm 1 'go back' instruction is ambiguous

**Status**: [Pending]

**Quote**:
> Step 3: if there are fewer than $n + 1$ lines in the ancestry return to step 2. Otherwise go back to the last time at which there were $n$ lines in the ancestry and stop.

**Feedback**:
It would be helpful to state the stopping criterion and recorded output explicitly to avoid off‑by‑one implementation errors. Readers might misimplement the “go back” phrasing. Replace with a precise instruction: simulate events until the first event that would increase the number of lines from n to n+1, then record the configuration immediately before that event (the most recent configuration with exactly n lines) and stop. Also indicate what is returned (the labeled history, time index, etc.).

---

### 11. MRCA type = stationary law requires ergodicity/coalescent limit

**Status**: [Pending]

**Quote**:
> At stationarity, under the neutrality assumption, the distribution of the type of the MRCA is given by the stationary distribution of the (mutation) Markov chain  $P$ .

**Feedback**:
It would be helpful to state the conditions under which this equality holds. Readers might note equality requires P irreducible/aperiodic and is an asymptotic/coalescent‑limit statement rather than necessarily exact for finite N. Add a sentence that the equality holds when P is irreducible (and aperiodic) and in the coalescent limit (N→∞ with θ fixed), and cite standard references (e.g. Ethier & Kurtz or Donnelly & Kurtz).

---

### 12. Specify geometric pmf parameterization to match Eq. (17)

**Status**: [Pending]

**Quote**:
> mutating it according to the mutation matrix $P$ a geometric number of times, with parameter $\theta /(n + \theta)$, i.e.
> 
> $$
> \hat {\pi} (\beta | A _ {n}) = \sum_ {\alpha \in E} \sum_ {m = 0} ^ {\infty} \frac {n _ {\alpha}}{n} \left(\frac {\theta}{n + \theta}\right) ^ {m} \frac {n}{n + \theta} (P ^ {m}) _ {\alpha \beta}. \tag {17}
> $$

**Feedback**:
It would be helpful to remove ambiguity because two parameterizations of the geometric distribution exist. Readers might note (17) uses support {0,1,2,...} with P(M=m)=(1−λ_n)λ_n^m where λ_n=θ/(n+θ) and 1−λ_n=n/(n+θ). Explicitly state the pmf P(M=m) = (n/(n+θ))(θ/(n+θ))^m so implementers reproduce (17) exactly.

---

### 13. Advice: retain post‑burn‑in draws rather than routine thinning

**Status**: [Pending]

**Quote**:
> If $\mathcal{T}^{(1)}, \mathcal{T}^{(2)}, \ldots$ is a sample (after burn-in, and possibly thinning) from a Markov chain with stationary distribution $P_{\theta_0}(\mathcal{T} | A_n)$, then a relative likelihood surface for $\theta$ can be estimated by using

**Feedback**:
It would be helpful to advise practitioners to retain all post‑burn‑in draws and account for dependence rather than routinely thinning. Readers might note thinning reduces storage but typically lowers ESS per CPU. Replace 'and possibly thinning' with guidance such as: 'retain all post‑burn‑in draws and estimate Monte Carlo error via ESS, batch means or spectral variance estimators; thin only for storage constraints, not as a default for variance reduction.'

---

### 14. Instability of estimating likelihood by posterior ÷ prior division

**Status**: [Pending]

**Quote**:
> an estimate of the relative likelihood surface for $\theta$ may be obtained by estimating the posterior density and dividing by the prior density.

**Feedback**:
It would be helpful to warn about numerical instability and recommend alternative estimators. Readers might note that KDEs on dependent MCMC draws can be noisy and dividing by small prior values amplifies error. Recommend established approaches (Chib's method, bridge sampling, thermodynamic integration) or, if dividing a smoothed posterior, require ESS‑adjusted uncertainty and bandwidth sensitivity checks. Add references and a brief recipe when the paper discusses this route.

---

### 15. Qualification: Q^{SD} sampling rule vs θ‑dependence of weights

**Status**: [Pending]

**Quote**:
> This procedure defines an IS function $Q^{\mathrm{SD}}$ which we note is independent of $\theta$, removing the need to specify a driving value.

**Feedback**:
It would be helpful to qualify the claim. Readers might note while the sampling rule for Q^{SD} may not require plugging in a numeric θ, the true backward‑event rates (and the optimal proposal) depend on θ (for example total mutation rate n(θ/2), coalescence rate \binom{n}{2}), and importance weights P_θ(H)/Q(H) remain θ‑dependent. Clarify that Q^{SD}'s sampling rule is θ‑free but a driving value is still implicit in weight computation for likelihood estimation.

---

### 16. Truncation of type space breaks shift‑invariance — quantify sensitivity

**Status**: [Pending]

**Quote**:
> The implementation of our IS scheme is facilitated by centring the sample distribution near 10 repeats and truncating the type space $E$ to $\{0, 1, \dots, 19\}$ by insisting that all mutations to alleles of length 0 or 19 involve the gain or loss respectively of a single repeat.

**Feedback**:
It would be helpful to quantify the bias introduced by truncation since it breaks the stated shift‑invariance. Readers might note for samples concentrated between 8 and 13 truncation may be negligible but this should be demonstrated. Provide either an analytic bound on the probability of hitting boundaries before coalescence as a function of θ and n, or a numerical sensitivity check (recompute with a wider truncation, e.g. {0,..,39}, and report changes in likelihood/curves). Report how likelihoods change and whether conclusions are robust.

---

### 17. Use matrix exponential closed form for Poisson mixture (Eq. 32)

**Status**: [Pending]

**Quote**:
> F_{\alpha_i\beta_i}^{(\theta,t,n)} = \sum_{m=0}^{\infty} \frac{(\theta t/n)^m}{m!} \exp\left(-\frac{\theta t}{n}\right) (P^m)_{\alpha_i\beta_i}. \tag{32}

**Feedback**:
It would be helpful (and numerically preferable) to note the closed form. Readers might recognise the Poisson‑weighted sum equals exp\{\lambda(P−I)\} with λ=(θ t/n). State F = exp{λ(P−I)} so implementers can compute F via standard, stable matrix exponential routines (scaling and squaring, Pade) rather than truncating the infinite sum.

---

### 18. GPD tail fit: explicit estimator and tail‑index reporting

**Status**: [Pending]

**Quote**:
> In particular we propose fitting a generalized Pareto distribution (see Davison and Smith (1990) for example) to the weights above some threshold, and using a parametric bootstrap to estimate confidence intervals for the mean of the weights (i.e. the estimate of the likelihood).

**Feedback**:
It would be helpful to give the explicit formula and tail‑index checks so users know when the mean/variance are finite. Readers might note: let u be threshold, p̂=k/M the exceedance proportion, fit GPD(ξ̂,σ̂) to exceedances Y=W_i−u; the estimated mean contribution of the tail is p̂*(u + σ̂/(1−ξ̂)) provided ξ̂<1, and the variance is finite only if ξ̂<1/2. Require reporting ξ̂ (with CI) and prescribe actions: if ξ̂≥1 report divergence of the mean; if 1/2≤ξ̂<1 indicate variance is infinite and normal‑theory CIs are invalid and recommend robust percentile intervals or defensive proposals. Add these explicit formulae and decision rules in the methods.

---

### 19. IS regularity conditions for weighted empirical posterior omitted

**Status**: [Pending]

**Quote**:
> the distribution with atoms of size $w_i/\sum w_j$ on histories $\mathcal{H}^{(i)}$ ($i=1,\ldots,M$) is an approximation to the conditional distribution of $\mathcal{H}$ given $A_{n}$.

**Feedback**:
It would be helpful to state the standard regularity conditions that justify this approximation. Readers might note one needs absolute continuity (q(h)>0 whenever π(h):=P_θ(A_n|h)P_θ(h)>0) and finite moments E_Q[|w f|]<∞ (and Var_Q[w f]<∞ to report CLT SEs). Add these conditions and note that failure (e.g. Q missing target support or infinite second moment) invalidates convergence and motivates diagnostics (ESS, PSIS k) or alternative schemes such as defensive mixtures or bridge sampling.

---
