# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 3/3/2026, 8:59:22 PM
**Domain**: Example
**Taxonomy**: Demo
**Filter**: Active comments

---

## Overall Feedback

Here are some high-level reactions to the text.


**Outline**

The paper proceeds in three main observational stages. First, it introduces a network model characterized by sparse, random connectivity and strong synaptic weights. Second, it develops a mean-field theory solution to show how these networks naturally settle into a "balanced state," where internal inhibition dynamically cancels strong external excitation. Third, the text characterizes the spatiotemporal statistics of this state—arguing for an asynchronous chaotic regime—and concludes by analyzing the stability conditions and the resulting capability for fast tracking of time-dependent inputs.


**The domain of validity for the mean-field description**

The central results regarding the existence of the balanced fixed point, rate distributions, and fast tracking rely heavily on the dynamic mean-field formulation and the Gaussian-input approximation. In the current exposition, the justification for these approximations often rests on heuristic arguments, such as the neglect of activity–connectivity correlations, or is deferred to the appendices. A reader skeptical of the $N \to \infty$ limit might find the argument more persuasive if the main text explicitly defined the precise large-$N$, large-$K$ conditions required for these closures to hold. Furthermore, comparing the mean-field predictions directly to microscopic simulations of finite-size networks would help confirm that the balanced regime is realizable in networks of finite order.


**Distinguishing deterministic chaos from irregularity**

A conceptual pillar of the work is the assertion that intrinsic dynamics generate "deterministic chaos" rather than simply high-dimensional irregularity. The divergence analysis currently presented, which yields an infinitely large Lyapunov exponent, appears to depend on the singular Heaviside nonlinearity. This leaves open the question of whether this behavior persists in finite-$N$ networks or under biologically plausible smoothing of the transfer function. To substantiate the claim of true chaos, it would be beneficial to demonstrate a positive, finite Lyapunov exponent in a differentiable system or through numerical sensitivity measures in a deterministic finite update scheme.


**Quantifying the asynchronous nature of the state**

The narrative places significant weight on the distinction between the "asynchronous chaotic state" described here and prior "synchronized chaotic states." The text asserts that spatial cross-correlations are weak and vanish in the large system limit. However, the analytic focus remains primarily on single-neuron and population statistics, without an explicit derivation of cross-neuron correlation functions ($C_{ij}(\tau)$) or their scaling with $N$ and $K$. Since the absence of synchrony is a defining feature of the proposed regime, deriving these correlations or plotting their distributions from simulation would solidify the distinction from synchronized states.


**Mapping parameter inequalities to biological values**

The existence and stability of the balanced state rest on specific inequalities regarding synaptic strengths and external drives, specifically the scaling of $J_{kl}$ and the dominance of external input over thresholds. For an audience rooted in physiology, it may be difficult to gauge whether conditions like $E/I > J_E/J_I > 1$ are naturally satisfied by cortical circuits. An explicit mapping of these dimensionless conditions to estimated physiological values—such as PSP amplitudes and membrane time constants—would help ground the theoretical constraints in biological reality.


**Robustness of the operating regime**

Related to the parameter mapping is the issue of sensitivity. The fast-tracking property and the stability of the balanced fixed point appear derived under specific bounds. Readers may wonder how the system behaves when these ratios are perturbed. Demonstrating that the qualitative features of the balanced asynchronous state survive moderate variations in synaptic ratios or input scaling would reassure readers that the mechanism is robust enough to function in the variable environment of the cortex.

**Status**: [Pending]

---

## Detailed Comments (12)

### 1. Inconsistent general formula for the rate distribution

**Status**: [Pending]

