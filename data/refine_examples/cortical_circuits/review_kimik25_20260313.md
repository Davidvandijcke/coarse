# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 03/13/2026
**Domain**: natural_sciences/neuroscience
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

This paper develops a mean-field theory for sparse balanced networks of binary neurons to analyze the existence, stability, and dynamic tracking properties of asynchronous balanced states. The authors derive self-consistent conditions for maintaining stable, low-rate activity through inhibitory feedback, characterize the resulting chaotic microscopic dynamics, and identify parameter regimes permitting global stability and fast tracking of time-varying external inputs. The analysis predicts that networks can track input variations on timescales of order 1/√K while exhibiting divergent Lyapunov exponents due to the discrete state space.

Below are the most important issues identified by the review panel.

**Restrictive Scaling Condition for Mean-Field Validity**

Appendix A states that statistical independence of inputs holds rigorously only when K ≪ log N, yet the main text presents the theory as valid under the weaker scaling 1 ≪ K ≪ N. This discrepancy is significant because biological cortical networks typically exhibit K ~ 10³–10⁴ and N ~ 10⁵–10⁶, where log N ~ 11–14, violating the rigorous condition. Simulations presented use K = 1000, which may not satisfy K ≪ log N for realistic network sizes. It would be helpful to clarify whether the results hold when K is comparable to log N, or to quantify the finite-size corrections and correlation effects that persist at O(1/K) when the independence assumption breaks down.

**Breakdown of Gaussian Approximation in Low-Rate Regimes**

The mean-field theory approximates synaptic inputs as Gaussian via the Central Limit Theorem, valid for large K. However, in the balanced state with low firing rates (m_k ≪ 1), threshold crossings depend on rare events in the distribution tails where the Gaussian approximation fails. The underlying Poisson-binomial statistics for finite K produce heavier tails than the Gaussian approximation, particularly problematic near threshold where the response function varies rapidly. While Section 4.2 addresses finite-K corrections to mean rates, it does not quantify the systematic bias from using Gaussian tail statistics versus the true discrete distribution. It would be helpful to derive large-deviation corrections for the tail probabilities or verify via exact enumeration that the Gaussian approximation remains accurate for K ~ 1000 and rates relevant to cortex.

**Theoretical Inconsistencies in Characterization of Chaotic Dynamics**

Section 8 characterizes the balanced state as chaotic based on a maximum Lyapunov exponent that diverges to infinity, an artifact of the binary discretization and discontinuous Heaviside activation that does not generalize to continuous neuronal models. Readers might note that this reflects exponential sensitivity specific to the discrete state space rather than conventional deterministic chaos. Furthermore, an unresolved tension exists between the microscopic chaos (with divergent λ_L implying vanishing autocorrelation time) and the macroscopic stability analysis assuming stable fixed-point dynamics, as well as the derivation of temporal autocorrelations in Section 5.2 assuming simple Markovian structure. It would be helpful to clarify the relationship between mean-field stability and microscopic chaos, validate the autocorrelation derivation against direct simulations, and discuss how the results would scale for continuous neuron models with finite Lyapunov exponents.

**Limitations of Instantaneous Synaptic Transmission and Tracking Constraints**

The model assumes instantaneous synaptic transmission without temporal filtering, which is critical for the stability analysis and the claim of fast tracking on timescales of order 1/√K. Realistic AMPA and GABA synaptic dynamics introduce delays and low-pass filtering that could destabilize the balanced state or limit tracking speed to synaptic timescales rather than the claimed 1/√K regime. Additionally, the fast tracking results in Section 9 require external input variations to satisfy restrictive bounds on dm_0/dt (Eq. 9.8), and the paper does not analyze network behavior when these bounds are violated by realistic stochastic inputs or quantify recovery from such excursions. It would be helpful to discuss how first-order synaptic dynamics would modify the stability conditions and tracking limits, and to analyze the distribution of tracking errors for stochastic inputs that may occasionally violate the balance conditions.

**Approximations in Global Stability Analysis**

