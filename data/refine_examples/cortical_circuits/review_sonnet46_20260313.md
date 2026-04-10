# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 03/13/2026
**Domain**: computational_neuroscience/neural_circuits
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a mean-field theory for large networks of binary threshold neurons operating in a 'balanced' regime where strong excitatory and inhibitory inputs approximately cancel, yielding irregular, low-rate firing. The authors derive self-consistent equations for firing rates, autocorrelations, and rate distributions; analyze local and global stability of the balanced fixed point; characterize the dynamics as 'chaotic' via a Lyapunov exponent calculation; and argue that the balanced state enables rapid tracking of time-varying inputs on timescales O(1/√K). Comparisons with prefrontal cortex firing-rate distributions are offered as qualitative empirical support.

Below are the most important issues identified by the review panel.

**Infinite Lyapunov Exponent Does Not Constitute a Standard Characterization of Chaos**

Section 8 and equation 8.6 claim to establish the 'chaotic nature' of the balanced state by showing that the maximum Lyapunov exponent λ_L is infinite, arising because the distance D_k grows from zero even for infinitesimally small perturbations due to the discontinuous threshold nonlinearity. All three reviewers flag this as a fundamental conceptual issue: an infinite Lyapunov exponent is a trivial consequence of the binary (discontinuous) gain function and would hold for any binary threshold network, balanced or not, rather than being a distinctive property of the balanced attractor. In continuous dynamical systems, chaos is defined by a finite positive Lyapunov exponent measuring exponential divergence of nearby trajectories; the divergence here reflects a modeling artifact of discrete state variables. The paper briefly acknowledges that the definition is 'technically inapplicable' to discrete systems but does not resolve the issue. It would be helpful to either (a) provide a regularized or coarse-grained Lyapunov measure computed over timescales longer than a single update that converges to a finite, parameter-dependent value, or (b) explicitly adopt an alternative formal definition of chaos appropriate for discrete-state systems—such as positive topological entropy or sensitivity in the sense of Devaney—and demonstrate that the balanced state satisfies it while unbalanced states do not. Without this, the central claim of 'chaotic' dynamics in the abstract and Section 8 rests on a measure that is uninformative about the attractor structure.

**Mean-Field Validity Requires K ≪ log N, a Condition Incompatible with the Paper's Primary Analytical Regime**

Appendix A explicitly states that the independence assumption underlying the mean-field factorization 'holds rigorously provided that K ≪ log N_k' (citing Derrida et al., 1987). However, the paper's central results are developed in the double limit N → ∞ followed by K → ∞, with the working condition 1 ≪ K ≪ N (equation 8), and figures use K = 1000. For K = 1000, the condition K ≪ log N requires N ≫ exp(1000), which is astronomically large and biologically irrelevant. The paper claims the mean-field theory is 'exact in the limit of large network size' (abstract), but this exactness is conditional on K ≪ log N, which is violated when K → ∞. The order of limits (N → ∞ first, then K → ∞) does not resolve the tension, because for any fixed large K the mean-field factorization is only justified when N is super-exponentially large in K. The paper does not quantify the error introduced by violating this condition, does not provide direct network simulations with explicit (N, K) pairs to validate mean-field predictions, and does not verify that the Gaussian approximation of the Poisson input distribution (equations A.6–A.7) remains accurate at K = 1000. It would be helpful to add direct network simulations comparing population statistics against mean-field predictions at realistic (N, K) values, or to provide an explicit bound on the correlation-induced error in F_k (equation A.5) and qualify the exactness claim accordingly.

**Global Stability Analysis Relies on an Approximation Whose Domain of Validity Is Not Established**

