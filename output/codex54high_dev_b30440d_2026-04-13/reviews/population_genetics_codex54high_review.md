# Inference in molecular population genetics

**Date**: 04/13/2026
**Domain**: natural_sciences/biology
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper has a strong core idea: characterize the optimal backward proposal through conditional sampling probabilities, then approximate those probabilities to build a practical importance sampler. The main concerns are not about whether the approach is interesting, but about how far the theory really supports the proposed sampler, how convincing the Monte Carlo evidence is, and whether the framing matches the narrow model class actually analyzed.

Theorem 1 and the backward-time formulation in Section 4 are the paper's main strengths. They clarify the relation between coalescent likelihoods and importance sampling, and the numerical examples do suggest that the proposed sampler can beat the canonical Griffiths-Tavare proposal in several settings. The paper is less convincing when it moves from that theoretical contribution to broad claims about practical inference in population genetics, because the approximation driving the method, the Monte Carlo diagnostics, and the benchmarking design are all thinner than the framing implies.

**The key approximation driving the proposal is only weakly justified outside special cases**

The central methodological step is the replacement of the exact conditional sampling probabilities in theorem 1 and equation (15) by the approximation hat-pi from definition 1 and equation (17), leading to the proposal in equation (25). That substitution is what makes the method run, but proposition 1 establishes exactness only for parent-independent mutation and for the case n = 1 with reversible P, plus a consistency property in equation (20). There is no quantitative control on how close hat-pi is to the true pi for the general parent-dependent mutation models that motivate the paper, nor any argument tying approximation error in hat-pi to variance inflation in the IS weights. Because the whole efficiency claim rests on hat-pi being close enough to the optimal object in equation (15), this is a real gap in the methodological case. Readers are left with examples, not a theory of when the approximation should work and when it should fail. The revision should add either error bounds or exact small-state comparisons for pi versus hat-pi, and then connect those discrepancies to the behavior of the proposal weights across mutation models and theta values.

**Monte Carlo uncertainty is not quantified well enough to support the strongest efficiency claims**

Section 5 explicitly acknowledges that sample standard errors can be misleading under heavy-tailed importance weights and that the authors 'have not performed the larger scale simulation studies that are necessary to obtain accurate estimates of Monte Carlo errors.' Section 20 goes further and says finite variance of the weights could not be proved except in the infinite sites case. Despite that, the paper repeatedly labels long runs from the proposed sampler as 'accurate' benchmarks and uses them to declare several-orders-of-magnitude gains in efficiency in Tables 1 and Figures 2-5. That is shaky, because a long run from the same method is not an independent ground truth when tail behavior is the problem under discussion. The NSE example in Section 5.4 makes this especially visible: after very long IS runs, the paper itself says micsat appears more accurate. A revision needs a more defensible validation design: replicated runs across many seeds, diagnostics based on tail behavior or effective sample size, tractable cases with exact likelihoods or independent reference calculations, and a conservative error-reporting scheme actually implemented rather than only proposed for future work.

**The empirical comparison is too narrow and too asymmetric to justify broad performance claims**

The introduction and summary suggest a general advance for 'modern population genetics data,' but the evaluation in Section 5 is concentrated on small or otherwise favorable problems, and Section 21 openly says the paper deliberately focuses on a one-dimensional inference problem under the simplest evolutionary model. That would be fine if the claims stayed at that level, but they do not. The comparisons with competing MCMC methods are also uneven: in Sections 5.3 and 5.4 the MCMC implementations are often used with published defaults or generic guidelines, and the paper itself notes that tuning could improve micsat, while in the NSE example the MCMC curve seems more accurate. The result is that the paper does show that the new proposal can improve markedly on the canonical Griffiths-Tavare proposal, but it does not yet show a stable ranking against well-tuned alternatives across regimes that matter. This matters because the paper's framing is comparative, not just constructive. The revision should include a designed simulation grid over sample size, mutation model, sequence length, and theta regime, with matched compute budgets, tuned baselines, and a clear report of where IS wins, where it loses, and where both methods become unreliable.

**The infinite-sites method is presented as a continuation of the theory, but it is really a separate heuristic algorithm**

