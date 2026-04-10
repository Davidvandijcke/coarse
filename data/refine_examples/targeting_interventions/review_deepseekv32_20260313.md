# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/13/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper analyzes optimal interventions in network games where a planner can adjust agents' standalone marginal returns to maximize aggregate welfare. Using a linear-quadratic game with a symmetric network and quadratic intervention costs, it derives a closed-form solution (Theorem 1) and shows that for large budgets, the optimal intervention simplifies to targeting the principal component of the network associated with the largest eigenvalue (for strategic complements) or smallest eigenvalue (for substitutes). The analysis is extended to an incomplete information setting where the planner knows only the distribution of returns.

Below are the most important issues identified by the review panel.

**Strong Reliance on Symmetric Networks and Quadratic Costs**

The core theoretical results depend critically on the assumptions of a symmetric adjacency matrix and a quadratic intervention cost function. While these provide analytical tractability, they exclude common real-world cases such as directed networks (e.g., supply chains, citation graphs) and alternative cost structures like linear budgets or fixed costs. The extension to non-symmetric matrices via singular value decomposition is relegated to the appendix and severs the intuitive link between network eigenvalues and strategic multipliers. Similarly, the large-budget simplicity result—where interventions target a single principal component—is derived specifically for quadratic costs and may not hold under more general specifications. Readers might note that the paper's central policy prescriptions are therefore conditional on these strong functional form assumptions, limiting their direct applicability.

**Limited Robustness of Core Insights to General Payoff Structures**

The elegant characterization of optimal interventions relies on 'Property A,' where aggregate welfare is proportional to the sum of squared equilibrium actions. This property holds in canonical examples like investment or local public good games but fails in other cases with linear externalities. The extension for general externalities in the Online Appendix is complex and loses the clean ordering of principal components by strategic type unless further restrictive assumptions are imposed. Consequently, the paper's key insight—that complements target the top component and substitutes the bottom—is not a general feature of network games but a consequence of this specific welfare property. It would be helpful to more prominently discuss the empirical relevance of Property A and the conditions under which it might serve as a reasonable approximation.

**Incomplete Information Model with Unmotivated Cost Assumptions**

The extension to incomplete information, where the planner knows only the distribution of standalone returns, introduces cost functions (Assumptions 4 and 5) that lack microfoundations. Specifically, the cost for controlling variances is assumed to depend only on the trace of the covariance matrix and to be invariant under orthogonal transformations. This rotational invariance is mathematically convenient but economically unmotivated—there is no clear reason why creating variance in any orthogonal direction should be equally costly. The results on variance targeting (Proposition 4) are therefore conditional on this artificial separation between cost and benefit structures. The analysis also sidesteps the more policy-relevant scenario of two-sided incomplete information among agents, limiting its contribution to the broader literature on uncertainty in network games.

**Ambiguous Practical Relevance and Empirical Feasibility**

The paper does not address how its theoretically optimal interventions could be implemented in practice. The intervention formula requires precise knowledge of the network structure, the strategic parameter β, and the status quo benefit vector—quantities that are challenging to identify and estimate with real data. Furthermore, the thresholds for when 'simple' interventions are nearly optimal depend on spectral gaps in the network, which can be arbitrarily small in common network models (e.g., sparse, scale-free graphs). Without a discussion of the typical magnitude of these gaps in economic networks or the sensitivity of the policy to measurement error, the practical utility of the simplicity results remains uncertain. Readers might note that the omission of any bridge to empirics—such as estimation strategies or robustness to mismeasurement—limits the model's applicability to real-world policy design.

**Narrow Scope of Interventions and Treatment of Network Endogeneity**

The model frames interventions exclusively as changes to agents' standalone marginal returns, which may not encompass common policy tools like altering the network structure itself, providing public information, or imposing quantity regulations. While mathematically convenient, this limits the policy scope. Additionally, the analysis treats the network as exogenous and fixed. In many contexts, interventions that change payoffs could also induce agents to form or sever links, making the network endogenous. The optimal policy derived under exogeneity might then be suboptimal or have unintended dynamic consequences. Although a full analysis of network formation is beyond the paper's scope, a discussion of the potential biases introduced by ignoring endogeneity and the conditions for the exogenous assumption to be reasonable would clarify the boundaries of the theory's applicability.

**Potential Gaps in Proofs and Interpretation of Large-Budget Limits**

