# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 04/12/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper has a clear and interesting spectral reformulation of the planner's targeting problem in linear-quadratic network games, and the complete-information benchmark yields a neat ordering of intervention directions by eigenvalues. The main concerns are not about whether the decomposition is elegant, but about how much of the substantive message survives the strong structural restrictions that make the decomposition work, how clearly the welfare objective is separated from those restrictions, and whether the extensions actually establish broader relevance rather than restating the benchmark under renamed assumptions.

The paper's main strength is the principal-components representation in Sections 3-4, which gives a compact way to think about optimal targeting under complements and substitutes. It also does a good job connecting the top and bottom eigendirections to different economic intuitions. The difficulty is that the headline policy claims are broader than the part of the model where the results are genuinely sharp, and several key extensions rely on assumptions that make the conclusions close to mechanical.

**The welfare objective is narrower than the paper's framing suggests**

Sections 2 and 4 frame the planner's problem as maximizing utilitarian welfare in a broad class of network games, but the sharp characterization in Theorem 1 only goes through under Property A, which reduces welfare to \(W(\mathbf{b},\mathbf{G}) = w (\mathbf{a}^*)^\top \mathbf{a}^*\). That restriction rules out many natural cases in which welfare depends on the level of actions, their distribution, or externalities that are not proportional to squared actions; the paper itself acknowledges this in OA3.1. This matters because the paper's main policy takeaway, namely that complements call for top principal components and substitutes for bottom principal components, is derived for a special welfare class rather than for utilitarian planning in general. The OA3.1 extension actually shows that once linear and aggregate terms enter welfare, the special role of the first component can reappear for reasons unrelated to the complements/substitutes logic, which weakens the claimed general message. The paper should tighten its framing in the introduction and conclusion, and move the distinction between the Property A benchmark and general welfare objectives into the main text rather than leaving it as an appendix caveat.

**The baseline theorem depends on restrictive spectral assumptions that do more than simplify notation**

Assumptions 1 and 2 in Section 2 require a symmetric network, distinct eigenvalues, and \(\rho(\beta \mathbf{G})<1\). Symmetry is not a harmless technical step here: the entire principal-components interpretation in Section 3 relies on an orthogonal eigendecomposition of \(\mathbf{G}\), and the economic ordering result in Corollary 1 is stated in that language. OA3.2 replaces this with an SVD of \(\mathbf{M}=\mathbf{I}-\beta \mathbf{G}\), but once the network is directed the left and right singular vectors need not coincide with economically meaningful directions in the original network, and the clean complements-versus-substitutes interpretation is largely lost. That means the paper's title and introduction overstate how general the targeting rule is for network interventions. A stronger revision would either narrow the claims to symmetric interaction structures throughout, or elevate the directed-network case into the main text and spell out exactly which substantive conclusions survive when eigenvectors are replaced by singular vectors.

**Policy prescriptions are highly sensitive to primitives the planner must know exactly**

Every main result in Sections 2-6 assumes the planner knows \(\mathbf{G}\), the sign and magnitude of \(\beta\), and the status-quo vector \(\hat{\mathbf{b}}\). That is not an empirical identification complaint; it is a theoretical scope issue because the optimal direction depends on \(\alpha_\ell = (1-\beta \lambda_\ell)^{-2}\), which becomes extremely sensitive when \(\beta\lambda_\ell\) approaches one. Near that boundary, small misspecification in \(\beta\) or in the spectrum of \(\mathbf{G}\) can radically change which components dominate, and in the substitutes case a sign or magnitude error can flip the recommended targeting pattern. Proposition 2 already shows that spectral gaps govern how concentrated the intervention becomes, which is exactly the setting where small perturbations can matter most, yet the paper never studies robustness of the rule to primitive uncertainty. Since the contribution is framed as a targeting principle for planners, the paper should either add a sensitivity analysis showing when the rule is stable to misspecification, or explicitly recast the results as a full-information benchmark whose applicability depends on very accurate knowledge of the network and strategic parameter.

**The incomplete-information section adds limited content beyond the deterministic benchmark**

