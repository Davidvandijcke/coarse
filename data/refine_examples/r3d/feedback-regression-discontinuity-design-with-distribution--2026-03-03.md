# Regression Discontinuity Design with Distribution-Valued Outcomes

**Date**: 3/3/2026, 11:23:50 AM
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**The definition and weighting of the estimand**

Definition 1 establishes the local average quantile treatment effect as $\tau^{R3D}(q)=E[Q_{Y^1}(q)-Q_{Y^0}(q)\mid X=0]$, which characterizes an unweighted average over units’ quantile functions (answering the treatment effect on the "average unit"). Section 2.3.1 notes that "one can also easily incorporate weights," but the manuscript does not formalize what specific weighted versions correspond to or what additional assumptions might be required when treatment alters group size or composition. 

The text correctly foregrounds composition issues for means in Section 2.4.2, but largely brackets them for LAQTE. This becomes an active structural consideration in the CPS application in Section 4.2.1, which applies CPS probability weights and constructs within-state distributions. Without a formal mapping from these weights to a specific population causal estimand, the substantive interpretation of the treatment effect—whether it applies to the "effect on the average state" or the "effect on the average family"—remains unsettled. Pinning down this mapping will ensure that readers can transparently interpret the application's results.


**Framing the comparison with Q-RDD**

The manuscript characterizes standard quantile RD as "biased and inconsistent" in this setting (in the Abstract, Section 2.4.1, the simulation discussion in Section 4.1, and Figure 3/Table 2). Specifically, Section 2.4.1 details that the Q-RD sampling framework "could never result in multiple data points having the same value of the (continuous) running variable." 

Readers observing this comparison will likely note that the divergence stems fundamentally from an estimand mismatch rather than a statistical bias relative to a shared target. Applying Q-RD to pooled micro outcomes with a group-level $X$ typically targets the jump in a pooled or mixture marginal distribution, rather than the LAQTE defined as an expectation of unit-level quantiles. The manuscript notes in Section 2.4.2 that pooled quantiles need not correspond to an "average of group-level QTEs." A compact formal statement of what Q-RD actually converges to under the grouped DGP, along with conditions under which it might equal LAQTE, would fortify the manuscript's positioning and prevent the simulation evidence from being read as targeting a straw man.


**The role of the interior-point condition in empirical settings**

Theorem 4 and Corollary 2 rely on the projection $\Pi_{\mathcal Q}$ possessing a Hadamard derivative equal to the identity at $m_\pm$, rendering the projection asymptotically "inactive." Assumption L4 enforces this condition by specifying $\kappa\le \partial_q E[Q_Y(q)\mid X=x]$ on $[a,b]$. 

In empirical distributions relevant to the target applications—such as income distributions featuring top-coding, winsorization, or heaping—the average quantile curve can contain locally flat segments. These are the exact regions where the projection becomes active, potentially altering or invalidating the delta-method linearization that underpins the "same Gaussian limit" and "same multiplier bootstrap bands." Providing diagnostics, boundary sensitivity analyses, or an alternative inference route for cases where L4 is violated would fully secure the uniform inference claims for these common empirical scenarios.


**The sampling structure and the empirical illustration**

The primary asymptotic and bootstrap results in Theorems 1–3 are derived under Assumption L1(i), which requires $\{(Y_i,T_i,X_i)\}_{i=1}^n$ to be i.i.d. across $i$. In contrast, the gubernatorial application in Section 4.2.1 utilizes 356 state-election observations spanning 1984–2010, meaning the same states appear repeatedly in the sample. 

In such a panel structure, serial dependence in both electoral margins and state-level income distributions is the default expectation. The manuscript mentions in Section 4.2.1 that normalizing by the poverty threshold "mak[es] the i.i.d. assumption…more likely to hold." However, this normalization addresses location scale rather than the fundamental serial dependence that influences the $\sqrt{nh}$ Gaussian process approximation and the validity of the multiplier bootstrap for uniform bands and tests. Accommodating clustered or serial dependence explicitly, or providing evidence verifying its absence, is required to align the showcased empirical application with its underlying statistical theory.


**Verifying the rate condition for empirical quantiles**

