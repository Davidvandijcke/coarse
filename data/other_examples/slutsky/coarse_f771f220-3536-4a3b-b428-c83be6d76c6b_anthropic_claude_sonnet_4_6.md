# Nonparametric Testability of Slutsky Symmetry

**Date**: 03/17/2026
**Domain**: social_sciences/economics
**Taxonomy**: academic/working_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper addresses whether Slutsky symmetry—a core restriction from consumer theory—is nonparametrically testable in a heterogeneous-agent demand system with endogenous income. Building on the control-function framework of Dette et al. (2016) and the quantile-derivative approach of Hoderlein and Mammen (2007), the paper derives a conditional quantile restriction (equation 2) that it claims characterizes the testable content of Slutsky symmetry when there are three or more goods. The main result, Theorem 2.1, is presented as refuting a conjecture by Maes and Malhotra (2024) that symmetry is nontestable in this setting.

Below are the most important issues identified by the review panel.

**Theorem 2.1 Establishes Only a Necessary Condition, Yet the Paper Claims Full Testability of Slutsky Symmetry**

The paper's central contribution—refuting the conjecture that Slutsky symmetry is nontestable—requires showing that equation (2) has genuine empirical content: that it is violated by some data-generating process consistent with the model assumptions but violating symmetry. Theorem 2.1 explicitly derives equation (2) as a necessary condition for symmetry, but never establishes sufficiency. Without sufficiency, a demand system could satisfy equation (2) while violating Slutsky symmetry, making any test based on equation (2) incomplete. The abstract and conclusion repeatedly claim that symmetry is 'testable' and that the Maes–Malhotra conjecture is 'false,' but these claims require either (a) a proof that equation (2) is also sufficient for the average conditional Slutsky symmetry being tested, or (b) an explicit example of a symmetry-violating demand system for which equation (2) fails, confirming the condition has discriminating power. It would be helpful to reframe the contribution precisely—either as a necessary-and-sufficient characterization (if sufficiency can be proved) or as a necessary testable implication whose empirical content relative to the full restriction of symmetry is clearly delineated.

**Individual vs. Average Symmetry Conflation in the Proof of Theorem 2.1**

The proof of Theorem 2.1 moves from the assumption that the Slutsky matrix S is symmetric to equation (3) by equating conditional expectations of e_i'Se_j and e_j'Se_i. This step is valid if S is symmetric at the individual level (almost surely in A), but the model allows S to vary with the latent A, making individual-level and average symmetry distinct conditions. If the paper intends to test average Slutsky symmetry—which Kono (2025) argues is nontestable—the proof strategy risks being vacuous or circular. If it intends to test individual-level symmetry, the passage from individual symmetry to the conditional expectation equality in equation (3) holds trivially, but then equation (2) reflects only average behavior and may not detect violations that cancel in expectation. The authors should clarify precisely which notion of symmetry is being tested and verify that the proof logic, the disintegration argument, and the final testable restriction are all consistent with that notion. The disintegration theorem is invoked to equate two sequential decompositions, but the intermediate sigma-algebra claim is either unnecessary or potentially misleading and should be streamlined.

**Identification Gap: The Correction Terms D_ij and the Conditioning on Latent V Are Not Shown to Be Empirically Recoverable**

Equation (2) contains correction terms D_ij(w*) and D_ij^(x)(w*) involving the conditional distribution F_{Y_i|W,Y_j} differentiated with respect to prices and income, where W = (P,X,Q,V) includes the unobservable control-function residual V. Since V is latent, F_{Y_i|W,Y_j} is not directly observable, and the paper does not provide a formal identification argument showing that these terms—and the quantile derivatives in Lemma 2.1—are point-identified from the observable joint distribution of (Y,P,X,Q,S). The proof of Lemma 2.1 correctly notes that the correction terms do not vanish under Assumption 2.2, but treats them as identified without verification. It would be helpful to add a formal identification lemma showing that substituting the control-function residual V = μ^{-1}(P,Q,S,X) for the latent V is valid, and specifying what additional smoothness or consistency conditions on the first-stage inversion are required for the quantile conditions in Theorem 2.1 to remain valid in terms of observables.

**Scalar Unobservable V Imposes Strong Implicit Restrictions That May Conflict with the Claimed Generality of Preference Heterogeneity A**