Section 5 is presented as an important extension, but Proposition 3 mainly shows that with deterministic mean shifts and quadratic costs, the planner acts as if the status quo were its mean \(\mathbb{E}[\hat{\mathbf{b}}]\). Given equation (8), that conclusion is almost built into the specification rather than generated by new strategic reasoning. The more novel variance-control result in Proposition 4 depends on Assumption 5, especially rotation-invariant costs, which makes it almost inevitable that variance will be allocated toward the components with the largest welfare weights \(\alpha_\ell\). This matters because the section is supposed to broaden the economic reach of the paper, yet it does not address the harder and more relevant case in which agents themselves face incomplete information or the planner only observes noisy network primitives. The section would be much stronger if it either studied a genuine informational problem with strategic uncertainty among agents, or was repositioned as a narrow comparative-static corollary rather than a major extension.

**Some theorem statements do not fully match the conditions used in the proofs**

Theorem 1 in Section 4 is stated without requiring nonzero projections of \(\hat{\mathbf{b}}\) on each principal component, but the proof in Appendix A explicitly imposes a generic \(\hat{\mathbf{b}}\) with \(\hat{\underline{b}}_\ell \neq 0\) for all \(\ell\). That matters because the key change-of-variables step defines \(x_\ell = (\underline{b}_\ell - \hat{\underline{b}}_\ell)/\hat{\underline{b}}_\ell\), and the similarity ratio \(r_\ell^*\) is undefined when \(\rho(\hat{\mathbf{b}}, \mathbf{u}^\ell)=0\). So the theorem, as written, appears more general than the proof supports. There is also an internal inconsistency around Assumption 3: Section 4 says the first-best with \(w<0\) is attainable when \(C \geq \|\hat{\mathbf{b}}\|^2\), but Assumption 3 is written as \(C < \|\hat{\mathbf{b}}\|\), dropping the square. These are fixable issues, but they should be corrected in the main theorem statements and assumptions because they affect the precise domain of the paper's main characterization.

**The paper does not do enough to show that the spectral rule has bite relative to existing heuristics**

The introduction positions the contribution against familiar centrality-based targeting ideas, especially Bonacich and eigenvector centrality, and OA2.1 explains why the planner's objective differs from maximizing the sum of actions. Even so, the paper offers little direct evidence on when the new rule changes recommendations in economically meaningful ways, beyond the stylized figures in Section 4 and a few asymptotic statements for large budgets. This is a missing piece because a top-field theory paper should show not only that the spectral decomposition is elegant, but also that it yields substantively different policies and welfare gains compared with simpler benchmarks such as uniform interventions, Bonacich targeting, or first-eigenvector targeting outside the large-budget limit. Without that comparison, readers are left unsure whether the contribution is a new representation of known logic or a materially different targeting prescription. The revision should add a worked example or simulation exercise that compares welfare and target profiles across the paper's rule and the most natural competing heuristics over budgets, signs of \(\beta\), and network structures.

**No closed-form benchmark on a canonical network**

The paper never works out the optimal intervention all the way through for a simple named network where the eigenvectors and eigenvalues are explicit. Figures give intuition, but they do not let the reader see how Theorem 1 translates into target levels as functions of \(\beta\), \(C\), and the status quo \(\hat b\). That is a real omission for a theory paper built around a spectral decomposition, because readers need one case where the formula can be checked by hand and tied to familiar network structure. A natural addition is a fully solved star or circle network under Example 1 and Example 2: compute \(\lambda_\ell\), \(u^\ell\), the coefficients \(x_\ell^*=w\alpha_\ell/(\mu-w\alpha_\ell)\), and then recover \(b_i^*\) in original coordinates. For the star, the paper could show directly how the hub-versus-periphery pattern changes between \(\beta>0\) and \(\beta<0\); for the circle, it could show how the bottom eigenvector induces alternating signs under substitutes. One worked benchmark of this kind would make the main result much easier to calibrate and would show that the theorem has operational content beyond the abstract cosine-similarity statement.

**Incomplete-information extension lacks an explicit optimal design**

Section 5 states broad prescriptions about how the planner should shift means or variances across principal components, but it never constructs an actual optimal random intervention in a concrete model. As written, Proposition 4 is mostly an ordering result on projected variances, so the reader is left without a clear sense of what the planner would implement as a distribution over incentives. That matters because this section is supposed to broaden the paper beyond deterministic targeting, yet it does not show the shape of an optimal stochastic policy in any familiar case. A useful addition would be a worked Gaussian example on the 14-node circle from Example 3 under the trace cost in equation (9): solve for the covariance matrix that puts all variance on \(u^1\) when \(\beta>0,w>0\), and on \(u^{14}\) when \(\beta<0,w>0\), then compute the implied variance of equilibrium actions. The paper could also compare that design to isotropic noise with the same cost. That would turn the variance-control result from a ranking statement into an explicit intervention rule.

