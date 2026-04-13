# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 04/12/2026
**Domain**: computer_science/computational_neuroscience
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper is ambitious and influential in scope, but several central claims rest on reductions that are looser than the prose suggests. The main concerns are the mismatch between what is proved for the population mean-field system and what is claimed for the full deterministic network, the thin evidence for chaos, and the limited treatment of finite-\(K\) and heterogeneity effects precisely where the biological interpretation depends on them.

The paper's main contribution is clear: it proposes a strong-coupling sparse-network regime in which excitation and inhibition cancel to leave fluctuation-driven activity, and it gives a tractable mean-field description of that regime. The analysis of balance conditions in Sections 4 and 7 is the strongest part of the paper, and the contrast with weak-synapse scaling is conceptually useful. Still, the paper often moves from an exact large-\(N\), large-\(K\) population theory to stronger statements about asynchronous chaos, cortical variability, and fast tracking in the full network without enough supporting derivation or validation.

**Chaos is asserted from overlap dynamics, but the diagnostic does not establish a standard chaotic attractor**

Section 8 is the paper's main basis for calling the balanced state chaotic, yet the argument is not as strong as the claim. Equation (8.9) implies a \(\sqrt{D_k}\)-type growth law near zero distance rather than the usual linearized exponential separation used to define a Lyapunov exponent, and the manuscript then concludes that the Lyapunov exponent is 'infinitely large.' That is a statement about the discontinuous binary update rule as much as about the network attractor, and it does not rule out very fast desynchronization in a nonchaotic or effectively stochastic-looking system. Readers will also notice that the evidence is built from two-copy overlap equations for the mean-field theory, not from a direct dynamical characterization of the full deterministic network. The paper should either narrow the claim to rapid loss of microscopic overlap in the large-\(N\) binary model or add a more standard chaos diagnostic for the deterministic update system, such as a carefully defined finite-size perturbation growth analysis that distinguishes exponential instability from one-step amplification induced by threshold discontinuities.

**The stability theory is for population rates, but the manuscript presents it as stability of the full balanced network state**

Sections 6.1 and 6.2 analyze stability by perturbing the macroscopic rates \(m_E,m_I\) in equation (3.3), and the resulting criteria \(\tau<\tau_L\) and \(\tau<\tau_G\) are therefore criteria for the reduced two-population mean-field dynamics. That is not the same as stability of the microscopic asynchronous state of the full sparse random network, especially when the paper later emphasizes local chaotic degrees of freedom and weak but nonzero cross-correlations. This gap matters because the prose in Section 6 and the discussion treats these conditions as if they certify the balanced state's existence and stability in the full network, while they actually leave open whether microscopic modes, finite-size structure, or weak correlations generate dynamics not seen in the two-dimensional reduction. The tension is visible in the paper's own distinction between macroscopic fixed-point stability and microscopic chaos in Section 8. A revision should separate these claims cleanly: state that Sections 6.1-6.2 establish stability of the mean population rates, then add simulations that test whether the full network obeys the same phase boundaries and whether microscopic observables remain stationary across those boundaries.

**The balance claim is derived asymptotically, but finite-\(K\) support is too thin for the regimes used in the figures and biological discussion**

The core mechanism depends on cancellation of \(O(\sqrt{K})\) excitation and inhibition to leave a net input of order one; this is derived in Sections 4 and 4.2 through equations (4.1)-(4.4) and the finite-\(K\) corrections in equations (4.17)-(4.18). Yet the paper largely treats \(K=1000\) as if it were already in the asymptotic regime, even though several conclusions hinge on subleading terms: low-rate behavior, threshold effects, tracking, and the distinction between balanced and unbalanced states. Figure 3 shows nontrivial finite-\(K\) deviations exactly where cortical relevance is claimed, but the manuscript then says these corrections are 'only quantitative' except for thresholding, which is stronger than the evidence provided. This matters because the model's operating regime at low \(m_0\) is where the balance mechanism is supposed to explain irregular low-rate cortical activity, and there the right-hand sides of (4.17)-(4.18) are not negligible. The paper would be much more convincing if it mapped how net input, firing rates, and input variances scale with \(K\) across a range of values, rather than relying on one illustrative choice and asymptotic formulas.

**The Gaussian mean-field closure is taken as exact under conditions where the paper later studies instability and heterogeneity**

