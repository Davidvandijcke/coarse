# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 03/13/2026
**Domain**: natural_sciences/neuroscience
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper analyzes a binary neural network with strong synapses (J ~ 1/√K) and external drive scaling as √K. Using a mean-field theory in the asymptotic limit of large connectivity K, it predicts a temporally fluctuating 'balanced state' characterized by low, irregular firing. The central claim is that this state is chaotic, exhibits fast tracking of time-varying inputs, and is robust to certain heterogeneities.

Below are the most important issues identified by the review panel.

**Validity of the asymptotic mean-field theory for finite, low-rate biological regimes**

The paper's theoretical framework relies on taking the limits N→∞ and K→∞, with the Gaussian approximation for input statistics justified in this asymptotic regime. Multiple reviewers note that for the biologically relevant case of finite K (e.g., K=1000) and low mean firing rates (m_k ~ 0.01), the condition m_k >> 1/K required for the Gaussian approximation becomes borderline or is violated. This casts doubt on the accuracy of key predictions derived from the mean-field equations, including the rate distribution, autocorrelation functions, and the stability analysis. It would be helpful to quantify the error introduced by the Gaussian approximation for finite K and low m_0, perhaps by comparing the full binomial expression with the Gaussian limit, and to explicitly state the range of K and m_k for which the theory is expected to be accurate.

**Problematic evidence and definition for chaotic dynamics**

The paper's central claim of a 'chaotic balanced state' rests heavily on an analysis showing an 'infinitely large' Lyapunov exponent, derived from the scaling of eigenvalues in the linearized mean-field equations. Reviewers unanimously argue that this divergence is an artifact of the continuous Gaussian approximation applied to a system with discrete binary dynamics and an infinitely high gain at threshold. In the actual discrete network, the distance between trajectories is bounded, and the claimed infinite exponent does not correspond to exponential divergence in a continuous state variable. The evidence presented (e.g., rapid saturation of distance in simulations) conflates discrete state transitions with deterministic chaos. This undermines the core claim. It would be more accurate to characterize the state as highly sensitive to perturbations and to quantify this sensitivity with a finite measure, or to provide a more rigorous analysis of chaos in the microscopic dynamics (e.g., computing Lyapunov exponents from simulated trajectories or analyzing a softened transfer function).

**Incomplete and inconsistent analysis of heterogeneity and parameter scalings**

The analysis of how the network responds to inhomogeneities, such as distributed thresholds, is fragmented and creates apparent contradictions. The treatment in Section 7 (for strong synapses) is performed within the large-K theory, while the comparison with the 'weak synapse' scenario in Section 10.2 introduces a different scaling argument (freezing if threshold width > 1/√K). Reviewers note that these analyses are not reconciled under a unified scaling framework; the condition for freezing should logically depend on the threshold width relative to the scale of intrinsic input fluctuations (√m_k), not an absolute scale. Furthermore, the biological justification and interpretation of the core scaling assumptions—J ~ 1/√K for synapses and u^0 ~ √K for external drive—are insufficiently addressed. The paper does not clearly map these dimensionless scalings to biophysical quantities or discuss whether the required strong external drive relative to recurrent feedback is biologically plausible. A unified analysis of inhomogeneity effects across regimes and a discussion linking model parameters to experimental measurements are needed.

**Overstated functional claims without rigorous finite-K verification**

The paper makes strong functional claims, notably that the network can perfectly track time-varying external inputs with an error of only O(1/√K). This conclusion is derived from an asymptotic analysis of the linearized dynamics. However, reviewers note that the simulations demonstrating tracking use a finite K=1000, and the paper does not verify that the tracking performance for this finite K aligns with the asymptotic theory. There is no analysis of how the tracking error or bandwidth scales with K for a given input frequency. Given that the stability eigenvalues scale as √K, the tracking capabilities should be explicitly connected to the network's effective finite-K time constants. The claim of fast tracking, a key proposed functional advantage, therefore lacks rigorous support for the finite networks that would be implemented biologically or in simulations.

**Limited exploration of stability conditions and their biological plausibility**

