# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/04/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Applicability to Directed Network Structures**

The core theoretical results rely on the adjacency matrix being symmetric to facilitate eigendecomposition, yet many economic networks such as supply chains are inherently directed. While the Online Appendix explores Singular Value Decomposition for non-symmetric cases, the main text's intuition regarding eigenvalues does not directly translate to singular values without qualification. It would be helpful to clarify in the main analysis how the interpretation of principal components shifts when left and right singular vectors differ, as targeting strategies may vary significantly in directed settings.

**Sensitivity to Network Measurement Error**

The proposed methodology decomposes interventions based on exact eigenvectors of the network matrix, but spectral analysis can be sensitive to small perturbations in the adjacency structure. Readers might note that in empirical applications, network links are often estimated with noise, which could destabilize the identified principal components and lead to suboptimal resource allocation. It would be beneficial to include a discussion on the robustness of the targeting strategy to measurement error, potentially providing bounds on how perturbations affect the alignment of the optimal intervention vector.

**Dependence on Linear-Quadratic and Cost Specifications**

The amplification mechanism and the result that optimal interventions simplify for large budgets are derived under specific linear-quadratic utility and quadratic cost constraints. Reviewers note that if marginal returns diminish or if cost functions are linear rather than convex, the eigenvalue ordering and diversification results may no longer hold accurately. It would be helpful to clarify the range of parameters where the linear approximation remains valid and discuss how alternative cost specifications might alter the recommended spectral targeting.

**Generalizability of Principal Component Interpretations**

The paper characterizes top principal components as reflecting global network structure and bottom components as local, primarily illustrated using regular network topologies. However, in heterogeneous networks such as core-periphery models, eigenvectors can exhibit localization phenomena where mass concentrates on specific nodes regardless of eigenvalue rank. It would be helpful to qualify this structural interpretation to prevent overgeneralization, as the mapping between eigenvalue rank and network scope is not uniform across all topologies.

**Information Requirements and Static Topology Assumptions**

The baseline model assumes the planner has perfect knowledge of the network adjacency matrix while only facing uncertainty regarding standalone marginal returns. Additionally, the network is treated as static, ignoring potential endogenous link adjustments in response to interventions. Readers might note that uncertainty about the network structure itself would fundamentally change the principal component basis used for targeting. It would be helpful to acknowledge these limitations and discuss conditions under which the network remains stable or how uncertainty about the topology impacts the decomposition.

**Unverified Budget Magnitude in Large Budget Simulations**

Proposition 2 derives a specific lower bound on the budget C (dependent on the spectral gap and status quo norm) required for the optimal intervention to approximate the simple principal component form. However, the simulation in Figure 2 selects C=500 to represent 'large budgets' without verifying that this value satisfies the theoretical bound for the specific 11-node network and status quo vector employed. This creates a gap between the theoretical sufficient conditions and the empirical parameter selection, leaving the asymptotic claim reliant on visual similarity rather than analytical verification.

**Illustrative Network Violates Distinct Eigenvalue Assumption**

Assumption 2 requires all eigenvalues of the adjacency matrix G to be distinct to ensure unique principal component decomposition. Figure 1 utilizes a circle network which the text explicitly acknowledges is 'nongeneric' with non-unique eigenvectors. While the authors argue a perturbation would resolve this, the visual illustration of principal components relies on a specific basis selection that is not theoretically guaranteed under the stated assumptions for the depicted graph structure, potentially misleading readers about the genericity of the decomposition.

**Status**: [Pending]

---

## Detailed Comments (20)

### 1. Orthogonality and Symmetry Assumption

**Status**: [Pending]

**Quote**:
> How does a planner optimally target interventions that change individuals' private returns to investment? We analyze this question by decomposing any intervention into orthogonal principal components , which are determined by the network and are ordered according to their associated eigenvalues.

**Feedback**:
It would be helpful to explicitly state that the orthogonality of these components presupposes a symmetric adjacency matrix. In linear algebra, eigenvectors of a general matrix are not orthogonal unless the matrix is normal. Readers might note that for directed networks, this decomposition would require singular value decomposition instead of eigendecomposition to maintain orthogonality.

---

### 2. Network Multiplier Definition Precision

**Status**: [Pending]