Extending the framework to the two-layer sampling structure involves the rate condition Q1, requiring $\sqrt{nh}\max_i r_{n_i}\to 0$ so that within-unit quantile estimation noise is asymptotically negligible for Proposition 2 and Corollary 3. In the context of the CPS application (Section 4.2.1), $n$ reflects the number of state-elections near the cutoff, while the within-group sample sizes $n_i$ derive from CPS data utilizing probability weights and explicit winsorization at 0.95. 

Features like weights and top-coding materially define the effective within-state information and can induce flat regions in the upper tail distributions. Although the text describes Q1 as "light," it leaves a gap regarding how an empirical researcher should assess or verify Q1 in practice—including how to calculate effective sample sizes, handle probability weights, or account for non-negligible first-stage quantile uncertainty in the multiplier process. Elaborating on how to verify this condition would substantially improve the framework's practical usability.


**The IMSE bandwidth and tail variance heterogeneity**

The bandwidth selection procedure in Section 2.7 proposes a single IMSE-optimal bandwidth $h_\oplus^*$ derived by integrating the MSE over $[a,b]$. This implies an equal integration weight across all analyzed quantiles. 

Economic variables such as income natively exhibit substantially higher variance and curvature in the upper tails. The manuscript's implementation trims the domain to $[10^{-6},0.95+10^{-6}]$ specifically due to top-coding and winsorization pathologies (Section 4.2.1). In the presence of highly heterogeneous tail variances, a globally integrated bandwidth can oversmooth stable mid-quantiles while undersmoothing volatile higher quantiles. This threatens the accuracy of the uniform confidence bands at the distribution's extremes. Introducing a principled weighting or trimming rule inside the IMSE criterion—linked directly to the regions where uniform inference is required to perform reliably—would alleviate vulnerability to tail pathologies.

**Status**: [Pending]

---

## Detailed Comments (20)

### 1. Flawed deduction of zero covariance in Theorem 1 proof

**Status**: [Pending]

**Quote**:
> - (ii) (c) The covariance

$$
\begin{aligned}
& \sigma_{12}\left(q, q^{\prime} \mid X=x\right)=E\left[\left(Q_{Y}(q)-E\left[Q_{Y}(q) \mid X=x\right]\right)(T-E[T \mid X=x]) \mid X=x\right] \\
& =P(T=1 \mid X=x) E\left[Q_{Y}(q) \mid X=x\right]-P(T=1 \mid X=x) E\left[Q_{Y}(q) \mid X=x\right] \\
& +E[T \mid X=x] E\left[Q_{Y}(q) \mid X=x\right]-E[T \mid X=x] E\left[Q_{Y}(q) \mid X=x\right]=0
\end{aligned}
$$

where the second equality follows from the law of total expectation.

**Feedback**:
The displayed calculation setting $\sigma_{12}(q,q'\mid X=x)=0$ does not follow from the law of total expectation in general: it implicitly treats $E[Q_Y(q)\mid T=1,X=x]$ as equal to $E[Q_Y(q)\mid X=x]$, i.e. a conditional mean-independence restriction. In a sharp RD, $\sigma_{12}$ is indeed trivially zero because $T$ is degenerate conditional on $X=x$ (away from the cutoff), but in a fuzzy RD the cross-covariance need not vanish. It would help to clarify whether this step is intended only for the sharp case, or else replace it with an argument/assumption ensuring $\sigma_{12}(q,q'\mid x)$ satisfies the required smoothness/finite-moment condition for the fuzzy case.

---

### 2. Contradictory fuzzy RD monotonicity assumption

**Status**: [Pending]

**Quote**:
> - Compliers: $C=\left\{\omega: T^{1}(\omega)>T^{0}(\omega)\right\}$.
- Indefinites: $I=\left\{\omega: T^{1}(\omega)=T^{0}(\omega)\right\} \backslash\left\{\omega: T^{1}(\omega)=T^{0}(\omega) \in\{0,1\}\right\}$.

The treatment effects of interest are,
Definition 2 (Fuzzy LAQTE). The local average quantile treatment effects for the fuzzy R3D design are,

$$
\tau^{\mathrm{F} 3 \mathrm{D}}(q):=E\left[Q_{Y^{1}}(q)-Q_{Y^{0}}(q) \mid X=0, C\right] \quad q \in[0,1]
$$

