# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/16/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper studies how a planner should optimally alter agents' standalone incentives in a network game to maximize aggregate welfare. Using a linear-quadratic setup it diagonalizes the planner's problem into principal components (via eigen- or singular-value decompositions) and derives closed-form prescriptions and asymptotics: for small budgets the planner tweaks many components proportionally, while for large budgets the optimal intervention concentrates on an extremal principal component determined by the interaction structure. The main analytical device is a spectral decomposition of the game matrix and a scalar shadow price that yields simple ratios for componentwise targeting.

Below are the most important issues identified by the review panel.

**Scope and limits of Property A and the linear–quadratic structure**

It would be helpful to make explicit the exact model primitives under which the principal-component prescriptions hold. Many of the paper's central formulas and the neat intuition that "complements => top PC, substitutes => bottom PC" rely on Property A (welfare proportional to sum of squared actions) and the linear–quadratic best-response structure; when either fails (non-quadratic welfare, nonlinear best responses, or richer cross-terms) the amplification weights and optimal directions can change qualitatively. Readers might note that the Appendix contains relevant relaxations and counterexamples, but the main text should (a) state up front the precise class of welfare and response functions for which Theorem 1 and its corollaries apply, (b) add a local-robustness result showing when linear–quadratic conclusions are valid approximately (first-order Taylor expansion conditions), and (c) include a short worked counterexample (e.g. a 3–4 node model) in the main paper illustrating how failure of Property A reverses or alters the PC ordering.

**Strong cost assumptions drive closed-form structure and large-budget simplicity**

Readers might note that the quadratic, separable intervention cost is not innocuous: it is central to the Lagrangian first-order conditions and the single-scalar shadow-price characterization that produce the simple ratios and the large‑budget concentration on one component. Alternative cost primitives (linear, L1, non‑separable, or heterogeneous per-agent marginal costs) can produce corner solutions, sparsity, or allocations spread over multiple components. It would strengthen the paper to (a) state up front that Theorem 1 and Propositions 1–2 assume quadratic separability, (b) provide a theorem or clear corollary identifying the broader class of cost functions (e.g., isotropic/homogeneously scalable or rotationally invariant K) under which the scalar-µ structure and asymptotics survive, and (c) present at least one robustness result or short counterexample (e.g. L1 costs or heterogeneous diagonal costs) showing how the optimal target changes and when sparsity or multi-component solutions arise.

**Non‑symmetric networks, SVD formulation, and eigenvalue multiplicity**

It would be helpful to treat the non‑symmetric case in the main text through a parallel SVD formulation rather than relegating it to the appendix, and to handle eigenspace multiplicity explicitly. For directed or nonnormal G the natural decomposition uses singular values and left/right singular vectors of M=I−βG, the amplification factors become 1/s_l^2 (instead of functions of eigenvalues of G), and left versus right singular vectors have distinct economic interpretations; moreover, repeated eigenvalues/eigenspaces make a single 'leading eigenvector' prescription ambiguous. Suggested fixes: (a) promote the appendix SVD results into a main-text statement of Theorem 1 in SVD language (α_l = 1/s_l^2) and explain interpretation of left/right singular vectors for welfare and implementability; (b) correct the algebraic/notation slip in OA3.2 (replace the erroneous _ll^* = (1/s_ll) b_ll^2 with _ll^* = (1/s_ll) _ll and show the derivation a* = V S^{-1} U^T b); and (c) add a precise treatment of multiplicity by restating results in terms of projections onto extremal eigenspaces and proving convergence of projection norms (or continuity under small eigenvalue splits) so prescriptions remain well-defined in the degeneracy case.

**Incomplete-information and variance-control assumptions are economically restrictive**

Readers might note that the incomplete-information extensions (Section 5) rely on strong directional neutrality and implementability assumptions (mean-shift costs quadratic and variance-control costs orthogonally invariant), which make costs blind to which principal components are adjusted. These assumptions are strong relative to realistic administrative frictions or instruments and can materially affect the planner's trade-offs between amplification and directional cost heterogeneity. It would be helpful to (a) state Assumptions 4–5 explicitly at the start of Section 5 and spell out the economic content and institutional settings that would justify them, (b) add robustness results for more realistic cost structures (for example diagonal but non-identical variance costs K = sum c_i y_i^2 or cost functions that penalize off-diagonal covariances), and (c) include a short worked example showing how directional cost asymmetry can change the ranking of principal components or reverse the complete-information prescription.

