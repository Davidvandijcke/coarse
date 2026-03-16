# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 03/16/2026
**Domain**: computational_neuroscience/neural_circuits
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a mean-field theory for a randomly connected network of binary threshold neurons operating in a 'balanced state,' where strong excitatory and inhibitory inputs cancel to produce low firing rates and fast fluctuations. The authors derive self-consistency equations for population rates and autocorrelations, analyze local and global stability of the balanced fixed point, characterize the temporal statistics of single-cell activity (including ISIs and rate distributions), and argue that the balanced state is chaotic and capable of rapidly tracking time-varying inputs. The main results include analytical conditions for the balanced state to be the unique attractor, a predicted power-law firing rate distribution, and a tracking timescale of order 1/√K.

Below are the most important issues identified by the review panel.

**Mean-Field Factorization Is Formally Justified Only in a Regime Far from the Biologically Relevant Parameters**

Appendix A explicitly states that the independence assumption underlying the mean-field factorization—that inputs to a given cell from different presynaptic cells are uncorrelated—holds rigorously only when K ≪ log N_k, citing Derrida et al. (1987). However, the paper's primary regime of interest is 1 ≪ K ≪ N_k, and for biologically realistic parameters (N ~ 10^4–10^5, K ~ 10^3), log N is approximately 10–12, meaning K exceeds log N by orders of magnitude. The entire mean-field theory—including the balanced state equations, the autocorrelation self-consistency equation, and the stability analysis—rests on this factorization. The paper does not quantify the error introduced by input correlations when K is not small relative to log N, nor does it provide direct network simulations validating the mean-field predictions (m_k, q_k, autocorrelation functions) at the K and N values used in the figures. It would be helpful to include at least one systematic comparison between analytical predictions and direct simulation results at cortically realistic parameter values, or to provide explicit bounds on the correction terms arising from input correlations as a function of K and N.

**Characterization of Chaos via an Infinite Lyapunov Exponent Conflates Discreteness with Dynamical Sensitivity**

Section 8 and equation 8.6 conclude that the maximum Lyapunov exponent λ_L is infinite in the balanced state, based on the observation that the distance metric D_k grows from zero at a rate proportional to √D_k, implying D_k ~ t² (algebraic) rather than D_k ~ e^{λt} (exponential) growth. The paper attributes this to 'the discreteness of the degrees of freedom' and 'infinitely high microscopic gain,' but this argument conflates the non-smooth behavior of the binary threshold function with genuine exponential sensitivity to initial conditions—the standard definition of chaos. An infinite Lyapunov exponent is not a conventional characterization of chaos and does not distinguish the balanced state from a system exhibiting transient sensitivity without a true chaotic attractor. The authors themselves acknowledge the argument is 'technically inapplicable' to discrete systems, yet the 'chaotic' label is used throughout without qualification. It would be helpful to either provide a numerical measurement of the divergence rate of nearby trajectories as a function of N (demonstrating expected scaling toward a finite positive Lyapunov exponent), or to clearly distinguish the paper's notion of sensitivity from the standard definition and qualify the chaotic characterization accordingly.

**Stationarity of the Autocorrelation Function Is Assumed but Not Verified in the Chaotic Regime**

The derivation of the autocorrelation self-consistency equation (5.17) and its extension to the overlap equation (8.4) both assume that the network has reached a stationary state in which time-averaged quantities are well-defined and the joint distribution of inputs at two different times is Gaussian with a covariance determined by q_k(τ) itself. This Gaussian closure is justified at equal times by the central limit theorem, but the joint distribution of inputs at times t and t+τ is Gaussian only if presynaptic activities are jointly Gaussian across time—an assumption imposed rather than derived. More fundamentally, Section 8 simultaneously argues that the balanced state is chaotic, with diverging trajectories, yet the autocorrelation derivation requires ergodicity and stationarity of the autocorrelation function. The paper does not verify that time averages ⟨σ_k^i(t)⟩ converge, that q_k(τ) is independent of the reference time t, or that the self-consistent integral equation 5.17 has a unique, stable fixed-point solution. It would be helpful to demonstrate numerically that the iteration converges to a unique solution and that the autocorrelation function measured in simulation matches the self-consistent prediction, thereby confirming that the chaotic attractor supports well-defined stationary statistics.

**Stability Analysis Covers Only Macroscopic Rate Dynamics and Leaves Intermediate Perturbation Regimes Unaddressed**