The global stability analysis in Section 6.2 approximates the smooth sigmoidal response function H(-u_k/√α_k) by the hard threshold Θ(u_k), eliminating the variance term α_k entirely. This piecewise linear approximation may not capture true basin of attraction boundaries, particularly near transitions to limit cycle regimes or where α_k ~ O(1) significantly affects transition probabilities. The claim of a 'comfortable parameter regime' for global stability may therefore be overstated. It would be helpful to justify the Θ-function limit by showing its validity for the specific parameter scaling used, or to verify the global stability boundaries using the full nonlinear equations including variance contributions to ensure the stability condition (Eq. 6.5) accurately reflects the dynamics.

**Status**: [Pending]

---

## Detailed Comments (10)

### 1. Inconsistency between power-law activity claims and freezing conditions

**Status**: [Pending]

**Quote**:
> The activity levels of single cells are broadly distributed, and their distribution exhibits a skewed shape with a long power-law tail.

**Feedback**:
The text claims single-cell activity follows a power-law distribution, yet Section 10.2 states that with inhomogeneous thresholds exceeding $1/\sqrt{K}$, the network becomes 'increasingly frozen' with neurons saturating or becoming inactive. A power-law distribution implies substantial probability mass at extreme rates, which would require threshold variations exceeding the freezing bound. Furthermore, the mean-field theory derives Gaussian input statistics via the Central Limit Theorem, which would not naturally generate power-law distributed firing rates without specific fine-tuning. It would be helpful to specify the exact parameter regime (e.g., particular threshold distributions) that yields power-law activity while maintaining the stable balanced state, or to verify that the tail is instead exponential or log-normal.

---

### 2. Missing scaling qualifications for mean-field exactness

**Status**: [Pending]

**Quote**:
> We present an analytical solution of the mean-field theory of this model, which is exact in the limit of large network size.

**Feedback**:
The text states the mean-field solution is exact in the large network limit. However, Appendix A indicates that statistical independence of inputs—which underlies the mean-field theory—holds rigorously only when $K \ll \log N$. While satisfied in the limit $N \to \infty$ with fixed $K$, this condition is violated for biologically relevant regimes where $K \sim 10^{3}$ and $\log N \sim 11-14$. Readers might note that claiming exactness without specifying the scaling relationship between $K$ and $N$ could imply validity for regimes where finite-size correlations persist. It would be helpful to qualify the statement by specifying that the solution is exact in the thermodynamic limit where $K \to \infty$, $N \to \infty$ with $K \ll \log N \ll N$, or to quantify the finite-size corrections when this scaling is not strictly satisfied.

---

### 3. Summation index errors in variance equation (3.12)

**Status**: [Pending]

**Quote**:
> $$ \alpha_{k}(t)=[(\delta u_{k}^{i}(t))^{2}]=\sum_{l,l'=1}^{2}\,\sum_{j,j'=1}^{N_{i}}[\,(\,\delta(J_{kl}^{ij}\sigma_{l}^{j}(t))\,)^{2}\,], \eqno(3.12) $$

**Feedback**:
The summation indices contain typographical errors affecting the mathematical content. The term inside the average depends only on indices $l$ and $j$, but the sum runs over $l'$ and $j'$ as well, erroneously introducing multiplicative factors of approximately $N_l$. Furthermore, the upper limit $N_i$ is inconsistent: $i$ indexes the postsynaptic neuron, so $N_i$ would equal 1, whereas the sum should extend over the presynaptic population size $N_l$. The correct expression should be $\sum_{l=1}^{2}\sum_{j=1}^{N_{l}}[\,(\,\delta(J_{kl}^{ij}\sigma_{l}^{j}(t))\,)^{2}\,]$. It would be helpful to rewrite the equation with the corrected summation limits to properly represent the variance calculation.

---

### 4. Scaling inconsistency in variance derivation

**Status**: [Pending]

**Quote**:
> Observing that $[(J_{kl}^{ij}\sigma_{l}^{j}(t))^{2}]=J_{kl}^{2}m_{l}/N$, whereas $[(J_{kl}^{ij}\sigma_{l}^{j}(t))]^{2}=J_{kl}^{2}m_{l}^{2}K/N^{2}$, which is negligible, one obtains equation 3.6.