The global stability analysis in Section 6.2 approximates H(−u_k/√α_k) by the Heaviside function Θ(u_k) on the grounds that large perturbations destroy balance, making u_k of order √K (equation 6.4). This converts the smooth mean-field equations into piecewise-linear dynamics and yields an explicit expression for τ_G (equation 6.6). However, the approximation is not verified to be uniformly valid throughout the transient trajectory: α_k depends on m_E and m_I (equation 3.10), which change during the perturbation, and if m_k transiently approaches 0 or 1, α_k could become very small or large, invalidating H ≈ Θ. More critically, during the intermediate phase when u_k transitions from O(√K) back to O(1), the approximation breaks down and the actual dynamics may differ qualitatively from equation 6.4. Since τ_G determines the boundary between qualitatively distinct dynamical regimes (the three cases in Section 6.3), errors in this approximation could misclassify the stability of the balanced state. It would be helpful to bound α_k during the transient evolution to confirm self-consistency of the approximation, or to validate equation 6.6 numerically across a range of perturbation magnitudes and initial conditions.

**Stationarity and Ergodicity Assumptions in the Autocorrelation Derivation Are Unjustified for a Claimed Chaotic Attractor**

The derivation of the autocorrelation function q_k(τ) in Section 5.2 and Appendix A.2 assumes stationarity and ergodicity, so that time averages equal ensemble averages and the autocorrelation depends only on lag τ (equations 5.16–5.17 and A.10–A.14). Specifically, equation A.13 assumes that the joint probability of a cell being active at two times factorizes in terms of q_l(τ), which requires ergodicity of the single-cell process. However, Section 8 establishes that the balanced state is chaotic, with trajectories that diverge completely from any reference trajectory. In chaotic systems, ergodicity is not guaranteed—the system may explore only a subset of the attractor, or mixing times may be very long relative to the timescales of interest. The paper does not prove uniqueness of the stationary solution to equation 5.17, does not demonstrate convergence of the fixed-point iteration, and does not verify numerically that time-averaged autocorrelations match the theoretically predicted stationary solution. It would be helpful to either prove ergodicity of the single-cell process within the mean-field framework, or to validate equation 5.17 by comparing its predictions against autocorrelations measured in direct network simulations.

**Fast Tracking Claims Lack a Quantitative Fidelity Metric and Use an Unfair Comparison Network**

Section 9 argues that the balanced network tracks time-varying inputs on timescales O(1/√K), presented as a key functional advantage. Two problems weaken this claim. First, the comparison in Figures 14–16 is between the balanced binary network and a threshold-linear rate network (equation 9.10) whose synaptic strengths scale as J_kl/K rather than J_kl/√K, meaning the comparison network has fundamentally weaker recurrent feedback by a factor of √K. This conflates the effects of balance with the effects of synaptic strength scaling; a fair comparison would hold synaptic scaling fixed and vary only the balance condition. Second, tracking fidelity is assessed only qualitatively from figures, with no quantitative metric such as mean-squared tracking error, coherence as a function of input frequency, or signal-to-noise ratio. The paper itself acknowledges in Section 10.5 that 'the microscopic state is not tightly locked to the stimulus temporal variations' for homogeneous inputs, meaning individual neurons do not reliably encode the stimulus even though the population rate tracks it—a distinction that is biologically critical for neural coding. It would be helpful to define an explicit tracking error metric, include a comparison network with the same 1/√K synaptic scaling but without E-I balance, and clarify what computational operations benefit from population-rate tracking in the presence of microscopic chaos.

**Experimental Comparison of Rate Distributions Is Underconstrained and Not Falsifiable as Presented**

Section 7.3 compares the theoretically predicted rate distribution (Figure 11B) with an experimentally observed histogram from prefrontal cortex (Figure 11C, Abeles et al., 1988) and concludes the results are 'consistent with theoretical predictions.' Several issues limit the strength of this comparison. The comparison is qualitative—no goodness-of-fit statistic is provided, and the power-law tail ρ_k(m) ∝ 1/(m√|log m|) predicted by equation 7.12 is not explicitly tested against the data. The theoretical prediction holds specifically in the limit m_0 ≪ 1 under a bounded uniform threshold distribution, but the experimental data come from behaving animals with a mean rate of 15.8 Hz, a regime where the low-rate approximations underlying equations 7.10–7.14 may not apply. The experimental histogram also excludes silent neurons, which would systematically distort comparison with the theoretical ρ_k(m) that includes all cells. More fundamentally, the power-law character of the tail is a direct consequence of the specific choice of uniform P(θ) combined with the logarithmic relationship h(m) (equation 4.13), and the paper does not demonstrate robustness to other threshold distributions or identify which features of ρ_k(m) are genuinely universal. It would be helpful to derive the rate distribution for a broader class of P(θ), provide at least a semi-quantitative fit to the data, and explicitly acknowledge whether Figure 11C constitutes a test of the model or merely a post-hoc consistency illustration.