The stability analysis divides perturbations into local and global classes and derives critical time constants τ_L and τ_G. Reviewers raise several concerns: (1) The analysis of global stability simplifies the transfer function to a step function, a drastic approximation whose accuracy is not validated. (2) The stability phase diagram (Figure 9) varies certain parameters while holding others (like mean rates) fixed, but does not comprehensively explore the dependence on the external drive m_0, which is critical as cortical activity levels vary. (3) The paper does not discuss whether the derived parameter ranges for stability (e.g., the inequality (E/I) > (J_E/J_I) > 1) are biologically plausible. The conditions are presented in abstract terms without mapping to measurable biological quantities like relative synaptic strengths or time constants. A more comprehensive numerical exploration of the parameter space and a discussion of expected biological ranges would strengthen the model's relevance.

**Inadequate treatment of correlations and potential limitations of binary dynamics**

The derivation of temporal autocorrelations in the mean-field theory assumes presynaptic activities are uncorrelated, neglecting the feedback of correlations in a recurrent network. The consistency of this assumption is not examined, nor is the theoretical prediction for q_k(τ) rigorously verified against simulations of the full binary network. Furthermore, reviewers note that the extreme simplification of binary neuron dynamics with asynchronous updates, while enabling tractable theory, may qualitatively alter functional properties compared to more biological models. The discussion suggests predictions apply to integrate-and-fire models, but this leap is not sufficiently supported. Key phenomena like the 'infinite' Lyapunov exponent and the fast tracking mechanism are direct consequences of the binary, high-gain rule and may not persist in models with continuous subthreshold dynamics, refractory periods, or conductance-based synapses. The paper's interpretations would be more convincing with a discussion of these expected modifications.

**Status**: [Pending]

---

## Detailed Comments (19)

### 1. Incorrect definition of connection probability

**Status**: [Pending]

**Quote**:
> The connection between the $i$th postsynaptic neuron of the $k$th population and the $j$th presynaptic neuron of the $l$th population, denoted $J_{kl}^{ij}$ is $J_{kl}/\sqrt{K}$ with probability $K/N_{k}$ and zero otherwise. Here $k,l=1,2$.

**Feedback**:
The connection probability is defined as $K/N_k$, where $N_k$ is the size of the postsynaptic population. For a random sparse network, the probability should depend on the size of the presynaptic population $N_l$ to achieve an average of $K$ incoming connections from population $l$. The correct probability is $K/N_l$. Rewrite the quoted text as 'with probability $K/N_l$ and zero otherwise'.

---

### 2. Missing factor in variance derivation

**Status**: [Pending]

**Quote**:
> Observing that $[(J_{kl}^{ij}\sigma_{l}^{j}(t))^{2}]=J_{kl}^{2}m_{l}/N$, whereas $[(J_{kl}^{ij}\sigma_{l}^{j}(t))]^{2}=J_{kl}^{2}m_{l}^{2}K/N^{2}$, which is negligible, one obtains equation 3.6.

**Feedback**:
The second moment per presynaptic neuron should be $J_{kl}^2 m_l / N_l$, not $J_{kl}^2 m_l / N$. The denominator $N$ is ambiguous; it should be the size of the presynaptic population $N_l$. Rewrite the quoted text as 'Observing that $[(J_{kl}^{ij}\sigma_{l}^{j}(t))^{2}]=J_{kl}^{2}m_{l}/N_l$, whereas $[(J_{kl}^{ij}\sigma_{l}^{j}(t))]^{2}=J_{kl}^{2}m_{l}^{2}K/N_l^{2}$, which is negligible, one obtains equation 3.6.'

---

### 3. Missing factor in linearization term f_kl

**Status**: [Pending]

**Quote**:
> Calculating $f_{kl}$ by partial differentiation of the r.h.s. of equation 3 yields
> 
> $f_{kl}=\frac{\exp(-u_{k}^{2}/2\alpha_{k})J_{kl}}{\sqrt{2\pi\alpha_{k}}}.$ (11)