**Feedback**:
The derivation contains a scaling inconsistency relative to the final result. The text states $[(J_{kl}^{ij}\sigma_{l}^{j})^{2}]=J_{kl}^{2}m_{l}/N$ and implies summing over the presynaptic population yields equation (3.6), where $\alpha_{k}=\sum_{l}(J_{kl})^{2}m_{l}$. However, summing $J_{kl}^{2}m_{l}/N$ over $N_{l}$ presynaptic neurons yields $(N_{l}/N)J_{kl}^{2}m_{l}$. Since $N=N_{E}+N_{I}$ and $N_{l}<N$, this produces a factor of $N_{l}/N$ (e.g., 1/2 for equal-sized populations) that does not appear in equation (3.6). For the derivation to yield equation (3.6), the variance per connection should be $[(J_{kl}^{ij}\sigma_{l}^{j})^{2}]=J_{kl}^{2}m_{l}/N_{l}$. It would be helpful to clarify whether $N$ denotes the presynaptic population size $N_{l}$ in this specific context, or to correct the denominator to $N_l$ to maintain consistency.

---

### 5. Scaling inconsistency in mean input derivation

**Status**: [Pending]

**Quote**:
> The population average $[J_{kl}^{ij}]$ is equivalent to a quenched average over the random connectivity and is therefore equal to $J_{kl}\sqrt{K}/N$, yielding equation 3.5.

**Feedback**:
The scaling of the average connectivity is inconsistent with the resulting mean-field equation (3.5). If $[J_{kl}^{ij}] = J_{kl}\sqrt{K}/N$ where $N=N_E+N_I$, substituting into equation (3.11) (with corrected summation limit $N_l$) yields $u_k(t) = \sum_{l=1}^2 (N_l/N) J_{kl}\sqrt{K} m_l(t)$. This contains an extra factor of $N_l/N$ compared to equation (3.5), which reads $u_k(t) = \sqrt{K} (\sum_{l=1}^2 J_{kl} m_l(t) + E_k m_0) - \theta_k$. For consistency with (3.5), the average should be $[J_{kl}^{ij}] = J_{kl}\sqrt{K}/N_l$. It would be helpful to clarify whether $N$ denotes the presynaptic population size $N_{l}$ in this specific context, or to correct the denominator to $N_l$.

---

### 6. Inconsistent scaling of cross-correlations with network parameters

**Status**: [Pending]

**Quote**:
> Most of the cross-correlations are of the order $1/N$, where $N$ is the network size. The maximal value of the cross-correlations occurs for pairs that are directly connected, and this cross-correlation is of the order of the strength of the synapse, $O(1/\sqrt{K})$.

**Feedback**:
It is not clear how the scaling $O(1/N)$ is derived for the cross-correlations between unconnected neurons. For a sparse random network with connectivity $K$ and synaptic weights $J \sim O(1/\sqrt{K})$, the covariance of inputs to two neurons sharing $O(K^2/N)$ common presynaptic inputs is expected to scale as $(K^2/N) \cdot J^2 \sim O(K/N)$. For the parameters used in the paper (e.g., $K=1000$), this yields $O(K/N) \sim 0.1$ (assuming $N \sim 10^{4}$), which exceeds the $O(1/\sqrt{K}) \sim 0.03$ correlation for directly connected pairs. This would contradict the claim that directly connected pairs exhibit the maximal correlations. It would be helpful to clarify whether the balanced state induces a dynamic cancellation mechanism that suppresses the shared-input contribution from $O(K/N)$ to $O(1/N)$, or to verify that the condition $K^{3/2} \ll N$ holds for the simulated network sizes, ensuring $K/N \ll 1/\sqrt{K}$.

---

### 7. Missing external input scaling assumption for general synaptic exponent

**Status**: [Pending]

**Quote**:
> Finally, the model can be generalized to a model with synaptic strengths that scale as $K^{-\alpha}$, with $0<\alpha<1$. Of course, these models can be distinguished from the present model only in the large $K$ limit. In this limit, the net average inputs into the populations scale as $K^{1-\alpha}$, while the quenched and temporal fluctuations in the inputs scale as $K^{1/2-\alpha}$. Therefore the leading order in the inputs has to cancel, leading to the balance condition.

