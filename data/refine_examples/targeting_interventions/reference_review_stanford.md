Summary
The paper studies how a planner should optimally target incentive interventions in linear-quadratic network games where a symmetric network mediates strategic spillovers (complements or substitutes) and possibly pure externalities. The key methodological contribution is a principal-components (eigenbasis) decomposition of the intervention space, which renders the planner’s problem separable across orthogonal components and yields a closed-form characterization: the optimal intervention tilts toward higher-eigenvalue components in games of complements and toward lower-eigenvalue components in games of substitutes. For large budgets, optimal interventions become simple—concentrating on a single principal component (top for complements, bottom for substitutes)—with sharp bounds that depend on spectral gaps and the norm of the status quo incentives.

Strengths
Technical novelty and innovation
Introduces a clean and powerful principal-components decomposition of the intervention problem that makes the planner’s optimization transparent and tractable.
Establishes an elegant closed-form relationship between optimal similarity weights, eigenvalues, and the budget’s shadow price (Theorem 1), culminating in clear limiting behavior (Proposition 1) and spectral-gap-driven simplicity guarantees (Proposition 2).
Connects strategic structure (complements vs. substitutes) to which part of the spectrum (top vs. bottom eigenvectors) planners should target, offering crisp and generalizable prescriptions.
Experimental rigor and validation
While primarily theoretical, the paper provides intuitive illustrations and numerical examples that align with the theorems and help build intuition (e.g., hub-and-spoke network example; complements vs. substitutes).
Clarity of presentation
The main results are stated clearly with good intuition: amplification factors αℓ, status-quo projections, and budget dual variables jointly determine targeting.
The complement/substitute contrast is explained well, including the interpretation of bottom eigenvectors as cutting across local neighborhoods to reduce crowding out under substitutes.
Significance of contributions
Offers a principled and implementable approach to policy targeting in networked environments, unifying and extending classic insights (e.g., eigenvector centrality) within a planner’s problem.
The spectral-gap conditions for “simple” near-optimality are practical and informative for policy designers who face resource and measurement constraints.
Weaknesses
Technical limitations or concerns
Reliance on symmetry of G and distinct eigenvalues (Assumption 1 and part of Assumption 2) narrows generality; irregular or directed networks are common in applications.
Property A (welfare proportional to squared actions) is restrictive; while extensions are noted, many relevant environments will not directly satisfy this property.
The cost is quadratic and separable; other cost structures (e.g., sparsity, fairness constraints, bounds, or heterogeneity in intervention costs) might materially alter targeting prescriptions.
The solution formula includes terms that are undefined if the status-quo projection onto a component is zero (ρ(b̂, uℓ) = 0), requiring careful treatment of corner cases.
Experimental gaps or methodological issues
No formal robustness analysis to network estimation error or to misspecification of β, which are central in empirical practice.
Sensitivity to near-instability regimes (β close to 1/λ1 or 1/|λn|) is not deeply explored; amplification can explode and may interact with constraints (e.g., nonnegativity).
Clarity or presentation issues
There appears to be a typographical artifact where aℓ* is written as aℓ* = √(αℓ bℓ); the correct relation is aℓ* = √(αℓ) bℓ = bℓ/(1 − βλℓ). Clarifying this avoids dimensional confusion.
The description of “principal components of G” could be tightened: with symmetric G, PCA on columns of G concerns GGᵀ = G², sharing eigenvectors with G but with squared eigenvalues; distinguishing this from standard data-analytic PCA would preempt misinterpretation.
Missing related work or comparisons
Stronger positioning relative to works on planner optimization with endogenous links and multiple activities would help. For instance, Dasaratha and Shah (2602.12897) show that once links are endogenous, instrument choice changes; Balzer and Benlahlou (2602.02403) emphasize cross-activity complementarities and Katz–Bonacich centrality in a related planner’s problem.
Robustness to directed/asymmetric or weighted networks is highly relevant (common in diffusion and information settings); more discussion or summary of the Online Appendix results would help.
Detailed Comments
Technical soundness evaluation
The eigenbasis diagonalization under symmetry cleanly yields aℓ* = bℓ/(1 − βλℓ); with separable quadratic costs and Property A, the Lagrangian decomposition by orthogonal components is sound. The marginal return = marginal cost equalization producing the formula in Theorem 1 is well-motivated.
Existence and uniqueness: the spectral radius assumption ensures (I − βG) is invertible; the condition μ > wαℓ for all ℓ is necessary to keep denominators positive in (5). It would help to include a short proof sketch of the monotone mapping in μ that guarantees uniqueness of the solution to (6).
Corner cases: if b̂ℓ = 0 for some ℓ, then the similarity ratio rℓ* becomes undefined; the optimal solution can still place weight on that component depending on μ and wαℓ. Clarifying whether unused components at baseline can receive positive interventions (they can) and how (5) should be interpreted in that case would improve completeness.
Constraint sets: nonnegativity of actions (a_i ≥ 0) or interventions, or bounds on b, are common. The paper briefly notes feasibility for small enough C; a more formal statement (e.g., existence of a Ĉ that preserves sign constraints) with proof or sufficient conditions would strengthen applicability.
Experimental evaluation assessment
The figures are useful for intuition. Given the policy nature of the paper, small-scale simulations exploring:
sensitivity to errors in G and β,
the impact of constraints (a_i ≥ 0),
and behavior near stability boundaries
would materially enhance practical credibility without detracting from the theory.
Comparison with related work (using the summaries provided)
Relative to Balzer and Benlahlou (2602.02403), this paper provides a single-layer spectral prescription while their multi-activity framework yields Katz–Bonacich-type effective centralities spanning multiple networks and suggests targeting bridge agents. Connecting your principal-component targeting to multi-layer or cross-activity settings (e.g., block matrices and joint spectra) would broaden relevance.
Dasaratha and Shah (2602.12897) demonstrate that with endogenous link formation, the planner’s optimal instrument mix may reverse classic spectral prescriptions (e.g., action vs. link subsidies). It would be valuable to discuss how your targeting logic extends or fails when links adapt endogenously, and whether an analogue of your principal-component targeting emerges for the equilibrium spillover matrix M rather than exogenous G.
Broader epidemiological or diffusion contexts (e.g., 2601.13730) emphasize heterogeneity and network segmentation; discussing how your bottom-component targeting under substitutes might map to “cut-set” immunization strategies or heterogeneous susceptibility would help connect to those literatures.
Discussion of broader impact and significance
The work offers a rigorous and interpretable rule for resource allocation in networked environments with spillovers, directly informing policy in education, R&D, marketing, crime prevention, and public goods. The spectral-gap thresholds for simple policies are especially useful in real settings with limited data on b̂.
Risks include over-amplification near instability or unintended inequities if high-centrality targeting correlates with disadvantaged groups. Adding guidance on fairness-aware variants (e.g., weighted costs or constraints) could make the approach more policy-ready.
Questions for Authors
How do you recommend handling components with zero status-quo projection (ρ(b̂, uℓ) = 0)? Can (5) be extended to include such components explicitly (e.g., via KKT complementary slackness), and under what conditions will the optimum endogenously allocate positive weight to them?
Can you provide a short argument showing existence and uniqueness of μ from (6) for all admissible C, and monotonicity of μ(C), including the limiting behavior as C → 0 and C → ∞ for both w > 0 and w < 0?
Property A is central to the compact characterization. Among the applications where it does not hold, which qualitative conclusions (e.g., top vs. bottom targeting, simplicity at large budgets) remain robust, and which rely critically on quadratic/w^T a* a* structure?
How sensitive are your prescriptions to misspecification of β and to network measurement error? Would a minimax-robust or Bayesian-robust variant of the targeting rule preserve the “top vs. bottom component” guidance?
The paper assumes symmetric G. Do your main results extend cleanly to asymmetric or directed G (via SVD, singular vectors, or the Jordan form)? If so, what replaces the complement/substitute ordering, and how do complex eigenvalues affect targeting?
In practice, constraints such as a_i ≥ 0 or bounds on b_i are common. Can you characterize approximate optimality guarantees for projected or clipped versions of your interventions, or provide sufficient conditions ensuring feasibility at all C below a computable threshold?
Could you comment on the relationship between your principal-component targeting and Katz–Bonacich or diffusion centrality targeting, especially when the planner only has access to node-level statistics rather than the full spectrum?
In the large-budget limit for substitutes, the last eigenvector partitions nodes into opposing sets. Have you considered fairness or political-economy constraints that discourage negative interventions for some groups? How would such constraints warp the targeting geometry?
Overall Assessment
This is a well-executed and conceptually elegant contribution that advances our understanding of optimal targeting in network games. The principal-components framing yields sharp, interpretable prescriptions that differentiate complements from substitutes and connect policy leverage to spectral properties, including a clean simplicity result governed by spectral gaps. The technical approach is sound under the stated assumptions, and the policy relevance is high. The main opportunities for strengthening the paper are (i) clarifying corner cases and minor typographical artifacts, (ii) discussing robustness to asymmetric networks, parameter/network misspecification, and common feasibility constraints, and (iii) situating the results more explicitly relative to endogenous-link and multi-activity planner problems highlighted in recent literature. With these refinements, the paper is strong enough for a top-tier venue in economic theory and networks.

