# Inference in molecular population genetics

**Date**: 03/04/2026
**Domain**: statistics/statistical_methodology
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Statistical Validity of Inference and Estimator Properties**

The authors explicitly state they could not prove the finiteness of the variance of importance weights except in special cases, which invalidates the Central Limit Theorem application and renders reported standard errors (Table 1, Figures 2-4) theoretically unjustified. Compounding this, the authors acknowledge uncertainty regarding whether classical asymptotic theory applies to the log-likelihood in this context, yet proceed to use likelihood surfaces for inference without alternative validation. Additionally, standard convergence diagnostics are acknowledged to suffer if weight variance is underestimated, with proposed solutions lacking validation. Consequently, both the uncertainty estimates and the statistical significance of the inference claims lack rigorous frequentist justification.

**Restrictive Model Assumptions Limit Practical Applicability**

The methodology restricts analysis to chromosomal regions ignoring recombination and assumes constant population size, assumptions explicitly challenged by discussants as unrealistic for most modern genetic data. While the Abstract claims to address 'modern population genetics data,' the method is applied to sequence and microsatellite data in Section 5 without quantifying the bias introduced by violating these core demographic and genetic assumptions. This significantly reduces the practical utility of the proposed method for the stated domain unless extensions or defensibility limits are clearly provided.

**Insufficient Scalability and Efficiency Analysis**

Despite Abstract claims of improving efficiency by 'several orders of magnitude' for 'modern data,' empirical benchmarks are limited to relatively small problems (e.g., 50 sequences), and Section 6.5 admits many real datasets remain beyond computational limits. The paper lacks a formal analysis of computational complexity (e.g., Big-O notation) with respect to sample size and loci. Without theoretical scaling analysis or larger empirical validation, the claim that the method resolves computational challenges for large-scale genomic data is unsupported.

**Incomplete Theoretical Grounding of Proposal Distribution**

Section 4 introduces the proposal distribution $Q_{SD}$ as an approximation to the optimal $Q^*$ without providing theoretical bounds on their divergence for general demographic scenarios. Furthermore, the extension to the Infinite Sites model relies on an 'analogy with proposition 2' rather than a rigorous derivation, leaving the optimality and correctness of the proposal distribution for this widely used model unsupported. These gaps make the efficiency claims contingent on unverified approximation quality and may not hold for complex models outside the tested examples.

**Inadequate Methodological Benchmarking and Comparison**

The comparison with existing MCMC methods (e.g., Fluctuate) rests on a baseline that may not have been optimally tuned or converged for the specific data used, as noted in the Discussion. Additionally, discussants highlight fundamental differences in parameterization (genealogical trees vs. topology with mutations) that affect search space and convergence, creating a confounding factor in the performance comparison. The paper does not standardize representations or acknowledge these structural differences, making it unclear whether performance advantages reflect algorithmic efficiency or implementation details.

**Infinite Sites Model Violates Stationary Distribution Assumption**

The theoretical framework explicitly assumes the mutation transition matrix P has a unique stationary distribution (Section 2: 'we focus on the case where P has a unique stationary distribution'). However, the paper acknowledges that for the infinite sites model, 'the transition matrix P does not have a stationary distribution.' While a workaround is proposed (measuring types relative to the MRCA with arbitrary type assignment), this represents a fundamental theoretical inconsistency. The optimal proposal distribution characterization (Theorem 1) and the importance sampling weights depend on the stationary distribution, meaning the elegant theoretical results do not directly apply to one of the most commonly used mutation models in population genetics without modification.

**Stationarity Assumption Lacks Verification in Applications**

The likelihood formulation fundamentally requires that samples are 'taken from the population at stationarity' (Section 2), which ensures the MRCA type distribution follows the stationary distribution of the mutation Markov chain. This assumption is critical for Algorithm 1 Step 1 and the entire coalescent-based likelihood framework. However, the paper does not describe any diagnostics or methods to verify whether this assumption holds for empirical datasets in the applications section. Real population genetic data often comes from populations that may not be at mutation-drift equilibrium (e.g., recently expanded, bottlenecked, or structured populations), and applying these methods without verifying stationarity could lead to biased parameter estimates and incorrect inference.

**Constant Population Size Coalescent Approximation Conditions Not Verified**

The methods rely on the n-coalescent approximation, which is valid when population size N is large and the sample size n is small relative to N (n/N << 1). The paper states they focus on 'populations of constant (large) size N' and uses the coalescent timescale in units of N generations. However, the applications section does not explicitly verify whether the example datasets or simulation parameters satisfy the N >> n condition required for the coalescent approximation to be accurate. If examples use parameter values where this approximation breaks down (e.g., large sample fractions or small effective population sizes), the theoretical guarantees underlying the importance sampling and MCMC methods would not hold, potentially affecting the validity of the efficiency comparisons presented.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Stationarity assumption contradicted by infinite sites model application [CRITICAL]