Equation (3.3) and the later formulas for variability and overlap all rely on a Gaussian closure derived from weak correlations and self-averaging in the sparse large-\(N\), large-\(K\) limit. But the manuscript then pushes this same closure into settings where those assumptions are least secure: near local or global instability in Section 6, in low-rate regimes where finite-\(K\) terms matter in Section 4.2, and with broad threshold heterogeneity in Section 7. The text acknowledges that correlations due to specific connectivity are neglected in equations (3.11)-(3.12), yet many later claims, especially about vanishing cross-correlations and temporal Gaussian inputs, depend on those neglected terms remaining harmless. That is a substantive omission because the paper's framing is not merely that a closure yields a plausible picture, but that the mean-field theory is exact in the relevant limit and predicts the full spatiotemporal statistics. The authors should add either a sharper derivation of why the closure remains valid in the unstable and heterogeneous regimes, or simulation checks showing that input distributions, pairwise correlations, and autocorrelation functions match the Gaussian predictions over the parameter ranges used for the headline claims.

**The fast-tracking result is a small-signal property, but the discussion presents it as a broad functional advantage**

Section 9 derives tracking around an instantaneous-response solution by assuming in equation (9.5) that deviations remain of order \(1/\sqrt{K}\), and the admissible drive rates are then bounded by equation (9.8). That is a local, small-signal statement tied to slow enough changes in a homogeneous external drive, not a general theorem about rapid tracking by balanced networks. The paper does note the bound, but the surrounding discussion and the framing in the abstract make the result sound broader than what the derivation supports. This matters because the proposed functional significance of the balanced state rests heavily on this section, yet the analysis excludes large-amplitude perturbations, spatially structured inputs, and regimes where the balance is temporarily broken. A revision should narrow the claim to small homogeneous perturbations or add simulations and theory for larger and more realistic classes of inputs, showing when the network truly stays near balance and when it does not.

**The treatment of heterogeneity shows fragility, but the paper frames the balanced mechanism as broadly robust**

Section 7 is one of the most revealing parts of the manuscript because it shows that the outcome depends sharply on the tail behavior of the threshold distribution: Gaussian-like tails can drive the low-rate state toward freezing through equations (7.6)-(7.8), while bounded heterogeneity preserves broad fluctuating rate distributions through equations (7.9)-(7.14). That is a major limitation of scope, not a side result, because the paper's biological motivation leans on low-rate irregular activity and heterogeneous cortical populations. The distinction is especially important since the manuscript later compares favorably with cortical firing-rate distributions in Figure 11C, even though the theory predicts very different qualitative outcomes for different threshold families and does not establish which family is biologically appropriate. As written, the robustness claim is too broad relative to what Section 7 actually shows. The paper should foreground this dependence in the abstract and discussion, and it should add sensitivity analyses over threshold distributions and widths to clarify exactly which aspects of the balanced-chaotic picture survive heterogeneity.

**No explicit failure case for broken balance**

The paper derives parameter restrictions such as equations (4.9) and (4.10), but it never shows in a concrete network run what happens when those conditions fail. That leaves the main mechanism looking more formal than tested: readers are told balance is necessary, yet they do not see a specific deterministic network that loses the balanced-chaotic state once the inequalities are violated. This matters because the paper presents the balanced regime as a real dynamical phase rather than a bookkeeping consequence of the mean-field equations. A clean addition would be a matched counterexample using the Figure 3 parameter set with one coefficient moved across the boundary, for example setting \(J_E<1\) or choosing \(E/I<J_E/J_I\), and then plotting the excitatory and inhibitory input components, the net input, and the resulting rates. Showing saturation, quiescence, or an unbalanced oscillation in that nearby parameter set would make the existence conditions bite in a way the current manuscript does not.

**Poisson-like firing is shown too narrowly**

The claim that the balanced state yields Poisson-like firing is supported only by a single-cell ISI histogram and a surrogate gaussian-input construction in Sections 5.2 and 5.3. That is not enough for a paper that says it provides a complete statistical characterization of the state. Readers need to know whether near-Poisson spiking is a generic property of the actual deterministic network or just an illustrative outcome for one excitatory cell at one parameter choice. This matters because Poisson-like irregularity is one of the headline cortical signatures the paper is trying to explain. A stronger demonstration would measure ISI distributions, coefficient of variation, and long-window Fano factors directly from full-network simulations for several parameter sets and sizes, say \(K=250,500,1000\) and both low- and moderate-rate regimes, then compare those statistics to equation (5.18) and the autocorrelation prediction from equation (5.17).

**Weak cross-correlations are asserted, not characterized**