To identify these, I need the following standard additional assumptions,
I3 (Fuzzy RD). $\lim _{x \rightarrow 0^{+}} P(T \mid X=x)>\lim _{x \rightarrow 0^{-}} P(T \mid X=x)$.
I4 (Treatment Continuity). $E[T \mid X=x]$ is continuous in $x$ over $(-\varepsilon, \varepsilon) \backslash\{0\}, \varepsilon>0$.
I5 (Monotonicity). $\lim _{x \rightarrow 0} P\left(T^{1}>T^{0} \mid X=x\right)=1$ and $P($ Indefinites $)=0$.

**Feedback**:
In the fuzzy R3D identification setup, Assumption I5 as stated ($\lim_{x\to 0}P(T^1>T^0\mid X=x)=1$) is not compatible with the binary-treatment framework used elsewhere: $T^1>T^0$ forces $(T^1,T^0)=(1,0)$, so it rules out always-takers/never-takers at the cutoff and effectively collapses the design to sharp (the treatment-probability jump becomes 1). Relatedly, the “Indefinites” set definition is empty when $T^1,T^0\in\{0,1\}$, making the additional condition $P(\text{Indefinites})=0$ vacuous. This matters because the fuzzy identification proof later uses identities (e.g., $E[T^1-T^0\mid X=0]=\Pr(T^1>T^0\mid X=0)$) that rely on the standard binary monotonicity structure.

---

### 3. Missing parameter and contradictions in DGP 2

**Status**: [Pending]

**Quote**:
> DGP 2: Normal-Exponential Mixture with Normal-Exponential means. Set $\mu_{i}=\operatorname{Uniform}(-5,5)+ 2 X_{i}$ and $\lambda_{i}=\operatorname{Uniform}(0.5,1.5)$. Then, generate

$$
Y_{i}=N\left(\mu_{i}+\delta^{+} \Delta, 1\right)+2 \operatorname{Exp}\left(\lambda_{i}+\delta^{+} \Delta_{\lambda}\right) .
$$

In both setups, I let $\Delta$ vary across different simulations to test different treatment effect magnitudes.

**Feedback**:
DGP 2 is underspecified: $\Delta_{\lambda}$ enters $2\operatorname{Exp}(\lambda_i+\delta^+\Delta_\lambda)$ but is never defined or given a value, while the text says only $\Delta$ varies across simulations. This also makes it hard to interpret the “$\Delta=0$” column as a no-effect case: if $\Delta_\lambda\neq 0$ when $\Delta=0$, there is still a treatment effect; if instead $\Delta_\lambda=0$, it is unclear how DGP 2 generates heterogeneous quantile effects. The very low homogeneity-test acceptance reported for DGP 2 at $\Delta=0$ suggests the implemented DGP/test may not match the “no effect / heterogeneous effect” narrative, so the relationship between $\Delta$ and $\Delta_\lambda$ (and the intended null case) needs to be stated and reconciled with Table 2.

---

### 4. Mischaracterization of Q-RDD continuity assumption

**Status**: [Pending]

**Quote**:
> Second, as mentioned, the quantile continuity assumption required for the identification of the estimator in Frandsen et al. (2012) is highly restrictive in the R3D setting, requiring that two units that are both close to the threshold have essentially identical distributions. In the examples in Section 2.2, this would imply that, conditional on having the same value of the running variable, two different restaurants would have the exact same distributions of product prices, two different schools the same distribution of tests, and two different counties the same distribution of child mortality.

**Feedback**:
The discussion of Q-RDD’s identifying continuity assumption seems overstated here. A continuity condition of the type used in scalar-outcome quantile RDDs is a restriction on a population conditional object (e.g., the conditional distribution/quantile function as $x\to 0^\pm$), and is compatible with substantial heterogeneity across units at a given $X=x$. As written, “requiring that two units … have essentially identical distributions” reads like a unit-level equality requirement, which is stronger than what continuity of an average/mixture conditional distribution would imply. It would help to sharpen the comparison so that the substantive distinction is clearly framed as (i) sampling model/level of observation and (ii) the estimand (average of unit quantiles vs. quantiles of a pooled/mixture distribution), rather than as an implication that Q-RDD rules out heterogeneity across units at the cutoff.

---

### 5. Misstatement of Hadamard differentiability definition

**Status**: [Pending]