**Quote**:
> In general, for small $\mathrm{m}_{\mathrm{k}}$, a threshold distribution $\mathrm{P}(\theta)$ will yield a rate distribution $\rho_{\mathrm{k}}$ for population k that is given by $$\rho_{\mathrm{k}}(\mathrm{m})=\sqrt{2 \pi} \mathrm{P}\left(-\sqrt{\alpha_{\mathrm{k}}}\left(\mathrm{h}(\mathrm{m})+\tilde{\mathrm{h}}_{\mathrm{k}}\right)\right) \mathrm{e}^{\mathrm{h}^{2}(\mathrm{~m}) / 2}$$ where $\tilde{\mathrm{h}}_{\mathrm{k}} \equiv \mathrm{h}\left(\mathrm{m}_{\mathrm{k}}\right)$ is determined by $$\int \mathrm{dm} \mathrm{~m} \rho_{\mathrm{k}}(\mathrm{m})=\mathrm{m}_{\mathrm{k}}$$

**Feedback**:
Toward the end of section 7.2 the general expression for the rate distribution, ρ_k(m)=√2π P(-√α_k[h(m)+h̃_k])exp[h(m)^2/2], appears inconsistent with the standard change-of-variables relation between a threshold distribution P(θ) and the induced rate distribution. From m = H((θ-u_k)/√α_k) and the definition m=H(-h(m)), one obtains the inverse mapping θ(m)=u_k-√α_k h(m) and the Jacobian |dθ/dm|=√2πα_k exp[h(m)^2/2]. This yields ρ_k(m)=√2πα_k P(u_k-√α_k h(m))exp[h(m)^2/2]. Compared with this, equation 7.15 is missing the factor √α_k in the prefactor (the Jacobian) and replaces the general dependence on u_k by the specific combination -√α_k(h(m)+h̃_k), which corresponds to assuming a particular relation between u_k and h̃_k=h(m_k). It would be important to correct equation 7.15 so that it includes the appropriate √α_k factor and expresses the argument of P in terms of the actual mean input u_k, with any approximate identification of u_k with h̃_k stated explicitly and restricted to the regimes where it is valid. This would bring the general formula for ρ_k(m) into line with the underlying mapping from thresholds to rates.

---

### 2. Apparent contradiction on fast response to stimuli in Sec. 10.3

**Status**: [Pending]

**Quote**:
> This may be related to the fast tracking predicted in our model. The fact that our model does not respond quickly to a sudden switching of the stimulus (see Figure 13) is probably a result of the dynamics of binary neurons. However, the switching time constants observed in Tsodyks and Sejnowski (1995) is of the same order as the single-cell integration time constant, while the fast tracking should occur on a much shorter time constant.

**Feedback**:
The statement that "our model does not respond quickly to a sudden switching of the stimulus (see Figure 13)" seems inconsistent with the analysis and interpretation given earlier in Section 9, where Figure 13 is used to illustrate fast tracking on a timescale of order τ/√K, much shorter than the single-cell time constant. Because that fast tracking is presented as a principal functional result, having the Discussion explicitly claim the model "does not respond quickly" while referring to the same figure is confusing. It would help to clarify exactly what stimulus regime is meant by "sudden switching" here (e.g., large versus small changes, or pattern changes rather than amplitude) and to adjust the wording so it does not appear to negate the fast-tracking behavior previously derived and demonstrated.

---

### 3. Clarification on the mean-field theory's regime of validity

**Status**: [Pending]

**Quote**:
> The mean-field theory is exact in the limit of large network size, N, and $1 \ll \mathrm{~K} \ll \mathrm{~N}$. In section 4 the behavior of the population rates in the balanced state is studied. Section 5is devoted to the spatial and temporal distribution of activity within the network.

**Feedback**:
In several places the paper uses different formulations for the asymptotic regime underlying the mean-field theory: the Introduction states that the theory is "exact in the limit of large network size, N, and $1 \ll K \ll N$," Section 3 emphasizes a limit with $K$ fixed as $N \to \infty$ followed by a large-$K$ approximation, and Appendix A.1 notes that the uncorrelated-input assumption "holds rigorously provided that $K \ll \log N_k$" (citing Derrida et al.). At first reading it is not entirely clear how these conditions are meant to fit together, nor in which precise sense the mean-field description is "exact" as opposed to being a controlled approximation. Clarifying the intended ordering of limits (first $N \to \infty$ at fixed $K$, then large $K$), the role of the $K \ll \log N_k$ condition as a sufficient rigorous criterion rather than a general scaling assumption, and what is assumed when one informally writes $1 \ll K \ll N$ would help readers understand more precisely the regime of validity of the subsequent large‑$K$ results.

