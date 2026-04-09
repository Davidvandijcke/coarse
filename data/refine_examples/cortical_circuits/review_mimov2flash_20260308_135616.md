# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 03/08/2026
**Domain**: natural_sciences/biology
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Validity of Mean-Field Approximations for Finite-Size Sparse Networks**

The mean-field theory is derived as exact in the limit of large N and K with 1 ≪ K ≪ N, but biological networks have finite N and K where this condition may not hold. Readers might note that finite-K corrections (Section 4.2) show significant deviations at low rates (Figure 3), suggesting the balanced state may not be robust in smaller networks. It would be helpful to explicitly state the range of K and N over which the theory remains accurate and provide a more detailed analysis of finite-size effects on stability and chaos.

**Assumptions About Poisson-Like Spike Statistics in Balanced State Regimes**

The paper claims approximate Poissonian statistics, but autocorrelation analysis (Section 5.2, Figure 5) shows enhanced short-time correlations due to refractoriness, contradicting the claim. This affects comparisons to experimental data and functional implications for cortical computation. It would be helpful to clarify the extent of deviation from Poisson statistics and discuss how this impacts the interpretation of the balanced state as a model for cortical irregularity.

**Handling of Time Delays in Autocorrelation and Stability Analysis**

Stability analysis and autocorrelation calculations assume instantaneous interactions, but biological synapses involve transmission delays that can affect balance and chaos. The paper does not address how delays might destabilize the balanced state or alter fast tracking capabilities. It would be helpful to discuss the potential effects of finite delays, perhaps by referencing related work or suggesting future directions, and to specify conditions under which the balanced state remains stable with delays.

**Scalability of Analytical Solutions to Biologically Realistic Parameter Ranges**

The analytical solutions rely on scaling synaptic strengths as 1/√K and external inputs as √K, implying fine-tuned parameters that may not align with experimental measurements. The paper does not quantitatively compare its parameter ranges to empirical data or assess robustness to variations. It would be helpful to add a subsection comparing model parameters to experimental estimates and to include a sensitivity analysis of the balanced state to parameter changes.

**Impact of Synaptic Dynamics and Threshold Heterogeneity on Balanced State Robustness**

The model assumes static synapses and homogeneous thresholds, but biological networks exhibit short-term plasticity and threshold heterogeneity, which can alter balance stability and chaos. The paper mentions these omissions but does not integrate them into core analyses. It would be helpful to discuss how synaptic depression/facilitation and threshold inhomogeneity might modify the mean-field equations and whether the balanced state persists under such dynamics, perhaps by citing related work or suggesting future extensions.

**Assumption of Infinite Network Size (K → ∞) Without Finite-K Corrections in Some Analyses**

The formal assumption (Section 3) is that the mean-field theory is exact in the limit of large network size N and large connectivity index K, with 1 ≪ K ≪ N. The paper derives key results (e.g., balanced state conditions, rate distributions) in the limit K → ∞, and later discusses finite-K corrections (Section 4.2). However, in Section 8 (Chaotic Nature), the analysis of sensitivity to initial conditions uses the large-K limit to claim an infinitely large Lyapunov exponent (equation 8.9), which may not hold for finite K. Readers might note that for finite K, the Lyapunov exponent could be finite, affecting the interpretation of chaos in biologically plausible networks. The paper does not explicitly check whether the finite-K corrections alter the chaotic nature conclusion. It would be helpful to clarify whether the chaotic behavior persists for finite K, perhaps by simulating the model with K = 1000 (as used in other figures) and measuring the Lyapunov exponent.

**Neglect of Synaptic Depression/Facilitation in Balanced State Dynamics**

The model assumes static synaptic strengths (Section 2), with no short-term plasticity (e.g., depression or facilitation). In Section 10.5, the paper acknowledges that synaptic depression and facilitation could affect the balanced state, but it does not incorporate them into the formal assumptions or analysis. Readers might note that biological synapses often exhibit short-term plasticity, which could alter the balance conditions and tracking capabilities. The paper suggests future work on this topic but does not defend the static synapse assumption against potential violations. It would be helpful to discuss how the inclusion of synaptic depression/facilitation might modify the balanced state predictions, perhaps by referencing related work (e.g., Markram and Tsodyks, 1996) and suggesting robustness checks with plastic synapses.

**Assumption of Homogeneous Thresholds Across Neuron Populations in Main Analysis**

