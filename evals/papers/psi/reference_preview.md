# Post-Selection Inference via Algorithmic Stability

**Date**: 11/20/2026, 6:03:29 PM
**Domain**: Mathematics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions from a careful reading of the paper.

**Shared variance estimation across selection and inference**

A central technical question arises in the unknown-variance analysis of Algorithms 2 and 3. In Appendices A.10 and A.12, the proofs establish the high-probability score bounds by averaging over the independent scale estimate $\hat{\sigma}$, yet they compare selection on $y$ against selection on the oracle mean $\mu$ while holding $\hat{\sigma}$ fixed. Because the resulting oracle selection generally depends on $\hat{\sigma}$, conditioning on the oracle model does not preserve the fixed-model $t$-distribution calibration invoked in Corollary 2.

Theorem 2 itself is unaffected by this issue, so the gap is specific to the unknown-variance pipeline. Closing it would seem to require either a coverage argument that explicitly tracks the dependence introduced by reusing $\hat{\sigma}$ across selection and inference, or two separate independent variance estimates for the two stages. A related point concerns the iteration count $k = \lceil n \|X\|_{\infty}^2 C_1 \eta / (\hat{\sigma} \|X\|_{2,\infty}) \rceil$ recommended in Proposition 3: because $k$ depends on $\hat{\sigma}$, the coverage argument would also need to account for this random stopping time rather than invoking the fixed-step certificate of Proposition 2 unchanged.

**Noise calibration in the vignettes and Orlicz-norm extension**

Two separate calibration details warrant attention in the motivating examples of Section 2 and the non-Gaussian extension in Appendix C. First, Claims 1 and 3 allow a general noise level $\sigma$, but their stated Laplace noise scales omit $\sigma$, and the proofs in Appendices A.2 and A.3 analyze unit-scale score deviations. In Claim 1 under equal means, increasing $\sigma$ while keeping the stated perturbation fixed pushes the randomized selection toward the unrandomized maximum, for which the claimed interval can undercover. Either explicit standardization or $\sigma$-scaled Laplace perturbations would align the statements with their proofs.

Second, Appendix C has a distinct calibration gap in Algorithms 6 and 7. The Orlicz-norm bound used there controls each individual projection at level $\delta$, rather than controlling the maximum across all $d$ coordinates simultaneously at level $\delta$. Extending the score-concentration step to all $d$ features calls for a simultaneous bound, such as calibrating the noise scale with $\psi^{-1}(d/\delta)$.

**Conditioning event in the publication-bias example**

In Section 7, the interpretation of Claim 5 turns closely on the role of the high-probability event $E$, which Appendix A.9 defines by the exact same deviation from $\mu$ that determines whether the confidence interval covers. Whenever $\alpha(1-\nu)e^{-\eta} \leq \nu$, the resulting interval automatically contains $\mu$ throughout $E$. In particular, at the parameter values used in Figure 3 ($\nu = 0.05$ and $\alpha \leq 0.05$), even the unadjusted interval has zero miscoverage on $E$.

Moreover, a high marginal probability for $E$ does not ensure that $E$ has high probability conditional on reporting—especially when reporting is rare, which is the primary regime of interest in the file-drawer problem. It would clarify the scope of Section 7 to distinguish this truncated guarantee explicitly from coverage conditional on reporting alone, and to spell out what the $\nu / \mathbb{P}\{\mathrm{report}\}$ bound on the omitted probability permits in the publication-bias setting.

**Error-budget accounting and coverage verification in Section 9**

Readers trying to reconcile the theoretical error budget with the simulations in Section 9 and Appendix B will encounter an ambiguity in how $\delta$ is parameterized. Appendix B states that Algorithms 2 and 3 are run with $\delta = 0.5$, yet even the basic certificates in Propositions 2 and 4 spend $\delta$ on the stability failure event alone, which already exceeds Section 9's total miscoverage target of $\alpha = 0.1$. If $0.5$ instead represents a fraction of $\alpha$ (mirroring the convention in the vignettes of Section 2), stating the exact input passed to the algorithms and tracing the per-step noise, composition rule, and remaining error budget through to the plotted quantiles would remove the ambiguity; otherwise, the experimental comparisons would need recalibration.