**Feedback**:
The derivation of the balance condition for general $\alpha$ requires the external input to scale as $K^{1-\alpha}$ to cancel the recurrent input scaling $K^{1-\alpha}$. This holds for the specific cases discussed: for $\alpha=1/2$, the external input is $E m_0 \sqrt{K} \sim K^{1/2}$; for $\alpha=1$ (weak synapses), it is $O(1) = K^{0}$. However, the generalization does not explicitly state this assumption. Without external input scaling as $K^{1-\alpha}$, the leading order terms would not cancel, and the balance condition would not follow. It would be helpful to rewrite the quoted text to add: 'We assume the external input scales as $K^{1-\alpha}$ so that it cancels the leading order recurrent input, yielding the balance condition.'

---

### 8. Overgeneralized claim of chaotic activity for all synaptic exponents

**Status**: [Pending]

**Quote**:
> For any $\alpha$, this leads to asynchronous chaotic activity in a homogeneous network, similar to the case $\alpha=1/2$.

**Feedback**:
The text asserts that homogeneous networks exhibit asynchronous chaotic activity for any $\alpha \in (0,1)$. However, for $\alpha > 1/2$, the quenched and temporal fluctuations in the inputs scale as $K^{1/2-\alpha}$ and vanish in the large $K$ limit. With vanishing fluctuations, the net input to each neuron becomes deterministic and constant (equal to the mean field value). Binary threshold neurons receiving constant input exhibit regular, periodic firing or remain silent, rather than chaotic activity. This contradicts the claim for $\alpha > 1/2$. It would be helpful to restrict the statement to $\alpha \leq 1/2$, or to clarify that for $\alpha > 1/2$, the activity becomes regular (frozen) even in homogeneous networks.

---

### 9. Ambiguous terminology for net versus total synaptic input

**Status**: [Pending]

**Quote**:
> An important question is whether external input is large relative to net input to a cortical cell. Recent experimental findings of Ferster, Chung, and Wheat (1996) in cat primary visual cortex suggest that the input from the lateral geniculate nucleus (LGN) to layer 4 cortical cells are in fact a fraction of the net input.

**Feedback**:
The model assumes external input scales as $E m_0 \sqrt{K}$ (order $\sqrt{K}$) whereas the net input $u_E$ (the algebraic sum of external and recurrent synaptic currents) remains of order 1 (Section 10.2), meaning external input is explicitly assumed to be much larger than net input. The experimental finding cited—that LGN input is a fraction (i.e., smaller) of the net input—directly contradicts this scaling. Readers might note that 'net input' could refer here to the total absolute synaptic drive (scaling as $O(\sqrt{K})$) rather than the algebraic sum $u_E$, but this terminology conflicts with the technical definition used throughout the paper. It would be helpful to rewrite 'fraction of the net input' as 'fraction of the total absolute synaptic drive' because this clarifies that the comparison involves the sum of absolute synaptic strengths (which scales as $O(\sqrt{K})$ and is indeed larger than the external input), avoiding contradiction with the model's assumption that the algebraic net input $u_E$ is $O(1)$ and smaller than the external drive.

---

### 10. Variable naming inconsistency in Appendix B equation (4)

**Status**: [Pending]

**Quote**:
> $$ m_{k}(t)=\frac{1}{\tau_{k}}\int_{0}^{\infty}dt^{i}e^{-t'/\tau_{k}}F_{k}(m_{E}(t-t^{i}),m_{I}(t-t^{i})), \eqno(4) $$

**Feedback**:
Re-deriving the typographical check confirms the inconsistency: the integration variable is denoted as $t^{i}$ in the differential $dt^{i}$ and in the function arguments $F_{k}(m_{E}(t-t^{i}),m_{I}(t-t^{i}))$, but the exponential factor uses $t'$ (prime) instead of $t^{i}$. The derivation in the preceding text correctly implies the substitution $t^{i}$ throughout when changing variables from equation (3). For notational consistency, the exponent should use the same variable symbol as the integration measure. It would be helpful to rewrite the equation as $m_{k}(t)=\frac{1}{\tau_{k}}\int_{0}^{\infty}dt^{i}e^{-t^{i}/\tau_{k}}F_{k}(m_{E}(t-t^{i}),m_{I}(t-t^{i}))$ to ensure the integration variable matches in all terms.

---
