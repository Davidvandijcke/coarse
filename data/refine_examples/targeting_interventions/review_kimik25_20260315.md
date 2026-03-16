# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/14/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper studies optimal targeted interventions in network games where a planner adjusts agents' standalone returns to maximize aggregate welfare. Under the assumption of symmetric network adjacency matrices and quadratic welfare functions (Property A), the authors characterize optimal interventions using spectral decomposition, showing that small budgets favor targeting principal components aligned with the status quo, while large budgets target specific eigenvectors (first for complements, last for substitutes) depending on the nature of strategic interactions. The analysis provides conditions under which optimal interventions become 'simple' (concentrated on a single principal component) and extends to incomplete information settings with random standalone returns.

Below are the most important issues identified by the review panel.

**Limitations of Symmetric Network Assumptions for Directed Graphs**

The characterization results rely on symmetric adjacency matrices, which excludes economically important directed networks such as supply chains, citation networks, and hierarchical organizations. While the online appendix extends the analysis to non-symmetric matrices using singular value decomposition, this generalization severs the connection to eigenvector centrality and yields distinct left and right singular vectors that complicate the economic interpretation of targeting. It would be helpful to clarify in the main text that the clean targeting insights regarding 'global' versus 'local' structure apply primarily to undirected networks, and to characterize which singular vectors are prioritized when the network is directed.

**Genericity Assumptions and Undefined Similarity Ratios**

The main theorems assume distinct eigenvalues (Assumption 2) and implicitly require the status quo vector to have non-zero projection on all principal components, excluding symmetric network structures with repeated eigenvalues and status quo vectors orthogonal to certain eigenvectors. When these genericity conditions fail, similarity ratios become undefined (0/0) and the small-budget characterization in Proposition 1 does not hold as stated, leaving a gap for important cases such as regular graphs or uniform status quo vectors. It would be helpful to explicitly state the genericity conditions in the theorem assumptions and to provide the optimal intervention characterization for non-generic cases, particularly when the status quo lacks support on certain principal components.

**Spectral Gaps and the Validity of Simple Intervention Characterizations**

Proposition 2 establishes that optimal interventions become 'simple' (concentrated on a single principal component) only when budgets exceed thresholds scaling with the inverse square of spectral gaps (α₁-α₂ for complements, αₙ₋₁-αₙ for substitutes). For networks with small spectral gaps—such as those with community structure or near-bipartite graphs—these thresholds imply arbitrarily large budget requirements, and the optimal intervention may never simplify even with substantial resources. It would be helpful to clarify that the simple intervention results apply only when eigenvalue gaps are sufficiently large, and to characterize optimal interventions for moderate budgets when spectral gaps are small, bridging the gap between the small-budget perturbation and large-budget regimes.

**Restrictive Welfare Specifications and Externalities**

The principal component targeting results rely on Property A, which restricts welfare to be proportional to the sum of squares of equilibrium actions, excluding general externality structures with linear terms or cross-components. As shown in Theorem OA1, when externalities take more general forms, the optimal intervention may prioritize the second principal component over the first even in the large-budget limit, contradicting the main text's suggestion that the key insights extend unchanged to general externalities. It would be helpful to prominently acknowledge in the main text that the targeting priorities depend crucially on Property A, and to either present the general characterization from Theorem OA1 or provide robustness analysis showing how the principal component ordering changes with different externality structures.

**Unaddressed Constraints on Actions and Intervention Classes**

The analysis assumes actions can take any real value and restricts attention to deterministic mean shifts under incomplete information, but many applications require non-negative actions (investment, effort) and may benefit from state-contingent or randomized interventions. Large interventions targeting the last principal component for strategic substitutes can induce negative equilibrium actions, yet the paper lacks a characterization of optimal interventions under explicit non-negativity constraints, which would require solving constrained rather than unconstrained quadratic programs. Additionally, Proposition 3 does not establish that deterministic interventions are optimal among all possible state-contingent or randomized strategies. It would be helpful to discuss how the optimal intervention changes with non-negativity constraints and to either prove the optimality of deterministic shifts or quantify the welfare loss from this restriction.

**Status**: [Pending]

---

## Detailed Comments (14)

### 1. Incorrect identification of network multiplier

**Status**: [Pending]

**Quote**:
> This basis has three special properties: (a) the effects of an intervention along a principal component is proportional to the intervention, scaled by a network multiplier; (b) the “network multiplier” is an eigenvalue of the network corresponding to that principal component; (c) the principal components are orthogonal, so that the effects along various principal components can be treated separately (in a suitable sense).