**Status**: [Pending]

---

## Detailed Comments (21)

### 1. Mean-field exactness claim contradicted by Appendix A condition K ≪ log N

**Status**: [Pending]

**Quote**:
> We present an analytical solution of the mean-field theory of this model, which is exact in the limit of large network size.

**Feedback**:
The abstract claims exactness 'in the limit of large network size,' but Appendix A explicitly conditions this on K ≪ log N_k (citing Derrida et al., 1987). For K = 1000 (used in figures), K ≪ log N requires N ≫ exp(1000). The introduction compounds this by stating the weaker condition 1 ≪ K ≪ N, which is mathematically incompatible with K ≪ log N: at K = 1000, K ≪ N is satisfied for any N ≫ 1000, whereas K ≪ log N requires super-exponentially large N. It would be helpful to rewrite the exactness claim to specify that it holds rigorously only when K ≪ log N, and to acknowledge that the working regime 1 ≪ K ≪ N is an approximation whose error is not quantified.

---

### 2. Summation upper limit uses wrong index in mean input derivation

**Status**: [Pending]

**Quote**:
> u_{k}(t)\,=\,[u_{k}^{i}(t)]=\sum_{l=1}^{2}\,\sum_{j=1}^{N_{i}}[\,J_{kl}^{ij}\,][\,\sigma_{l}^{j}(t)\,]\,+u_{k}^{0}-\theta_{k}.

**Feedback**:
The inner sum over presynaptic neurons in population l should run from j = 1 to N_l, not N_i. Here i indexes the postsynaptic neuron and l indexes the presynaptic population. With [J_kl^ij] = J_kl √K / N_l, summing over N_l presynaptic neurons yields Σ_l J_kl √K m_l, matching equation 3.5. Using N_i in the upper limit is inconsistent because N_i is the size of the postsynaptic population k, not the presynaptic population l, so the sum would not cancel the 1/N_l factor correctly. Rewrite the upper limit of the inner sum as N_l.

---

### 3. Normalization convention sets J_EE = J_IE = 1 without justifying that ratio is removable

**Status**: [Pending]

**Quote**:
> Since the model neurons are threshold elements, the absolute scale of $u_{i}^{k}$ is irrelevant. We therefore set
> 
> $J_{EE}=J_{IE}=1,$ (6)

**Feedback**:
The argument justifies fixing one overall scale (e.g., J_EE = 1) by rescaling u_E, but it does not justify simultaneously fixing J_IE = 1, because the ratio J_IE/J_EE is a dimensionless parameter that affects the relative drive to inhibitory versus excitatory cells and is not removable by a single rescaling. Since u_E and u_I each have independent thresholds θ_E and θ_I, rescaling u_E does not simultaneously rescale u_I. Setting J_EE = J_IE = 1 is therefore a genuine restriction on parameter space, not merely a choice of units. The paper should either demonstrate that J_IE/J_EE can be absorbed into θ_k or E_k without loss of generality, or acknowledge equation 6 as a simplifying assumption.

---

### 4. Equation 4.6 attribution conflates existence of unbalanced solution with argument for condition 4.5

**Status**: [Pending]

**Quote**:
> Equation 4.6 admits an unbalanced solution in which $m_{E} = 0$. In this solution, $m_{I}$ is to leading order in $k$ given by $m_{I} = Im_{0} / J_{I}$ (since the leading order in $u_{I}$ should vanish) so that
> 
> $$
> u _ {E} = \sqrt {K} \left(E - J _ {E} I / J _ {I}\right) m _ {0} <   0. \tag {4.7}
> $$

