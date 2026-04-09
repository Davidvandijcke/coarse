# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/05/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Symmetry Assumption and Directed Networks**

Assumption 1 restricts the adjacency matrix to be symmetric, which guarantees real eigenvalues and orthogonal eigenvectors used in the principal component decomposition. While the Online Appendix addresses non-symmetric matrices via singular value decomposition, the main text presents the eigenvector centrality intuition as the core contribution. It would be helpful to clarify in the introduction whether the main intuition regarding strategic complements holds for directed networks or if the symmetry assumption is a necessary condition for the proposed targeting rule. Readers might note that many empirical networks, such as trade or information flows, are naturally directed, which limits the direct application of the main results without consulting the appendix.

**Dependence on Property A for Welfare Characterization**

Theorem 1 and Corollary 1 explicitly require the network game to satisfy Property A, where aggregate utility is proportional to the sum of squared equilibrium actions. Although the Online Appendix extends the analysis to general externalities, the clean ranking of principal components in the main text relies on this specific utility structure. It would be helpful to clarify how the optimal targeting rule changes when the welfare function includes linear terms or different externalities that violate Property A. Readers might note that the main policy recommendation is conditional on this technical property holding, and the ranking of components could depend on additional parameters in more general settings.

**Sensitivity to Cost Function Specification**

The main analysis assumes quadratic intervention costs, which leads to distributed targeting across the network to equalize marginal costs. However, the Online Appendix shows that linear costs lead to targeting a single individual with the highest welfare centrality, contradicting the distributed intervention result in the main text. It would be helpful to discuss the robustness of the principal component ranking under different cost convexities, as the curvature drives the interior solution. This sensitivity suggests the distributed intervention result is driven by the cost specification rather than network structure alone, and clarifying this would strengthen the policy implications regarding administrative costs of targeting.

**Spectral Gap Requirements for Simple Interventions**

Proposition 2 establishes that interventions converge to a single principal component only when the spectral gap is sufficiently large relative to the budget and status quo incentives. In networks with strong community structures, the gap between the top two eigenvalues can be small, implying that complex interventions involving multiple components are often optimal. It would be helpful to provide empirical examples of network structures where this gap condition fails to illustrate the practical limits of the simple intervention heuristic. Without this context, readers might assume targeting eigenvector centrality is always sufficient for large budgets, whereas the condition highlights that network topology dictates the complexity of the optimal policy.

**Cost Invariance in Incomplete Information Settings**

Section 5 analyzes optimal interventions under incomplete information but relies on Assumption 5, which requires the cost of intervention to be invariant under orthogonal transformations of the variance-covariance matrix. This assumption implies that the cost of inducing variance depends only on the total variance, not on which specific agents are affected. It would be helpful to discuss scenarios where targeting specific agents for variance reduction might be more costly than others. This limitation restricts the applicability of Proposition 4 to settings where cost structures are directionally neutral, and relaxing this assumption might alter the optimal variance targeting strategy.

**Consistency of Status Quo Dependence in Large Budget Limits**

There is a potential tension between Theorem 1 and the discussion in Section 4.1 regarding the role of the status quo vector. Theorem 1 establishes that the similarity between the optimal intervention and a principal component is proportional to the similarity between the status quo vector and that component, yet Section 4.1 states that for large budgets, the optimal intervention becomes proportional to the first principal component. It would be helpful to reconcile these statements by explicitly stating the condition on the status quo vector required for the large-budget limit to align with a single principal component. Clarifying this would ensure the convergence claim does not contradict the orthogonality implications of the main theorem.

**Illustrative Network Structure and Eigenvalue Distinctness**

Assumption 2 requires that all eigenvalues of the adjacency matrix G are distinct to ensure a unique principal component decomposition. In Figure 1, the authors illustrate eigenvectors using a 'circle network with 14 nodes.' Readers might note that regular circle networks typically possess symmetries that result in repeated eigenvalues, which technically violates Assumption 2. Footnote 11 acknowledges this, stating the network is 'nongeneric in that eigenvectors are not uniquely determined.' While the authors suggest that an arbitrarily small perturbation would resolve this, it would be helpful to explicitly clarify in the figure caption or text whether the numerical results presented rely on a perturbed version of the circle network that satisfies the distinct eigenvalue condition, as the strict decomposition in Theorem 1 requires this property.

**Status**: [Pending]

---

## Detailed Comments (22)

### 1. Best Response Equation Mismatch

**Status**: [Pending]

