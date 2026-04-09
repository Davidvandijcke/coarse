# 3 Mean-Field Equations for Population Rates

**Date**: 03/16/2026
**Domain**: natural_sciences/neuroscience
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper develops a mean-field theory for sparsely connected binary neural networks to characterize balanced-state statistics, temporal correlations, and stability/response properties. Using a Gaussian/moment-closure approximation for the summed inputs, the authors derive self-consistent equations for means, variances, autocorrelations, and finite‑K corrections, and they analyze local/global stability and sensitivity (including claims about Lyapunov behavior). The main claimed results are analytic formulae for firing-rate moments and autocorrelations, finite‑K corrections that preserve linear response properties, thresholds delimiting stability regimes, and a strong sensitivity statement for the balanced state. Reviewers find the approach promising but identify several technical and validation gaps that affect the paper's core conclusions and their biological interpretation.

Below are the most important issues identified by the review panel.

**Unclear order of limits and unjustified Gaussian / moment-closure**

Readers might note a logical tension between the Gaussian moment-closure used throughout the main text and the rigorous condition cited in Appendix A (activity independence holding only when K ≪ log N). The paper often phrases the closure as ‘‘exact in the large K limit’’ and elsewhere takes N → ∞ then K → ∞, which is incompatible with the K ≪ log N regime used to justify independence. It would be helpful to state explicitly the order-of-limits and the precise scaling assumptions linking K and N (for example K = o(log N) or an alternative regime), correct the citation/statement in Appendix A, and present a controlled cumulant expansion (Edgeworth or similar) in the Appendix that writes the leading non‑Gaussian corrections (third/fourth cumulants) and bounds their magnitude as functions of K and N. Concretely, add the derivation/bounds for leading cumulants, state when they can be neglected for the K,N ranges used in figures, and provide a small set of numerical diagnostics (QQ‑plots, skewness/kurtosis, tail error metrics) from full network simulations to validate the Gaussian approximation in the biologically relevant parameter regime.

**Finite-K corrections lack explicit error estimates and systematic validation**

It would be helpful to replace qualitative statements that finite‑K corrections are ‘‘small’’ with explicit asymptotic expansions and empirical scaling. Reviewers recommend deriving a controlled expansion for m_k, u_k and α_k in powers of 1/√K or 1/K that displays the leading error term and its dependence on m_k and θ_k, and stating precise sufficient conditions (e.g., error bounds C(K)=O(K^{-1/2})) under which the expansion holds. Complement the analysis with systematic numerical tests comparing analytic finite‑K formulae to ensemble-averaged network simulations across a range of K and N (suggested K={50,100,300,1000,3000} and representative N), report quantitative error curves (L2 or relative error) and fitted scaling exponents, and show parameter regions (in m0, θ) where the asymptotics break down. If discrepancies remain, present next‑order analytic corrections or clearly delimit the regimes where the finite‑K mean-field predictions are reliable.

**Derivation, indexing and stationarity assumptions in the autocorrelation equation are incomplete**

The self‑consistent autocorrelation kernel (eq. 5.17 and Appendix A.2) is central to claims about temporal correlations and tracking, yet the printed equation contains ambiguous/mismatched terms and the derivation omits intermediate steps and error estimates. Readers might note missing explanation for the time‑indexing of β_k(t+τ) inside nonlinearities and unquantified stationarity/ergodicity assumptions used to close temporal moments. It would be helpful to publish a corrected, fully worked derivation in Appendix A.2 (showing how time shifts enter and resolving any typographical duplication), analyze the well‑posedness and numerical stability of the integral equation (existence/uniqueness and condition numbers), and provide robustness checks: compare q_k(τ) and β_k(τ) computed from direct full-network simulations (same binary update rules) to solutions of the corrected eq. 5.17 across parameter sets; test sensitivity to non‑Gaussian input statistics and to discrete update schedules; and report convergence diagnostics (time-window dependence, discretization error bars) for the numerical solver.

