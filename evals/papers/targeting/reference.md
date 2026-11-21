# Targeting Interventions in Networks

**Date**: 3/3/2026, 8:59:21 PM
**Domain**: Example
**Taxonomy**: Demo
**Filter**: Active comments

---

## Overall Feedback

**Central Claim**
The paper characterizes optimal incentive targeting in network games by decomposing policies along the principal components of the interaction matrix, finding that optimal interventions load on top eigenvectors for strategic complements and bottom eigenvectors for substitutes, eventually converging to simple single-component policies as budgets increase.

**Main Areas for Reflection**

- **Generalizing the welfare specification**
The current analysis relies on Property A, where aggregate welfare takes the form $W(b,G) \propto a^{* \top} a^*$. To assist readers interested in broader applications, it may be helpful to briefly discuss how the principal-component logic extends to general quadratic welfare forms. Incorporating a result from the current appendices into the main text could concisely demonstrate that the high-versus-low spectral targeting insight remains robust beyond this specific scalar structure.

- **Asymmetries and directed networks**
Since the decomposition $G=U\Lambda U^\top$ assumes symmetry, readers might naturally wonder about the applicability to directed networks common in economic settings. A short derivation or proposition clarifying how the analysis adapts—perhaps by focusing on the symmetric component $(G+G^\top)/2$ or singular vectors—would help clarify the scope. This could reinforce the qualitative findings regarding spectral modes without requiring a complete re-derivation of the model.

- **Instrument costs and heterogeneity**
The optimization currently exploits the rotational invariance of the cost function $K(b,\hat b)=\sum (b_i-\hat b_i)^2$. It might be beneficial to briefly address how the conceptual insights translate when costs are heterogeneous or when instruments operate on actions directly (e.g., subsidies). A short note mapping these more complex instruments into the existing $b$-space framework could clarify the conditions under which the eigenbasis decoupling remains a valid guide for policy.

- **Distinction from centrality measures**
Given the rich literature on spectral centrality, distinguishing the specific contributions of this decomposition approach is valuable. It could be illuminating to explicitly contrast the "bottom-eigenvector" targeting for substitutes against standard centrality heuristics found in prior work. A simple worked example where this method's recommendations diverge from traditional key-player policies would effectively highlight the distinct economic prescriptions offered by this framework.

**Status**: [Pending]

---

## Detailed Comments (6)

### 1. Limiting direction of intervention in Proposition 1

**Status**: [Pending]

**Quote**:
> If $\beta>0$ (the game features strategic complements), then the similarity of $\boldsymbol{y}^{*}$ and the first principal component of the network tends to $1: \rho\left(\boldsymbol{y}^{*}, \boldsymbol{u}^{1}(\boldsymbol{G})\right) \rightarrow 1$.
2b. If $\beta<0$ (the game features strategic substitutes), then the similarity of $\boldsymbol{y}^{*}$ and the last principal component of the network tends to $1: \rho\left(\boldsymbol{y}^{*}, \boldsymbol{u}^{n}(\boldsymbol{G})\right) \rightarrow 1$.

**Feedback**:
In Proposition 1(2a–b) you state that, as $C\to\infty$, the cosine similarity between the optimal intervention and the relevant principal component converges to 1, and you later write that $\boldsymbol{y}^*\to\sqrt{C}\,\boldsymbol{u}^1(\boldsymbol{G})$ (or $\sqrt{C}\,\boldsymbol{u}^n(\boldsymbol{G})$). 