**Feedback**:
The expression for $f_{kl}$ is missing a factor of $\sqrt{K}$. The derivative of the transfer function $\Phi$ with respect to $m_l$ yields $\Phi'(...) * \sqrt{K} J_{kl}$. This factor is crucial for the eigenvalues to scale as $\sqrt{K}$, as stated later. Rewrite equation (11) as $f_{kl}=\sqrt{K}\frac{\exp(-u_{k}^{2}/2\alpha_{k})J_{kl}}{\sqrt{2\pi\alpha_{k}}}$.

---

### 4. Incorrect linearized equation for distance D_k

**Status**: [Pending]

**Quote**:
> $\tau_{k}\frac{dD_{k}}{dt}=\frac{2}{\pi}\frac{e^{-u_{k}^{2}/2\alpha_{k}}}{\sqrt{\alpha_k}}\sqrt{\alpha_{k}-\gamma_{k}}.$ (13)

**Feedback**:
For small $D_k$, the linearization should yield $dD_k/dt$ proportional to $D_k$, not $\sqrt{D_k}$. The term $\sqrt{\alpha_k - \gamma_k}$ scales as $\sqrt{D_k}$, which leads to an incorrect infinite Lyapunov exponent. The correct linearized equation should be linear in $D_k$. Rewrite equation (13) as $\tau_k dD_k/dt = (\sqrt{2/\pi}) (e^{-u_k^2/(2\alpha_k)}/\sqrt{\alpha_k}) * (J_{kE}^2 D_E + J_{kI}^2 D_I)/2$.

---

### 5. Inconsistent time variable in integral

**Status**: [Pending]

**Quote**:
> $m_{k}(t)=\frac{1}{\tau_{k}}\int_{0}^{\infty}dt^{i}e^{-t/\tau_{k}}F_{k}(m_{E}(t-t^{i}),m_{I}(t-t^{i})),$ (4)

**Feedback**:
The exponential factor $e^{-t/\tau_k}$ uses the absolute time $t$, not the integration variable $t^i$. This makes the integral mathematically incorrect. The exponential should decay with $t^i$. Rewrite equation (4) as $m_{k}(t)=\frac{1}{\tau_{k}}\int_{0}^{\infty}dt^{i}e^{-t^{i}/\tau_{k}}F_{k}(m_{E}(t-t^{i}),m_{I}(t-t^{i}))$.

---

### 6. Missing definition of α_k in stability section

**Status**: [Pending]

**Quote**:
> $f_{kl}=\frac{\exp(-u_{k}^{2}/2\alpha_{k})J_{kl}}{\sqrt{2\pi\alpha_{k}}}.$ (11)

**Feedback**:
The symbol $\alpha_k$ appears without definition in this section. From context, $\alpha_k$ is the variance of the input noise, but its definition should be provided for clarity. Additionally, the exponent uses $u_k^2$, which assumes the threshold $\theta_k=0$. If thresholds are non-zero, the exponent should be $-(u_k-\theta_k)^2/(2\alpha_k)$. Add a sentence before equation (11) defining $\alpha_k$ and clarifying the threshold assumption.

---

### 7. Ambiguous definition of J_k in global stability equation

**Status**: [Pending]

**Quote**:
> $\tau_{k}\frac{d}{dt}\delta m_{k}(t)=-\delta m_{k}(t)+\Theta(\delta m_{E}-J_{k}\delta m_{I})-m_{k}.$ (6.4)

**Feedback**:
The symbol $J_k$ in equation (6.4) is not defined. From the context of balance, the argument of the step function likely involves the ratio $J_I/J_E$. Without a clear definition, the reader cannot interpret the equation or verify the derivation of $\tau_G$. Define $J_k$ explicitly, e.g., 'where $J_k = J_{kI}/J_{kE}$' or 'where $J = J_I/J_E$ for both populations.'

---

### 8. Inconsistent equation numbering and mislabeling

**Status**: [Pending]

**Quote**:
> Equations 12 and 13 determine the average rates of the populations, but they must be consistent also with the general equilibrium results of equation 17. According to equations 12 and 13, the leading $O(\sqrt{K})$ contributions to $u_{k}$ cancel each other. Thus, the net value of $u_{k}$ is determined by subleading contributions, such as corrections of order $1/\sqrt{K}$ to $m_{k}$. In fact, equations 17 should be viewed as equations that determine the net synaptic inputs $u_{k}$ given the mean activity rates $m_{k}$, equations 12 and 13. It is useful to denote by $h(m)$ the scaled input of $m$, defined as the solution of the equation
> 
> $m=H(-h).$ (12)
> 
> Thus, equation 17 reduces to
> 
> $u_{k}=\sqrt{\alpha_{k}}h(m_{k}).$ (13)