---

### 4. Incorrect variance term in q_k expression (sec:Inhomogeneous Thresholds)

**Status**: [Pending]

**Quote**:
> In this case, the spatial fluctuations in the inputs (relative to thresholds) consist of two gaussian terms. One is induced by the random connectivity and has a variance $\alpha_{\mathrm{k}}$, and the other is induced by the thresholds and has a variance $\Delta$. The balance conditions that determine the population rates (equations 4.3 and 4.4) still hold. In addition, $$\mathrm{m}_{\mathrm{k}}=\mathrm{H}\left(\frac{-\mathrm{u}_{\mathrm{k}}}{\sqrt{\alpha_{\mathrm{k}}+\Delta^{2}}}\right)$$ which determines $\mathrm{u}_{\mathrm{k}}$, and $$\mathrm{q}_{\mathrm{k}}=\int \mathrm{D} \mathrm{x}\left[\mathrm{H}\left(\frac{-\mathrm{u}_{\mathrm{k}}-\sqrt{\Delta+\beta_{\mathrm{k}}} \mathrm{x}}{\sqrt{\alpha_{\mathrm{k}}-\beta_{\mathrm{k}}}}\right)\right]^{2}$$

**Feedback**:
The description of the threshold-induced variance and the expression for q_k in section 7.1 are internally inconsistent with the definition of P(θ) in equation 7.3. There P(θ)= [Δ√2π]^{-1}exp[-(θ/Δ)^2/2], so Δ is the standard deviation and the variance is Δ^2. Yet the text refers to a variance Δ, and equation 7.5 uses √(Δ+β_k) as the prefactor of the quenched Gaussian term. Since the quenched contributions from thresholds and from connectivity are independent Gaussians with variances Δ^2 and β_k, their sum must have variance Δ^2+β_k, leading to a factor √(Δ^2+β_k). I initially had trouble reconciling this with the subsequent low–rate analysis because of this variance mismatch. However, the later conclusion that q_k ≈ m_k and that the state becomes effectively frozen at low mean rates relies only on the dominance of threshold heterogeneity over α_k,β_k, so it still follows once the combined quenched variance is written correctly. It would be helpful if the text and equation for q_k were adjusted to use Δ^2 consistently as the variance of the threshold distribution.

---

### 5. Inconsistent definition of connection probability in Sec. 2

**Status**: [Pending]

**Quote**:
> The connection between the ith postsynaptic neuron of the kth population and the jth presynaptic neuron of the lth population, denoted $\mathrm{J}_{\mathrm{kl}}^{\mathrm{ij}}$, is $\mathrm{J}_{\mathrm{kl}} / \sqrt{\mathrm{K}}$ with probability $\mathrm{K} / \mathrm{N}_{\mathrm{k}}$ and zero otherwise. Here $\mathrm{k}, \mathrm{l}=1,2$. The synaptic constants $\mathrm{J}_{\mathrm{k} 1}$ are positive and $\mathrm{J}_{\mathrm{k} 2}$ negative. Thus, on average, K excitatory and K inhibitory neurons project to each neuron.

