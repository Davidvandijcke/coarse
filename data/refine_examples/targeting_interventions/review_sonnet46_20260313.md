# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/13/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper studies a planner's optimal intervention problem in network games with linear-quadratic payoffs, where the planner shifts agents' standalone returns subject to a quadratic budget constraint. The main methodological contribution is a principal-components decomposition of the intervention problem, which yields closed-form similarity-ratio characterizations of the optimal policy (Theorem 1) and ordering results linking the targeted eigenvectors to the nature of strategic interaction (Corollary 1). The paper further establishes large-budget 'simplicity' results (Propositions 1–2) showing that the optimal intervention concentrates on a single eigenvector, and extends the framework to incomplete information about the status-quo vector (Section 5) and asymmetric networks (Online Appendix).

Below are the most important issues identified by the review panel.

**Property A Is Load-Bearing for All Main Results but Its Scope and Limitations Are Understated**

Theorem 1, Corollary 1, and Propositions 1–2 all depend critically on Property A, which requires aggregate equilibrium welfare to be proportional to (a*)ᵀa*. This condition is what allows the welfare function to diagonalize cleanly in the principal-component basis, making the Lagrangian separable and the similarity-ratio ordering tractable. Without it, cross-component terms in welfare do not vanish and the monotone ordering of Corollary 1 need not hold. The Online Appendix (Section OA3.1) shows that relaxing Property A requires the additional Assumption OA1 (constant row sums, a doubly-stochastic-like condition), which is itself quite restrictive and not satisfied by sparse, scale-free, or heterogeneous-degree networks that are common in empirical work. Under OA1, the characterization (Theorem OA1) involves multiple cases depending on parameter signs, and the large-budget limit can converge to either the first or second component. The main text presents Property A as a 'technically convenient property' satisfied by two canonical examples, but readers might note that the generality claimed in the introduction is partially overstated. It would be helpful to state explicitly in the main text that Corollary 1's monotone ordering is specific to Property A environments, to characterize more precisely which economically relevant games satisfy both Property A and Assumption OA1, and to discuss whether the qualitative results survive when neither condition holds.

**Theorem 1's Change-of-Variables Breaks Down When Any Status-Quo Principal-Component Projection Vanishes**

The proof of Theorem 1 performs the change of variables x_ℓ = y_ℓ / b̂_ℓ, which requires b̂_ℓ ≠ 0 for every principal-component projection of the status-quo vector. The proof acknowledges this only in passing ('We take a generic b̂ such that b̂_ℓ ≠ 0 for all ℓ'), but this condition is neither stated as a formal assumption in the theorem statement nor discussed in the main text. This is not merely a knife-edge case: whenever b̂ lies in the span of a strict subset of eigenvectors—for instance, when standalone returns are uniform on a regular graph, making b̂ proportional to the all-ones vector and hence orthogonal to all other eigenvectors—some b̂_ℓ equal zero, the change of variables is undefined, and the similarity-ratio formula in equation (5) takes a 0/0 form. The same issue propagates to Proposition 1, Part 2, where the large-budget limit ρ(y*, u¹(G)) → 1 requires ρ(b̂, u¹(G)) ≠ 0; if b̂ is orthogonal to the first eigenvector, the numerator of x₁* is zero for all C and the limit fails entirely. It would be helpful to add 'b̂_ℓ ≠ 0 for all ℓ' as an explicit assumption in Theorem 1 and Proposition 1, provide a separate characterization of the optimal intervention for degenerate cases, and verify that the numerical examples in Figures 2–3 do not approach this boundary.

**The Large-Budget Simplicity Threshold Scales Poorly with Network Structure, Limiting the Policy Recommendation**

Proposition 2 gives a sufficient condition for the simple intervention to be ε-optimal: C > (2‖b̂‖²/ε)(α₂/(α₁ − α₂))². The term α₂/(α₁ − α₂) diverges as the spectral gap λ₁ − λ₂ closes, and ‖b̂‖² grows with n when standalone returns are bounded away from zero. For large networks with small spectral gaps—community-structured or near-bipartite networks, which are empirically common—the budget required for simplicity may be astronomically large relative to any realistic intervention. The paper discusses the role of the spectral gap qualitatively (Section 4.2 and Figure 3) but does not characterize how the threshold scales with n or with typical network parameters, nor does it provide a lower bound on the welfare loss from using the simple intervention below the threshold. The ratio W*/Wˢ can be arbitrarily large for near-degenerate spectral gaps, meaning the policy recommendation to use eigenvector-centrality targeting could perform arbitrarily poorly for any fixed budget. Additionally, the welfare ratio bound in Proposition 2 implicitly assumes Wˢ > 0; if the status-quo welfare is negative or zero, the multiplicative bound is meaningless, and restating the approximation as an additive gap W* − Wˢ would be more robust. It would be helpful to provide an order-of-magnitude scaling analysis of the threshold as a function of network size and density, and either a two-sided bound on W*/Wˢ or an explicit example quantifying the welfare loss in networks with small spectral gaps.