**Feedback**:
The labels (12) and (13) are reused for new equations within the same passage, creating significant ambiguity. Readers cannot distinguish whether a reference to 'equation 12' points to an earlier result or the newly defined relation. Introduce unique equation numbers for the definitions $m=H(-h)$ and $u_k = \sqrt{\alpha_k} h(m_k)$ to avoid cross-reference errors.

---

### 9. Missing derivation for equation 7.11

**Status**: [Pending]

**Quote**:
> Indeed, analyzing the rate distribution for this case, we find that it is unimodal with width<!-- PAGE BREAK -->$\sqrt{q_k}$, where
> 
> $$
> q_k \propto \Delta \alpha_k^{3/2}. \tag{7.11}
> $$

**Feedback**:
Equation 7.11 states $q_k \propto \Delta \alpha_k^{3/2}$ without derivation or justification. The scaling is not obvious from preceding equations. Provide a brief explanation or reference to an appendix showing how this scaling arises from integrating $H^2$ over the threshold distribution.

---

### 10. Inconsistent scaling in equation 9.6 derivation

**Status**: [Pending]

**Quote**:
> The rates $m_{k}$ satisfy equation 3.3. To leading order in $K$ this is
> 
> $\tau_{k}\frac{dm_{k}^{\infty}(t)}{dt}=-m_{k}^{\infty}(t)+H\left(-\frac{u_{k}^{\infty}(t)+\sum_{l}J_{kl}m_{l}^{1}(t)}{\sqrt{\alpha_{k}^{\infty}(t)}}\right),k=1,2.$ (9.6)

**Feedback**:
The derivation from equation 3.3 to equation 9.6 is incomplete. The ansatz $m_k = m_k^{\infty} + m_k^1/\sqrt{K}$ and expansions for $u_k$ and $\alpha_k$ should be shown explicitly to justify how the $1/\sqrt{K}$ correction $m_l^1$ enters the argument of $H$. Without intermediate steps, the form of equation 9.6 is not self-evident.

---

### 11. Unsubstantiated claim about integrate-and-fire predictions

**Status**: [Pending]

**Quote**:
> Although constructing an exact mean-field theory for the integrate-and-fire dynamics similar to the one presented here for binary units is much more difficult, we believe that most of the predictions of our mean-field theory are applicable to the integrate-and-fire dynamics as well, provided that the same connectivity architecture and scaling of parameters with $N$ and $K$ are used.

**Feedback**:
This statement expresses a belief without evidence. The mean-field theory relies on specific assumptions (asynchronous updates, Gaussian input, step-function transfer) that may not hold for integrate-and-fire dynamics. The claim should be tempered with a discussion of necessary conditions or potential differences. Rewrite to hypothesize qualitative predictions may apply, but note that quantitative aspects like stability and chaos may differ.

---

### 12. Contradiction on fast tracking vs. fast switching

**Status**: [Pending]

**Quote**:
> Tsodyks and Sejnowski (1995) show numerically that their model is capable of “fast switching” in response to a fast change in the external stimulus. This may be related to the fast tracking predicted in our model. The fact that our model does not respond quickly to a sudden switching of the stimulus (see Figure 13) is probably a result of the dynamics of binary neurons. However,<!-- PAGE BREAK -->Chaotic Balanced State in a Model of Cortical Circuits
> 
> the switching time constants observed in Tsodyks and Sejnowski (1995) is of the same order as the single-cell integration time constant, while the fast tracking should occur on a much shorter time constant.

**Feedback**:
There is a logical contradiction: if fast tracking is much faster than the switching in Tsodyks and Sejnowski, the two phenomena are not directly comparable. The initial suggestion of a relationship is misleading. Furthermore, the claim that the model does not respond quickly to sudden switching contradicts earlier claims about fast tracking. Resolve the inconsistency by clarifying the distinct time scales and mechanisms.