**Feedback**:
The definition of the connection probability in Section 2 seems to contain a subscript error that conflicts with the stated average in-degree and with later mean-field derivations. As written, the text specifies that $J_{kl}^{ij}$ is nonzero "with probability $K/N_k$," i.e. depending on the postsynaptic population size, and then states "Thus, on average, K excitatory and K inhibitory neurons project to each neuron." For general $N_1$ and $N_2$, a probability $K/N_k$ would give an expected number of inputs from population $l$ equal to $N_l K/N_k$, which equals $K$ only if $N_l=N_k$. Moreover, Appendix A and Section 3 later assume that the number of synapses from population $l$ onto a given neuron is Poisson with mean $K$ (eq. A.6), and use this to derive $u_k=\sqrt{K}\sum_l J_{kl} m_l + \dots$ and $\alpha_k=\sum_l J_{kl}^2 m_l$. Those forms are consistent with a connectivity rule in which each presynaptic neuron in population $l$ connects with probability $K/N_l$, yielding a mean of $K$ inputs from each population, and are not consistent with $K/N_k$. It would therefore be helpful to correct the connectivity definition to make explicit that the connection probability is $K/N_l$ (depending on the presynaptic population size), which matches both the verbal statement about "on average, K excitatory and K inhibitory neurons project to each neuron" and the subsequent mean-field analysis.

---

### 6. Prefactor in the distance dynamics equation (sec:8)

**Status**: [Pending]

**Quote**:
> To find the initial rate of divergence, we expand equation 8.5 for small $\mathrm{D}_{\mathrm{k}}$ and find that to leading order, the distances satisfy $$\tau_{\mathrm{k}} \frac{\mathrm{dD}_{\mathrm{k}}}{\mathrm{dt}}=\frac{2}{\pi} \frac{\mathrm{e}^{-\mathrm{u}_{\mathrm{k}}^{2} / 2 \alpha_{\mathrm{k}}}}{\sqrt{\alpha_{\mathrm{k}}}} \sqrt{\alpha_{\mathrm{k}}-\gamma_{\mathrm{k}}} .$$ Since $\alpha_{\mathrm{k}}-\gamma_{\mathrm{k}} \propto \mathrm{D}_{\mathrm{k}}$, equation 8.9 has a growing solution even if $\mathrm{D}_{\mathrm{k}}(0)=$ 0 . This implies that the Lyapunov exponent $\lambda_{\mathrm{L}}$ is infinitely large in the balanced state.

**Feedback**:
Re-deriving the small-D_k expansion of equation 8.5, i.e., the expansion of the bivariate normal integral as γ_k → α_k, I obtain a different numerical prefactor from the one written in equation 8.9. In particular, for the symmetric case u_k=0, α_k=1, the exact formula for P(Z_1>0,Z_2>0) in terms of the correlation coefficient ρ=γ_k/α_k gives m_k - G(γ_k) = (√2/2π)√(α_k-γ_k) + O((α_k-γ_k)^{3/2}), which would translate into τ_k dD_k/dt = (√2/π)(e^{-u_k^2/(2α_k)}/√α_k)√(α_k-γ_k) rather than the factor 2/π appearing in equation 8.9. It would be helpful to check the small–α_k-γ_k expansion leading to equation 8.9 and adjust the prefactor if necessary. The qualitative conclusion that λ_L diverges hinges only on the √D_k dependence and is unaffected by the precise numerical coefficient.

---

### 7. Discrepancy regarding stability boundaries in Sec. 6.2

**Status**: [Pending]

**Quote**:
> To illustrate the region of stability of the balanced state, we have calculated the phase diagram of the network in terms of two parameters: (1) the inhibitory time constant $\tau$ and (2) the ratio between the external input into the inhibitory population and the external input into the excitatory population. We have chosen to scale $\mathrm{m}_{0}$ so that the excitatory population rate is held fixed. The results areshown in Figure9, where both the local and global stability lines are presented. For these parameters, $\tau_{\mathrm{L}}$ is always smaller than $\tau_{\mathrm{G}}$.

**Feedback**:
The final sentence of the quoted paragraph appears to have the ordering of the two stability boundaries reversed. The figure and the numerical values given for Figure 8 indicate that, for the parameter set used in Figure 9, the dashed curve corresponding to $\tau_{\mathrm{L}}$ lies above the solid curve corresponding to $\tau_{\mathrm{G}}$, and the example $\tau_{\mathrm{L}} = 1.61$, $\tau_{\mathrm{G}} = 1.50$ also has $\tau_{\mathrm{L}} > \tau_{\mathrm{G}}$. This suggests that the phrase "$\tau_{\mathrm{L}}$ is always smaller than $\tau_{\mathrm{G}}$" should state the opposite inequality. Clarifying this wording so that it matches the plotted curves and numerical example would remove a small but definite inconsistency.