**The Incomplete-Information Section Leaves the Equilibrium Concept, Timing, and Key Assumptions Implicit**

Section 5 studies a setting where the planner does not know b̂ but agents play a complete-information game after observing the realized b (footnote 23). While this timing is internally consistent, the equilibrium concept for the planner's problem (IT-G) is never formally defined: it is unclear whether the planner commits to a mechanism before or after the realization is observed by agents, and whether agents' strategies can depend on the planner's announced policy. Proposition 3 reduces the problem to the deterministic case by linearity of the objective in the mean, which is correct, but its proof implicitly assumes that variance terms drop out of the optimization because the cost function (Assumption 4) does not penalize variance—a condition that should be stated explicitly in the proposition rather than left implicit. Proposition 4 requires Assumption 5 (rotational symmetry of the cost function), which rules out the economically natural case of individual-specific budget limits. Furthermore, Assumption 2 guarantees equilibrium uniqueness for any fixed b, but the paper does not verify that the set of realizations for which this might fail has measure zero under the planner's chosen distribution. It would be helpful to provide a formal definition of the equilibrium concept, a clear statement of the timing, an explicit statement of the variance-neutrality condition in Proposition 3, and a discussion of why Assumption 5's rotational symmetry is appropriate for the described applications.

**The SVD Extension for Asymmetric Networks Contains an Apparent Notational Error and an Unverified Separability Claim**

In Online Appendix Section OA3.2, the paper extends the analysis to non-symmetric G using the SVD M = USVᵀ of M = I − βG. The equilibrium condition is stated as ā_ℓ* = (1/s_ℓ) b_ℓ², where the exponent '2' appears to be a typographical error: from Ma* = b, multiplying on the left by Uᵀ gives S(Vᵀa*) = Uᵀb, so the correct expression should be ā_ℓ* = b̄_ℓ / s_ℓ. As written, the formula equates an action to the square of a projection, which is dimensionally inconsistent and would make the welfare expression a fourth-order function of b, breaking the subsequent analysis. Beyond this notational issue, there is a deeper concern: the cost function ‖y‖² decomposes in the U-basis (since U is orthogonal), while the welfare objective w(a*)ᵀa* decomposes in the V-basis. Because U ≠ V generically for asymmetric G, the cost and welfare do not share the same orthogonal basis, and the separability argument that drives Theorem 1 does not go through without additional algebraic steps showing that cross-basis terms vanish. The paper does not provide these steps. It would be helpful to correct the displayed equation, verify the assignment of left and right singular vectors throughout OA3.2, and either supply the missing separability argument or acknowledge that the extension requires a modified cost function measured in the U-basis for the analogy to hold exactly.

**The Contribution Relative to Closest Antecedents Is Not Formally Delineated in the Main Text**

The paper claims its main contribution is the principal-components decomposition methodology, distinguishing itself from Demange (2017) and Belhaj–Deroïan (2018) primarily through the quadratic cost function and welfare objective. However, the main text does not provide a formal comparison showing which results are genuinely new relative to these papers and which are recoverable from their frameworks by a change of objective. Demange (2017) also uses eigenvalue-based multipliers for optimal targeting under complementarities, and the ordering result of Corollary 1—that higher principal components receive more weight under complements—has a close analogue in her centrality-multiplier characterization. The key substantive distinction, between Bonacich centrality and eigenvector centrality targets, is discussed in Online Appendix OA2.1 but is not connected to a formal comparison theorem in the main text. Similarly, the local public good example (Example 2) involves strategic substitutes with w < 0, and Corollary 1 implies the planner should target the first principal component—not the last—which appears to contradict the paper's general narrative that substitutes games call for last-component targeting; this case is not worked through explicitly to confirm the correct ordering. It would be helpful to include a proposition or remark in the main text that precisely delineates which results are new relative to the closest competitors, and to work through Example 2 explicitly to reconcile the ordering result with the stated intuition for the substitutes case.

**Status**: [Pending]

---

## Detailed Comments (23)

