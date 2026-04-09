# Inference in molecular population genetics

**Date**: 03/06/2026
**Domain**: statistics/computational_statistics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Reliability of Uncertainty Quantification**

Reviewers note that the finiteness of the variance of importance weights is unproven for general mutation models, which limits the reliability of reported standard errors. Readers might note that the standard error can severely underestimate the true uncertainty if the weight distribution is heavy-tailed. It would be helpful to establish conditions under which the variance is finite or provide empirical evidence that it remains bounded in practice. Additionally, incorporating extreme value theory diagnostics and reporting the effective sample size would provide a more robust measure of estimator reliability.

**Sensitivity to Driving Value Selection**

The methodology relies on a single driving value theta_0 for the proposal distribution, which may lead to underestimation of the likelihood surface away from this value. It would be helpful to integrate the suggestion to combine estimates from multiple driving values using bridge sampling. This would ensure the likelihood surface is accurately estimated across the entire parameter range of interest without artificial peaks.

**Robustness to Model Misspecification**

The methodology assumes constant population size and selective neutrality, which are strong assumptions for real genetic data. It would be helpful to include a simulation study where the true demographic history differs from the model used for inference. This would clarify the practical utility of the method for real-world data where these assumptions are often violated.

**Theoretical Justification for Approximations**

The extension to the infinite sites model and the approximation of conditional probabilities lack rigorous theoretical justification for general mutation models. It would be helpful to provide a formal derivation for the uncountable case or analyze how efficiency gains hold as the mutation matrix deviates from the parent-independent case. This would ensure the mathematical consistency of the method across different mutation models.

**Fairness of Comparative Analysis**

The comparisons with MCMC methods vary in computational budgets and tuning parameters, potentially favoring the importance sampling method. Readers might note that the conclusion that IS is superior in constrained settings depends heavily on the specific MCMC proposal distributions used. It would be helpful to standardize CPU time or iteration counts across all methods to provide a clearer picture of relative efficiency gains.

**Computational Scalability and Approximation Error**

Appendix A describes an approximation for calculating pi_hat using Gaussian quadrature to handle large type spaces like sequence data. It would be helpful to investigate how the approximation error scales with sequence length and whether this impacts the validity of the likelihood surface estimation for modern genomic data. This is crucial given the paper's focus on modern population genetics data in the abstract.

**Potential Population Structure in NSE Data Set**

The formal model assumes a single randomly mating population of constant size (Section 2). However, the NSE data set analyzed in Section 5.4 consists of 60 males from three distinct geographic populations (Nigeria, Sardinia, and East Anglia). It is not clear how the violation of the single-population assumption affects the likelihood estimates presented in Fig. 5, particularly given that population structure can bias estimates of theta. The authors acknowledge extensions for structured populations in Section 6.2 but do not apply them to this specific dataset.

**Stationarity Assumption vs. Human Demographic History**

The inference framework assumes the sample is taken from a population at stationarity (Section 2). The NSE data comes from human populations, which are often characterized by non-equilibrium demographic histories such as expansions (mentioned in Section 6.5). It would be helpful to discuss the robustness of the likelihood surface estimates to violations of the stationarity assumption, as demographic expansions can significantly alter the distribution of genealogies and mutation patterns.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Mutation Rate Description vs Table 1

**Status**: [Pending]

**Quote**:
>  each sequence position /C40.\_so E  f 1, 2 g 10 ). Mutations were assumed to occur at total rate = 2, with the location of each mutation being chosen independently and uniformly along the sequence. The transitio

**Feedback**:
The text states mutations occur at total rate 2, but Table 1 presents results for theta = 2.0, 10.0, 15.0. It would be helpful to clarify that the initial description refers to the general model structure or specify that multiple rates were used from the outset to align with the results presented in Table 1.

---

### 2. Type Space Notation Inconsistency

**Status**: [Pending]

**Quote**:
> ion near 10 repeats and truncating the type space E to f 0, 1, . . ., 19 g 

**Feedback**:
The type space is defined as E = {0, 1, ..., 19} for the simulated data, but later for the NSE dataset it states 'E = {0, 1, ..., 19}^5'. Readers might note this notation change is not explicitly explained - the first is a single locus with 20 possible allele lengths, while the second represents 5 independent loci. It would be helpful to clarify this distinction when introducing the NSE dataset analysis.

---

### 3. Rooted Gene Trees Count

**Status**: [Pending]

**Quote**:
> ach possible rooted gene tree. /C40.\_There are S  1 such rooted gene trees, where S is the number of mutations in the data.) We

**Feedback**:
Readers might note that the number of possible roots in an unrooted gene tree is typically determined by the number of edges, which for a sample of size n is 2n-3. The claim that there are S+1 rooted gene trees implies the count depends only on the number of mutations S, not the sample size n. It would be helpful to clarify the derivation or definition of 'rooted gene trees' used here to ensure consistency with standard coalescent theory.

---

### 4. Markov Structure Terminology

**Status**: [Pending]

**Quote**:
> In the case of a varying population size, the simple Markov structure of the underlying processes is lost

**Feedback**:
The coalescent process with varying population size N(t) remains a Markov process, specifically a time-inhomogeneous one where the coalescence rate at time t is binom(k,2)/N(t). While the time-homogeneity is lost, the Markov property itself is preserved. It would be helpful to clarify that the time-homogeneous structure is what is lost, as this distinction affects how proposal distributions Q(H) are constructed to account for time-dependent rates.

---

### 5. Naive Estimator Weights Boundedness

**Status**: [Pending]

**Quote**:
> ories is ®nite. /C40.\_In contrast the naõÈ ve estimator /C40.\_5) is guaranteed to have a ®nite /C40.\_though usually huge) variance, as the weights are bounded. 