---

### 8. Unclear derivation of q_k for bounded thresholds

**Status**: [Pending]

**Quote**:
> Thus, the population rates adjust themselves so that synapticinputisslightly below the smallest threshold in the population, $\theta_{\mathrm{k}}-\mathrm{D} / 2$; see equation 3.8. The small gap between the mean synaptic input and the minimal threshold is such that the temporal fluctuations of the network, with the low variance $\alpha_{\mathrm{k}}$, are sufficient to bring the neurons to threshold levels. Indeed, analyzing the rate distribution for this case, we find that it is unimodal with width $\sqrt{\mathrm{q}_{\mathrm{k}}}$, where $$\mathrm{q}_{\mathrm{k}} \propto \Delta \alpha_{\mathrm{k}}^{3 / 2}$$

**Feedback**:
I initially had trouble seeing how the scaling relation q_k ∝ Δα_k^{3/2} in the bounded–threshold case follows from the preceding equations. Equation 7.9 gives an exact expression for m_k, and later equations (7.12–7.14) provide an explicit asymptotic form for ρ_k(m) and the cutoffs m_±, but the steps connecting these to the stated dependence of q_k on Δ and α_k are not shown. Since this scaling is used to summarize the breadth of the distribution in the low–rate regime, it would be helpful to indicate more explicitly how it is derived from eq. 7.9 (for example by sketching how q_k=∫dm m^2ρ_k(m) is evaluated using the asymptotic ρ_k(m)), or to point to a calculation where this is worked out. That would make it easier for readers to verify the argument and to see how logarithmic factors and the dependence on Δ enter.

---

### 9. Variance of inhibitory input in Sec 5.3

**Status**: [Pending]

**Quote**:
> The time average of the total excitatory (inhibitory) component is itself sampled from a gaussian distribution with a mean $\sqrt{\mathrm{K}}\left(\mathrm{m}_{\mathrm{E}}+\mathrm{Em}_{0}\right)\left(\sqrt{\mathrm{K}} \mathrm{~J}_{\mathrm{E}} \mathrm{m}_{\mathrm{I}}\right)$ and a variance $\mathrm{q}_{\mathrm{E}}\left(\mathrm{J}_{\mathrm{E}} \mathrm{q}_{\mathrm{I}}\right)$. The time-dependent fluctuations of the total excitatory (inhibitory) inputhave atime-delayed au-

**Feedback**:
In the description of the Gaussian sampling in Section 5.3, the variance of the time-averaged inhibitory component is written as $J_{\mathrm{E}} q_{\mathrm{I}}$. Using the general expression for the quenched variance, $\beta_{\mathrm{E}} = q_{\mathrm{E}} + J_{\mathrm{E}}^{2} q_{\mathrm{I}}$, and applying the same reasoning restricted to the inhibitory contribution alone, this variance should be $J_{\mathrm{E}}^{2} q_{\mathrm{I}}$. This looks like a missing square on $J_{\mathrm{E}}$ rather than a substantive problem, but it would be helpful to correct it for consistency with the earlier formulas.

---

### 10. Clarity of the model's scaling argument in the Introduction

**Status**: [Pending]

**Quote**:
> An essential ingredient of our model is the introduction of strong connections among the units. A cell is connected, on the average, to K other cells, and K is large. However, the gap between the threshold of the cell and its resting potential is only of the order of $\sqrt{\mathrm{K}}$ excitatory inputs. Thus, the network will saturate unless a dynamically developed balance between the excitatory inputs and the inhibitory inputs to a cell emerges.

