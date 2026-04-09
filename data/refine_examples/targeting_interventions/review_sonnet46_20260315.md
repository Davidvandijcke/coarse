# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/16/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper studies a planner's optimal intervention problem in linear-quadratic network games, where the planner shifts agents' standalone marginal returns subject to a quadratic budget constraint. The main result (Theorem 1) characterizes the optimal intervention in terms of the network's principal components (eigenvectors of the interaction matrix), showing that the planner optimally adjusts the 'similarity' between the intervention and each eigenvector according to an amplification factor and a status-quo effect. Corollary 1 establishes a monotone ordering of these similarity ratios, and Propositions 1–2 show that large-budget interventions simplify to targeting the leading eigenvector (eigenvector centrality) under strategic complements. Extensions address planner uncertainty, non-symmetric networks, and welfare functions beyond the baseline Property A assumption.

Below are the most important issues identified by the review panel.

**Property A Is More Restrictive Than Acknowledged, and Its Relaxation Requires Additional Conditions Not Foregrounded in the Main Text**

Theorem 1, Corollary 1, and Propositions 1–2 all rely on Property A, which requires aggregate equilibrium welfare to be proportional to (a*)ᵀa*. The paper presents this as a technically convenient but non-essential simplification, yet it rules out heterogeneous welfare weights, distributional objectives, and any utilitarian sum where individual utilities are not quadratic in own action with unit cost. The two canonical examples satisfy Property A only because of special features of the LQ structure. More importantly, the Online Appendix extension (Theorem OA1) shows that when Property A fails, the first principal component receives qualitatively different treatment from all others, and the large-budget limit can converge to either the first or second principal component depending on parameter signs—a substantive bifurcation, not a minor perturbation. Furthermore, the OA3.1 extension requires Assumption OA1 (uniform degree / constant row sums), an additional network restriction not imposed in the main text, meaning the relaxation is not as general as the framing in Section 6 implies. It would be helpful to state explicitly in the main text that the monotone ordering of similarity ratios across all principal components does not survive the relaxation of Property A, to name Assumption OA1 as a maintained hypothesis in any discussion of extensions, and to clarify which qualitative conclusions carry over to the non-Property-A setting.

**Theorem 1's Proof Implicitly Requires All Status-Quo Projections to Be Nonzero, a Condition That Fails in Economically Natural Cases**

The proof of Theorem 1 introduces the change of variables xₗ = yₗ/b̂ₗ and derives first-order conditions by dividing through by b̂ₗ², steps that are valid only when b̂ₗ = uˡ · b̂ ≠ 0 for every eigenvector ℓ. The paper acknowledges this only in passing as a 'genericity condition,' but the restriction is substantive: b̂ₗ = 0 occurs whenever b̂ is orthogonal to the ℓth eigenvector, which happens systematically—for instance, a uniform status-quo vector on a regular graph is proportional to the leading eigenvector, making all other projections exactly zero. When b̂ₗ = 0, the similarity ratio ρ(b̂, uˡ) in equation (5) takes a 0/0 form, the formula in Theorem 1 is undefined, and the status-quo effect interpretation breaks down. Because the paper's central economic message concerns how the status-quo vector shapes the optimal intervention, this gap is directly relevant to the main result. It would be helpful to either add a formal assumption (b̂ₗ ≠ 0 for all ℓ) to the statement of Theorem 1 with discussion of its economic content, or to provide a separate analysis of boundary cases showing that the qualitative ordering of Corollary 1 still holds when some projections vanish.

**The Large-Budget Simplicity Result May Be Vacuous for Empirically Relevant Networks, and the Welfare Bound Behaves Counterintuitively at the Limits**

Proposition 2 provides a sufficient budget threshold C > (2‖b̂‖²/ε)(α₂/(α₁−α₂))² for the simple eigenvector-centrality intervention to be near-optimal. The term α₂/(α₁−α₂) diverges as the spectral gap λ₁−λ₂ shrinks or as βλ₁ approaches the stability boundary, meaning the threshold can be arbitrarily large in precisely the network topologies most common in empirical applications—community-structured networks with homophily, R&D collaboration networks with industry clusters, and supply chains with modular structure. In such networks, the eigenvector-centrality targeting rule, which is the paper's main actionable recommendation, may never be a good approximation at any realistic budget. Additionally, the bound diverges as β → 0, suggesting interventions are never simple for weak strategic interactions—counterintuitive since the problem is trivially separable at β = 0. It would be helpful to quantify the threshold for at least one canonical network family (e.g., stochastic block models), to characterize what the optimal intervention looks like in the small-gap regime, and to verify whether a sharper bound could be derived that does not diverge as β → 0.