**Quote**:
> Concretely, there is a remainder map $r(\cdot)$ such that, uniformly on compact subsets of $C([a,b])$,

$$
\Pi_{\mathcal{Q}}\left(m_{ \pm}+\epsilon\right)=m_{ \pm}+\epsilon+r(\epsilon), \quad\|r(\epsilon)\|_{\infty}=o\left(\|\epsilon\|_{\infty}\right) \quad \text { as }\|\epsilon\|_{\infty} \rightarrow 0
$$

**Feedback**:
The remainder expansion invoked here is stronger than Hadamard differentiability tangentially to $C([a,b])$: writing $\|\;r(\epsilon)\;\|_\infty=o(\|\epsilon\|_\infty)$ (uniformly on compact subsets) is essentially a Fréchet/“compact” differentiability-type statement and does not generally follow from Lemma A-7 as stated. For Lemma A-9, it should be enough to apply the definition of Hadamard differentiability (or the functional delta method) along the particular sequence $\epsilon_n=\hat m_{\pm,p}-m_\pm$ with $t_n=(nh)^{-1/2}$ and $h_n=\sqrt{nh}\,\epsilon_n$ (tight in $C([a,b])$), which would yield $\Pi_{\mathcal Q}(m_\pm+\epsilon_n)=(m_\pm+\epsilon_n)+o_p((nh)^{-1/2})$ without requiring a global $o(\|\epsilon\|_\infty)$ remainder bound.

---

### 6. Inconsistent polynomial orders in bandwidth selection

**Status**: [Pending]

**Quote**:
> h_{1, n}^{0}(q)=\left(\frac{1}{2(p+1)} \frac{C_{1,0}(q)^{\prime}}{C_{1,0}(q)^{2}}\right)^{\frac{1}{2 p+3}} n^{-\frac{1}{2 p+3}}

where $C_{1,0}$ and $C_{1,0}^{\prime}$ are the bias and variance expressions derived above with first-stage estimates plugged in,

$$
\begin{aligned}
C_{1,0}(q) & =e_{0}^{\prime}\left[\left(\Gamma_{s}^{+}\right)^{-1} \Lambda_{s, s+1}^{+} \frac{\partial^{s+1} \bar{m}_{+}(q)}{\partial x^{s+1}}-\left(\Gamma_{s}^{-}\right)^{-1} \Lambda_{s, s+1}^{-} \frac{\partial^{s+1} \bar{m}_{-}(q)}{\partial x^{s+1}}\right] /(s+1)! \\
C_{1,0}^{\prime}(q) & =\frac{1}{\hat{f}_{X}(0)} e_{0}^{\prime}\left[\bar{\sigma}_{1,+}^{2}(q)\left(\Gamma_{s}^{+}\right)^{-1} \Psi_{s}^{+}\left(\Gamma_{s}^{+}\right)^{-1}+\bar{\sigma}_{1,-}^{2}(q)\left(\Gamma_{s}^{-}\right)^{-1} \Psi_{s}^{-}\left(\Gamma_{s}^{-}\right)^{-1}\right] e_{0}
\end{aligned}

**Feedback**:
In A-4.2.3, the practical bandwidth-selection steps mix the roles of the polynomial orders $s$ (order for which the MSE/IMSE-optimal bandwidth is derived) and $p$ (higher order used for bias correction / final estimation). In particular, $h_{1,n}^0(q)$ is described as a pilot bandwidth “for fits of order $p$” and its formula uses $p$, but the constants $C_{1,0}(q)$ and $C_{1,0}'(q)$ are then defined entirely using $s$-order objects (e.g. $\Gamma_s^\pm,\Lambda_{s,s+1}^\pm,\Psi_s^\pm$ and an $(s+1)$-st derivative). Relatedly, Step 2 says to run order-$s$ local polynomial regressions with the pilot bandwidths, even though the leading bias term used later depends on the $(s+1)$-st derivative. As written, it is unclear which step is supposed to supply the $(s+1)$-st derivative needed for the final bandwidth calculation, and the algorithm is difficult to implement without additional interpretation.

---

### 7. Insufficient rate condition for empirical quantiles

**Status**: [Pending]

**Quote**:
> The last equality follows from Assumption Q1.