Sections 3 and 4 build the main theory for countable type spaces with a stationary mutation chain, culminating in theorem 1 and the proposal of equation (25). Section 5.5 then moves to the infinite sites model, where the type space is uncountable and the mutation process is not reversible, and says that technical challenges are set aside 'for simplicity' in favor of an adaptation 'by analogy with proposition 2.' That is a substantial methodological break. The resulting sampler may still be a valid importance sampler, but the paper no longer shows that it is a principled approximation to the optimal backward proposal characterized earlier, and the rooted-tree modification is admitted not to use root information efficiently. Since some of the headline gains in Section 5 come from this setting, the paper should not blur the distinction between proved method and heuristic extension. The revision should present the infinite-sites procedure as a separate algorithm, state clearly which parts of the Section 4 logic no longer apply, and either supply a dedicated derivation or add much stronger empirical evidence across rooted and unrooted cases, including outgroup-informed settings.

**The framing overstates the demographic scope relative to the model class actually identified and tested**

Section 3 adopts a very narrow data-generating model: stationarity, neutrality, panmixia, constant population size, no recombination in the region, and known mutation matrix P, with most examples further collapsing the inferential target to the single parameter theta. Yet the introduction and conclusion repeatedly speak in terms of full likelihood-based inference for molecular population genetics and even demographic history. Section 18 lists possible extensions, but those are mostly future directions rather than results demonstrated here, and the discussion itself notes that the practically interesting questions often concern other aspects of the model instead of theta. That mismatch matters because the assumptions are not innocent technicalities; they determine the genealogy law, identifiability, and even whether the observed data are informative about the stated parameter. The paper would be stronger if it were more explicit that the contribution is a proposal-construction strategy for a stylized neutral coalescent setting, not a broadly validated inference framework for realistic demographic analysis. The revision should either narrow the claims in the abstract and introduction or add at least one extension or sensitivity analysis showing how the method behaves under misspecified P, population structure, or changing population size.

**Several application-side modeling shortcuts change the target likelihood without any sensitivity analysis**

The applications make substantive approximations that are treated as computational conveniences rather than inferential assumptions. In Section 5.4 the microsatellite allele space is truncated to {0, ..., 19} with forced behavior at the boundaries, and the paper says this 'will make little difference' without demonstrating that claim for the data analyzed. The same section also assumes independent loci on the Y chromosome with a common mutation rate across loci, which is a strong simplification for the NSE data. Appendix A adds another layer by approximating hat-pi through quadrature and finite sums, and then notes that the approximation can be 'rather rough.' None of these choices necessarily invalidates the method, but together they mean that some likelihood curves are for a surrogate model whose distance from the intended biological model is unknown. A revision should report sensitivity to allele-space truncation, boundary placement, quadrature accuracy, and locus-specific mutation assumptions, at least for the flagship empirical examples.

**No exact non-PIM worked example**

The paper’s main theoretical objects, especially the backward rates in equation (15), stay abstract in the very settings that motivate the method. The only exact worked case is parent-independent mutation, where the problem is unusually simple and the new sampler is already optimal. Readers never see a fully specified parent-dependent mutation model in which the exact sampling probabilities can still be computed and the theorem can be inspected directly. That matters because the paper’s story is that the time-reversal formula has practical content, not just formal interest. A useful addition would be a tiny finite-state example, such as a three-allele nearest-neighbor mutation chain or a two-site binary sequence model with n=2 or 3, where the authors solve the linear system for \pi_\theta(A_n), compute \pi(\cdot\mid A_n), plug it into equation (15), and then compare the exact q_\theta^*, the Griffiths-Tavare proposal, and Q_\theta^{\mathrm{SD}} side by side, including the resulting weight variance.

**Constrained problems are never operationalized**

A recurring claim is that importance sampling works well for genetically 'constrained' problems, whereas MCMC has an edge in less constrained ones. The paper gives intuition for this, but it never turns the idea into something a reader could actually diagnose on a new dataset. That leaves the promised general guidance underdeveloped. The distinction matters because it is one of the paper’s main lessons beyond the specific algorithm, and the applications span several data types where the amount of constraint clearly differs. The revision should define at least one concrete measure of constraint, for example the number of admissible backward moves from a state, the number of feasible rooted histories for an unrooted gene tree, or a proxy based on root ambiguity and singleton structure, and then show across Sections 5.2-5.5 how that measure tracks effective sample size for IS and mixing or between-run stability for MCMC.

**No recipe for driving-value selection**

