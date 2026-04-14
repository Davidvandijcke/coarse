# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 04/13/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper has an elegant spectral decomposition and a clear core insight, but the framing is broader than the results the main text actually establishes. The sharp targeting rules hinge on a narrow combination of assumptions: symmetric networks, distinct eigenvalues, quadratic intervention costs, and welfare proportional to \((\boldsymbol a^*)^\top \boldsymbol a^*\). The places where policy relevance should be strongest, especially large-budget targeting, strategic substitutes, and incomplete information, are also the places where feasibility restrictions or additional assumptions do the most work.

The paper's main contribution is a clean way to express intervention problems in the eigenbasis of the interaction matrix, and that gives a readable characterization in Theorem 1. The link between strategic complements versus substitutes and the ranking of components is interesting, and the paper does a good job explaining the basic algebra. The problem is that several headline claims about breadth, policy relevance, and incomplete-information robustness are not yet matched by the model class actually solved in the main text.

**The main theorem is tied to a much narrower class of objectives than the framing suggests**

Section 2 introduces a fairly broad planner problem with pure externalities \(P_i\), but the main characterization in Theorem 1 only goes through after imposing Property A and the quadratic budget set in problem (IT). That is a much smaller class than the introduction and conclusion imply. The limitation matters because the extensions already show the ranking logic is not invariant once welfare departs from \(w(\boldsymbol a^*)^\top \boldsymbol a^*\): in OA3.1, Theorem OA1, the large-budget target can depend on a comparison between \((w_1+w_2)\alpha_1\) and \(w_1\alpha_n\), so the simple complements-versus-substitutes split from Section 4 no longer summarizes the answer. OA3.3 makes a similar point on the cost side, where only a local small-budget analogue survives for general costs. The paper should either narrow its claim sharply in the abstract, introduction, and conclusion, or move the robustness analysis into the main text and state explicitly which comparative statics are truly stable beyond Property A and quadratic costs.

**The headline large-budget prescriptions rely on action and intervention sets that are hard to defend in the flagship applications**

The core asymptotic message in Proposition 1 and Definition 2 is that, for large budgets, the planner should move along a single eigenvector, often the last one under strategic substitutes. But the model in Section 2 allows \(a_i \in \mathbb{R}\) and arbitrary positive or negative shifts in \(b_i\), while the economic examples in Section 2 are investment and local public goods, where nonnegative actions and one-sided subsidies are the natural benchmark. The paper briefly notes after Corollary 1 that a nonnegativity constraint on actions is respected only for budgets below some \(\hat C\), yet the large-budget results and the \(C \to \infty\) asymptotics are exactly what the paper emphasizes. Under strategic substitutes, the optimal simple intervention typically requires raising incentives for one set of nodes and lowering them for another in proportion to \(\boldsymbol u^n\), which may mean taxes, negative effort targets, or both. This matters because the most policy-facing claim of the paper may sit outside the economically meaningful region in its own examples. A revision should solve the constrained problem with \(a_i \ge 0\) and, if relevant, one-sided interventions \(b_i \ge \hat b_i\), or else treat the large-budget result as a mathematical benchmark and show finite-budget constrained analogues.

**The incomplete-information section largely collapses back to the complete-information benchmark**

Section 5 is presented as an extension to incomplete information, but the timing immediately removes the main strategic content of such a problem: realized \(\boldsymbol b\) is common knowledge to agents when they choose actions. That means the game agents play is still complete information, and the planner's uncertainty is only ex ante. Proposition 3 then reduces the mean-shift problem to the deterministic case with status quo \(\mathbb E[\hat{\boldsymbol b}]\), while Proposition 4 depends on Assumption 5's rotational symmetry so that only variances of principal components matter. Those are clean results, but they do not show that the principal-components prescription survives richer informational frictions such as private signals, noisy network knowledge, or network misspecification by the planner. Since the paper itself motivates targeting as a policy problem, this is a substantial gap. The revision should either rename Section 5 more narrowly as moment-control under planner uncertainty, or add a genuinely incomplete-information model in which agents and planner do not share the realized \(\boldsymbol b\) or the network and then show what remains of the spectral targeting logic.

**The distinct-eigenvalue assumption is doing more work than the paper admits**