The distinction from synchronized chaos rests on weak pairwise correlations, yet the manuscript never gives a direct quantitative characterization of those correlations in the simulated network. The text says sparsity makes activity correlations very small and quotes heuristic orders such as \(1/N\) or \(1/\sqrt{K}\), but there is no figure or calculation showing the distribution of pairwise correlations, nor any finite-size scaling that supports the vanishing-correlation claim. This is a real gap because weak cross-correlation is one of the paper's core advertised features, not a side remark. Without that demonstration, the contrast with synchronized chaotic models stays mostly verbal. The natural fix is to compute spike-count or activity cross-correlations \(C_{ij}(\tau)\) for connected and unconnected pairs over several \(N\) and \(K\), and verify the predicted scaling of typical and maximal correlations while the single-cell variability remains large.

**A fully worked benchmark case is missing**

The theory gives many general formulas, but the paper never carries one concrete model all the way from the balance equations to the higher-order statistics in a form that readers can inspect line by line. Top theory papers usually include at least one benchmark case where the main objects are computed explicitly enough to calibrate intuition. Here a natural choice would be a symmetric low-rate excitatory-inhibitory setup with homogeneous thresholds and fixed \(\tau\), where one solves for \(m_E,m_I\) from equations (4.3)-(4.4), computes \(u_k\) via equations (4.12)-(4.15), then evaluates \(q_k\) from equation (5.12) and the implied ISI law. That would show, in one self-contained example, how balance, temporal variability, and rate heterogeneity fit together quantitatively. As written, the reader sees many separate formulas and figures, but not one complete worked special case that turns the abstract mechanism into a usable template.

**Recommendation**: major revision. The paper contains a valuable theoretical idea and some elegant asymptotic calculations, but the current version overstates what has been established about chaos, network-level stability, and robustness. A publishable revision would need to align the claims with what is actually proved and provide stronger validation that the reduced theory captures the full deterministic sparse network in the regimes emphasized most strongly.

**Key revision targets**:

1. Strengthen the evidence for chaos in Section 8 by either providing a more standard dynamical diagnostic for the deterministic network or revising the claim to a weaker statement about rapid desynchronization of microscopic trajectories.
2. Separate macroscopic rate stability from microscopic network stability in Section 6, and verify with full-network simulations whether the phase boundaries predicted by \(\tau_L\) and \(\tau_G\) match the behavior of the sparse network.
3. Add a systematic finite-\(K\) analysis showing how balance, net input, and variability scale with \(K\), especially in the low-rate regime where the biological interpretation is made.
4. Validate the Gaussian mean-field closure against simulations for input distributions, autocorrelations, and pairwise correlations in the unstable, low-rate, and heterogeneous regimes used in the paper.
5. Reframe the robustness and biological-implication claims to reflect the strong dependence on threshold-distribution tails, or add analyses demonstrating that the main conclusions persist across realistic forms of heterogeneity.

**Status**: [Pending]

---

## Detailed Comments (9)

### 1. Unbalanced branch is assigned to the wrong parameter regime

**Status**: [Pending]

**Quote**:
>  1. \tag {4.6}
> $$
>
> Besides this balanced solution, we should also examine the possibility of unbalanced solutions in which either $m_{k} = 0$ and $u_{k}$ is of order $\sqrt{K}$ and negative, or $m_{k} = 1$ and $u_{k}$ is of order $\sqrt{K}$ and positive. Equation 4.5 admits an unbalanced solution in which $m_{E} = 0$. In this solution, $m_{I}$ is to leading order in $K$ given by $m_{I} = Im_{0} / J_{I}$ (since the leading order in $u_{I}$ should vanish) so that
>
> $$
> u _ {E} = \sqrt {K} \left(E - J _ {E} I / J _ {I}\right) m _ {0}

**Feedback**:
This sign check goes the other way. With $m_I=Im_0/J_I$, the coefficient of $\sqrt K$ in $u_E$ is $I(E/I-J_E/J_I)m_0$. Under equation (4.5), $E/I>J_E/J_I$, so that coefficient is positive, not negative. The displayed branch fits equation (4.6), not equation (4.5). This matters because the admissible unbalanced branches are being used to motivate the final parameter restrictions. The clean fix is to replace “Equation 4.5 admits” by “Equation 4.6 admits,” or to redo the branch analysis if a different convention was intended.

---

### 2. Equations (4.9)-(4.10) do not remove every unbalanced fixed point

**Status**: [Pending]