The local stability analysis in Section 6.1 linearizes only the two macroscopic population-rate equations around the balanced fixed point, finding eigenvalues of order √K, but does not include perturbations in the second-moment variable q_k or any microscopic fluctuation modes. It is not shown that perturbations in q_k are slaved to those in m_k or that all modes of the full infinite-dimensional system are stable under the same condition τ < τ_L. The global stability analysis in Section 6.2 approximates H(−u_k/√α_k) ≈ Θ(u_k) on the grounds that large perturbations destroy balance, but this approximation requires |u_k|/√α_k ≫ 1 and is invalid for intermediate perturbations of order √α_k, leaving a gap between the local linearized and global Heaviside regimes. Neither analysis addresses whether attractors could exist in this intermediate regime. Furthermore, the paper does not clearly delineate that the stability conditions guarantee only macroscopic rate convergence while the microscopic state remains chaotic—a distinction crucial for biological interpretation. It would be helpful to extend the linearization to include q_k dynamics, provide a piecewise analysis covering the intermediate perturbation regime, and explicitly state that stability conditions pertain to order-parameter dynamics rather than microscopic trajectories.

**Balanced State Conditions Are Shown to Be Sufficient but Not Necessary, Leaving the Uniqueness Claim Incomplete**

Section 4 derives conditions (equations 4.9–4.10) stated to 'eliminate all possible unbalanced states,' but the paper checks only specific unbalanced solutions (m_E = 0 and m_E = m_I = 1) rather than providing a systematic enumeration of all fixed-point configurations of the mean-field equations for arbitrary m_E, m_I ∈ [0,1]. Mixed cases where one population saturates while the other does not, and the case m_I = 0 with m_E > 0, are not fully analyzed. Without a complete bifurcation analysis of the two-dimensional fixed-point system, the claim that the balanced solution is the unique non-trivial attractor under the stated conditions is not fully established. This matters because the paper's central robustness claim depends on the absence of competing attractors. It would be helpful to provide either a complete fixed-point analysis covering all boundary cases or a proof by exhaustion that all configurations with m_k = 0 or m_k = 1 for any population are excluded under equations 4.9–4.10.

**Key Comparisons with Experiment and with the Weak-Synapse Scenario Lack Quantitative Rigor**

Section 7.3 compares the theoretically predicted firing rate distribution with experimental data from prefrontal cortex of a behaving monkey, but no quantitative fit or goodness-of-fit measure is provided, the applicability of a homogeneous random-connectivity model to prefrontal cortex during active behavior is not justified, and the mean rate of 15.8 Hz in the experimental data is not obviously in the low-rate regime (m_k ≪ 1) required for the approximations in Section 7.2. Section 10.2 contrasts the strong-synapse and weak-synapse scenarios qualitatively, but the weak-synapse analysis is presented only descriptively with a single numerical example and a citation to an unpublished manuscript; no mean-field equations, stability criteria, or autocorrelation predictions are provided for the weak-synapse case to enable rigorous comparison. Similarly, the paper does not provide systematic bounds on how large K must be for the large-K predictions to be quantitatively accurate in the biologically relevant low-rate regime. It would be helpful to either provide quantitative fits with confidence intervals for the experimental comparison, or to explicitly qualify it as illustrative, and to include at minimum the mean-field fixed-point equations and leading-order stability condition for the weak-synapse scenario to make that comparison self-contained.

**Status**: [Pending]

---

## Detailed Comments (11)

### 1. Connection probability uses postsynaptic pool size instead of presynaptic

**Status**: [Pending]

**Quote**:
> The connection between the $i$th postsynaptic neuron of the $k$th population and the $j$th presynaptic neuron of the $l$th population, denoted $J_{kl}^{ij}$ is $J_{kl}/\sqrt{K}$ with probability $K/N_{k}$ and zero otherwise. Here $k,l=1,2$. The synaptic constants $J_{k1}$ are positive and $J_{k2}$ negative. Thus, on average, $K$ excitatory and $K$ inhibitory neurons project to each neuron.

**Feedback**:
It would be helpful to verify the connection probability index. The expected number of inputs a neuron in postsynaptic population k receives from presynaptic population l is N_l × (K/N_k). This equals K only when N_l = N_k. For an 80/20 excitatory-inhibitory split (N_1 = 4N_2), the fan-in from the inhibitory population to an excitatory neuron would be N_2 × (K/N_1) = K/4, directly contradicting the stated claim that 'on average, K excitatory and K inhibitory neurons project to each neuron.' The correct probability should be K/N_l, yielding expected fan-in N_l × (K/N_l) = K regardless of relative population sizes. Readers might note that rewriting 'K/N_{k}' as 'K/N_{l}' resolves this inconsistency.

---

### 2. Index mismatch between left and right sides of equation (1)

**Status**: [Pending]

**Quote**:
> $\sigma_{k}^{j}(t)=\Theta(u_{k}^{i}(t)),$ (1)