A step in the proof of Proposition 2, which compares welfare under optimal and simple interventions, relies on an inequality ('x̃₁ ≥ x₁*') that is stated without justification. If this inequality does not hold, the subsequent bound on the welfare ratio could be invalid. This matters because Proposition 2 provides key quantitative conditions for when simple interventions are nearly optimal. Separately, the 'large budget' results (Propositions 1 and 2) describe behavior as the budget tends to infinity, but the economic interpretation of an unbounded budget under quadratic costs is unclear. The convergence also depends critically on spectral gaps that may be small, leaving the practical definition of 'large' ambiguous. It would be helpful to clarify these mathematical points and discuss the finite-budget relevance of the asymptotic results.

**Status**: [Pending]

---

## Detailed Comments (16)

### 1. Incorrect network multiplier definition

**Status**: [Pending]

**Quote**:
> At the heart of our approach is a particular way to organize the spillover effects in terms of the *principal components* of the matrix of interactions. Any change in the vector of standalone (marginal) returns can be expressed in a basis of these principal components. This basis has three special properties: (a) the effects of an intervention along a principal component is proportional to the intervention, scaled by a network multiplier; (b) the “network multiplier” is an eigenvalue of the network corresponding to that principal component; (c) the principal components are orthogonal, so that the effects along various principal components can be treated separately (in a suitable sense).

**Feedback**:
Property (b) is incorrect. The network multiplier for the effect on equilibrium actions is 1/(1-βλ_ℓ), not simply λ_ℓ. This mischaracterization could mislead readers about the amplification mechanism. It would be helpful to rewrite property (b) as: 'the network multiplier is a function of the eigenvalue λ_ℓ of the network corresponding to that principal component, specifically 1/(1-βλ_ℓ).'

---

### 2. Unqualified claim about optimal intervention for substitutes

**Status**: [Pending]

**Quote**:
> In games of strategic substitutes, the order is reversed: the optimal intervention is most similar to the *last* principal component. The “higher” principal components capture the more global structure of the network: this is important for taking advantage of the aligned feedback effects arising under strategic complementarities. The “lower” principal components capture the local structure of the network: they help the planner to target the intervention so that it does not cause crowding out between adjacent neighbors: this is an important concern when actions are strategic substitutes.

**Feedback**:
The claim that the optimal intervention is most similar to the last principal component under strategic substitutes is not generally true; it depends on the sign of the welfare weight w. From Theorem 1, the similarity ratio r_ℓ* is proportional to wα_ℓ/(μ - wα_ℓ). For β<0 (substitutes), α_ℓ is increasing in λ_ℓ if w>0, making r_ℓ* largest for the largest λ_ℓ (first component). The statement holds only if w<0. Since Assumption 3 allows w>0 or w<0, the claim needs qualification. Rewrite to clarify: 'In games of strategic substitutes with w < 0, the optimal intervention is most similar to the last principal component; with w > 0, it is most similar to the first.'

---

### 3. Inconsistent norm in Assumption 3 condition

**Status**: [Pending]

**Quote**:
> If $w<0$, the planner wishes to minimize the sum of the squares of the equilibrium actions. In this case, when the budget is large enough, that is, $C\geq\|\hat{\mathbf{b}}\|^{2}$, the planner can allocate resources to ensure that individuals have a zero target action by setting $b_{i}=0$ for all $i$. It follows from the best-response equations that all individuals choose action $0$ in equilibrium, and so the planner achieves the first-best. The next assumption implies that the planner’s bliss point cannot be achieved, so that there is an interesting optimization problem:
> 
> ###### Assumption 3.
> Either $w<0$ and $C<\|\hat{\mathbf{b}}\|$, or $w>0$.

**Feedback**:
The condition for achieving first-best when w<0 is C ≥ ‖̂b‖², as the cost to set b=0 is ‖0 - ̂b‖² = ‖̂b‖². However, Assumption 3 writes C < ‖̂b‖ (without the square), which is inconsistent. This appears to be a typo. Rewrite Assumption 3 as: Either w<0 and C < ‖̂b‖², or w>0.

---

### 4. Missing closing parenthesis in equation (8)

**Status**: [Pending]