**Feedback**:
I initially had trouble with the scaling argument in this introductory paragraph because the statement "the gap between the threshold of the cell and its resting potential is only of the order of $\sqrt{K}$ excitatory inputs" appears before the synaptic-strength scaling is specified. However, reading on to section 2 makes clear that the formal model assumes thresholds of order one and synaptic strengths of order $1/\sqrt{K}$, so that the rest–threshold gap in units of a single EPSP is indeed $O(\sqrt{K})$, and the saturation/balance argument is consistent. That said, this is a central conceptual point, and the introduction is the first place the reader encounters it. It might improve the ease of first-pass comprehension if the authors briefly foreshadow here that, in the detailed model, individual synaptic strengths scale as $1/\sqrt{K}$ while thresholds remain $O(1)$, and that this is what underlies the statement that the threshold corresponds to $O(\sqrt{K})$ excitatory inputs and therefore a vanishing fraction of the $K$ available inputs.

---

### 11. Standard deviation of input counts in Appendix A.1

**Status**: [Pending]

**Quote**:
> Equations A. 4 through A. 6 define the mean-field equations for the population activity levels for finite $K$. The average values of $n_{E}$ and $n_{I}$ satisfy $\left\langle\mathrm{n}_{\mathrm{k}}\right\rangle=\mathrm{m}_{\mathrm{k}} \mathrm{K}$. The standard deviations $\sigma\left(\mathrm{n}_{\mathrm{E}}\right)$ and $\sigma\left(\mathrm{n}_{\mathrm{I}}\right)$ are given by $\sigma\left(\mathrm{n}_{\mathrm{k}}\right)=\mathrm{m}_{\mathrm{k}} \mathrm{K}$. In the large K limit, the probability distributions $\mathrm{p}_{\mathrm{k}}(\mathrm{n})$ can be replaced by gaussian distributions.

**Feedback**:
In Appendix A.1 there is a small inconsistency in the stated statistics of the number of active inputs n_k. After deriving the Poisson distribution p_l(n) = (m_l K)^n/n! e^{-m_l K}, the text says "The standard deviations σ(n_E) and σ(n_I) are given by σ(n_k) = m_k K." For this Poisson distribution the variance is Var(n_k)=K m_k, so the standard deviation should be σ(n_k)=√(K m_k), not m_k K. The next sentence correctly identifies the mean and variance as [n_k]=[(δn_k)^2]=K m_k, and the subsequent derivation of α_k uses this variance correctly. It would be helpful to correct the expression for σ(n_k) to avoid this local contradiction.

---

### 12. Sign convention for quenched noise in Sec 5

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> q_{\mathrm{k}}=\int \mathrm{Dx}\left[\mathrm{H}\left(\frac{-\mathrm{u}_{\mathrm{k}}+\sqrt{\beta_{\mathrm{k}}} \mathrm{x}}{\sqrt{\alpha_{\mathrm{k}}-\beta_{\mathrm{k}}}}\right)\right]^{2} ... \times \exp \left(-\mathrm{t} / \tau_{\mathrm{k}}\right) \int \mathrm{Dx}\left[\mathrm{H}\left(\frac{-\mathrm{u}_{\mathrm{k}}-\sqrt{\beta_{\mathrm{k}}(\mathrm{t}+\tau)} \mathrm{x}}{\sqrt{\alpha_{\mathrm{k}}-\beta_{\mathrm{k}}(\mathrm{t}+\tau)}}\right)\right]^{2}.

**Feedback**:
I initially had trouble with the opposite signs of the $\sqrt{\beta_k}\,x$ term in equations 5.12 and 5.17, which at first seemed to imply different conventions for the quenched Gaussian variable $x$. However, since $x$ is a standard normal with symmetric measure $Dx$, the sign of this term can always be absorbed by redefining $x \to -x$, and the resulting integrals (and hence the statistics of $m_k^i$ and $q_k(\tau)$) are unchanged. If you think readers might dwell on this point, it could be helpful to mention explicitly that the sign of the quenched Gaussian factor is arbitrary.

---
