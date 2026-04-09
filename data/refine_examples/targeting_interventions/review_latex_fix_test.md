# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/06/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Dependence of Principal Component Ordering on Welfare Specification**

Theorem 1 and Corollary 1 establish the ordering of principal components in optimal interventions, relying critically on Property A defined in Section 2. This property requires aggregate welfare to be proportional to the sum of squared equilibrium actions, a condition many economic applications involving linear terms or cross-products may not satisfy. Readers might note that when welfare includes distributional concerns or heterogeneous marginal utilities, the clean monotonicity result in Corollary 1 may not hold. It would be helpful to clarify in Section 4 the extent to which the principal component ranking is robust to deviations from Property A, perhaps by discussing the magnitude of linear terms required to reverse the ordering.

**Sensitivity of Large-Budget Simplicity to Cost Function Form**

Propositions 1 and 2 characterize optimal interventions for large budgets as simple, aligning with a single principal component, assuming a quadratic cost function. However, Online Appendix Section OA3.3 demonstrates that under linear costs, the optimal intervention targets a single individual rather than a network component. This suggests the simplicity result is specific to quadratic costs rather than a general feature of large budgets. It would be beneficial to qualify the claims in Section 4.2 to explicitly note that the convergence to a single principal component depends on the curvature of the cost function.

**Core Results Restricted to Symmetric Interaction Matrices**

Assumption 1 requires the adjacency matrix $G$ to be symmetric, which underpins the eigenvector decomposition used in Theorem 1. For directed networks common in economic applications, the left and right singular vectors differ, complicating the interpretation of targeting a component. While Section OA3.2 extends the methodology to non-symmetric matrices using Singular Value Decomposition, the main text intuition relies on eigenvector centrality. It would be helpful to integrate the SVD interpretation more prominently in Section 3 or clarify the limitations of applying the symmetric results to directed networks.

**Robustness to Network Measurement Error and Spectral Constraints**

The analysis presumes the planner knows the adjacency matrix $G$ perfectly and that the spectral radius of $\beta G$ is less than 1 to ensure equilibrium uniqueness. Given that spectral decomposition can be sensitive to perturbations in matrix entries, especially when eigenvalues are close, this assumption represents a significant scope limitation. Readers might note that in practical policy settings, network links are often estimated with error, and policy recommendations near the spectral radius threshold could carry significant risk. It would be helpful to discuss in Section 6 how measurement error in $G$ might affect the stability of the recommended intervention vectors.

**Exogenous Network Structure Ignores Endogenous Responses**

The adjacency matrix $G$ is treated as fixed and exogenous throughout Sections 2-4, meaning the planner intervenes on $b$ but cannot affect the network structure itself. This is a significant limitation for policy applications, as individuals may respond to interventions by altering their network connections, changing $G$ and thus rendering the spectral decomposition used to design the intervention inapplicable. It would be helpful to add a scope limitation in Section 4 acknowledging that the results apply only when network structure is sufficiently stable relative to the intervention timeline.

**Property A Restriction on Welfare Function**

The main characterization results (Theorem 1, Propositions 1-2) formally require Property A, which stipulates that aggregate equilibrium utility is proportional to the sum of squared actions ($W \propto \sum a_i^2$). However, the introduction cites applications such as peer effects in smoking (Jackson et al., 2017) which often involve negative externalities not captured by this specific quadratic form. As acknowledged in Example OA1 and Section OA3.1, when Property A is violated (e.g., welfare includes linear terms or cross-terms in actions), the objective function in the principal component basis is no longer purely diagonal in the same manner, and the optimal intervention characterization changes (e.g., $b_1$ enters both linearly and quadratically). It would be helpful to clarify in the main text that the simple principal component targeting rules are specific to this welfare structure, explicitly directing readers to Online Appendix OA3.1 for the generalized characterization to avoid misapplication to games with non-quadratic externalities.

**Symmetry Assumption and Directed Network Interpretations**

Assumption 1 requires the adjacency matrix $G$ to be symmetric to ensure real eigenvalues and an orthogonal eigenvector basis ($G = U \Lambda U^\top$). This assumption underpins the interpretation of the first principal component as 'eigenvector centrality' in Section 4.1. However, many empirical networks relevant to intervention (e.g., citation, trade, information flow) are directed, where eigenvalues can be complex and left/right eigenvectors differ. While Online Appendix OA3.2 extends the analysis using Singular Value Decomposition (SVD) for non-symmetric $G$, the main text presents the symmetric case as the primary framework without sufficient qualification. Readers might note that applying the 'eigenvector centrality' rule to directed networks without adjustment could be misleading, as the spectral properties differ. It would be beneficial to explicitly state in Section 4 that the centrality interpretation strictly applies to undirected networks, referencing the SVD extension for directed cases.

