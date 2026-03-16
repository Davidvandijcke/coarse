# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 03/16/2026
**Domain**: natural_sciences/neuroscience
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a mean-field theory for sparse balanced networks of binary neurons, analyzing how excitatory and inhibitory inputs balance to produce irregular, low-rate activity. Using Gaussian approximations for synaptic input statistics, the authors derive conditions for the existence and stability of balanced states, characterize the dynamics through Lyapunov exponents, and analyze the network's capacity to track time-varying inputs. The main results include stability boundaries for global attractors, predictions for firing rate distributions in low-rate regimes, and theoretical bounds on input tracking speeds, supported by numerical simulations for networks with large in-degree $K$.

Below are the most important issues identified by the review panel.

**Mean-field validity and finite-size effects in simulations**

The mean-field theory assumes uncorrelated inputs requiring the restrictive condition $K \ll \log N$ (Appendix A), yet the paper presents simulation results for $K=1000$ (Figures 3, 8, 9) without verifying that $N$ is exponentially large or quantifying the impact of finite-size correlations. Additionally, Equation 3.12 calculates input variance $\alpha_k$ by assuming negligible correlations between cellular activity and connectivity realizations, but pairwise correlations may persist in finite networks with shared presynaptic inputs. It would be helpful to explicitly state the network size $N$ used in simulations, demonstrate that finite-$N$ correlations do not significantly alter the variance or stability conditions, and quantify the contribution of pairwise correlations to the input statistics for biologically realistic network sizes.

**Characterization of instability and Lyapunov exponent divergence**

Section 8 claims the balanced state exhibits chaos with an 'infinitely large' Lyapunov exponent based on Equation 8.9; however, readers might note that $\tau_k dD_k/dt \propto \sqrt{D_k}$ implies algebraic growth $D_k(t) \propto t^2$ rather than exponential growth $D_k \sim e^{\lambda t}$. Furthermore, for binary neurons with discrete state spaces, the minimum perturbation is finite, suggesting the divergence may reflect the order of limits rather than standard chaotic sensitivity. It would be helpful to clarify whether the instability represents a discontinuous jump rather than exponential chaos, provide a finite characterization of unpredictability for the binary network, and discuss how the algebraic scaling affects predictability timescales compared to exponential divergence.

**Validity of Gaussian approximations for low-rate dynamics**

The mean-field equations (3.3) assume Gaussian input statistics valid when $m_k K \gg 1$, yet the paper extensively analyzes the low-rate regime $m_k \to 0$ (Sections 5.1, 7) where $m_k \sim K^{-1}$ and Poisson statistics become significant. The Gaussian approximation underestimates tail probabilities in this regime, yet quantitative predictions for $K=1000$ (Figure 3) and rate distributions (Equations 7.12–7.14) rely on this approximation without verification via exact combinatorial calculations or Monte Carlo sampling of Poisson inputs. It would be helpful to quantify the approximation errors when $m_k K \sim 1$, provide corrections for Poisson statistics, or bound the impact of non-Gaussian tails on the predicted firing rates and stability boundaries.

**Robustness of balanced states to parameter perturbations**

The existence of balanced states requires strict parameter constraints (Equations 4.9–4.10: $J_E > 1$ and $E/I > J_E/J_I > 1$) representing fine-tuned excitatory-inhibitory balance. The paper does not analyze the robustness of the dynamics to synaptic noise, parameter drift, or deviations from these precise ratios, nor does it propose homeostatic mechanisms to maintain the balance. Without demonstrating the volume of stable parameter space or biological mechanisms to enforce these constraints, the applicability to biological circuits remains unclear. It would be helpful to characterize the sensitivity of the balanced state to parameter perturbations or discuss whether inhibitory plasticity or other homeostatic mechanisms are required to stabilize the network against slow drift in synaptic strengths.

**Rigorous justification of stability and tracking approximations**

The global stability analysis (Section 6.2) employs a heuristic approximation replacing the smooth error function $H$ with a Heaviside step function (Equation 6.4) without establishing that solutions bound the true nonlinear dynamics or that neglected nonlinear terms do not affect the stability boundary $\tau_G$ (Equation 6.6). Similarly, Section 9 derives necessary bounds on input tracking rates (Equation 9.8) without proving sufficiency for the small-deviation approximation or characterizing whether the network simply lags or enters a different dynamical regime when bounds are violated. Furthermore, the fast tracking analysis assumes effectively Markovian synaptic fluctuations while the chaotic dynamics implies complex temporal correlations. It would be helpful to rigorously justify the Heaviside approximation for global stability, establish the sufficiency of the tracking bounds, and verify the fast tracking results through direct simulation with time-dependent inputs.

**Status**: [Pending]

---

## Detailed Comments (14)

### 1. Inconsistent scaling conditions for mean-field validity

**Status**: [Pending]