Given Theorem 1 and the budget constraint, what can generally be shown under Assumptions 1–3 and Property A is that $\rho(\boldsymbol{y}^*,\boldsymbol{u}^1)^2\to 1$ when $\beta>0$ (and analogously for $\boldsymbol{u}^n$ when $\beta<0$). For $w>0$ we have $x_\ell^* = w\alpha_\ell/(\mu-w\alpha_\ell)\ge 0$ and $\underline{y}_\ell^* = \underline{\hat b}_\ell x_\ell^*$. As $C\to\infty$, the component $\underline{y}_1^*$ dominates the budget, with $(\underline{y}_1^*)^2\sim C$, so
\[
\rho(\boldsymbol{y}^*,\boldsymbol{u}^1) 
= \frac{\underline{y}_1^*}{\sqrt{C}}
\to \mathrm{sign}(\hat{\boldsymbol{b}}\cdot\boldsymbol{u}^1),
\]
and similarly with $\boldsymbol{u}^n$ in the substitutes case. Thus, for a fixed orientation of the eigenvectors, the limit of the cosine similarity is $\pm 1$, with the sign determined by $\hat{\boldsymbol{b}}\cdot\boldsymbol{u}^1$ (or $\hat{\boldsymbol{b}}\cdot\boldsymbol{u}^n$). 

Since eigenvectors are only defined up to sign, one can always reorient $\boldsymbol{u}^1$ (or $\boldsymbol{u}^n$) so that the limiting cosine similarity is $+1$, and the economic content of the result is that the intervention concentrates on the corresponding one-dimensional eigenspace. It would nonetheless be helpful to make this explicit—e.g., by formulating Proposition 1 in terms of $|\rho(\boldsymbol{y}^*,\boldsymbol{u}^1)|\to 1$ (and $|\rho(\boldsymbol{y}^*,\boldsymbol{u}^n)|\to 1$), or by stating any normalization of eigenvectors and/or restriction on the status quo vector that guarantees $\hat{\boldsymbol{b}}\cdot\boldsymbol{u}^1>0$ and $\hat{\boldsymbol{b}}\cdot\boldsymbol{u}^n>0$.

---

### 2. Comparative static claim in Footnote 16

**Status**: [Pending]

**Quote**:
> It can be verified that, for every $\ell \in\{1, \ldots, n-1\}$, the ratio $x_{\ell} / x_{\ell+1}$ is increasing (decreasing) in $\beta$ for the case of strategic complements (substitutes): thus the intensity of the strategic interaction shapes the relative importance of different principal components.

**Feedback**:
Footnote 16 states that, for each $\ell$, the ratio $x_\ell/x_{\ell+1}$ is increasing in $\beta$ when $\beta>0$ and decreasing in $\beta$ when $\beta<0$. Using the expression from Theorem 1, $x_\ell^* = w\alpha_\ell/(\mu - w\alpha_\ell)$ with $\alpha_\ell=(1-\beta\lambda_\ell)^{-2}$ and $\mu$ determined by (6), one can look at the small‑budget limit $C\to 0$, where $\mu\to\infty$ and hence
\[
\frac{x_\ell^*}{x_{\ell+1}^*}\to \frac{\alpha_\ell}{\alpha_{\ell+1}} = \left(\frac{1-\beta\lambda_{\ell+1}}{1-\beta\lambda_\ell}\right)^2.
\]
Differentiating this limiting expression with respect to $\beta$ gives a strictly positive derivative for all admissible $\beta$, irrespective of the sign of $\beta$. Thus, at least for small budgets, the ratio $x_\ell^*/x_{\ell+1}^*$ is increasing in $\beta$ both for strategic complements and for strategic substitutes, contrary to the literal wording of the footnote.

This is a local, not a global, calculation, but by continuity it is hard to reconcile with the claim that the ratio is everywhere decreasing in $\beta$ when $\beta<0$. It would be helpful to double‑check this comparative static and either (i) reverse the direction for the substitutes case, or (ii) clarify that the intended statement is about monotonicity in the intensity $|\beta|$ rather than in $\beta$ itself, or else drop the claim.

---

### 3. Sign error in discussion of Proposition 2 (substitutes case)

**Status**: [Pending]