**The Incomplete-Information Extension Features One-Sided Planner Uncertainty, Not Strategic Incomplete Information Among Agents, and the Information Structure Requires Justification**

Section 5 is framed as an 'incomplete information' extension, but footnote 23 explicitly states that 'the game individuals play is one of complete information'—agents observe the realization b before choosing actions. The planner's uncertainty is therefore entirely one-sided, and the section does not address the economically important case where agents have private information about their own bᵢ values. Beyond the framing issue, the information structure raises a consistency concern: if the planner's intervention y is publicly announced before agents choose actions (as the timing requires), and agents observe both y and their own bᵢ, agents may be able to infer the planner's beliefs about b̂ from the announced y, potentially unraveling the incomplete-information structure. Proposition 3's clean result—that the optimal mean-shift intervention coincides with the deterministic problem evaluated at E[b̂]—relies on the welfare decomposition treating E[bₗ]² + Var[bₗ] as additively separable, which holds only because the welfare function is quadratic and agents' equilibrium play depends only on realized b. It would be helpful to retitle Section 5 as 'Planner Uncertainty about Standalone Returns,' to clarify in the introduction what type of incomplete information is actually modeled, and to address whether the equilibrium concept remains valid when agents can update beliefs about b̂ from observing y.

**The Non-Symmetric Extension via SVD Loses the Strategic Interpretation That Motivates the Main Results and Contains an Unverified Claim About Theorem 1's Applicability**

Online Appendix OA3.2 extends the analysis to non-symmetric G using the SVD of M = I − βG, with M = USVᵀ where U ≠ V in general. The paper claims 'Theorem 1 applies, with the only difference that now αₗ = 1/sₗ²,' but this claim is not immediate: the welfare function W = w(a*)ᵀa* is expressed in the V-basis while the cost K = ‖y‖² is expressed in the U-basis, and because U ≠ V the budget constraint does not automatically take the diagonal form used in the symmetric proof. A separate argument is needed to establish that the optimization decomposes in the same way. Beyond this technical gap, the extension loses the central economic interpretation of the symmetric case: the monotone relationship between eigenvalues of G and amplification factors αₗ = (1−βλₗ)⁻² directly reflects whether the game has strategic complements or substitutes, but singular values of M = I−βG are not monotone functions of β in any simple sense, and the left and right singular vectors differ from any standard network centrality measure. It would be helpful to either provide the missing argument showing the budget constraint diagonalizes in the V-basis, supply conditions on non-symmetric G under which the ordering of singular values still reflects the nature of strategic interaction, or explicitly acknowledge that the complement/substitute dichotomy does not extend cleanly to the directed-network case.

**The Differentiation from Ballester et al. (2006) and Demange (2017) Conflates Two Sources of Difference and Understates Overlap in the Large-Budget Limit**

The paper positions its main contribution as the use of principal components rather than Bonacich centrality for optimal targeting, attributing the difference to the objective function (aggregate utility vs. sum of actions). However, the discussion in OA2.1 conflates two distinct sources of difference: the objective function and the cost structure. Ballester et al. (2006) use a linear cost (targeting one player), while this paper uses quadratic costs (spreading the intervention); Corollary OA1 shows that even when the planner maximizes the sum of actions subject to a quadratic cost, the optimal intervention is proportional to eigenvector centrality rather than Bonacich centrality—a difference driven by cost structure, not objective. More substantively, for large budgets under strategic complements (Proposition 1, part 2), the optimal intervention is proportional to u¹(G)—the Perron eigenvector—which is also the large-budget limit in Demange (2017)'s complementarities setting. The paper does not provide a formal comparison showing exactly where the two problems diverge at intermediate budgets. It would be helpful to present a 2×2 comparison (linear vs. quadratic costs crossed with sum-of-actions vs. sum-of-utilities objectives) to cleanly isolate each modeling choice's contribution, and to quantify how different the resulting interventions are for intermediate budgets where the two approaches may genuinely differ.