**Linearization and global reductions used in stability analysis need explicit validity ranges and finite‑K checks**

Sections 6.1–6.2 derive local (linear) and global (piecewise‑linear / Θ) stability thresholds τ_L and τ_G, but the analysis does not state the precise smallness/large‑ness conditions under which higher‑order terms are negligible, nor does it bound the time over which linearization remains valid. It would be helpful to (a) make explicit the amplitude regimes (e.g., |δm| ≪ 1/√K) and time horizons for which the Jacobian linearization is justified and quantify remainder terms, (b) include a second‑order (or nonlinear) expansion or Lyapunov‑style estimate that provides bounds on deviations from linearized trajectories, and (c) validate analytic thresholds by computing Lyapunov exponents, Floquet exponents where relevant, and by mapping basins of attraction using full nonlinear simulations for representative K,N and τ. Concretely, add error bounds on the linearization used to derive τ_L and τ_G (or qualify the statements), and present numerical basin maps / phase portraits that demonstrate where the analytic boundaries are accurate or need modification.

**Claim of an 'infinite' Lyapunov exponent conflates limit prescriptions and lacks finite‑size spectra**

Readers might note that declaring the Lyapunov exponent λ_L infinite because of microscopic discreteness is a strong statement that depends on the order of limits (N→∞ vs. perturbation size →0) and on equating single‑bit flips with infinitesimal perturbations. It would be helpful to replace the blanket divergence claim with quantitative finite‑size analysis: compute the maximal Lyapunov exponent and the Lyapunov spectrum numerically for large but finite N across the regimes studied, report how the maximal exponent scales with N and K (or show finite‑time Lyapunov growth rates), and discuss alternative limit prescriptions and their dynamical implications. If microscopic discreteness produces very large initial growth but a finite exponential rate, present the appropriate finite‑time or short‑scale growth measure instead of ‘‘infinite’’ λ_L. Concretely, add numeric Lyapunov computations (or equivalent Hamming‑distance growth rates) and an analytic discussion of how discreteness and thermodynamic limits interact.

**Limited treatment of heterogeneity and structured connectivity undermines robustness claims**

The heterogeneous-parameters analysis focuses on independent threshold variations with two simple distributions, and structured connectivity (degree correlations, synaptic-weight heterogeneity, motifs, spatial clustering) is largely unaddressed. Readers might note that biologically relevant correlated heterogeneities and non‑i.i.d. connectivity can qualitatively alter balance, variability, and stability. It would be helpful to extend the mean‑field derivation to allow joint distributions of thresholds, in‑degree, and synaptic weights (showing how β_k and α_k are modified), to derive explicit conditions that tie heterogeneity width Δ to K (e.g., when fluctuations remain balanced only if Δ = o(1) or Δ ≪ c/√K), and to validate claims with simulations that include synaptic heterogeneity and threshold–connectivity correlations. If full generalization is infeasible in this manuscript, please clearly qualify the results as applying to unstructured i.i.d. random networks and add a targeted figure showing how a few simple structured motifs (modularity, degree–threshold correlations, a small fraction of strong motifs) alter key predictions.

**Status**: [Pending]

---

## Detailed Comments (20)

### 1. Unclear order-of-limits and K–N scaling for mean-field exactness

**Status**: [Pending]

**Quote**:
> We present an analytical solution of the mean-field theory of this model, which is exact in the limit of large network size.

**Feedback**:
Readers might note the derivation of Gaussian/independence closure depends on how K scales with N (Appendix A cites K ≪ log N_k). It would be helpful to state the precise joint limit used (for example N→∞ with K = o(log N) or K^2/N→0), to indicate which statements assume N→∞ before K→∞ versus simultaneous scaling, and to include the combinatorial argument (expected number of short loops ~ K^l/N^{l-1}) that motivates the K = o(log N) regime. Concretely, add a short paragraph in the main text or appendix that (a) declares the limit ordering and scaling assumptions, (b) points to which lemmas/results require which ordering, and (c) flags any results that fail outside the stated regime.