**Feedback**:
Property (b) incorrectly states that the network multiplier equals the eigenvalue $\lambda_{\ell}$. In the linear-quadratic model, equilibrium actions satisfy $\bm{a} = (\bm{I} - \beta\bm{G})^{-1}\bm{b}$, so the effect of an intervention along principal component $\ell$ scales by $\frac{1}{1-\beta\lambda_{\ell}}$ for actions (or $\frac{1}{(1-\beta\lambda_{\ell})^{2}}$ for welfare), not by $\lambda_{\ell}$ itself. It would be helpful to rewrite property (b) to state that the multiplier is determined by the eigenvalue via $\frac{1}{1-\beta\lambda_{\ell}}$ (or $\frac{1}{(1-\beta\lambda_{\ell})^{2}}$ for welfare).

---

### 2. Incorrect optimization characterization of first principal component

**Status**: [Pending]

**Quote**:
> The first principal component of $\bm{G}$ is defined as the $n$-dimensional vector that minimizes the sum of squares of the distances to the columns of $\bm{G}$.

**Feedback**:
The objective $\sum_{i=1}^n \|\bm{g}_i - \bm{v}\|^2$ is minimized by the centroid $\bar{\bm{g}}$, not the first principal component. The first principal component is the unit vector $\bm{u}$ that minimizes the sum of squared reconstruction errors $\sum_{i=1}^n \|\bm{g}_i - (\bm{g}_i \cdot \bm{u})\bm{u}\|^2$, or equivalently maximizes the variance of projections. It would be helpful to rewrite this sentence as: "The first principal component of $\bm{G}$ is defined as the unit vector that minimizes the sum of squares of the distances from the columns of $\bm{G}$ to their projections onto this vector."

---

### 3. Incorrect proportionality claim for status quo norm

**Status**: [Pending]

**Quote**:
> Observe that the first term on the right-hand side of the inequality for $C$ is proportional to $\|\hat{\bm{b}}\|$.

**Feedback**:
Proposition 2 states the budget threshold as $C>\frac{2\|\hat{\bm{b}}\|^{2}}{\epsilon}\left(\frac{\alpha_{2}}{\alpha_{1}-\alpha_{2}}\right)^{2}$. The dependence on the status quo enters through the squared Euclidean norm $\|\hat{\bm{b}}\|^{2}$, not the linear norm. A larger status quo magnitude increases the required budget quadratically. It would be helpful to rewrite "$\|\hat{\bm{b}}\|$" as "$\|\hat{\bm{b}}\|^{2}$" to correctly describe the scaling relationship.

---

### 4. Unstated dependence on status quo in Proposition 1.1

**Status**: [Pending]

**Quote**:
> As $C\to 0$, in the optimal intervention, $\frac{r_{t}^{*}}{r_{\ell^{\prime}}^{*}}\to\frac{\alpha_{\ell}}{\alpha_{\ell^{\prime}}}$.

