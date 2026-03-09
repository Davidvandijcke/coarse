# Regression Discontinuity Design with Distribution-Valued Outcomes

**Date**: 03/04/2026
**Domain**: statistics/causal_inference
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Identification relies on untestable continuity of average quantile functions**

The core identification assumption (I1) requires continuity of the conditional average quantile function E[Q_Y(q)|X=x] at the cutoff for all quantiles q. While presented as a mild generalization of standard RDD continuity, this functional continuity assumption is inherently untestable and its plausibility in applications like gubernatorial elections is difficult to assess. Strategic sorting or manipulation around the cutoff could induce discontinuities in the average distribution even if mean income is continuous. The paper should discuss substantive conditions under which I1 holds and propose diagnostic procedures, such as extending placebo tests or density tests to the distributional context.

**Inadequate treatment of within-group dependence in theory and application**

The asymptotic theory assumes i.i.d. sampling of group-level distributions (L1), but in practice, these distributions are constructed from micro-units (e.g., families within states) that are likely correlated. This within-group dependence violates the i.i.d. assumption for the empirical quantile functions and could affect the convergence rate r_{n_i} in Assumption Q1. The multiplier bootstrap validity relies on independence across groups, which may not hold if there are spatial or temporal correlations. The paper should address how within-group clustering affects asymptotic variance and discuss whether cluster-robust adjustments are needed for the empirical quantile estimation stage.

**Unverified justification for single bandwidth selection in Fréchet estimator**

The proposed integrated MSE-optimal bandwidth for the Fréchet estimator relies on Lemma A-9, which claims asymptotic equivalence between the Fréchet and local polynomial estimators' IMSE. The derivation shows a pointwise o_p((nh)^{-1/2}) difference, but for IMSE equivalence, one needs the integrated squared difference to be o_p(1/(nh)). The current argument using Cauchy-Schwarz appears insufficiently rigorous. A more careful analysis of the L² norm difference is needed to ensure the bandwidth selector is truly optimal for the Fréchet estimator's IMSE, especially given that the projection operation could alter the bias-variance trade-off differently across quantiles.

**Potential gaps in the proof of Hadamard differentiability**

Theorem 4 relies on Lemma A-7, which states the L² projection operator onto quantile functions is Hadamard differentiable at a strictly increasing limit. The proof invokes results from Zarantonello (1971) but requires that for any direction h in C([a,b]), the path m + t_n h remains within the convex cone Q for sufficiently small t_n. While this holds for smooth h, the limit process G_H± from Theorem 1 is a Gaussian process with continuous but not necessarily differentiable sample paths. The paper needs to rigorously justify that Hadamard differentiability holds tangentially to C([a,b]), not just for smooth directions, perhaps by invoking more general results on projections onto convex sets in Banach spaces.

**Ambiguous causal interpretation and strong assumptions in fuzzy design**

The fuzzy RDD estimand τ_F3D(q) is interpreted as a Local Average Quantile Treatment Effect for compliers, but requires strong monotonicity (I5: essentially all groups are compliers). In the gubernatorial application, this means all states near the cutoff would change governor party based on tiny vote share changes—a strong assumption. Additionally, the interpretation of distribution-valued treatment effects for complier groups is less straightforward than in scalar cases. The paper should discuss the plausibility of I5 in empirical contexts and clarify the population to which LAQTE applies, especially when group sizes vary substantially.

**Empirical application lacks robustness and has potential confounding**

The gubernatorial election results show sensitivity to estimator choice, kernel, and bandwidth, particularly for the homogeneity test central to the equality-efficiency trade-off narrative. Effects are identified using a 3-4 year lag, during which time-varying confounders (national economic shocks, federal policies) could differentially affect states with Democratic versus Republican governors. While the paper includes a robustness check using election-year incomes, it doesn't fully address potential interference between states or systematic differences in economic shocks correlated with party control. A more systematic sensitivity analysis and discussion of the no-interference assumption's plausibility would strengthen the empirical findings.

**Empirical quantile functions may violate the fully observed quantile assumption**