**Feedback**:
The claim that the weights are bounded requires the proposal density to dominate the target density everywhere, which is not guaranteed for all naive choices. It is not clear how the boundedness follows from the definition of the naive estimator in Equation 5 without further specification of the proposal. It would be helpful to explicitly state the proposal distribution used to validate this guarantee.

---

### 6. Complex Settings Contradiction

**Status**: [Pending]

**Quote**:
> methods described in the paper are becoming routinely used by biologists for much larger data sets, and in some more complex settings

**Feedback**:
Readers might note an apparent tension between this claim and the subsequent statement that there is an 'urgent need for the continuing development of more efficient inference methods, for their extension to more complex genetic and demographic scenarios'. If the methods are already routinely applied in complex settings, the urgency for extension is less clear. It would be helpful to clarify whether the 'complex settings' referenced here differ from the 'complex scenarios' requiring further development, or to qualify the extent of current applicability to avoid ambiguity.

---

### 7. Mutation Count Equivalence

**Status**: [Pending]

**Quote**:
> It follows from elementary properties of Poisson processes that this is equivalent to drawing a time t from an exponential distribution with rate parameter 1, and then applying mi mutations to locus i

**Feedback**:
It would be helpful to verify the mathematical equivalence between the geometric and Poisson formulations described. Under the stated parameters, the expected number of mutations in the geometric case is n/(l*theta), while in the Poisson case it is l*theta/n. These expectations are reciprocals and do not match unless n = l*theta. It would be helpful to clarify the derivation or correct the parameters to ensure the expected mutation counts align.

---

### 8. Q_GT Underestimation Magnitude

**Status**: [Pending]

**Quote**:
> mate of the likelihood using 20000 samples, the samples from Q GT  underestimate the likelihood by seven orders of magnitude. 

**Feedback**:
The claim that Q_GT underestimates the likelihood by seven orders of magnitude is specific. It would be helpful to provide the exact values from Table 1 to verify this calculation. This would allow readers to assess the severity of the underestimation and the reliability of the comparison between methods.

---

### 9. Finite Variance Proof Limitation

**Status**: [Pending]

**Quote**:
> be available, this is often not the case. For example, we could not prove ®niteness of the variance of our weights, except in the special case of the in®nite sites model where the number of possible histories is ®nite. /C40.\_In contrast the naõÈ 

**Feedback**:
The text states that finiteness of the variance of weights could not be proved except for the infinite sites model. It would be helpful to discuss the implications of this for the reliability of standard errors in other models, as heavy-tailed weights can lead to underestimation of uncertainty. This would clarify the robustness of the reported confidence intervals.

---

### 10. Micsat Accuracy Claim Evidence

**Status**: [Pending]

**Quote**:
> ined by using our method and micsat . Further investigation /C40.\_more runs of each method) suggested that the curve obtained by using micsat is more accurate.
> 
> ## 5.5. In

**Feedback**:
The text states that further investigation suggested the micsat curve is more accurate, but does not provide details of this investigation. It would be helpful to summarize the evidence or reference the specific runs that led to this conclusion to ensure transparency. This would allow readers to evaluate the validity of the comparison.

---

### 11. Unrooted Gene Tree Likelihood Estimation

**Status**: [Pending]

**Quote**:
> removing the need to specify a driving value. The likelihood for the unrooted gene tree is estimated, as in equation /C40.\_9), by the average of the importance weights.
> 
> The

**Feedback**:
Readers might note that equation (9) estimates the likelihood L(theta), but the text states it estimates the likelihood for the unrooted gene tree. It would be helpful to clarify if this refers to the marginal likelihood of the data or the probability of the tree structure, as the distinction affects the interpretation of the estimator. This would ensure the methodological description is precise.

---

### 12. Single IS Function Efficiency Claim

**Status**: [Pending]

**Quote**:
> tion Q  for each value of  . However, it appears to be more ecient to reuse samples from a single IS function. This is in

**Feedback**:
The text claims it is more efficient to reuse samples from a single IS function. It would be helpful to quantify this efficiency gain or provide a reference to the theoretical justification, as reusing samples can lead to high variance if the proposal differs substantially from the target. This would strengthen the argument for this approach.

---

### 13. PIM Exact Likelihood Formula

**Status**: [Pending]

**Quote**:
> pendent mutation
> 
> For PIM models, the conditional distributions  . j .  are known exactly /C40.\_see equation /C40.\_16) above), and hence so also is the likelihood. This class of models 

**Feedback**:
The text states that for PIM models the likelihood is known exactly. It would be helpful to specify the formula for this exact likelihood to allow readers to verify the implementation of the algorithm. This would provide a concrete benchmark for the proposed method.

---

### 14. Algorithm 1 Time Scaling

**Status**: [Pending]

**Quote**:
> nealogical tree /C40.\_see for example Fig. 1). It turns out that the natural timescale on which to view the evolution of the population is in units of N = 2 generations, where  2

**Feedback**:
Algorithm 1 describes sampling from P_theta(A). It would be helpful to clarify how this algorithm relates to the coalescent approximation mentioned earlier, specifically regarding the time scaling N/σ^2. This would ensure the connection between the discrete generation model and the continuous coalescent time scale is clear.

---

### 15. Optimal IS and Likelihood Equivalence

**Status**: [Pending]

**Quote**:
> es  . j .  . We have seen at equation /C40.\_11) that knowledge of Q *  is equivalent to knowledge of the likelihood L   . It is also easy to see that knowing t

**Feedback**:
Readers might note that the text states knowledge of Q* is equivalent to knowledge of the likelihood L(theta). It would be helpful to explicitly show the relationship between the conditional probabilities and the likelihood to clarify this equivalence. This would improve the mathematical transparency of the derivation.

---