**Feedback**:
Equation (1) has sigma_k^j(t) on the left-hand side (superscript j) but u_k^i(t) on the right-hand side (superscript i). In equation (2), the input is consistently written as u_k^i, suggesting the left-hand side of (1) should also carry superscript i. As written, the equation appears to say that the state of neuron j is determined by the input to neuron i. It would be helpful to rewrite equation (1) as sigma_{k}^{i}(t) = Theta(u_{k}^{i}(t)) to make the neuron index consistent on both sides.

---

### 3. Variance derivation references wrong equation number

**Status**: [Pending]

**Quote**:
> Observing that $[(J_{kl}^{ij}\sigma_{l}^{j}(t))^{2}]=J_{kl}^{2}m_{l}/N$, whereas $[(J_{kl}^{ij}\sigma_{l}^{j}(t))]^{2}=J_{kl}^{2}m_{l}^{2}K/N^{2}$, which is negligible, one obtains equation 10.

**Feedback**:
The derivation computes the variance alpha_k: each presynaptic neuron j in population l contributes J_{kl}^2 m_l/N_l, summing over N_l neurons gives J_{kl}^2 m_l per population, and summing over l=1,2 yields alpha_k = m_E + J_k^2 m_I, which matches the equation defining alpha_k (labeled 12 in the paper). Equation 10 is the mean input u_E, an entirely different quantity. The reference 'one obtains equation 10' appears to be a mislabeling. It would be helpful to correct the cross-reference to the appropriate equation number for alpha_k.

---

### 4. Inner sum upper limit N_i should be N_l in equation 14

**Status**: [Pending]

**Quote**:
> $\alpha_{k}(t)=[(\delta u_{k}^{i}(t))^{2}]=\sum_{l,l^{\prime}=1}^{2}\,\sum_{j,j^{\prime}=1}^{N_{i}}[\,(\,\delta(J_{kl}^{ij}\sigma_{l}^{j}(t))\,)^{2}\,],$

**Feedback**:
The inner sum is over presynaptic neurons j in population l, so its upper limit should be N_l (the size of the l-th presynaptic population), not N_i (which is a neuron index, not a population size). The derivation immediately following uses the fact that there are N_l presynaptic neurons in population l, each connected with probability K/N_l, to obtain the per-neuron contribution J_{kl}^2 m_l/N_l; summing N_l such terms yields J_{kl}^2 m_l. If the upper limit were literally N_i, the derivation would be dimensionally inconsistent. Additionally, the double sum over (l,l') and (j,j') implies cross-terms, but the summand involves only indices l and j; it would be helpful to add a sentence explaining that cross-terms vanish by independence of the random connectivity variables.

---

### 5. Two distinct results share the same equation label in Section 7

**Status**: [Pending]

**Quote**:
> $H(x)\approx\frac{\exp(-x^{2}/2)}{\sqrt{2\pi}\left|x\right|}$ (14)
> 
> to obtain
> 
> $h(m)\approx-\sqrt{2|\log m|}.$ (14)

**Feedback**:
Both the large-|x| asymptotic for H and the resulting inversion h(m) ≈ −√(2|log m|) are assigned label (14). These are logically distinct steps: from H(−h) ≈ exp(−h²/2)/(√(2π)|h|) = m, taking logarithms gives log m ≈ −h²/2 − ½log(2π) − log|h|, yielding h ≈ −√(2|log m|) to leading order. Sharing one label makes any cross-reference to 'equation 14' ambiguous. It would be helpful to assign distinct labels to these two equations and renumber subsequent equations accordingly.

---

### 6. Width of rate distribution scaling inconsistent with equation 5.14

**Status**: [Pending]

**Quote**:
> Equation 5.14 implies that when the mean activity $m_{k}$ decreases, the width of the distribution is proportional to $(m_{k})^{3/2}$; it decreases faster than the mean $m_{k}$.

**Feedback**:
From equation 5.14, q_k = m_k^2 + O(m_k^2 |log m_k|), so the variance of the rate distribution is q_k − m_k^2 = O(m_k^2 |log m_k|). The standard deviation (width) is therefore proportional to m_k |log m_k|^{1/2}, not m_k^{3/2}. For the width to scale as m_k^{3/2}, the variance would need to scale as m_k^3, but m_k^2 |log m_k| dominates m_k^3 as m_k → 0. The qualitative conclusion that the width decreases faster than m_k is correct, but the stated exponent 3/2 appears inconsistent with equation 5.14. It would be helpful to rewrite 'the width of the distribution is proportional to (m_k)^{3/2}' as 'the width of the distribution is proportional to m_k |log m_k|^{1/2}.'

---

### 7. Standard deviation of Poisson input stated incorrectly in Appendix A

**Status**: [Pending]