**Distinct Eigenvalues Assumption vs. Circle Network Illustration**

Assumption 2 requires that 'all eigenvalues of G are distinct' to ensure the principal component decomposition is uniquely determined (up to sign). However, Figure 1 uses a circle network with 14 nodes to illustrate these principal components. In spectral graph theory, cycle graphs $C_n$ for $n \geq 3$ typically have repeated eigenvalues (specifically, $\lambda_k = \lambda_{n-k}$ for the adjacency matrix), violating the distinct eigenvalue condition. Footnote 11 acknowledges this, stating the network is 'nongeneric in that eigenvectors are not uniquely determined.' While the defense that 'an arbitrarily small perturbation... will select a unique basis' is theoretically sound for genericity arguments, it creates a direct inconsistency between the formal assumption required for the unique decomposition in Theorem 1 and the specific data structure used to visualize it. It would be helpful to note that the visual representation in Figure 1 depicts one possible basis from a degenerate subspace, rather than the unique principal components guaranteed by Assumption 2.

**Status**: [Pending]

---

## Detailed Comments (19)

### 1. Network Multiplier Description Accuracy

**Status**: [Pending]

**Quote**:
> the 'network multiplier' is an eigenvalue of the network corresponding to that principal component

**Feedback**:
In standard linear-quadratic network games with equilibrium $a = (I - \beta G)^{-1}b$, decomposing $b$ in the eigenvector basis of $G$ gives $a = \sum_i c_i/(1 - \beta\lambda_i) u_i$. The actual multiplier for component $i$ is $1/(1 - \beta\lambda_i)$, which is a function of the eigenvalue $\lambda_i$, not $\lambda_i$ itself. It would be helpful to clarify that the eigenvalue determines the multiplier through this functional relationship, as readers familiar with network game theory may expect the multiplier to be $1/(1 - \beta\lambda_i)$ rather than $\lambda_i$ directly.

---

### 2. Example 1 Utility Labeling Contradicts Welfare Definition

**Status**: [Pending]

**Quote**:
> ty of i is
> 
> $$\mathbb{E}[W(\boldsymbol{b}, \boldsymbol{G})] = w\mathbb{E}[(\boldsymbol{a}^*)^\top \boldsymbol{a}^*] = w\mathbb{E}[\boldsymbol{a}^\top \boldsymbol{a}] = w \sum_\ell \alpha_\ell \left( \mathbb{E}[\underline{b}_\ell]^2 + \text{Var}[\underline{b}_\ell] \right). \quad (8)$$
> 
> The case with β &gt; 0 is the canonical case of investment complementarities as in Ballester et al. (2006). Here, an individual's marginal returns are e

**Feedback**:
The text labels Equation (8) as 'The utility of i is', but the equation defines $\mathbb{E}[W(\boldsymbol{b}, \boldsymbol{G})]$, which is Expected Aggregate Welfare. Earlier in the section, $W$ is explicitly defined as the sum of equilibrium utilities ($W = \sum_i U_i$). For $n \geq 2$, individual utility $U_i$ cannot equal aggregate welfare $W$. This labeling contradicts the section's own definitions and should read 'The expected social welfare is'.

---

### 3. Example 2 Welfare Form Ambiguously Violates Property A

**Status**: [Pending]

**Quote**:
>  / 2 and β = -˜ β/ 2 (with the status quo equal to ˆ b i = [ τ -˜ b i ] / 2) yields a best-response structure exactly as in condition (2). The aggregate equilibrium utility is W ( b , G ) = -( a ∗ ) T a ∗ .
> 
> These two canonical examples share a technically convenient property:
> 
> Property A. The aggregate equilibrium utility is proportional to the sum of the squares of the equilibrium actions, that is, W ( b , G ) = w · ( a ∗ ) T a ∗ for some w ∈ R , where a ∗ is the Nash equilibrium of the network game.
> 
> Online A

**Feedback**:
The text claims Example 2 satisfies Property A ($W \propto \boldsymbol{a}^\top \boldsymbol{a}$). However, the displayed welfare equation for Example 2 includes terms $\frac{w_2}{n} (\sum a_i)^2$ and $\frac{w_3}{\sqrt{n}} \sum a_i$. Unless $w_2 = w_3 = 0$, these terms prevent $W$ from being proportional to $\sum a_i^2$. The text later states $W = -(a^*)^\top a^*$, implying the terms vanish, but the initial display suggests they are part of the model, creating a logical gap in verifying Property A.