Assumption 2.1 specifies that income X = μ(P,Q,S,V) with V scalar and μ invertible in V, which is the foundation of the control-function approach. However, the demand equation allows A to be infinite-dimensional, appropriate for full generality of preferences. The conditional independence A ⊥⊥ (P,X) | (Q,V) required by Assumption 2.2 then demands that a single scalar residual absorbs all correlation between the infinite-dimensional preference heterogeneity and the endogenous income variable. If income endogeneity arises from multiple sources of unobserved heterogeneity not reducible to a scalar index, Assumption 2.2 fails and the identification of the Slutsky terms in Lemma 2.1 breaks down. The paper acknowledges the scalar S assumption as 'for ease of exposition' but does not discuss the scalar V restriction as a substantive limitation. It would be helpful to state explicitly what economic restrictions on the joint distribution of (A,V) are implied by Assumption 2.2 when V is scalar, whether these are plausible in standard multi-good demand settings, and whether the framework could be extended following multivariate instrument approaches such as Gunsilius (2023).

**Regularity Conditions in Assumption A.1 Are High-Level and May Implicitly Favor the Null Hypothesis**

Assumption A.1 imposes approximate differentiability of φ (condition 4) and joint absolute continuity of (e_i'Y, ∂_{w_{1s}}φ) given (W, e_j'Y) (condition 5). Condition 5 is particularly strong: it requires that the joint distribution of demand and its price derivative, conditional on the demand level of another good, is absolutely continuous—a non-primitive condition not derived from assumptions on preferences or the distribution of A. In demand systems, the mapping from preferences to demands can be non-smooth at kinks, corner solutions, or non-convexities, and the conditional distribution of ∂_{w_{1s}}φ given e_j'Y = y_j* may fail to be absolutely continuous precisely in cases where Slutsky symmetry is violated. If condition 5 is more easily satisfied when symmetry holds than when it fails, the regularity assumption may implicitly reduce the power of any test based on Theorem 2.1. It would be helpful to discuss whether Assumption A.1 can be derived from primitive conditions on the utility function and the distribution of A, and to verify that it does not rule out the alternatives against which the test is intended to have power. The proof step factoring k_{α_j,j}(w*) out of the conditional expectation in the B_2 calculation should also be made explicit, with verification that Lemma 2.1 applies to the income derivative in the same way as the price derivative.

**The Marginal Contribution Relative to Existing Literature and the Role of the L≥3 Condition Are Not Precisely Delineated**

The paper positions itself as closing the gap left by Dette et al. (2016) on symmetry testing, but does not clearly articulate what the binding technical obstacle was that required the new bivariate quantile construction. Section 2.1 states that the result of Hoderlein and Mammen (2007) cannot be generalized to the multivariate setting directly, citing Hoderlein and Mammen (2009), but does not explain precisely which step fails and how the conditional-marginal quantile decomposition circumvents the non-identification result. Relatedly, Lemma 2.1 is stated only for L≥3 without explanation of what fails for L=2, even though the proof in Appendix A.2 does not appear to use L≥3 in any essential way—leaving it unclear whether the condition is a genuine restriction or an expository artifact. Since Section 3 connects the results to the two-good welfare analysis of Hausman and Newey (2016), clarifying the L=2 case is important for understanding the scope of the contribution. It would be helpful to include a brief formal remark explaining why the bivariate joint quantile K_{ij} is not identified without the conditional-marginal decomposition, how the new construction avoids the Hoderlein–Mammen (2009) obstruction, and whether L≥3 is a genuine technical requirement or can be relaxed.

**Status**: [Pending]

---

## Detailed Comments (13)

### 1. Missing transpose in Slutsky income-effect outer product

**Status**: [Pending]

**Quote**:
> The Slutsky matrix $\mathcal{S}(p,x,u)$ takes the form
> 
> $\mathcal{S}=D_{p}\psi(p,x,u)+\partial_{x}\psi(p,x,u)\psi(p,x,u),$
> 
> where $D_{p}$ is the Jacobian of Marshallian demands with respect to prices and $\partial_{x}$ is a vector of partial derivatives of Marshallian demands with respect to income.