**Status**: [Pending]

---

## Detailed Comments (16)

### 1. Self-referential change-of-variables formula in Example 2

**Status**: [Pending]

**Quote**:
> Performing the change of variables $b_{i}=[\tau-b_{i}]/2$ and $\beta=-\tilde{\beta}/2$ (with the status quo equal to $\hat{b}_{i}=[\tau-\tilde{b}_{i}]/2$) yields a best-response structure exactly as in condition (2).

**Feedback**:
The formula defines b_i in terms of itself: b_i = (tau minus b_i)/2, which solves to b_i = tau/3, a constant independent of model parameters. The status-quo formula immediately following uses the original endowment b-tilde_i on the right-hand side, confirming the intended substitution is b_i = (tau minus b-tilde_i)/2. One can verify: the FOC from U_i gives a_i = (tau minus b-tilde_i)/2 minus (beta-tilde/2) times the sum of g_{ij}a_j, matching condition (2) exactly when b_i = (tau minus b-tilde_i)/2 and beta = minus beta-tilde/2. It would be helpful to rewrite the formula as b_i = [tau minus b-tilde_i]/2 because the right-hand side must use the original information endowment b-tilde_i, not the transformed standalone return b_i.

---

### 2. Assumption 3 uses norm instead of squared norm as threshold

**Status**: [Pending]

**Quote**:
> Either $w<0$ and $C<\|\hat{\bm{b}}\|$, or $w>0$.

**Feedback**:
The cost of zeroing all actions requires intervention y = minus b-hat with cost equal to the squared norm of b-hat. Assumption 3 is supposed to rule out this first-best case, so the threshold should be the squared norm. As written, C less than the norm of b-hat leaves a gap where the first-best is achievable yet Assumption 3 is satisfied. The budget constraint in the proof sketch is the sum over ell of b-hat_ell squared times x_ell squared, bounded by C, and the cost of zeroing all actions equals the squared norm of b-hat, confirming the squared norm is the correct threshold. It would be helpful to rewrite Assumption 3 as: Either w less than 0 and C less than the squared norm of b-hat, or w greater than 0.

---

### 3. Inline alpha_ell definition missing the square in denominator

**Status**: [Pending]

**Quote**:
> The second factor, $\frac{w\alpha_{\ell}}{\mu-w\alpha_{\ell}}$, is determined by two quantities: the eigenvalue corresponding to $\bm{u}^{\ell}(\bm{G})$ (via $\alpha_{\ell}=\frac{1}{1-\beta\lambda_{\ell}}$), and the budget $C$ (via the shadow price $\mu$).

**Feedback**:
The display equation earlier in the same section defines alpha_ell = 1/(1 minus beta times lambda_ell) squared, and this squared form is essential for the welfare calculation. The inline formula alpha_ell = 1/(1 minus beta times lambda_ell) is missing the square, contradicting the paper's own display definition. Using the unsquared version would give a_ell-star = alpha_ell times b-underline_ell instead of the correct equilibrium expression, inconsistent with equation (4). It would be helpful to rewrite the inline formula as alpha_ell = 1/(1 minus beta times lambda_ell) squared to match the display definition and the proof sketch.

---

### 4. Missing square on b-hat_ell in Lagrangian first term

**Status**: [Pending]

**Quote**:
> $\mathcal{L}=w\sum_{\ell}\alpha_{\ell}(1+x_{\ell})^{2}\hat{\underline{b}}_{\ell}+\mu\left[C-\sum_{\ell}\hat{\underline{b}}_{\ell}^{2}x_{\ell}^{2}\right].$

**Feedback**:
The transformed objective is w times the sum over ell of alpha_ell times b-hat_ell squared times (1+x_ell) squared, so the weight on each component is b-hat_ell squared. The Lagrangian as written has b-hat_ell unsquared in the first term. Differentiating the written Lagrangian with respect to x_ell gives 2w times alpha_ell times (1+x_ell) times b-hat_ell, whereas the first-order condition reads 2 times b-hat_ell squared times [w times alpha_ell times (1+x_ell-star) minus mu times x_ell-star] = 0, which is consistent only with the squared version. It would be helpful to rewrite the first term replacing b-hat_ell with b-hat_ell squared.

---

### 5. Proposition 2 part 2 denominator sign inconsistency