### 1. Self-referential change-of-variables in Example 2

**Status**: [Pending]

**Quote**:
> Performing the change of variables $b_{i}=[\tau-b_{i}]/2$ and $\beta=-\tilde{\beta}/2$ (with the status quo equal to $\hat{b}_{i}=[\tau-\tilde{b}_{i}]/2$) yields a best-response structure exactly as in condition (2).

**Feedback**:
The change-of-variables formula is self-referential: $b_i = (\tau - b_i)/2$ implies $b_i = \tau/3$, a fixed constant rather than a substitution. The status-quo formula immediately following uses $\tilde{b}_i$ (the original endowment parameter), confirming that the intended substitution is $b_i = (\tau - \tilde{b}_i)/2$. Rewrite the first formula as $b_{i}=[\tau-\tilde{b}_{i}]/2$.

---

### 2. PCA ordering by explained variance corresponds to absolute eigenvalue, not signed eigenvalue

**Status**: [Pending]

**Quote**:
> A well-known result is that the eigenvectors of $\bm{G}$ that diagonalize the matrix (i.e., the columns of $\bm{U}$) are indeed the principal components of $\bm{G}$ in this sense.

**Feedback**:
Standard PCA of a data matrix $X$ finds directions maximizing explained variance via eigenvectors of $X^\top X$. Here the data matrix is $G$, so PCA yields eigenvectors of $G^\top G = G^2$ (since $G$ is symmetric), with eigenvalues $\lambda_\ell^2$ ordered by $|\lambda_\ell|$. The eigenvectors of $G^2$ coincide with those of $G$, so the conclusion is correct, but the ordering differs: when $|\lambda_n| > \lambda_1$ (e.g., near-bipartite networks), the first principal component in the PCA sense is the last eigenvector under the paper's signed ordering. It would be helpful to note explicitly that the paper's ordering convention is by signed eigenvalue, not by PCA-explained variance, and that these coincide only when all eigenvalues are non-negative.

---

### 3. Assumption 3 missing squared norm in budget threshold

**Status**: [Pending]

**Quote**:
> Assumption 3.
> 
> Either $w<0$ and $C<\|\hat{\bm{b}}\|$, or $w>0$.

**Feedback**:
The preceding paragraph states that the planner achieves first-best when $C \geq \|\hat{\bm{b}}\|^2$ (squared norm). Assumption 3 is meant to exclude this first-best case, so it should require $C < \|\hat{\bm{b}}\|^2$. As a concrete check: if $\|\hat{\bm{b}}\| = 2$, first-best is achievable for $C \geq 4$, but Assumption 3 as written only excludes $C \geq 2$, leaving $2 \leq C < 4$ unaddressed. The Appendix proof also uses $\sum_\ell \hat{\underline{b}}_\ell^2 > C$, i.e., $\|\hat{\bm{b}}\|^2 > C$, confirming the squared norm is correct. Rewrite as $C < \|\hat{\bm{b}}\|^{2}$.

---

### 4. Alpha formula missing square in discussion paragraph

**Status**: [Pending]

**Quote**:
> The second factor, $\frac{w\alpha_{\ell}}{\mu-w\alpha_{\ell}}$, is determined by two quantities: the eigenvalue corresponding to $\bm{u}^{\ell}(\bm{G})$ (via $\alpha_{\ell}=\frac{1}{1-\beta\lambda_{\ell}}$), and the budget $C$ (via the shadow price $\mu$).

**Feedback**:
The theorem statement and formal definition give $\alpha_\ell = 1/(1-\beta\lambda_\ell)^2$. The discussion paragraph reproduces this as $\alpha_\ell = 1/(1-\beta\lambda_\ell)$, omitting the square. With $\beta=0.5$ and $\lambda_\ell=1$, the correct value is $\alpha_\ell = 4$ while the formula as written gives $2$. The squared form is essential because it arises from squaring the equilibrium condition $a_\ell^* = \sqrt{\alpha_\ell}\,\underline{b}_\ell$, so that $W = w\sum_\ell \alpha_\ell \underline{b}_\ell^2$. Rewrite as $\alpha_{\ell}=\frac{1}{(1-\beta\lambda_{\ell})^{2}}$.

---

### 5. Lagrangian missing squared factor on status-quo projection

**Status**: [Pending]

**Quote**:
> $\mathcal{L}=w\sum_{\ell}\alpha_{\ell}(1+x_{\ell})^{2}\hat{\underline{b}}_{\ell}+\mu\left[C-\sum_{\ell}\hat{\underline{b}}_{\ell}^{2}x_{\ell}^{2}\right].$