**Directed-network extension has no economic worked case**

The online appendix says the approach extends to non-symmetric interaction matrices through the SVD of \(M=I-\beta G\), but there is no concrete directed network where the reader can see what this means. That leaves a gap because the paper's title and framing invite applications to many network settings where direction matters, and the economic interpretation changes once left and right singular vectors separate. Without a worked case, it is hard to judge whether the SVD extension is a genuine extension of the targeting logic or mainly a change of coordinates. The appendix should include a small directed example, such as a three-node line \(1\to2\to3\) or a buyer-seller chain, compute \(U\), \(S\), and \(V\), and then show the optimal intervention and resulting actions under a fixed budget. The point should be to spell out which vector governs the planner's intervention, which vector governs equilibrium responses, and how that differs from the symmetric benchmark. One explicit calculation would make clear what substantive content survives in the directed case.

**Existing centrality benchmarks are discussed, not recovered**

The paper talks at several points about Bonacich centrality, eigenvector centrality, and earlier targeting papers, but it does not formally recover the main benchmark prescriptions inside its own framework. That is more than a literature-positioning issue: for a methodological paper, readers need to see exactly when the new spectral rule collapses to familiar objects and when it does not. OA2.1 says that with an objective linear in the sum of actions and quadratic costs one gets Bonacich targeting, but the paper does not provide the derivation or place it alongside Theorem 1. A clean way to fix this is to add a proposition that solves the planner's problem with objective \(\sum_i a_i^*\) in the Ballester-Calvo-Armengol-Zenou investment game and shows that the optimal target is proportional to Bonacich centrality, then compare it analytically to the \(w(a^*)^\top a^*\) objective. The comparison should be done on the same network and status quo, so readers can see when the two prescriptions coincide, when they diverge, and why the welfare objective introduces different component weights. That would give the paper a sharper connection to existing approaches than the current verbal discussion.

**Recommendation**: major revision. The core spectral insight is strong enough to merit serious attention, but the paper currently presents a benchmark result under narrow welfare and network assumptions as if it were a broadly applicable targeting principle. A revision needs to clarify the true scope of the theorem, strengthen the substantive content of the extensions, and demonstrate that the proposed rule changes policy conclusions in a meaningful way.

**Key revision targets**:

1. Rewrite the framing of the main contribution so that Theorem 1 is explicitly presented as a Property A benchmark, and bring the non-Property-A implications from OA3.1 into the main text.
2. State the exact conditions needed for Theorem 1 and related objects such as \(x_\ell\) and \(r_\ell^*\), including what happens when \(\hat{\underline{b}}_\ell = 0\), and correct the inconsistency in Assumption 3's budget threshold.
3. Add a robustness analysis showing how targeting recommendations vary with misspecification in \(\beta\), in the network spectrum, and near the boundary \(\rho(\beta \mathbf{G})=1\).
4. Either deepen Section 5 into a genuine informational extension with strategic uncertainty or reframe it as a narrow corollary and reduce its role in the paper's claims.
5. Include a quantitative illustration comparing the paper's optimal rule with uniform targeting, Bonacich-style targeting, and first-eigenvector targeting across several network structures and budget levels.

**Status**: [Pending]

---

## Detailed Comments (23)

### 1. Beauty-contest best response uses the wrong coefficient

**Status**: [Pending]

**Quote**:
> It can be verified that the first-order condition for individual $i$ is given by
>
> $$
> a_i = \frac{\tilde{b}_i}{1 + \gamma} + \frac{\tilde{b}_i + \gamma}{1 + \gamma} \sum g_{ij} a_j.
> $$
>
> By defining $\beta = \frac{\tilde{\beta} + \gamma}{1 + \gamma}$ and $\boldsymbol{b} = \frac{1}{1 + \gamma}\tilde{\boldsymbol{b}}$, we obtain a best-response structure exactly as in condition (2).

