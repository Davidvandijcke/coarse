# Inference in molecular population genetics

**Date**: 03/06/2026
**Domain**: statistics/methodology
**Taxonomy**: academic/review_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Theoretical Justification of the Sampling Approximation**

Reviewers note that the core approximation \(\hat{\pi}(\cdot|A_n)\) lacks theoretical error bounds for general mutation matrices when \(n > 1\). Additionally, the extension to the infinite sites model is described as being done 'by analogy' despite the lack of reversibility, which questions the theoretical foundation of the optimality claims. It would be helpful to provide a formal derivation or error analysis for non-reversible cases to ensure the efficiency gains are not compromised by theoretical inconsistencies.

**Reliability of Variance Estimation and Uncertainty Quantification**

Multiple reviewers highlight that standard error estimates for likelihoods can severely underestimate true uncertainty due to the high skewness of importance weights, with some cases suggesting potentially infinite variance. Readers might note that without a validated method to correct for this underestimation, practitioners could be misled into believing their likelihood estimates are more precise than they actually are. It would be helpful to include robust diagnostics or conservative stopping rules that account for the possibility of unstable weight distributions to prevent potential misinterpretation of precision.

**Consistency of Performance Claims Against MCMC Methods**

Although the abstract claims favorable comparison with MCMC, results on the NSE microsatellite dataset indicate the MCMC method produced a more accurate likelihood curve. This contradiction suggests the advantages of the IS approach may not hold universally across all data structures. It would be helpful to clarify the specific boundary conditions, such as dimensionality or mutation rates, under which MCMC may outperform the proposed IS method to prevent overgeneralization.

**Sensitivity to Driving Value Selection and Likelihood Surface Stability**

The methodology relies on a driving value \(\theta_0\), and efficiency drops significantly away from this point, potentially leading to artificially peaked likelihood curves. The authors acknowledge the challenge of designing a universally efficient IS function but do not provide a concrete algorithm for combining multiple runs or selecting \(\theta_0\) adaptively. It would be helpful to detail how techniques like bridge sampling could be integrated to ensure accurate estimation across the entire parameter range.

**Robustness to Model Assumptions and Real-World Data Challenges**

The current method assumes constant population size and neutrality, with limited discussion on how to incorporate demographic changes or handle ascertainment bias in SNP data. Given that real genetic data often violates these assumptions, the sensitivity of the importance weights to such misspecifications remains an unaddressed limitation. It would be helpful to conduct a sensitivity analysis or provide a worked example demonstrating adjustments for these common biological complexities.

**Consistency of Single-Population Assumption with Multi-Population Data**

Section 3 defines the demographic model for a random sample of n chromosomes taken from a single population at stationarity. However, Section 5.4 applies this method to the NSE dataset, which consists of 60 males from Nigeria, Sardinia, and East Anglia. It is not clear how the single-population assumption holds when the sample is drawn from distinct geographic groups with potentially different demographic histories. It would be helpful to clarify whether the analysis treats these as a single pooled population or if the method accounts for structure, as pooling can bias parameter estimates like theta.

**Validity of Truncated Type Space for Microsatellite Data**

Section 5.4 describes implementing the IS scheme by truncating the type space E to {0, 1, ..., 19} to facilitate computation. While the text notes this makes little difference if allele lengths are not close to these boundaries, it does not explicitly verify the range of the NSE data alleles. It is not clear how the likelihood calculation is affected if observed alleles fall outside this truncated space. It would be helpful to report the observed allele range to confirm the approximation is valid for this specific dataset.

**Applicability of Stationarity Assumption to Human Demographic Data**

The formal model assumes the population is at stationarity (Section 3). However, human populations often experience expansions or bottlenecks, which are acknowledged as extensions in Section 6.2. It is not clear how robust the inference for theta is when applied to the NSE data, which may not satisfy the strict stationarity condition. It would be helpful to discuss potential biases arising from demographic history violations in this context, particularly given the known complexity of human demographic history.

