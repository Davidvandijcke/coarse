# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/07/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Scope of Linearity and Welfare Assumptions**

The core mathematical results rely on linear best-response functions and a specific welfare structure where utility is proportional to the sum of squared actions (Property A). While extensions are noted in the Online Appendix, the main text presents these spectral targeting results as broadly applicable to network games. It would be helpful to clarify in the introduction whether the principal component intuition remains robust when strategic interactions are non-linear or when welfare functions include cross-terms that break this proportionality.

**Network Information Requirements and Symmetry**

The model assumes the planner possesses perfect information regarding the complete network adjacency matrix and that this matrix is symmetric. Although the Online Appendix addresses non-symmetric matrices using singular value decomposition, the main intuition is derived from the symmetric case. Readers might note that the robustness of the optimal intervention strategy to network estimation errors and the applicability to directed networks remain open questions that warrant further discussion in the main text.

**Sensitivity to Spectral Gaps and Budget Constraints**

Proposition 2 establishes that the budget required for a simple intervention depends inversely on the spectral gap between the top eigenvalues. In empirical settings, estimating these eigenvalues with precision can be difficult, particularly when the gap is small. It would be helpful to provide a more explicit discussion on the practical implications of small spectral gaps for policy design, as the 'simple intervention' heuristic might fail for realistic budget sizes in certain topologies.

**Static Framework Versus Dynamic Adjustment**

The analysis is conducted within a static, simultaneous-move game framework, assuming agents immediately reach equilibrium after the intervention. In many policy contexts, such as education or public health, interventions unfold over time and agents may adjust their behavior gradually. It would be helpful to discuss how the spectral targeting logic might change if the planner considers a dynamic game where the network or actions evolve, as the current static equilibrium characterization might not capture transitional welfare effects.

**Cost Function Assumptions and Status Quo Genericity**

The optimal intervention strategy relies on a quadratic cost function that is rotationally invariant and assumes a generic status quo vector where baseline returns are non-zero across all components. These assumptions simplify the closed-form solution but may not hold in practice where targeting specific nodes is more expensive or where initial incentives are orthogonal to certain network modes. It would be helpful to explore how the optimal variance allocation changes if the cost function penalizes interventions on specific nodes differently or to clarify the strategy in non-generic cases.

**Assumption 2 (Distinct Eigenvalues) vs. Figure 1 Circle Network Illustration**

Assumption 2 requires that all eigenvalues of the adjacency matrix G are distinct to ensure the uniqueness of the principal components (eigenvectors) used in the decomposition (Fact 1). However, Figure 1 illustrates eigenvectors using a circle network with 14 nodes. The text explicitly states, 'The circle network is nongeneric in that eigenvectors are not uniquely determined,' which implies the presence of repeated eigenvalues. While the authors note that an arbitrarily small perturbation would resolve this, the specific network implementation in Figure 1 technically violates the distinct eigenvalue assumption required for the uniqueness of the basis in the main theorems. It would be helpful to clarify in the figure caption that the displayed basis is one of multiple valid bases due to eigenvalue multiplicity, or to use a perturbed network for the illustration to strictly satisfy Assumption 2.

**Status**: [Pending]

---

## Detailed Comments (17)

### 1. Network Multiplier Terminology

**Status**: [Pending]

**Quote**:
> (b) the 'network multiplier' is an eigenvalue of the network corresponding to that principal component

**Feedback**:
Readers might note that the response to a shock is scaled by $(1-\beta\lambda_i)^{-1}$, not $\lambda_i$ itself. It would be helpful to clarify the relationship between the eigenvalue and the scaling factor to prevent ambiguity. Rewrite the phrase to indicate the multiplier is a function of the eigenvalue.

---

### 2. Inconsistent Vector Notation

**Status**: [Pending]

**Quote**:
> She does this by changing the status quo standalone marginal returns ˆ b , to new values, b , subject to a budget constraint on the cost of her intervention.

**Feedback**:
The text uses non-bold notation in this paragraph, while subsequent equations define the cost function using bold notation. It would be helpful to rewrite '$\hat{b}$' as '$\hat{\boldsymbol{b}}$' and '$b$' as '$\boldsymbol{b}$' in the paragraph to match the equation notation.

