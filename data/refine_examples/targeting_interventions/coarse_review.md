# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/03/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Restriction to Symmetric Interaction Matrices**

The core theoretical framework relies on orthogonal spectral decomposition, which necessitates that the network interaction matrix be symmetric. This assumption excludes a vast class of economic networks that are inherently directed, such as supply chains, financial exposures, or information cascades where influence is not reciprocal. By relegating the analysis of non-symmetric matrices to an appendix, the paper limits the immediate applicability of its main results to undirected networks, which are less common in policy-relevant settings. The authors should integrate the non-symmetric analysis into the main text or explicitly discuss the economic environments where symmetry is a plausible approximation.

**Sensitivity to Network Measurement Error**

The proposed optimal targeting strategy depends critically on the eigenvectors of the network matrix, particularly for strategic substitutes where lower-order components are weighted. Spectral properties of adjacency matrices are known to be highly sensitive to perturbations; small errors in estimating network links can lead to large deviations in the computed eigenvectors. The paper does not address the robustness of the optimal intervention to measurement error or estimation uncertainty in the network structure. Without a robustness analysis or regularization method, the practical implementation of these targeting rules in empirical settings where networks are estimated rather than observed is severely threatened.

**Dependence on Linear-Quadratic Structure**

The tractability of the principal component decomposition and the resulting closed-form solutions hinge on a Linear-Quadratic-Gaussian (LQG) framework, as evidenced by the variance and mean analysis in the appendix. Real-world interventions often face non-linear cost structures, diminishing returns, or threshold effects that are not captured by quadratic costs. The claim that optimal interventions become 'simple' (involving a single principal component) for large budgets may be an artifact of the quadratic assumption rather than a general economic principle. The authors should test the robustness of their main qualitative results under alternative, non-linear specifications of costs or payoffs.

**Reliance on Technical Regularity Conditions**

The conclusion explicitly acknowledges that the basic analysis relies on 'Property A,' a technical condition that is only relaxed in the Online Appendix. This indicates that the intuitive main results regarding the mapping between strategic complements/substitutes and principal components are not universal but conditional on specific spectral or topological properties of the network. Relying on such conditions without emphasizing their necessity in the main text risks overstating the generality of the findings. The authors should clarify the economic interpretation of Property A and discuss which network topologies might violate it.

**Robustness of the Simple Intervention Claim**

The abstract claims that for large budgets, optimal interventions are 'simple' and involve a single principal component. This result is derived under specific budget constraint formulations and cost functions. However, in many policy contexts, budget constraints are not the only binding restriction; political feasibility, equity constraints, or implementation lags may prevent the concentration of resources on a single spectral component. The paper does not sufficiently explore how the 'simplicity' result degrades when additional realistic constraints are introduced, potentially limiting the prescriptive value of this finding for actual planners.

**Generic Initial Benefits Assumption May Fail in Structured Networks**

The proof of Theorem 1 assumes a 'generic b̂ such that b̂_ℓ ≠ 0 for all ℓ' to ensure the denominator in the optimal solution is nonzero. However, in structured networks like the circle network shown in Figure 1, symmetries can cause certain eigenvector projections to be exactly zero. This measure-zero assumption may not hold in empirical applications with symmetric or regular network structures, potentially invalidating the closed-form solution.

**Symmetric Interaction Matrix Restriction Limits Empirical Applicability**

The concluding remarks acknowledge the paper focuses on symmetric interaction matrices, with asymmetric extensions relegated to the Online Appendix. Many empirical network applications involve directed relationships (e.g., social media followers, supply chains, information flow) where G is inherently asymmetric. The main theoretical results cannot be directly applied to these common empirical settings without the extensions that are not provided in the main text.

**Budget Constraint Conditions May Not Hold in Practice**

Assumption 3 requires either w > 0, or w < 0 with Σb̂_ℓ² > C to ensure the budget constraint binds. Additionally, Proposition 2's approximation results require C > 2∥b̂∥²/ϵ² × α₂/(α₁-α₂). These rate conditions on the budget relative to initial benefits and eigenvalue gaps may not be satisfied in empirical settings with fixed or small budgets, potentially undermining the approximation guarantees claimed in the propositions.

**Status**: [Pending]

---

## Detailed Comments (18)

### 12. Generic Initial Benefits Assumption Typo [CRITICAL]

**Status**: [Pending]

**Quote**:
> We take a generic _**b**_ [ˆ] such that [ˆ] b ~~_ℓ_~~ = 0 for all ℓ .