**Status**: [Pending]

---

## Detailed Comments (17)

### 1. Notation Ambiguity in Equation (1) Variable Definition

**Status**: [Pending]

**Quote**:
> where $n$ is the number of chromosomes in $H_{i-1}$ and $n_{\alpha}$ is the number of chromosomes of type $\alpha$ in $H_{i-1}$.

**Feedback**:
Readers might note that the symbol $n$ is previously defined as the fixed sample size in 'a random sample of $n$ chromosomes'. Reusing $n$ for the variable number of lines in Equation (1) creates ambiguity regarding whether the denominator refers to the fixed sample size or the current number of lines. It would be helpful to distinguish these quantities to ensure the probability formula is interpreted correctly.

---

### 2. Transition Probability Validity for MRCA State in Algorithm

**Status**: [Pending]

**Quote**:
> It follows from algorithm 1 that the distribution $P_{\theta}(\mathcal{H})$ is defined by the distribution $\psi(\cdot)$ of the type of the MRCA, the stopping procedure (step 3 of the algorithm) and the Markov transition probabilities

**Feedback**:
It is not clear how Equation (1) applies to the transition from the MRCA state. If $H_{i-1}$ corresponds to the MRCA with 1 chromosome, the split probability term $\frac{n-1}{n-1+\theta}$ becomes zero, yet Algorithm 1 Step 1 requires an immediate split from the single line. It would be helpful to clarify the range of validity for the transition probabilities.

---

### 3. Inconsistency in Markov Chain Dependency Description

**Status**: [Pending]

**Quote**:
> Naïve application of this method to estimate the likelihood function $L(\cdot)$ requires simulation from a different Markov chain for each value of $\theta$.

**Feedback**:
The text states that the method described in Equation (6) requires a different Markov chain for each value of $\theta$ in a 'naïve application'. However, Equation (6) is attributed to Griffiths and Tavaré (1994a), who are specifically known for developing an importance sampling scheme that uses a single proposal chain independent of $\theta$. The subsequent sentence acknowledges this single-chain capability, creating a logical inconsistency in the description of the method's properties. It would be helpful to clarify that the 'naïve' approach refers to simulating the true genealogical process, while the GT method uses a fixed proposal.

---

### 4. Notation inconsistency in Theorem 1 proof

**Status**: [Pending]

**Quote**:
> = \frac {P \left\{\Upsilon_ {\mathrm {m}} \cap A _ {k} (t - \delta) = \left(\alpha_ {1} , \dots , \alpha_ {k - 1} , \beta\right) \cap A _ {k} (t) = \left(\alpha_ {1} , \dots , \alpha_ {k - 1} , \alpha\right) \right\}}{P \left\{A _ {k} (t) = \left(\alpha_ {1} , \dots , \alpha_ {k - 1} , \alpha\right) \right\}} \\ \end{array}
> $$
> 
> <!-- PAGE BREAK -->
> 
> 614 M. Stephens and P. Donnelly
> 
> $$
> \begin{array}{l}
> = \frac {\pi \left(\alpha_ {1} , \dots , \alpha_ {n - 1} , \beta\right) \delta \theta P _ {\beta \alpha} / 2}{\pi \left(\alpha_ {1} , \dots , \alpha_ {n - 1} , \alpha\right)} + o (\delta) \\
> = \delta \frac {\theta}{2} \frac {\pi (\beta | A _ {k} - \alpha)}{\pi (\alpha | A _ {k} - \alpha)} P _ {\beta \alpha} + o (\delta).
> \end{array}
> $$
> 
> By exchangeability this result holds for every line of type $\alpha$, and so