**Quote**:
> The mean-field theory is exact in the limit of large network size, $N$, and $1\ll K\ll N$.

**Feedback**:
Readers might note that the condition $1 \ll K \ll N$ in the introduction differs from the condition $K \ll \log N$ derived in Appendix A. For example, with $N = 10^6$, the stricter condition requires $K \ll 14$, whereas the paper presents simulation results for $K = 1000$. It would be helpful to reconcile these conditions or clarify that the theory is approximate when $K \gg \log N$.

---

### 2. Inconsistent population scaling in synaptic averages

**Status**: [Pending]

**Quote**:
> The population average $[J_{kl}^{ij}]$ is equivalent to a quenched average over the random connectivity and is therefore equal to $J_{kl}\sqrt{K}/N$, yielding equation 3.5.

**Feedback**:
Readers might note a potential scaling inconsistency between the derived synaptic averages and the mean-field equations. Substituting $[J_{kl}^{ij}] = J_{kl}\sqrt{K}/N$ into equation (3.11) yields $u_k = \sqrt{K}\sum_l (N_l/N)J_{kl}m_l$, whereas equation (3.5) states $u_k = \sqrt{K}\sum_l J_{kl}m_l$. Similarly, the variance calculation requires $[(J_{kl}^{ij})^2] = J_{kl}^2/N$ to obtain $\alpha_k = \sum_l (N_l/N)J_{kl}^2 m_l$, but equation (3.6) shows $\alpha_k = \sum_l J_{kl}^2 m_l$. It would be helpful to verify whether the averages should scale with the presynaptic population size $N_l$ rather than the total network size $N$ to maintain consistency with equations (3.5) and (3.6).

---

### 3. Undefined function $h(m_k)$ in finite $K$ equations

**Status**: [Pending]

**Quote**:
> In particular, the finite $K$ equations for the fixed point are
> 
> $Em_{0}+m_{E}-J_{E}m_{I}=(\theta_{E}+\sqrt{\alpha_{E}}h(m_{E}))/\sqrt{K}.$ (4.17)
> $Im_{0}+m_{E}-J_{I}m_{I}=(\theta_{I}+\sqrt{\alpha_{I}}h(m_{I}))/\sqrt{K}.$ (4.18)

**Feedback**:
Readers might note that the function $h(m_k)$ appears in equations 4.17 and 4.18 without being defined in this section. From the structure of these equations, $h(m_k)$ appears to serve as the inverse of the gain function, satisfying $u_k = \theta_k + \sqrt{\alpha_k}h(m_k)$ where $m_k = \Phi((u_k - \theta_k)/\sqrt{\alpha_k})$. It would be helpful to add a definition such as 'where $h(m_k) = \Phi^{-1}(m_k)$ is the inverse of the single-neuron gain function defined in equation 3.7' to ensure the derivation is self-contained.

---

### 4. Boundary case at scale $1/\sqrt{K}$ not addressed

**Status**: [Pending]

**Quote**:
> To determine the stability of the balanced state, we have to study the response of the system to small perturbations in the population activity rates. However, because of the nature of the balanced state, we have to distinguish two scales of perturbations: local perturbations, in which the deviations in the rates are small compared to $1/\sqrt{K}$, and global perturbations, in which these deviations are large compared to $1/\sqrt{K}$.

**Feedback**:
Readers might note that the text distinguishes perturbations small compared to $1/\sqrt{K}$ from those large compared to $1/\sqrt{K}$, but does not address the boundary case where deviations are of order $1/\sqrt{K}$. At this scale, the input perturbation becomes comparable to the neuronal threshold, placing the system in a weakly nonlinear intermediate regime. It would be helpful to explicitly state whether this intermediate regime is excluded from the analysis or to characterize the dynamics at this boundary.

---

### 5. Stability condition incorrectly stated as dependent on time constant

**Status**: [Pending]

**Quote**:
> Requiring that their real part be negative yields a condition on $\tau$ of the form
> 
> $\tau<\tau_{L},$ (6.3)
> 
> where $\tau_{L}$ is of order 1; its precise value depends on the system parameters. Since both $\lambda_{1}$ and $\lambda_{2}$ are of order $\sqrt{K}$, if $\tau<\tau_{L}$, small perturbations will decay with an extremely short time constant of order $1/\sqrt{K}$.

**Feedback**:
Re-deriving the linearized dynamics from equation 6.1 yields eigenvalues $\lambda = (-1 + \sqrt{K}\mu)/\tau$ where $\mu$ are eigenvalues of the matrix $\mathbf{f}$. Since $\tau > 0$, the sign of $\text{Re}(\lambda)$ depends solely on $\text{Re}(-1 + \sqrt{K}\mu)$, independent of $\tau$. It would be helpful to verify whether the stability condition should instead require the eigenvalues of $\mathbf{f}$ to satisfy $\text{Re}(\mu) < 1/\sqrt{K}$, with the time constant $\tau$ affecting only the rate of decay rather than stability itself.