**Feedback**:
The step that attributes the $o_p(1)$ remainder to Assumption Q1 appears to require control of $\max_{1\le i\le n}\sup_{q\in[a,b]}|\widehat Q_{Y_i}(q)-Q_{Y_i}(q)|$ (since the empirical-quantile error enters through a weighted sum over $i$ and a sufficient bound uses the maximum). As stated, Q1 gives $\sup_{q}|\widehat Q_{Y_i}-Q_{Y_i}|=O_p(r_{n_i})$ “for all $i$,” but it is unclear whether this $O_p(\cdot)$ is meant uniformly over $i$ (or whether $r_{n_i}$ is chosen to already incorporate the union bound/log factors needed to control the maximum). Clarifying Q1 to explicitly bound the maximum over $i$ (or adding conditions ensuring such a bound) would make the proof of Proposition 2 fully rigorous.

---

### 8. Sign error and invalid notation in Proposition A-3 proof

**Status**: [Pending]

**Quote**:
> \begin{aligned}
& \frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h) d_{L^{2}}\left(Q_{Y_{i}}, \hat{m}_{+, p}\right)^{2}+d_{L^{2}}\left(Q_{\omega}, \hat{m}_{+, p}\right)^{2} \\
& =\left\langle\frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h), Q_{Y_{i}}^{2}\right\rangle_{L^{2}}-2\left\langle\hat{m}_{+, p}, \frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h) Q_{Y_{i}}\right\rangle_{L^{2}}+\frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h)\left\langle\hat{m}_{+, p}, \hat{m}_{+, p}\right\rangle_{L^{2}} \\
& +\left\langle Q_{\omega}, Q_{\omega}\right\rangle_{L^{2}}-2\left\langle\frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h) Q_{Y_{i}}, Q_{\omega}\right\rangle_{L^{2}}+\left\langle\hat{m}_{+, p}, \hat{m}_{+, p}\right\rangle_{L^{2}} \\
& =\left\langle\frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h), Q_{Y_{i}}^{2}\right\rangle_{L^{2}}-\left\langle Q_{\omega}, Q_{\omega}\right\rangle_{L^{2}}-2\left\langle\frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h) Q_{Y_{i}}, Q_{\omega}\right\rangle_{L^{2}} \\
& =\frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h) d_{L^{2}}\left(Q_{Y_{i}}, Q_{\omega}\right)^{2}
\end{aligned}

**Feedback**:
The algebra in this display appears to contain (at least) two local issues that make the chain of equalities incorrect as written: (i) $\langle Q_{\omega}, Q_{\omega}\rangle_{L^2}$ enters with a positive sign in the expansion but then switches to a negative sign in the next line, and (ii) the inner-product notation $\left\langle\frac{1}{n} \sum_{i=1}^{n} s_{+, i n}^{(p)}(h), Q_{Y_{i}}^{2}\right\rangle_{L^{2}}$ is not well-formed (the summation over $i$ should remain outside the $L^2$ inner product, e.g. as a weighted sum of $\|Q_{Y_i}\|_{L^2}^2$ terms). These look like notation/sign slips in what is essentially a standard weighted-variance decomposition argument, but it would help to correct the display so each equality is literally valid.

---

### 9. Intro: Projection operator smoothness

**Status**: [Pending]

**Quote**:
> Leveraging this link, I extend the results of Chiang et al. (2019) to derive uniform, debiased confidence bands for the pointwise estimator, and then extend these results to distribution space by exploiting the smoothness of the projection operator.

**Feedback**:
The phrase “exploiting the smoothness of the projection operator” is potentially misleading in this setting: the $L^2$ projection onto the cone of nondecreasing functions is Lipschitz but not globally differentiable, with nonregular behavior at boundary points. Later results (e.g., Theorem 4 / Lemma A-7) rely on Assumption L4 (strict monotonicity of the limiting average quantile function) so that the projection is locally inactive and has Hadamard derivative equal to the identity at the true $m_\pm$. It would help to align the introductory description with this local differentiability/“projection-as-identity at the truth” mechanism, rather than suggesting global smoothness.

---

### 10. Category error in LAQTE closed-form solution

**Status**: [Pending]

**Quote**:
> For the first DGP, the true treatment effects have the closed-form solution $N(\Delta, 2)$, implying constant treatment effects. The heterogeneous treatment effects in the second DGP are estimated by averaging across a large number of simulated quantile functions.