**Status**: [Pending]

**Quote**:
> If the game has the strategic substitutes property, $\beta<0$, then for any $\epsilon>0$, if $C>\frac{2\|\hat{\bm{b}}\|^{2}}{\epsilon}\left(\frac{\alpha_{n-1}}{\alpha_{n}-\alpha_{n-1}}\right)^{2}$, then $W^{*}/W^{s}<1+\epsilon$

**Feedback**:
Under beta less than 0 with lambda_n less than lambda_{n-1}, we have (1 minus beta times lambda_n) squared greater than (1 minus beta times lambda_{n-1}) squared, giving alpha_n less than alpha_{n-1}. Therefore alpha_n minus alpha_{n-1} is negative, making the denominator structurally negative. The prose correctly writes alpha_{n-1}/(alpha_{n-1} minus alpha_n) with positive denominator. It would be helpful to rewrite the threshold with alpha_{n-1} minus alpha_n in the denominator, because that quantity is positive and consistent with the prose description.

---

### 6. Welfare ratio conclusion uses W-superscript-2 instead of W-superscript-s

**Status**: [Pending]

**Quote**:
> is sufficient to establish that $\frac{W^{*}}{W^{2}}<1+\epsilon$.

**Feedback**:
The proof introduces simple-intervention welfare as W-superscript-s and optimal welfare as W-star. The conclusion should reference W-superscript-s, not W-superscript-2. The superscript 2 does not correspond to any quantity defined in the proof and is a typographical error for s. It would be helpful to rewrite W-superscript-2 as W-superscript-s in the final inequality to match the notation established at the start of the proof.

---

### 7. Corollary 1 attribution incorrect for x(x+2) monotonicity step

**Status**: [Pending]

**Quote**:
> $\leq\alpha_{2}x_{2}^{*}(x_{2}^{*}+2)\sum_{\ell\neq 1}\hat{\underline{b}}_{\ell}^{2}$ Corollary 1

**Feedback**:
The step bounds the sum over ell not equal to 1 of b-hat_ell squared times x_ell-star times (x_ell-star+2) by x_2-star times (x_2-star+2) times the sum of b-hat_ell squared, requiring (i) x_2-star greater than or equal to x_ell-star for ell at least 2 (from Theorem 1) and (ii) f(x) = x(x+2) is increasing on the positive reals (since f-prime(x) = 2x+2 > 0). Corollary 1 concerns ordering of cosine similarities, not the function x(x+2). It would be helpful to replace the citation Corollary 1 with a reference to Theorem 1 for the ordering of x_ell-star and to the monotonicity of x(x+2) on the positive reals.

---

### 8. Notation conflict: overbar-b used for fixed mean and realizations of B-tilde

**Status**: [Pending]

**Quote**:
> Assumption 5. The cost function satisfies two properties: (a) $K(\mathcal{B}) = \infty$ if $\mathbb{E}\pmb {b}\neq \bar{\pmb{b}}$; (b) $K(\mathcal{B}) = K(\widetilde{\mathcal{B}})$ if $\widetilde{\pmb{b}} -\bar{\pmb{b}} = \pmb {O}(\pmb {b} - \bar{\pmb{b}})$, where $\pmb{O}$ is an orthogonal matrix. Analogous to our other notation, we use $\overline{\pmb{b}}$ for realizations of the random vector with distribution $\widetilde{\mathcal{B}}$.

**Feedback**:
In parts (a) and (b), b-bar is the fixed target mean vector (a constant). The closing sentence then declares b-bar to be realizations of B-tilde, directly conflicting with both prior uses. If b-bar denoted a realization of B-tilde, part (b)'s condition b-tilde minus b-bar = O times (b minus b-bar) would read realization minus realization, which is either trivially zero or incoherent. The intended meaning is that b-tilde (not b-bar) denotes realizations of B-tilde, consistent with the use of b-tilde in part (b) itself. It would be helpful to rewrite the closing sentence as: Analogous to our other notation, we use b-tilde for realizations of the random vector with distribution B-tilde.

---

### 9. Contradiction inequality chain is garbled and self-contradictory

**Status**: [Pending]