---

### 6. Ambiguity between population-specific time constants and single stability bound

**Status**: [Pending]

**Quote**:
> $\tau_{k}\frac{d}{dt}\delta m_{k}(t)=-\delta m_{k}(t)+\sqrt{K}\sum_{l=1,2}f_{kl}\delta m_{l}(t).$ (6.1)
> 
> Calculating $f_{kl}$ by partial differentiation of the r.h.s. of equation 3.3 yields
> 
> $f_{kl}=\frac{\exp(-u_{k}^{2}/2\alpha_{k})J_{kl}}{\sqrt{2\pi\alpha_{k}}}.$ (6.2)
> 
> Solving equations 6.1 one obtains $\delta m_{k}(t)=\delta m_{k,1}\exp(\lambda_{1}t)+\delta m_{k,2}\exp(\lambda_{2}t)$ where the eigenvalues $\lambda_{1}$ and $\lambda_{2}$ of the 2 by 2 equations (see equations 6.1) are both of order $\sqrt{K}$. Requiring that their real part be negative yields a condition on $\tau$ of the form
> 
> $\tau<\tau_{L},$ (6.3)

**Feedback**:
Readers might note that equation 6.1 indexes the time constant as $\tau_k$, allowing for distinct time constants between populations, whereas equation 6.3 introduces a single symbol $\tau$ without defining its relationship to $\tau_k$. If $\tau_1 \neq \tau_2$, the eigenvalues depend on the matrix $\text{diag}(1/\tau_k)(-\mathbf{I} + \sqrt{K}\mathbf{f})$, and stability cannot be expressed as a simple inequality on a single time constant without specifying the ratio $\tau_1/\tau_2$. It would be helpful to clarify whether identical time constants are assumed or to reformulate condition 6.3 to explicitly involve the time constant ratio.

---

### 7. Undefined dynamics at switching boundaries

**Status**: [Pending]

**Quote**:
> $\tau_{k}\frac{d}{dt}\delta m_{k}(t)=-\delta m_{k}(t)+\Theta(\delta m_{E}-J_{k}\delta m_{I})-m_{k}.$ (6.4)

**Feedback**:
Readers might note that equation 6.4 contains a Heaviside function $\Theta$ with argument $\delta m_E - J_k \delta m_I$, creating switching lines where the dynamics changes abruptly. When trajectories reach the surface where $\delta m_E = J_k \delta m_I$, the value of $\Theta(0)$ is undefined, and standard existence and uniqueness theorems for ODEs do not apply. It would be helpful to specify the treatment of these boundaries (e.g., using the Filippov convex method or stating the specific value assigned to $\Theta(0)$) to ensure the explicit solution is well-defined.

---

### 8. Incorrect scaling in equation 7.10

**Status**: [Pending]

**Quote**:
> To assess the effect of $\Delta$, we analyze equation 7.9 in the low $m_{k}$ limit. In this case, the solution for $u_{k}$ is
> 
> $$
> u _ {k} + \Delta / 2 = O (\sqrt {m _ {k}}). \tag {7.10}
> $$

**Feedback**:
Analyzing the asymptotic behavior for low rates: for the uniform threshold distribution on $[-\Delta/2, \Delta/2]$, let $\delta = -(u_k + \Delta/2)$. When $m_k \ll 1$, using the asymptotic form $H(y) \sim \frac{e^{-y^2/2}}{\sqrt{2\pi}y}$ yields $m_k \sim \frac{\alpha_k^{3/2}}{\Delta \delta^2} e^{-\delta^2/(2\alpha_k)}$, which implies $\delta \sim \sqrt{-2\alpha_k \log m_k}$ (logarithmic scaling) rather than $O(\sqrt{m_k})$. It would be helpful to verify and correct the scaling in equation 7.10 to reflect this logarithmic dependence.

---

### 9. Dimensional inconsistency in equation 7.14

**Status**: [Pending]

**Quote**:
> $$
> m_+ \propto \Delta \sqrt{\alpha_k / |\log(\alpha_k)|} \gg m_k. \tag{7.14}
> $$

**Feedback**:
Readers might note a potential dimensional inconsistency: the quantity $m_+$ represents a firing rate (dimensionless), while the right-hand side $\Delta \sqrt{\alpha_k}$ has dimensions of voltage$^2$ (since $\Delta$ is voltage and $\sqrt{\alpha_k}$ is voltage). From the asymptotic analysis, $m_+ \sim H(\delta/\sqrt{\alpha_k}) \sim \frac{\sqrt{\alpha_k}}{\delta} e^{-\delta^2/(2\alpha_k)}$, and substituting $\delta \sim \sqrt{\alpha_k |\log m_k|}$ yields $m_+ \propto \sqrt{\alpha_k / |\log \alpha_k|}$ without the factor of $\Delta$. It would be helpful to remove $\Delta$ from equation 7.14 to maintain dimensional consistency.