---

### 4. Ambiguity in Spectral Ordering Terminology

**Status**: [Pending]

**Quote**:
> In games of strategic complements (substitutes), interventions place more weight on the top (bottom) principal components, which reflect more global (local) network structure.

**Feedback**:
Readers might note that the term 'bottom' principal components is ambiguous in spectral graph theory, as it could refer to eigenvalues with the smallest magnitude (closest to zero) or the algebraically smallest values (most negative). For strategic substitutes, the optimal intervention relies on the algebraically smallest eigenvalues (most negative) to maximize the multiplier effect, not necessarily those with small magnitude. It would be helpful to rewrite 'top (bottom)' as 'largest (algebraically smallest)' to ensure the spectral ordering is unambiguously understood.

---

### 5. Conflation of G Assumptions and Welfare Structure

**Status**: [Pending]

**Quote**:
> This section introduces a basis for the space of standalone marginal returns and actions in which, under our assumptions on G , strategic effects and the welfare function of interest to the planner both take a simple form.

**Feedback**:
The phrasing implies that the welfare function's simple form follows from assumptions on $G$. Since welfare simplification depends on Property A rather than network topology, readers might infer an unnecessary dependency. It would be helpful to separate these conditions to clarify that strategic diagonalization follows from $G$ while welfare simplification follows from Property A.

---

### 6. Principal Component Definition Versus Eigenvalue Ordering

**Status**: [Pending]

**Quote**:
> The first principal component of G is defined as the n -dimensional vector that minimizes the sum of squares of the distances to the columns of G .

**Feedback**:
This definition describes Principal Component Analysis (PCA) on the columns of $G$, which identifies the direction of maximum variance. Mathematically, this corresponds to the eigenvector of $G^T G = G^2$ with the largest eigenvalue, ordering components by magnitude $|\lambda_\ell|$. However, the text orders eigenvalues algebraically ($\lambda_1 \geq \lambda_2$) and treats $u^1$ as the first component. It would be helpful to clarify that 'principal component' here refers to the spectral decomposition ordering by algebraic value, distinguishing it from standard variance-based PCA.

---

### 7. Sign Error in Proposition 2 Discussion Denominator

**Status**: [Pending]

**Quote**:
> -λ 2 , the 'spectral gap' of the graph, is small. If β &lt; 0, then the term α n -1 / ( α n -1 -α n ) is small when the 'bottom gap' of the graph, the difference λ n -1 -λ n , is small.
> 
> We now exam

**Feedback**:
For $\beta < 0$ (strategic substitutes), we have $\alpha_n > \alpha_{n-1}$ since $\alpha_\ell = (1 - \beta\lambda_\ell)^{-2}$ and $\lambda_n$ is the most negative eigenvalue. This means $\alpha_{n-1} - \alpha_n < 0$, making the denominator negative. However, Proposition 2 part 2 states the budget bound with $\alpha_n - \alpha_{n-1}$ in the denominator (positive). The discussion text incorrectly writes $\alpha_{n-1} - \alpha_n$, which would yield a negative ratio. The correct expression should read $\alpha_{n-1}/(\alpha_n - \alpha_{n-1})$ to match the proposition formula.

---

### 8. Welfare Decomposition Conflates Realization and Distribution Moments

**Status**: [Pending]

**Quote**:
> -not-decoded -->
> 
> In words, welfare is determined by the mean and variance of the realized components b glyph[lscript] ; these in turn are determined by the first and second moments of the chosen random variable B . In view of this, we will consider intervention problems where the p

**Feedback**:
The welfare decomposition under Property A yields $E[W] \propto \sum_\ell [1/(1-\beta\lambda_\ell)^2] \times E[b_\ell^2] = \sum_\ell [1/(1-\beta\lambda_\ell)^2] \times (Var(b_\ell) + (E[b_\ell])^2)$. The text states welfare depends on 'the mean and variance of the realized components $b_\ell$', but a single realization $b_\ell$ does not have a mean or variance—these are distributional properties. The correct statement is that expected welfare depends on the mean $E[b_\ell]$ and variance $Var(b_\ell)$ of the distribution of $B_\ell$, not of the realization.

---

### 9. Property A Misidentified as Externality Restriction

**Status**: [Pending]

**Quote**:
> We also relax Property A, a technical condition which facilitated our basic analysis, and cover a more general class of externalities.