**Feedback**:
This statement claims the generic initial benefit vector has zero entries for all components, contradicting the derivation requiring division by b̂_ℓ. This appears to be a typo for '≠ 0'. Rewrite as 'b̂_ℓ ≠ 0 for all ℓ' to ensure the change of variables is well-defined and the math is correct.

---

### 13. Optimization Problem Restatement Error [CRITICAL]

**Status**: [Pending]

**Quote**:
> max w _**x**_ 2 ℓ s.t. _αℓ_ (1 + _xℓ_ ) [2][ˆ] b ℓ 2 ~~_ℓ_~~ _[x]_ [2] ℓ _[≤]_ _[C]_ ˆ b ℓ

**Feedback**:
The restatement of the optimization problem in terms of x is syntactically broken and appears to swap or corrupt the objective and constraint. This makes the derivation of the First-Order Conditions impossible to verify. Rewrite the maximization problem clearly using standard notation.

---

### 14. Proposition 1 Proof Text Corruption [CRITICAL]

**Status**: [Pending]

**Quote**:
> withThis implies x _[∗]_ ℓ [=] _µ−wα_ that _wαℓ_ ℓ [.] x [From] _[∗]_ ℓ _[→]_ α [expression] 1 _α−ℓαℓ_ [for] [all][6] _[ℓ]_ [of][= 1.][Theorem][As] [a] [result,][1,] [it] [follows][if] _[C]_ _[→∞]_ [that][then][if] _[C]_ _[ρ][→∞]_ [(] _**[y]**_ _[∗][,]_ _**[ u]**_ [then] _[ℓ]_ [(] _**[G]**_ [))] _[µ][ →][ →]_ [0] _[wα]_ [for][1][.]

**Feedback**:
This paragraph in the Proof of Proposition 1 is unintelligible due to severe text corruption, mixing variable definitions and limit arguments. This prevents verification of the key asymptotic result regarding large budgets. Rewrite this section to clearly state the limit behavior and logical steps.

---

### 1. Symmetric Interaction Matrix Assumption

**Status**: [Pending]

**Quote**:
> Assumption 1. The adjacency matrix G is symmetric.

**Feedback**:
The core theoretical framework relies on orthogonal spectral decomposition, necessitating a symmetric network interaction matrix. This excludes inherently directed networks like supply chains or information cascades. The authors should integrate non-symmetric analysis into the main text or explicitly discuss economic environments where symmetry is a plausible approximation.

---

### 2. Symmetry Restriction in Conclusion

**Status**: [Pending]

**Quote**:
> To develop these ideas in the simplest way, we have focused on a model in which the matrix of interaction is symmetric...

**Feedback**:
The concluding remarks acknowledge the focus on symmetric matrices, with asymmetric extensions relegated to the Online Appendix. Many empirical applications involve directed relationships where G is inherently asymmetric. Add a paragraph in the Conclusion explicitly warning empirical users that the main results cannot be directly applied to directed settings without the extensions.

---

### 3. Sensitivity to Network Measurement Error

**Status**: [Pending]

**Quote**:
> Assumption 2. The spectral radius of β G is less than 1, and all eigenvalues of G are distinct...

**Feedback**:
The proposed optimal targeting strategy depends critically on the eigenvectors of the network matrix. Spectral properties are known to be highly sensitive to perturbations; small errors in estimating links can lead to large deviations. Include a simulation with perturbed G to demonstrate the robustness of the optimal intervention to measurement error.

---

### 4. Dependence on Linear-Quadratic Payoff

**Status**: [Pending]

**Quote**:
> Ui ( a , G ) = ai bi + β gijaj j − ~~~~ - ~~~~ returns from own action 1 − 2 [a] i^{2}

**Feedback**:
The tractability of the principal component decomposition hinges on a Linear-Quadratic-Gaussian framework. Real-world interventions often face non-linear cost structures or diminishing returns not captured by quadratic costs. Discuss the potential impact of non-linear utility specifications on the principal component targeting result.

---

### 5. General Cost Functions Extension

**Status**: [Pending]

**Quote**:
> For discussions and extensions on more general cost functions, see the Online Appendix Section OA3.3.

**Feedback**:
The claim that optimal interventions become 'simple' for large budgets may be an artifact of the quadratic cost assumption. Relying on extensions in the Online Appendix for general cost functions limits the immediate applicability of the main results. Move the discussion of non-linear cost robustness to the main text.

---

