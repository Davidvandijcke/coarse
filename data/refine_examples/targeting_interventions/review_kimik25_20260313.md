# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/13/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper studies optimal targeting interventions in networked economies where agents' actions exhibit strategic complementarities or substitutabilities. Using a linear-quadratic framework, the authors characterize the optimal intervention via spectral decomposition of the network adjacency matrix, showing that the planner should target specific principal components (eigenvectors) depending on whether spillovers are substitutes or complements and on the intervention budget size. The analysis provides conditions under which optimal interventions simplify to targeting a single network component, connecting optimal policy to network centrality measures.

Below are the most important issues identified by the review panel.

**Restrictive symmetry and spectral assumptions limit applicability to directed networks and regular graphs**

The analysis relies on Assumption 1 (symmetric adjacency matrix) and Assumption 2 (distinct eigenvalues), which exclude directed networks, asymmetric influence relationships, and structures with eigenvalue multiplicities such as regular graphs or symmetric community structures. When eigenvalues repeat, the spectral decomposition is not unique, rendering the optimal intervention ill-defined without additional selection criteria. While Section OA3.2 mentions singular value decomposition for non-symmetric cases, the paper does not establish whether the targeting insights regarding top versus bottom principal components generalize to directed settings, nor does it provide economic interpretations for left versus right singular vectors. Readers might note that the economic distinction between 'global' and 'local' network structure breaks down when singular vectors differ. It would be helpful to characterize optimal interventions under eigenvalue multiplicity by specifying a selection rule such as minimizing the intervention norm, and to derive explicit analogues of Theorem 1 and Proposition 2 for asymmetric networks using SVD that clarify how directedness alters the optimal targeting structure.

**Strong informational requirements and computational constraints hinder practical implementation**

The optimal intervention characterized in Theorem 1 requires the planner to possess complete knowledge of the entire network structure (all n² entries), the status quo standalone marginal benefits for every agent, and the precise eigenvectors of the adjacency matrix. This represents an idealized benchmark that ignores substantial costs of network measurement, privacy constraints surrounding individual benefit parameters, and computational limitations. Computing the full spectral decomposition requires O(n³) operations and O(n²) storage, which becomes prohibitive for large-scale networks with millions of nodes or time-varying topologies. While Section 5 relaxes knowledge of status quo benefits, it maintains perfect knowledge of the network structure without analyzing welfare loss from using estimated or sampled networks. It would be helpful to characterize optimal interventions under partial network observation (e.g., knowing only local neighborhoods or aggregated statistics), to quantify welfare degradation when using estimated eigenvectors rather than true ones, and to develop iterative or sampling-based algorithms that achieve near-optimal welfare with sub-cubic complexity for sparse network structures.

**Dependence on specific welfare functional form limits generalizability of targeting insights**

The main results rely on Property A, which requires that aggregate equilibrium welfare be proportional to the sum of squared equilibrium actions. This functional form implies the planner cares about the variance of actions across agents rather than the mean, and it holds only for specific payoff structures such as the investment game in Example 1. As shown in Online Appendix OA3.1, when the planner instead maximizes the sum of actions (linear welfare), the optimal intervention always targets the first principal component regardless of whether spillovers are substitutes or complements, fundamentally altering the targeting priorities. The paper does not establish conditions under which the qualitative insight—targeting top versus bottom components depending on strategic substitutes versus complements—survives alternative welfare specifications, nor does it provide bounds on targeting effectiveness for general concave-convex payoff structures. It would be helpful to include a robustness discussion in the main text highlighting the sensitivity of targeting priorities to welfare specification, and to characterize the optimal intervention for a broader class of welfare functions that includes linear objectives as a special case, clarifying under what conditions the core spectral targeting insights remain valid.

**Uncharacterized non-negativity constraints limit applicability to large-budget interventions**