**Quote**:
> the 'network multiplier' is an eigenvalue of the network corresponding to that principal component

**Feedback**:
In the standard linear-quadratic network game framework, the equilibrium action vector satisfies $a = (I - \beta G)^{-1} b$. If the intervention aligns with an eigenvector with eigenvalue $\lambda_k$, the scaling factor is $(1 - \beta \lambda_k)^{-1}$, not $\lambda_k$ itself. While the eigenvalue determines the multiplier, stating the multiplier is the eigenvalue is mathematically imprecise as the multiplier diverges as $\lambda_k \to 1/\beta$.

---

### 3. Notation Consistency in Optimization Objective

**Status**: [Pending]

**Quote**:
> The incentive-targeting (IT) problem is given by

**Feedback**:
The optimization problem states the objective as max_b w*a^T*a, but the constraint uses a* to denote equilibrium actions: [I - βG]a* = b. This creates notational inconsistency—the objective should reference a* rather than a to match the constraint notation. It would be helpful to ensure the objective reads max_b w*(a*)^T*(a*) to clarify that actions are equilibrium outcomes determined by b.

---

### 4. Symmetry Requirement for Fact 1

**Status**: [Pending]

**Quote**:
> Fact 1. If G satisfies Assumption 1, then G = U Λ U T , where:

**Feedback**:
Fact 1 relies on Assumption 1 (symmetry) to guarantee real eigenvalues and orthogonal eigenvectors. It would be helpful to explicitly list Assumption 1 in the statement of Fact 1 or the preceding text, rather than using a collective reference. This ensures that the dependency between the network structure and the welfare function's tractability is transparent before the mathematical details begin.

---

### 5. Small Budget Limit Status Quo Term

**Status**: [Pending]

**Quote**:
> As C → 0, in the optimal intervention, r ∗ glyph[lscript] r ∗ glyph[lscript] ′ → α glyph[lscript] α glyph[lscript] ′ .