**Feedback**:
From equation (5), $r_\ell^* = \frac{w\alpha_\ell}{\mu - w\alpha_\ell}\hat{b}_\ell$. As $C\to 0$, $\mu\to\infty$, so $r_\ell^* \approx \frac{w\alpha_\ell}{\mu}\hat{b}_\ell$. The ratio $r_\ell^*/r_{\ell'}^*$ converges to $\frac{\alpha_\ell \hat{b}_\ell}{\alpha_{\ell'} \hat{b}_{\ell'}}$, not $\frac{\alpha_\ell}{\alpha_{\ell'}}$, unless $\hat{b}_\ell = \hat{b}_{\ell'}$ for all $\ell$. It would be helpful to add after Proposition 1.1: "This assumes $\hat{b}_\ell \neq 0$ for all $\ell$, where $r_\ell^*$ denotes the ratio of the optimal intervention to the status quo in the $\ell$-th principal component."

---

### 5. Typo in Lagrangian objective term

**Status**: [Pending]

**Quote**:
> $\mathcal{L}=w\sum_{\ell}\alpha_{\ell}(1+x_{\ell})^{2}\hat{\underline{b}}_{\ell}+\mu\left[C-\sum_{\ell}\hat{\underline{b}}_{\ell}^{2}x_{\ell}^{2}\right].$

**Feedback**:
The objective term omits the necessary square on $\hat{\underline{b}}_{\ell}$. The transformed objective is $w \sum_{\ell} \alpha_{\ell} (1 + x_{\ell})^{2} \hat{\underline{b}}_{\ell}^{2}$, and the first-order condition (10) is derived correctly only if the Lagrangian contains $\hat{\underline{b}}_{\ell}^{2}$. Readers might note that rewriting the Lagrangian as $\mathcal{L}=w\sum_{\ell}\alpha_{\ell}(1+x_{\ell})^{2}\hat{\underline{b}}_{\ell}^{2}+\mu\left[C-\sum_{\ell}\hat{\underline{b}}_{\ell}^{2}x_{\ell}^{2}\right]$ would align the display with the derivation.

---

### 6. Linear cost interventions do not necessarily target only one individual

**Status**: [Pending]

**Quote**:
> if we consider problem (IT) but we assume that the cost of intervention is linear, that is, $K(\bm{b},\hat{\bm{b}})=\sum_{i}|b_{i}-\hat{b}_{i}|$, then the optimal intervention will target only one individual (see the discussion in Online Appendix Section OA3.3); note that the targeted individual is not necessarily the individual with the highest Bonacich centrality.

**Feedback**:
The claim that the optimal intervention necessarily targets exactly one individual is overstated. For isolated nodes ($\bm{G} = \bm{0}$), minimizing $\sum_i (b_i + y_i)^2$ subject to $\sum_i |y_i| \leq C$ yields $y_i = -\text{sign}(b_i)\min(|b_i|, \tau)$ where $\sum_i \min(|b_i|, \tau) = C$. If $\hat{\bm{b}} = (2, 2, 0, \dots, 0)$ and $C = 3$, we obtain $y_1 = y_2 = -1.5$, targeting two individuals. It would be helpful to rewrite "will target only one individual" as "may target only one individual when the budget is sufficiently small relative to the status quo heterogeneity".

---

### 7. Incorrect condition for positive externality

**Status**: [Pending]

**Quote**:
> This is a game of strategic complements; moreover, an increase in $j$'s action has a positive effect on individual $i$'s utility if and only if $a_j < a_i$.

**Feedback**:
Computing $\partial U_i/\partial a_j$ for $j \neq i$ yields $g_{ij}[(\tilde{\beta} + \gamma)a_i - \gamma a_j]$. This is positive if and only if $a_j < (1 + \frac{\tilde{\beta}}{\gamma})a_i$, not $a_j < a_i$. The stated condition holds only if $\tilde{\beta} = 0$. It would be helpful to rewrite as "an increase in $j$'s action has a positive effect on individual $i$'s utility if and only if $a_j < (1 + \frac{\tilde{\beta}}{\gamma})a_i$".

---

### 8. Welfare formula requires column-stochastic assumption

**Status**: [Pending]

**Quote**:
> Moreover, the aggregate equilibrium utility is $W(\pmb{b},\pmb{g}) = \frac{1}{2} (\pmb{a}^*)^\top \pmb{a}^*$.

**Feedback**:
Deriving aggregate utility $\sum_i U_i$ from the payoff function yields $\frac{1}{2}\sum_i (a_i^*)^2 + \frac{\gamma}{2}\sum_i (a_i^*)^2(1 - \sum_k g_{ki})$. The simplification to $\frac{1}{2}(\pmb{a}^*)^\top\pmb{a}^*$ requires $\sum_k g_{ki} = 1$ for all $i$ (column-stochastic). It would be helpful to add the assumption that $\pmb{G}$ is doubly stochastic, or correct the formula to account for arbitrary column sums.

---

### 9. Incorrect baseline coefficient in $w_1$ definition

**Status**: [Pending]

**Quote**:
> $w_{1}=1+m_{2}+m_{5}+(n-1)m_{4}$

**Feedback**:
At equilibrium, player $i$'s utility is $\hat{U}_{i}=\frac{1}{2}a_{i}^{2}$, so $\sum_{i}\hat{U}_{i}=\frac{1}{2}(\bm{a}^{*})^{\mathsf{T}}\bm{a}^{*}$. This creates an inconsistency with Example OA1 where the coefficient should be $\frac{1}{2}$. It would be helpful to rewrite the definition as $w_{1}=\frac{1}{2}+m_{2}+m_{5}+(n-1)m_{4}$.

---

### 10. Swapped externality coefficients $m_4$ and $m_5$ in $w_1$ and $w_2$

**Status**: [Pending]

**Quote**:
> $w_{1}=1+m_{2}+m_{5}+(n-1)m_{4}$, $w_{2}=nm_{5}(n-2)$

**Feedback**:
Aggregating the non-strategic externalities: $m_4(\sum_{j\neq i}a_j)^2$ contributes $m_4(n-2)(\sum_i a_i)^2 + m_4\sum_i a_i^2$, while $m_5\sum_{j\neq i}a_j^2$ contributes $m_5(n-1)\sum_i a_i^2$. The correct coefficients are $w_1 = \frac{1}{2}+m_2+m_4+(n-1)m_5$ and $w_2 = nm_4(n-2)$. It would be helpful to swap the $m_4$ and $m_5$ coefficients in the definitions.

---

### 11. Index error in Lemma OA2 derivative denominator

**Status**: [Pending]

**Quote**:
> $\frac{d\mu}{dx_{1}}=\frac{\hat{\underline{b}}_{1}^{2}x_{1}}{\sum_{\ell=2}\frac{w_{1}^{2}\hat{\underline{b}}_{1}^{2}\alpha_{\ell}^{2}}{(\mu-w_{1}\alpha_{\ell})^{3}}}$

**Feedback**:
Implicit differentiation yields $\frac{d\mu}{dx_{1}}=\frac{\hat{\underline{b}}_{1}^{2}x_{1}}{\sum_{\ell=2}\frac{w_{1}^{2}\hat{\underline{b}}_{\ell}^{2}\alpha_{\ell}^{2}}{(\mu-w_{1}\alpha_{\ell})^{3}}}}$. The summation index in the denominator must be $\ell$, not fixed at $1$. Readers might note that rewriting the denominator as $\sum_{\ell=2}\frac{w_{1}^{2}\hat{\underline{b}}_{\ell}^{2}\alpha_{\ell}^{2}}{(\mu-w_{1}\alpha_{\ell})^{3}}$ would correct the expression.