---

### 2. Unjustified Gaussian/CLT condition and missing error bound

**Status**: [Pending]

**Quote**:
> For finite $K$, the equilibrium activities satisfy $m_{k}=F_{k}(m_{E},\,m_{I})$, with $F_{k}$ given by equation 5. However, as long as
> 
> $m_{k}\gg K^{-1},$ (16)
> 
> the gaussian assumption of the input statistics is a good approximation; hence, equations 7 still hold.

**Feedback**:
Readers might note the informal condition m_k ≫ 1/K should be replaced by a precise probabilistic statement. It would be helpful to (a) restate the requirement as K m_pre ≫ 1 together with the synaptic weight scaling (J∼1/√K) and weak presynaptic correlations, and (b) add a CLT error bound (for example a Berry–Esseen style bound giving O((K m_pre)^{-1/2}) error) or cite a suitable finite-sample CLT for sums of rare Bernoulli inputs. Concretely, add one displayed inequality bounding the approximation error in expectation or distribution (e.g., sup_x |P(S_K≤x)−Φ(x)| ≤ C/(K m_pre)^{1/2}) and state the extra independence/weight-scaling hypotheses required for that bound to hold.

---

### 3. Neglected covariance between connectivity and activity in Eq. 3.11

**Status**: [Pending]

**Quote**:
> Note that on the right-hand side (r.h.s.) of equation 3.11 we have neglected the correlations between the random fluctuations in the activity of a cell and the particular realization of its output connectivity. This is justified since such correlations are weak in the large $N$ limit.

**Feedback**:
Readers might note replacing E[J_{kl}^{ij} σ_l^j] by E[J_{kl}^{ij}]E[σ_l^j] omits Cov(J,σ), which scales as (J_{kl}/√K) E_J[ξ_{ij} δ_j(J)]. It would be helpful to (a) state the quenched self-averaging assumption explicitly, (b) provide a short bound under which Cov(J,σ)=o(1) (for example show Cov(J,σ)=O(K^2/N) or o(1) under K^2/N→0), or (c) cite a result justifying that the covariance vanishes in the stated limit. Concretely, insert one short derivation or a lemma that writes the covariance and shows its scaling with K and N.

---

### 4. Connection probability indexing yields incorrect expected in‑degree

**Status**: [Pending]

**Quote**:
> The connection between the $i$th postsynaptic neuron of the $k$th population and the $j$th presynaptic neuron of the $l$th population, denoted $J_{kl}^{ij}$ is $J_{kl}/\sqrt{K}$ with probability $K/N_{k}$ and zero otherwise. Here $k,l=1,2$.