**Quote**:
> -->Thus if we require that there be no stationary solutions with $m_{E}=0, 1$ or $m_{I}=0, 1$ for small $m_{0}$, the following constraints have to be satisfied:
>
> $\frac{E}{I} &gt; \frac{J_{E}}{J_{I}} &gt; 1.$ (4.9)
>
> $J_{E} &gt; 1.$ (4.10)
>
> It is straightforward to show that these constraints eliminate all possible unbalanced

**Feedback**:
That last sentence is too strong as written. There is still an $m_I=1$ branch with $0<m_E<1$ in part of this parameter region. Setting the leading term of $u_E$ to zero gives $m_E=J_E-Em_0$, and then the leading term of $u_I$ becomes $(J_E-J_I)+(I-E)m_0$. For example, with $E=1.5$, $I=1$, $J_E=1.05$, $J_I=1.01$, and $m_0=0.04$, equations (4.9) and (4.10) hold, $A_k m_0<1$ holds, but $m_E=0.99$, $m_I=1$, $u_E=0$, and $u_I=0.02\sqrt K>0$. So an unbalanced state remains. The paper needs either an extra restriction on $m_0$ or a narrower claim about which branches are excluded.

---

### 3. Connection probability does not match the claimed indegree

**Status**: [Pending]

**Quote**:
> The connection between the $i$th postsynaptic neuron of the $k$th population and the $j$th presynaptic neuron of the $l$th population, denoted $J_{kl}^{ij}$ is $J_{kl} / \sqrt{K}$ with probability $K/N_{k}$ and zero otherwise. Here $k,l=1,2$. The synaptic constants $J_{k1}$ are positive and $J_{k2}$ negative. Thus, on average, $K$ excitatory and $K$ inhibitory neurons project to each neuron.

**Feedback**:
The expected indegree from population $l$ under this rule is $N_l\cdot K/N_k=K N_l/N_k$, not $K$ unless $N_l=N_k$. Since the presynaptic sum in equation (2.2) runs over $j=1,\dots,N_l$, the natural Bernoulli probability here is $K/N_l$ if the aim is to give each neuron $K$ inputs from each source population on average. This is a small line, but it propagates into the normalization of the mean-field terms. I would correct the connection probability or state explicitly that the factors $N_l/N_k$ have been absorbed into the coupling constants.

---

### 4. The low-rate width estimate does not follow from equation (5.14)

**Status**: [Pending]

**Quote**:
> In the low rate limit, $m_{0}\ll 1$, equation 5.12 can be solved using equations 4.13 through 4.15, yielding to leading order,
>
> $q_{k}=m_{k}^{2}+O(m_{k}^{2}/|\log m_{k}|).$ (5.14)
>
> Thus, if the network evolves to a state with low average activity levels, $m_{k}\ll 1$, $q_{k}$ is slightly larger than $m_{k}^{2}$. The fact that $q_{k} \ll m_{k}$ implies that the balanced state is characterized by strong temporal fluctuations in the activity of the individual cells. On the other hand, the fact that $q_{k}$ is not exactly equal to $m_{k}^{2}$ reflects the spatial inhomogeneity in the time-averaged rates within a population. Equation 5.14 implies that when the mean activity $m_{k}$ decreases, the width of the distribution is proportional to $(m_{k})^{3/2}$; it decreases faster than the mean $m_{k}$.

**Feedback**:
The narrowing claim is fine, but the stated power law is not what equation (5.14) gives. Since $q_k=\mathbb E[(m_i^k)^2]$ and $m_k=\mathbb E[m_i^k]$, the variance of the rate distribution is $q_k-m_k^2=O(m_k^2/|\log m_k|)$. The corresponding width is therefore $O(m_k/\sqrt{|\log m_k|})$, not $O(m_k^{3/2})$. That still supports the qualitative point that the relative width shrinks to zero at low rates, but the specific scaling should be corrected.

---

### 5. Equation (7.15) uses the wrong density transformation

**Status**: [Pending]

**Quote**:
> In general, for small $m_k$, a threshold distribution $P(\theta)$ will yield a rate distribution $\rho_k$ for population $k$ that is given by
>
> $$
> \rho_k(m) = \sqrt{2\pi} P\left(-\sqrt{\alpha_k} (h(m) + \tilde{h}_k)\right) e^{h^2(m)/2}, \tag{7.15}
> $$
>
> where $\tilde{h}_k \equiv h(m_k)$ is determined by
>
> $$
> \int dm \, m \rho_k(m) = m_k. \tag{7.16}
> $$