---

### 12. Proposition OA1 limit depends on status quo projections

**Status**: [Pending]

**Quote**:
> At the optimal intervention, if $C\to 0$ we have $\frac{r_{\ell}^{*}}{r_{\ell^{\prime}}^{*}}\to\frac{\alpha_{\ell}}{\alpha_{\ell^{\prime}}}$.

**Feedback**:
Re-deriving shows $r_{\ell}^{*} \propto \alpha_{\ell}^{2}\hat{\underline{b}}_{\ell}$ for generic $\hat{\bm{b}}\neq\bm{0}$, yielding $\frac{r_{\ell}^{*}}{r_{\ell^{\prime}}^{*}}\to\frac{\alpha_{\ell}^{2}\hat{\underline{b}}_{\ell}}{\alpha_{\ell^{\prime}}^{2}\hat{\underline{b}}_{\ell^{\prime}}}$. It would be helpful to rewrite the proposition to state the limit is $\frac{\alpha_{\ell}\hat{\underline{b}}_{\ell}}{\alpha_{\ell^{\prime}}\hat{\underline{b}}_{\ell^{\prime}}}$ (if first-order term dominates) or add the assumption that $\hat{\bm{b}}$ has equal projections.

---

### 13. Rescaled objective divergence in Proposition OA1 proof

**Status**: [Pending]

**Quote**:
> Let the objective at $C=0$ be the limit of $C^{-1}\Delta(C^{1/2}\check{\bm{y}})$ as $C\downarrow 0$, which we call $F$.

**Feedback**:
For generic $\hat{\bm{b}}\neq\bm{0}$, the limit does not exist because $C^{-1}\Delta(C^{1/2}\check{\bm{y}})=C^{-1/2}\sum_{\ell}\alpha_{\ell}^{2}\hat{\underline{b}}_{\ell}\check{\underline{y}}_{\ell}+O(1)$ diverges as $C\downarrow 0$. Consequently, Berge's Theorem of the Maximum does not apply. It would be helpful to restrict Proposition OA1 to $\hat{\bm{b}}=\bm{0}$, or modify the rescaling to subtract the linear term.

---

### 14. Uniform convergence claim misattributed to Lemma OA3

**Status**: [Pending]

**Quote**:
> Because the convergence of the objective is actually uniform on $\mathcal{K}$ by the Lemma, this is possible if and only if $\check{\bm{y}}$ approaches the solution of the problem

**Feedback**:
Lemma OA3 establishes uniform convergence of the rescaled cost function $C^{-1}\kappa(C^{1/2}\bm{z})\to k\|\bm{z}\|^{2}$, not the objective function $C^{-1}\Delta(C^{1/2}\check{\bm{y}})$. The uniform convergence of the objective requires additional justification. It would be helpful to add a proof that $C^{-1}\Delta(C^{1/2}\check{\bm{y}})$ converges uniformly on $\mathcal{K}$, or correct the attribution to the Lemma.

---