The practical use of the method depends on choosing a driving value \theta_0 and deciding when one proposal can safely support an entire likelihood surface. Yet the paper gives little operational advice on how to pick \theta_0, how to detect poor overlap away from it, or when multiple driving values are needed. This is more than a minor implementation detail, because the likelihood-surface examples in Sections 5.3 and 5.4 rely exactly on reusing a single proposal across \theta. Readers are told that problems can arise, but not how to avoid them in practice. A complete version of the paper should add a pilot-to-production workflow: run short pilot samplers on a coarse grid of \theta_0 values for one of the sequence examples, monitor overlap diagnostics such as effective sample size or the share of total mass carried by the largest weight at target \theta values, and then combine overlapping runs by bridge sampling or mixture reweighting to produce the final curve.

**No repeated-data parameter recovery study**

The applications show that the new proposal can stabilize likelihood estimation on particular datasets, but they do not show what that buys for inference about \theta across repeated samples. That is a real gap for a paper titled 'Inference in molecular population genetics,' especially since the introduction emphasizes how little information these data may contain. Better Monte Carlo behavior does not automatically mean better recovery of the mutation rate, better interval coverage, or even a reliably located likelihood peak. Readers need to see whether the method improves the inferential target, not only the numerical estimator. A natural addition would be a simulation study under the sequence model in equation (28) and the stepwise microsatellite model, with many replicated datasets at fixed \theta, reporting the distribution of the MLE or posterior mean and likelihood-based intervals from Q_\theta^{\mathrm{SD}}, alongside matched-budget results from the Griffiths-Tavare and MCMC methods.

**Recommendation**: major revision. The paper contains an important theoretical idea and a proposal mechanism that looks genuinely useful, especially relative to earlier IS schemes. But the current version does not yet justify its broader methodological framing: the proposal approximation is only partly supported, the Monte Carlo error analysis is not strong enough for the headline comparisons, and some extensions and applications rely on heuristics whose inferential impact is not quantified.

**Key revision targets**:

1. Provide a substantive validation of the approximation hat-pi to pi, either through theory or exact small-state experiments, and show how approximation error affects the variance and stability of the IS estimator.
2. Redesign the numerical evaluation around replicated runs, defensible Monte Carlo error assessment, and independent benchmarks where possible, rather than treating long runs from the same sampler as sufficient ground truth.
3. Separate the infinite-sites and rooted-tree procedures from the proved countable-state theory, and either derive them rigorously or label them as heuristic extensions with dedicated validation.
4. Align the framing with the actual model class, or add sensitivity and extension results for misspecified mutation matrices, nonconstant demography, and more realistic multilocus or microsatellite settings.
5. Quantify the inferential effect of application-side approximations such as allele-space truncation, common mutation rates across loci, and the quadrature approximation used in Appendix A.

**Status**: [Pending]

---

## Detailed Comments (12)

### 1. Initial Split Is Missing From The State Kernel

**Status**: [Pending]

**Quote**:
> Step 1: choose a type in $E$ at random according to the stationary distribution $\psi(\cdot)$ of the transition matrix $P$. Start the ancestry with a gene of this type which splits immediately into two lines of this type.

**Feedback**:
Algorithm 1 starts with a deterministic move from the MRCA type to the two-line state $\{\alpha,\alpha\}$. Equation (1) cannot generate that transition: with one lineage the split term is zero and the mutation term stays in a one-line state. The paragraph introducing $P_{\theta}(\mathcal{H})$ therefore needs one extra sentence stating that the first split is an initial condition and that equation (1) applies only once there are at least two lines.

---

### 2. History Kernel Needs An Event-Level Definition

**Status**: [Pending]

**Quote**:
> Formally we define $\mathcal{H}$ to be the type of the MRCA, together with an ordered list of the split and mutation events which occur in the typed ancestry (including the details of the genetic type or types involved in each event, but not including the details of exactly which line was involved in each event). The history $\mathcal{H}$ thus includes a record of the states $(H_{-m}, H_{-(m-1)}, \ldots, H_1, H_0)$ visited by a Markov process beginning with the genetic type $H_{-m} \in E$ of the MRCA and ending with the genetic types $H_0 \in E^n$ corresponding to the genetic types of a random sample. Here $m$ is random, and the $H_i$ are unordered lists of genetic types. For notational convenience we shall write $\mathcal{H} = (H_{-m}, H_{-(m-1)}, \ldots, H_1, H_0)$, although $\mathcal{H}$ actually contains details of the transitions which occur between these states (which may not be uniquely determined by the list of states if $P_{\alpha \alpha} > 0$ for more than one $\alpha \in E$).