### 6. Property A Definition

**Status**: [Pending]

**Quote**:
> Property A. The aggregate equilibrium utility is proportional to the sum of the squares of the equilibrium actions...

**Feedback**:
The conclusion acknowledges that the basic analysis relies on 'Property A,' a technical condition relaxed in the Online Appendix. This indicates that intuitive main results regarding strategic complements/substitutes are conditional on specific spectral properties. Clarify the economic interpretation of Property A in the main text.

---

### 7. Property A Relaxation Reference

**Status**: [Pending]

**Quote**:
> Online Appendix Section OA3.1 extends the analysis to cover important cases where this property does not hold.

**Feedback**:
Relying on technical conditions without emphasizing their necessity in the main text risks overstating the generality of the findings. Move the discussion of which network topologies might violate Property A from the Online Appendix to the main text.

---

### 8. Simple Intervention Claim in Abstract

**Status**: [Pending]

**Quote**:
> For large budgets, optimal interventions are simple - they involve a single principal component.

**Feedback**:
The abstract claims optimal interventions are 'simple' for large budgets. However, in many policy contexts, budget constraints are not the only binding restriction; political feasibility or equity constraints may prevent concentration on a single spectral component. Qualify the abstract claim to reflect these potential limitations.

---

### 9. Simple Intervention Proposition 1

**Status**: [Pending]

**Quote**:
> Proposition 1. Suppose Assumptions 1–3 hold... As C →∞, in the optimal intervention...

**Feedback**:
Proposition 1 shows optimal interventions are simple for large budgets. This result is derived under specific budget constraint formulations. Add a remark in the Proposition 1 section discussing how the 'simplicity' result degrades when additional realistic constraints are introduced.

---

### 10. Budget Constraint Assumption 3

**Status**: [Pending]

**Quote**:
> Assumption 3. Either w < 0 and C < ∥ b [ˆ] ∥, or w > 0.

**Feedback**:
Assumption 3 requires conditions to ensure the budget constraint binds. These rate conditions on the budget relative to initial benefits may not be satisfied in empirical settings with fixed or small budgets. Discuss the empirical plausibility of these budget sizes in the context of Assumption 3.

---

### 11. Budget Condition Proposition 2

**Status**: [Pending]

**Quote**:
> Proposition 2. Suppose w > 0, Assumptions 1 and 2 hold... if C > [2] ∥ [**b]** [ˆ] [∥] [2]...

**Feedback**:
Proposition 2's approximation results require specific rate conditions on the budget relative to eigenvalue gaps. These conditions may not be satisfied in empirical settings. Provide a calibration or discussion on the empirical plausibility of these budget sizes required for the approximation to hold.

---

### 15. Circle Network Structured Example

**Status**: [Pending]

**Quote**:
> Figure 1 illustrates some eigenvectors/principal components of a circle network with 14 nodes...

**Feedback**:
The proof of Theorem 1 assumes a generic b̂ such that b̂_ℓ ≠ 0. However, in structured networks like the circle network shown in Figure 1, symmetries can cause certain eigenvector projections to be exactly zero. Discuss the circle network case explicitly as a boundary condition where the generic assumption fails.

---

### 16. Strategic Substitutes Characterization

**Status**: [Pending]

**Quote**:
> In games of strategic substitutes, the order is reversed: the optimal intervention is most similar to the last principal component.

**Feedback**:
The characterization for strategic substitutes relies on the last principal component. This component captures local structure to avoid crowding out. Discuss how this targeting rule performs if the network structure is misestimated, given the known sensitivity of lower eigenvalues to noise.

---

### 17. Incomplete Information Section

**Status**: [Pending]

**Quote**:
> Section 5 studies a setting where the planner has incomplete information about agents' standalone marginal returns.

**Feedback**:
Section 5 extends the analysis to incomplete information, but still relies on the Linear-Quadratic structure. Real-world planners often face non-linear cost structures or threshold effects not captured here. Add a note in Section 5 acknowledging that the incomplete information results also inherit the LQG robustness limitations.

---

### 18. Welfare Function Definition

**Status**: [Pending]

**Quote**:
> The utilitarian social welfare at equilibrium is given by the sum of the equilibrium utilities:

**Feedback**:
The utilitarian welfare function assumes equal weighting of all agents. In policy contexts, equity constraints or distributional concerns may prevent the concentration of resources on a single spectral component implied by the optimal solution. Discuss how the results might change if distributional weights were applied to the welfare function.

---