**Feedback**:
The small budget limit claim requires verification. From Theorem 1, the similarity ratio r*_ℓ should be proportional to [wα_ℓ/(μ-wα_ℓ)]·ρ(b̂,u_ℓ). As C→0, μ→∞, so r*_ℓ/r*_ℓ' → [α_ℓ/α_ℓ']·[ρ(b̂,u_ℓ)/ρ(b̂,u_ℓ')]. The proposition states the ratio converges to α_ℓ/α_ℓ' alone, which implicitly assumes ρ(b̂,u_ℓ) = ρ(b̂,u_ℓ') for all ℓ,ℓ'. It would be helpful to clarify if r*_ℓ is defined to cancel these status quo similarity terms.

---

### 6. Proposition 2 Budget Bound Formula Structure

**Status**: [Pending]

**Quote**:
> If the game has the strategic complements property, β &gt; 0, then for any glyph[epsilon1] &gt; 0, if C &gt; 2 ‖ ˆ b ‖ 2 glyph[epsilon1] ( α 2 α 1 -α 2 ) 2 , then W ∗ /W s &lt; 1 + glyph[epsilon1] and ρ ( y ∗ , √ C u 1 ) &gt; √ 1 -glyph[epsilon1] .

**Feedback**:
The budget bound C > 2‖b̂‖²/[ε(α₂/α₁ - α₂)²] has an unusual structure. Simplifying the denominator: (α₂/α₁ - α₂)² = α₂²(1/α₁ - 1)². Standard spectral gap bounds typically depend on (α₁-α₂)² directly. It would be helpful to verify the correct form, as the current expression may underestimate the budget needed when α₁ and α₂ are close.

---

### 7. Spectral Gap Dependency in Budget Bound

**Status**: [Pending]

**Quote**:
> Recall that α glyph[lscript] = (1 -βλ glyph[lscript] ) -2 ; thus if β &gt; 0, the term α 2

**Feedback**:
The text uses α_ℓ in the budget bound formula for Proposition 2. Given the definition α_ℓ = (1-βλ_ℓ)^(-2), the term α_2/α_1 in the bound depends on the squared amplification factors. It would be helpful to verify that the budget bound properly captures how the required budget scales with the spectral gap between the top two eigenvalues using this squared definition.

---

### 8. Simple Intervention Definition Uniqueness

**Status**: [Pending]

**Quote**:
> Definition 2 (Simple interventions) . An intervention is simple if, for all i ∈ N ,

**Feedback**:
Definition 2 defines simple interventions as proportional to u_1 or u_n. However, if eigenvalues are not distinct (violating Assumption 2), u_1 or u_n may not be unique. It would be helpful to qualify this definition to state that simplicity assumes a unique principal component basis, or to specify how simplicity is defined in the presence of eigenspace multiplicities.

---

### 9. Genericity Assumption in Proof of Theorem 1

**Status**: [Pending]

**Quote**:
> Note that, for all glyph[lscript] , α glyph[lscript] are well-defined (by Assumption 1) and strictly positive (by genericity of G ).

**Feedback**:
The proof states α_ℓ are strictly positive by genericity of G. However, α_ℓ = (1-βλ_ℓ)^(-2) is strictly positive for all real λ_ℓ < 1/β, regardless of genericity. Genericity is required for distinct eigenvalues, not positivity. It would be helpful to correct this attribution to avoid confusion about which assumption guarantees positivity versus uniqueness.

---

### 10. Proof Conclusion Mismatch Lemma vs Proposition

**Status**: [Pending]

**Quote**:
> This concludes the proof of Proposition 2.

**Feedback**:
The proof section header and opening line identify it as Proof of Lemma 1, but the conclusion states it proves Proposition 2. This inconsistency creates ambiguity about which result is being established in this section. It would be helpful to align the proof label with the conclusion to ensure readers can correctly map the argument to the corresponding theorem statement.

---

### 11. Tautological Justification in Proof

**Status**: [Pending]

**Quote**:
> The next equality follows by noticing that ‖ ˆ b ‖ 2 = ‖ ˆ b ‖ 2 .

**Feedback**:
The justification provided for the equality is a tautology (a quantity equals itself), which does not explain the algebraic step taken. It is not clear how this observation leads to the equality without further specification of the terms involved. It would be helpful to clarify the specific terms that are being equated or canceled in this step.

---

### 12. Basis Transformation Notation in OA1

**Status**: [Pending]

**Quote**:
> Note that the random variable B ∗ can be written as U T B ∗ , and so the variance-covariance matrix of the random variable B ∗ is Σ B ∗ = U T Σ B ∗ U , where recall that Σ B ∗ is the variancecovariance matrix of the random variable B ∗ .

**Feedback**:
It appears there is a notation inconsistency in the basis transformation definition. The equation $B^* = U^T B^*$ implies $(I - U^T)B^* = 0$, which generally requires $B^*=0$ since $U^T \neq I$. Readers might note that the intended relation is likely for the coordinates in the eigenbasis, $\hat{B}^* = U^T B^*$. It would be helpful to distinguish the bases to avoid implying rotational invariance of the covariance matrix itself.

---

### 13. Missing Covariance Transformation Step in OA1

**Status**: [Pending]

**Quote**:
> Furthermore, the matrix and so Var( b ∗∗ k ) = Var( b ∗ k ) for all k /negationslash∈ { /lscript, /lscript ′ } and Var( b ∗∗ /lscript ) = Var( b ∗ /lscript ′ ) &gt; Var( b ∗∗ /lscript ′ ) = Var( b ∗ /lscript ).

**Feedback**:
The phrase 'Furthermore, the matrix and so' omits the specific matrix property used to derive the variance equalities. To verify that $\text{Var}(b^{**}_k) = \text{Var}(b^*_k)$, one should show that the covariance matrix transforms as $Σ_{\hat{B}^{**}} = P Σ_{\hat{B}^*} P^T$ under the permutation $P$. It would be helpful to explicitly state this intermediate step to justify why variances are swapped for indices $ℓ, ℓ'$ and unchanged for others.

---

### 14. Undefined Scaling Factor in Proposition 3 Proof

**Status**: [Pending]

**Quote**:
> Thus, defining $x_\ell = y_\ell / \bar{b}_\ell$, with $\bar{b}_\ell = \mathbb{E}[\hat{B}_\ell]$, it satisfies the same conditions at the optimum as those derived in Theorem 1.

**Feedback**:
The definition $x_\ell = y_\ell / \bar{b}_\ell$ requires $\bar{b}_\ell \neq 0$ for all $\ell$. However, Proposition 4 later states 'without loss of generality we can normalize ¯ b = 0'. If the expectation of standalone returns can be zero, the definition in Proposition 3 becomes undefined. It would be helpful to specify that Proposition 3 assumes $\mathbb{E}[\hat{B}_\ell] \neq 0$ or to define the scaling factor using norms to avoid singularity.

---

### 15. Proposition 4 Normalization Contradiction

**Status**: [Pending]

**Quote**:
> without loss of generality we can normalize ¯ b = 0

**Feedback**:
This normalization in Proposition 4 conflicts with the scaling factor definition in Proposition 3 which divides by $\bar{b}_\ell$. Readers might note that if $\bar{b}$ is normalized to zero, the scaling factor $x_\ell$ becomes undefined. It would be helpful to reconcile these two propositions to ensure the scaling argument holds across both sections.

---

### 16. Bonacich Centrality Convergence Normalization

**Status**: [Pending]

**Quote**:
> rality converges to eigenvector centrality as the spectral radius of β G tends to 1; otherwise the two vectors can be quite different (see, for example, Calv´ o-Armengol et al. (2015) or Golub and Lever (2010)).

**Feedback**:
The Bonacich centrality vector is defined as c(β) = (I - βG)^(-1)1. As βλ_1 → 1, the term 1/(1 - βλ_1) diverges to infinity, meaning the Bonacich centrality vector itself blows up rather than converging to a finite limit. What actually converges is the normalized direction c(β)/||c(β)|| to the first eigenvector u_1. It would be helpful to clarify that it is the normalized Bonacich centrality that converges.

---

### 17. Smallest Eigenvalue Terminology Clarification

**Status**: [Pending]

**Quote**:
> t principal component: We have shown that in games with strategic substitutes, for large budgets interventions that aim to maximize the aggregate utility target individuals in proportion to the eigenvector of G associated to the smallest eigenvalue of G , the l

**Feedback**:
For adjacency matrices of undirected graphs, eigenvalues can range from negative to positive values. The term 'smallest eigenvalue' could mean either the minimum algebraic value (most negative) or the smallest in absolute value. For strategic substitutes, the results typically depend on the most negative eigenvalue. It would be helpful to clarify that 'smallest' means minimum algebraic value to prevent confusion with PCA conventions where eigenvalues are ordered by magnitude.

---

### 18. Unverified Budget Magnitude in Large Budget Simulations

**Status**: [Pending]

**Quote**:
> Figure 2 selects C=500 to represent 'large budgets'

**Feedback**:
Proposition 2 derives a specific lower bound on the budget C (dependent on the spectral gap and status quo norm) required for the optimal intervention to approximate the simple principal component form. However, the simulation in Figure 2 selects C=500 to represent 'large budgets' without verifying that this value satisfies the theoretical bound for the specific 11-node network and status quo vector employed. This creates a gap between the theoretical sufficient conditions and the empirical parameter selection.

---

### 19. Illustrative Network Violates Distinct Eigenvalue Assumption

**Status**: [Pending]

**Quote**:
> Figure 1 utilizes a circle network which the text explicitly acknowledges is 'nongeneric' with non-unique eigenvectors.

**Feedback**:
Assumption 2 requires all eigenvalues of the adjacency matrix G to be distinct to ensure unique principal component decomposition. Figure 1 utilizes a circle network which the text explicitly acknowledges is 'nongeneric' with non-unique eigenvectors. While the authors argue a perturbation would resolve this, the visual illustration of principal components relies on a specific basis selection that is not theoretically guaranteed under the stated assumptions for the depicted graph structure.

---

### 20. Generalizability of Principal Component Interpretations

**Status**: [Pending]

**Quote**:
> The paper characterizes top principal components as reflecting global network structure and bottom components as local

**Feedback**:
The paper characterizes top principal components as reflecting global network structure and bottom components as local, primarily illustrated using regular network topologies. However, in heterogeneous networks such as core-periphery models, eigenvectors can exhibit localization phenomena where mass concentrates on specific nodes regardless of eigenvalue rank. It would be helpful to qualify this structural interpretation to prevent overgeneralization, as the mapping between eigenvalue rank and network scope is not uniform across all topologies.

---