**Feedback**:
In the proof of Theorem 1, the text introduces $k$ as the number of lineages at time $t$ ('Suppose that at time $t$ the ancestry consists of $k$ lineages'). However, the first line of the displayed equation uses $n-1$ to denote the number of other lineages ($\alpha_{n-1}$), while the second line correctly uses $A_k - \alpha$. This creates a notation inconsistency where $n$ and $k$ are used interchangeably for the current number of lineages in the proof, although $n$ is defined in the theorem statement as the initial sample size. It would be helpful to maintain consistent notation throughout the proof to avoid confusion.

---

### 5. Statistical terminology regarding standard errors and weights

**Status**: [Pending]

**Quote**:
> suggesting that the standard errors in the smaller sample are accurately reflecting the standard deviation of the weights

**Feedback**:
The standard error of an estimator is defined as the standard deviation of the sampling distribution, which equals the standard deviation of the weights divided by the square root of the sample size. Stating that the standard error reflects the standard deviation of the weights directly may be misleading, as it ignores the sample size scaling factor. The observation that the standard error reduced by the expected factor of $\sqrt{1000}$ confirms the finite variance of the weights, but the phrasing conflates the estimator's precision with the weight distribution's spread. It would be helpful to clarify that the scaling behavior confirms the stability of the weight distribution rather than equating the two quantities.

---

### 6. Ambiguous Sample Size Description in Figure 3 Caption

**Status**: [Pending]

**Quote**:
> likelihood surface estimates obtained from the combined samples of size 50000 from $Q_{\theta_0=10.0}^{\mathrm{GT}}$ (---) and $Q_{\theta_0=10.0}^{\mathrm{SD}}$ (......... , which is almost superimposed on ———)

**Feedback**:
The caption states 'combined samples of size 50000 from $Q_{\theta_0=10.0}^{\mathrm{GT}}$ (---) and $Q_{\theta_0=10.0}^{\mathrm{SD}}$'. This phrasing is ambiguous: it is unclear whether the 50,000 samples are split between the two distributions (e.g., 25,000 each) or if 50,000 samples were drawn from each. Given the text earlier states '50000 samples [of GT] are also insufficient', it implies the GT estimate uses 50,000 samples. However, the caption lists both GT and SD with different line styles, suggesting two separate estimates. If the 50,000 applies to the total combined samples, the individual sample sizes are undefined. If it applies to each, the word 'combined' is misleading. Readers might note that this ambiguity affects the interpretation of computational efficiency comparisons.

---

### 7. Inconsistent notation for driving value

**Status**: [Pending]

**Quote**:
> ed curves in Fig. 2(c) for example). In principle IS methods based on a driving value of $\theta$ will tend to share this undesirable property, as designi

**Feedback**:
The text previously defines the fixed parameter value as $\theta_0$ (e.g., 'fix $\theta$ at a 'driving value' $\theta_{0}$'). Using 'driving value of $\theta$' here conflates the parameter $\theta$ with the specific value $\theta_0$. This creates ambiguity about whether $\theta$ is the variable or the fixed value. I initially expected consistent notation for the driving value throughout the discussion of IS methods. This is a notation inconsistency that could confuse readers about the parameter definitions.

---

### 8. Inconsistent Summation Index in IS Weights

**Status**: [Pending]

**Quote**:
> $w_{i}/\Sigma_{i}w_{j}$

**Feedback**:
Readers might note that the summation index in the denominator is inconsistent with the term being summed. The expression uses $w_{j}$ inside the sum, but the subscript on the summation symbol is $i$, which typically implies summation over $i$. Standard IS notation requires the denominator to sum over the same index as the weights, usually $\sum_{j}w_{j}$. This notation error could confuse readers about the normalization of the weights. It would be helpful to correct the index to match the weight variable.

---

### 9. Peeling Algorithm Does Not Require Importance Sampling

**Status**: [Pending]

**Quote**:
> which could be calculated by the peeling algorithm (to do this it would be necessary to apply IS to the full typed ancestry $\mathcal{A}$ of the sample).