**Feedback**:
This defines $\mathcal{H}$ as an event-level object, but equation (1) is written on unordered states. When self-mutations are possible for more than one type, distinct events can leave the same state unchanged, so the displayed kernel is ambiguous unless the transition law is defined first on labelled events and only then aggregated. A short clarification would fix this: say whether $p_{\theta}(H_i\mid H_{i-1})$ is an event kernel or a state kernel obtained by summing over all events that produce the same state.

---

### 3. Metropolis-Hastings Needs The Complete-Data Density

**Status**: [Pending]

**Quote**:
> If $\mathcal{T}$ represents missing data for which $\pi_{\theta}(A_n | \mathcal{T})$ is (relatively) easy to calculate, then it is straightforward to use the Metropolis–Hastings algorithm to construct a Markov chain with stationary distribution $P_{\theta}(\mathcal{T} | A_n)$.

**Feedback**:
An easy evaluation of $\pi_{\theta}(A_n\mid \mathcal{T})$ is not enough by itself to build a generic Metropolis-Hastings chain for $P_{\theta}(\mathcal{T}\mid A_n)$. The acceptance ratio depends on the joint quantity $P_{\theta}(\mathcal{T},A_n) \propto \pi_{\theta}(A_n\mid \mathcal{T})P_{\theta}(\mathcal{T})$, so the prior term on $\mathcal{T}$ must also be available unless a special proposal makes it cancel. Tighten this sentence to refer to the complete-data density rather than only the conditional likelihood.

---

### 4. Proposition 1(d) Proves Uniqueness But Not Existence

**Status**: [Pending]

**Quote**:
> If $\tilde{\pi}$ satisfies property (b) of the proposition, then $M^{(1)} = (1 - \lambda_1)(I - \lambda_1P)^{-1}$. It then follows from equation (23) and mathematical induction that $M^{(n)} = (1 - \lambda_n)(I - \lambda_nP)^{-1}$, and so $\tilde{\pi} = \hat{\pi}$.

**Feedback**:
As written, the proof after equation (23) shows uniqueness once the consistency relation is assumed, but it never verifies that the matrices in equation (19) actually satisfy equation (23). That check is short: with $A=\theta(I-P)$, $M^{(n)}=n(nI+A)^{-1}$, and the resolvent identity gives (23). Adding that line would close the argument cleanly.

---

### 5. The NSE Type Space Has The Wrong Dimension

**Status**: [Pending]

**Quote**:
> The type space is large ( $E = \{0,1,\dots,19\}^3$ )

**Feedback**:
The preceding sentence says each haplotype is observed at five loci, so the natural state space is a five-coordinate vector of repeat counts. The stated space $\{0,1,\ldots,19\}^3$ is therefore inconsistent with the model description. If only three loci were analyzed, say so explicitly. Otherwise this should be $\{0,1,\ldots,19\}^5$.

---

### 6. The Underestimation Claim Needs A Finite-Run Qualification

**Status**: [Pending]

**Quote**:
> As a result such methods will tend to underestimate the relative likelihood away from θ_{0}, leading to an estimated curve which is artificially peaked about this driving value (which we believe helps to explain the overly peaked curves in Fig. 2(c) for example).

**Feedback**:
This moves too quickly from skewed weights to a blanket underestimation claim. Once the first moment exists, the importance-sampling estimator is still unbiased; the practical problem is that finite runs often miss the rare large weights that matter away from $\theta_0$, so a typical run can fall below the truth and look too sharply peaked near the driving value. Rephrase the point in that finite-sample sense.

---

### 7. The Ascertainment Restriction Is Too Weak

**Status**: [Pending]

**Quote**:
> For the IS schemes that we have considered, assuming the infinite sites mutation model, the ascertainment effect can be accommodated by labelling every lineage which leads to any chromosome in the panel as a panel lineage and adapting both P_{θ}(ℋ) and Q_{θ}(ℋ) so that mutations can occur only on panel lineages.