**Feedback**:
After the change of variables $x_\ell = y_\ell / \hat{b}_\ell$, the objective becomes $w\sum_\ell \alpha_\ell \underline{b}_\ell^2 = w\sum_\ell \alpha_\ell \hat{b}_\ell^2(1+x_\ell)^2$. The first sum in the Lagrangian should therefore carry $\hat{\underline{b}}_\ell^2$ (squared), not $\hat{\underline{b}}_\ell$. The first-order condition (10) is nevertheless correct since differentiating the corrected Lagrangian with respect to $x_\ell$ yields $2\hat{b}_\ell^2[w\alpha_\ell(1+x_\ell^*) - \mu x_\ell^*] = 0$, so the error is confined to the display of the Lagrangian itself. Rewrite the first-term factor as $\hat{\underline{b}}_{\ell}^{2}$.

---

### 6. Proposition 1 large-budget limit requires nonzero status-quo projection on leading eigenvector

**Status**: [Pending]

**Quote**:
> As $C\to\infty$, in the optimal intervention
> 
> 1. If the game has the strategic complements property, $\beta>0$, then the similarity of $\bm{y}^{*}$ and the first principal component of the network tends to $1$, $\rho(\bm{y^{*}},\bm{u}^{1}(\bm{G}))\to 1$.

**Feedback**:
From the proof structure, $y_\ell = x_\ell^* \hat{b}_\ell$, so $y_1 = x_1^* \hat{b}_1$ where $\hat{b}_1 = \langle \hat{b}, u^1(G)\rangle$. For $\rho(y^*, u^1) \to 1$, component $y_1$ must dominate the norm of $y^*$, which requires $\hat{b}_1 \neq 0$. If $\hat{b}_1 = 0$, then $y_1 = 0$ for all $C$ and the cosine similarity with $u^1$ cannot tend to 1 regardless of budget. An analogous condition $\hat{b}_n \neq 0$ is needed for Part 2(ii). Neither condition appears in the statement of Proposition 1. These should be added as explicit hypotheses, consistent with the genericity condition already flagged in the proof.

---

### 7. Sign inconsistency in Proposition 2 Part 2 denominator

**Status**: [Pending]

**Quote**:
> If the game has the strategic substitutes property, $\beta<0$, then for any $\epsilon>0$, if $C>\frac{2\|\hat{\bm{b}}\|^{2}}{\epsilon}\left(\frac{\alpha_{n-1}}{\alpha_{n}-\alpha_{n-1}}\right)^{2}$, then $W^{*}/W^{s}<1+\epsilon$

**Feedback**:
When $\beta < 0$, $\alpha_\ell = (1-\beta\lambda_\ell)^{-2}$. Since $\lambda_n < \lambda_{n-1}$ and $\beta < 0$, we have $-\beta\lambda_n > -\beta\lambda_{n-1}$, so $1-\beta\lambda_n > 1-\beta\lambda_{n-1}$, giving $\alpha_n < \alpha_{n-1}$ and hence $\alpha_n - \alpha_{n-1} < 0$. The discussion paragraph immediately following writes the analogous term as $\alpha_{n-1}/(\alpha_{n-1}-\alpha_{n})$ with a positive denominator. The proposition's denominator $\alpha_n - \alpha_{n-1}$ is the negative of the discussion's denominator. While squaring makes the final expression positive either way, the proposition is internally inconsistent with the discussion and with the complements case where $\alpha_1 - \alpha_2 > 0$. Rewrite as $(\alpha_{n-1}/(\alpha_{n-1}-\alpha_{n}))^{2}$.

---

### 8. Welfare ratio bound requires positive simple-intervention welfare

**Status**: [Pending]

**Quote**:
> n the game has the strategic complements property ($\beta > 0$),
>     \item $b_i - \hat{b}_i = \sqrt{C} u_i^n$ when the game has the strategic substitutes property ($\beta < 0$).
> \end{itemize}
> 
> Let $W^{*}$ be the aggregate utility under the optimal intervention, and let $W^{s}$ be the aggregate utility under the simple intervention.
> 
> ###### Proposition 2.
> 
> Suppose $w>0$, Assumptions 1 and 2 hold, and the network game satisfies Property A.
> 
> 1. If the game has the strategic complements property, $\beta>0$, then for any $\epsilon>0$, if $C>\frac{2\|\hat{\bm{b}}\|^{2}}{\epsilon}\left(\frac{\alpha_{2}}{\alpha_{1}-\alpha_{2}}\right)^{2}$, then $W^{*}/W^{s}<1+\epsilon$ and $\rho