The main analysis (Sections 3–6) assumes identical thresholds for neurons within each population (θ_E and θ_I). Section 7 explicitly introduces inhomogeneous thresholds and shows that they can lead to frozen states or skewed rate distributions depending on the threshold distribution. However, the core balanced state conditions (equations 4.9 and 4.10) and stability analysis (Section 6) are derived under the homogeneous threshold assumption. Readers might note that biological neurons exhibit threshold variability, which could violate the homogeneous assumption and affect the existence of the balanced state. The paper defends this by analyzing inhomogeneous thresholds in Section 7, but the defense is qualitative and does not quantify how threshold inhomogeneity impacts the stability conditions or tracking capabilities. It would be helpful to provide a robustness check by simulating the model with threshold distributions (e.g., Gaussian or uniform) and verifying whether the balanced state persists for typical parameter values.

**Status**: [Pending]

---

## Detailed Comments (8)

### 1. Ambiguous claim about exactness of mean-field theory

**Status**: [Pending]

**Quote**:
> We present an analytical solution of the mean-field theory of this model, which is exact in the limit of large network size. This theory reveals a new cooperative stationary state of large networks, which we term a balanced state.

**Feedback**:
It would be helpful to clarify the precise limit for exactness, as the claim is ambiguous without specifying the scaling of connectivity. The paper later assumes 1 ≪ K ≪ N, but this is not stated here. Readers might note that the exactness depends on the connectivity index K growing with N, which may not hold for biologically realistic sparse networks. Rewrite the quoted text as: "We present an analytical solution of the mean-field theory of this model, which is exact in the limit of large network size N and large connectivity index K with 1 ≪ K ≪ N." because this specifies the scaling required for exactness and aligns with later sections.

---

### 2. Unqualified claim about Poissonian statistics

**Status**: [Pending]

**Quote**:
> The spatiotemporal statistics of the balanced state are calculated. It is shown that the autocorrelations decay on a short time scale, yielding an approximate Poissonian temporal statistics.

**Feedback**:
It would be helpful to qualify the claim of approximate Poissonian statistics by acknowledging the presence of short-time correlations due to refractoriness, which the paper itself shows in Section 5.2 and Figure 5. This contradicts the assumption of Poisson-like spike statistics in balanced state regimes. Readers might note that enhanced short-time correlations affect comparisons to experimental data and functional implications. Rewrite the quoted text as: "The spatiotemporal statistics of the balanced state are calculated. It is shown that the autocorrelations decay on a short time scale, yielding approximately Poissonian temporal statistics except for short-time correlations due to refractoriness." because this acknowledges the deviation shown in the paper's own analysis.

---

### 3. Missing specification of synaptic strength scaling

**Status**: [Pending]

**Quote**:
> The internal feedback is mediated by relatively large synaptic strengths, so that the magnitude of the total excitatory and inhibitory feedback is much larger than the neuronal threshold.

**Feedback**:
It would be helpful to specify the scaling of synaptic strengths, as the description "relatively large" is vague. The paper later assumes synaptic strengths scale as 1/√K to maintain balance, but this is not stated here. Readers might note that without this scaling, the balance condition may not hold for finite K. Rewrite the quoted text as: "The internal feedback is mediated by synaptic strengths that scale as 1/√K, so that the magnitude of the total excitatory and inhibitory feedback is much larger than the neuronal threshold." because this specifies the scaling required for the balanced state and aligns with the model's assumptions.

---

### 4. Assumption of homogeneous thresholds not stated

**Status**: [Pending]

**Quote**:
> We study a network model with excitatory and inhibitory populations of simple binary units.

**Feedback**:
It would be helpful to state the homogeneous threshold assumption explicitly, as the description of the network model does not specify that thresholds are homogeneous within each population, which is a key assumption in the main analysis (Sections 3–6). Section 7 later introduces inhomogeneous thresholds, but the core balanced state conditions are derived under homogeneous thresholds. Readers might note that biological neurons exhibit threshold variability, which could affect the existence of the balanced state. Rewrite the quoted text as: "We study a network model with excitatory and inhibitory populations of simple binary units with homogeneous thresholds within each population." because this clarifies a key assumption for the mean-field theory and stability analysis.

---

### 5. Inconsistent definition of firing rate and activity rate

**Status**: [Pending]

**Quote**:
> Note that the firing rate, $r_{k}^{i}$, of neuron $i$ in population $k$ is different from the average value, $m_{k}^{i}(t)$, of $\sigma_{k}^{i}$ because before the cell can spike, it has to update to the passive state. However, if neuron $i$ of the $k$th population updates to the active state in two consecutive updates, the synapses projecting from this cell stay active after the second update, even though no new spike is emitted. However, if $m_{k}^{i}$, which we will call the activity rate, is small, the probability of two consecutive updates to the active state is low, and thus for small $m_{k}^{i}$, the activity rate and the firing rate are nearly equal. Indeed, if we assume that at each update the probability of being in the active state is $m_{k}^{i}$ (very nearly true in this model for low rates, as shown in section 5.3), the firing rate is given by $r_{k}^{i}=m_{k}^{i}(1-m_{k}^{i})/\tau_{k}$.