**Feedback**:
Readers might note the connection probability should reference the presynaptic pool size N_l so that the expected number of incoming connections from population l is E[# from l] = N_l P = K. As written P = K/N_k gives E[# from l] = K (N_l/N_k), which equals K only if N_l = N_k. It would be helpful to correct the probability to K/N_l (or explicitly state equal population sizes) and annotate how this choice affects later sums and normalizations. Concretely, correct the text to P = K/N_l (or add the equal‑size assumption) and update any affected derivations or simulation parameter descriptions.

---

### 5. Incorrect form for bivariate Gaussian joint activation in Eq. 5.17

**Status**: [Pending]

**Quote**:
> Using this relation, the following self-consistent equation for $q_{k}(\tau)$ (with $\tau \geq 0$) is obtained:
> 
> $$
> \begin{array}{l}
> \tau_{k} \frac{d q_{k}(\tau)}{d \tau} = - q_{k}(\tau) + \int_{0}^{\infty} \frac{d t}{\tau_{k}} \\
> \quad \times \exp(-t / \tau_{k}) \int D x \left[ H \left(\frac{- u_{k} - \sqrt{\beta_{k}(t + \tau)} x}{\sqrt{\alpha_{k}} - \beta_{k}(t + \tau)} x\right) \right]^{2}. \tag{5.17}
> \end{array}
> $$

**Feedback**:
Readers might note the integrand [H(...)]^2 is not the correct bivariate‑Gaussian joint activation probability. For a bivariate Gaussian with mean u_k, Var α_k and covariance β_k(τ) the joint P[ z(t)>0, z(t+τ)>0 ] is representable by a one‑dimensional integral using the conditional Gaussian: ∫Dx Θ(u_k+√α_k x) Φ( (u_k + (β/√α_k)x)/√(α_k - β^2/α_k) ). It would be helpful to replace equation (5.17) with the conditional‑Gaussian integral, show the short derivation (conditioning on one time and using the conditional mean/variance), and then re-evaluate any numerical solutions and stability analysis that depend on q_k(τ). Concretely, provide the corrected displayed form, add the derivation steps in Appendix A.2, and flag numerical results that must be recomputed.

---

### 6. Missing coupling / normalization factors in input autocovariance (Eq. 5.15)

**Status**: [Pending]

**Quote**:
> $$
> \beta_{k}(\tau) = \left[ \left\langle \delta u_{i}^{k}(t) \delta u_{i}^{k}(t + \tau) \right\rangle \right] = q_{E}(\tau) + J_{k}^{2} q_{I}(\tau), \tag{5.15}
> $$

**Feedback**:
Readers might note the displayed form omits explicit factors of K, population sizes, and the paper's J rescaling. It would be helpful to show the microscopic sum explicitly: β_k(τ)=∑_l K_{kl} J_{kl}^2 q_l(τ), and then state how the authors' normalization (e.g., J_{kl}→J_{kl}/√K and K_{kl}=K) reduces this to the compact form used. Concretely, add a one‑paragraph algebraic derivation (expand the microscopic sum, substitute the J and K scalings) so units and scaling are explicit and reproducible.

---

### 7. Domain and singularity issues in ISI/interval formula (Eq. 5.18)

**Status**: [Pending]

**Quote**:
> $$
> I _ {i} (t) = \frac {m _ {i} \left(1 - m _ {i}\right)}{\tau_ {E} \left(1 - 2 m _ {i}\right)} \left(\exp \left(- m _ {i} t / \tau_ {E}\right) - \exp \left(- \left(1 - m _ {i}\right) t / \tau_ {E}\right)\right), t \geq 0. \tag {5.18}
> $$

**Feedback**:
Readers might note the long‑time decay is governed by the slower of m_i and 1−m_i, so the dominant decay constant is min(m_i,1−m_i)/τ_E rather than always m_i/τ_E; additionally the prefactor has 1−2m_i in the denominator and is singular at m_i=1/2. It would be helpful to (a) state the domain of validity (exclude or treat m_i=1/2), (b) provide the limiting form when m_i→1/2 (take the limit analytically to remove the removable singularity), and (c) correct the long‑time decay statement accordingly. Concretely, insert the limiting expression for m_i→1/2 and add a short sentence identifying the actual slowest timescale.

---

### 8. Missing derivation of averaging over update-intervals in autocorrelation equation

**Status**: [Pending]

**Quote**:
> Note that the integral over  $t$  in equation 5.17 results from averaging over the distribution of update time intervals. The solution of this integral equation yields a function  $q_{k}(t)$ , which decays to its equilibrium value with a time constant of the order of  $\tau_{k}$ .

**Feedback**:
Readers might note the derivation should show explicitly that the exponential kernel arises from Poisson updates and why the joint probability is evaluated at t'+τ (hence β_k(t'+τ)). It would be helpful to add the intermediate step writing q_k(τ)=∫_0^∞ r(t') P[z(t_0)>0,z(t_0+τ+t')>0] dt' with r(t')=τ_k^{-1} e^{-t'/τ_k}, then substitute the correct bivariate‑Gaussian joint probability (see comment 6). Concretely, add the displayed intermediate identity in Appendix A.2 so the averaging step is transparent.

---

### 9. Derivation of the 1/√K perturbation amplitude scale

**Status**: [Pending]

**Quote**:
> To determine the stability of the balanced state, we have to study the response of the system to small perturbations in the population activity rates. However, because of the nature of the balanced state, we have to distinguish two scales of perturbations: local perturbations, in which the deviations in the rates are small compared to $1/\sqrt{K}$, and global perturbations, in which these deviations are large compared to $1/\sqrt{K}$.

**Feedback**:
Readers might note the 1/√K amplitude arises directly from the input scaling. It would be helpful to include the few algebraic steps inline: show u∼√K m, so δu≈√K δm and the linearization condition δu≪1 implies |δm|≪1/√K. Concretely, insert these three lines near the quoted sentence so the origin of the mesoscopic O(1/√K) scale is explicit to readers.

---

### 10. Linearization time‑horizon and remainder estimate

**Status**: [Pending]

**Quote**:
> To determine the stability of the balanced state, we have to study the response of the system to small perturbations in the population activity rates. However, because of the nature of the balanced state, we have to distinguish two scales of perturbations: local perturbations, in which the deviations in the rates are small compared to $1/\sqrt{K}$, and global perturbations, in which these deviations are large compared to $1/\sqrt{K}$.

**Feedback**:
It would be helpful to quantify how long the linearization remains accurate. For an initial amplitude ε≪1/√K and an unstable eigenvalue λ≈O(√K), the linear regime persists up to roughly T≲(1/|λ|) log((c/√K)/ε) with c=O(1). Concretely, add a short displayed estimate of this form (with a brief justification) and state that linear conclusions about stability are valid only on that time horizon unless nonlinear terms are shown to remain small.

---

### 11. Algebraic misstatement: stability condition depends on F's spectrum, not τ alone

**Status**: [Pending]

**Quote**:
> Solving equations 10 one obtains $\delta m_{k}(t)=\delta m_{k,1}\exp(\lambda_{1}t)+\delta m_{k,2}\exp(\lambda_{2}t)$ where the eigenvalues $\lambda_{1}$ and $\lambda_{2}$ of the 2 by 2 equations (see equations 10) are both of order $\sqrt{K}$. Requiring that their real part be negative yields a condition on $\tau$ of the form
> 
> $\tau<\tau_{L},$ (12)
> 
> where $\tau_{L}$ is of order 1; its precise value depends on the system parameters.

**Feedback**:
Readers might note the linear algebra gives τλ = −1 + √K μ (with μ an eigenvalue of F), so Re(λ)<0 ⇔ √K Re(μ) < 1 — a condition on μ (and K), not directly on τ. It would be helpful to correct the text to state λ = (−1+√K μ)/τ and to explain that τ rescales λ but cannot change its sign for positive τ unless the μ dependence is taken into account. Concretely, replace the sentence implying a direct bound on τ with the equivalent spectral condition and show the algebraic steps yielding λ in terms of τ, √K, and μ.

---

### 12. Inconsistent fixed‑point subtraction in Θ approximation (Eq. 6.4)

**Status**: [Pending]

**Quote**:
> In fact, since the perturbation destroys the balance between excitation and inhibition, $H(-u_{k}/\sqrt{\alpha_{k}})$ of equation 3.3 can be approximated by $\Theta(u_{k})$; hence the evolution of the perturbations is described by
> 
> $\tau_{k}\frac{d}{dt}\delta m_{k}(t)=-\delta m_{k}(t)+\Theta(\delta m_{E}-J_{k}\delta m_{I})-m_{k}.$ (6.4)

**Feedback**:
Readers might note at δm=0 the RHS of (6.4) is Θ(u_k^*)−m_k^*, which need not vanish; the fixed point subtraction is inconsistent. It would be helpful to replace the RHS by −δm_k + Θ(u_k^*+Δu_k) − Θ(u_k^*) so the fixed‑point cancellation is explicit when approximating H by Θ. Concretely, rederive the piecewise dynamics with this subtraction, present the corrected equation, and indicate how the τ_G threshold is modified by the corrected piecewise flow.

---

### 13. Sign / convention confusion in Heaviside approximation H(·) → Θ(·)

**Status**: [Pending]

**Quote**:
> In fact, since the perturbation destroys the balance between excitation and inhibition, $H(-u_{k}/\sqrt{\alpha_{k}})$ of equation 3.3 can be approximated by $\Theta(u_{k})$; hence the evolution of the perturbations is described by

**Feedback**:
Readers might note if H(x) denotes a smoothed step (cdf) then H(-x)→Θ(-x) as the slope→∞, so the sign appears reversed in the manuscript. It would be helpful to state explicitly the definition and sign convention of H, correct the approximation (either to Θ(-u_k) or explain the authors' sign convention), and then verify that the piecewise flow and stability conclusions use the corrected sign. Concretely, add a parenthetical definition of H in the main text (H(s)=P(Z<s)) and update nearby approximations accordingly.

---

### 14. Nonstandard Lyapunov definition and unclear limit ordering

**Status**: [Pending]

**Quote**:
> The maximum Lyapunov exponent $\lambda_{L}$, defined by
> 
> $\lambda_{L}\equiv\lim_{D_{k}\to 0}D_{k}^{-1}\frac{dD_{k}}{dt},$ (12)
> 
> should be positive. Note that in calculating $\lambda_{L}$, we will first take the large $N$ limit of $D_{k}$ and then $D_{k}\to 0$ limit.

**Feedback**:
Readers might note the displayed formula is an instantaneous logarithmic derivative rather than the standard long‑time Lyapunov exponent λ = lim_{ε→0} lim_{t→∞} (1/t) ln(D(t)/D(0)). It would be helpful to (a) adopt the standard definition of Lyapunov exponent, (b) make explicit the order of limits used in the analysis (N→∞, ε→0, t→∞) and the rationale for that ordering, and (c) explain how microscopic discreteness (single‑bit flips) are treated under that ordering. Concretely, replace the displayed instantaneous definition with the standard double‑limit definition and add a brief paragraph discussing finite‑N finite‑time measures if discreteness prevents taking t→∞ first.

---

### 15. Locked solution stability depends on parameters (not generically unstable)

**Status**: [Pending]

**Quote**:
> This equation has two stationary solutions. One is
> 
> $Q_{k}=m_{k},$ (11)
> 
> which corresponds to a fully locked trajectories. This solution is unstable, as will be shown below.

**Feedback**:
Readers might note stability of the locked solution is parameter dependent. It would be helpful to state the explicit linear condition: linearization yields τ_k dD_k/dt = [−1 + κ_k (dI/dγ)|_{α_k}] D_k, so instability requires κ_k (dI/dγ)|_{α_k} > 1. Concretely, add this condition and, if the manuscript's parameter set satisfies it, show the numerical value of κ_k (dI/dγ)|_{α_k} for the chosen parameters to justify the qualitative statement.

---

### 16. Illegal square root of log(m) and sign error in rate–distribution asymptotic (7.17)

**Status**: [Pending]

**Quote**:
> $$
> \rho_{k}(m) \propto \frac{P \left(- \sqrt {\alpha_{k}} \left(\sqrt {2 \log (m)} - \tilde {h}_{k}\right)\right)}{m \sqrt {\log (m)}} \tag {7.17}
> $$

**Feedback**:
Readers might note for 0<m<1 we have log(m)<0, so expressions like √(log m) are not real. It would be helpful to replace log(m) by |log m| and fix the sign coming from the tail approximation h(m)≈−√{2|log m|}. Concretely, rewrite (7.17) as ρ_k(m) ∝ P(√α_k (√{2|log m|} − ˜h_k))/(m√{|log m|}) and add the short derivation step that produced the 1/(m√{|log m|}) Jacobian factor.

---

### 17. Asymptotic scaling for u_k in low‑rate limit is logarithmic, not algebraic

**Status**: [Pending]

**Quote**:
> To assess the effect of $\Delta$, we analyze equation 7.9 in the low $m_{k}$ limit. In this case, the solution for $u_{k}$ is
> 
> $$
> u_{k} + \Delta/2 = O(\sqrt{m_{k}}). \tag{7.10}
> $$

**Feedback**:
Readers might note Gaussian‑tail asymptotics give u_k + Δ/2 ∼ −√{2α_k |log m_k|} (i.e., grows like √{|log m|}, logarithmic in 1/m), not O(√m_k). It would be helpful to replace (7.10) with the correct tail result and sketch the derivation: use H(s)∼φ(s)/s for large negative s and invert the relation to obtain s^2/2 ∼ |log m|, hence s∼−√{2|log m|}. Concretely, correct the asymptotic statement and add two lines of derivation.

---

### 18. Incorrect standard deviation for presynaptic counts in Appendix A

**Status**: [Pending]

**Quote**:
> The average values of $n_E$ and $n_I$ satisfy $\langle n_k \rangle = m_k K$. The standard deviations $\sigma(n_E)$ and $\sigma(n_I)$ are given by $\sigma(n_k) = m_k K$.

**Feedback**:
Readers might note for Poisson (or Binomial) presynaptic counts with mean K m_k, we have Var(n_k) = K m_k and σ(n_k)=√(K m_k), not m_k K. It would be helpful to correct the standard deviation to √(K m_k) and briefly note that for large K the Gaussian approximation replaces p_k(n) by N(K m_k, K m_k). Concretely, change the displayed variance statement and any downstream approximations that used the incorrect scale.

---

### 19. Combinatorial error in A.12: product outside sums is invalid

**Status**: [Pending]

**Quote**:
> $$
> \begin{array}{l}
> F_k = \prod_{l=1,2} \sum_{n_{kl}} p_l(n_{1l}, n_{2l}, n_{3l}) \Theta \left( \sqrt{K} J_{k0} m_0 + \sum_l \frac{J_{kl}}{\sqrt{K}} (n_{1l} + n_{2l}) - \theta_k \right) \\
> \times \Theta \left( \sqrt{K} J_{k0} m_0 + \sum_l \frac{J_{kl}}{\sqrt{K}} (n_{1l} + n_{3l}) - \theta_k \right), \tag{A.12}
> \end{array}
> $$

**Feedback**:
Readers might note the Θ(...) depend on sums over l and therefore the product over l cannot be factored outside the sums. It would be helpful to replace A.12 by an explicit multi‑sum over the joint counts with the product of per‑population probabilities inside the sum, e.g. write F_k = ∑_{all n_{•l}} [∏_l p_l(…)] Θ(total input) Θ(total other input), and then proceed to the Gaussian limit. Concretely, correct A.12 to an explicit joint sum and add a short comment that only after joint summation can the central limit approximation be applied.

---

### 20. Missing time dependence in p_l for autocorrelation derivation (A.13)

**Status**: [Pending]

**Quote**:
> $$
> p_l(n_1, n_2, n_3) = \frac{(q_l K)^{n_1}}{n_1!} \frac{((m_l - q_l) K)^{n_2 + n_3}}{n_2! n_3!} e^{-(2m_l - q_l)K}. \tag{A.13}
> $$

**Feedback**:
Readers might note in A.10 the integrand depends on q_l(t'+τ), so the Poisson parameters in p_l should carry the appropriate time arguments. It would be helpful to write p_l(n_1,n_2,n_3; t',τ) with q_l evaluated at the shifted time (e.g. q_l(t'+τ)) and to indicate which factors depend on t' versus τ so the time‑translation/averaging is explicit and the Gaussian approximation steps become unambiguous. Concretely, modify A.13 to include the time arguments and update the subsequent integrals.

---