---

### 13. Incorrect interpretation of experimental data relevance

**Status**: [Pending]

**Quote**:
> Recent experimental findings of Ferster, Chung, and Wheat (1996) in cat primary visual cortex suggest that the input from the lateral geniculate nucleus (LGN) to layer 4 cortical cells are in fact a fraction of the net input. Stratford, Tarczy-Hornoch, Martin, Bannister, and Jack (1996) show that the total strength of the LGN synapses is about 2.5 to 3 times smaller than the total strength of the excitatory feedback synapses from layer 4 cells; however, this study does not measure the strength of the feedback from the inhibitory interneurons, so it does not allow for the estimation of the net feedback.

**Feedback**:
The experimental results suggest LGN input is a fraction of the net input and smaller than total excitatory feedback. This contradicts the model's core scaling assumption that external input is large ($O(\sqrt{K})$) relative to net input ($O(1)$) and comparable to total feedback. The statement should acknowledge this tension rather than presenting the data as supportive. Rewrite to clarify the discrepancy and the need for further experimental quantification.

---

### 14. Potential error in low-rate expansion for q_k

**Status**: [Pending]

**Quote**:
> In the low rate limit, $m_{0}\ll 1$, equation 5.12 can be solved using equations 4.13 through 4.15, yielding to leading order,
> 
> $q_{k}=m_{k}^{2}+O(m_{k}^{2}|\log m_{k}|).$ (5.14)
> 
> Thus, if the network evolves to a state with low average activity levels, $m_{k}\ll 1$, $q_{k}$ is slightly larger than $m_{k}^{2}$. The fact that $q_{k}\ll m_{k}$ implies that the balanced state is characterized by strong temporal fluctuations in the activity of the individual cells. On the other hand, the fact that $q_{k}$ is not exactly equal to $m_{k}^{2}$ reflects the spatial inhomogeneity in the time-averaged rates within a population. Equation 5.14 implies that when the mean activity $m_{k}$ decreases, the width of the distribution is proportional to $(m_{k})^{3/2}$; it decreases faster than the mean $m_{k}$.

**Feedback**:
The claim that the width scales as $(m_k)^{3/2}$ is inconsistent with the given asymptotic form. The variance $q_k - m_k^2$ is $O(m_k^2 |\log m_k|)$, so the standard deviation scales as $m_k \sqrt{|\log m_k|}$, not $(m_k)^{3/2}$. Rewrite the sentence as: 'Equation 5.14 implies that when the mean activity $m_k$ decreases, the standard deviation of the rate distribution scales as $m_k \sqrt{|\log m_k|}$; it decreases slightly slower than the mean $m_k$.'

---

### 15. Ambiguous bounds in equation 7.12

**Status**: [Pending]

**Quote**:
> The full shape of the rate distribution is given by
> 
> $$
> \rho_k(m) \approx \frac{\sqrt{\alpha_k / 2 \Delta^2}}{m \sqrt{|\log m|}}, \quad m_- < m < m_+ \tag{7.12}
> $$
> 
> and zero otherwise. The bounds of $m$ are:
> 
> $$
> m_- \propto \exp\left(-\Delta^2 / (2 \alpha_k)\right). \tag{7.13}
> $$
> 
> $$
> m_+ \propto \Delta \sqrt{\alpha_k / |\log(\alpha_k)|} \gg m_k. \tag{7.14}
> $$

**Feedback**:
The bounds $m_-$ and $m_+$ are given only up to proportionality constants. For quantitative comparison with simulations, the prefactors matter. The statement $m_+ \gg m_k$ is qualitative; without the proportionality constant, it's unclear how much larger $m_+$ is. Specify the bounds more precisely, perhaps by providing leading-order terms in an asymptotic expansion for small $m_k$, and explain the origin of the logarithmic factor in $m_+$.

---

### 16. Unclear scaling of δm_k in tracking explanation

**Status**: [Pending]

**Quote**:
> This initial large response causes a fast rate of increase in the population rates, since $\delta m_k \approx \tau_k^{-1} dt \Delta P_k$, implying that $\delta m_k$ reaches the value $A_k \delta m_0$ in time of order $\tau_k / \delta m_0 \approx \tau_k / \sqrt{K}$; see the dotted line in Figure 13.