Propositions 1 and 2 characterize simple optimal interventions for large budgets, assuming actions can take any real value and that the intervention vector approaches a scaled eigenvector of the network. However, in many economic applications such as investment, effort, or information acquisition, actions must be non-negative, and the paper acknowledges only in a footnote that such constraints may bind for large interventions without characterizing the threshold or the constrained solution. When non-negativity constraints bind, the optimal intervention is no longer proportional to a single eigenvector, and the simple characterization fails. Furthermore, if the status quo standalone benefits are small relative to the intervention budget, the unconstrained optimal solution might require negative actions for some agents to achieve proportional targeting, rendering the intervention infeasible. It would be helpful to derive explicit conditions on the budget size relative to the status quo benefits and network structure that ensure non-negativity constraints remain slack, or to characterize the constrained optimal intervention when constraints bind, potentially using Kuhn-Tucker conditions to show how the solution deviates from the eigenvector-based targeting.

**Exogenous network assumption ignores strategic link formation and dynamic responses**

The model treats the network as fixed and exogenous, assuming that the planner's intervention changes standalone benefits but does not alter the links between agents. However, in many economic contexts, changing investment incentives or standalone benefits would lead agents to strategically form or sever links to maximize their new payoffs, creating a feedback loop between interventions and network structure. For example, in R&D collaboration networks, subsidizing certain firms' investments might induce them to form new collaboration links, changing the adjacency matrix and its spectral decomposition, potentially rendering the original targeting suboptimal or destabilizing the equilibrium. The paper does not address whether optimal interventions are robust to small perturbations in the network topology, nor does it characterize targeting when the network is equilibrium-dependent. It would be helpful to acknowledge this limitation explicitly and discuss how the optimal intervention would need to be modified in a dynamic setting where the network evolves in response to the intervention, perhaps by considering a two-stage game where link formation precedes investment decisions or by analyzing the robustness of spectral targeting to network perturbations.

**Status**: [Pending]

---

## Detailed Comments (10)

### 1. Typographical error in change of variables (Example 2)

**Status**: [Pending]

**Quote**:
> Performing the change of variables $b_{i}=[\tau-b_{i}]/2$ and $\beta=-\tilde{\beta}/2$ (with the status quo equal to $\hat{b}_{i}=[\tau-\tilde{b}_{i}]/2$) yields a best-response structure exactly as in condition (2).

**Feedback**:
It would be helpful to correct the recursive definition $b_{i}=[\tau-b_{i}]/2$ to $b_{i}=[\tau-\tilde{b}_{i}]/2$ to properly express the transformation from the original parameter $\tilde{b}_i$ to the normalized parameter $b_i$. Deriving the first-order condition from the local public good utility confirms that $a_i = [\tau - \tilde{b}_i]/2 - [\tilde{\beta}/2]\sum_j g_{ij}a_j$, which matches the canonical form only with the corrected substitution.

---

### 2. Mislabeling of status quo standalone benefits as actions

**Status**: [Pending]

**Quote**:
> Note that as long as the status quo actions $\hat{\bm{b}}$ are positive, this constraint will be respected for all $C$ less than some $\hat{C}$, and so our approach will give information about the relative effects on various components for interventions that are not too large.

**Feedback**:
Readers might note that $\hat{\bm{b}}$ denotes the vector of standalone marginal benefits rather than equilibrium actions. The status quo equilibrium actions are given by $\hat{\bm{a}}^{*} = (\bm{I} - \beta\bm{G})^{-1}\hat{\bm{b}}$. It would be helpful to replace '$\hat{\bm{b}}$' with '$\hat{\bm{a}}^{*}$' or clarify that the non-negativity constraint concerns equilibrium actions derived from these standalone benefits.

---

### 3. Ambiguity in notation $\boldsymbol{b}^*$ in Proposition 4

**Status**: [Pending]

**Quote**:
> then $\mathrm{Var}(\bm{u}^{\ell}(\bm{G})\cdot\bm{b}^{*})$ is weakly decreasing in $\ell$