**Feedback**:
The text attributes the m_E = 0 unbalanced solution to condition 4.6, but the logical goal is to show that condition 4.5 eliminates it. Under condition 4.5, E/I > J_E/J_I implies E − J_E I/J_I > 0, making u_E > 0, which contradicts the requirement u_E < 0 for a silent excitatory population—thereby ruling out the m_E = 0 solution. As written, attributing the solution to 4.6 rather than showing how 4.5 rules it out leaves the logical argument incomplete. Rewrite to explicitly state that under condition 4.5, u_E > 0 contradicts m_E = 0, so condition 4.5 eliminates this unbalanced state.

---

### 5. Refractoriness attribution inverts the correct direction of autocorrelation effect

**Status**: [Pending]

**Quote**:
> As can be seen, the autocorrelations are larger than those predicted by Poisson statistics. This enhancement of short-time correlations reflect the refractoriness in the activities of the cells that project the cell.

**Feedback**:
Refractoriness suppresses repeated firing shortly after a spike, which reduces short-time autocorrelations relative to a Poisson process (producing a dip, not an excess). Enhanced short-time autocorrelations relative to Poisson are instead a signature of burstiness or positive temporal correlations in the drive. The ISI discussion in Section 5.3 correctly identifies refractoriness as causing the ISI to vanish at t = 0, but that is a statement about the ISI, not the autocorrelation function q_k(τ)—these two quantities carry opposite signatures of refractoriness. Rewrite the attribution as 'This enhancement of short-time correlations reflects the temporal persistence of the input fluctuations, which keeps the net input above threshold across consecutive update times.'

---

### 6. Stability threshold τ_L left without explicit expression despite fully determined 2×2 system

**Status**: [Pending]

**Quote**:
> Requiring that their real part be negative yields a condition on $\tau$ of the form
> 
> $\tau<\tau_{L},$ (12)
> 
> where $\tau_{L}$ is of order 1; its precise value depends on the system parameters.

**Feedback**:
The linearized system (equation 10) is a 2×2 matrix with entries √K f_kl given in closed form by equation (11). The eigenvalues satisfy det(M − λI) = 0, yielding an explicit algebraic expression for τ_L in terms of J_kl, u_k, and α_k. Leaving τ_L as 'of order 1; its precise value depends on the system parameters' makes equation (12) unverifiable and prevents readers from checking whether specific simulation parameters satisfy local stability. Since Section 6.2 references this condition to classify dynamical regimes, the omission propagates. It would be helpful to provide the explicit formula for τ_L derived from the characteristic equation of the 2×2 system, since all ingredients are already in hand.

---

### 7. Eigenvalue O(√K) claim fails when gain matrix F is singular

**Status**: [Pending]

**Quote**:
> Solving equations 10 one obtains $\delta m_{k}(t)=\delta m_{k,1}\exp(\lambda_{1}t)+\delta m_{k,2}\exp(\lambda_{2}t)$ where the eigenvalues $\lambda_{1}$ and $\lambda_{2}$ of the 2 by 2 equations (see equations 10) are both of order $\sqrt{K}$.

**Feedback**:
The 2×2 matrix has the form (−1/τ_k)I + √K F. If det(F) = f_EE f_II − f_EI f_IE = 0, one eigenvalue of F is zero and the corresponding full eigenvalue is −1/τ_k = O(1), not O(√K). In that degenerate case, the claim that 'small perturbations will decay with an extremely short time constant of order 1/√K' would be incorrect for one mode. It would be helpful to add the condition det(F) ≠ 0 as an explicit assumption, and to rewrite 'the eigenvalues λ_1 and λ_2 are both of order √K' as 'both of order √K, provided f_EE f_II ≠ f_EI f_IE.'

---

### 8. Argument of Θ in equation 6.4 appears to drop J_E factor

**Status**: [Pending]