**Feedback**:
It would be helpful to explicitly state the conditions under which the formula for firing rate holds, such as low activity rates and independent updates, and cross-reference the mean-field derivation in Section 3. The distinction between firing rate and activity rate relies on the binary update mechanism, and the formula $r_{k}^{i}=m_{k}^{i}(1-m_{k}^{i})/\tau_{k}$ is only approximate for low rates. Readers might note that this formula is used in mean-field derivations without clarifying its validity range. Rewrite the passage to explicitly state the conditions and cross-reference Section 3, because this ensures consistency in the derivation of mean-field equations.

---

### 6. Inconsistent scaling of net input magnitude

**Status**: [Pending]

**Quote**:
> In the notation of our model, the external input to an excitatory cell is $Em_0\sqrt{K}$, whereas the net input to this cell, $u_E$, is smaller than the external input by a factor of the order of $1/(m_0\sqrt{K})$, where $m_0$ is the rate of an input cell and is assumed to be much larger than $1/\sqrt{K}$.

**Feedback**:
It would be helpful to clarify that the net input $u_E$ is of order 1 in the balanced state, as the quoted text claims $u_E$ is smaller by a factor of $1/(m_0\sqrt{K})$, which could be misinterpreted. Readers might note that this scaling is consistent with the balanced-state condition that $u_E$ is of order 1 and much smaller than the external input. Rewrite the quoted text as: "In the notation of our model, the external input to an excitatory cell is $Em_0\sqrt{K}$, whereas the net input to this cell, $u_E$, is of order 1 and much smaller than the external input, by a factor of the order of $1/(m_0\sqrt{K})$, where $m_0$ is the rate of an input cell and is assumed to be much larger than $1/\sqrt{K}$." because this clarifies that $u_E$ is of order 1, consistent with the balanced-state theory.

---

### 7. Incorrect derivation of equation (8.9)

**Status**: [Pending]

**Quote**:
> tely. To find the initial rate of divergence, we expand equation 8.5 for small $D_{k}$ and find that to leading order, the distances satisfy
> 
> $\tau_{k}\frac{dD_{k}}{dt}=\frac{2}{\pi}\frac{e^{-u_{k}^{2}/2\alpha_{k}}}{\sqrt{\alpha_{k}}}\sqrt{\alpha_{k}-\gamma_{k}}.$ (8.9)
> 
> Since $\alpha_{k}-\gamma_{k} \propto D_{k}$, equation 8.9 has a growing solution even if $D_{k}(0)=0$. This implies that t

**Feedback**:
It would be helpful to correct equation (8.9) because the derivation appears to be incorrect. The expansion for small $D_k$ should yield a linear term in $D_k$, but the given equation has a square root of $(\alpha_k - \gamma_k)$, which scales as $\sqrt{D_k}$, leading to $dD_k/dt \sim \sqrt{D_k}$ rather than linearly in $D_k$. This contradicts the standard linearization of such equations and affects the claim of an infinitely large Lyapunov exponent. Rewrite equation (8.9) as $\tau_k dD_k/dt = K_k D_k$, where $K_k$ is a positive constant, because the correct linearized form must be linear in $D_k$ to yield a finite Lyapunov exponent for finite $K$.

---

### 8. Inconsistent claim about Lyapunov exponent divergence

**Status**: [Pending]

**Quote**:
> Since $\alpha_{k}-\gamma_{k} \propto D_{k}$, equation 8.9 has a growing solution even if $D_{k}(0)=0$. This implies that the Lyapunov exponent $\lambda_{L}$ is infinitely large in the balanced state.

**Feedback**:
It would be helpful to revise the claim about infinite Lyapunov exponent because it relies on the incorrect equation (8.9). For finite $K$, the correct linearization should yield $dD_k/dt \propto D_k$, leading to a finite Lyapunov exponent. Readers might note that the infinite value is an artifact of the large-$K$ limit and discreteness, but the derivation is flawed. Rewrite the quoted text as: "This implies that the Lyapunov exponent $\lambda_{L}$ is positive (and possibly infinite in the large-$K$ limit), but for finite $K$ it is finite." because this acknowledges the scope of the claim and avoids overgeneralization.

---