**Status**: [Pending]

**Quote**:
> To simplify the description we focus on the case where P has a unique stationary distribution.

**Feedback**:
Section 2 assumes P has a unique stationary distribution for the theoretical framework, but Section 5.5 applies the method to the infinite sites model where 'the transition matrix P does not have a stationary distribution.' This internal contradiction undermines the theoretical grounding since Theorem 1 and the importance sampling weights depend on the stationary distribution. The workaround (measuring types relative to MRCA) does not resolve this fundamental inconsistency.

---

### 6. Sample variance underestimation claim is statistically incorrect [CRITICAL]

**Status**: [Pending]

**Quote**:
> ing ®nite variance /C40.\_which is not guaranteed) the distribution of the weights may be so highly skewed that, even for very large M ,  2 is /C40.\_with high probability) underestimated by ^  2 , and

**Feedback**:
For the standard unbiased sample variance estimator σ̂² = (1/(M-1)) Σ(w_i - w̄)², we have E[σ̂²] = σ² regardless of distribution skewness (assuming finite variance exists). The sample variance is unbiased, not systematically underestimated. The actual issue is that Var(σ̂²) can be very large with skewed weights, making individual estimates highly variable. The statement should read 'σ̂² may have high variance and poor convergence properties' rather than 'σ² is underestimated by σ̂²'.

---

### 7. Incorrect count of rooted gene trees for infinite sites model [CRITICAL]

**Status**: [Pending]

**Quote**:
> There are S  1 such rooted gene trees, where S is the number of mutations in the data.

**Feedback**:
This claim is mathematically incorrect for general infinite sites data. The number of compatible rooted gene trees depends on the tree topology and sample size n, not just S. For an unrooted tree with n sequences, there are 2n-3 branches where the root can be placed (for n≥3). For example, with n=4 sequences and S=3 mutations, there are 2(4)-3=5 possible root positions, not S+1=4. The correct statement should reference that the number depends on both n and the specific mutation configuration.

---

### 12. MCMC posterior sampling framework incorrectly claims absolute likelihood estimation [CRITICAL]

**Status**: [Pending]

**Quote**:
> e of MCMC methods to sample from the conditional distribution of the missing data, again at one particular  -value, with IS /C40.\_(via equation /C40.\_7)) to estimate the likelihood surface; MC

**Feedback**:
Using samples from the posterior distribution Q(H) = P(Data|H)P(H)/L(θ₀) as the proposal in standard IS does not allow calculation of the absolute likelihood surface. The IS weights w = P(Data|H)P(H)/Q(H) simplify to L(θ₀), which is unknown. One can only estimate likelihood ratios, not the absolute surface, unless L(θ₀) is known by other means. The text implies absolute likelihood estimation is possible here, which is theoretically incorrect for this setup.

---

### 15. Central Limit Theorem application unjustified without variance finiteness proof [CRITICAL]

**Status**: [Pending]

**Quote**:
> which is not guaranteed) the distribution of the weights may be so highly skewed

**Feedback**:
The authors explicitly acknowledge they could not prove finiteness of the variance of importance weights except in special cases, yet proceed to apply the Central Limit Theorem for standard error calculations in Table 1 and Figures 2-4. Without finite variance, the CLT does not apply and reported confidence intervals are theoretically unjustified. This undermines all uncertainty quantification in the paper's results.

---

### 2. Algorithm 1 rate parameter contains encoding corruption

**Status**: [Pending]

**Quote**:
> : if there are currently k lines in the ancestry, wait a random amount of time which is exponentially distributed with rate parameter  k  k k  1   2 and t

**Feedback**:
The rate parameter formula in Algorithm 1 Step 2 contains corrupted characters (, , , , ) that obscure the mathematical expression. The standard coalescent rate should be λ_k = [k(k-1) + kθ]/2, but the garbled text prevents verification. Additionally, the probability expression 'k 1 k 1' is unintelligible, making algorithm implementation impossible from the published text.

---

### 3. Mutation matrix P assumed known contradicts stated inference goals

**Status**: [Pending]

**Quote**:
> se of exposition we focus on the problem of likelihood inference for  /C40.\_assuming P is known). We

**Feedback**:
Section 3 states P (mutation matrix) is assumed known for inference on θ, yet Section 3 lists inference for 'the mutation matrix P' itself as question (a) of interest. This creates an internal contradiction where P is both a target parameter and a fixed assumption. The methodology excludes P from inference while the problem formulation includes it, creating ambiguity about what the method actually estimates.

---

### 8. Efficiency claim contradicted by NSE dataset runtime comparison

**Status**: [Pending]

**Quote**:
> suggests that for this problem our IS method is considerably more ecient than micsat