Assumption 2 requires all eigenvalues of \(\boldsymbol G\) to be distinct, and the paper treats this as a generic convenience. In this setting, however, the identity of the targeted component is part of the economic prescription, so multiplicity is not a harmless technicality. Many canonical symmetric graphs have repeated eigenvalues, and the paper's own Example 3 in Section 5 uses a 14-node circle, which is a standard case with repeated eigenvalues and non-unique eigenvectors inside eigenspaces. Once multiplicity appears, statements about the ordering of principal components, the direction of the 'last' component, and the content of a simple intervention become basis-dependent rather than invariant. That weakens both interpretation and implementation, because different orthogonal bases for the same eigenspace generate different node-level targeting vectors with the same objective value. The right fix is to restate the results in terms of eigenspaces or orthogonal projectors, and to revise the examples so the policy prescription is invariant to arbitrary basis choices.

**The paper does not show when the principal-components machinery changes policy relative to simpler heuristics**

The introduction positions the paper as a normative advance over familiar centrality-based intuitions, but the main text never quantifies when the full solution materially outperforms simpler rules. Under strategic complements and large budgets, Proposition 1 drives the answer back to the first eigenvector; under small budgets, the optimal intervention is essentially a component-wise rescaling of the status quo. OA2.1 discusses Bonacich and eigenvector centrality, but only verbally, and Figures 2 and 3 are illustrative rather than comparative welfare exercises. For a methodological paper, that is a real omission, because readers need to see when the extra spectral structure matters enough to change a planner's recommendation. The revision should add either analytical comparisons or calibrated examples that report welfare gaps relative to degree targeting, eigenvector-centrality targeting, Bonacich targeting, and single-node targeting across complements, substitutes, and different spectral-gap regimes.

**Section 4 contains a threshold inconsistency in the negative-welfare case**

The paragraph opening Section 4 says that when \(w<0\), the planner can set \(b_i=0\) for all \(i\) and reach the first best whenever \(C \ge \|\hat{\boldsymbol b}\|^2\), which matches the budget formula \(K(\boldsymbol b,\hat{\boldsymbol b}) = \sum_i (b_i-\hat b_i)^2\). Assumption 3 then states the nontrivial case as 'Either \(w<0\) and \(C<\|\hat{\boldsymbol b}\|\), or \(w>0\).' That is not the same threshold, and it also has the wrong units relative to the quadratic budget set. Because Theorem 1 and Corollary 1 are stated under Assumption 3, the admissible domain of the main results is not currently specified correctly. This should be corrected to the squared norm threshold and checked throughout Section 4 and the appendix wherever Assumption 3 is invoked.

**No closed-form benchmark network solved fully**

The paper has applications and figures, but it never works through Theorem 1 on a network where the eigenstructure is explicit. That leaves the main mechanism a bit too abstract for a paper whose contribution is the principal-components decomposition itself. Readers should be able to see, on paper, how the weight formula changes with \(\beta\), the budget \(C\), and the status quo profile \(\hat{\boldsymbol b}\). A natural benchmark is a star, a complete graph, or a two-block network, since the eigenvalues and eigenvectors are simple and economically interpretable. The paper should compute equation (5) and solve equation (6) for one of these models, then report the node-level intervention under both \(\beta>0\) and \(\beta<0\). That would make the "global" versus "local" language concrete and show exactly when the status-quo term \(\rho(\hat{\boldsymbol b},\boldsymbol u^\ell)\) changes the ranking implied by \(\alpha_\ell\).

**Proposition 2 lacks a bite check**

The simplicity result is one of the paper's headline takeaways, yet the paper never shows whether the bound in Proposition 2 is informative on networks economists actually use. A sufficient condition can be correct and still be so loose that it gives almost no guidance. That matters here because the abstract and conclusion both lean on the message that large budgets collapse the problem to a single principal component. The paper should add a numerical exercise that evaluates the threshold \(C_\epsilon=\frac{2\|\hat{\boldsymbol b}\|^2}{\epsilon}\left(\frac{\alpha_2}{\alpha_1-\alpha_2}\right)^2\) and its strategic-substitutes analogue on standard graph families such as a star, a path, a bipartite graph, and a two-community graph. For each case, it should compare the bound to the exact welfare loss \(W^*/W^s-1\) from solving (IT). That would show when Proposition 2 is sharp, when it is conservative, and whether the large-budget prescription has real content beyond an asymptotic slogan.