**Quote**:
> tor of standalone marginal returns exactly and implements a deterministic adjustment relative to it.
> 
> To guide our modeling of the cost of intervention, we now review the features of the distribution of $\mathcal{B}$ that matter for aggregate welfare. For network games that satisfy Property A, we can write:
> 
> $$
> \mathbb{E} \left[ W(\mathbf{b}; \mathbf{G}) \right] = w \mathbb{E} \left[ \left(\mathbf{a}^* \right)^{\top} \mathbf{a}^* \right] = w \mathbb{E} \left[ \underline{\mathbf{a}}^{\top} \underline{\mathbf{a}} \right] = w \sum_{\ell} \alpha_{\ell} \left( \mathbb{E} \left[ \underline{b}_{\ell} \right]^2 + \operatorname{Var} \left[ \underline{b}_{\ell} \right] \right. ). \tag{8}
> $$
> 
> In words, welfare is determined by the mean and variance of the realized components $\underline{b}_{\ell}$; these in turn are determined by the first and

**Feedback**:
Equation (8) has a syntax error: a left parenthesis '\left(' is closed by '\right.' (a dummy delimiter) followed by an extra ')'. This makes the expression ambiguous and typographically incorrect. The correct expression should be: $$\mathbb{E} \left[ W(\mathbf{b}; \mathbf{G}) \right] = w \mathbb{E} \left[ \left(\mathbf{a}^* \right)^{\top} \mathbf{a}^* \right] = w \mathbb{E} \left[ \underline{\mathbf{a}}^{\top} \underline{\mathbf{a}} \right] = w \sum_{\ell} \alpha_{\ell} \left( \mathbb{E} \left[ \underline{b}_{\ell} \right]^2 + \operatorname{Var} \left[ \underline{b}_{\ell} \right] \right).$$

---

### 5. Ambiguous notation for variance in Proposition 4

**Status**: [Pending]

**Quote**:
> 1. Suppose the planner likes variance (i.e., $w>0$). If the game has strategic complements ($\beta>0$), then $\operatorname{Var}(\mathbf{u}^{\ell}(\mathbf{G})\cdot\mathbf{b}^{*})$ is weakly decreasing in $\ell$; if the game has strategic substitutes ($\beta<0$), then $\operatorname{Var}(\mathbf{u}^{\ell}(\mathbf{G})\cdot\mathbf{b}^{*})$ is weakly increasing in $\ell$.
> 2. Suppose the planner dislikes variance (i.e., $w<0$). If the game has strategic complements ($\beta>0$), then $\operatorname{Var}(\mathbf{u}^{\ell}(\mathbf{G})\cdot\mathbf{b}^{*})$ is weakly increasing in $\ell$; if the game has strategic substitutes ($\beta<0$), then $\operatorname{Var}(\mathbf{u}^{\ell}(\mathbf{G})\cdot\mathbf{b}^{*})$ is weakly decreasing in $\ell$.

**Feedback**:
The notation Var(u^ℓ(G)·b*) is ambiguous without specifying the ordering of eigenvalues. The eigenvectors are ordered according to eigenvalues λ_ℓ from largest to smallest. The proposition's monotonicity claims depend on this ordering. To avoid confusion, add a clarifying phrase: 'where the eigenvectors are ordered according to the corresponding eigenvalues λ_ℓ from largest to smallest.'

---

### 6. Misattribution of positivity to genericity

**Status**: [Pending]

**Quote**:
> Note that, for all $\ell$, $\alpha_{\ell}$ are well-defined (by Assumption 1) and strictly positive (by genericity of $\mathbf{G}$). This has two implications.²⁶

**Feedback**:
The claim that α_ℓ are strictly positive 'by genericity of G' is incorrect. Positivity follows from Assumption 2 (spectral radius of βG less than 1), which ensures 1-βλ_ℓ > 0, so α_ℓ = 1/(1-βλ_ℓ)² > 0. Genericity (distinct eigenvalues) is irrelevant for positivity. This misattribution could confuse readers. Rewrite the sentence as: 'Note that, for all ℓ, α_ℓ are well-defined and strictly positive (by Assumption 2).'

---

### 7. Insufficient justification for inequality in welfare ratio step

**Status**: [Pending]

**Quote**:
> &\leq 1 + \frac{\sum_{\ell \neq 1} \hat{\underline{b}}_{\ell}^{2} \alpha_{\ell} x_{\ell}^{*} (x_{\ell}^{*} + 2)}{\hat{\underline{b}}_{1}^{2} \alpha_{1} \tilde{x}_{1}^{2}} \quad \text{summands in denominator are positive}