**Feedback**:
Re-deriving: psi maps into R^{L-1}, so partial_x psi is an (L-1)×1 column vector and psi is also (L-1)×1. The standard Slutsky entry (i,j) is partial_{p_j} psi_i + psi_j * partial_x psi_i, which in matrix form is D_p psi + (partial_x psi)(psi)^top—an outer product yielding an (L-1)×(L-1) matrix. As written, (partial_x psi)(psi) without a transpose attempts to multiply two column vectors, which is not a valid matrix product and cannot be added to the (L-1)×(L-1) matrix D_p psi. Rewrite the displayed equation as S = D_p psi(p,x,u) + partial_x psi(p,x,u) psi(p,x,u)^top to restore dimensional consistency.

---

### 2. Joint bivariate quantile notation treats isoquant as point

**Status**: [Pending]

**Quote**:
> We also need to make use of the *joint bivariate $\alpha$-quantile* $K_{ij}(\alpha\mid w)$ for elements $(Y_{i},Y_{j})\equiv\left(e^{\prime}_{i}Y,e^{\prime}_{j}Y\right)$ of the vector $Y\in\mathbb{R}^{L-1}$, which is defined as
> 
> $P\left((Y_{i},Y_{j})\leq K_{ij}(\alpha\mid w)\mid W=w\right)=\alpha.$
> 
> Note that $K_{ij}$ is not unique without further assumption: it is not a point but an isoquant in $\mathbb{R}^{2}$

**Feedback**:
The defining equation uses K_{ij}(alpha|w) as a single point in R^2 (the componentwise CDF evaluated at a point equals alpha), but the immediately following remark states it is a curve, not a point. The set of k in R^2 satisfying P((Y_i,Y_j) <= k | W=w) = alpha is a level curve of the bivariate CDF, so the notation is formally inconsistent with the remark. It is not clear how set-valued K_{ij} enters subsequent expressions. Add a clarification specifying either a selection rule that pins down a unique K_{ij}(alpha|w) from the isoquant, or an explicit statement that K_{ij}(alpha|w) denotes the isoquant as a set together with how it enters subsequent expressions.

---

### 3. partial_2 notation conflates differentiation with respect to two structurally different arguments

**Status**: [Pending]

**Quote**:
> \partial_{w_{1s}}k_{\alpha_{j},j}(w^{*})\left[\partial_{2}k_{\gamma_{i|j},i}(w^{*},k_{\alpha_{j},j}(w^{*}))+\frac{\partial_{2}F_{Y_{i}|W=w^{*},Y_{j}=k_{\alpha_{j},j}(w^{*})}(k_{\gamma_{i|j},i}(w^{*},k_{\alpha_{j},j}(w^{*})))}{f_{Y_{i}|W=w^{*},Y_{j}=k_{\alpha_{j},j}(w^{*})}(k_{\gamma_{i|j},i}(w^{*},k_{\alpha_{j},j}(w^{*})))}\right]

**Feedback**:
The symbol partial_2 appears twice but refers to differentiation with respect to structurally different arguments. For k_{gamma_{i|j},i}(w, y_j), partial_2 is the derivative with respect to y_j (the second positional argument). For F_{Y_i|W=w*, Y_j=y_j}(y_i), if partial_2 is read uniformly as the derivative with respect to the second positional argument of the function as written, that argument is the evaluation point y_i, giving f/f = 1 and collapsing the bracket incorrectly. The intended meaning must be d/dy_j of the CDF with respect to the conditioning value. Rewrite partial_2 F_{Y_i|W=w*, Y_j=k_{alpha_j,j}(w*)}(k_{gamma_{i|j},i}(...)) as (d/dy_j) F_{Y_i|W=w*, Y_j=y_j}(k_{gamma_{i|j},i}(w*, y_j)) evaluated at y_j = k_{alpha_j,j}(w*) to distinguish it from the positional partial_2 applied to the quantile function.

---

### 4. C_ij correction terms may vanish identically by implicit function theorem

**Status**: [Pending]