**Quote**:
> for individual i 's action to be a best response is:
> 
> 
> ho(oldsymbol{y}^*, oldsymbol{u}^	ext{ell}(oldsymbol{G})) 
> quad 
> propto 
> quad 
> ho(oldsymbol{	ext{hat}}oldsymbol{b}, oldsymbol{u}^	ext{ell}(oldsymbol{G})) 
> rac{w	ext{alpha}_	ext{ell}}{	ext{mu} - w	ext{alpha}_	ext{ell}}, 
> quad 	ext{ell} = 1, 2, 
> dots, n,

**Feedback**:
It would be helpful to verify the equation labeled as the best response condition. Deriving the first-order condition from the utility function yields a linear relationship between actions and standalone returns, whereas the displayed formula involves correlations with eigenvectors and intervention parameters. This formula corresponds to the optimal targeting result in Theorem 1 rather than the equilibrium condition. Relocating this formula to the intervention analysis section would improve clarity.

---

### 2. Principal Component Definition Minimizes Distance to Columns Inaccurately

**Status**: [Pending]

**Quote**:
> The first principal component of G is defined as the n -dimensional vector that minimizes the sum of squares of the distances to the columns of G .

**Feedback**:
It would be helpful to clarify the objective function for the principal component definition. Readers might note that minimizing the sum of squared distances from a vector to a set of points yields the centroid (mean) of those points, rather than the direction of maximum variance. Standard PCA minimizes the sum of squared orthogonal distances from the data points to the line spanned by the principal component vector. Rewriting the definition to specify that the vector minimizes the distance to the subspace spanned by it would align the mathematical characterization with the standard spectral interpretation.

---

### 3. Inconsistent Definition of Alpha Parameter

**Status**: [Pending]

**Quote**:
> Recall that αₙ = (1 -βλₙ ) -2 ; thus if β > 0, the term α₂ / ( α₁ -α₂ ) of the inequality is large when λ₁ -λ₂ , the 'spectral gap' of the graph, is small.

**Feedback**:
It would be helpful to clarify the definition of αₙ. Earlier in the text, αₙ is defined as (1 - βλₙ)^-1 in the context of Theorem 1, while Footnote 6 in the Online Appendix defines it as 1 / (1 -βλ₁ ) 2. Since the welfare function depends on the square of the action multiplier, consistency in this definition is crucial for the derived bounds and similarity ratios. Verifying the exponent across sections would ensure the mathematical derivations remain consistent.

---

### 4. Proposition 2 Bound Formula Discrepancy

**Status**: [Pending]

**Quote**:
> ε > 0, if C > 2 ‖ ̂ b ‖ 2 ε ( α₂ α₁ -α₂ ) 2 , then W * /W s < 1 + ε and ρ ( y * , √ C u₁ ) > √ 1 -ε .

**Feedback**:
Readers might note that the term ( α₂ α₁ -α₂ ) 2 in the budget condition appears inconsistent with the subsequent discussion which refers to the ratio α₂ / ( α₁ -α₂ ). It would be helpful to verify if the bound should involve ( α₁ -α₂ ) 2 to align with the spectral gap logic described in the paragraph following the proposition. Ensuring the formula matches the spectral gap intuition would strengthen the result.

---

### 5. Assumption 5(a) Constraint Logic Error

**Status**: [Pending]

**Quote**:
> Assumption 5. The cost function satisfies two properties: (a) K ( B ) = ∞ if E b = ̅ b ; (b) K ( B ) = K ( ̃ B ) if ̃ b -̅ b = O ( b -̅ b ), where O is an orthogonal matrix.

**Feedback**:
Property (a) states the cost is infinite if the mean equals the fixed vector ̅ b. However, Section 5.2 specifies the planner faces means 'fixed at ̅ b' and intervenes on variances. If the cost is infinite for the required mean, the intervention problem becomes infeasible. It would be helpful to revise the condition to read K ( B ) = ∞ if E b ≠ ̅ b to enforce the mean constraint while allowing finite costs for feasible interventions.

---

### 6. Assumption 4 Missing Cost Formula

**Status**: [Pending]

**Quote**:
> Assumption 4. The cost of implementing r.v. B y is and K ( B ) is ∞ for any other random variable.

**Feedback**:
The definition of the cost function is incomplete, reading 'is and' without the mathematical expression. Proposition 3 relies on this cost structure to equate the stochastic problem to the deterministic one. It would be helpful to include the quadratic cost formula (e.g., K ( B y ) = γ || y ||^2 ) to allow readers to verify the derivation and ensure the assumption is well-defined.

---

### 7. Proposition 4 Item Numbering Inversion

**Status**: [Pending]

**Quote**:
> 2. Suppose the planner dislikes variance (i.e., w < 0). If the game has strategic complements ( β > 0), then Var( uₙ ( G ) · b * ) is weakly increasing in ℓ ; if the game has strategic substitutes ( β < 0), then Var( uₙ ( G ) · b * ) is weakly decreasing in ℓ . 1. Suppose the planner likes variance (i.e., w > 0)...