**Feedback**:
The Monte Carlo description seems to conflate the paper’s estimand (the deterministic LAQTE function $\tau^{\mathrm{R}3\mathrm{D}}(q)$) with a distribution of unit-level effects. Under DGP 1, the LAQTE should be constant in $q$ (typically $\tau^{\mathrm{R}3\mathrm{D}}(q)\equiv\Delta$), whereas $N(\Delta,2)$ would more naturally describe the cross-sectional distribution of a unit-level location shift (e.g., $\mu_i^1-\mu_i^0$ under an independent-draw representation). Clarifying which object is meant here would avoid confusion about what the simulations are benchmarking.

---

### 11. Typo in Lemma 1 referencing Assumption IQ

**Status**: [Pending]

**Quote**:
> Lemma 1 (Identification). Under Assumptions I1 and IQ, for a given $q \in[0,1]$, the unobserved $\tau^{\mathrm{R} 3 \mathrm{D}}(q)$ is identified from the joint distribution of the observed $(X, Y)$ as,

**Feedback**:
Lemma 1 cites “Assumptions I1 and IQ,” but no Assumption IQ is defined. Given the surrounding text (which introduces I1 and I2 as the two identification assumptions) and the appendix proof referencing I1 and I2, this appears to be a typo/mislabeled assumption in the lemma statement that should be corrected for clarity.

---

### 12. Mathematical error in Fubini-Tonelli equation

**Status**: [Pending]

**Quote**:
> $$
E\left[Q_{Y}(q)\right]=\int_{[0,1]} \int_{\mathcal{Y}} Q_{y}(q) \mathrm{d} F_{Y}(y) \mathrm{d} q=\int_{\mathcal{Y}} \int_{[0,1]} Q_{y}(q) \mathrm{d} q \mathrm{~d} F_{Y}(y)=\int_{\mathcal{Y}} E[y] \mathrm{d} F_{Y}(y)
$$

**Feedback**:
The displayed Fubini–Tonelli calculation appears to equate $E[Q_Y(q)]$ (which elsewhere is a function of $q$) to an expression that integrates over $q\in[0,1]$ and therefore yields a scalar. The surrounding discussion suggests the intended statement is about averaging the quantile curve over $q$ to recover the mean (e.g., $\int_0^1 E[Q_Y(q)]\,dq$), after which swapping integrals delivers $\int_{\mathcal Y}E[y]\,dF_Y(y)$. As written, the left-hand side (and thus the first equality) is not consistent with the rest of the paper’s notation distinguishing functional vs. scalar objects.

---

### 13. Circular notation in bandwidth formulas

**Status**: [Pending]

**Quote**:
> $$
h^{*}(q)=\left(\frac{1}{2(s+1)} \frac{\operatorname{Var}\left(\hat{\tau}_{s}^{\mathrm{R} 3 \mathrm{D}}\right)(q)}{\operatorname{Bias}\left(\hat{\tau}_{s}^{\mathrm{R} 3 \mathrm{D}}(q)\right)^{2}}\right)^{1 /(2 s+3)} n^{-1 /(2 s+3)},
$$

**Feedback**:
The optimal bandwidth display in Section 2.7 is potentially confusing because $\operatorname{Var}(\hat{\tau}_s^{\mathrm{R}3\mathrm{D}})(q)$ and $\operatorname{Bias}(\hat{\tau}_s^{\mathrm{R}3\mathrm{D}}(q))$ could be read as full finite-sample variance/bias terms (which depend on $h$), making the expression look implicit. Given the appendix derivations, it seems these are meant as leading asymptotic variance/bias components (constants) used in the closed-form minimizer; it would help to make that explicit in the main text. Also, in the displayed IMSE-optimal Fréchet bandwidth, the numerator is written with $\mathrm{d}q$ inside $\operatorname{Var}(\cdot)$, which appears to be a typographical error (the integral should be over $\operatorname{Var}(\hat{\tau}_{\oplus,s}^{\mathrm{R}3\mathrm{D}}(q))$).

---

### 14. Misuse of notation in conditional expectation integral

**Status**: [Pending]

**Quote**:
> Observe that the expectation is taken with respect to the conditional distribution of distributions, $F_{Y^{t} \mid X=0}$,