The theoretical framework assumes that the full quantile functions Q_Y_i(q) are observed for each unit i (e.g., all employees within a firm). However, the empirical application uses CPS data, which provides only a sample of families within each state-year. While Proposition 2 extends the theory to empirical quantile functions under Assumption Q1, this requires that within-group sample sizes n_i are large enough relative to the across-group sample size n to ensure the empirical quantile estimator converges faster than the R3D estimator rate (√(nh)). The paper does not verify whether this condition holds in the application. If within-state samples are too small, the asymptotic approximations may break down, potentially biasing inference.

**Bandwidth selection for Fréchet estimator relies on asymptotic equivalence**

The Fréchet estimator uses a single bandwidth selected by minimizing the integrated MSE (IMSE) derived from the local polynomial estimator's asymptotic MSE, based on Lemma A-9 which shows the difference between the two estimators is o_p((nh)^{-1/2}). However, in finite samples, especially with limited data near the cutoff, this asymptotic equivalence may not hold perfectly. The simulations show the Fréchet estimator has lower bias and variance than the local polynomial estimator for small samples, suggesting their finite-sample behaviors differ. Using the local polynomial's optimal bandwidth for the Fréchet estimator might not be optimal, though the paper notes this approach is justified asymptotically. A more robust approach would be to derive the Fréchet estimator's finite-sample properties directly or use cross-validation as suggested for distributional settings.

**Status**: [Pending]

---

## Detailed Comments (22)

### 1. Inconsistent notation for conditional expectation operator

**Status**: [Pending]

**Quote**:
> ght) 1(|x/h_1(q)| \le 1)$$ and $$\hat{\mathcal{E}}_2(y, t, x, q) = \left(T - \tilde{E}[T \mid X = x]\right) 1(|x/h_2(q)| \le 1)$$

**Feedback**:
The notation \(\tilde{E}\) is used for a conditional expectation in the definition of residuals. In the context of defining the population treatment assignment mechanism, the standard expectation operator \(E[\cdot|X=x]\) should be used. If \(\tilde{E}\) is intended to denote an estimator, then the equations define estimated residuals, which is inconsistent with the surrounding text discussing population quantities. The notation should be clarified to avoid confusion.

---

### 2. Incomplete or malformed LaTeX expression for pdf

**Status**: [Pending]

**Quote**:
> Finally, denote the marginal distributions of X and Y as F X , F Y , with f X := ∂F X ( x ) ∂x the pdf of X which will be well-defined near the cutoff c under the stated assumptions.