**Quote**:
> C _ {i j} (w ^ {*}) := \partial_ {2} k _ {\gamma_ {i | j}, i} (w ^ {*}, k _ {\alpha_ {j}, j} (w ^ {*})) + \frac {\partial_ {2} F _ {Y _ {i} | W = w ^ {*} , Y _ {j} = k _ {\alpha_ {j} , j} (w ^ {*})} (k _ {\gamma_ {i | j} , i} (w ^ {*} , k _ {\alpha_ {j} , j} (w ^ {*})))}{f _ {Y _ {i} | W = w ^ {*} , Y _ {j} = k _ {\alpha_ {j} , j} (w ^ {*})} (k _ {\gamma_ {i | j} , i} (w ^ {*} , k _ {\alpha_ {j} , j} (w ^ {*})))}

**Feedback**:
The conditional quantile satisfies F_{Y_i|W=w*, Y_j=y_j}(k_{gamma_{i|j},i}(w*, y_j)) = gamma_{i|j} (constant in y_j). Differentiating both sides with respect to y_j via the implicit function theorem gives f * partial_2 k + partial_{y_j} F = 0, so partial_2 k = -partial_{y_j}F/f. If partial_2 F in the numerator of C_{ij} also denotes differentiation with respect to the conditioning value y_j, then C_{ij} = -partial_{y_j}F/f + partial_{y_j}F/f = 0 identically, making the economic discussion of when C_{ij} is small vacuous. The alternative interpretation that partial_2 F denotes differentiation with respect to the evaluation argument gives partial_2 F/f = 1, making C_{ij} = partial_2 k + 1, which is dimensionally inconsistent. Rewrite the definition of C_{ij} using distinct notation distinguishing differentiation with respect to the conditioning value versus the evaluation point, and verify via the implicit function theorem that the resulting expression is not identically zero.

---

### 5. nabla_{p,1} operator undefined and ambiguous relative to nabla_p

**Status**: [Pending]

**Quote**:
> D _ {i j} (w ^ {*}) := \frac {\nabla_ {p , 1} F _ {Y _ {i} | W = w ^ {*} , Y _ {j} = k _ {\alpha_ {j} , j} (w ^ {*})} (k _ {\gamma_ {i | j} , i} (w ^ {*} , k _ {\alpha_ {j} , j} (w ^ {*})))}{f _ {Y _ {i} | W = w ^ {*} , Y _ {j} = k _ {\alpha_ {j} , j} (w ^ {*})} (k _ {\gamma_ {i | j} , i} (w ^ {*} , k _ {\alpha_ {j} , j} (w ^ {*})))}

**Feedback**:
The operator nabla_{p,1} appears in the definitions of D_{ij} and in equation (2) but is never defined. In equation (2), the leading term uses nabla_{p,1} k_{gamma_{i|j},i}(w*, k_{alpha_j,j}(w*)), while the C_{ij} correction uses nabla_p k_{alpha_j,j}(w*) without the subscript 1. If nabla_{p,1} denotes the partial gradient with respect to the price component of the first argument w* holding the second argument k_{alpha_j,j}(w*) fixed, it differs from the total price derivative which includes the indirect effect through the second argument. Since the functions in D_{ij} take (w*, k_{alpha_j,j}(w*)) as arguments and w* contains prices, this distinction directly affects the correctness of equation (2). Add a sentence immediately after the definition of D_{ij} clarifying that nabla_{p,1} denotes the partial gradient with respect to the price component of the first argument w* holding the second argument fixed, and verify this is consistent with the derivation leading to equation (2).

---

### 6. Index range in Assumption A.1 condition 5 exceeds demand dimension

**Status**: [Pending]