**Variance-control results need a concrete policy construction**

Section 5.2 gives an ordering of optimal variances across principal components, but it never shows what an optimal distribution actually looks like under a specific admissible cost. As written, the incomplete-information contribution stays at the level of comparative statics. Readers learn which components should receive more variance, but not how that becomes a covariance matrix over individuals. A worked construction would fix that. One clean option is to take cost function (9) with \(\phi(t)=t\), restrict attention to Gaussian interventions \(\mathcal B\sim N(\bar{\boldsymbol b},\Sigma)\), and solve explicitly for the optimal \(\Sigma\) in the principal-component basis. On a circle or star network, the paper could then transform that \(\Sigma\) back to node space and display the implied pattern of positive and negative covariances across neighbors.

**No guidance for computing targets from estimated primitives**

The planner's prescription depends on \(\beta\), the full interaction matrix, the status quo vector, and in Section 5 the relevant moments of the shock distribution. The paper treats these objects as known, but it does not discuss how stable the target vector is when they are estimated with error. That is a real gap because equation (5) is not just qualitative; it produces a high-dimensional intervention that can move a lot when eigenvalues are close or when \(\mu\) is near \(w\alpha_\ell\). The paper does not need an empirical identification section, but it does need an implementation section explaining what must be measured and how errors propagate into the policy rule. A useful addition would be a perturbation exercise: derive a first-order approximation, or a Davis-Kahan style bound, for the change in the leading target direction when \(\boldsymbol G\) or \(\beta\) is misspecified. The authors could then illustrate that bound on a two-community graph with a small spectral gap and on a star with a large gap, so readers can see when the spectral prescription is usable and when it is fragile.

**Recommendation**: major revision. The spectral decomposition is elegant and the main theorem is interesting, but the paper's broader claims about intervention design, incomplete information, and policy relevance run ahead of what the baseline model and extensions establish. A revision that tightens the scope, fixes the threshold inconsistency, and confronts feasibility and robustness more directly would make the contribution much more convincing for a top field audience.

**Key revision targets**:

1. Make the scope of the main contribution match the actual theorem: either narrow the claims in the abstract, introduction, and conclusion to the Property A plus quadratic-cost setting, or bring the OA3.1 and OA3.3 robustness results into the main text and state exactly which comparative statics survive beyond that baseline.
2. Analyze the planner's problem under economically natural constraints, especially \(a_i \ge 0\) and, where appropriate, one-sided interventions, and show how Proposition 1, Proposition 2, and the strategic-substitutes prescriptions change once those constraints are imposed.
3. Replace or substantially deepen Section 5 so it treats a genuinely incomplete-information environment rather than an ex ante moment-control problem with realized \(\boldsymbol b\) common knowledge to agents.
4. Generalize the spectral statements to repeated eigenvalues by formulating the prescriptions at the eigenspace level, and revise Example 3 and related discussion so the target is invariant to basis choice.
5. Add formal comparisons between the proposed targeting rule and simpler heuristics such as degree, eigenvector centrality, Bonacich centrality, and single-node targeting, with welfare comparisons across complement/substitute and spectral-gap regimes.

**Status**: [Pending]

---

## Detailed Comments (8)

### 1. Theorem 1 Drops a Real KKT Case

**Status**: [Pending]

**Quote**:
> Define $x_{\ell} = (\underline{b}_{\ell} - \hat{\underline{b}}_{\ell}) / \hat{\underline{b}}_{\ell}$ as the change of $\underline{b}_{\ell}$, relative to $\hat{\underline{b}}_{\ell}$.