$$
m_{t}(q)=E\left[Q_{Y^{t}}(q) \mid X=0\right]=\int_{\mathcal{Y}} Q_{y}(q) \mathrm{d} F_{Y^{t} \mid X=0}(0, y), \quad t=0,1
$$

**Feedback**:
The differential notation $\mathrm{d}F_{Y^{t}\mid X=0}(0,y)$ is confusing in an integral over $\mathcal{Y}$. Since $F_{Y^{t}\mid X=0}$ is (or can be taken as) a probability measure on the Borel sets of $\mathcal{Y}$, it would be clearer to write the integral with respect to $\mathrm{d}F_{Y^{t}\mid X=0}(y)$ (or $F_{Y^{t}\mid X=0}(\mathrm{d}y)$). As written, the extra “$0$” inside the differential suggests a joint CDF-style object in $(x,y)$, which is not the relevant representation here.

---

### 15. Misleading interpretation of zero-probability ties

**Status**: [Pending]

**Quote**:
> Proposition 1 (Smooth average vs. discontinuous observed quantile functions). Fix $q \in (0,1)$. Suppose

$$
Q_{Y}(q)=\mu(X, q)+\varepsilon(q) \quad \text { a.s. }
$$

where $\mu(\cdot, q)$ is continuous in $x$ near 0 , and $\varepsilon(q)$ is independent of $X$ with a continuous density and $E[\varepsilon(q)]$ finite (w.l.o.g. take $E[\varepsilon(q)]=0$, else absorb it into $\mu$ ). Let $\left\{\left(X_{i}, Y_{i}\right)\right\}_{i=1}^{n}$ be i.i.d., and write $\varepsilon_{i}(q)$ for the copy attached to unit $i$.
(i) Smooth average quantiles. The conditional average quantile

$$
E\left[Q_{Y}(q) \mid X=x\right]=\mu(x, q)+E[\varepsilon(q)]
$$

is continuous in $x$.
(ii) Observed discontinuities for nearby units. For any $\delta>0, q \in[0,1]$,

$$
P\left(\exists i \neq j:\left|X_{i}-X_{j}\right|<\delta \text { and } Q_{Y_{i}}(q)=Q_{Y_{j}}(q) \mid X_{1}, \ldots, X_{n}\right)=0 \quad \text { a.s. }
$$

**Feedback**:
Proposition 1(ii) is a correct “no ties” result under a continuous density for $\varepsilon(q)$, but calling it an “observed discontinuity” (and using it to support statements like “observed distributions will almost surely not vary smoothly”) may be misleading. The fact that nearby units almost surely have different realized quantiles is generic noise/heterogeneity and does not, by itself, establish a discontinuity in any functional sense or a violation of an RD continuity condition (which is usually about the relevant conditional population object). It would help to clarify that the intended contrast is between smoothness of the conditional average quantile function in $x$ versus idiosyncratic cross-unit randomness in realized quantile curves, rather than discontinuity per se.

---

### 16. Clarify limits of standard RD in Conclusion

**Status**: [Pending]

**Quote**:
> Standard RD methods do not apply to such settings since they do not account for the two-level randomness involved in these settings, which introduces sampling at the level of distributions.

**Feedback**:
The conclusion sentence quoted (“Standard RD methods do not apply…”) seems broader than what the paper establishes and may be read as contradicting Section 2.4.2, which notes that standard RDD approaches remain applicable for ATE/mean effects in two-level settings (e.g., via aggregation to the group level or micro-level estimation with clustered inference). It would help to qualify that the main limitation is for distribution-valued/distributional estimands (e.g., quantile/distributional effects) under two-level randomness—where standard scalar-outcome RD/quantile-RD does not deliver the object of interest and can give misleading inference—rather than an inability to use RDD at all in grouped data.

---

### 17. Incorrect bandwidth in first-stage estimator

**Status**: [Pending]

**Quote**:
> \tilde{E}\left[Q_{Y}(q) \mid X=x\right]:=r_{t}\left(x / h_{1}(q)\right)^{\prime} \hat{\boldsymbol{\alpha}}_{+, t} \delta_{x}^{+}+r_{t}\left(x / h_{2}(q)\right)^{\prime} \hat{\boldsymbol{\alpha}}_{-, t} \delta_{x}^{-}