**Feedback**:
The bound $W^*/W^s < 1+\epsilon$ is a multiplicative ratio. For it to be meaningful, $W^s$ must be strictly positive. The proposition assumes $w > 0$ but does not verify $W^s > 0$; since $W^s$ depends on $\hat{b}$ and the network, it is not guaranteed positive under the stated assumptions alone. If $W^s \leq 0$, the ratio is either undefined or the inequality carries no approximation content. It would be helpful to add an explicit condition ensuring $W^s > 0$, or to restate the approximation as the additive bound $W^* - W^s < \epsilon \cdot |W^s|$ with a note that this requires $W^s > 0$.

---

### 9. Proof of Proposition 2 uses W superscript 2 instead of W superscript s in conclusion

**Status**: [Pending]

**Quote**:
> is sufficient to establish that $\frac{W^{*}}{W^{2}}<1+\epsilon$. The proof for the case of strategic substitutes follows the same steps; the only difference is that we use $\alpha_{n}$ instead of $\alpha_{1}$ and $\alpha_{n-1}$ instead of $\alpha_{2}$.

**Feedback**:
Throughout the proof of Proposition 2, the welfare under the simple intervention is consistently denoted $W^s$. The conclusion writes $W^*/W^2$, where the superscript 2 is a typographical error for s. The main-text statement of Proposition 2 also refers to $W^s$. Rewrite as $W^*/W^s < 1+\epsilon$.

---

### 10. Lemma 1 proof contains tautological justification

**Status**: [Pending]

**Quote**:
> The next equality follows by noticing that $\|\hat{\bm{b}}\|^{2}=\|\hat{\bm{b}}\|^{2}$. The final inequality follows because, from the facts that $\mu>w\alpha_{1}$ and that $\alpha_{1}>\alpha_{2}>\cdots>\alpha_{n}$, we can deduce that for each $\ell>1$

**Feedback**:
The sentence stating that the next equality follows by noticing $\|\hat{b}\|^2 = \|\hat{b}\|^2$ is a tautology providing no logical justification. The step in question rewrites $\|\hat{b}\|^2$ as $\sum_\ell \hat{\underline{b}}_\ell^2$, which follows from the Parseval identity: since $U$ is orthogonal, $\|\hat{b}\|^2 = \|U^\top \hat{b}\|^2 = \sum_\ell \hat{\underline{b}}_\ell^2$. Rewrite as: The next equality follows by noticing that $\|\hat{b}\|^2 = \sum_\ell \hat{\underline{b}}_\ell^2$, which holds because $U$ is orthogonal (Parseval identity).

---

### 11. Covariance matrix equation stated for wrong variable in Proposition 4 proof

**Status**: [Pending]