**Feedback**:
This coefficient cannot be right. Differentiating the displayed payoff gives
$\tilde b_i+(\tilde\beta+\gamma)\sum_j g_{ij}a_j-(1+\gamma)a_i=0$,
so the best response is
$$a_i=\frac{\tilde b_i}{1+\gamma}+\frac{\tilde\beta+\gamma}{1+\gamma}\sum_j g_{ij}a_j.$$
That also matches the next sentence, which defines $\beta=(\tilde\beta+\gamma)/(1+\gamma)$. As printed, the formula uses $\tilde b_i+\gamma$ in the interaction coefficient, which breaks the mapping to the baseline model. This needs a direct correction.

---

### 2. Best-response formula needs an explicit no-self-loop condition

**Status**: [Pending]

**Quote**:
> response. The first-order conditionfor individual $i$’s action to be a best response is:
>
> $a_{i}=b_{i}+\beta\sum_{j} g_{ij}a_{j}.$
>
> Any Nash equilibrium action profile $\boldsymbol{a}^{*}$ of the game satisfies
>
> $[\boldsymbol{I}-\beta\boldsymbol{G}]\boldsymbol{a}^{*}=\boldsymbo

**Feedback**:
As written, this derivation is valid only if own-action terms are excluded from the interaction sum, equivalently if $g_{ii}=0$ for all $i$. Otherwise differentiating $a_i\bigl(b_i+\beta\sum_j g_{ij}a_j\bigr)-\tfrac12 a_i^2$ produces an extra term from the product rule, and the best response is no longer the displayed equation. The cleanest fix is to state the restriction on $G$ explicitly or rewrite the payoff/best response with $\sum_{j\neq i}$. Without that, equations (2) and (3) are not fully justified.

---

### 3. The paper calls the eigenvalue a multiplier, but the multiplier is a function of it

**Status**: [Pending]

**Quote**:
> This basis has three special properties: (a) the effects of an intervention along a principal component is proportional to the intervention, scaled by a network multiplier; (b) the “network multiplier” is an eigenvalue of the network corresponding to that principal component; (c) the principal components are orthogonal, so that the effects along various principal components can be treated separately (in a suitable sense).

**Feedback**:
This mixes up two different objects. In Section 3 the amplification along component $\ell$ is $1/(1-\beta\lambda_\ell)$, while $\lambda_\ell$ is the eigenvalue that indexes that amplification. They are not interchangeable. If $\beta=0$, for instance, the multiplier is 1 for every component even though the eigenvalues differ. The sentence should say that the multiplier is determined by the eigenvalue, not that the multiplier is the eigenvalue itself.

---

### 4. The PCA definition is not correct as written

**Status**: [Pending]

**Quote**:
> The first principal component of $\bm{G}$ is defined as the $n$-dimensional vector that minimizes the sum of squares of the distances to the columns of $\bm{G}$. The first principal component can therefore be thought of as a fictitious column that “best summarizes” the dataset of all columns of $\bm{G}$.

**Feedback**:
Under this definition, the minimizer is the sample mean of the columns, not a principal-component direction. If $g^j$ denotes column $j$, minimizing $\sum_j\|g^j-v\|^2$ gives $v=\frac1n\sum_j g^j$. That is generally not an eigenvector. To support the later spectral interpretation, this paragraph should use the standard PCA definition: the first component is the unit direction maximizing projected variance, or equivalently the one-dimensional subspace minimizing reconstruction error.

---

### 5. PCA ordering is by $|\lambda_\ell|$, not by $\lambda_\ell$

**Status**: [Pending]

**Quote**:
> We continue in this way, projecting orthogonally off the (subspace generated by) vectors obtained to date, to find the next principal component. A well-known result is that the eigenvectors of $\bm{G}$ that diagonalize the matrix (i.e., the columns of $\bm{U}$) are indeed the principal components of $\bm{G}$ in this sense.

**Feedback**:
Even after fixing the definition, the ordering needs care. PCA of the column data uses $GG^{\top}$, and for symmetric $G$ this is $G^2$. So the eigendirections coincide, but the ranking is by $\lambda_\ell^2$, not by $\lambda_\ell$. A simple counterexample is $G=\operatorname{diag}(1,-3)$: ordering eigenvalues from greatest to least picks $e_1$ first, while PCA ranks $e_2$ first because $9>1$. The paragraph should separate the claim about directions from the claim about ordering.