**Quote**:
> $\tau_{k}\frac{d}{dt}\delta m_{k}(t)=-\delta m_{k}(t)+\Theta(\delta m_{E}-J_{k}\delta m_{I})-m_{k}.$ (6.4)

**Feedback**:
The perturbation to u_k is δu_k = J_E δm_E − J_I δm_I. The approximation H(−u_k/√α_k) ≈ Θ(u_k) then gives Θ(J_E δm_E − J_I δm_I), not Θ(δm_E − J_k δm_I). The notation J_k (with population index k) is also inconsistent with the J_E, J_I notation used throughout this section. Since τ_G in equation 6.6 depends on J_E and J_I separately, the piecewise-linear system in equation 6.4 must retain both coefficients to yield equation 6.6 correctly. Rewrite Θ(δm_E − J_k δm_I) as Θ(J_E δm_E − J_I δm_I) and replace J_k with J_I throughout equation 6.4.

---

### 9. Global stability conclusion conflates global and local stability

**Status**: [Pending]

**Quote**:
> In conclusion, the global stability condition guarantees that starting from arbitrary initial values $m_{k}(0)$, the population rates eventually will approach the balanced regime characterized by local fields $u_{k}$, which are of order 1 and not $\sqrt{K}$. In other words, the rates will deviate from the values of the balanced fixed point by at most $O(1/\sqrt{K})$ quantities.

**Feedback**:
Equation 6.5 (τ < τ_G) guarantees return to the balanced regime where u_k = O(1), but the second sentence—that rates deviate from the fixed point by at most O(1/√K)—additionally requires local stability (equation 6.3, τ < τ_L). Without local stability, the system may settle into a balanced limit cycle of amplitude O(1/√K) rather than converging to the fixed point (exactly Case 2 in Section 6.3). The phrase 'in other words' incorrectly presents these as equivalent. Rewrite the second sentence as: 'In other words, the rates will enter the balanced regime (u_k = O(1)), but whether they converge to the fixed point or to a limit cycle of amplitude O(1/√K) depends additionally on the local stability condition, equation 6.3.'

---

### 10. Square root of negative argument in equation 7.17

**Status**: [Pending]

**Quote**:
> $$
> \rho_{k}(m) \propto \frac{P \left(- \sqrt {\alpha_{k}} \left(\sqrt {2 \log (m)} - \tilde {h}_{k}\right)\right)}{m \sqrt {\log (m)}} \tag {7.17}
> $$
> 
> for $m_{-} < m < m_{+}$.

**Feedback**:
The domain of validity is m_- < m < m_+ with m_+ ≪ 1, so log(m) < 0 throughout, making both √(2 log m) and √(log m) imaginary. The very next sentence in the text corrects this by writing √(2 log(1/m)), and equation 7.13 uses log(1/m) consistently. Rewrite equation 7.17 as ρ_k(m) ∝ P(−√α_k (√(2 log(1/m)) − h̃_k)) / (m √(log(1/m))) because log(m) < 0 for all m in the stated domain.

---

### 11. Experimental comparison excludes silent neurons, biasing the rate distribution test

**Status**: [Pending]

**Quote**:
> The average rate (of the neurons that showed any activity during the time of measurement) was $15.8\mathrm{Hz}$. The observed histogram has a distinct unimodal skewed shape with a tail extending up to $80\mathrm{Hz}$. These results are consistent with the theoretical predictions of Figure 11B.

**Feedback**:
The parenthetical explicitly states that silent neurons are excluded from the experimental histogram, but the theoretical distribution ρ_k(m) in equation 7.12 includes all neurons. Excluding silent neurons truncates the left tail of the empirical distribution, making it appear more unimodal than it actually is and systematically favoring agreement with Figure 11B over the bimodal prediction of Figure 11A. Since the key qualitative distinction between sections 7.1 and 7.2 is precisely whether the rate distribution is bimodal or unimodal, the exclusion of silent neurons removes the most diagnostic feature of the comparison. The comparison sentence should acknowledge that the exclusion of silent neurons prevents a test of the bimodal vs. unimodal distinction, and that agreement with Figure 11B is a consistency check on the unimodal tail shape only.