**Quote**:
> If the game has the strategic substitutes property, $\beta<0$, then for any $\epsilon>0$, if $C> \frac{2\|\hat{\boldsymbol{b}}\|^{2}}{\epsilon}\left(\frac{\alpha_{n-1}}{\alpha_{n}-\alpha_{n-1}}\right)^{2}$, then...
...
If $\beta<0$, then the term $\alpha_{n-1} /\left(\alpha_{n-1}-\alpha_{n}\right)$ is large when the difference $\lambda_{n-1}-\lambda_{n}$, which we call the "bottom gap," is small.

**Feedback**:
In the paragraph interpreting Proposition 2 for the substitutes case, the factor governing the bound on $C$ is described as $\alpha_{n-1}/(\alpha_{n-1}-\alpha_n)$, whereas in the formal statement of the proposition the factor is $\alpha_{n-1}/(\alpha_n-\alpha_{n-1})$ inside a square. Since for $\beta<0$ one has $\alpha_n>\alpha_{n-1}$, the latter uses a positive denominator and matches the expression used in the proof, while the former has the opposite sign. Because the ratio is squared in the bound, this does not affect the actual condition on $C$, but it introduces an avoidable notational inconsistency. It would be helpful to align the discussion with the proposition (using $\alpha_n-\alpha_{n-1}$) so that the "corresponding factor for bottom $\alpha$'s" is written with the same ordering throughout.

---

### 4. Unclear notation in proof of Proposition 2

**Status**: [Pending]

**Quote**:
> Cosine similarity. We now turn to the cosine similarity result. We focus on the case of strategic complements. The proof for the case of strategic substitutes is analogous. We start by writing a useful explicit expression for $\rho\left(\Delta \boldsymbol{b}^{*}, \sqrt{C} \boldsymbol{u}^{1}\right)$:

$$
\rho\left(\Delta \boldsymbol{b}^{*}, \sqrt{C} \boldsymbol{u}^{1}\right)=\frac{\left(\boldsymbol{b}^{*}-\hat{\boldsymbol{b}}\right) \cdot\left(\sqrt{C} \boldsymbol{u}^{1}\right)}{\left\|\boldsymbol{b}^{*}-\hat{\boldsymbol{b}}\right\|\left\|\sqrt{C} \boldsymbol{u}^{1}\right\|}=\frac{\left(\boldsymbol{b}^{*}-\hat{\boldsymbol{b}}\right) \cdot\left(\boldsymbol{u}^{1}\right)}{\sqrt{C}},
$$

where the last equality follows because, at the optimum, $\left\|\boldsymbol{b}^{*}-\hat{\boldsymbol{b}}\right\|^{2}=C$. ... Hence, using this in equation (12), we can deduce that

$$
\rho\left(\Delta \boldsymbol{b}^{*}, \boldsymbol{u}^{1}\right)=\frac{1}{\sqrt{C}} \frac{w \alpha_{1}}{\mu-w \alpha_{1}} \hat{b}_{1} \geq \sqrt{1-\epsilon} \quad \text { iff } \quad\left(\frac{w \alpha_{1}}{\mu-w \alpha_{1}}\right)^{2} \hat{b}_{1}^{2}-C(1-\epsilon) \geq 0 .
$$

**Feedback**:
At first the cosine‑similarity part of the proof of Proposition 2 was a bit hard to parse because of notation. The vector $\Delta\boldsymbol{b}^*$ is not explicitly defined, and the text switches between $\rho(\Delta\boldsymbol{b}^*,\sqrt{C}\boldsymbol{u}^1)$ and $\rho(\Delta\boldsymbol{b}^*,\boldsymbol{u}^1)$. From the displayed equality
$$
\rho(\Delta\boldsymbol{b}^*,\sqrt{C}\boldsymbol{u}^1)
= \frac{(\boldsymbol{b}^*-\hat{\boldsymbol{b}})\cdot(\sqrt{C}\boldsymbol{u}^1)}
{\|\boldsymbol{b}^*-\hat{\boldsymbol{b}}\|\,\|\sqrt{C}\boldsymbol{u}^1\|},
$$
one can infer that $\Delta\boldsymbol{b}^*=\boldsymbol{b}^*-\hat{\boldsymbol{b}}$, and using $\|\boldsymbol{b}^*-\hat{\boldsymbol{b}}\|^2=C$ and $\|\boldsymbol{u}^1\|=1$ it is easy to verify that $\rho(\Delta\boldsymbol{b}^*,\sqrt{C}\boldsymbol{u}^1)=\rho(\Delta\boldsymbol{b}^*,\boldsymbol{u}^1)$. Still, defining $\Delta\boldsymbol{b}^*$ explicitly (or sticking to $\boldsymbol{y}^*$) and noting the scale‑invariance of cosine similarity would make this part of the proof smoother to follow.