**Feedback**:
Section 5.4 claims the IS method is 'considerably more efficient than micsat' based on Fig. 4 results (30s vs 1.5h). However, for the NSE dataset in Fig. 5, the IS method took 18h per run while micsat took 4.5h, and the text admits micsat was 'more accurate.' This contradicts the general efficiency claim for challenging datasets and undermines the section's conclusion about IS superiority over MCMC methods.

---

### 9. Truncation violates stated model invariance property for microsatellites

**Status**: [Pending]

**Quote**:
> Under this mutation model the joint distribution of sample con®gurations is invariant under the addition of any ®xed number of repeats to each sampled allele

**Feedback**:
Section 5.4 states the stepwise mutation model is invariant under addition of repeats (implying infinite support), but the implementation truncates the space to {0,...,19} with reflecting boundaries ('insisting that all mutations to alleles of length 0 or 19 involve the gain or loss'). This violates the invariance property for alleles near boundaries, potentially biasing likelihood estimates if the stationary distribution has mass near 0 or 19.

---

### 14. Theta parameter notation corrupted throughout Section 5.1

**Status**: [Pending]

**Quote**:
> Our focus throughout the paper is inference for

**Feedback**:
The parameter θ (theta), the standard population genetics mutation parameter (θ = 4Nμ), appears as the garbled character '' throughout Section 5.1. This encoding error occurs in multiple places: 'Q SD ', 'Q * ', 'P '. The correct notation should be θ consistently. This affects mathematical precision and cross-referencing with earlier sections where θ is defined, making verification of equation references like 'equation (9)' and 'equation (16)' impossible with corrupted notation.

---

### 4. Theorem 1 uses n for two different quantities [MINOR]

**Status**: [Pending]

**Quote**:
> he number of chromosomes of type in Hi . The constant of proportionality C is given by

**Feedback**:
In Theorem 1, the variable 'n' is used to denote two different quantities in consecutive sentences: first as 'the number of chromosomes of type [α] in Hi' (a specific type count), then as 'the number of chromosomes in Hi' (total count). These cannot both be true. The first should read 'where n_α denotes the number of chromosomes of type α in Hi' to distinguish from the total chromosome count n, creating ambiguity in the optimal proposal distribution formula.

---

### 5. Proposition 1 properties enumerated out of alphabetical order [MINOR]

**Status**: [Pending]

**Quote**:
> ecoded --> Proposition 1 . The distribution ^  . j An  de®ned by de®nition 1 has the following properties.

**Feedback**:
The properties in Proposition 1 are enumerated as (a), (c), (b), (d), (e) instead of alphabetical order (a), (b), (c), (d), (e). Property (c) appears before property (b) in the text. This is a clear typographical error in the proposition statement that affects readability and reference consistency when citing specific properties later in the paper.

---

### 10. Type space notation E reused inconsistently for single and multi-locus spaces [MINOR]

**Status**: [Pending]

**Quote**:
>  The type space is large /C40.\_ E  f 0, 1, . . ., 19 g 5

**Feedback**:
The symbol E is initially defined as the single-locus allele space ({0,...,19}) in Section 5.4's first paragraph, but here redefined as the 5-locus genotype space (E^5) without clarification. This notational inconsistency creates ambiguity in the likelihood formulation and transition probability definitions, as E cannot represent both sets simultaneously. The multi-locus space should be denoted E^5 or E_multi to distinguish from the single-locus definition.

---

### 11. Scaling factor notation contains undefined symbols [MINOR]

**Status**: [Pending]

**Quote**:
> maller by a factor of 500 p  22

**Feedback**:
The symbols 'p' and '' are undefined or corrupted in the text, likely intended to represent the square root function (√) and approximation (≈). The standard error should scale by 1/√N, where N_ratio = 10^7 / 20,000 = 500, giving √500 ≈ 22. The expression should read 'smaller by a factor of √500 ≈ 22' to clearly convey the mathematical relationship from the Central Limit Theorem.

---

### 13. Inconsistent equation references for likelihood surface estimation frameworks [MINOR]

**Status**: [Pending]

**Quote**:
> shed: the use of IS to estimate the likelihood at one particular value of  , with further IS /C40.\_(via equation /C40.\_12)) to estimate the likelihood

**Feedback**:
Section 3.4 describes three frameworks for likelihood estimation. Framework 1 correctly identifies Eq. (12) for surface estimation via reweighting samples from a single IS function. However, Framework 2 describes an analogous reweighting process (samples from a θ₀-specific distribution to estimate the surface) but cites Eq. (7). Since both frameworks rely on the same mathematical identity to estimate the likelihood surface from samples generated at fixed θ₀, they should reference the same reweighting equation (Eq. 12), creating notational inconsistency.

---