---

### 3. Variable Definition Contradiction

**Status**: [Pending]

**Quote**:
> For any vector z ∈ R n , let z = U T z .

**Feedback**:
This statement defines the variable z in terms of itself, which is a logical contradiction. It would be helpful to rewrite 'let z = U T z' as 'let $\underline{z} = U^T z$' to correct the definition and align with the notation used later in the section.

---

### 4. Inconsistent Budget Threshold

**Status**: [Pending]

**Quote**:
> on problem:
> 
> Assumption 3. Either w &lt; 0 and C &lt; ‖ ˆ b ‖ , or w &gt; 0.
> 
> $$\

**Feedback**:
The text preceding Assumption 3 states that the first-best is achieved when $C \geq \| \hat{b} \|^2$. Assumption 3 sets the threshold at $C < \| \hat{b} \|$. It would be helpful to rewrite 'C < ‖ ˆ b ‖' as 'C < ‖ ˆ b ‖ 2' to match the budget constraint derived earlier.

---

### 5. Missing Division Operator in Proposition 2

**Status**: [Pending]

**Quote**:
> for any glyph[epsilon1] &gt; 0, if C &gt; 2 ‖ ˆ b ‖ 2 glyph[epsilon1] ( α 2 α 1 -α 2 ) 2 , then W ∗ /W s &lt

**Feedback**:
The text later explains this bound involves the term '$\alpha_2 / (\alpha_1 - \alpha_2)$'. However, the formula in Proposition 2 lacks the division operator. It would be helpful to rewrite '( α 2 α 1 -α 2 ) 2' as '( α 2 / ( α 1 -α 2 ) ) 2' to match the explanation.

---

### 6. Assumption 5 Infinite Cost Condition

**Status**: [Pending]

**Quote**:
> Assumption 5. The cost function satisfies two properties: (a) K ( B ) = ∞ if E b = ¯ b ;

**Feedback**:
The text states the planner faces a vector of means fixed at $\bar{b}$ and restricts interventions to be mean-neutral. However, Assumption 5(a) assigns infinite cost if $E b = \bar{b}$. It would be helpful to rewrite 'K ( B ) = ∞ if E b = ¯ b' as 'K ( B ) = ∞ if E b ≠ ¯ b' to align with the mean-neutral restriction.

---

### 7. Generic Baseline Vector Definition

**Status**: [Pending]

**Quote**:
> We take a generic ˆ b such that ˆ b glyph[lscript] = 0 for all glyph[lscript] .

**Feedback**:
The proof defines the control variable as $x_\ell = y_\ell / \hat{b}_\ell$ earlier in the text. If $\hat{b}_\ell = 0$, this transformation involves division by zero. It would be helpful to rewrite 'ˆ b glyph[lscript] = 0' as 'ˆ b glyph[lscript] != 0' because the transformation requires non-zero baseline components.

---

### 8. Index Typo in Limit Behavior

**Status**: [Pending]

**Quote**:
> where the first equality follows because x ∗ glyph[lscript] → α glyph[lscript] α 1 -α glyph[lscript] for all glyph[lscript] = 1.

**Feedback**:
As $C \to \infty$, $\mu \to w \alpha_1$, which implies $x_1^* \to \infty$. The finite limit expression applies only to components where the denominator does not vanish. It would be helpful to rewrite 'for all glyph[lscript] = 1' as 'for all glyph[lscript] != 1' to correctly reflect that the first component diverges.

---

### 9. Proof Label Inconsistency

**Status**: [Pending]

**Quote**:
> This concludes the proof of Proposition 2.

**Feedback**:
The proof begins by identifying itself as 'Proof of Lemma 1', but concludes with 'This concludes the proof of Proposition 2.' It would be helpful to rewrite 'This concludes the proof of Proposition 2.' as 'This concludes the proof of Lemma 1.' to align with the section header.

---

### 10. Incomplete Sentence in Lemma 1

**Status**: [Pending]