---

### 10. Dimensional inconsistency in low-rate condition

**Status**: [Pending]

**Quote**:
> For fixed $\Delta$, if the mean rates become sufficiently low so that $m_k \ll \Delta$, the intrinsic variances $\alpha_k$ and $\beta_k$ can be neglected compared with $\Delta$

**Feedback**:
Readers might note that the condition $m_k \ll \Delta$ compares a dimensionless firing rate $m_k$ to a threshold standard deviation $\Delta$ with dimensions of voltage. The appropriate condition for neglecting intrinsic variances compared to the threshold variance should compare quantities with identical dimensions, specifically $\alpha_k, \beta_k \ll \Delta^2$. It would be helpful to rewrite the condition as $\alpha_k, \beta_k \ll \Delta^2$ to ensure dimensional consistency.

---

### 11. Cross-correlation scaling for unconnected pairs

**Status**: [Pending]

**Quote**:
> Most of the cross-correlations are of the order $1/N$, where $N$ is the network size. The maximal value of the cross-correlations occurs for pairs that are directly connected, and this cross-correlation is of the order of the strength of the synapse, $O(1/\sqrt{K})$.

**Feedback**:
Readers might note that the claimed $O(1/N)$ scaling for cross-correlations between unconnected neurons may need revision. For a random sparse network with connectivity $K$, two neurons share approximately $K^2/N$ presynaptic inputs. With synaptic strengths $J_{kl} \sim 1/\sqrt{K}$, the covariance of synaptic input scales as $(K^2/N) \cdot (1/\sqrt{K})^2 = K/N$. Assuming the gain of the input-output relation is order unity, the output correlation coefficient should scale as $K/N$ rather than $1/N$. It would be helpful to verify whether the correlation for unconnected pairs should be $O(K/N)$.

---

### 12. Cited experimental evidence contradicts model's requirement for large external input

**Status**: [Pending]

**Quote**:
> Recent experimental findings of Ferster, Chung, and Wheat (1996) in cat primary visual cortex suggest that the input from the lateral geniculate nucleus (LGN) to layer 4 cortical cells are in fact a fraction of the net input.

**Feedback**:
Readers might note a potential tension between the model requirements and the cited experimental evidence. Section 10.2 states that the balanced state requires external input of order $\sqrt{K}$ (much larger than net synaptic input), whereas the cited finding of Ferster, Chung, and Wheat (1996) indicates that thalamic input is only a fraction of the net input. It would be helpful to discuss how the theory applies when external input is small relative to net input, or to clarify the regime in which the balanced state remains applicable.

---

### 13. Missing membrane time constant in relaxation time scale

**Status**: [Pending]

**Quote**:
> If the input is suddenly increased by a small amount, the network rates increase to the rate the network would have in equilibrium if the synaptic strengths were not changed in a time of order $1/\sqrt{K}$ and then, on a much slower time scale, the rates decrease due to the change in the synaptic strengths.

**Feedback**:
Readers might note that the claim of response 'in a time of order $1/\sqrt{K}$' appears dimensionally inconsistent, as $1/\sqrt{K}$ is dimensionless while time has dimensions of seconds. Section 6.1 shows eigenvalues of $O(\sqrt{K}/\tau_k)$, yielding a relaxation time of $O(\tau_k/\sqrt{K})$, and Section 9 derives tracking conditions involving $\tau_k$. It would be helpful to include the membrane time constant $\tau$ (or $\tau_k$) in the expression, rewriting it as 'in a time of order $\tau/\sqrt{K}$'.

---

### 14. Incorrect terminology for input variance in equation A.9

**Status**: [Pending]

**Quote**:
> and standard deviation of the input $\alpha_{k}$
> 
> $$
> \alpha_{k} = \left(J_{kE}\right)^{2} m_{E} + \left(J_{kI}\right)^{2} m_{I}, \tag{A.9}
> $$

**Feedback**:
Re-deriving the statistics of the synaptic input from equation A.3: the variance of the contribution from population $l$ is $\text{Var}\left(\frac{J_{kl}}{\sqrt{K}} n_{l}\right) = \frac{J_{kl}^2}{K} \cdot m_{l}K = J_{kl}^2 m_{l}$. Summing independent contributions yields $\text{Var}(u_k) = J_{kE}^2 m_E + J_{kI}^2 m_I$, matching equation A.9. Furthermore, equation A.7 expresses the noise term as $\sqrt{\alpha_k} x$ where $x$ is a standard normal variable, confirming that $\alpha_k$ represents the variance. It would be helpful to correct the text to describe $\alpha_k$ as the variance rather than the standard deviation.

---