---

### 12. Lyapunov exponent definition yields polynomial, not exponential, divergence

**Status**: [Pending]

**Quote**:
> The maximum Lyapunov exponent $\lambda_{L}$, defined by
> 
> $\lambda_{L}\equiv\lim_{D_{k}\to 0}D_{k}^{-1}\frac{dD_{k}}{dt},$ (12)
> 
> should be positive.

**Feedback**:
The standard Lyapunov exponent is λ_L = lim_{t→∞} (1/t) log(D(t)/D(0)). The definition given here is the instantaneous relative growth rate at D_k = 0, a different quantity. Since equation 13 shows dD_k/dt ∝ √D_k, integrating gives D_k(t) ∝ t², which is polynomial growth. For polynomial growth, the standard Lyapunov exponent is lim_{t→∞} (1/t) log(t²) = 0, not infinity. The quantity D_k⁻¹ dD_k/dt ~ D_k^{−1/2} diverges as D_k → 0, but this reflects the non-Lipschitz character of the √D_k vector field at the origin, not exponential sensitivity. The text should clarify that the quantity defined is the instantaneous relative growth rate at D_k = 0, that the resulting t² growth is polynomial divergence arising from the discontinuous gain function, and that this is distinct from the exponential divergence that characterizes chaos in continuous dynamical systems.

---

### 13. Prefactor 2/π in equation 13 lacks derivation in the singular limit γ_k → α_k

**Status**: [Pending]

**Quote**:
> To find the initial rate of divergence, we expand equation 10 for small $D_{k}$ and find that to leading order, the distances satisfy
> 
> $\tau_{k}\frac{dD_{k}}{dt}=\frac{2}{\pi}\frac{e^{-u_{k}^2/2\alpha_{k}}}{\sqrt{\alpha_{k}}}\sqrt{\alpha_{k}-\gamma_{k}}.$

**Feedback**:
The derivation requires expanding equation 14 around the locked fixed point Q_k = m_k (i.e., γ_k → α_k). Setting ε = α_k − γ_k and substituting y = (−u_k + √α_k x)/√ε, the integral over [H(y)]² with the transformed Gaussian measure must be evaluated as ε → 0. The claimed prefactor 2/π is plausible but involves a non-trivial interchange of the ε → 0 limit with the x-integration that is not presented anywhere in the paper or appendices. Since this prefactor is the only quantitative output of Section 8 and directly supports the claim that λ_L is infinite, its derivation is essential. It would be helpful to add the step-by-step expansion of the integral in equation 14 near γ_k = α_k to Appendix A, showing explicitly how the prefactor 2/π · exp(−u_k²/2α_k)/√α_k arises.

---

### 14. Stability of desynchronized fixed point Q_k = q_k is asserted but never demonstrated

**Status**: [Pending]

**Quote**:
> This solution is unstable, as will be shown below. The stable fixed point is
> 
> $Q_{k}=q_{k},$ (12)
> 
> which corresponds to a fully desynchronized trajectory so that at long times, the correlations between the two trajectories at the same time are those induced by the time-independent average activities.

**Feedback**:
The paper promises to show instability of Q_k = m_k 'below,' which is partially addressed by equation 13 showing dD_k/dt > 0 for D_k > 0. However, the stability of Q_k = q_k is asserted but never demonstrated. To verify stability, one must linearize equation 14 around Q_k = q_k and confirm the resulting eigenvalue is negative. Without this, there could be additional fixed points between q_k and m_k, or the dynamics near q_k could be oscillatory or unstable. The global convergence claim—'starting from any non-identical states, the two trajectories eventually will desynchronize completely'—requires more than local stability of q_k. It would be helpful to add an explicit linearization of equation 14 around Q_k = q_k to Appendix A, completing the stability argument for both fixed points as promised.

---

### 15. Equation 9.13 defines a ramp for all t but text describes a piecewise protocol