**Feedback**:
The items in Proposition 4 are listed as '2.' followed by '1.'. This inversion of numbering may confuse readers regarding the logical structure of the proposition. It would be helpful to reorder these to '1.' and '2.' for clarity and consistency with standard proposition formatting.

---

### 8. Contradiction in Generic b Assumption

**Status**: [Pending]

**Quote**:
> We take a generic ̂ b such that ̂ bℓ = 0 for all ℓ .

**Feedback**:
Readers might note that the transformation xℓ = yℓ / ̂ bℓ requires ̂ bℓ ≠ 0 to be well-defined. If ̂ bℓ = 0, the variable xℓ is undefined. Additionally, the subsequent argument relies on the term 2 ̂ bℓ^2 w αℓ being non-zero to derive a contradiction. It would be helpful to revise the text to state 'such that ̂ bℓ ≠ 0 for all ℓ' to ensure mathematical consistency.

---

### 9. Inconsistent Notation in Cost Constraint

**Status**: [Pending]

**Quote**:
> The fact b₁² ̃ x₁² = C , used above, follows because the simple policy allocates the entire budget to changing b₁ .

**Feedback**:
The cost constraint is defined on the intervention vector y, where yℓ = ̂ bℓ xℓ. Consequently, the budget constraint in the transformed basis should read ̂ b₁² ̃ x₁² = C. Using b₁² instead of ̂ b₁² creates a notation inconsistency with the earlier definition of the cost function. It would be helpful to correct the subscript to match the status quo vector ̂ b used in the transformation.

---

### 10. Division by Zero in Limit Expression

**Status**: [Pending]

**Quote**:
> This implies that x *ℓ → αℓ α₁ -αℓ for all ℓ = 1.

**Feedback**:
As μ → wα₁, the denominator α₁ - αℓ vanishes when ℓ = 1, rendering the expression undefined. The limit holds for components where ℓ ≠ 1, as the denominator remains non-zero. It would be helpful to specify 'for all ℓ ≠ 1' to avoid division by zero and accurately reflect the convergence behavior of the optimal intervention.

---

### 11. Inconsistent Proof Labeling (Lemma vs Proposition)

**Status**: [Pending]

**Quote**:
> This concludes the proof of Proposition 2.

**Feedback**:
The section header states 'Lemma 1. Assume' and the proof begins with 'Proof of Lemma 1'. However, the text concludes with 'This concludes the proof of Proposition 2.' It would be helpful to align the proof label with the section title and the concluding statement to ensure clarity on which result is being established.

---

### 12. Tautological Justification for Equality Step

**Status**: [Pending]

**Quote**:
> The next equality follows by noticing that ‖ ̂ b ‖² = ‖ ̂ b ‖² .

**Feedback**:
It is not clear how the equality follows from the statement that a quantity equals itself. This appears to be a tautology that does not provide mathematical justification for the step. Readers might note that the intended expression likely involves a relationship between the intervention vector and the budget constraint, but the current text does not support the derivation. Clarifying the intended algebraic step would improve the proof's rigor.

---

### 13. Incomplete Section Title and Missing Content

**Status**: [Pending]

**Quote**:
> ## ADDITIONAL PROOFS, DISCUSSION AND EXTENSIONS FOR

**Feedback**:
The section title ends abruptly with the preposition 'FOR', leaving the object of the phrase unspecified. This ambiguity makes it unclear whether the extensions apply to the main text, the online appendix, or a specific theorem. It would be helpful to provide the complete title to ensure the additional proofs and extensions can be properly reviewed. Without this information, readers cannot assess the validity of the additional proofs or the consistency of the extensions with the main results.

---

### 14. Inconsistent Covariance Matrix Transformation Notation

**Status**: [Pending]

**Quote**:
> Note that the random variable B * can be written as U T B * , and so the variance-covariance matrix of the random variable B * is Σ B * = U T Σ B * U , where recall that Σ B * is the variancecovariance matrix of the random variable B * .

**Feedback**:
It would be helpful to clarify the notation regarding the transformation of the variance-covariance matrix. Standard linear algebra dictates that if the principal components are defined as the transformed variable ̃ B * = U T B *, then their covariance is Cov(̃ B *) = U T Cov(B *) U. The text states Cov(B *) = U T Cov(B *) U, which implies the covariance of the original vector equals the covariance of the transformed vector. The correct expression should define the covariance of the principal components, not B * itself.

---

### 15. Missing Equation in Proposition 3 Proof

**Status**: [Pending]

**Quote**:
> Proof of Proposition 3. Using expression (8), we can write the dependence of E [ W ( b ; G )] on intervention B y as follows:

**Feedback**:
It would be helpful to include the expression referenced after 'as follows:'. The proof claims to use expression (8) to write the dependence of expected welfare, but the equation is omitted. Without this expression, readers cannot verify that maximizing expected welfare is identical to the deterministic setting in Theorem 1, as the intermediate step is missing. Adding the equation would complete the logical flow of the proof.

---

### 16. Incomplete Sentence in Proposition 4 Proof

**Status**: [Pending]

**Quote**:
> Furthermore, the matrix and so Var( b ** k ) = Var( b * k ) for all k ∉ { ℓ, ℓ ' }

**Feedback**:
It would be helpful to complete the sentence beginning with 'Furthermore, the matrix'. The text currently reads 'Furthermore, the matrix and so', which skips the explanation of how the orthogonal matrix O affects the variances of the principal components. Completing this step would clarify why the variances are swapped between indices ℓ and ℓ '. This would ensure the proof is self-contained and verifiable.

---

### 17. Marginal Utility Condition Contradicts Strategic Complement Assumption

**Status**: [Pending]

**Quote**:
> visions' actions. 3 This is a game of strategic complements; moreover, an increase in j 's action has a positive effect on individual i 's utility if and only if a j < a i .

**Feedback**:
The marginal utility with respect to a j is ∂ U i / ∂ a j = β̃ a i + γ (a i - a j), which is positive if a j < (1 + β̃/γ) a i. Since β̃ > 0, this threshold exceeds a i, contradicting the claim that the effect is positive if and only if a j < a i. It would be helpful to clarify the condition under which the marginal effect depends solely on the relative action levels. This distinction is important for understanding the coordination incentives in the game.

---

### 18. Index Notation Ambiguity in Theorem OA1 Part 2a

**Status**: [Pending]

**Quote**:
> 2. a. For all ℓ = 1, x *ℓ > 0 if and only if w₁ > 0;

**Feedback**:
It is not clear how the condition for ℓ = 1 follows here, given that Part 2b explicitly provides a separate condition for x *₁. Context suggests this statement is intended to apply to all components other than the first principal component. It would be helpful to correct the index notation to read 'For all ℓ ≥ 2' to avoid confusion with the specific case for the first component detailed in Part 2b.

---

### 19. Recursive Notation in SVD Definition

**Status**: [Pending]

**Quote**:
> Let a = V T a and b = U T b ; then the equilibrium condition implies that:

**Feedback**:
The notation is recursive and mathematically inconsistent. The vector a is defined as the vector of actions, while V T a is its projection onto the basis V. They cannot be equal unless V=I. The correct notation should introduce new variables, e.g., ̃ a = V T a and ̃ b = U T b, to distinguish the transformed coordinates from the original vectors. This would prevent confusion regarding the coordinate transformation.

---

### 20. Truncated Limit Statement in Corollary OA3

**Status**: [Pending]

**Quote**:
> 3. If C →∞ then | x₁ |→∞ and xℓ → ℓ ( α₁ -αℓ ) for all ℓ ≥

**Feedback**:
The sentence is incomplete and ends abruptly with '≥'. It should specify the index range (e.g., ∀ ℓ > 1 or ℓ > 2). Additionally, the limit expression depends on the specific parameters of Example OA1, but the truncation prevents verification of the full claim. Completing the sentence would allow readers to assess the validity of the limit behavior.

---

### 21. Proposition OA3 Intervention Statement Error

**Status**: [Pending]

**Quote**:
> Proposition OA3. The solution to problem IT-Linear Cost has the property that there exists i * such that b * i = ̂ b i * and b * i = ̂ b i for al i = i * .

**Feedback**:
The proposition states that the optimal intervention satisfies b*_{i*} = ̂b_{i*}, which implies no change in the intervention vector (y=0). However, the subsequent text explicitly states that the planner uses the full budget C, setting b = ̂b + C 1_{i*}. The proposition statement should reflect the budget usage, likely b*_{i*} = ̂b_{i*} + C, to be consistent with the optimization problem and the later explanation.

---

### 22. Integral Limits in Cost Derivation

**Status**: [Pending]

**Quote**:
> Integrating across all the individuals whose actions are changed gives ∫ y i 0 xdx , a cost that is quadratic in the magnitude of the change.

**Feedback**:
The integral limits are written as ∫_{y_i}^0 x dx, which evaluates to -1/2 y_i^2. Since cost must be non-negative, the limits should be reversed to ∫_0^{y_i} x dx (assuming y_i > 0), yielding 1/2 y_i^2. This sign discrepancy in the integration bounds contradicts the claim that the cost is quadratic in the magnitude of the change. Correcting the limits would ensure the cost derivation is mathematically sound.

---