**Feedback**:
This change of variables is not consistent with equation (7.1). From $m=H((\theta-u_k)/\sqrt{\alpha_k})$, one gets $\theta=u_k+\sqrt{\alpha_k}h(m)$, so the density should be
$\rho_k(m)=\sqrt{2\pi\alpha_k}\,P\!\left(u_k+\sqrt{\alpha_k}h(m)\right)e^{h(m)^2/2}$.
The printed formula drops the $\sqrt{\alpha_k}$ Jacobian and replaces the shift by $u_k$ with $-\sqrt{\alpha_k}\tilde h_k$, which is not the same object once thresholds are heterogeneous. This is worth fixing because equations (7.12)-(7.17) are supposed to summarize the general threshold-to-rate map.

---

### 6. The single-cell mean-field equation is missing the ensemble average

**Status**: [Pending]

**Quote**:
> $$
> \tau_{k} \frac{d}{dt} m_{k}^{i}(t) = - m_{k}^{i}(t) + \Theta (u_{k}^{i}(t)), \tag{A.2}
> $$

**Feedback**:
Given the definition in equation (A.1), the right-hand side of (A.2) should still be averaged over the same ensemble. The standard asynchronous-update derivation gives
$\tau_k \dot m_k^i(t)=-m_k^i(t)+\langle \Theta(u_k^i(t))\rangle$.
Without those brackets, equation (A.2) mixes an averaged left-hand side with a microscopic right-hand side. That is easy to repair, but it should be repaired because appendix A is where the closure is being set up formally.

---

### 7. The response-time estimate in Section 9 uses the reciprocal scale

**Status**: [Pending]

**Quote**:
> Thus, the initial response is highly nonlinear due to the initial disruption of the balance in the inputs and the highly nonlinear dynamics of single cells. This initial large response causes a fast rate of increase in the population rates, since $\delta m_k \approx \tau_k^{-1} dt \Delta P_k$, implying that $\delta m_k$ reaches the value $A_k \delta m_0$ in time of order $\tau_k / \delta m_0 \approx \tau_k / \sqrt{K}$; see the dotted line in Figure 13.

**Feedback**:
The final timescale estimate is reversed. If the initial slope is of order $\Delta P_k/\tau_k=O(1/\tau_k)$ and the total rate change needed is $A_k\delta m_0=O(1/\sqrt K)$, then the time to reach the new balanced value is of order $\tau_k A_k\delta m_0/\Delta P_k=O(\tau_k/\sqrt K)$. The printed expression $\tau_k/\delta m_0$ instead scales like $\tau_k\sqrt K$. The conclusion about fast tracking survives, but the intermediate estimate should be corrected so the argument is internally consistent.

---

### 8. The ramp formula does not match the protocol described in the text

**Status**: [Pending]

**Quote**:
> Figures 14 and 15 show a comparison of the tracking capabilities of a balanced network with $K = 1000$ and an unbalanced network with threshold linear units. Between $t = 0$ and $t = 1$, the networks are at equilibrium. In Figure 14 the external activity is ramped between $t = 1$ and $t = 2$,
>
> $$
> m _ {0} (t) = m _ {0} + v _ {0} t, \tag {9.13}
> $$
>
> and after $t = 2$ $m_0$ is kept constant again.

**Feedback**:
As written, equation (9.13) starts the ramp from $m_0+v_0$ at $t=1$, not from the equilibrium value $m_0$. If the ramp really runs only on the interval $1\le t\le2$, the formula should be written on that clock as $m_0(t)=m_0+v_0(t-1)$. This is a small editorial fix, but it matters because the current version adds an unintended jump at the start of the ramp.

---

### 9. Equation (A.9) is a variance, not a standard deviation

**Status**: [Pending]

**Quote**:
> ) / \sqrt{2\pi}$. From the above statistics of $n_l$, one obtains that the average input, relative to threshold, $u_k$ into a cell of population $k$ given by
>
> $$
> u_{k} = \left(E_{k} m_{0} + J_{kE} m_{E} + J_{kI} m_{I}\right) \sqrt{K} - \theta_{k} \tag{A.8}
> $$
>
> and standard deviation of the input $\alpha_{k}$
>
> $$
> \alpha_{k} = \left(J_{kE}\right)^{2} m_{E} + \left(J_{kI}\right)^{2} m_{I}, \tag{A.9}
> $$
>
> from which equati

**Feedback**:
The quantity in equation (A.9) is the variance of the input fluctuations. Equation (A.7) already uses $\sqrt{\alpha_k}$ as the Gaussian standard deviation, so the prose here should match that notation. This is minor, but in a derivation-heavy appendix it is better not to swap variance and standard deviation.

---