**Equilibrium uniqueness, shadow-price μ existence, and equilibrium selection concerns**

It would be helpful to make explicit the equilibrium-selection assumptions and to give a careful existence/uniqueness argument for the scalar shadow price μ that determines component weights. The current presentation relies on Assumption 2 (invertibility of I−βG and distinct eigenvalues) but does not consistently state whether welfare comparisons are conditional on a unique equilibrium or on a selection rule when multiplicity appears (e.g., with substitutes or nonlinearity). Reviewers suggest adding a standalone lemma proving existence, uniqueness, continuity and monotonicity of μ (handling cases w>0 and w<0 and zero status‑quo projections), and providing a numerically stable algorithm (bisection or damped Newton with bracketing) for computing μ. It would also be useful to add discussion/propositions on robustness of the main PC‑ordering results under equilibrium multiplicity (e.g., hold for any locally stable equilibrium or provide bounds across equilibria) and a short example where an intervention changes multiplicity so practitioners see the relevance for policy design.

**Robustness to network measurement error and implementability constraints**

Readers might note that the practical recommendation to target principal components assumes precise knowledge of G and the ability to implement arbitrary node‑level linear combinations, but empirical networks are estimated and political or logistical constraints often restrict instruments. Small perturbations in G can rotate eigenvectors dramatically when spectral gaps are small. Suggested remedies are to (a) add a robustness section that uses standard matrix-perturbation results (Davis–Kahan / Weyl / Wedin bounds) to translate G perturbations into bounds on eigenvector rotation and resulting welfare loss, (b) analyze constrained intervention spaces (k-sparse or sign-restricted y) by deriving the projection of the unconstrained optimum onto feasible subspaces and presenting KKT/algorithmic solutions, and (c) offer practical diagnostics (report spectral gap, confidence intervals for leading eigenvectors) and a numerical illustration showing how estimation noise or sparsity constraints change the recommended target.

**Status**: [Pending]

---

## Detailed Comments (13)

### 1. Ordering depends on amplification αℓ, not raw λℓ

**Status**: [Pending]

**Quote**:
> We analyze this question by decomposing any intervention into orthogonal principal components, which are determined by the network and are ordered according to their associated eigenvalues.

**Feedback**:
It would be helpful to state that the planner's ordering is induced by amplification factors α_ℓ = 1/(1-βλ_ℓ)^2 rather than raw eigenvalues. Readers might note that dα/dλ = 2β/(1-βλ)^3, so α_ℓ increases with λ_ℓ when β>0 and decreases when β<0 (provided 1-βλ_ℓ>0). Please rewrite the sentence to emphasize α_ℓ as the decision-relevant mapping from eigenvalues to importance and add the short derivative remark to make the monotonicity condition explicit.

---

### 2. Large-budget concentration requires distinct extremal amplification

**Status**: [Pending]

**Quote**:
> For large budgets, optimal interventions are simple - they involve a single principal component.

**Feedback**:
It would be helpful to qualify this claim by noting the claim relies on quadratic, rotationally invariant costs, symmetric G, and a unique extremal amplification α. Readers might note that if the extremal α is repeated the scalar-denominator arguments (e.g. factors like (α_1-α_2)) vanish and the large-C limit concentrates on the entire extremal eigenspace rather than a unique vector. Please add a short proviso in the main text stating these assumptions and, where used, replace statements that assert concentration onto a single eigenvector with the more precise statement 'concentration onto the corresponding extremal eigenspace' when α has multiplicity.

---

### 3. Incorrect change-of-variables in Example 2 (tilde vs plain b)

**Status**: [Pending]

**Quote**:
> Performing the change of variables $b_{i}=[\tau-b_{i}]/2$ and $\beta=-\tilde{\beta}/2$ (with the status quo equal to $\hat{b}_{i}=[\tau-\tilde{b}_{i}]/2$) yields a best-response structure exactly as in condition (2).

**Feedback**:
It would be helpful to correct the substitution so the algebra is consistent: differentiating the example yields b_i = (τ-\tilde b_i)/2 (not b_i = (τ-b_i)/2) and β = -\tildeβ/2. Readers might note the right-hand side must use \tilde b_i (the original parameter) rather than b_i. Please replace the quoted line with the corrected substitution b_i = (τ-\tilde b_i)/2 and β = -\tildeβ/2 and show the short derivation step so the mapping to condition (2) is transparent.

---

### 4. Alpha definition missing square: α_ℓ = (1-βλ_ℓ)^{-2}