**Feedback**:
Property A is formally defined in the paper (Section 2) as a restriction on the planner's welfare function (specifically, $W \propto \sum a_i^2$), rather than on the network interaction matrix $G$ which governs externalities. Consequently, relaxing Property A expands the set of admissible welfare specifications, not the class of network externalities themselves. It would be more precise to state that the extension covers a 'more general class of welfare functions' to maintain consistency with the formal definition used in Theorem 1.

---

### 10. Undefined Variable Transformation When Baseline is Zero

**Status**: [Pending]

**Quote**:
> nslash]
> 
> We take a generic ˆ b such that ˆ b glyph[lscript] = 0 for all glyph[lscript] . If fo

**Feedback**:
The proof earlier defines the control variable as $x_\ell = y_\ell / \hat{b}_\ell$. If $\hat{b}_\ell = 0$, this division is undefined, invalidating the change of variables used throughout the derivation. A generic vector in this context typically implies $\hat{b}_\ell \neq 0$ to ensure the coordinate transformation is valid. It would be helpful to correct this to $\hat{b}_\ell \neq 0$ to maintain consistency with the definition of $x$.

---

### 11. Tautological Norm Equality Lacks Substitution

**Status**: [Pending]

**Quote**:
> The next equality follows by noticing that ‖ ˆ b ‖ 2 = ‖ ˆ b ‖ 2 .

**Feedback**:
It is not clear how the tautology $\| \hat{b} \|^2 = \| \hat{b} \|^2$ justifies the equality step. Given the earlier mention of a 'binding budget constraint,' this step likely intends to substitute the norm with the budget constant $C$ (i.e., $\| \hat{b} \|^2 = C$). Writing the expression explicitly would clarify the derivation for readers.

---

### 12. Covariance Matrix Notation Collision in Proposition 4

**Status**: [Pending]

**Quote**:
> Note that the random variable B ∗ can be written as U T B ∗ , and so the variance-covariance matrix of the random variable B ∗ is Σ B ∗ = U T Σ B ∗ U , where recall that Σ B ∗ is the variancecovariance matrix of the random variable B ∗ .

**Feedback**:
The equation $\Sigma_{B^*} = U^T \Sigma_{B^*} U$ implies the covariance matrix is invariant under the orthogonal transformation $U$, which is not generally true. The left-hand side should denote the covariance of the transformed variable (in the principal component basis), distinct from the original basis covariance on the right. It would be helpful to distinguish these, for example by writing $\Sigma_{\hat{B}^*} = U^T \Sigma_{B^*} U$, where $\hat{B}^* = U^T B^*$.

---

### 13. Beta Parameter Definition Inconsistent with Standard Beauty Contest Derivation

**Status**: [Pending]

**Quote**:
> By defining β = ˜ β + γ 1+ γ and b = 1 1+ γ ˜ b , we obtain a best-response structure exactly as in condition (2).

**Feedback**:
For a standard beauty contest payoff $U_i = -(a_i - \tilde{b}_i)^2 - \gamma \sum_j g_{ij}(a_j - a_i)^2$ with $\sum_j g_{ij} = 1$, the first-order condition yields $a_i = \tilde{b}_i/(1+\gamma) + \gamma/(1+\gamma) \sum_j g_{ij} a_j$. This gives $\beta = \gamma/(1+\gamma)$, not $\beta = \tilde{\beta} + \gamma/(1+\gamma)$. The $\tilde{\beta}$ term appears to be incorrectly added. The correct transformation should be $\beta = \gamma/(1+\gamma)$ and $b = \tilde{b}/(1+\gamma)$ to match the standard best-response form.

---

### 14. Welfare Function Claim Lacks Derivation from Stated Payoff Structure

**Status**: [Pending]

**Quote**:
> Moreover, the aggregate equilibrium utility is W ( b , g ) = 1 2 ( a ∗ ) T a ∗ . Hence, this game satisfies Property A.

**Feedback**:
The claim that $W = (1/2)(a^*)^T a^*$ requires verification. Summing individual payoffs $U_i = (private return term) - (a_i - \tilde{b}_i)^2 - \gamma \sum_j g_{ij}(a_j - a_i)^2$ across all players does not obviously yield $(1/2)\sum_i (a_i^*)^2$ without additional assumptions. The coordination cost terms $\gamma \sum_j g_{ij}(a_j - a_i)^2$ sum to $\gamma \sum_i \sum_j g_{ij}(a_j - a_i)^2$, which is generally non-zero. For Property A to hold, these coordination terms must cancel or be absorbed, but this derivation is not shown.

---

### 15. Footnote 6 Defines Alpha_1 with Incorrect Squared Denominator

**Status**: [Pending]

**Quote**:
> 6 The last equality follows because α 1 = 1 / (1 -βλ 1 ) 2 , and assumption OA1 implies that λ 1 = 1.

