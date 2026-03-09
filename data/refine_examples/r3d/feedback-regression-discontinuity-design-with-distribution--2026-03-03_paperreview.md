The paper develops a regression discontinuity framework for distribution-valued outcomes (R3D), where treatment is assigned at an aggregate level but outcomes are full within-unit distributions (e.g., wage, test-score, or price distributions). It defines a local average quantile treatment effect (LAQTE), identified by continuity of the conditional average quantile function in the running variable, and proposes estimation via local Fréchet regression in 2-Wasserstein space and a related pointwise local-polynomial approach with an L2 projection to the quantile cone. The paper derives uniform asymptotic normality, valid multiplier bootstrap confidence bands, and a data-driven bandwidth selector, demonstrates performance in simulations, and applies the method to close gubernatorial elections to study effects on within-state income distributions.

Strengths
Technical novelty and innovation
Introduces an RDD framework for random distributions, a practically important but methodologically underdeveloped setting.
Defines LAQTE as an average quantile effect and connects it to the 2-Wasserstein barycenter, providing a geometrically meaningful estimand.
Proposes a distribution-valued local polynomial estimator via local Fréchet regression, avoiding quantile crossing with a single bandwidth and leveraging the full distribution.
Establishes a useful equivalence: the Fréchet estimator is the L2 projection of pointwise local-polynomial regressions onto the cone of monotone quantile functions, enabling inference by piggybacking on Euclidean asymptotics.
Experimental rigor and validation
Simulation evidence suggests the proposed estimators perform well and that standard quantile-RD is biased/inconsistent in this setting, reinforcing the need for the new framework.
Provides a real application (close elections) with policy-relevant findings on the equality-efficiency trade-off.
Develops a multiplier bootstrap for uniform confidence bands and a data-driven, integrated MSE bandwidth selector for the entire quantile curve.
Clarity of presentation
Clearly contrasts the randomness “across units” vs “within units” and the distinction between observed quantile discontinuities and continuity in conditional averages.
Intuitive figures and examples clarify the identification condition and the geometric meaning of the average distribution.
Sensible discussion situating the work relative to quantile RD and Fréchet regression literatures.
Significance of contributions
Addresses a highly prevalent empirical situation where policy assignment is at a coarser level than the outcome of interest, with direct implications for many existing and future RD applications.
Provides the first uniform inference results for local Wasserstein-Fréchet regression to my knowledge, which is of independent methodological interest beyond RD.
The R package promises practical uptake and reproducibility.
Weaknesses
Technical limitations or concerns
The inference strategy relies on “smoothness” of the L2 projection onto the cone of monotone functions; projection operators on convex cones are nonexpansive but not generally differentiable at boundary points. Clear conditions (e.g., strict monotonicity/no mass points in the average quantile) under which Hadamard differentiability holds and uniform inference is valid should be spelled out.
Uniform bands over q typically require trimming away from 0 and 1 and density conditions (bounded away from zero/infinity) for quantile processes. The current exposition allows q∈[0,1]; the precise domain and tail conditions should be clarified.
The treatment of within-group sampling (empirical cdfs/quantiles) is deferred to a later section; asymptotic regimes (e.g., n→∞ with m_i→∞, relative rates, heteroskedastic m_i) and their implications for bandwidth, bias, and variance require more explicit statement.
For fuzzy RD, ratio-type estimands in distribution space raise nontrivial issues (e.g., delta-method in function space); the regularity conditions, influence functions, and bootstrap validity warrant more detail.
Experimental gaps or methodological issues
Simulations appear favorable but the range of DGPs is unclear: performance under heavy tails, multimodality, mass points, skewness, and heteroskedastic within-group sample sizes should be investigated.
Sensitivity analyses for bandwidth choice and quantile grid resolution (for the pointwise approach) would strengthen the empirical guidance.
Comparisons to alternative distributional estimators (e.g., smoothing a vector of several quantiles jointly with shape constraints, or Wasserstein barycentric smoothing without local-polynomial bias correction) would be informative.
Clarity or presentation issues
The “mild continuity” assumption should be formalized precisely (domain of x, uniformity over q, and measurability in the space of random distributions).
Notation is at times dense: collecting assumptions (including those for within-group sampling and fuzzy RD) in a single, self-contained section would aid readers.
It would help to more explicitly connect the LAQTE to the Wasserstein barycenter identity in one dimension (i.e., average of quantiles equals barycenter quantile), including uniqueness conditions.
Missing related work or comparisons
While the paper covers key literatures, a brief contrast with distributional RD approaches based on RIF-regression or other scalarizations of distributional effects would help clarify when R3D offers decisive advantages.
Further discussion of shape-constrained regression and rearrangement-based inference pitfalls (e.g., boundary points) could better situate the projection-based inference step.
Detailed Comments
Technical soundness evaluation
The identification argument—continuity of the conditional expectation of quantile functions in x—is a natural analog of mean continuity in classical RD and is appropriate for random distributions. The distinction from quantile-RD’s stronger continuity assumptions is well-argued.
The estimation via local Fréchet regression in W2 is elegant and appropriate: in one dimension, barycenter quantiles equal the average quantiles, aligning with the proposed LAQTE. The projection link to pointwise local-polynomial fits is powerful for inference.
However, the projection operator to the cone of nondecreasing functions is not everywhere smooth; to transfer Gaussian limits to the projected process and get valid uniform bands, the paper should explicitly assume conditions guaranteeing interiority or strict monotonicity (e.g., densities bounded away from zero on [ε,1−ε]). Otherwise, nondifferentiability might induce nonstandard limits akin to isotonic problems.
The uniformity over q likely requires restricting to compact subsets [ε,1−ε]. If the results cover the full [0,1], the density/regularity conditions must be strong and should be articulated.
The extension to empirical quantile functions adds a second sampling layer. Clear asymptotics (n→∞, min m_i→∞, possible heterogeneity in m_i, and their interactions with the bandwidth h_n) are needed. If m_i is bounded for many groups, bias/variance inflation and potential inconsistency should be discussed.
For fuzzy RD, ratio estimators in function space require careful application of the functional delta method. Please state the conditions ensuring joint convergence of numerator/denominator processes, the nonvanishing jump in the first stage, and bootstrap validity.
Experimental evaluation assessment
The simulation study is a good start but should report: (i) coverage of uniform bands across multiple DGPs (including mass points, heavy tails, multimodality), (ii) sensitivity to tail behavior and to trimming choices, (iii) robustness to imbalanced and variable within-group sample sizes, and (iv) performance under mild violations of the average-quantile continuity.
Include comparisons to alternative pragmatic estimators: (a) smoothing a low-dimensional vector of quantiles jointly with rearrangement; (b) local-polynomial smoothing of Wasserstein distances or barycentric coordinates; (c) cluster-RD with averaged outcomes as a baseline (to illustrate information loss and cross-check conclusions).
Provide ablation on bandwidth selection (e.g., plug-in vs cross-validation vs IMSE selector) and its effect on bias/variance and coverage, especially near the cutoff.
Comparison with related work (using the summaries provided)
Relative to quantile RD (Frandsen et al., 2012; Chiang et al., 2019; Qu and Yoon, 2019), the paper convincingly argues that those approaches target a different estimand and impose stronger continuity assumptions unsuited for random distributions across aggregates.
Compared with the extensive RD literature on heterogeneity and multiscore/boundary designs (e.g., Cattaneo et al.; the reviewed network/interference RDD and boundary designs), this contribution is orthogonal and complementary: it changes the outcome space rather than the score space.
Within Fréchet/Wasserstein regression, prior work has focused on global models and, for local models, on pointwise inference; this paper’s uniform inference for local Fréchet regression is novel and valuable.
Discussion of broader impact and significance
Empirically, many published RD applications aggregate or disaggregate relative to the treatment assignment; a principled framework that respects the two-level randomness is timely and will likely change practice in applied work.
The LAQTE concept yields interpretable distributional effects at the cutoff and connects naturally to the barycenter, allowing practitioners to report “average distributional shifts” with rigorous uncertainty quantification.
The application to gubernatorial elections is compelling. To bolster credibility, standard RD validity checks (McCrary density test, covariate balance, bandwidth sensitivity, donut RD, placebo cutoffs) should be reported, and attention to income measurement (weights, top-coding, equivalence scales, price adjustments) is important given distributional outcomes.
Questions for Authors
What precise regularity conditions ensure the projection from the pointwise local-polynomial process onto the quantile cone is Hadamard differentiable, enabling uniform Gaussian limits? Do you require strict monotonicity (densities bounded away from zero) on a trimmed set [ε,1−ε]?
How do your asymptotics treat within-group sampling? What assumptions on m_i (bounded vs diverging), their heterogeneity, and their growth rates relative to n and bandwidth h are needed for consistency and valid inference?
For the fuzzy RD extension, what is the exact functional ratio estimand, and how do you establish asymptotic linearity and bootstrap validity? Please provide influence function expressions and the assumptions ensuring a nondegenerate first stage uniformly over q.
Does the uniform inference cover q∈[0,1] or a trimmed interval? How sensitive are coverage and bias to tail behavior, mass points, and top-coding? Could you provide recommended practice (e.g., trimming and diagnostics)?
In simulations, can you add DGPs with heavy tails, multimodality, and quantile plateaus to assess robustness? Also, please report sensitivity to bandwidth choices and the quantile grid resolution in the pointwise estimator.
In the empirical application, how are state income distributions constructed (data source, equivalence scales, inflation adjustment, treatment of top-coding, use of survey weights)? Are results robust to weighting states by population (size-weighted barycenters)?
Please report standard RD diagnostics (McCrary test, covariate balance around the cutoff, placebo margins, donut RD) for the close-election design, and provide bandwidth sensitivity analyses for the distribution-valued estimator.
Could you elaborate on computational complexity and numerical stability (e.g., grid sizes, solving the projection, runtime with large numbers of groups and within-group observations), and any heuristics included in the R package?
Overall Assessment
This paper tackles an important and prevalent empirical problem—RD with distribution-valued outcomes—by developing a coherent identification strategy, an estimator that respects the geometry of distributions, and a practically useful inference framework. The conceptual advance (LAQTE as a Wasserstein-average quantile) and the methodological bridge (projection of local-polynomial fits enabling uniform inference) are both novel and potentially field-shaping. The simulation and empirical components are promising, and the provision of software will facilitate adoption.

That said, several technical elements should be clarified and strengthened before publication in Econometrica: conditions ensuring the smoothness/regularity of the projection for uniform inference, a more explicit treatment of within-group sampling asymptotics, sharper statements for the fuzzy RD extension, and broader simulation/evidence on robustness (tails, mass points, bandwidth sensitivity). The empirical application would also benefit from standard RD diagnostics and richer robustness checks given the ambitious distributional conclusions.

Overall, I view this as a strong and original contribution that is suitable for Econometrica after revisions addressing the technical regularity conditions and empirical robustness. I recommend a revise-and-resubmit with the above clarifications and additions.