In addition, the empirical section evaluates selection quality via LASSO FDR and marginal screening score loss, without reporting simultaneous miscoverage for the selected-model projection coefficients $\beta_{\hat{M}}$. Defining the ground truth used for LASSO FDR and reporting empirical simultaneous coverage alongside the selection metrics would directly verify the coverage event of Corollary 2, which neither selection metric tests.

**Benchmarking the width–utility tradeoff**

The empirical comparison against data splitting in Section 9 also raises structural questions about how the width–utility tradeoff is assessed. Section 9 treats data-splitting intervals as matched in width to stability intervals via the splitting fraction $f(\eta)$ from Section 5.1, yet that calculation equates only a scalar inflation factor and does not account for realized OLS standard errors or the rank of the held-out design matrix. For $n = 50$ and $k = 20$, even the more generous approximation to the prescribed $f(k\eta)$ leaves roughly six rows for inference at $\eta = 1$, which is too few to fit the selected 20-variable model; and even in regimes where the fit is feasible, the projection target defined on the held-out design can differ from the full-design target.

Finally, the empirical evaluation omits a natural nonrandomized benchmark that is already established in the paper. At $d = 200$ and $k = 20$, Proposition 1 yields a smaller correction than basic composition at the upper end of the $\eta$ sweep for a matched error budget, without perturbing selection at all. Comparing realized interval widths and selection utility in settings where splitting targets the same estimand, and including the Proposition 1 benchmark, would clarify where randomization buys a genuine advantage.

**Status**: [Pending]

---

## Detailed Comments (6)

### 1. Appendix A.10: the good set depends on the variance estimate

**Importance**: Critical
**Category**: Substance
**Fix effort**: Needs new work
**Status**: [Pending]

**Quote**:
> Since $\frac{2}{n \hat{\sigma}} \phi^{\top} X^{\top}(y-\mu)$ follows a rescaled $t$-distribution with $r$ degrees of freedom and there are $d$ terms in the sum on the right-hand side, for $s=s^{*}:=\frac{2 t_{r, 1-\delta /(2 d)} C_{1}\|X\|_{2, \infty}}{n}$, the probability above is at most $\delta$. Denote $Y_{\delta}=\left\{\omega: \max _{\phi \in S_{C_{1}}}\left|\frac{2}{n \hat{\sigma}} \phi^{\top} X^{\top}(\omega-\mu)\right| \leq s^{*}\right\}$; we have thus shown $\mathbb{P}\left\{y \in Y_{\delta}\right\} \geq 1-\delta$.

**Feedback**:
The Student-$t$ calculation in Appendix A.10 bounds the failure probability jointly over $y$ and $\hat\sigma$, whereas the selection-law comparison fixes a common realized $\hat\sigma$. This does not establish the high-probability set of responses required by Definition 2 for the algorithm that uses the random variance estimate.

---

### 2. Appendix A.10: advanced composition needs both directions

**Importance**: Minor
**Category**: Substance
**Fix effort**: Quick fix
**Status**: [Pending]

**Quote**:
> and this is true for all $\phi^{*} \in S_{C_{1}}$. Therefore, for all $y \in Y_{\delta}, \phi_{t} \approx_{\eta, 0} \phi_{t}^{\mu}$. By post-processing, this also implies $g_{t}(\theta, y) \approx_{\eta, 0} g_{t}(\theta, \mu)$, for all $\theta$.

By Lemma 3. we finally conclude that, for all $y \in Y_{\delta}$, the output of the stable LASSO algorithm when applied to $y$ is $\left(\frac{1}{2} k \eta^{2}+\sqrt{2 k \log (1 / \delta)} \eta, \delta\right)$-indistinguishable from the output implied by the oracle input $\mu$, for all $\delta \in(0,1)$, or alternatively it is $(k \eta, 0)$-indistinguishable.

**Feedback**:
The one-sided comparison proved in Appendix A.10 suffices for simple composition, but not for the advanced rate in Lemma 3(b), whose stated premise is also one-sided. At a common fixed scale, the absolute score bound gives the missing reverse comparison by the same Laplace argument.

---

### 3. Appendix A.10: the gradient reverses the vertex scores

**Importance**: Minor
**Category**: Substance
**Fix effort**: Quick fix
**Status**: [Pending]