and

$$
\tilde{E}[T \mid X=x]:=r_{t}\left(x / h_{2}(q)\right)^{\prime} \hat{\boldsymbol{\alpha}}_{+, T, t} \delta_{x}^{+}+r_{t}\left(x / h_{2}(q)\right)^{\prime} \hat{\boldsymbol{\alpha}}_{-, T, t} \delta_{x}^{-}
$$

**Feedback**:
The definition of $\tilde{E}\left[Q_{Y}(q)\mid X=x\right]$ uses $h_{1}(q)$ on the $\delta_x^+$ branch but $h_{2}(q)$ on the $\delta_x^-$ branch, even though $\hat{\mathcal E}_1$ is truncated using $1(|x/h_1(q)|\le 1)$ and $h_2(q)$ is used consistently for the separate treatment regression $\tilde E[T\mid X=x]$. This asymmetry looks inadvertent and could lead to incorrect implementation of the first-stage residuals if followed literally.

---

### 18. Incorrect limit variable in Lemma 3 proof

**Status**: [Pending]

**Quote**:
> \begin{aligned}
& \lim _{x \rightarrow 0^{+}} E[T \mid X=0]-\lim _{x \rightarrow 0^{-}} E[T \mid X=0] \\
& \quad=E\left[T^{1} \mid X=0\right]-E\left[T^{0} \mid X=0\right] \\
& \quad=E\left[T^{1}-T^{0} \mid X=0\right] \\
& \quad=\operatorname{Pr}\left(T^{1}>T^{0} \mid X=0\right)=\operatorname{Pr}(\mathrm{C} \mid X=0)
\end{aligned}

**Feedback**:
At first the opening line of the Lemma 3 proof is confusing because it writes $\lim_{x\to 0^\pm}E[T\mid X=0]$, which is constant in $x$ and would make the jump equal to zero. The intended expression appears to be the standard fuzzy-RD discontinuity $\lim_{x\to 0^+}E[T\mid X=x]-\lim_{x\to 0^-}E[T\mid X=x]$ (consistent with the lemma statement and the rest of the proof), so this looks like a typo worth fixing.

---

### 19. Intro: Phrasing of continuity condition

**Status**: [Pending]

**Quote**:
> Identification follows from an intuitive condition: the conditional mean of the quantile functions must be continuous in the running variable, but not the quantile functions themselves.

**Feedback**:
(2) At first the phrasing “must be continuous …, but not the quantile functions themselves” reads like it rules out continuity of the realized/unit-level quantile functions (as if discontinuity were required). However, later Assumption I1 and the surrounding discussion make clear the intended condition is that continuity is imposed on $E[Q_Y(\cdot)\mid X=x]$, while the realized $Q_{Y_i}(\cdot)$ need not be continuous/smooth in $x$. It may help to tweak the introductory wording to avoid that momentary ambiguity about the identification condition.

---

### 20. Use of "positive definite" for a scalar variance

**Status**: [Pending]

**Quote**:
> Finally, denote the marginal distributions of $X$ and $Y$ as $F_{X}, F_{Y}$, with $f_{X}:=\frac{\partial F_{X}(x)}{\partial x}$ the pdf of $X$ which will be well-defined near the cutoff $c$ under the stated assumptions. I equip $\mathcal{Y}$ with the Borel $\sigma$-algebra induced by the $W_{2}$ (2-Wasserstein) metric. Let $F_{Y \mid X=x}$ denote the conditional distribution of $Y$ given $X=x$, which exists because ( $\mathcal{Y}, W_{2}$ ) is Polish (Villani et al., 2008) and hence the disintegration theorem applies (Chang and Pollard, 1997). In addition, let $\mu=E[X]$ and $\Sigma=\operatorname{var}(X)$ with $\Sigma$ positive definite.

**Feedback**:
At first, “$\Sigma=\operatorname{var}(X)$ with $\Sigma$ positive definite” made me wonder whether $X$ was intended to be vector-valued, since $X$ is defined as scalar ($X\in\mathbb{R}$) and “positive definite” is usually used for covariance matrices. It’s technically fine (a $1\times 1$ covariance is positive definite iff $\operatorname{var}(X)>0$), but it would be slightly clearer to state the non-degeneracy condition in scalar terms.

---