---

### 6. The nonnegativity discussion should be stated in terms of equilibrium actions

**Status**: [Pending]

**Quote**:
> In some problems there may be a nonnegativity constraint on actions, in addition to the constraints in problem (IT). Note that as long as the status quo actions $\hat{\bm{b}}$ are positive, this constraint will be respected for all $C$ less than some $\hat{C}$, and so our approach will give information about the relative effects on various components for interventions that are not too large.

**Feedback**:
The condition here is on the wrong object. The added constraint is $a_i\ge 0$, so what matters is strict positivity of the status-quo equilibrium action vector $\hat{\bm a}^*=(I-\beta G)^{-1}\hat{\bm b}$, not positivity of $\hat{\bm b}$ itself. With strategic substitutes, positive standalone returns can still generate negative equilibrium actions. A continuity argument works, but it has to start from $\hat{\bm a}^*>0$.

---

### 7. The large-budget result is directional, not exact vector convergence

**Status**: [Pending]

**Quote**:
> Turning now to the case where $C$ grows large, the shadow price converges to $w\alpha_{1}$ if $\beta>0$, and to $w\alpha_{n}$ if $\beta<0$ (by equation (6)). Plugging this into equation (5), we find that in the case of strategic complements, the optimal intervention shifts individuals’ standalone marginal returns (very nearly) in proportion to the first principal component of $\bm{G}$, so that $\bm{y}^{*}\to\sqrt{C}\bm{u}^{1}(\bm{G})$. In the case of strategic substitutes, on the other hand, the planner changes individuals’ standalone marginal returns (very nearly) in proportion to the last principal component, namely $\bm{y}^{*}\to\sqrt{C}\bm{u}^{n}(\bm{G})$.

**Feedback**:
This goes a step too far. Equation (5) shows that non-main components remain bounded as $C\to\infty$, while the main component grows like $\sqrt C$. That gives directional convergence, exactly as Proposition 1 states through cosine similarity, but it does not imply that the vector difference from $\sqrt C\,u^1$ or $\sqrt C\,u^n$ vanishes. The statement here, and the matching prose in the abstract and footnote 3, should be rewritten in asymptotic directional terms.

---

### 8. The substitutes-side bottom-gap comparative static is reversed

**Status**: [Pending]

**Quote**:
> If $\beta<0$, then the term $\alpha_{n-1}/(\alpha_{n-1}-\alpha_{n})$ is small when the “bottom gap” of the graph, the difference $\lambda_{n-1}-\lambda_{n}$, is small.

**Feedback**:
The sign and the monotonicity are both off here. Under strategic substitutes, Proposition 2 uses $\alpha_{n-1}/(\alpha_n-\alpha_{n-1})$, and when the bottom gap $\lambda_{n-1}-\lambda_n$ is small, the denominator goes to zero, so this ratio becomes large, not small. This matters because the paragraph is explaining when convergence to a simple policy is slow. A small bottom gap makes the threshold harder, not easier, to satisfy.

---

### 9. The circle example treats a nonunique eigenvector as unique

**Status**: [Pending]

**Quote**:
> The second principal component (top left panel of Figure 1) splits the graph intotwo sides, one with positive entries and the other with negative entries.

**Feedback**:
For a 14-node cycle, the non-extremal adjacency eigenvalues come in pairs. That means the second-largest eigenvalue has a two-dimensional eigenspace, so there is no unique “second principal component” or unique sign pattern attached to it. The figure can still show one convenient orthonormal basis vector, but the text should say that explicitly. Otherwise the example suggests a uniqueness that this graph does not have.

---

### 10. The Lagrangian in the proof of Theorem 1 drops a square

**Status**: [Pending]

**Quote**:
> Observe that the Lagrangian corresponding to the maximization problem is
>
> $\mathcal{L}=w\sum_{\ell}\alpha_{\ell}(1+x_{\ell})^{2}\hat{\underline{b}}_{\ell}+\mu\left[C-\sum_{\ell}\hat{\underline{b}}_{\ell}^{2}x_{\ell}^{2}\right].$
>
> Taking our observation above that the constraint is binding at $\bm{x}=\bm{x}^{*}$, together with the standard results on the Karush–Kuhn–Tucker conditions, the first-order conditions must hold exactly at the optimum with a positive $\mu$:
>
> $0=\frac{\partial\mathcal{L}}{\partial x_{\ell}}=2\hat{\underline{b}}_{\ell}^{2}\left[w\alpha_{\ell}(1+x_{\ell}^{*})-\mu x_{\ell}^{*}\right]=0.$ (10)