**Feedback**:
This reparametrization breaks exactly where the theorem still claims to apply: when some status-quo loading $\hat{\underline b}_{\ell}$ is zero. In that case the issue is not just a proof gap. The formula can give the wrong intervention. Take the two-node network with $G=\begin{pmatrix}0&1\\1&0\end{pmatrix}$, $\beta=1/2$, $w=1$, and $C=1$. In principal-component coordinates the eigenvalues are $1$ and $-1$, so $\alpha_1=4$ and $\alpha_2=4/9$. If the status quo is $\hat b=(0,1)$ in that basis, the true problem is to maximize $4y_1^2+\frac{4}{9}(1+y_2)^2$ subject to $y_1^2+y_2^2\le 1$. The optimum has $y_2=1/8$ and $y_1=\sqrt{63}/8\neq 0$. But equation (5) forces zero weight on the first component because $\rho(\hat b,u^1)=0$. So the statement of Theorem 1 needs a separate treatment for zero projections, with the Kuhn-Tucker case handled directly in the $y_{\ell}$ variables rather than through $x_{\ell}$.

---

### 2. The OA3.1 Welfare Decomposition Is Miscomputed

**Status**: [Pending]

**Quote**:
> with:
>
> $w_{1}$ $=$ $1+m_{2}+m_{5}+(n-1)m_{4}$
> $w_{2}$ $=$ $nm_{5}(n-2)$
> $w_{3}$ $=$ $\sqrt{n}[m_{1}+(n-1)m_{3}].$

**Feedback**:
These coefficients are not what follows from the displayed payoff. Let $Q=\sum_i a_i^{*2}$ and $S=\sum_i a_i^*$. At equilibrium, $\sum_i \hat U_i(a^*,G)=\tfrac12 Q$. Also, $\sum_i \sum_j g_{ij} a_j^{*2}=Q$, $\sum_i \sum_{j\ne i} a_j^{*2}=(n-1)Q$, and $\sum_i (\sum_{j\ne i} a_j^*)^2=(n-2)S^2+Q$. Substituting gives
$W=\left(\tfrac12+m_2+m_4+(n-1)m_5\right)Q + m_4(n-2)S^2 + [m_1+(n-1)m_3]S.$
So the baseline coefficient on $Q$ should start from $1/2$, not $1$, and the $m_4$ and $m_5$ terms are swapped in the text. Because Theorem OA1 is built on these weights, the extension needs to be recomputed from the corrected decomposition.

---

### 3. The PCA Analogy Is Not Right

**Status**: [Pending]

**Quote**:
> The first principal component of $\bm{G}$ is defined as the $n$-dimensional vector that minimizes the sum of squares of the distances to the columns of $\bm{G}$. The first principal component can therefore be thought of as a fictitious column that “best summarizes” the dataset of all columns of $\bm{G}$.

**Feedback**:
This paragraph mixes up three different objects: the column mean, uncentered PCA, and the spectral decomposition you actually use later. Minimizing $\sum_j \|g_j-v\|^2$ picks $v=\frac1n\sum_j g_j$, the centroid of the columns, not a principal-component direction. If the goal is an uncentered PCA story, one maximizes $u^\top G G^\top u$; for symmetric $G$ that ranks directions by $|\lambda_\ell|$, not by raw $\lambda_\ell$. As written, the data-analysis interpretation is mathematically wrong. I would either drop the PCA analogy or restate it in standard spectral terms and keep the argument tied to Fact 1 and equation (4).

---

### 4. The "Network Multiplier" Is Misidentified

**Status**: [Pending]

**Quote**:
> This basis has three special properties: (a) the effects of an intervention along a principal component is proportional to the intervention, scaled by a network multiplier; (b) the “network multiplier” is an eigenvalue of the network corresponding to that principal component;

**Feedback**:
Section 3 uses a different object. If the intervention moves only along component $\ell$, equation (4) gives $\underline a_\ell^*=\frac{1}{1-\beta\lambda_\ell}\,\underline b_\ell$. So the multiplier is $1/(1-\beta\lambda_\ell)$, not $\lambda_\ell$ itself. That distinction matters because the welfare weights later become $\alpha_\ell=(1-\beta\lambda_\ell)^{-2}$. A short rewrite would fix this: the eigenvalue determines the multiplier, but it is not the multiplier.

---

### 5. The Finite-Budget Ranking Still Depends on the Status Quo

**Status**: [Pending]

**Quote**:
> In games of strategic complements, the optimal intervention is most similar to the first principal component – the familiar eigenvector centrality – and progressively less similar as we move down the principal components. In games of strategic substitutes, the order is reversed: the optimal intervention is most similar to the last principal component.