**Quote**:
> The conditional distribution of $(e_i'Y, \partial_{w_1s}\phi)$ given $(P, X, Z, e_j'Y)$ is absolutely continuous with respect to Lebesgue measure for $(W, e_j'Y) = (w^*, k_{\alpha,j}(w^*))$ and all $i, j \in \{1, \ldots, L\}$.

**Feedback**:
From Assumption 2.1, Y takes values in R^{L-1}, so valid indices for e_i and e_j run from 1 to L-1. The preamble to Assumption A.1 explicitly states 'all i,j = 1,2,...,L-1', and conditions 1 and 2 use the same bound. Condition 5 is the sole place where the upper bound is written as L. For a concrete check: with L=3 goods, Y is in R^2, so e_3'Y would require a third component that does not exist. Rewrite 'all $i, j \in \{1, \ldots, L\}$' as 'all $i, j \in \{1, \ldots, L-1\}$' because Y is in R^{L-1} and the index L is out of range.

---

### 7. Condition 4 opening signature of phi omits Q and A arguments

**Status**: [Pending]

**Quote**:
> The function $\phi(p,x,u)$ is approximately differentiable in all dimensions of $w_1 := (p,x) \in \mathbb{R}^L$ in the sense that there exist measurable functions $\Delta_s, s = 1,\ldots,L$ satisfying

**Feedback**:
Assumption 2.1 defines phi: P × X × Q × A → Y with four arguments, written phi(P,X,Q,A) in the structural equation Y = phi(P,X,Q,A). Condition 4 opens with 'The function phi(p,x,u)' using only three arguments with a scalar placeholder u, conflicting with the four-argument model signature. The display equation within the same condition correctly uses four arguments: phi(w*_{1s}+delta, w*_{-1s}, z*, A). The analogous condition in Dette, Hoderlein and Neumeyer (2016) uses a scalar unobservable because their model is univariate; the present paper's phi has an infinite-dimensional latent argument A, making the scalar u a misrepresentation. Rewrite 'The function $\phi(p,x,u)$' as 'The function $\phi(p,x,z^*,A)$' to match the four-argument signature established in Assumption 2.1 and the display equation that follows.

---

### 8. Sigma-algebra coincidence claim imprecise for disintegration argument

**Status**: [Pending]

**Quote**:
> By uniqueness of the disintegration, the $\sigma$-algebras generated by these two decompositions coincide at the point $(y_{i}^{*},y_{j}^{*})$, so that

**Feedback**:
The disintegration theorem guarantees a.e. uniqueness of the regular conditional distribution given a sub-sigma-algebra. Decompositions (i) and (ii) generate different sequential filtrations—sigma(Yj) ⊂ sigma(Yj,Yi) versus sigma(Yi) ⊂ sigma(Yi,Yj)—which are genuinely distinct sigma-algebras, so the claim that they coincide is not what the cited theorem establishes. What the theorem guarantees is that both sequential decompositions yield the same joint regular conditional distribution of (Yi,Yj) given W=w* at the atom containing (yi*,yj*), and hence the same conditional expectation. The conclusion is correct but the stated justification is imprecise. Rewrite 'By uniqueness of the disintegration, the sigma-algebras generated by these two decompositions coincide at the point (yi*,yj*)' as 'By uniqueness of the joint disintegration at (yi*,yj*), both sequential decompositions yield the same regular conditional distribution of (Yi,Yj) given W=w*, and hence the same conditional expectation of any integrable function at that point.'

---

### 9. Final subtraction and rearranging step entirely omitted from proof of Theorem 2.1

**Status**: [Pending]

**Quote**:
> The same result holds when switching the roles of $i$ and $j$ (using decomposition (ii) with indices $\gamma_{j|i}, \alpha_i$), and subtraction and rearranging gives the claim.

**Feedback**:
The proof computes multi-term expressions for e_i'(B1+B2)e_j under decomposition (i) and for e_j'(B1+B2)e_i under decomposition (ii), then asserts 'subtraction and rearranging gives the claim' without showing any algebra. The theorem's stated testable restriction is a specific equation involving quantile derivatives and CDF/density ratios; it is not obvious that the difference of the two multi-term expressions simplifies to exactly the stated condition without explicit cancellations being verified. This is the central algebraic step of the entire theorem. Add after 'subtraction and rearranging gives the claim' a displayed equation showing the full subtraction and the algebraic steps by which the terms reduce to the theorem's stated testable restriction.

---

### 10. Testability claim overstated: necessary condition presented as full refutation of conjecture

**Status**: [Pending]

**Quote**:
> This shows that a recent conjecture *(Maes and Malhotra, 2024)* is false and opens the door to testing a empirically informed version of rationality with heterogeneity.

**Feedback**:
Theorem 2.1 derives equation (2) only as a necessary condition for Slutsky symmetry. A necessary condition has empirical content only if it can actually be violated by some data-generating process that satisfies the model assumptions but violates symmetry. The paper provides neither (a) a proof that equation (2) is sufficient for the relevant notion of symmetry, nor (b) a concrete example of a symmetry-violating demand system for which equation (2) fails. Without either, the claim that the conjecture is 'false' is not demonstrated—if every DGP consistent with Assumptions 2.1–2.2 and A.1 satisfies equation (2) regardless of whether the Slutsky matrix is symmetric, the condition has no discriminating power. Rewrite 'This shows that a recent conjecture (Maes and Malhotra, 2024) is false' to accurately reflect that Theorem 2.1 provides a necessary condition expressible in observables, and that establishing the conjecture's falsity requires either a sufficiency proof or a demonstration that the condition fails for some symmetry-violating DGP.

---

### 11. Estimability claim for correction terms involving latent V is unsubstantiated

**Status**: [Pending]

**Quote**:
> Since it involves only conditional and marginal quantiles and their derivatives, all of its components are estimable from data via conditional quantile inference methods.

**Feedback**:
The correction terms D_ij(w*) and D_ij^{(x)}(w*) in equation (2) involve the conditional distribution F_{Y_i|W,Y_j} differentiated with respect to prices and income, where W = (P,X,Q,V) includes the latent control-function residual V. Since V is unobservable, these terms are not directly estimable without a prior identification and estimation step for V via the first-stage inversion V = mu^{-1}(P,Q,S,X). The paper does not provide a formal identification lemma showing that substituting the estimated residual V-hat for V preserves the validity of the quantile conditions, nor does it address the smoothness or consistency requirements on the first-stage inversion. Rewrite this sentence to acknowledge the two-step nature of the estimation and the conditions required for the plug-in to be valid.

---

### 12. L≥3 condition stated without dimensional justification; bivariate label misleads for L>3

**Status**: [Pending]

**Quote**:
> Then for $L\geq 3$, the following holds
> 
> $E\Big{[}\partial_{w_{1s}}\phi\ \Big{|}\ W=w^{*},\,e^{\prime}_{i}Y=k_{\gamma_{i|j},i}(w^{*},k_{\alpha_{j},j}(w^{*})),\,e^{\prime}_{j}Y=k_{\alpha_{j},j}(w^{*})\Big{]}$

**Feedback**:
For L=2, Y is scalar so no distinct pair (i,j) with i≠j exists; the lemma is vacuous rather than false, and L≥3 is simply the requirement that two distinct demand components exist for the bivariate conditioning to be well-defined. The paper states the condition without this explanation. Separately, the paper later describes the Slutsky symmetry case as 'bivariate,' but for L goods the Slutsky matrix has (L-1)(L-2)/2 off-diagonal pairs; the bivariate Lemma 2.1 handles each pair separately and suffices for all L≥3, but the label could mislead readers into thinking the paper only addresses L=3. Add a parenthetical after the L≥3 condition explaining the dimensional necessity, and rewrite the 'bivariate' description as: 'Since each Slutsky symmetry condition S_{ij}=S_{ji} reduces to a pairwise condition on (Y_i,Y_j), the bivariate Lemma 2.1 suffices for all L≥3.'

---

### 13. Consistency of beta with marginal and conditional quantile indices unverified in proof

**Status**: [Pending]

**Quote**:
> This point lies on the isoquant $K_{ij}(\beta \mid w^*)$ for $\beta := F_{Y_i, Y_j | W=w^*}(y_i^*, y_j^*)$.

**Feedback**:
The proof defines beta as the joint CDF F_{Yi,Yj|W=w*}(yi*,yj*) and separately defines alpha_j as the marginal quantile index of Yj and gamma_{i|j} as the conditional quantile index of Yi given Yj=yj*. The relationship between beta and the pair (alpha_j, gamma_{i|j}) is not made explicit. In general, F_{Yi,Yj|W=w*}(yi*,yj*) does not factor as F_{Yj|W=w*}(yj*) × F_{Yi|W=w*,Yj=yj*}(yi*) unless Yi and Yj are conditionally independent given W=w*, which is not assumed. Without clarifying how beta relates to alpha_j and gamma_{i|j}, it is unclear whether the disintegration is being applied to the correct conditioning sigma-algebra. Add a sentence after 'for beta := F_{Yi,Yj|W=w*}(yi*,yj*)' clarifying that alpha_j = F_{Yj|W=w*}(yj*) and gamma_{i|j} = F_{Yi|W=w*,Yj=yj*}(yi*) parametrize the two sequential disintegrations independently of beta, and explaining the relationship between the joint and sequential parametrizations.

---