**Feedback**:
The derivative notation "∂F_X(x) ∂x" is malformed; it appears to be missing a fraction bar or division symbol. The standard definition of the probability density function is \(f_X(x) = dF_X(x)/dx\) or \(f_X(x) = F_X'(x)\). The current expression is not valid mathematical notation and should be corrected.

---

### 3. Incorrect characterization of Card and Krueger (2000) design

**Status**: [Pending]

**Quote**:
> In another seminal article, Card and Krueger (2000) studied the effect of a minimum wage increase ( T ) in New Jersey on wages, employment, and prices in fast food restaurants, comparing establishments on either side of the border with Pennsylvania. The running variable here is distance to the border ( X ) . Since establishments typically sell many items and employ tens to hundreds of employees, one could, with the right data, observe entire distributions ( Y ) for each establishment.

**Feedback**:
The Card and Krueger (2000) study is a canonical difference-in-differences design, not a regression discontinuity design (RDD). Treatment (the minimum wage increase) applies uniformly to all establishments in New Jersey, regardless of their distance to the Pennsylvania border. There is no known discontinuity in treatment probability at a specific distance cutoff. Using this as an example of an RDD is incorrect and misleading for the R3D framework, which requires a discontinuous treatment assignment rule based on a running variable.

---

### 4. Ambiguous claim about 'close-election' RD designs

**Status**: [Pending]

**Quote**:
> Furthermore, since vote-based allocation systems typically aggregate decisions of many individuals into higher-level outcomes, many instances of the ubiquitous 'closeelection' RD design fall under the R3D framework.

**Feedback**:
The claim is ambiguous. For a close-election RD to fall under the R3D framework, the *outcome variable* for each unit (e.g., electoral district) must be a distribution (e.g., the distribution of constituent incomes), not just that treatment assignment is based on aggregated votes. The statement as written could be misinterpreted to include all close-election RDDs, which typically have scalar outcomes. It would be helpful to clarify that R3D applies specifically when the outcome of interest is distribution-valued.

---

### 5. Proposition 1(ii) proof step requires clarification

**Status**: [Pending]

**Quote**:
> Proof. (i) Follows from independence and continuity of µ ( · , q ) . (ii) For any pair ( i, j ) ,
> 
> <!-- formula-not-decoded -->
> 
> <!-- PAGE BREAK -->
> 
> Conditional on ( X i , X j ) , the difference ε i ( q ) -ε j ( q ) has a continuous density, so it equals the fixed value -{ µ ( X i , q ) -µ ( X j , q ) } with probability 0 . A finite union over pairs yields the claim.

**Feedback**:
The proof for part (ii) is incomplete as presented. It correctly argues that for a fixed pair (i,j), \(P(Q_{Y_i}(q) = Q_{Y_j}(q) | X_i, X_j) = 0\). To extend this to the event that *any* pair among units with \(|X_i|, |X_j| < \delta\) has equal quantiles, one must apply the union bound over all \(O(n^2)\) such pairs. The phrase 'A finite union over pairs yields the claim' is correct but should be explicitly connected to the union bound: \(P(\exists i\neq j: Q_{Y_i}(q)=Q_{Y_j}(q), |X_i|,|X_j|<\delta) \le \sum_{i<j} P(Q_{Y_i}(q)=Q_{Y_j}(q) | |X_i|,|X_j|<\delta) = 0\).

---

### 6. Lemma 1 identification formula missing explicit limit notation

**Status**: [Pending]

**Quote**:
> Lemma 1 (Identification) . Under Assumptions I1 and I2, for a given q ∈ [0 , 1] , the unobserved τ R3D ( q ) is identified from the joint distribution of the observed ( X,Y ) as,
> 
> <!-- formula-not-decoded -->
> 
> Note that the lemma implicitly defines m ± ( q ) and m ( q ). Thus, the R3D estimand is the jump in the conditional average quantile at x = 0.

**Feedback**:
The identification formula in Lemma 1 is presented as a placeholder without explicit mathematical notation. Based on the text, the identified expression should be \(\tau_{R3D}(q) = \lim_{x \downarrow 0} E[Q_Y(q)|X=x] - \lim_{x \uparrow 0} E[Q_Y(q)|X=x]\). The lemma should explicitly state this formula and define \(m_+(q)\) and \(m_-(q)\) as these one-sided limits. The current presentation omits the core mathematical result.

---

### 7. Incomplete and garbled mathematical expression for discontinuity definition

**Status**: [Pending]

**Quote**:
> Thus, I can define a discontinuity in our setting to occur when, for some q ∈ [0 , 1]
> 
> ̸
> 
> <!-- formula-not-decoded -->

**Feedback**:
The text contains a garbled and incomplete mathematical expression intended to define a discontinuity. The characters '̸' and the HTML comment are not valid notation. This makes the precise definition unclear. It should be replaced with a complete, well-defined condition, such as: 'Thus, I can define a discontinuity in our setting to occur when, for some \(q \in [0,1]\), \(\lim_{x \downarrow 0} E[Q_Y(q)|X=x] \neq \lim_{x \uparrow 0} E[Q_Y(q)|X=x]\)'.

---

### 8. Mischaracterization of Quantile RD Estimator's Target

**Status**: [Pending]

**Quote**:
> Thus, the R3D aims to estimate a conditional average quantile. The Q-RDD on the other hand, aims to estimate a fixed distribution function. Practically, they do so with the following local linear estimators,
> 
> <!-- formula-not-decoded -->
> 
> As can be seen, the R3D approach fi rst estimates quantiles and only then runs a local
> 
> <!-- PAGE BREAK -->
> 
> regression. This properly accounts for the two-level randomness intrinsic to the R3D setting. Distribution estimation at a given X = x precedes smoothing. By contrast, the Q-RDD estimator intrinsically estimates the distribution by smoothing, ignoring the randomness across units. In the presence of such randomness, the observed distributions will almost surely not vary smoothly, and the Q-RD approach will be biased and inconsistent.

**Feedback**:
The claim that the Quantile RD (Q-RDD) estimator targets a 'fixed distribution function' and ignores randomness across units is incorrect. The standard Quantile RD estimator (Frandsen et al., 2012) targets the conditional quantile function \(Q_{Y|X}(q | x)\), a functional parameter of the population conditional distribution of a scalar outcome Y given X. It uses local linear smoothing of i.i.d. scalar observations \((Y_i, X_i)\) and accounts for their randomness. The statement that it 'ignores the randomness across units' misrepresents the method. The bias claim is unsubstantiated without a formal comparison of probability limits under the R3D data-generating process.

---

### 9. Incorrect Description of Q-RDD Sampling Model

**Status**: [Pending]

**Quote**:
> First, as mentioned, the sampling model imposed by the Q-RDD setting does not correctly represent the underlying data-generating process. In particular, it assumes i.i.d. sampling of scalar-valued outcomes instead of distribution-valued ones, which ignores the within-unit sampling that characterizes the R3D setting. As such, the sampling framework of the Q-RD design could never result in multiple data points having the same value of the (continuous) running variable.

**Feedback**:
The claim that the Q-RDD sampling framework 'could never result in multiple data points having the same value of the (continuous) running variable' is false. In standard RD applications, multiple units can share the same value of a continuous running variable due to measurement precision or discrete measurement. The i.i.d. assumption does not preclude ties. The core issue is that Q-RDD treats each scalar outcome as an independent observation, ignoring the grouped structure where multiple scalars come from the same aggregate unit. This grouped structure induces dependence, violating the i.i.d. assumption if the unit-level distribution is the target, not the impossibility of tied X values.

---

### 10. Overstated Restrictiveness of Quantile Continuity Assumption

**Status**: [Pending]

**Quote**:
> Second, as mentioned, the quantile continuity assumption required for the identification of the estimator in Frandsen et al. (2012) is highly restrictive in the R3D setting, requiring that two units that are both close to the threshold have essentially identical distributions. In the examples in Section 2.2, this would imply that, conditional on having the same value of the running variable, two different restaurants would have the exact same distributions of product prices, two different schools the same distribution of tests, and two different counties the same distribution of child mortality.

**Feedback**:
This misstates the continuity assumption in standard quantile RD. The assumption is continuity of the population conditional quantile function \(Q_{Y|X}(q | x)\) at the cutoff. This is a property of the population distribution of Y given X, not a requirement that two individual units with the same X have identical outcome distributions. Heterogeneity across units with the same X is allowed. The text confuses the population conditional distribution with unit-specific distributions. A correct comparison would note that applying standard quantile RD to scalar outcomes from grouped data requires continuity of the marginal quantile function, which may differ from the R3D assumption (I1).

---

### 11. Incorrect statement about equivalence of ATE estimands

**Status**: [Pending]

**Quote**:
> Moreover, the implied average treatment effect is identical, since, under Fubini-Tonelli,
> 
> <!-- formula-not-decoded -->
> 
> so that first estimating R3D and then averaging estimates the same ATE as first averaging and then estimating a standard local polynomial regression.

**Feedback**:
The claim that the ATE estimands are identical is incorrect without additional assumptions. Let \(Y_{ij}\) be individual j in group i. The group-average approach estimates \(E[E[Y_{ij}|X=x]]\), where the inner expectation averages over individuals within a group. The R3D approach, after averaging distributions, estimates \(E[F_{Y|X=x}]\), where F is the conditional distribution. These are generally different unless group sizes are equal or the conditional distribution of Y given X is homogeneous across groups. The Fubini-Tonelli theorem allows swapping integration order, but the averaging operations are different: one averages individual outcomes, the other averages distribution functions. The equivalence does not hold in general.

---

### 12. Ambiguous claim about clustering and estimands

**Status**: [Pending]

**Quote**:
> Clustering helps adjust standard errors, but does not affect the estimand. The strategy of first aggregating to the group level and then estimating treatment effects, on the other hand, will estimate the unweighted average treatment effect and inherently accounts for clustering (Bartalotti and Brummet, 2017).

**Feedback**:
The statement that clustering 'does not affect the estimand' is misleading. While clustering corrects standard errors for within-group correlation, the estimand itself can differ. An individual-level regression with clustering estimates a group-size-weighted ATE (weighted by the number of individuals per group). A group-level regression estimates an unweighted ATE (each group gets equal weight). These are different population quantities unless group sizes are equal. The paper should clarify that clustering adjusts inference for the estimand from the individual-level regression, but that estimand is inherently weighted by group size.

---

### 13. Missing definition of projection operator Π_Q

**Status**: [Pending]

**Quote**:
> where Q ( Y ) is the space of quantile functions of the cdfs in Y , restricted to [ a, b ] ⊆ [0 , 1]. I define Π Q as the L 2 projection onto that space of restricted quantile functions. 2 In Proposition A-3, I show that ˆ m ± , ⊕ ,p is unique and exists under the stated assumptions. The estimated treatment effects are then defined as

**Feedback**:
The text defines Π_Q as the L² projection onto the space of restricted quantile functions but does not specify its functional form. For a function \(f \in L^2([a,b])\), the projection onto the closed convex cone of non-decreasing functions is the solution to \(\Pi_Q(f) = \arg\min_{g \in Q} \int_a^b (f(q) - g(q))^2 dq\). This is an isotonic regression problem, typically solved by the pool-adjacent-violators algorithm (PAVA). Without this clarification, the estimator's definition is incomplete.

---

### 14. Lemma 2 statement lacks quantifier over x

**Status**: [Pending]

**Quote**:
> Lemma 2 (Improvement in Estimation Property) . Suppose that ˆ Q is an estimator of some true quantile curve Q 0 . Then the projected curve ˆ Q ∗ = Π Q ( ˆ Q ) is closer to the true curve in the sense that, for each x ∈ R ,

**Feedback**:
Lemma 2 is stated incompletely. The quote ends with 'for each x ∈ R ,' but the inequality that should follow is not provided. Based on the reference to Lin et al. (2019) and the description of a 'no-regret' property, the intended inequality is likely an integral norm inequality, such as \(\int_a^b |\hat{Q}^*(q) - Q_0(q)|^p dq \le \int_a^b |\hat{Q}(q) - Q_0(q)|^p dq\) for some \(p \ge 1\). However, the statement as given is missing the crucial mathematical claim, making it impossible to verify.

---

### 15. Ambiguity in 'closer to the true curve' for each x

**Status**: [Pending]

**Quote**:
> Then the projected curve ˆ Q ∗ = Π Q ( ˆ Q ) is closer to the true curve in the sense that, for each x ∈ R ,

**Feedback**:
The phrase 'for each x ∈ R' suggests a pointwise improvement, i.e., \(|\hat{Q}^*(x) - Q_0(x)| \le |\hat{Q}(x) - Q_0(x)|\) for every x. However, the classical isotonic regression result guarantees improvement in an integral norm (e.g., L²), not pointwise dominance. Pointwise improvement is not generally true. For example, consider \(Q_0(q)=q\) and \(\hat{Q}(q)=1.5 - q\) on [0,1]. The isotonic projection \(\hat{Q}^*\) will be constant, and at q=0, the pointwise error may increase. The lemma should clarify that the improvement is in a global norm sense.

---

### 16. Bandwidth condition nh^2 → ∞ is insufficient for consistency

**Status**: [Pending]

**Quote**:
> ) . The bandwidths satisfy h 1 ( q ) = c 1 ( q ) h and h 2 ( q ) = c 2 ( q ) h for c 1 ( q ) : [ a, b ] → C ⊂ R a bounded Lipschitz function and c 2 ( q ) = ¯ c 2 &gt; 0 . The baseline bandwidth h = h n satisfies h → 0 , nh 2 →∞ , nh 2 p +3 → 0 .
> 
> - L1 (Sa

**Feedback**:
The condition \(nh^2 \to \infty\) is insufficient for consistency of local polynomial regression of order p. For a p-th order local polynomial, the standard condition for consistency is \(nh^{2p+1} \to \infty\) (Fan and Gijbels, 1996). The condition \(nh^2 \to \infty\) would only suffice for p=0 (local constant) or p=1 (local linear). For p>1, a stronger condition is needed; e.g., for p=2 (local quadratic), \(nh^5 \to \infty\) is required. The condition \(nh^{2p+3} \to 0\) is correctly stated for bias control (undersmoothing), but the variance condition should be \(nh^{2p+1} \to \infty\).

---

### 17. Inconsistent notation for bandwidth functions in fuzzy RD

**Status**: [Pending]

**Quote**:
> tiles [ a, b ], a compact subset of (0 , 1), and let $\underline{c} < 0 < \bar{c}$ . Also, define Y c := { Y ( ω ) : ω ∈ Ω x , X ( ω ) ∈ [ c, ¯ c ] } as the set of random cdfs that are realized in a small neighborhood around the cutoff, with Ω x the sample space. Also, let h 1 ( q ) be the bandwidth for the numerator in the fuzzy RD at quantile q , and h 2 ( q ) the same for the denominator.
> 
> K1 (Kernel) . The kernel K is a continuous probability density function, symmetric around zero, and non-negative valued with compact support.
> 
> K2 (Bandwidth) . The bandwidths satisfy h 1 ( q ) = c 1 ( q ) h and h 2 ( q ) = c 2 (

**Feedback**:
There is an inconsistency in the definition of \(c_2(q)\). The text first says \(h_2(q)\) is 'the same for the denominator' (implying it may also depend on q), then in K2 states \(c_2(q) = \bar{c}_2 > 0\) (a constant). This means \(h_2(q) = \bar{c}_2 h\) is constant across q, while \(h_1(q) = c_1(q)h\) varies with q. This asymmetric treatment needs justification: why would the numerator bandwidth be quantile-specific while the denominator bandwidth is constant? In fuzzy RD, the denominator estimates \(E[T|X=x]\), where T is binary. If the smoothness of this function differs from that of the quantile functions, optimal bandwidths could differ, but this should be explicitly discussed.

---

### 18. Definition of residual E_k contains undefined symbols

**Status**: [Pending]

**Quote**:
> Further, define the population residual E k ( y, t, x, q ) := g k ( y, t, q ) -E [ g k ( y, t, q ) | X i = x ] , k = 1 , 2 and let

**Feedback**:
The definition of \(E_k\) uses \(g_k\), which was defined earlier as \(g_1: (Y, T, q) \to Q_Y(q)\) and \(g_2: (Y, T, q) \to T\). However, the notation "( y, t, x, q )" suggests \(E_k\) depends on four arguments, while \(g_k\) only depends on three. The conditional expectation \(E[g_k(y, t, q) | X_i = x]\) is problematic because \(g_k\) is a function of (y, t, q), not of x. Likely, the intended definition is \(E_k(Y_i, T_i, X_i, q) := g_k(Y_i, T_i, q) - E[g_k(Y_i, T_i, q) | X_i]\), where the expectation is over (Y_i, T_i) conditional on X_i. The current notation is confusing and should be clarified.

---

### 19. Missing definition for sigma_kl(q,q'|0±) limit

**Status**: [Pending]

**Quote**:
> with k, l ∈ { 1 , 2 } , q, q ′ ∈ [ a, b ], and σ kl ( q, q ′ | 0 ± ) = lim x → 0 ± σ kl ( q, q ′ | x ).

**Feedback**:
The symbol \(\sigma_{kl}(q,q'|x)\) is used without prior definition. From context, it likely represents the conditional covariance \(\text{Cov}(E_k(Y_i,T_i,X_i,q), E_l(Y_i,T_i,X_i,q') | X_i = x)\). However, this should be explicitly defined before being used in the limit expression. A clear statement such as "Let \(\sigma_{kl}(q,q'|x) = \text{Cov}(E_k(Y_i,T_i,X_i,q), E_l(Y_i,T_i,X_i,q') | X_i = x)\)" would prevent ambiguity and allow verification of the asymptotic covariance formulas.

---

### 20. Incomplete definition of Gamma_±,p integral

**Status**: [Pending]

**Quote**:
> write Γ ± ,p := ∫ R ± K ( u ) r p ( u ) r ′ p ( u ) d u where I remind the reader that r p ( u ) := (1 , u, . . . , u p ).

**Feedback**:
The definition of \(\Gamma_{\pm,p}\) is ambiguous. The integral is over "R_±", which presumably means \(\mathbb{R}_+\) for \(\Gamma_{+,p}\) and \(\mathbb{R}_-\) for \(\Gamma_{-,p}\). The integrand \(K(u) r_p(u) r'_p(u) du\) uses notation \(r'_p(u)\), which is unusual; typically one writes \(r_p(u) r_p(u)^T\), producing a (p+1)×(p+1) matrix. The domain of integration should be specified clearly: e.g., \(\Gamma_{+,p} = \int_{0}^{\infty} K(u) r_p(u) r_p(u)^T du\) and \(\Gamma_{-,p} = \int_{-\infty}^{0} K(u) r_p(u) r_p(u)^T du\), assuming K has compact support.

---

### 21. Weak convergence notation is incorrectly defined

**Status**: [Pending]

**Quote**:
> Also, let X n ; X denote weak convergence for some sequence of random variables X n and a random variable X , while X n p ξ X de- notes conditional weak convergence. The latter is defined as sup h ∈ BL 1 ∣ ∣ E ξ | x [ h ( X n ) -E [ h ( X )]] ∣ ∣ → x 0 where BL 1 the set of bounded Lipschitz functions with supremum norm bounded by 1 and p → x denotes convergence in probability with respect to probability measure P x (van der Vaart and Wellner, 1996, § 1.13).

**Feedback**:
The notation for weak convergence is non-standard ("X n ; X"). More importantly, the definition of conditional weak convergence "X n p ξ X" is problematic. The superscript "p ξ" is not standard. The definition given mixes concepts: "E_ξ|x" is unclear—likely it means expectation with respect to the multiplier ξ conditional on the data. The reference to van der Vaart and Wellner (1996, §1.13) is about conditional convergence in distribution, but the notation and definition should be clarified to align with standard treatments.

---

### 22. Theorem statements are incomplete due to formatting

**Status**: [Pending]

**Quote**:
> Theorem 1 (Convergence: Conditional Means) . Under Assumptions I2, K1, K2, L1-(i), L2, L3,
> 
> <!-- formula-not-decoded -->
> 
> <!-- PAGE BREAK -->
> 
> where G H ± : Ω x → l ∞ ([ a, b ] ×{ 1 , 2 } ) is a zero-mean Gaussian process with covariance function,
> 
> <!-- formula-not-decoded -->
> 
> where,
> 
> <!-- formula-not-decoded -->
> 
> for each q, q ′ ∈ [ a, b ] .

**Feedback**:
The theorem statement is incomplete because the actual result (the asymptotic distribution) is replaced by the placeholder "<!-- formula-not-decoded -->". This prevents verification of the claimed convergence. The theorem should explicitly state the convergence result, e.g., \(\sqrt{nh} (\hat{m}_{\pm,p}(q) - m_{\pm}(q))\) converges weakly to \(G_{H\pm}(q,1)\). Without the explicit formula, one cannot check the scaling, centering, or covariance structure. The subsequent covariance function is also missing its expression.

---