**Feedback**:
The section defines $\mathcal{B}$ as the random variable and $\boldsymbol{b}$ as its realization, and defines $\mathcal{B}^*$ as the optimal random variable. Readers might note that $\boldsymbol{b}^*$ inside the variance operator suggests a specific realization, which would yield zero variance, rather than the random variable distributed according to $\mathcal{B}^*$. It would be helpful to clarify that the variance is taken over $\boldsymbol{b} \sim \mathcal{B}^{*}$.

---

### 4. Unspecified ordering of eigenvectors in Proposition 4

**Status**: [Pending]

**Quote**:
> 1. Suppose the planner likes variance (i.e., $w>0$). If the game has strategic complements ($\beta>0$), then $\mathrm{Var}(\bm{u}^{\ell}(\bm{G})\cdot\bm{b}^{*})$ is weakly decreasing in $\ell$; if the game has strategic substitutes ($\beta<0$), then $\mathrm{Var}(\bm{u}^{\ell}(\bm{G})\cdot\bm{b}^{*})$ is weakly increasing in $\ell$.

**Feedback**:
The monotonicity statements presuppose that eigenvectors are indexed such that $\lambda_{1} \geq \lambda_{2} \geq \dots \geq \lambda_{n}$, since for strategic complements the coefficients $\alpha_{\ell} = (1-\beta\lambda_{\ell})^{-2}$ decrease with $\ell$ only under this ordering. It would be helpful to explicitly state this indexing convention after Proposition 4 to ensure the comparative statics are interpretable.

---

### 5. Notation inconsistency in simple intervention definition

**Status**: [Pending]

**Quote**:
> Define by $\tilde{\pmb{x}}$ the simple intervention, and note that $\tilde{x}_1 = \sqrt{C} / \hat{b}_1$ and that $\tilde{x}_{\ell} = 0$ for all $\ell > 1$.

**Feedback**:
The constraint $\sum_{\ell} \hat{\underline{b}}_{\ell}^{2} x_{\ell}^{2} \leq C$ requires the principal component coordinate $\hat{\underline{b}}_{1}$ in the denominator, since $\hat{\underline{b}}_{1}^{2}(\sqrt{C}/\hat{\underline{b}}_{1})^{2}=C$. Using $\hat{b}_1$ (the standard basis first component) would not generally satisfy the constraint. It would be helpful to write $\tilde{x}_1 = \sqrt{C} / \hat{\underline{b}}_{1}$ to maintain consistency with the transformed problem.

---

### 6. Incorrect coefficient in Example OA1 welfare expression

**Status**: [Pending]

**Quote**:
> $W(\bm{b},\bm{G})=\frac{1}{2}\,(\bm{a}^{*})^{\mathsf{T}}\,\bm{a}^{*}-n\gamma\sum_{i}a_{i}^{*},$ (OA-1)

**Feedback**:
Summing the bilateral externalities $-\gamma\sum_{j\neq i}a_j$ over all $i$ yields $-\gamma\sum_i(\sum_j a_j - a_i) = -\gamma(n-1)\sum_i a_i$. For example, with $n=2$, the externality sums to $-\gamma(a_1+a_2)$, confirming the coefficient is $(n-1)\gamma$ rather than $n\gamma$. It would be helpful to correct the expression to $W=\frac{1}{2}(\bm{a}^{*})^{\mathsf{T}}\bm{a}^{*}-(n-1)\gamma\sum_{i}a_{i}^{*}$.

---

### 7. Incorrect eigenvector normalization in Lemma OA1

**Status**: [Pending]

**Quote**:
> 2. $\lambda_{1}(\bm{G})=1$ and $u_{i}^{1}(\bm{G})=\sqrt{n}$ for all $i$