**Quote**:
> $$
> \boldsymbol {\Sigma} _ {\mathcal {B} ^ {* *}} = \boldsymbol {P} \boldsymbol {\Sigma} _ {\mathcal {B} ^ {*}} \boldsymbol {P} ^ {\top}
> $$
> 
> and so  $\mathrm{Var}(\underline{b}_k^{**}) = \mathrm{Var}(\underline{b}_k^*)$  for all  $k\notin \{\ell ,\ell '\}$

**Feedback**:
Since $\mathcal{B}^{**} = O\mathcal{B}^*$ with $O = UPU^\top$, the original covariance transforms as $\Sigma_{\mathcal{B}^{**}} = O\Sigma_{\mathcal{B}^*}O^\top = UPU^\top \Sigma_{\mathcal{B}^*} UP^\top U^\top$, which does not equal $P\Sigma_{\mathcal{B}^*}P^\top$. The correct statement is for the rotated covariance in the eigenvector basis: $\Sigma_{\underline{\mathcal{B}}^{**}} = U^\top \Sigma_{\mathcal{B}^{**}} U = P(U^\top \Sigma_{\mathcal{B}^*} U)P^\top = P\Sigma_{\underline{\mathcal{B}}^*}P^\top$. It is this rotated covariance whose diagonal entries are permuted by $P$, which is what the proof needs to conclude that $\text{Var}(\underline{b}_k^{**}) = \text{Var}(\underline{b}_k^*)$ for $k$ not in the set containing $\ell$ and $\ell'$. Rewrite the displayed equation using the rotated covariance notation throughout.

---

### 12. Self-contradictory chain of equalities in Proposition 4 contradiction argument

**Status**: [Pending]

**Quote**:
> $\mathrm{Var}(\underline{b}_{\ell}^{*}) = \mathrm{Var}(\underline{b}_{\ell '}^{*}) > \mathrm{Var}(\underline{b}_{\ell '}^{**}) = \mathrm{Var}(\underline{b}_{\ell}^{*})$  Since  $\alpha_{\ell} > \alpha_{\ell '}$  intervention  $\mathcal{B}^{**}$  does strictly better than  $\mathcal{B}^*$ , a contradiction to our initial hypothesis that  $\mathcal{B}^*$  was optimal.

**Feedback**:
The displayed chain asserts A = B > C = A, which reduces to A > A, a logical impossibility that invalidates the contradiction argument as written. The intended argument is that the permutation P swaps the variances of components $\ell$ and $\ell'$: $\text{Var}(\underline{b}_\ell^{**}) = \text{Var}(\underline{b}_{\ell'}^*)$ and $\text{Var}(\underline{b}_{\ell'}^{**}) = \text{Var}(\underline{b}_\ell^*)$. By hypothesis $\text{Var}(\underline{b}_\ell^*) < \text{Var}(\underline{b}_{\ell'}^*)$, so $\mathcal{B}^{**}$ places more variance on the higher-weighted component $\ell$ (with $\alpha_\ell > \alpha_{\ell'}$), yielding strictly higher welfare. Rewrite the chain as $\mathrm{Var}(\underline{b}_{\ell}^{**}) = \mathrm{Var}(\underline{b}_{\ell'}^{*}) > \mathrm{Var}(\underline{b}_{\ell}^{*}) = \mathrm{Var}(\underline{b}_{\ell'}^{**})$.

---

### 13. Aggregate welfare formula requires column-stochasticity, not just row-stochasticity

**Status**: [Pending]

**Quote**:
> Moreover, the aggregate equilibrium utility is $W(\pmb{b},\pmb{g}) = \frac{1}{2} (\pmb{a}^*)^\top \pmb{a}^*$. Hence, this game satisfies Property A.

**Feedback**:
Summing $U_i$ over $i$ and substituting the equilibrium FOC to eliminate cross terms yields a factor $\sum_i g_{ij}$ for each $j$. For this to cancel and leave $W = (1/2)\|a^*\|^2$, one needs $\sum_i g_{ij} = 1$ for all $j$ (column-stochasticity). Row-stochasticity alone ($\sum_j g_{ij}=1$) is insufficient unless $G$ is doubly stochastic. Since the paper only imposes row-stochasticity, the Property A claim is unverified for non-doubly-stochastic $G$. It would be helpful to either assume doubly stochastic $G$ explicitly or provide the derivation showing why column sums equal 1 in the intended application.

---

### 14. Cross-effect sign condition misstated when beta-tilde is positive

**Status**: [Pending]

**Quote**:
> It is a game of strategic complements; moreover, an increase in $j$'s action has a positive effect on individual $i$'s utility if and only if $a_j < a_i$.

**Feedback**:
Computing $\partial U_i/\partial a_j$ directly gives $g_{ij}[\tilde{\beta} a_i + \gamma(a_i - a_j)]$. This is positive when $(\tilde{\beta}+\gamma)a_i > \gamma a_j$, not simply when $a_j < a_i$. The stated condition would be correct only if $\tilde{\beta}=0$, but the paper assumes $\tilde{\beta}>0$. Since $\tilde{\beta}>0$ and equilibrium actions are positive, the cross-effect is positive even for some $a_j > a_i$ (specifically whenever $a_j < ((\tilde{\beta}+\gamma)/\gamma)a_i$). Rewrite as: an increase in $j$'s action has a positive effect on $i$'s utility if and only if $(\tilde{\beta}+\gamma)a_i > \gamma a_j$.

---

### 15. Typo in OA proof: wrong sign condition for x_ell*

**Status**: [Pending]

**Quote**:
> Note that, for all $\ell \geq 2$, $x_\ell^* > 0$ if $w_1 > 0$ and $x_\ell^* < 0$ if $w_1 > 0$.

**Feedback**:
Both branches of the condition read $w_1 > 0$, making the statement internally contradictory. From the formula $x_\ell^* = w_1\alpha_\ell/(\mu - w_1\alpha_\ell)$ with $\mu > w_1\alpha_\ell$, the sign of $x_\ell^*$ equals the sign of $w_1$. Therefore $x_\ell^* < 0$ if and only if $w_1 < 0$. Rewrite the second condition as $x_\ell^* < 0$ if $w_1 < 0$.

---

### 16. SVD equilibrium formula has spurious exponent 2 on b

**Status**: [Pending]

**Quote**:
> Let $\underline{\bm{a}}=\bm{V}^{\mathsf{T}}\bm{a}$ and $\underline{\bm{b}}=\bm{U}^{\mathsf{T}}\bm{b}$; then the equilibrium condition implies that:
> 
> $\underline{a}_{\ell}^{*}=\frac{1}{s_{\ell}}b_{\ell}^{2},$

**Feedback**:
The equilibrium condition $Ma^* = b$ with $M = USV^\top$ gives, upon left-multiplying by $U^\top$: $S(V^\top a^*) = U^\top b$, i.e., $s_\ell \underline{a}_\ell^* = \underline{b}_\ell$, so $\underline{a}_\ell^* = \underline{b}_\ell/s_\ell$. The displayed formula equating an action to the square of a projection is dimensionally inconsistent and would make welfare a fourth-order function of $b$, breaking the subsequent claim that Theorem 1 applies with $\alpha_\ell = 1/s_\ell^2$. Rewrite as $\underline{a}_{\ell}^{*}=\frac{1}{s_{\ell}}\underline{b}_{\ell}$.

---

### 17. Corollary OA3 part 3 large-C limit omits strategic-complements qualifier

**Status**: [Pending]

**Quote**:
> 3. If $C\to\infty$ then $|x_{1}^{*}|\to\infty$ and $x_{\ell}^{*}\to\frac{\alpha_{\ell}}{(\alpha_{1}-\alpha_{\ell})}$ for all $\ell\geq 2$.

**Feedback**:
Under strategic substitutes ($\beta < 0$), $\alpha_n > \alpha_1$, placing the problem in a case where $|x_n^*|$ diverges and $x_1^*$ remains finite, the opposite of what Corollary OA3 part 3 states. The stated limits hold only under strategic complements ($\beta > 0$), where $\alpha_1 > \alpha_2 > \cdots > \alpha_n$ and the relevant case of Theorem OA1 applies. Rewrite part 3 to specify: If $C\to\infty$ and $\beta > 0$, then $|x_{1}^{*}|\to\infty$ and $x_{\ell}^{*}\to\frac{\alpha_{\ell}}{(\alpha_{1}-\alpha_{\ell})}$ for all $\ell\geq 2$.

---

### 18. Missing factor of 1/2 in cost formula K(y)

**Status**: [Pending]

**Quote**:
> $K(\bm{y})$ $=$ $\frac{1}{2}\sum_{i}\bm{1}_{y_{i}>0}\int_{a_{i}(\bm{y})-y_{i}}^{a_{i}(\bm{y})}s_{i}^{1}(\tau_{i})d\tau_{i}+\sum_{i}(1-\bm{1}_{y_{i}>0})\int_{a_{i}(\bm{y})}^{a_{i}(\bm{y})+|y_{i}|}s_{i}^{0}(\tau_{i})d\tau_{i}$
> $=$ $\frac{1}{2}\sum_{i}y_{i}^{2}$

**Feedback**:
If each supply function is linear (e.g., $s_i^1(\tau) = s_i^0(\tau) = \tau$), each individual integral evaluates to $y_i^2/2$. The displayed formula applies an extra factor of $1/2$ to the first sum but not the second, giving $K(y) = (1/2)\sum_{y_i>0} y_i^2/2 + \sum_{y_i<0} y_i^2/2$, which is asymmetric across cases and does not simplify to $(1/2)\sum_i y_i^2$. For the final answer to be correct, the leading $1/2$ should be removed from the first sum, since each integral already contributes $y_i^2/2$.

---

### 19. Lemma OA3 proof ends before uniform convergence is established

**Status**: [Pending]

**Quote**:
> Local separability (4) says that there are no terms of the form $y_{i}y_{j}$. Non-negativity (3) ($\kappa$ is nonnegative and $\kappa(\bm{0})=0$) implies that all first-order terms are zero. Also, (5) says that terms of the form $y_{i}^{2}$ must have positive coefficients, and symmetry (2) says that their coefficients must all be the same.

**Feedback**:
The proof ends after establishing the structure of the Taylor expansion of $\kappa$, but the lemma claims that $C^{-1}\kappa(C^{1/2}z)$ converges uniformly to $k\|z\|^2$ on compact sets as $C\to 0$. The Taylor expansion gives $\kappa(y) = k\|y\|^2 + R(y)$ with $R(y) = O(\|y\|^3)$. Substituting $y = C^{1/2}z$ yields $C^{-1}\kappa(C^{1/2}z) = k\|z\|^2 + C^{-1}R(C^{1/2}z) = k\|z\|^2 + O(C^{1/2}\|z\|^3)$, which converges to $k\|z\|^2$ uniformly on compact sets. This calculation is the core of the lemma but is entirely absent from the proof. It would be helpful to add this derivation before the end-of-proof mark.

---

### 20. Rescaled problem optimization variable incorrectly labeled

**Status**: [Pending]

**Quote**:
> $\max_{\bm{b}}\ C^{-1}\Delta(C^{1/2}\check{\bm{y}})$ ($\hat{\text{IT}}(C)$)
> $\text{s.t.}\ C^{-1}\kappa(C^{1/2}\check{\bm{y}})\leq 1.$

**Feedback**:
The rescaled problem is stated as maximizing over $b$, but the objective and constraint are written entirely in terms of the rescaled variable $\check{y} = C^{-1/2}(b-\hat{b})$. The optimization variable should be $\check{y}$, not $b$. The subsequent application of Berge's Theorem of the Maximum and the limit problems also treat $\check{y}$ as the decision variable. Rewrite the maximization as being over $\check{y}$ in all three displayed optimization problems in this proof.

---

### 21. Proposition OA3 proof boundary argument has a missing logical step

**Status**: [Pending]

**Quote**:
> Note that $L$ is contained in a convex set
> 
> $E=\{\bm{b}:W(\bm{b})\leq W^{*}\}.$
> 
> The point $\bm{b^{*}}$ is contained in the interior of $L$; thus $\bm{b^{*}}$ is in the interior of $E$.

**Feedback**:
The argument that $b^*$ is in the interior of $E$ requires that $L \subseteq E$, i.e., $W(b) \leq W^*$ for every $b$ on $L$. This holds because $L$ is contained in the feasible set $F$ and $b^*$ is the optimum, so every feasible $b$ satisfies $W(b) \leq W(b^*) = W^*$. This logical step is not stated in the proof; the proof jumps directly from stating $L$ is contained in $E$ to concluding $b^*$ is in the interior of $E$ without establishing why $L \subseteq E$. Add the explicit justification: Since $L \subseteq F$ and $b^*$ is the optimum, every $b$ on $L$ satisfies $W(b) \leq W(b^*) = W^*$, so $L \subseteq E$.

---

### 22. Large-C limit of mu stated imprecisely for negative-weight cases

**Status**: [Pending]

**Quote**:
> $\lim_{C\to\infty}\mu=\max\{w_{1}\max\{\alpha_{2},\alpha_{n}\},(w_{1}+w_{2})\alpha_{1}\}.$

**Feedback**:
When $w_1 < 0$, $w_1\max\{\alpha_2,\alpha_n\} < 0$, and if additionally $w_1+w_2 < 0$, the stated formula gives a negative limit for $\mu$, contradicting the requirement $\mu > 0$ from the Lagrangian. The argument that both denominators are positive by definition of the Lagrange multiplier does not resolve this, since the formula is derived from the budget equation rather than assumed. A case analysis distinguishing the signs of $w_1$ and $w_1+w_2$ is needed to verify the stated limit formula in each configuration.

---

### 23. w2 coefficient appears to omit m4 contribution in OA welfare decomposition

**Status**: [Pending]

**Quote**:
> $w_{1} = 1+m_{2}+m_{5}+(n-1)m_{4}$
> $w_{2} = nm_{5}(n-2)$
> $w_{3} = \sqrt{n}[m_{1}+(n-1)m_{3}].$

**Feedback**:
Computing $\sum_i m_4(\sum_{j\neq i} a_j)^2$ under Assumption OA1 yields a contribution of $m_4(n-2)$ to the coefficient of $(\sum_i a_i^*)^2/n$ (i.e., to $w_2/n$) and $m_4$ to the coefficient of $(a^*)^\top a^*$ (i.e., to $w_1$). Similarly, $\sum_i m_5 \sum_{j\neq i} a_j^2$ contributes $m_5(n-1)$ to $w_1$, not $m_5$ as stated. These discrepancies suggest the roles of $m_4$ and $m_5$ in $w_1$ and $w_2$ may be swapped or miscounted. It would be helpful to add a brief derivation of $w_1, w_2, w_3$ from $P_i$ after the statement of Lemma OA1 to allow readers to verify these coefficients.

---