**Quote**:
> For the sake of readability, we denote the squared loss, rescaled by $\hat{\sigma}$, by $L(\theta ; X, y):=\frac{1}{n \hat{\sigma}}\|y-X \theta\|_{2}^{2}$; hence, $\nabla L(\theta ; X, y)=\frac{2}{n \hat{\sigma}} X^{\top}(y-X \theta)$. Also, we denote by $S_{C_{1}}:=C_{1} \cdot\left\{ \pm e_{i}\right\}_{i=1}^{d}$ the set of $2 d$ extreme points of the $\ell_{1}$-ball in $\mathbb{R}^{d}$, scaled by the LASSO constraint $C_{1}$.

**Feedback**:
The displayed gradient in Appendix A.10 has the opposite sign from both the derivative of the squared loss and the deterministic scores minimized in Algorithm 5. The sign error leaves the absolute score-deviation bound unchanged, but the resulting noise threshold does not characterize selection of the stated vertex.

---

### 4. The LASSO utility bound drops parameter restrictions

**Importance**: Minor
**Category**: Substance
**Fix effort**: Needs rework
**Status**: [Pending]

**Quote**:
> Note that the above inequality is true for all $\gamma>0$. After optimizing over $\gamma$, the right-hand side reduces to

$$
\frac{8 C_{1}\|X\|_{2, \infty}}{n \eta}+\frac{16 t_{r, 1-\delta /(2 d)} C_{1}\|X\|_{2, \infty}\left(1+\log \left(k d L_{1} n \eta /\left(4 t_{r, 1-\delta /(2 d)}\|X\|_{2, \infty}\right)\right)\right)}{n \eta} .
$$

Using $k \leq \frac{2 n\|X\|_{\infty}^{2} C_{1} \eta}{\hat{\sigma}\|X\|_{2, \infty}}$ and the value of $L_{1}$, we finally get

**Feedback**:
Appendix A.11 optimizes over all $\gamma>0$, although the expectation argument requires $\zeta=\gamma/(2C_1L_1)$ to be a valid probability tolerance. For sufficiently large admissible values of $\hat{\sigma}$, the resulting expression is negative despite bounding a nonnegative loss gap. In the same regime, the argument $x$ of the ceiling defining $k$ can fall below $1/2$, so $k=\lceil x\rceil\leq 2x$ also fails.

---

### 5. Lemma 5 needs a step-size condition

**Importance**: Minor
**Category**: Substance
**Fix effort**: Quick fix
**Status**: [Pending]

**Quote**:
> Lemma 5 ([27]). Fix $s>0$ and $\theta_{1} \in \mathcal{D} \subseteq \mathbb{R}^{d}$. Let $\left(\phi_{1}, \ldots, \phi_{k}\right)$ be a sequence of vectors from $\mathcal{D}$ and let $\theta_{t+1}=\left(1-\Delta_{t}\right) \theta_{t}+\Delta_{t} \phi_{t}$, for arbitrary $\Delta_{t} \in[0,1]$. Define the curvature constant of $L$ as

**Feedback**:
Lemma 5’s $1/(k+2)$ bound does not hold for arbitrary step sizes in $[0,1]$. If every step size is zero, even an exact linear oracle leaves the iterate at its starting point, which need not be optimal. Algorithm 2 uses a schedule that supports the bound, but the lemma as stated does not require it.

---

### 6. The LASSO curvature bound loses a factor of two

**Importance**: Minor
**Category**: Substance
**Fix effort**: Quick fix
**Status**: [Pending]

**Quote**:
> By the curvature characterization for quadratics due to Clarkson [14], we can bound the curvature constant as

$$
C_{L} \leq \frac{1}{n \hat{\sigma}} \max _{\theta, \theta^{\prime}:\|\theta\|_{1} \leq C_{1},\left\|\theta^{\prime}\right\|_{1} \leq C_{1}}\left\|X\left(\theta-\theta^{\prime}\right)\right\|_{2}^{2} \leq \frac{1}{n \hat{\sigma}} \max _{\varphi:\|\varphi\|_{1} \leq 2 C_{1}}\|X \varphi\|_{2}^{2} \leq \frac{4}{\hat{\sigma}}\|X\|_{\infty}^{2} C_{1}^{2} .
$$

**Feedback**:
The first upper bound in Appendix A.11 is half the exact curvature under the displayed definitions of $L$ and $C_L$. The missing factor of two affects the explicit optimization term obtained by substitution, but not its rate.

---