**Status**: [Pending]

**Quote**:
> In Figure 14 the external activity is ramped between $t = 1$ and $t = 2$,
> 
> $$
> m _ {0} (t) = m _ {0} + v _ {0} t, \tag {9.13}
> $$
> 
> and after $t = 2$ $m_0$ is kept constant again.

**Feedback**:
Equation 9.13 defines m_0(t) = m_0 + v_0 t for all t, giving m_0(0) = m_0 and m_0(1) = m_0 + v_0, but the text states the network is at equilibrium for t ∈ [0,1] with fixed m_0, so the ramp should start at t = 1. The correct piecewise definition is m_0(t) = m_0 for t ≤ 1, m_0(t) = m_0 + v_0(t−1) for 1 ≤ t ≤ 2, and m_0(t) = m_0 + v_0 for t ≥ 2. This is consistent with Figure 14's caption but not with equation 9.13. Rewrite equation 9.13 as the piecewise function m_0(t) = m_0 + v_0 max(0, t−1) (capped at v_0 after t = 2) to match both the text description and Figure 14.

---

### 16. Comparison network uses 1/K synaptic scaling instead of 1/√K, conflating balance with synaptic strength

**Status**: [Pending]

**Quote**:
> To compare the tracking capabilities of balanced networks with those of an unbalanced network, we consider a network of threshold linear neurons with synapses of strength $J_{kl}/K$ for internal connections and $\tilde{J}_{k0}/K$ for the strengths of the synapses projecting from the external population

**Feedback**:
The comparison network uses synaptic weights of order 1/K, whereas the balanced network uses weights of order 1/√K—a factor of √K weaker. The claimed √K tracking advantage ('m_k^1 will be of order √K times larger than in a balanced network') is therefore partly a consequence of this synaptic strength difference rather than solely of the balance condition. A fair comparison would use a threshold-linear network with 1/√K synaptic weights but without E-I balance, to isolate the effect of balance from the effect of synaptic scaling. As currently presented, the tracking advantage conflates two distinct factors, and the quantitative claim of a √K improvement attributable to balance alone is not substantiated.

---

### 17. Rate distribution narrows near saturation (m ≈ 1/2), not at low rates, for α < 1/2

**Status**: [Pending]

**Quote**:
> if $\alpha<1/2$, the fluctuations grow with $K$, and therefore the inhomogeneity in the threshold becomes negligible in the large $K$ limit. Thus, a network with inhomogeneous thresholds will act in the same way as a network with homogeneous thresholds. Specifically for low rates, the rate distribution will become narrow.

**Feedback**:
When α < 1/2, the input fluctuation σ ~ K^{1/2−α} grows without bound. For a binary threshold unit, m = H(u/σ); as σ → ∞ with u = O(1), the argument u/σ → 0, so H(u/σ) → H(0) = 1/2 for a symmetric gain function. All cells converge to firing rate ≈ 1/2 regardless of threshold—the distribution narrows near saturation (m ≈ 1/2), not near low rates. Rewrite 'Specifically for low rates, the rate distribution will become narrow' as 'Specifically, the rate distribution will become narrow and concentrated near the saturation rate m ≈ 1/2, rather than at low rates,' because the diverging fluctuations drive all cells toward the midpoint of the gain function.

---

### 18. Experimental citation on LGN input fraction appears to invert the logical support for balanced state

**Status**: [Pending]

**Quote**:
> Recent experimental findings of Ferster, Chung, and Wheat (1996) in cat primary visual cortex suggest that the input from the lateral geniculate nucleus (LGN) to layer 4 cortical cells are in fact a fraction of the net input.

**Feedback**:
The balanced state requires that external (LGN) input be large relative to the net (residual) synaptic input. But the sentence states LGN input 'is in fact a fraction of the net input,' which would mean LGN input is smaller than net input—the opposite of what the model requires. If 'net input' here means total gross synaptic drive (excitatory + inhibitory) rather than the residual after cancellation, the sentence is logically consistent with the model but uses 'net' in a non-standard way that reverses the intended meaning. Rewrite to clarify that 'fraction of the net input' refers to the total (gross) synaptic input, not the residual (excitatory minus inhibitory) input, and state explicitly whether the cited data support or challenge the large-external-input condition.