**Feedback**:
The justification 'summands in denominator are positive' is insufficient to justify the inequality. The step replaces the denominator with a smaller quantity, since ẍ̃₁(ẍ̃₁+2) > ẍ̃₁² and ∑_ℓ α_ℓ ẍ̂_ℓ² > 0. The inequality direction is correct, but the reasoning should be explicit. Rewrite the justification as: 'since ẍ̃₁(ẍ̃₁+2) > ẍ̃₁² and ∑_ℓ α_ℓ ẍ̂_ℓ² > 0, the denominator on the left is larger than ẍ̂₁² α₁ ẍ̃₁², so the fraction is smaller.'

---

### 8. Incorrect coefficient in aggregate welfare expression for Example OA1

**Status**: [Pending]

**Quote**:
> It can be checked that the aggregate equilibrium welfare is:
> 
> $W(\mathbf{b},\mathbf{G})=\frac{1}{2}\,(\mathbf{a}^{*})^{\mathsf{T}}\,\mathbf{a}^{*}-n\gamma\sum_{i}a_{i}^{*},$ (OA-1)
> 
> with $\mathbf{a}^{*}$ given by expression (3).

**Feedback**:
The coefficient on the linear term is incorrect. From the utility function U_i = Û_i - γ ∑_{j≠i} a_j, summing over i gives ∑_i ∑_{j≠i} a_j = (n-1) ∑_i a_i. Therefore, the second term should be γ (n-1) ∑_i a_i^*, not nγ ∑_i a_i^*. Rewrite equation (OA-1) as: $W(\mathbf{b},\mathbf{G}) = \frac{1}{2} (\mathbf{a}^{*})^{\mathsf{T}} \mathbf{a}^{*} - \gamma (n-1) \sum_i a_i^{*}$.

---

### 9. Inconsistent definition of w2 in Lemma OA1

**Status**: [Pending]

**Quote**:
> Using part 1 of Lemma OA1, and that individuals play an equilibrium (actions satisfy expression (3)), we obtain:
> 
> $W(\mathbf{b},\mathbf{G})=w_{1}\left(\mathbf{a}^{*}\right)^{\mathsf{T}}\mathbf{a}^{*}+\frac{w_{2}}{n}\left(\sum_{i}a_{i}^{*}\right)^{2}+\frac{w_{3}}{\sqrt{n}}\sum_{i}a_{i}^{*},$
> 
> with:
> 
> $w_{1}$ $=$ $1+m_{2}+m_{5}$
> $w_{2}$ $=$ $n(m_4+m_5)$
> $w_{3}$ $=$ $\sqrt{n}[m_{1}+(n-1)m_{3}].$

**Feedback**:
The expression for w2 conflicts with an earlier definition. Collecting coefficients from the externality terms yields w2 = n m4 + (n-2) m5, not n(m4+m5). The earlier definition w2 = n m4 - m5 also appears incorrect. Rewrite the definitions to be consistent with the derived welfare expression: w1 = 1+m2+m5, w2 = n m4 + (n-2) m5, w3 = √n [m1+(n-1)m3].

---

### 10. Sign error in condition for x1* positivity in Theorem OA1

**Status**: [Pending]

**Quote**:
> b. $x_{1}^{*} > 0$ if and only if $w_{1} + w_{2} + \frac{w_{3}}{2\sqrt{\alpha_{1}\hat{b}_{1}}} > 0$.

**Feedback**:
The condition contains a typo: the denominator under w3 should be 2√α₁ ẍ̂₁, not 2√(α₁ẍ̂₁). From part 1, x1* = α₁/(μ - (w1+w2)α₁) [w1+w2 + w3/(2√α₁ ẍ̂₁)]. The positivity condition should match this. Rewrite part 2b as: '$x_{1}^{*} > 0$ if and only if $w_{1} + w_{2} + \frac{w_{3}}{2\sqrt{\alpha_{1}}\hat{\underline{b}}_{1}} > 0$.'

---

### 11. Incomplete proof of Lemma OA3 uniform convergence

**Status**: [Pending]