**Quote**:
> The average values of $n_E$ and $n_I$ satisfy $\langle n_k \rangle = m_k K$. The standard deviations $\sigma(n_E)$ and $\sigma(n_I)$ are given by $\sigma(n_k) = m_k K$.

**Feedback**:
From equation A.6, p_l(n) is Poisson with parameter λ = m_l K. For a Poisson distribution, Var(n_k) = m_k K and therefore σ(n_k) = √(m_k K). The sentence stating σ(n_k) = m_k K is inconsistent with the immediately following variance statement: if σ = m_k K then Var = (m_k K)², contradicting Var = m_k K. The downstream equations are unaffected since the variance contribution to α_k is (J_{kl}/√K)² × Var(n_l) = (J_{kl}²/K) × m_l K = J_{kl}² m_l, correctly yielding equation A.9. It would be helpful to rewrite 'σ(n_k) = m_k K' as 'σ(n_k) = √(m_k K).'

---

### 8. Integration variable wrong in exponent of equation (4), Appendix B

**Status**: [Pending]

**Quote**:
> $m_{k}(t)=\frac{1}{\tau_{k}}\int_{0}^{\infty}dt^{i}e^{-t/\tau_{k}}F_{k}(m_{E}(t-t^{i}),m_{I}(t-t^{i})),$ (4)

**Feedback**:
Substituting R_k(τ) = τ e^{−τ/τ_k}/τ_k² into equation (3) and switching integration order yields m_k(t) = (1/τ_k) ∫₀^∞ dt' e^{−t'/τ_k} F_k(m_E(t−t'), m_I(t−t')). The exponential decay must be in the dummy integration variable t' (written t^i), not in the global time argument t of m_k(t). As written, e^{−t/τ_k} is a constant with respect to the integration and would factor out, making the expression structurally inconsistent with the convolution form. It would be helpful to rewrite e^{−t/τ_k} as e^{−t^i/τ_k} in equation (4).

---

### 9. Cross-correlation scaling O(1/sqrt(K)) for connected pairs asserted without derivation

**Status**: [Pending]

**Quote**:
> The maximal value of the cross-correlations occurs for pairs that are directly connected, and this cross-correlation is of the order of the strength of the synapse, $O(1/\sqrt{K})$. Thus, chaos in this state is the result of instability in local degrees of freedom, similar to chaos in asymmetric spin glasses and neural networks.

**Feedback**:
The claim that pairwise cross-correlations for directly connected neurons are O(1/√K) is stated as a result but is not derived anywhere in the paper. Section 5.2 derives only autocorrelations and concludes that cross-correlations are 'very small,' without providing the O(1/√K) scaling for connected pairs. Since this O(1/√K) cross-correlation is central to the classification of asynchronous chaos and distinguishes it from the O(1) cross-correlations of synchronized chaos, it would be helpful to add a brief derivation or a precise reference to the equation in Section 5 that establishes this scaling.

---

### 10. Frozen-state stability asserted without derivation in Section 5

**Status**: [Pending]

**Quote**:
> Equations 5.12 have two solutions: an unstable solution with $q_{k}=m_{k}$, corresponding to a frozen state, and a stable solution, $(m_{k})^{2}<q_{k}<m_{k}$, which corresponds to a temporally fluctuating state.

**Feedback**:
The paper asserts that the frozen solution q_k = m_k is unstable and the fluctuating solution is stable, but provides no derivation. Stability of fixed points of the self-consistency equation 5.12 requires analyzing the derivative of the right-hand side with respect to q_k at each solution and showing it is less than 1 in magnitude for the stable branch and greater than 1 for the unstable branch — a non-trivial calculation depending on the specific form of H and the parameters u_k, α_k, β_k. It would be helpful to add a brief derivation or appendix reference showing that d/dq_k of the integral in equation 5.12 satisfies the appropriate inequality at each fixed point.

---

### 11. Claim that microscopic state locks to inhomogeneous input contradicts chaotic characterization

**Status**: [Pending]

**Quote**:
> preliminary analysis (van Vreeswijk & Sompolinsky, 1998) shows that in the case of spatially inhomogeneous input fluctuations, the microscopic state of the network will tightly lock to the stimulus temporal variations.

**Feedback**:
This claim sits in direct tension with the paper's central result that the balanced state is chaotic, with sensitive dependence on initial conditions and diverging microscopic trajectories (Section 8). In a chaotic system, tight locking of the microscopic state to an external drive requires the drive to suppress the chaotic instability, yet the paper does not explain the mechanism by which spatial inhomogeneity achieves this, nor does it quantify what 'tightly locked' means relative to the divergence rate characterized in Section 8. Since this claim rests entirely on an unpublished preliminary analysis, it would be helpful to add a sentence explaining the suppression mechanism or explicitly qualify the claim as speculative pending the full analysis in the cited 1998 reference.

---