---

### 19. Product index in A.12 structurally ambiguous: Θ functions must sit outside the product over l

**Status**: [Pending]

**Quote**:
> F_k = \prod_{l=1,2} \sum_{n_{1l}, n_{2l}, n_{3l}} p_l(n_{1l}, n_{2l}, n_{3l}) \Theta \left( \sqrt{K} J_{k0} m_0 + \sum_l \frac{J_{kl}}{\sqrt{K}} (n_{1l} + n_{2l}) - \theta_k \right) \\
> \times \Theta \left( \sqrt{K} J_{k0} m_0 + \sum_l \frac{J_{kl}}{\sqrt{K}} (n_{1l} + n_{3l}) - \theta_k \right), \tag{A.12}

**Feedback**:
The Θ functions contain an inner sum over l (all populations simultaneously), yet the outer product also runs over l. As written, the product distributes over the Θ functions, which would square the threshold conditions rather than factorize the probability over populations. The correct structure is: F_k = [Σ over all n_{1l},n_{2l},n_{3l}] × [Π_l p_l(n_{1l},n_{2l},n_{3l})] × Θ(√K J_{k0}m_0 + Σ_l J_{kl}(n_{1l}+n_{2l})/√K − θ_k) × Θ(√K J_{k0}m_0 + Σ_l J_{kl}(n_{1l}+n_{3l})/√K − θ_k). Rewrite equation A.12 by moving the product symbol to apply only to p_l and placing both Θ functions outside the product.

---

### 20. Equivalence of deterministic and stochastic models not demonstrated for two-time correlations

**Status**: [Pending]

**Quote**:
> Thus, in this completely deterministic model, the mean rates $m_{k}$ satisfy exactly the same equations as the model with stochastic updating. This also holds true for the other mean-field equations of the model.

**Feedback**:
The equivalence demonstrated in Appendix B shows that m_k(t) satisfies the same integral equation for both models. However, the claim that equivalence 'holds true for the other mean-field equations'—including the autocorrelation equation A.10—is not demonstrated. The autocorrelation derivation in A.2 uses the exponential kernel exp(−t'/τ_k)/τ_k arising from Poisson update statistics via the memoryless property. For the deterministic model with kernel R_k(τ) = τ exp(−τ/τ_k)/τ_k², the joint distribution of update times at t and t+τ differs, and it is not verified that this R_k reproduces the identical kernel in the two-time correlation equation A.10. Rewrite 'This also holds true for the other mean-field equations of the model' as 'This equivalence holds for the single-time mean-field equations; the extension to two-time correlations requires additional verification that the joint update-time distribution under R_k reproduces the kernel in equation A.10.'

---

### 21. Microscopic locking claim for inhomogeneous input is in tension with established chaotic dynamics

**Status**: [Pending]

**Quote**:
> preliminary analysis (van Vreeswijk & Sompolinsky, 1998) shows that in the case of spatially inhomogeneous input fluctuations, the microscopic state of the network will tightly lock to the stimulus temporal variations.

**Feedback**:
Section 8 establishes that the balanced state is chaotic, with complete divergence of nearby trajectories. The claim that the microscopic state 'tightly locks' to inhomogeneous stimulus fluctuations requires that the stimulus suppresses the chaotic instability—a non-trivial dynamical claim analogous to chaos suppression or generalized synchronization. The section does not state what property of the inhomogeneous input produces locking, does not quantify the required inhomogeneity amplitude relative to intrinsic fluctuations O(1/√K), and cites only a preliminary unpublished analysis. It would be helpful to add a sentence clarifying the mechanism—e.g., whether the inhomogeneous input must exceed O(1/√K) to suppress chaos—and to note explicitly that this result is preliminary and unverified in the present paper.

---