**Quote**:
> ###### Lemma OA3.
> Under the conditions of Assumption OA2, on any compact set the function $C^{-1}\kappa(C^{1/2}\mathbf{z})$ converges uniformly to $k\|\mathbf{z}\|^{2}$, as $C\downarrow 0$, where $k>0$ is some constant. We call the limit $G$.
> 
> ###### Proof.
> Consider the Taylor expansion of $\kappa$ around $\mathbf{0}$. We will now study its properties under parts (2) to (5) of Assumption OA2. (5) ensures that the Taylor expansion exists. Local separability (4) says that there are no terms of the form $y_{i}y_{j}$. Non-negativity (3) ($\kappa$ is nonnegative and $\kappa(\mathbf{0})=0$) implies that all first-order terms are zero. Also, (5) says that terms of the form $y_{i}^{2}$ must have positive coefficients, and symmetry (2) says that their coefficients must all be the same. ∎

**Feedback**:
The proof only analyzes the Taylor expansion structure but does not demonstrate uniform convergence. To show uniform convergence, one must bound the remainder term uniformly on compact sets. Add a rigorous argument: 'By Taylor's theorem, κ(y) = k ∑_i y_i² + R(y) with R(y)/||y||² → 0 as y→0. For any compact K, sup_{z∈K} |C⁻¹ R(C^{1/2} z)| = sup_{z∈K} (||z||² · |R(C^{1/2} z)|/(C ||z||²)) ≤ (sup_{z∈K} ||z||²) · sup_{||y|| ≤ C^{1/2} M} |R(y)|/||y||² → 0, where M = sup_{z∈K} ||z||. Hence C⁻¹ κ(C^{1/2} z) converges uniformly to k ||z||² on K.'

---

### 12. Logical gap in proof of Proposition OA3

**Status**: [Pending]

**Quote**:
> Define $W(\mathbf{b})=\mathbf{a}(\mathbf{b})^{\mathsf{T}}\mathbf{a}(\mathbf{b})$. Let $F$ be the set of *feasible* $\mathbf{b}$, those satisfying the budget constraint $K(\mathbf{b};\hat{\mathbf{b}})\leq C$. Suppose the conclusion does not hold and let $\mathbf{b}^{*}$ be the optimum, with $W^{*}=W(\mathbf{b}^{*})$. Then, because by hypothesis the optimum is not at an extreme point, $F$ contains a line segment $L$ such that $\mathbf{b}^{*}$ is in the interior of $L$.
> 
> Now restrict attention to a plane $P$ containing this $L$ and the origin. Note that $L$ is contained in a convex set
> 
> $E=\{\mathbf{b}:W(\mathbf{b})\leq W^{*}\}.$
> 
> The point $\mathbf{b^{*}}$ is contained in the interior of $L$; thus $\mathbf{b^{*}}$ is in the interior of $E$. On the other hand, $\mathbf{b^{*}}$ must be on the (elliptical) boundary of $E$ because $W$ is strictly increasing in each component (by irreducibility of the network) and continuous. This is a contradiction. ∎

**Feedback**:
The contradiction argument is incomplete. Since b* maximizes W over F, W must be constant on L (otherwise moving along L would increase W). Thus L lies in the boundary of E, not its interior. The contradiction arises because W is a strictly convex quadratic function (positive definite Hessian), so its level sets are strictly convex, which cannot contain a nontrivial line segment. Rewrite the relevant step: 'Since b* maximizes W over F, W is constant on L, so L ⊆ {b: W(b) = W*}, the boundary of E. But W is strictly convex, contradicting the existence of a nontrivial line segment in the boundary.'

---

### 13. Missing derivation for equivalence in linear cost problem

**Status**: [Pending]

**Quote**:
> It is easy to verify that the solution to problem IT-Linear Cost is:
> 
> $i^{*}=\operatorname*{argmax}_{i}\left\{\mathbf{a}(\hat{\mathbf{b}}+C\mathbf{1}_{i})^{\mathsf{T}}\mathbf{a}(\hat{\mathbf{b}}+C\mathbf{1}_{i})-\mathbf{a}(\hat{\mathbf{b}})^{\mathsf{T}}\mathbf{a}(\hat{\mathbf{b}})\right\}.$
> 
> This is equivalent to
> 
> $i^{*}=\operatorname*{argmax}_{i}\left\{C\|\mathbf{a}(\mathbf{1}_{i})\|\left[2\|\mathbf{a}(\hat{\mathbf{b}})\|\rho(\mathbf{a}(\mathbf{1}_{i}),\mathbf{a}(\hat{\mathbf{b}}))+C\|\mathbf{a}(\mathbf{1}_{i})\|\right]\right\}.$ (OA-3)

