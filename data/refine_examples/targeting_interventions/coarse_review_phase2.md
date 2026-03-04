# TARGETING INTERVENTIONS IN NETWORKS

**Date**: 03/04/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Reliance on Symmetric Network Structures**

The core theoretical results and economic intuition depend on eigenvalue decomposition, which strictly requires the network adjacency matrix to be symmetric. However, many real-world economic and social networks are directed, where eigenvalues may be complex and the interpretation of principal components becomes ambiguous without Singular Value Decomposition (SVD). The main text presents the symmetric case as the primary contribution, potentially overstating applicability and risking misleading readers about eigenvector centrality rules in directed graphs. The authors should either restrict claims to undirected networks explicitly or integrate the SVD-based analysis into the primary narrative to ensure robustness.

**Sensitivity to Network Estimation Errors**

The optimal intervention strategy relies critically on precise knowledge of the network's spectral properties, yet eigenvectors and eigenvalues can be highly unstable under perturbation, particularly when spectral gaps are small. There is currently no analysis of how estimation errors in the network topology propagate to welfare losses or mis-targeting of interventions, representing a significant threat to external validity. A sensitivity analysis quantifying the degradation of welfare gains under varying levels of network measurement error is necessary to validate the practical utility of the proposed targeting mechanism.

**Restrictiveness of Linear-Quadratic Payoff Assumptions**

The orthogonality of intervention effects across principal components is a direct mathematical consequence of the linear-quadratic utility and cost assumptions, which may not hold in real-world strategic interactions exhibiting non-linearities such as saturation or thresholds. If payoffs are non-linear, the decomposition fails as components interact, potentially undermining the simple intervention result for large budgets. The analysis should more clearly delineate the class of games where this decomposition holds, discuss robustness to non-linear perturbations, or provide bounds on the approximation error for non-linear settings.

**Equilibrium Uniqueness and Stability Conditions**

The welfare analysis assumes a unique equilibrium outcome determined by the intervention, yet games of strategic complements are prone to multiple equilibria. A large enough intervention could theoretically push the system across a threshold where uniqueness is no longer guaranteed or trigger a shift to a different equilibrium branch, rendering the linear comparative statics invalid. The authors should explicitly articulate the stability constraints on the intervention size and discuss how equilibrium selection mechanisms might alter the optimal targeting strategy or predicted welfare effects.

**Practical Feasibility and Welfare Quantification**

The claim that optimal interventions are 'simple' depends inversely on the spectral gap, implying the budget required for this approximation to hold may be unrealistically large in common network topologies without quantification. Furthermore, the paper provides limited quantitative comparison against naive uniform intervention strategies to establish the practical value of the complex targeting method. To justify the informational and computational costs, the authors should quantify what constitutes a 'large budget' relative to typical structures and include explicit welfare comparisons between the optimal targeted intervention and uniform benchmarks.

**Violation of Distinct Eigenvalues Assumption in Principal Component Illustration**

Assumption 2 explicitly states that 'all eigenvalues of G are distinct' to ensure the principal component decomposition is uniquely determined. However, Figure 1 utilizes a circle network, which is acknowledged in Footnote 11 as 'nongeneric in that eigenvectors are not uniquely determined.' While the authors argue that a small perturbation would resolve this, the actual data used in the figure violates the strict theoretical assumption required for the uniqueness claims made in the accompanying text (Section 3).

**Unverified 'Large Budget' Condition in Simulation Design**