**Quote**:
> and so  $\mathrm{Var}(\underline{b}_k^{**}) = \mathrm{Var}(\underline{b}_k^*)$  for all  $k\notin \{\ell ,\ell '\}$  and  $\mathrm{Var}(\underline{b}_{\ell}^{*}) = \mathrm{Var}(\underline{b}_{\ell '}^{*}) > \mathrm{Var}(\underline{b}_{\ell '}^{**}) = \mathrm{Var}(\underline{b}_{\ell}^{*})$

**Feedback**:
The hypothesis is Var(b-underline_ell-star) less than Var(b-underline_{ell-prime}-star). The permutation P swaps positions ell and ell-prime, so Var(b-underline_ell-double-star) = Var(b-underline_{ell-prime}-star) and Var(b-underline_{ell-prime}-double-star) = Var(b-underline_ell-star). The correct chain is: Var(b-underline_ell-double-star) = Var(b-underline_{ell-prime}-star) greater than Var(b-underline_ell-star) = Var(b-underline_{ell-prime}-double-star). The printed chain instead asserts Var(b-underline_ell-star) = Var(b-underline_{ell-prime}-star) at the outset, directly contradicting the hypothesis, and ends with the absurdity A = B greater than C = A. It would be helpful to rewrite the inequality chain with the correct equalities reflecting the permutation swap.

---

### 10. Eigenvector normalization u-superscript-1_i stated as square-root-n instead of 1/square-root-n

**Status**: [Pending]

**Quote**:
> 2. $\lambda_{1}(\bm{G})=1$ and $u_{i}^{1}(\bm{G})=\sqrt{n}$ for all $i$

**Feedback**:
Under Assumption OA1, G times the all-ones vector equals the all-ones vector, confirming lambda_1 = 1 with eigenvector proportional to the all-ones vector. The unit-norm convention requires u-superscript-1 = (1/square-root-n) times the all-ones vector, giving u-superscript-1_i = 1/square-root-n. Verification: the squared norm equals n times (1/square-root-n) squared = 1. The stated value square-root-n gives squared norm equal to n times (square-root-n) squared = n squared, which is not 1. Cross-checking with part 3 of the same lemma confirms that u-superscript-1_i = 1/square-root-n is internally consistent with the equilibrium sum formula. It would be helpful to rewrite part 2 as u-superscript-1_i(G) = 1/square-root-n for all i.

---

### 11. Feasible interval for x_1 in First Step missing square root

**Status**: [Pending]

**Quote**:
> First Step. We fix $x_1$ so that $C(x_1) \geq 0$; that is, $x_1 \in [-C / \hat{\underline{b}}_1, C / \hat{\underline{b}}_1]$.

**Feedback**:
The condition C(x_1) greater than or equal to 0 is C minus b-hat_1 squared times x_1 squared greater than or equal to 0, giving the absolute value of x_1 at most square-root-C divided by b-hat_1. The correct feasible interval is x_1 in [minus square-root-C divided by b-hat_1, square-root-C divided by b-hat_1]. The stated interval [minus C divided by b-hat_1, C divided by b-hat_1] is inconsistent with the budget constraint. This is confirmed by Lemma OA2, which explicitly states limits as x_1 approaches plus or minus square-root-C divided by b-hat_1, and the Second Step constraint box, which states the same corrected interval. It would be helpful to rewrite the range with square-root-C in the numerator.

---

### 12. Large-C limit formula for mu can yield non-positive value

**Status**: [Pending]

**Quote**:
> $\lim_{C\to\infty}\mu=\max\{w_{1}\max\{\alpha_{2},\alpha_{n}\},(w_{1}+w_{2})\alpha_{1}\}.$

**Feedback**:
This formula can be negative when both w_1 less than 0 and w_1 plus w_2 less than 0, since all alpha_ell are positive. But mu must be positive as a Lagrange multiplier on a binding budget constraint, so a negative limit is impossible. Parts 4 and 5 of Theorem OA1 handle the cases correctly via explicit case analysis requiring the larger quantity to be positive, so the theorem statements themselves are correct. The issue is confined to this summary formula in the proof. It would be helpful to rewrite the limit formula by replacing the single max expression with explicit case statements matching parts 4 and 5, because the current formula can yield a non-positive value contradicting mu greater than 0.

---

### 13. Corollary OA3 part 3 large-C limit omits strategic-complement assumption

**Status**: [Pending]

**Quote**:
> 3. If $C\to\infty$ then $|x_{1}^{*}|\to\infty$ and $x_{\ell}^{*}\to\frac{\alpha_{\ell}}{(\alpha_{1}-\alpha_{\ell})}$ for all $\ell\geq 2$.

**Feedback**:
The formula x_ell-star converging to alpha_ell divided by (alpha_1 minus alpha_ell) requires alpha_1 greater than alpha_ell for all ell at least 2, which holds under strategic complements (beta greater than 0) since alpha_ell is increasing in lambda_ell and lambda_1 is the largest eigenvalue. Under strategic substitutes (beta less than 0), alpha_n can exceed alpha_1, placing the problem in a different case of Theorem OA1 and yielding a different limit. It would be helpful to add the qualifier that the game has strategic complements (beta greater than 0) to the hypothesis of Corollary OA3 part 3, or to provide the analogous formula for the substitutes case.

---

### 14. Proof of Proposition OA3 contradiction step uses undefined U and wrong mechanism

**Status**: [Pending]

**Quote**:
> The point $\bm{b^{*}}$ is contained in the interior of $L$; thus $\bm{b^{*}}$ is in the interior of $E$. On the other hand, $\bm{b^{*}}$ must be on the (elliptical) boundary of $E$ because $U$ is strictly increasing in each component (by irreducibility of the network) and continuous. This is a contradiction.

**Feedback**:
The proof appeals to U being strictly increasing in each component by irreducibility, but U is not defined anywhere in this section; the objective is W(b) = a(b)-transpose times a(b). The correct mechanism is strict convexity: W(b) = b-transpose times (I minus beta G) to the negative-transpose times (I minus beta G) to the negative-1 times b is a positive-definite quadratic form, so the level set E is a strictly convex ellipsoid. Any interior point of E satisfies W(b) strictly less than W-star, but b-star in the interior of L inside E gives W(b-star) strictly less than W-star, contradicting W(b-star) = W-star from optimality. It would be helpful to rewrite the contradiction step using strict convexity of W rather than the undefined U.

---

### 15. Berge's Theorem invocation does not justify argmax convergence without uniqueness

**Status**: [Pending]

**Quote**:
> The Theorem of the Maximum therefore implies that the maximized value is continuous at $C=0$. Because the convergence of the objective is actually uniform on $\mathcal{K}$ by the Lemma, this is possible if and only if $\check{\bm{y}}$ approaches the solution of the problem

**Feedback**:
Berge's Theorem guarantees upper hemicontinuity of the argmax correspondence and continuity of the value function, but does not imply that the argmax converges to a unique limit. The if-and-only-if claim requires that the limit problem has a unique solution; otherwise one can only conclude that limit points lie in the limit argmax set. The paper acknowledges set-valuedness by writing that the solution may be set-valued, yet treats convergence as if to a unique point. Under Property A the leading eigenvalue is simple, likely making the limit problem have a unique solution on the unit sphere, but this uniqueness must be stated explicitly. It would be helpful to rewrite the passage to first establish uniqueness of the limit problem's solution via Property A, then invoke upper hemicontinuity to conclude convergence.

---

### 16. Welfare centrality formula has incorrect exponent on eigenvalue multipliers

**Status**: [Pending]

**Quote**:
> $\|\bm{a}(\bm{1}_{i})\|=\|\underline{\bm{a}}(\underline{\bm{1}}_{i})\|=\sqrt{\sum_{\ell}\alpha_{\ell}(u_{i}^{\ell})^{2}}.$

**Feedback**:
Let alpha_ell = 1/(1 minus beta times lambda_ell) be the eigenvalue of (I minus beta G) to the negative-1. Then a(1_i) = the sum over ell of alpha_ell times u_i-superscript-ell times u-superscript-ell, so the squared norm of a(1_i) equals the sum over ell of (alpha_ell times u_i-superscript-ell) squared = the sum over ell of alpha_ell squared times (u_i-superscript-ell) squared. The formula in the paper has alpha_ell where alpha_ell squared is needed. This would be consistent only if alpha_ell were defined as 1 divided by the square root of (1 minus beta times lambda_ell), a non-standard definition not stated in this section. It would be helpful to rewrite the formula with alpha_ell squared inside the square root, or to clarify explicitly the definition of alpha_ell used in this expression.

---