**Feedback**:
The equivalence is not immediately obvious; it requires algebraic manipulation using the linearity of a(·). For clarity, add the intermediate derivation: 'Using linearity, a(̂b + C 1_i) = a(̂b) + C a(1_i). Then the objective becomes 2C a(̂b)^⊤ a(1_i) + C² ||a(1_i)||² = C ||a(1_i)|| [2 ||a(̂b)|| ρ(a(1_i), a(̂b)) + C ||a(1_i)||].'

---

### 14. Undefined notation in welfare centrality expression

**Status**: [Pending]

**Quote**:
> It is convenient to express the welfare centrality of individual $i$ in terms of principal components of $\mathbf{G}$. Note that
> 
> $\|\mathbf{a}(\mathbf{1}_{i})\|=\|\underline{\mathbf{a}}(\underline{\mathbf{1}}_{i})\|=\sqrt{\sum_{\ell}\alpha_{\ell}(u_{i}^{\ell})^{2}}.$

**Feedback**:
The notation ȧ and 1̲_i is not defined in this section. Readers may be confused by the sudden appearance of underlined symbols. Add a brief explanation: 'Let U be the orthogonal matrix of eigenvectors of G. In the principal component basis, a(1_i) has coordinates U^⊤ a(1_i) = (α_1^{1/2} u_i^1, …, α_n^{1/2} u_i^n). Hence its squared norm is ∑_ℓ α_ℓ (u_i^ℓ)^2.'

---

### 15. Incorrect mapping to standard best-response structure in extension example

**Status**: [Pending]

**Quote**:
> By defining $\beta = \frac{\tilde{\beta} + \gamma}{1 + \gamma}$ and $\mathbf{b} = \frac{1}{1+\gamma}\tilde{\mathbf{b}}$, we obtain a best-response structure exactly as in condition (2).

**Feedback**:
The mapping appears inconsistent. Substituting the definitions into the first-order condition yields a_i = (1+γ) b_i + β ∑_j g_{ij} a_j, which does not match condition (2) (a_i = b_i + β ∑_j g_{ij} a_j) unless γ=0. To match condition (2), one should set b_i = ẍ̃_i. Clarify the intended mapping: either set b = ẍ̃ and keep the factor (1+γ) on the left, or adjust the definition of b. Rewrite as: 'By defining β = (ẍ̃+γ)/(1+γ) and b = ẍ̃, we obtain a_i = b_i + β ∑_j g_{ij} a_j.'

---

### 16. Inconsistent externality term argument in general form

**Status**: [Pending]

**Quote**:
> Recall that player $i$’s utility for action profile $\mathbf{a}$ is
> 
> $U_{i}(\mathbf{a},\mathbf{G})=\hat{U}_{i}(\mathbf{a},\mathbf{G})+P_{i}(\mathbf{a}_{-i},\mathbf{G},\mathbf{b}),$
> 
> where $\hat{U}_{i}(\mathbf{a},\mathbf{G})=a_{i}(b_{i}+\beta \sum_{j}g_{ij}a_{j})-\frac{1}{2}a_{i}^{2}$.
> 
> At an equilibrium $\mathbf{a}^{*}$, it can be checked that $\sum_{i}\hat{U}_{i}(\mathbf{a}^{*},\mathbf{G}) \propto (\mathbf{a}^{*})^{\mathsf{T}}\,\mathbf{a}^{*}$. Therefore, a sufficient condition for Property A to be satisfied is that $\sum_{i}P_{i}(\mathbf{a}_{-i}^{*},\mathbf{G},\mathbf{b})$ is also proportional to $(\mathbf{a}^{*})^{\mathsf{T}}\,\mathbf{a}^{*}$.

**Feedback**:
The definition of P_i includes b as an argument, but the subsequent general form for P_i omits b. This creates an inconsistency. If P_i is meant to be independent of b, the initial definition should not include b. Alternatively, the general form should include b, or it should be stated that the coefficients m_k may depend on b. Add a sentence: 'Here, the coefficients m_1, …, m_5 may depend on b and G.'

---