Proposition 1 characterizes optimal interventions in the limit as the budget $C \to \infty$, and Proposition 2 provides a specific lower bound for $C$ (dependent on the network's spectral gap) for the intervention to be considered 'simple' or close to the limit. Figure 2 uses a fixed budget of $C=500$ and claims the results are 'in line with' the large budget proposition. However, the simulation design does not verify whether $C=500$ satisfies the spectral gap-dependent bound derived in Proposition 2 for the specific 11-node network used. This creates a potential mismatch between the theoretical conditions for the asymptotic result and the specific parameter choice in the implementation.

**Status**: [Pending]

---

## Detailed Comments (18)

### 4. Equilibrium Uniqueness and Stability Conditions [CRITICAL]

**Status**: [Pending]

**Quote**:
> The welfare analysis assumes a unique equilibrium outcome determined by the intervention, yet games of strategic complements are prone to multiple equilibria.

**Feedback**:
Explicitly articulate stability constraints on intervention size and discuss how equilibrium selection mechanisms might alter optimal targeting or welfare effects.

---

### 1. Reliance on Symmetric Network Structures

**Status**: [Pending]

**Quote**:
> The core theoretical results and economic intuition depend on eigenvalue decomposition, which strictly requires the network adjacency matrix to be symmetric.

**Feedback**:
The analysis relies on eigenvalue decomposition which assumes symmetry. Real-world networks are often directed. Restrict claims to undirected networks explicitly or integrate SVD-based analysis to ensure robustness for directed graphs.

---

### 2. Sensitivity to Network Estimation Errors

**Status**: [Pending]

**Quote**:
> The optimal intervention strategy relies critically on precise knowledge of the network's spectral properties, yet eigenvectors and eigenvalues can be highly unstable under perturbation...

**Feedback**:
Add a sensitivity analysis quantifying welfare degradation under varying levels of network measurement error to validate practical utility.

---

### 3. Restrictiveness of Linear-Quadratic Payoff Assumptions

**Status**: [Pending]

**Quote**:
> The orthogonality of intervention effects across principal components is a direct mathematical consequence of the linear-quadratic utility and cost assumptions...

**Feedback**:
Delineate the class of games where this decomposition holds, discuss robustness to non-linear perturbations, or provide bounds on approximation error for non-linear settings.

---

### 5. Practical Feasibility and Welfare Quantification

**Status**: [Pending]

**Quote**:
> The claim that optimal interventions are 'simple' depends inversely on the spectral gap, implying the budget required for this approximation to hold may be unrealistically large...

**Feedback**:
Quantify what constitutes a 'large budget' relative to typical structures and include explicit welfare comparisons between optimal targeted intervention and uniform benchmarks.

---

### 6. Violation of Distinct Eigenvalues Assumption in Figure 1

**Status**: [Pending]

**Quote**:
> Assumption 2 explicitly states that 'all eigenvalues of G are distinct'... However, Figure 1 utilizes a circle network, which is acknowledged in Footnote 11 as 'nongeneric...'

**Feedback**:
Ensure the data used in figures strictly adheres to theoretical assumptions (distinct eigenvalues) or clarify how the nongeneric case is handled without violating uniqueness claims.

---

### 7. Unverified 'Large Budget' Condition in Simulation

**Status**: [Pending]

**Quote**:
> Figure 2 uses a fixed budget of C=500 and claims the results are 'in line with' the large budget proposition. However, the simulation design does not verify whether C=500 satisfies the spectral gap-dependent bound...

**Feedback**:
Verify and report whether the specific budget C=500 satisfies the spectral gap-dependent bound derived in Proposition 2 for the 11-node network used.

---

### 8. Derivation of Property A Welfare Function

**Status**: [Pending]

**Quote**:
> Property A. The aggregate equilibrium utility is proportional to the sum of the squares of the equilibrium actions...

**Feedback**:
Derive the conditions under which Property A holds from primitive utility functions to close the logical gap, rather than stating it as a standalone property.

---

### 13. Proposition 2 Budget Bound Tightness

**Status**: [Pending]

**Quote**:
> C _>_ [2] _[∥]_ _**[b]**_ [ˆ] _[∥] [2], then W _/W_ _[s]_ _<_ 1 +

**Feedback**:
Discuss whether the lower bound on C is tight or if alternative conditions exist for near-optimality with more reasonable budgets given the spectral gap dependency.

---

### 18. Proposition 4 Variance Stability Conditions

**Status**: [Pending]

**Quote**:
> Suppose the planner likes variance (i.e., w _>_ 0). If the game has strategic complements ( β _>_ 0), then Var( _**u**_ _[ℓ]_ ( _**G**

**Feedback**:
Explicitly state the stability condition (e.g., βλ_1 < 1) required for the variance ordering to hold in the proposition.

---

### 9. Ambiguous Definition of Simple Interventions [MINOR]

**Status**: [Pending]

**Quote**:
> We then turn to the study of _simple_ optimal interventions, i.e., ones where the intervention... is determined by a single network statistic...

**Feedback**:
Rigorously define 'simple' mathematically (e.g., proportional to eigenvector centrality) to avoid ambiguity about which network statistic is implied.

---

### 10. Imprecise Genericity Claim in Assumption 2 [MINOR]

**Status**: [Pending]

**Quote**:
> all eigenvalues of _**G**_ are distinct (the latter condition holds generic

**Feedback**:
Clarify the measure or topology with respect to which genericity holds (e.g., 'for almost all G in the space of symmetric matrices under Lebesgue measure').

---

### 11. Budget Constraint Notation and Properties [MINOR]

**Status**: [Pending]

**Quote**:
> [approximate] K ( b , b [ˆ] ) = \sum_{i∈N} (b_i - \hat{b}_i)^2 ≤ C,

**Feedback**:
Clean up notation artifacts and explicitly state whether C is non-negative, if the inequality is binding, and define convexity/differentiability of cost function K.

---

### 12. Undefined Similarity Ratio When Status Quo Orthogonal [MINOR]

**Status**: [Pending]

**Quote**:
> [approximate] we define the similarity ratio of u^l(G) to be the fraction r*_l = rho(y*, u^l(G)) / rho(b_hat, u^l(G)).

**Feedback**:
Handle the case where the status quo vector is orthogonal to a principal component (denominator zero) by restricting attention or defining the ratio separately.

---

### 14. Figure 2 Reproducibility [MINOR]

**Status**: [Pending]

**Quote**:
> Figure 2 presents optimal targets when the budget is large - in particular, for C = 500. We consider an 11-node undirected network with

**Feedback**:
Provide the full adjacency matrix of the 11-node network in an appendix or describe the structure precisely to ensure reproducibility.

---

### 15. Undefined Notation in Definition 2 [MINOR]

**Status**: [Pending]

**Quote**:
> Definition 2 (Simple interventions). An intervention is _simple_ if, for all

**Feedback**:
Define all notation (e.g., b̂) locally within Definition 2 or the immediate context to ensure self-containment.

---

### 16. Confusing Terminology for Smallest Eigenvalues [MINOR]

**Status**: [Pending]

**Quote**:
> recall that the smallest two eigenvalues, _λn_ and _λn−_ 1,

**Feedback**:
Clarify 'smallest' as 'algebraically smallest' or 'most negative' to avoid ambiguity with magnitude.

---

### 17. Incomplete Variance Intervention Section [MINOR]

**Status**: [Pending]

**Quote**:
> We prove a result on optimal intervention for all cost functions satisfying certain s

**Feedback**:
State the proposition clearly in the main text before referring to the appendix for the proof.

---