**Feedback**:
Equation (10) follows only if the first term in the Lagrangian is $w\sum_\ell \alpha_\ell (1+x_\ell)^2\hat{\underline b}_\ell^2$. As printed, differentiating gives a factor $\hat{\underline b}_\ell$, not $\hat{\underline b}_\ell^2$. This is a local fix, but an important one, because the closed-form expression for $x_\ell^*$ is derived from this step.

---

### 11. The variance-control proof permutes the covariance in the wrong basis

**Status**: [Pending]

**Quote**:
> Furthermore, the matrix
>
> $$
> \boldsymbol {\Sigma} _ {\mathcal {B} ^ {* *}} = \boldsymbol {P} \boldsymbol {\Sigma} _ {\mathcal {B} ^ {*}} \boldsymbol {P} ^ {\top}
> $$
>
> and so $\operatorname{Var}(\underline{b}_k^{**}) = \operatorname{Var}(\underline{b}_k^*)$ for all $k \notin \{\ell, \ell'\}$ and $\operatorname{Var}(\underline{b}_{\ell}^{*}) = \operatorname{Var}(\underline{b}_{\ell'}^{*}) > \operatorname{Var}(\underline{b}_{\ell'}^{*}) = \operatorname{Var}(\underline{b}_{\ell}^{*})$.

**Feedback**:
The swap argument should be written in the principal-component basis, not in the original coordinates. Since $\underline{\mathcal B}^{**}=P\underline{\mathcal B}^*$, the right covariance identity is $\Sigma_{\underline{\mathcal B}^{**}}=P\Sigma_{\underline{\mathcal B}^*}P^{\top}$. In original coordinates one has $\Sigma_{\mathcal B^{**}}=O\Sigma_{\mathcal B^*}O^{\top}$. Once the basis is corrected, the welfare comparison is straightforward: the permutation swaps the two projected variances while leaving the cost unchanged, and the higher weight should sit on the larger variance.

---

### 12. Bonacich centrality converges only after normalization

**Status**: [Pending]

**Quote**:
> Bonacich centrality converges to eigenvector centrality as the spectral radius of $\beta\bm{G}$ tends to 1; otherwise the two vectors can be quite different (see, for example, *Calvó-Armengol et al. (2015)* or *Golub and Lever (2010)*).

**Feedback**:
This needs a normalization qualifier. If Bonacich centrality is $(I-\beta G)^{-1}\mathbf 1$, its norm blows up as $\beta\lambda_1\uparrow 1$. What converges is the direction of the vector, for example after dividing by its norm. That is the standard near-instability comparison, and stating it that way would avoid a false literal convergence claim.

---

### 13. Smallest-eigenvalue targeting is not unique when the eigenvalue is repeated

**Status**: [Pending]

**Quote**:
> Last principal component: We have shown that in games with strategic substitutes, for large budgets interventions that aim to maximize the aggregate utility target individuals in proportion to the eigenvector of $\bm{G}$ associated to the smallest eigenvalue of $\bm{G}$, the last principal component.

**Feedback**:
This summary is too definite unless the smallest eigenvalue is simple. For graphs such as $K_3$, the smallest eigenvalue has multiplicity two, so there is no unique associated eigenvector and no unique targeting pattern of the form claimed here. The right statement is in terms of the smallest-eigenvalue eigenspace, with uniqueness only in the simple-eigenvalue case.

---

### 14. The beauty-contest intuition uses the wrong threshold for positive spillovers

**Status**: [Pending]

**Quote**:
> This is a game of strategic complements; moreover, an increase in $j$'s action has a positive effect on individual $i$'s utility if and only if $a_j < a_i$.

**Feedback**:
The derivative with respect to $a_j$ is $g_{ij}[(\tilde\beta+\gamma)a_i-\gamma a_j]$, so for a linked pair the effect is positive when $a_j<\frac{\tilde\beta+\gamma}{\gamma}a_i$, not when $a_j<a_i$. This is a small sentence, but it is presenting the economic intuition of the example, so it should match the algebra exactly.

---

### 15. Lemma OA1 gives the wrong normalization for the first eigenvector

**Status**: [Pending]

**Quote**:
> Lemma OA1.
>
> Assumption OA1 implies that:
>
> 1. for any $a\in\mathbb{R}^{n}$, $\sum_{i}\sum_{j}g_{ij}a_{j}=\sum_{i}a_{i}$ and $\sum_{i}\sum_{j}g_{ij}a_{j}^{2}=\sum_{i}a_{i}^{2}$
> 2. $\lambda_{1}(\bm{G})=1$ and $u_{i}^{1}(\bm{G})=\sqrt{n}$ for all $i$

**Feedback**:
Because $U$ is orthogonal, each eigenvector has unit norm. If $u_i^1$ is constant across $i$, that constant must be $1/\sqrt n$, not $\sqrt n$. Part 3 of the same lemma already uses the correct normalization implicitly, since $\sum_i b_i=\sqrt n\,\underline b_1$. So this line should be corrected for consistency and for the later formulas that depend on it.

---

### 16. Example OA1 overcounts the aggregate peer-effect term

**Status**: [Pending]

**Quote**:
> It can be checked that the aggregate equilibrium welfare is:
>
> $W(\bm{b},\bm{G})=\frac{1}{2}\,(\bm{a}^{*})^{\mathsf{T}}\,\bm{a}^{*}-n\gamma\sum_{i}a_{i}^{*},$ (OA-1)

**Feedback**:
Summing $-\gamma\sum_{j\neq i} a_j$ over players counts each action $a_j$ exactly $n-1$ times, not $n$ times. The aggregate term should therefore be $-(n-1)\gamma\sum_i a_i^*$. The later specialization to $w_3=-\gamma\sqrt n(n-1)$ is consistent with that corrected coefficient, so the issue seems to be local to this displayed formula.

---

### 17. The feasible interval for $x_1$ is missing a square root

**Status**: [Pending]

**Quote**:
> We fix $x_1$ so that $C(x_1) \geq 0$; that is, $x_1 \in [-C / \hat{\underline{b}}_1, C / \hat{\underline{b}}_1]$.

**Feedback**:
Since $C(x_1)=C-\hat{\underline b}_1^2 x_1^2$, the condition is $|x_1|\le \sqrt C/|\hat{\underline b}_1|$. The proof later uses the endpoints $\pm \sqrt C/\hat b_1$ in Lemma OA2, so the displayed interval should be corrected here as well. As written, it solves the wrong inequality.

---

### 18. Lemma OA2 drops the component weights in implicit differentiation

**Status**: [Pending]

**Quote**:
> $\frac{d\mu}{dx_{1}}=\frac{\hat{b}_{1}^{2}x_{1}}{\sum_{\ell=2}\frac{w_{1}^{2}\hat{b}_{1}^{2}\alpha_{\ell}^{2}}{(\mu-w_{1}\alpha_{\ell})^{3}}}$

**Feedback**:
The denominator should retain the original weights $\hat b_\ell^2$ from the budget equation. Implicit differentiation of
$$\sum_{\ell=2}\hat b_\ell^2\left(\frac{w_1\alpha_\ell}{\mu-w_1\alpha_\ell}\right)^2=C-\hat b_1^2x_1^2$$
gives
$$\frac{d\mu}{dx_1}=\frac{\hat b_1^2x_1}{\sum_{\ell=2}\hat b_\ell^2\frac{w_1^2\alpha_\ell^2}{(\mu-w_1\alpha_\ell)^3}}.$$
Replacing every $\hat b_\ell^2$ by $\hat b_1^2$ changes the derivative and the later calculation based on it.

---

### 19. The SVD extension writes the equilibrium coordinates incorrectly

**Status**: [Pending]

**Quote**:
> Let $\underline{\bm{a}}=\bm{V}^{\mathsf{T}}\bm{a}$ and $\underline{\bm{b}}=\bm{U}^{\mathsf{T}}\bm{b}$; then the equilibrium condition implies that:
>
> $\underline{a}_{\ell}^{*}=\frac{1}{s_{\ell}}b_{\ell}^{2},$

**Feedback**:
From $M a^*=b$ and $M=USV^{\top}$ one gets $S\underline a^*=\underline b$, so componentwise the relation is $\underline a_\ell^*=\underline b_\ell/s_\ell$. The printed formula has the wrong degree in $b$ and is inconsistent with the next line, where the welfare weights are taken to be $1/s_\ell^2$. This should be fixed before the SVD extension can be read as parallel to the symmetric case.

---

### 20. Lemma OA3 states the Taylor intuition but not the convergence it needs

**Status**: [Pending]

**Quote**:
> Consider the Taylor expansion of $\kappa$ around $\bm{0}$ ($\kappa$ is defined by part (1) of the assumption). We will now study its properties under parts (2) to (5) of Assumption OA2. (5) ensures that the Taylor expansion exists. Local separability (4) says that there are no terms of the form $y_{i}y_{j}$. Non-negativity (3) ($\kappa$ is nonnegative and $\kappa(\bm{0})=0$) implies that all first-order terms are zero. Also, (5) says that terms of the form $y_{i}^{2}$ must have positive coefficients, and symmetry (2) says that their coefficients must all be the same.

**Feedback**:
This identifies the quadratic term, but it stops before proving the lemma. What is still needed is a remainder estimate of the form $\kappa(y)=k\|y\|^2+r(y)$ with $r(y)=o(\|y\|^2)$ as $y\to 0$, and then the uniform conclusion on compact sets after substituting $y=C^{1/2}z$. Without that step, the later appeal to uniform convergence in the Berge argument is not yet established.

---

### 21. The Berge argument needs a uniqueness step

**Status**: [Pending]

**Quote**:
> The Theorem of the Maximum therefore implies that the maximized value is continuous at $C=0$. Because the convergence of the objective is actually uniform on $\mathcal{K}$ by the Lemma, this is possible if and only if $\check{\bm{y}}$ approaches the solution of the problem

**Feedback**:
Berge's theorem gives continuity of the value function and upper hemicontinuity of the argmax correspondence. It does not by itself imply convergence of optimizers to a single point, especially since the text explicitly allows the optimizer set to be set-valued. The safe conclusion is that every accumulation point of $\check y^*(C)$ lies in the argmax set of the limit problem. If you want convergence to one point, the limit problem needs a separate uniqueness argument.

---

### 22. The linear-cost proof should use strict convexity instead of the chord argument

**Status**: [Pending]

**Quote**:
> The point $\bm{b^{*}}$ is contained in the interior of $L$; thus $\bm{b^{*}}$ is in the interior of $E$. On the other hand, $\bm{b^{*}}$ must be on the (elliptical) boundary of $E$ because $U$ is strictly increasing in each component (by irreducibility of the network) and continuous. This is a contradiction.

**Feedback**:
The key step is not valid: being in the interior of a chord does not imply being in the interior of the full convex set. A boundary point of an ellipse can lie in the interior of a line segment contained in that ellipse. There is a cleaner proof available. Since $a(b)=Mb$ with $M=(I-\beta G)^{-1}$, one has $W(b)=b^{\top}M^{\top}Mb$, and $M^{\top}M$ is positive definite. So $W$ is strictly convex. If an optimum under the $\ell_1$ budget sat in the interior of a feasible line segment, one endpoint would have strictly higher welfare, which is the contradiction you need.

---

### 23. Assumption OA2 allows zero-cost interventions far from the origin

**Status**: [Pending]

**Quote**:
> Let us restrict $\mathrm{IT}(C)$ to a compact set $\mathcal{K}$ such that the constraint set $\{\bm{y}:C^{-1}\kappa(C^{1/2}\check{\bm{y}})\leq 1\}$ is contained in $\mathcal{K}$ for all small enough $C$.

**Feedback**:
This compactness step does not follow from Assumption OA2 alone. A function such as $\kappa(y)=\sum_i y_i^2(1-y_i)^2$ satisfies the listed local conditions, yet it gives zero cost at nonzero points like $e_i$. Then small budgets do not force feasible interventions into a neighborhood of the origin, and the rescaled feasible sets are not contained in any fixed compact set. The proposition needs an extra positivity/coercivity condition ensuring that small budgets imply small interventions.

---