**Feedback**:
It is not clear how the peeling algorithm requires Importance Sampling, as the algorithm is designed to calculate likelihoods exactly by summing over ancestral states. The peeling algorithm (Felsenstein's pruning algorithm) marginalizes over mutations on invariant sites deterministically without needing to sample them via IS. The parenthetical statement appears to suggest that IS is a prerequisite for using the peeling algorithm, which contradicts standard phylogenetic likelihood methods. It would be helpful to clarify that the peeling algorithm computes the factor exactly.

---

### 10. Ambiguity in finite histories claim for ISM

**Status**: [Pending]

**Quote**:
> except in the special case of the infinite sites model where the number of possible histories is finite.

**Feedback**:
Readers might note that in the standard continuous-time Kingman coalescent, the space of genealogies is uncountably infinite due to continuous branch lengths, even under the infinite sites model. It is not clear how the number of possible histories is finite without a specific definition of 'history' that discretizes the state space (e.g., ignoring branch lengths or using a discrete-time approximation). This claim is critical for the argument that variance is finite in this case. It would be helpful to clarify the definition of 'history' used or acknowledge the continuous nature of the standard coalescent to avoid mathematical inconsistency.

---

### 11. Duplicate introductory paragraph

**Status**: [Pending]

**Quote**:
> symptotic properties of the likelihood for genetics models would also be valuable.
> 
> # Acknowledgements
> 
> We thank all the discussants for their interesting comments. For brevity, our response will focus on several common themes raised.
> 
> We thank all the discussants for their interesting comments. For brevity, our response will focus on several common themes raised.
> 
> Several discussants (Mau, Me

**Feedback**:
The introductory paragraph is repeated verbatim at the beginning of the section. This repetition appears to be an editing oversight that reduces the professionalism of the text. Readers might note that the second instance adds no new information. It would be helpful to remove the duplicate to streamline the opening.

---

### 12. Inconsistency between Geometric and Poisson mutation parameters

**Status**: [Pending]

**Quote**:
> A_n$ uniformly at random, and then applying $m$ mutations to this chromosome (each of which involves choosing a locus uniformly and changing the type at that locus according to $P$), where $m$ is geometrically distributed with parameter $l\theta/(n+l\theta)$. It follows from elementary properties of Poisson processes that this is equivalent to drawing a time $t$ from an exponential distribution with rate parameter 1, and then applying $m_i$ mutations to locus $i$ ($i=1, \dots, l$), where the $m_i$ are independent and Poisson distributed with mean $\theta t/n$, and the mutations at each locus are governed by transition matrix $P$. Thus, writing types as $\alpha = (\alpha_1, 

**Feedback**:
Readers might note a discrepancy between the stated geometric parameter and the Poisson mixture derivation. If $t \sim \text{Exp}(1)$ and $m_i \sim \text{Poisson}(\theta t/n)$, the marginal distribution of total mutations $m$ is geometric with success probability $n/(n+l\theta)$, not $l\theta/(n+l\theta)$. This inconsistency could lead to sampling discrepancies in the proposal distribution. It would be helpful to rewrite the geometric parameter to $n/(n+l\theta)$ to match the Poisson derivation provided in the same paragraph.

---

### 13. Ambiguity in quadrature method for infinite integral

**Status**: [Pending]

**Quote**:
> The integral in equation (31) may be approximated by using Gaussian quadrature (see for example Evans (1993)):

**Feedback**:
It would be helpful to specify the type of quadrature used for the semi-infinite integral with exponential weight. Standard Gaussian quadrature typically refers to Gauss-Legendre on a finite interval, whereas Gauss-Laguerre is required for integrals of the form $\int_0^\infty e^{-t} f(t) dt$. Using the wrong quadrature rule would result in numerical discrepancies. It would be helpful to rewrite 'Gaussian quadrature' as 'Gauss-Laguerre quadrature' to ensure the implementation matches the integral's domain and weight function.

---

### 14. Coalescence coefficient in Equation (34)

**Status**: [Pending]

**Quote**:
> $$ p(\mathbf{n}) = \frac{\theta}{n + \theta - 1} \left\{ \sum_{\alpha = 1}^d \sum_{\beta = 1}^d \frac{n_{\beta} + 1 - \delta_{\alpha \beta}}{n} P_{\beta \alpha} p(\mathbf{n} + e_{\beta} - e_{\alpha}) \right\} + \frac{n - 1}{n + \theta - 1} \sum_{\{\alpha : n_{\alpha} > 0\}} \frac{n_{\alpha} - 1}{n - 1} p(\mathbf{n} - e_{\alpha}). \tag{34} $$

**Feedback**:
Readers might note that the coalescence term coefficient $\frac{n_{\alpha} - 1}{n - 1}$ differs from the standard Kingman coalescent probability of selecting a pair of type $\alpha$. In the standard coalescent, the probability of picking a specific pair of type $\alpha$ out of all $\binom{n}{2}$ pairs is $\frac{\binom{n_{\alpha}}{2}}{\binom{n}{2}} = \frac{n_{\alpha}(n_{\alpha} - 1)}{n(n - 1)}$. The text's coefficient is missing the factor $n_{\alpha}/n$, which would be required to correctly weight the coalescence events by the number of available pairs of that type. It would be helpful to rewrite the coalescence term in Equation (34) as $\frac{n - 1}{n + \theta - 1} \sum_{\{\alpha : n_{\alpha} > 0\}} \frac{n_{\alpha}(n_{\alpha} - 1)}{n(n - 1)} p(\mathbf{n} - e_{\alpha})$ to align with standard coalescent theory.

---

### 15. Consistency of Performance Claims Against MCMC Methods

**Status**: [Pending]

**Quote**:
> The new method also compares favourably with existing MCMC methods in some problems, and less favourably in others, suggesting that both IS and MCMC methods have a continuing role to play in this area.

**Feedback**:
Although the abstract claims favorable comparison with MCMC, results on the NSE microsatellite dataset indicate the MCMC method produced a more accurate likelihood curve. This contradiction suggests the advantages of the IS approach may not hold universally across all data structures. It would be helpful to clarify the specific boundary conditions, such as dimensionality or mutation rates, under which MCMC may outperform the proposed IS method to prevent overgeneralization.

---

### 16. Ambiguity in Griffiths-Tavaré Method Description

**Status**: [Pending]

**Quote**:
> ere $\mathcal{H}^{(1)},\dots ,\mathcal{H}^{(M)}$ are independent samples from $Q_{\theta_0}(\cdot)$. This approach is due to Griffiths and Tavaré (1994a), which refers to $\theta_0$ as the 'driving value' of $\theta$.
> 
> <!-- PAGE BREAK -->
> 
> Molecular Popul

**Feedback**:
The text describes the method as sampling from a fixed proposal $Q_{\theta_0}$ independent of the data. However, the standard Griffiths-Tavaré (1994a) algorithm constructs a proposal distribution that explicitly depends on the data $A_n$ (e.g., conditional on the current sample configuration). It is not clear how the fixed $Q_{\theta_0}$ formulation in Equation (12) aligns with the data-dependent proposal typically associated with this method. It would be helpful to add a sentence after Equation (12) clarifying whether $Q_{\theta_0}$ implicitly conditions on $A_n$ or if this is a simplified representation to ensure accuracy.

---

### 17. Sentence interrupted by figure caption

**Status**: [Pending]

**Quote**:
> The discontinuities are striking and evidence that

**Feedback**:
The sentence beginning with 'The discontinuities are striking' is split by a page break and figure caption, leaving it grammatically incomplete in the text flow. The continuation 'insufficient iterations have been performed...' appears after the caption. This disrupts the reading flow. It would be helpful to ensure the sentence is not broken by the figure placement in the final layout.

---
