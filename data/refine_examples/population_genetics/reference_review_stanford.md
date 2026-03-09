Summary
The paper develops a principled and highly effective importance sampling (IS) framework for full likelihood inference in molecular population genetics under the coalescent with recurrent mutation. The key contribution is a characterization of the optimal backward-time proposal distribution in terms of conditional sampling distributions (CSDs), followed by a tractable and well-motivated approximation to those CSDs that yields a new proposal with dramatically reduced variance relative to existing schemes (notably Griffiths–Tavaré). Empirical comparisons indicate orders-of-magnitude efficiency gains over prior IS methods and nuanced performance trade-offs relative to MCMC, together with practical guidance on diagnostics.

Strengths
Technical novelty and innovation
The optimal backward-time proposal is derived explicitly in terms of conditional probabilities π(·|·), a clean and powerful theoretical result that clarifies what makes proposals “good” or “bad.”
The proposed approximation π̂(·|·) is carefully constructed, satisfies desirable properties (e.g., exact under PIM and for n=1 with reversible P), and leads directly to an implementable and efficient proposal Q^SD.
The backward-time sampling and weight computation are elegantly simplified via Proposition 2, reducing computational overhead by leveraging exchangeability and conditional factorization.
Experimental rigor and validation
The paper reports extensive empirical comparisons to the canonical Griffiths–Tavaré IS and multiple MCMC approaches across several mutation models, with clear qualitative insights into “constrained” versus “less constrained” settings.
Absolute likelihood evaluation (rather than only relative likelihoods) is emphasized for IS, which is valuable for model comparison across non-nested models.
Clarity of presentation
The genealogical modeling background is thorough and accurate, and the motivation for focusing on histories H rather than full typed ancestries A is compelling.
The mathematical development proceeds logically from model, to optimal proposal characterization, to approximation, to implementation details and diagnostics.
Significance of contributions
The approach directly addresses a central bottleneck in population-genetic inference—computing full likelihoods under realistic mutation models—providing concrete variance reduction and computational savings.
The characterization of optimal proposals and practical approximations have enduring value; subsequent literature has built on this CSD-based perspective to generalize beyond Kingman and to more complex settings.
Weaknesses
Technical limitations or concerns
The coalescent-without-recombination assumption and known mutation matrix P limit applicability; performance and bias under misspecification (unknown P, recombination, selection) are not explored.
Approximation accuracy of π̂(·|·) is argued heuristically and via special cases; a more systematic error analysis (e.g., dependence on θ, spectrum of P, sample size, and allele space size) would strengthen confidence.
Experimental gaps or methodological issues
While the abstract claims large efficiency gains, more granular diagnostics (ESS, weight variance across steps, distribution of maximum weights) and ablation studies (components of π̂) would aid reproducibility and benchmarking.
Comparisons to adaptive/resampling-based sequential Monte Carlo variants are not discussed; in some regimes resampling could help or hurt (later theory suggests this depends on the mutation model).
Clarity or presentation issues
Some steps in proofs (e.g., normalization constants, independence arguments in the particle representation) could benefit from more explicit derivations to aid non-expert readers.
A concise, self-contained algorithmic pseudo-code for the full IS pipeline (including precomputation of M^(n), weight calculation, and likelihood-surface reuse across θ) would improve accessibility.
Missing related work or comparisons
At the time, coverage of MCMC alternatives is reasonable; however, readers would benefit from a brief discussion of product-of-approximate-conditionals (PAC) estimators and how/why they differ in bias/variance trade-offs.
No discussion of extension paths to recombination or multifurcations; later works (e.g., Rasmussen et al. on ARG/HMM threading; Koskela et al. on Λ/Ξ-coalescents) show the portability of the CSD viewpoint—highlighting such pathways would enhance impact.
Detailed Comments
Technical soundness evaluation
Theorem 1 is fundamental: it ties the optimal proposal to CSD ratios and clarifies why GT proposals can wander into low-probability regions. This backward characterization remains a cornerstone in later generalizations.
The π̂ construction via a geometric number of mutations from a uniformly sampled lineage is intuitive, computationally tractable, and exact under PIM; properties (a)–(e) establish internal coherence and computational convenience.
The lookdown/particle representation is aptly leveraged for backward-rate derivations; the argument that C is n(n−1+θ)/2 is correct and crucial for proper normalization.
A theoretical variance analysis would be valuable. Later asymptotics (Favero & Koskela 2024) suggest weight variance concentrates in late steps for finite-alleles models, offering a lens for explaining the observed efficiency and for proposing adaptive effort allocation; connecting to such principles would future-proof the methodology.
Experimental evaluation assessment
The stated comparisons across mutation models (finite-alleles, possibly infinite-sites) and to MCMC are appropriate; to fully assess claims, one hopes for:
Detailed CPU-time normalized ESS comparisons, variance of log-likelihood estimates, and confidence intervals on MLEs.
Sensitivity to θ, allele-space size, and sample size n, including transition regimes from “constrained” to “less constrained” types.
Robustness checks under parent-dependent versus parent-independent P, and under stationary versus skewed stationary distributions.
Diagnostics: the discussion of IS-specific diagnostics is welcome; in addition to weight histograms and ESS-by-step, reporting the per-step contribution to variance would align with later insights and guide targeted variance reduction.
Comparison with related work (using the summaries provided)
The CSD-based optimal-proposal philosophy here anticipates later generalizations to Λ- and Ξ-coalescents (Koskela et al. 2013), which show similar advantages when proposals are matched to the true backward generator; your framework could explicitly note the pathway to non-Kingman settings.
The recent asymptotic analysis of backward IS under finite-alleles (Favero & Koskela 2024) provides theoretical backing that most variance accrues late, suggesting practical heuristics (e.g., non-uniform particle allocation, delayed resampling). Your diagnostics and practical guidance could be reframed in light of this.
For recombination, ARGweaver (Rasmussen et al. 2013) demonstrates HMM-based threading for genome-wide ARG inference; your CSD approach might inform proposal design for local genealogies within SMC/HMM frameworks and clarify differences between joint ARG sampling and marginal-likelihood IS at a locus.
Modern amortized proposal learning (e.g., learned inverses for SMC, 1602.06701) suggests that π̂(·|·) could be further refined by data-driven surrogates trained offline to approximate CSDs, potentially improving performance in complex, high-dimensional allele spaces.
Recent SMC advances (2506.01083) and LFI with limited simulations (2111.01555) reinforce the value of well-correlated observation paths and surrogate transition models; analogous ideas (e.g., bridging across θ, surrogate π̂ refinements) could be adapted here.
Extensions to selfing/overlapping generations and pedigree-conditional coalescents (2510.26115, 2505.15481) underscore emerging inference needs beyond the standard Kingman setting; the CSD lens remains relevant and could guide future adaptations.
Discussion of broader impact and significance
By offering absolute likelihood estimates with large efficiency gains, the method makes previously intractable full-likelihood analyses feasible, enabling principled model comparison and parameter inference from rich genomic data.
The proposal-design insights (mutational drift toward the sample, coalescences biased by conditional probabilities) provide a reusable design pattern for Monte Carlo in other high-dimensional latent-tree settings.
Clear articulation of regimes favoring IS versus MCMC helps practitioners choose tools appropriately and set expectations for diagnostics, run length, and computational cost.
Questions for Authors
Can you provide quantitative diagnostics (ESS, log-weight variance, Gini of weights) across steps to illustrate where variance accumulates, and how this differs between finite-alleles and infinite-sites models?
How sensitive is performance to the accuracy of P? If P is misspecified or estimated from data, do small errors materially affect π̂ and thus variance/bias?
Could you include ablation experiments demonstrating which properties of π̂ (e.g., geometric mutation depth, uniform initial choice, reversibility) are most critical to performance?
In high-θ regimes, where π(·|A_n) approaches the stationary distribution, does π̂ retain its advantage, or do GT-like proposals become competitive? Can you show a θ-sweep study?
Have you explored adaptive “driving values” or bridge/umbrella sampling across θ to further stabilize the likelihood surface estimates while reusing particles?
Would resampling (SMC) be beneficial or detrimental in your setting? Can you report experiments with adaptive resampling thresholds and discuss trade-offs by mutation model?
For large allele spaces E, how does runtime scale with the number of accessible neighbors per state (graph degree under P)? Are there sparsity tricks or caching strategies you recommend?
Could the π̂ matrices M^(n) be approximated spectrally (e.g., low-rank approximations of (I − λP)−1) to reduce precomputation and memory for large E? Any empirical observations?
Do your diagnostics detect under-coverage or bias in likelihood estimates in the “less constrained” regimes? If so, are there corrective strategies (e.g., mixture proposals, tempering)?
How might your approach be adapted for recombination (e.g., local genealogies in an HMM/SMC framework) or for multiple-merger coalescents, where recent literature leverages analogous CSD-based proposals?
Overall Assessment
This paper makes a seminal contribution to likelihood-based inference in population genetics by deriving an optimal backward proposal in terms of CSDs and providing a principled, effective approximation that yields substantial practical gains. The theoretical development is clean and insightful, the algorithmic design is elegant and implementable, and the empirical comparisons (as described) substantiate major efficiency improvements over prior IS and competitive performance relative to MCMC in key regimes. The work has had and will continue to have significant impact, informing later generalizations (Λ/Ξ-coalescents, recombination-aware samplers) and modern proposal-learning ideas. To further strengthen the paper, I encourage deeper variance diagnostics, sensitivity analyses (θ, P, sample size), ablations of π̂’s design choices, and a brief roadmap to extensions (recombination, multiple mergers). With these additions, this is strong top-tier work that sets a high standard for proposal design in coalescent-based inference.