**Feedback**:
The scaling argument is muddled. If $\delta m_k \sim \delta m_0 \sim 1/\sqrt{K}$ and $d(\delta m_k)/dt \sim 1/\tau_k$, then the time to reach $\delta m_k$ is $\Delta t \sim \delta m_0 \tau_k \sim \tau_k/\sqrt{K}$. The expression $\tau_k / \delta m_0$ would give $\tau_k \sqrt{K}$, which is the opposite scaling. Rewrite the sentence to clarify: $\delta m_k \approx (\Delta P_k/\tau_k) \Delta t$, so $\Delta t \approx (\delta m_k) \tau_k / \Delta P_k$. With $\delta m_k = A_k \delta m_0 \sim \delta m_0$ and $\Delta P_k \sim 1$, we get $\Delta t \sim \tau_k \delta m_0 \sim \tau_k/\sqrt{K}$.

---

### 17. Inconsistent notation for temporal fluctuations variance

**Status**: [Pending]

**Quote**:
> \begin{aligned}
> [ (u_{k}^{i}(t) - \langle u_{k}^{i} \rangle)^2 ] & = \sum_{l=1}^{2} J_{kl}^{2} (m_{l} - q_{l}) = m_{E} - q_{E} + J_{k}^{2} (m_{l} - q_{l}) \\
> & = \alpha_{k} - \beta_{k} \tag{5.9}
> \end{aligned}

**Feedback**:
The notation is inconsistent. The second term uses '$m_l - q_l$' with subscript 'l' unspecified, while the first term explicitly uses '$m_E - q_E$'. This mix of explicit and indexed notation is confusing. Rewrite equation 5.9 as '$[ (u_k^i(t) - \langle u_k^i\rangle)^2 ] = J_{kE}^2 (m_E - q_E) + J_{kI}^2 (m_I - q_I) = m_E - q_E + J_k^2 (m_I - q_I) = \alpha_k - \beta_k$' to clarify contributions.

---

### 18. Missing definition of α_k in decomposition

**Status**: [Pending]

**Quote**:
> The statistics can be expressed by writing the instantaneous activity of a cell as a threshold function of two random variables $x_{i}$ and $y_{i}(t)$,
> 
> $$
> \sigma_{k}^{i}(t) = \Theta\left(- u_{k} + \sqrt{\beta_{k}} x_{i} + \sqrt{\alpha_{k} - \beta_{k}} y_{i}(t)\right). \tag{5.1}
> $$

**Feedback**:
The parameter $\alpha_k$ is introduced in equation 5.1 without definition. From context, $\alpha_k$ should represent the total variance of the synaptic input to a neuron in population $k$. This should be made explicit. Add a definition: 'The parameter $\alpha_k$ is the total variance of the synaptic input to a cell in population $k$, given by $\alpha_k = m_E + J_k^2 m_I$.'

---

### 19. Equation 5.17 appears incorrect

**Status**: [Pending]

**Quote**:
> $$
> \begin{array}{l}
> \tau_{k} \frac{d q_{k}(\tau)}{d \tau} = - q_{k}(\tau) + \int_{0}^{\infty} \frac{d t}{\tau_{k}} \\
> \quad \times \exp(-t / \tau_{k}) \int D x \left[ H \left(\frac{- u_{k} - \sqrt{\beta_{k}(t + \tau)} x}{\sqrt{\alpha_{k} - \beta_{k}(t + \tau)}}\right) \right]^{2}. \tag{5.17}
> \end{array}
> $$

**Feedback**:
Equation 5.17 seems to be a simplified or incorrect representation of the autocorrelation function. Typically, the two-time correlation involves a double integral over a bivariate Gaussian. The factor $[H(...)]^2$ is not standard. The equation does not obviously reduce to the correct boundary conditions $q_k(0)=m_k$ and $q_k(\infty)=q_k$. Provide a derivation showing how this form is obtained, or rewrite it as a proper double integral over the bivariate Gaussian distribution of inputs at two times.

---