**Feedback**:
That does not yet encode the stated discovery rule. A mutation ancestral to every panel chromosome still lies on a panel lineage, but it leaves the panel monomorphic and would not have been retained. The condition has to be sharper: retained-site mutations must fall on branches whose descendants contain a non-empty proper subset of the panel.

---

### 8. The Non-Varying-Sites Paragraph Conditions On Too Much

**Status**: [Pending]

**Quote**:
> Most of the information about the history $\mathcal{H}$ is in the bases which vary between chromosomes, and it would be much more efficient to define the IS distribution on the basis of those positions which are varying. The effect of the non-varying sites could then be taken into account by the factor $\pi_{\theta}(A_n|\mathcal{H}^{(i)})$ in estimator (9), which could be calculated by the peeling algorithm (to do this it would be necessary to apply IS to the full typed ancestry $\mathcal{A}$ of the sample).

**Feedback**:
The logic changes mid-paragraph. A peeling factor is useful when the proposal samples a reduced latent object, such as a genealogy or partial history, that does not already determine every observed base. If the sampler is instead run on the full typed ancestry $\mathcal{A}$, then the leaf types are already fixed and $\pi_{\theta}(A_n\mid\cdot)$ collapses to 1 or 0. This section should say explicitly which latent object is being proposed when the peeling correction is introduced.

---

### 9. The Pareto Bootstrap Needs A Shape Check

**Status**: [Pending]

**Quote**:
> In particular we propose fitting a generalized Pareto distribution (see Davison and Smith (1990) for example) to the weights above some threshold, and using a parametric bootstrap to estimate confidence intervals for the mean of the weights (i.e. the estimate of the likelihood).

**Feedback**:
A generalized Pareto tail supports inference for the mean only when the fitted shape parameter is below 1. If it is at least 1, the fitted tail has no finite mean; if it is at least 1/2, variance-based summaries are unstable as well. Because this section is motivated by exactly those heavy-tail cases, those conditions need to be stated up front.

---

### 10. The Tree Count Mixes Topology With Merger Order

**Status**: [Pending]

**Quote**:
> For example, there are $n!(n-1)!/2^{n-1}$ different possible topologies for the underlying trees.

**Feedback**:
The quantity $n!(n-1)!/2^{n-1}$ counts ranked labelled coalescent histories, not tree topologies alone. That distinction is easy to miss here, and it matters because the sentence uses the formula as an illustration of topological complexity. Replace 'topologies' with 'ranked labelled histories', or add the separate topology count if topology is what you want to emphasize.

---

### 11. The Likelihood Versus Log-Likelihood Argument Needs Tightening

**Status**: [Pending]

**Quote**:
> From a classical perspective it would be more natural to consider estimating and plotting log-likelihood surfaces. However, because of the limited information in data, it is at best unclear whether the classical asymptotic theory relating to the interpretation of the log-likelihood applies in genetics settings of interest. (Further work on this question would be welcomed.) From a Bayesian viewpoint, the likelihood is of more natural interest than is the log-likelihood. In part for these reasons, and in part to facilitate a direct comparison with published estimates, we focus here on likelihood and relative likelihood estimation.

**Feedback**:
The real issue here is calibration, not information content. Likelihood and log-likelihood carry the same inferential ordering, and Bayesian analysis does not privilege one over the other. What is genuinely doubtful in these small-sample genetics problems is the large-sample interpretation of log-likelihood differences. Recast the paragraph around that point, then say that the likelihood scale is used mainly to match the published literature.

---

### 12. Formula (8) Recasts The Problem Rather Than Replacing The Model-Specific Work

**Status**: [Pending]

**Quote**:
> For example, the various recurrence and integrorecurrence equations derived in Griffiths and Tavaré (1994a, b, c, 1999) for the coalescent, Bahlo and Griffiths (2000) for the structured coalescent, Griffiths and Marjoram (1996) for the ancestral recombination graph and Slade (2000) for the ancestral selection graph are all effectively replaced by the standard IS formula (8).

**Feedback**:
Equation (8) is a generic importance-sampling identity. It gives a new representation of the same likelihood, but it does not by itself remove the model-specific work that earlier recurrence arguments handled. The hard part remains choosing missing data, building a usable proposal, and evaluating weights. The conclusion would read more accurately if it said that these problems are re-expressed in IS form rather than simply replaced by formula (8).

---