**Quote**:
> noticing that ‖ ˆ b ‖ 2 = ‖ ˆ b ‖ 2 . The final inequality follows because, from the facts that µ &gt; wα 1 and that α 1 &gt; α 2 &gt; · · · &gt; α n , we can deduce that for each glyph[lscript] &gt; 1
> 
> This concludes the 

**Feedback**:
The sentence describing the final inequality justification cuts off after 'for each glyph[lscript] > 1' without stating the deduction. It would be helpful to rewrite the sentence to include the full deduction and the resulting inequality expression to complete the argument.

---

### 11. Covariance Transformation Notation

**Status**: [Pending]

**Quote**:
> Note that the random variable B ∗ can be written as U T B ∗ , and so the variance-covariance matrix of the random variable B ∗ is Σ B ∗ = U T Σ B ∗ U , where recall that Σ B ∗ is the variancecovariance matrix of the random variable B ∗ .

**Feedback**:
Readers might note that this notation conflates the covariance of the vector B* with the covariance of its principal components. It would be helpful to rewrite the sentence to distinguish between the intervention vector in the original basis and its coordinates in the eigenbasis.

---

### 12. Typo in Intervention Variable Definition

**Status**: [Pending]

**Quote**:
> Recalling the definition x /lscript = b /lscript -ˆ b /lscript ˆ b /lscript for every /lscript

**Feedback**:
The expression contains a repeated term 'ˆ b /lscript' which appears to be a typo. In the context of intervention problems, the deviation is typically $x_\ell = b_\ell - \hat{b}_\ell$. It would be helpful to rewrite the definition to correct the expression.

---

### 13. Notation Conflict in Variable Transformation

**Status**: [Pending]

**Quote**:
> Let a = V T a and b = U T b ; then the equilibrium condition implies that:

**Feedback**:
The equation $a = V^T a$ redefines the vector a in terms of itself, implying a is unchanged by the transformation. It would be helpful to rewrite 'Let a = V T a and b = U T b' as 'Let $\tilde{a} = V^T a$ and $\tilde{b} = U^T b$' to distinguish transformed variables.

---

### 14. Incomplete Sentence in Corollary OA2

**Status**: [Pending]

**Quote**:
> Corollary OA2. The optimal intervention in Example OA1 is characterized by and, for all /lscript ≥ 2:

**Feedback**:
The phrase 'characterized by and' lacks the object of the preposition 'by', indicating a missing equation. It would be helpful to rewrite 'characterized by and, for all' as 'characterized by [equation], and, for all' to complete the grammatical structure.

---

### 15. Incomplete Inequality in Corollary OA3

**Status**: [Pending]

**Quote**:
> 3. If C →∞ then | x 1 |→∞ and x /lscript → /lscript ( α 1 -α /lscript ) for all /lscript ≥

**Feedback**:
The inequality condition ends at '≥' without specifying the bound. It would be helpful to rewrite 'for all /lscript ≥' as 'for all /lscript ≥ 2' to complete the mathematical statement.

---

### 16. Incorrect Geometry Description in Linear Cost Proof

**Status**: [Pending]

**Quote**:
>  set
> 
> <!-- formula-not-decoded -->
> 
> The point b ∗ is contained in the interior of L ; thus b ∗ is in the interior of E . On the other hand, b ∗ must be on the (elliptical) boundary of E because U is str

**Feedback**:
Readers might note that the constraint set for linear costs is defined as $K(b; \hat{b}) = \sum |b_i - \hat{b}_i| \le C$, which forms an L1 ball (a polytope), not an ellipse. It would be helpful to rewrite '(elliptical) boundary of E' as 'polyhedral boundary of the constraint set'.

---

### 17. Sign Error in Monetary Incentives Cost Integral

**Status**: [Pending]

**Quote**:
> Integrating across all the individuals whose actions are changed gives ∫ y i 0 xdx , a cost that is quadratic in the magnitude of the change.

**Feedback**:
It would be helpful to correct the limits of integration to ensure the calculated cost is non-negative. The current limits evaluate to a negative value, whereas the magnitude of change requires integration from 0 to $y_i$. Rewrite '$\int y_i 0 xdx$' as '$\int_0^{y_i} xdx$'.

---