**Status**: [Pending]

**Quote**:
> The second factor, $\frac{w\alpha_{\ell}}{\mu-w\alpha_{\ell}}$, is determined by two quantities: the eigenvalue corresponding to $\bm{u}^{\ell}(\bm{G})$ (via $\alpha_{\ell}=\frac{1}{1-\beta\lambda_{\ell}}$), and the budget $C$ (via the shadow price $\mu$).

**Feedback**:
It would be helpful to correct the inconsistent definition: because a^*_ℓ = (1/(1-βλ_ℓ))·\underline{b}_ℓ and welfare involves a^2, the amplification factor used in the welfare expressions is α_ℓ = 1/(1-βλ_ℓ)^2. Readers might note the printed unsquared form contradicts the equilibrium relation and the surrounding algebra; please replace α_ℓ=1/(1-βλ_ℓ) by α_ℓ=(1-βλ_ℓ)^{-2} wherever α_ℓ is used to weight welfare or variance.

---

### 5. Parameterization x_ℓ undefined when status‑quo component is zero

**Status**: [Pending]

**Quote**:
> Define $x_{\ell} = (\underline{b}_{\ell} - \hat{\underline{b}}_{\ell}) / \hat{\underline{b}}_{\ell}$ as the change of $\underline{b}_{\ell}$, relative to $\hat{\underline{b}}_{\ell}$.

**Feedback**:
It would be helpful to note the implicit restriction $\hat{\underline b}_\ell\neq 0$ required for x_ℓ to be defined. Readers might note that if some status‑quo principal coordinate is zero the ratio is undefined; please either (a) state the domain restriction explicitly at the definition site, or (b) introduce the alternative local reparameterization y_ℓ = \underline b_ℓ - \hat{\underline b}_ℓ (so the budget is \sum y_ℓ^2 ≤ C) and indicate how coordinates with \hat{\underline b}_ℓ=0 are handled separately.

---

### 6. PCA interpretation: variance ∝ λ^2 and centering/unit‑norm

**Status**: [Pending]

**Quote**:
> An important interpretation of this diagonalization is as a decomposition into *principal components*. We can think of the columns of $\bm{G}$ as $n$ data points.

**Feedback**:
It would be helpful to make precise the PCA convention used: treating the columns x_i of G yields the (uncentered) second‑moment matrix GG^T, which for symmetric G equals G^2, so the variance explained by u^ℓ is proportional to λ_ℓ^2 and principal components are ordered by |λ_ℓ|. Readers might note also to state the unit‑norm constraint on principal directions and whether columns are mean‑centered (the paper appears to use the uncentered GG^T convention). Please add a brief explicit definition of the PCA convention and the normalization of u^ℓ so the interpretation and ordering are unambiguous.

---

### 7. Which spectral gap controls the simplicity threshold?

**Status**: [Pending]

**Quote**:
> When this gap is large, even at moderate budgets the intervention is simple.

**Feedback**:
It would be helpful to specify whether the 'gap' refers to raw eigenvalues (λ_1-λ_2) or to amplification differences (α_1-α_2) — and whether squared versions enter when welfare depends on a^2. Readers might note the budget threshold in the proofs depends on differences in mapped amplification factors α_ℓ (or α_ℓ^2); please replace 'this gap' by the precise quantity (e.g. 'the amplification gap α_1-α_2') and, if helpful, give the explicit expression for the threshold in terms of α's.

---

### 8. Bottom-gap ratio diverges as gap→0 for β<0 (sign correction)

**Status**: [Pending]

**Quote**:
> If $\beta<0$, then the term $\alpha_{n-1}/(\alpha_{n-1}-\alpha_{n})$ is small when the “bottom gap” of the graph, the difference $\lambda_{n-1}-\lambda_{n}$, is small.

**Feedback**:
It would be helpful to correct the asymptotic sign in this sentence: with α(λ)=(1-βλ)^{-2} and β<0, a small bottom gap δ makes α_{n-1}-α_n ≈ 2β(1-βλ_n)^{-3}δ → 0, so the ratio α_{n-1}/(α_{n-1}-α_n) actually grows without bound as δ→0. Replace 'is small' with 'grows large' and note that the threshold in Proposition 2 becomes arbitrarily large as the bottom gap shrinks; this change is important for interpreting the proposition when spectral gaps are small.

---

### 9. Typographical slip in Proposition 1: r_t -> r_ℓ