---

### 5. "Maximizer" vs. "minimizer" for smallest eigenvalues

**Status**: [Pending]

**Quote**:
> Turning next to strategic substitutes, recall that the smallest two eigenvalues, $\lambda_{n}$ and $\lambda_{n-1}$, can be written as follows:
$$
\lambda_{n}=\min _{\boldsymbol{u}:\|\boldsymbol{u}\|=1} \sum_{i, j \in \mathcal{N}} g_{i j} u_{i} u_{j}, \quad \lambda_{n-1}=\min _{\substack{\boldsymbol{u}:\|\boldsymbol{u}\|=1 \\ \boldsymbol{u} \cdot \boldsymbol{u}^{n}=0}} \sum_{i, j \in \mathcal{N}} g_{i j} u_{i} u_{j} .
$$
Moreover, the eigenvector $\boldsymbol{u}^{n}$ is a maximizer of the first problem, while $\boldsymbol{u}^{n-1}$ is a maximizer of the second; these are uniquely determined under Assumption 2.

**Feedback**:
In the substitutes discussion you correctly write the Rayleigh–Ritz characterizations for $\lambda_n$ and $\lambda_{n-1}$ as minimization problems, but then state that $\boldsymbol{u}^n$ and $\boldsymbol{u}^{n-1}$ are "maximizers" of these problems. Since the display uses $\min$ and the next sentence reintroduces $\boldsymbol{u}^n$ via an explicit $\arg\min$, these eigenvectors should be described as minimizers, not maximizers. This is clearly just a wording slip and does not affect any results, but it would be good to correct it for consistency with the complements case and with standard spectral terminology.

---

### 6. Typo in Lagrangian in proof of Theorem 1

**Status**: [Pending]

**Quote**:
> Observe that the Lagrangian corresponding to the maximization problem is

$$
\mathcal{L}=w \sum_{\ell=1}^{n} \alpha_{\ell}\left(1+x_{\ell}\right)^{2} \underline{\hat{b}}_{\ell}+\mu\left[C-\sum_{\ell=1}^{n} \hat{b}_{\ell}^{2} x_{\ell}^{2}\right] .
$$

Taking our observation above that the constraint is binding at $\boldsymbol{x}=\boldsymbol{x}^{*}$, together with the standard results on the Karush-Kuhn-Tucker conditions, the first-order conditions must hold exactly at the optimum with a positive $\mu$ :

**Feedback**:
The displayed Lagrangian in the proof of Theorem 1 appears to omit a square on the status‑quo component. Just above, the problem in the $x_\ell$ variables is written as
$$
\max_x\; w\sum_{\ell=1}^n \alpha_\ell (1+x_\ell)^2 \underline{\hat b}_\ell^2
\quad \text{s.t. } \sum_{\ell=1}^n \underline{\hat b}_\ell^2 x_\ell^2 \le C,
$$
so the corresponding Lagrangian should involve $\underline{\hat b}_\ell^2$ in the first term as well. The first‑order condition you derive immediately afterward matches the derivative of this corrected Lagrangian, not the one as currently printed. This is a minor typographical issue, but correcting the exponent (and, if desired, harmonizing the underline notation for $\hat b_\ell$) would remove the internal inconsistency in this display.

---