**Feedback**:
This sentence reads as a ranking of the raw component loadings of the intervention. Corollary 1 does not give that. It orders the similarity ratios, and the actual loading on component $\ell$ still carries the factor $\hat b_\ell$. A concrete example shows the gap. On the two-node network above, with $\beta=1/2$, $w=1$, and status-quo coordinates $(\hat b_1,\hat b_2)=(0.01,1)$, the theorem gives
$\frac{y_1^*}{y_2^*}=0.01\cdot \frac{\alpha_1}{\alpha_2}\cdot \frac{\mu-\alpha_2}{\mu-\alpha_1}$.
For small budgets, $\mu$ is large, so this ratio is close to $0.01\cdot 9=0.09<1$. The second component therefore has the larger loading even under complements. I would restate the result as a tilt relative to the status-quo vector, and reserve near-pure first/last-component language for the large-budget limit.

---

### 6. The Application Labels Treat Externality Signs as Fixed When They Are Not

**Status**: [Pending]

**Quote**:
>  marginal returns are enhanced when his neighbors work harder; this creates both strategic complementarities and positive externalities. The case of $\beta<0$ corresponds to strategic substitutes and negative externalities; thi

**Feedback**:
The strategic-complements and strategic-substitutes labels are fine. The externality labels are too blunt once actions are allowed to be negative. In Example 1, holding $a_i$ fixed, $\partial U_i/\partial a_j = \beta g_{ij} a_i$. In Example 2, $\partial U_i/\partial a_j = \tilde\beta g_{ij}(\tau-x_i)$, which at an interior equilibrium equals $\tilde\beta g_{ij} a_i$. In both examples the spillover sign therefore tracks the recipient's action, not the sign of $\beta$ alone. Since the baseline model takes $a_i\in\mathbb R$, the text should either add the sign restriction on actions that makes the claim true or soften the wording to say that these specifications can generate positive or negative externalities.

---

### 7. The Proposition 4 Proof Switches Bases Mid-Argument

**Status**: [Pending]

**Quote**:
> Define $\mathcal{B}^{**} = \mathcal{O}\mathcal{B}^*$ with $\pm m{O} = \pm m{U}\pm m{P}\pm m{U}^{\top}$. Clearly, $\pm m{O}$ is orthogonal, as $\pm m{U}$ and $\pm m{P}$ are both orthogonal. Hence, by Assumption 5, $K(\mathcal{B}^{*}) = K(\mathcal{B}^{**})$. Furthermore, the matrix
>
> $$
> \boldsymbol {\Sigma} _ {\mathcal {B} ^ {* *}} = \boldsymbol {P} \boldsymbol {\Sigma} _ {\mathcal {B} ^ {*}} \boldsymbol {P} ^ {\top}
> $$

**Feedback**:
The permutation argument should be written in principal-component coordinates. With $O=UPU^\top$, the covariance in original coordinates is $\Sigma_{\mathcal B^{**}} = O\Sigma_{\mathcal B^*}O^\top$. What gets permuted by $P$ is $\Sigma_{\underline{\mathcal B}^{**}} = P\Sigma_{\underline{\mathcal B}^*}P^\top$. The next line also needs the swapped identities $\operatorname{Var}(\underline b_\ell^{**})=\operatorname{Var}(\underline b_{\ell'}^*)$ and $\operatorname{Var}(\underline b_{\ell'}^{**})=\operatorname{Var}(\underline b_\ell^*)$. As written it compares starred variances to themselves, so the contradiction does not follow. I think the result can be saved, but the proof should be rewritten in the transformed basis.

---

### 8. Theorem 1 Needs a Separate Zero-Budget Case

**Status**: [Pending]

**Quote**:
> Theorem 1. Suppose Assumptions 1–3 hold and the network game satisfies Property A. At the optimal intervention, the similarity between $\boldsymbol{y}^*$ and principal component $\boldsymbol{u}^\ell(\boldsymbol{G})$ satisfies the following proportionality:

**Feedback**:
As stated, Assumption 3 still allows $w>0$ and $C=0$. Then the feasible set is just $y^*=0$, but every cosine similarity in equation (5) is undefined because $\|y^*\|=0$, and equation (6) has no finite solution unless one treats $\mu=\infty$ as a limit. A one-line restriction to $C>0$, with a separate remark for the zero-budget boundary case, would clean this up.

---