**Feedback**:
Under the orthogonal spectral decomposition $\bm{G}=\bm{U}\bm{\Lambda}\bm{U}^{\mathsf{T}}$, eigenvectors satisfy $\|\bm{u}^1\|^2 = \sum_i (u_i^1)^2 = 1$. If $u_i^1 = c$ for all $i$, then $n c^2 = 1$ implies $c = 1/\sqrt{n}$. The value $\sqrt{n}$ would yield $\|\bm{u}^1\| = n$, violating orthonormality. It would be helpful to correct the normalization to $u_{i}^{1}(\bm{G})=\frac{1}{\sqrt{n}}$.

---

### 8. Incorrect denominator in Lemma OA2 derivative

**Status**: [Pending]

**Quote**:
> $\frac{d\mu}{dx_{1}}=\frac{\hat{b}_{1}^{2}x_{1}}{\sum_{\ell=2}\frac{w_{1}^{2}\hat{b}_{1}^{2}\alpha_{\ell}^{2}}{(\mu-w_{1}\alpha_{\ell})^{3}}}$

**Feedback**:
Implicit differentiation of the budget constraint $\sum_{\ell=2}\hat{\underline{b}}_{\ell}^{2}(\frac{w_{1}\alpha_{\ell}}{\mu-w_{1}\alpha_{\ell}})^{2} = C(x_1)$ with respect to $x_1$ yields $\frac{d\mu}{dx_{1}}=\frac{\hat{\underline{b}}_{1}^{2}x_{1}}{\sum_{\ell=2}\frac{w_{1}^{2}\hat{\underline{b}}_{\ell}^{2}\alpha_{\ell}^{2}}{(\mu-w_{1}\alpha_{\ell})^{3}}}}$. The text incorrectly uses $\hat{b}_1^2$ inside the summation instead of $\hat{\underline{b}}_\ell^2$ for each term $\ell$. It would be helpful to correct the index in the denominator sum.

---

### 9. Index inconsistency in Proposition OA3 statement

**Status**: [Pending]

**Quote**:
> there exists $i^{*}$ such that $b_{i}^{*}\neq\hat{b}_{i^{*}}$ and $b_{i}^{*}=\hat{b}_{i}$ for al $i\neq i^{*}$

**Feedback**:
The condition describes a single targeted individual $i^*$, but the notation $b_i^* \neq \hat{b}_{i^*}$ mixes the free index $i$ with the specific index $i^*$. It would be helpful to correct the condition to '$b_{i^{*}}^{*}\neq\hat{b}_{i^{*}}$' to clarify that the deviation occurs for the specific individual $i^*$ while $b_i^* = \hat{b}_i$ for all other $i \neq i^*$.

---

### 10. Missing assumption on status quo for small-budget limit

**Status**: [Pending]

**Quote**:
> Consider the intervention problem (IT) with the modification that the cost function satisfies Assumption OA2. Suppose Assumptions 1 and 2 hold and the network game satisfies Property A. At the optimal intervention, if $C\to 0$ we have $\frac{r_{\ell}^{*}}{r_{\ell^{\prime}}^{*}}\to\frac{\alpha_{\ell}}{\alpha_{\ell^{\prime}}}$.

**Feedback**:
The proof relies on the expansion $\Delta(\bm{y}) = \nabla W(\hat{\bm{b}})^\mathsf{T}\bm{y} + \frac{1}{2}\bm{y}^\mathsf{T}\bm{H}(\hat{\bm{b}})\bm{y} + o(\|\bm{y}\|^2)$. For the rescaled objective $C^{-1}\Delta(C^{1/2}\check{\bm{y}})$ to converge as $C\downarrow 0$, the linear term must vanish, requiring $\nabla W(\hat{\bm{b}}) = \bm{M}^\mathsf{T}\bm{M}\hat{\bm{b}} = \bm{0}$ (i.e., $\hat{\bm{b}}=\bm{0}$ or the status quo is already optimal). Without this assumption, the optimal intervention aligns with the gradient direction. It would be helpful to add the assumption $\hat{\bm{b}}=\bm{0}$ to the proposition statement.

---