**Feedback**:
The equilibrium action profile satisfies $a^* = (I - \beta G)^{-1}b$. In the principal component basis, $a^*_\ell = \alpha_\ell b_\ell$ where $\alpha_\ell = 1/(1 - \beta\lambda_\ell)$ from the Neumann series expansion of $(I - \beta G)^{-1}$. For $\ell = 1$ with $\lambda_1 = 1$, this gives $\alpha_1 = 1/(1 - \beta)$, not $1/(1 - \beta)^2$. The squared denominator in footnote 6 is incorrect. This error propagates to Lemma OA1 part 3 where $\sum_i a^*_i = \sqrt{n}\alpha_1 b_1$ uses this definition.

---

### 16. Lemma OA1 Part 1 Requires Symmetry for Column Sum Property

**Status**: [Pending]

**Quote**:
> 1. for any a ∈ R n , ∑ i ∑ j g ij a j = ∑ i a i and ∑ i ∑ j g ij a 2 j = ∑ i a 2 i

**Feedback**:
Lemma OA1 part 1 claims $\sum_i \sum_j g_{ij} a_j = \sum_i a_i$ under Assumption OA1 ($\sum_j g_{ij} = 1$ for all $i$). However, $\sum_i \sum_j g_{ij} a_j = \sum_j a_j (\sum_i g_{ij})$, which equals $\sum_j a_j$ only if column sums $\sum_i g_{ij} = 1$. Assumption OA1 only guarantees row sums equal 1. This equality holds if $G$ is symmetric (Assumption 1), since then row sums equal column sums. The lemma should explicitly note it relies on Assumption 1 (symmetry) in addition to Assumption OA1.

---

### 17. SVD Singular Value Ordering Uses Strict Inequality

**Status**: [Pending]

**Quote**:
> t-decoded -->
> 
> where:
> 
> - (1) U is an orthogonal n × n matrix whose columns are eigenvectors of MM T ;
> - (3) S is an n × n matrix with all off-diagonal entries equal to zero and nonnegative diagonal entries S ll = s l , which are called singular values of M . As a convention, we order the singular values so that s /lscript &gt; s /lscript +1 .
> - (2) V

**Feedback**:
Singular values are conventionally ordered non-increasingly ($s_1 \geq s_2 \geq \dots$), but strict inequality ($s_\ell > s_{\ell+1}$) cannot be enforced by convention if the matrix has repeated singular values (e.g., the identity matrix has all singular values equal to 1). The statement should use $\geq$ to accommodate degenerate spectra. Claiming strict inequality as a convention is mathematically incorrect for general matrices.

---

### 18. Taylor Expansion Coefficient Missing Factor in Lemma OA3

**Status**: [Pending]

**Quote**:
> ′ .
> 
> Proof of Proposition OA1. First, we state and prove a lemma.
> 
> Lemma OA3. Under the conditions of Assumption OA2, on any compact set the function C -1 κ ( C 1 / 2 z ) converges uniformly to k ‖ z ‖ 2 , as C ↓ 0, where k &gt; 0 is some constant. We call the limit 

**Feedback**:
The standard second-order Taylor expansion gives $\kappa(y) = (1/2)\sum_i (\partial^2\kappa/\partial y_i^2)(0)y_i^2 + O(\|y\|^3)$. Substituting $y = C^{1/2}z$ yields $C^{-1}\kappa(C^{1/2}z) = (1/2)\sum_i (\partial^2\kappa/\partial y_i^2)(0)z_i^2 + O(C^{1/2})$. The limit as $C \downarrow 0$ should be $(1/2)k\|z\|^2$ where $k$ is the common second derivative value, not $k\|z\|^2$. The lemma should read 'converges uniformly to $(1/2)k\|z\|^2$' or clarify that $k$ already incorporates this factor.

---

### 19. Proposition OA3 Proof References Undefined Set E

**Status**: [Pending]

**Quote**:
> The point b ∗ is contained in the interior of L ; thus b ∗ is in the interior of E . On the other hand, b ∗ must be on the (elliptical) boundary of E because U is strictly increasing in each component (by irreducibility of the network) and continuous.

**Feedback**:
The proof claims $b^*$ is both in the interior of $E$ and on the boundary of $E$, creating a contradiction. However, the set $E$ is referenced via a formula-not-decoded placeholder, making it impossible to verify the argument. For the contradiction to hold, $E$ must be properly defined (likely an indifference set or level set of the objective). Without seeing $E$'s definition, readers cannot verify whether $b^*$ being interior to $L$ implies it's interior to $E$.

---