**Status**: [Pending]

**Quote**:
> As $C\to 0$, in the optimal intervention, $\frac{r_{t}^{*}}{r_{\ell^{\prime}}^{*}}\to\frac{\alpha_{\ell}}{\alpha_{\ell^{\prime}}}$.

**Feedback**:
It would be helpful to fix the index typo: the numerator should be r_ℓ^* to match the α_ℓ on the right-hand side. Readers might note the current r_t^* inflates confusion with an undefined index t; please replace r_t^* by r_ℓ^* so the notation matches surrounding text and the stated limit.

---

### 10. Unjustified comparison \tilde{x}_1 ≥ x_1^* used in inequality chain

**Status**: [Pending]

**Quote**:
> &\leq 1 + \frac{\sum_{\ell \neq 1} \hat{b}_{\ell}^{2} \alpha_{\ell} x_{\ell}^{*} (x_{\ell}^{*} + 2)}{\hat{b}_{1}^{2} \alpha_{1} \tilde{x}_{1} (\tilde{x}_{1} + 2) + \sum_{\ell} \alpha_{\ell} \hat{b}_{\ell}^{2}} \quad \text{as } \tilde{x}_{1} \geq x_{1}^{*}

**Feedback**:
It would be helpful to either justify the inequality \tilde{x}_1 \ge x_1^* under the standing assumptions or to remove that step and bound the denominator directly. Readers might note there is no general argument provided that \tilde{x}_1 = √C/\hat b_1 always exceeds x_1^* = wα_1/(μ-wα_1). Please either add a short lemma proving \tilde{x}_1 ≥ x_1^* under the model's parameter restrictions, or replace the inequality chain with a conservative bound (for example, lower-bound the denominator by \hat b_1^2 α_1 \tilde x_1^2) and carry the resulting (weaker) estimate through the argument.

---

### 11. OA lemma: eigenvector normalization error (√n vs 1/√n)

**Status**: [Pending]

**Quote**:
> 2. $\lambda_{1}(\bm{G})=1$ and $u_{i}^{1}(\bm{G})=\sqrt{n}$ for all $i$

**Feedback**:
It would be helpful to correct the normalization: if the all-ones vector is an eigenvector, the unit‑norm principal eigenvector is u^1=(1/\sqrt{n})1, so u_i^1=1/\sqrt{n}, not √n. Readers might note the current statement implies ||u^1||_2=n, which conflicts with subsequent identities that use u^1 normalized to unit length. Please replace √n by 1/√n and check all downstream formulas that use u^1 for consistency.

---

### 12. Lemma OA2 derivative index slip: denominator should involve \hat b_ℓ^2

**Status**: [Pending]

**Quote**:
> 2. $\frac{d\mu}{dx_{1}}=\frac{\hat{b}_{1}^{2}x_{1}}{\sum_{\ell=2}\frac{w_{1}^{2}\hat{b}_{1}^{2}\alpha_{\ell}^{2}}{(\mu-w_{1}\alpha_{\ell})^{3}}}$

**Feedback**:
It would be helpful to correct the denominator: implicit differentiation of $\sum_{\ell\ge 2}\hat b_\ell^2\left(\frac{w_1\alpha_\ell}{\mu-w_1\alpha_\ell}\right)^2 = C - \hat b_1^2 x_1^2$ yields $$\frac{d\mu}{dx_1}=\frac{\hat b_1^2 x_1}{\sum_{\ell\ge 2} \hat b_\ell^2 \frac{w_1^2 \alpha_\ell^2}{(\mu-w_1\alpha_\ell)^3}}.$$ Readers might note the printed formula mistakenly inserts \hat b_1^2 inside each summand; please replace those factors with the correct \hat b_\ell^2 and update the lemma statement and proof accordingly.

---

### 13. Feasible interval for x_1 missing square root on C

**Status**: [Pending]

**Quote**:
> We fix $x_1$ so that $C(x_1) \geq 0$; that is, $x_1 \in [-C / \hat{\underline{b}}_1, C / \hat{\underline{b}}_1]$.

**Feedback**:
It would be helpful to correct the feasible set: since $C(x_1)=C-\hat{\underline b}_1^2 x_1^2 \ge 0$, the correct bound is $|x_1| \le \sqrt{C}/\hat{\underline b}_1$. Readers might note the printed linear bound conflicts with the quadratic budget constraint; please replace C/\hat b_1 by √C/\hat b_1 and adjust any subsequent uses of this interval.

---
