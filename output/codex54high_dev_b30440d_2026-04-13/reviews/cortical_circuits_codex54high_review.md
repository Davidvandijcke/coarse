# Chaotic Balanced State in a Model of Cortical Circuits

**Date**: 04/13/2026
**Domain**: natural_sciences/neuroscience
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Outline**

The paper has a strong central idea: sparse strong excitation and inhibition can cancel at leading order and leave fluctuation-driven activity with weak pairwise correlations. The main problem is that several headline claims go beyond what the analysis actually pins down. The balanced-state construction is asymptotic and fairly tuned, the evidence for chaos is tied to a discontinuous binary update rule rather than a more standard dynamical notion, and a number of simulation-style figures are generated from the mean-field Gaussian theory instead of serving as an independent check on it.

The paper makes an important conceptual move by separating asynchronous irregular activity from synchronized chaos and by giving a tractable mean-field treatment of a sparse E-I network. The derivations around the large-\(K\) balance conditions and the discussion of rate heterogeneity are interesting and in places quite elegant. Still, by top-venue standards the paper overstates how general and how fully established its main conclusions are.

**The mean-field theory is presented as exact under assumptions that are not fully controlled**

Section 3 states that the mean-field theory is exact in the large-network limit, while the actual construction takes \(N \to \infty\) at fixed \(K\) and then simplifies further by sending \(K \to \infty\) (Section 3, equation 3.1, Appendix A.1). The derivation of equations 3.3 to 3.6 also drops correlations between activity and the realized connectivity, and it relies on Gaussian input statistics in a recurrent network that is later argued to be strongly chaotic. That may be fine asymptotically, but the paper never quantifies the size of the neglected terms or shows when the two-step limit is a good proxy for the finite \(N\), finite \(K\) systems used in figures. This matters because the main claims about balance, weak correlations, and rapid tracking all rest on equations 3.3 to 3.6. Readers need to know whether these are theorem-level statements for the stated architecture or leading-order heuristics whose accuracy depends on a restricted regime. A revision should make the order of limits explicit throughout, state the independence assumptions up front, and add direct finite-size tests of equations 3.3 to 3.6 as \(N\) and \(K\) vary.

**The balanced state is less broadly established than the framing suggests**

The abstract and introduction describe a balanced state that emerges dynamically over a wide range of parameters, but Section 4 shows that existence without saturation already requires the inequalities in equations 4.5, 4.9, and 4.10, along with an external drive that scales like \(\sqrt{K}\) (equation 2.3). Section 10.2 then adds that if the external input is only order one, maintaining balance needs near-cancellation in the denominators of equations 4.3 and 4.4, which is essentially a tuning statement. That is a narrower claim than the framing in the abstract, especially if the biological interpretation depends on strong feedforward drive. The issue is not that the construction is invalid; it is that the paper sells a generic mechanism while the analysis supports a particular asymptotic regime with specific parameter inequalities. This matters for publishability because the central contribution is the existence and relevance of the balanced regime. The paper should separate clearly what is proved for the strong-input, strong-synapse scaling from what is merely suggested for cortical circuits, and it should show how much parameter volume supports the balanced solution at finite \(K\).

**The evidence for chaos is tied to a singular binary update rule rather than a stable notion of network chaos**

Section 8 defines chaos through the divergence of the Hamming distance between two trajectories and concludes from equation 8.9 that the Lyapunov exponent is infinite. In a binary threshold system with discontinuous updates, that conclusion largely reflects the infinite microscopic gain of the threshold map, which the authors themselves note, rather than a conventional characterization of a chaotic attractor. The paper therefore slides between two claims: sensitivity to single-cell perturbations in a discontinuous automaton and chaos as a meaningful macroscopic explanation for cortical irregularity. Those are not the same thing. The concern is sharpened by Appendix B, where the update schedule can be stochastic or deterministic yet the same mean-field equations hold; the manuscript never shows that the claimed chaotic behavior is robust across these variants rather than being an artifact of the discrete update rule. A stronger version of the paper would either narrow the claim to rapid desynchronization of nearby trajectories in this binary model or supply a more standard dynamical analysis and finite-size simulations that distinguish chaos from threshold-induced branching.

**Key temporal-statistics figures validate the theory with samples drawn from the theory itself**

Sections 5.2 and 5.3 are meant to support the claims about fluctuation-driven inputs, Poisson-like spiking, and the structure of excitation-inhibition cancellation. But Figures 6 and 7 are generated by sampling Gaussian processes whose mean, variance, and autocorrelation are themselves taken from the mean-field theory, rather than by measuring these quantities in direct network simulations. That is useful as an illustration of what the theory implies, but it is not an independent check that the original network actually produces those statistics. This matters because the paper leans heavily on temporal irregularity as evidence that the balanced state is real and distinct from frozen or synchronized regimes. The same issue appears in the Poisson comparison around equation 5.18: part of the near-Poisson behavior may come from the asynchronous update rule and the definition of a spike as a 0-to-1 transition, not from the balanced mechanism alone. The revision should separate theory-generated surrogates from genuine simulations and add side-by-side validation of autocorrelations, ISI statistics, and input decomposition in the original network model.

**The stability analysis does not fully justify the phase portrait described after instability**

The split between local perturbations smaller than \(O(K^{-1/2})\) and global perturbations larger than that scale is an interesting feature of Section 6. However, the claims that follow go beyond what is established by equations 6.1 to 6.6. In Section 6.3, the existence of a balanced limit cycle of amplitude \(O(K^{-1/2})\), an unstable separating cycle, and the three instability regimes are inferred from schematic arguments and piecewise-threshold dynamics, not derived for the full mean-field system in equation 3.3. That leaves a gap between the formal local and global conditions and the asserted global phase portrait. This gap matters because the manuscript uses these results to argue that the balanced state is strongly stabilizing and to delimit where the theory applies. The paper needs either a proper bifurcation analysis of the full reduced dynamics or direct simulations showing that the proposed regimes in Section 6.3 do in fact occur and match the predicted boundaries \(\tau_L\) and \(\tau_G\).

**Robustness to heterogeneity and nonideal inputs is too narrow for the biological framing**

The only substantial heterogeneity analysis is the threshold-disorder study in Section 7, and even there the conclusions depend strongly on whether the tail is Gaussian or bounded. The paper does not test how the balanced asynchronous state behaves under structured connectivity, correlated external drive, synaptic delays, or more general disorder in synaptic strengths, even though the abstract and discussion frame the mechanism as an account of cortical irregularity. Appendix B shows some robustness to the timing of updates at the mean-field level, but that is much narrower than robustness of the state itself. This omission matters because a top-field theory paper should show that its main phenomenon is not a narrow consequence of homogeneous random connectivity plus regular external input. As written, the biological interpretation in Section 10.4 is stronger than the supporting analysis. The revision should either narrow the framing to a stylized model result or add robustness tests for at least one structured-connectivity perturbation, one nontrivial external-input process, and one alternative microscopic timing rule.

**The paper overreaches when linking the model to cortical data and function**

The manuscript moves from a stylized binary-network theory to claims about cortical irregularity, firing-rate distributions, and fast tracking of stimuli. The weakest point is Section 7.3, where a qualitative match to an unpublished prefrontal rate histogram is presented as support for the predicted skewed distribution, even though the comparison uses selected active neurons and does not test the scaling claims of equations 7.11 to 7.17. Section 9 makes a similar leap on function: the fast-tracking result holds for small changes around a balanced operating point under the bounds in equation 9.8, but the abstract states more broadly that the network can track time-dependent input on times much shorter than a single-cell time constant. Those are stronger biological statements than the model warrants. This matters because the novelty of the paper is not only mathematical; it is sold as explanatory for cortex. The biological discussion should be tightened to say exactly which features are model consequences and which are speculative analogies, unless the authors add direct tests in a more realistic spiking model or against data.

**Pairwise cross-correlations are asserted, not worked out**

The paper says the theory gives a complete statistical characterization of the balanced state, and the abstract leans hard on weak cross-correlations as the feature that separates this regime from synchronized chaos. But the manuscript never actually derives a pairwise correlation function or even a finite-size scaling law for it. Section 5 computes rate distributions and autocorrelations of single cells, then jumps to the statement that correlations between different cells are very small. That missing piece matters because the paper's main contrast with earlier chaotic network models is about shared fluctuations, not only single-neuron irregularity. The revision should add an explicit calculation of the pairwise covariance or cross-correlation function for two neurons, distinguishing unconnected pairs from directly connected pairs, and show from the same mean-field expansion that typical correlations are \(O(1/N)\) while the largest connected-pair contribution is \(O(1/\sqrt{K})\). A side-by-side simulation across increasing \(N\) at fixed \(K\), using the Figure 3 parameter set, would make the asynchronous claim concrete.

**Fast tracking lacks a frequency-response characterization**

The functional claim in the abstract is that the balanced network can track time-dependent input on time scales much shorter than a single-cell time constant. Section 9 gives step, ramp, and sinusoidal examples, but it never turns that statement into a clean input-output characterization. As a result, the reader does not learn the bandwidth of the effect, how the gain and phase lag depend on \(\tau\), or how the predicted speedup scales with \(K\). For a theory paper making a functional claim, this is missing core content rather than a cosmetic extension. The natural addition is a linear-response calculation around the balanced fixed point for \(m_0(t)=m_0+\epsilon e^{i\omega t}\), leading to explicit complex susceptibilities \(\chi_E(\omega)\) and \(\chi_I(\omega)\) and a cutoff frequency that can be compared with the threshold-linear network of equations 9.10 to 9.12. Then Figures 14 to 16 would read as checks of a stated transfer function, not just examples.

**No explicit failure case for balance conditions**

Equations 4.9 and 4.10 are the gatekeepers of the balanced state, and the paper repeatedly presents the resulting regime as a real alternative to ordinary tonic or saturated behavior. Still, the manuscript never gives a matched network example that violates these inequalities and visibly loses the balanced asynchronous state. The algebraic discussion of unbalanced solutions is useful, but it does not show the reader what the same model does when the restrictions fail. That leaves the main result less sharp than it should be, because the paper never demonstrates where the mechanism breaks. A concrete addition would be to keep the Figure 3 setup and then change one ingredient at a time, for example set \(J_E<1\) or choose \(E/I<J_E/J_I\), solve equations 3.7 and 6.4 to 6.6, and simulate the network to show the resulting silent, saturated, or strongly unbalanced oscillatory regime. That would show that the balance conditions are doing real work rather than merely organizing notation.

**Strong-synapse advantage under heterogeneity is not demonstrated**

One of the paper's strongest broader claims is in Section 10.2: the \(1/\sqrt{K}\) scaling is special because it still supports fluctuating low-rate activity with broad rate heterogeneity, whereas conventional \(1/K\) scaling freezes once thresholds vary. Yet the manuscript never presents a matched example that puts those two scalings under the same threshold disorder and compares the outcomes directly. Section 7 studies heterogeneous thresholds only for the strong-synapse model, and Figure 17 studies the weak-synapse model only in the homogeneous case. That gap matters because the skewed long-tailed rate distribution is one of the paper's headline consequences, and the claimed advantage over conventional scaling rests on this comparison. The paper should add a side-by-side computation for a specific threshold distribution, such as the uniform law on \([-\Delta/2,\Delta/2]\) with \(\Delta=0.2\), holding \(E,I,J_E,J_I,\tau\) fixed while comparing \(J_{kl}/\sqrt{K}\) to \(J_{kl}/K\). Reporting \(\rho_k(m)\), \(q_k/m_k\), and direct simulations as \(K\) grows would show whether the strong-synapse regime really is the unique nontrivial case the discussion claims.

**Recommendation**: major revision. The paper has a real idea and several interesting analytical results, but the main framing is ahead of the evidence in three places: exactness of the mean-field reduction, the status of the chaos claim, and the breadth of the biological interpretation. I would be positive on a revision that narrows the claims and adds direct validation of the asymptotic theory in finite networks.

**Key revision targets**:

1. Demonstrate, with direct network simulations across several \(N\) and \(K\), how accurately equations 3.3 to 3.6 predict rates, variances, cross-correlations, and finite-\(K\) corrections, and state the order-of-limits assumptions explicitly.
2. Replace or substantially strengthen Section 8 by using a chaos metric appropriate for discontinuous binary dynamics, and show that the result is not just a threshold artifact of the microscopic update rule.
3. Validate the temporal-statistics claims with measurements from the original network rather than only Gaussian surrogates, including autocorrelations, ISI distributions, and excitation-inhibition cancellation at the single-cell level.
4. Either provide a proper bifurcation analysis of the full reduced dynamics behind Section 6.3 or show by simulation that the predicted instability regimes and stability boundaries actually occur.
5. Tone down the cortical and functional claims unless additional robustness tests are added for structured heterogeneity, correlated or noisy external inputs, and alternative microscopic timing rules.

**Status**: [Pending]

---

## Detailed Comments (10)

### 1. Connectivity Probability Uses the Wrong Population Size

**Status**: [Pending]

**Quote**:
> The connection between the $i$th postsynaptic neuron of the $k$th population and the $j$th presynaptic neuron of the $l$th population, denoted $J_{kl}^{ij}$ is $J_{kl} / \sqrt{K}$ with probability $K/N_{k}$ and zero otherwise. Here $k,l=1,2$. The synaptic constants $J_{k1}$ are positive and $J_{k2}$ negative. Thus, on average, $K$ excitatory and $K$ inhibitory neurons project to each neuron.

**Feedback**:
Under the Bernoulli rule written here, a fixed postsynaptic cell in population $k$ receives $N_l(K/N_k)=K N_l/N_k$ presynaptic partners from population $l$ on average. That equals $K$ only if $N_l=N_k$. The sentence after the definition therefore does not follow from the model as written. If the intention is $K$ incoming excitatory and $K$ incoming inhibitory inputs per cell, the connection probability should scale as $K/N_l$. If $K/N_k$ is intentional, the later mean-field formulas need to carry the resulting $N_l/N_k$ factors explicitly.

---

### 2. Equations 4.9 and 4.10 Do Not Eliminate All Unbalanced States

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
This conclusion is too strong. A mixed branch with $m_I=1$ and $m_E=J_E-E m_0+O(K^{-1/2})$ remains self-consistent whenever $0<J_E-E m_0<1$ and $u_I=[(J_E-J_I)-(E-I)m_0]\sqrt{K}+O(1)>0$. For example, $E=2$, $I=1$, $J_E=1.2$, $J_I=0.8$, $m_0=0.15$ satisfies 4.9, 4.10, and $A_k m_0<1$, yet gives $m_E\approx0.9$ and $u_I\approx0.25\sqrt{K}$. The fully saturated branch also survives when $u_E=(E m_0+1-J_E)\sqrt{K}>0$ and $u_I=(I m_0+1-J_I)\sqrt{K}>0$; $E=10$, $I=1$, $J_E=2$, $J_I=1.01$, $m_0=0.105$ is one example. This section needs either extra bounds on $m_0$ or a narrower statement about what 4.9 and 4.10 exclude.

---

### 3. Equation 7.15 Is Not the General Change-of-Variables Formula

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
Equation 7.15 is not the general pushforward of the threshold law in 7.1. From $m=H((\theta-u_k)/\sqrt{\alpha_k})=H(-h(m))$, one gets $\theta=u_k-\sqrt{\alpha_k}\,h(m)$ and therefore
$\rho_k(m)=\sqrt{2\pi\alpha_k}\,P\!\left(u_k-\sqrt{\alpha_k}\,h(m)\right)e^{h^2(m)/2}$.
Two pieces are missing in the printed formula. First, the Jacobian contributes a factor $\sqrt{\alpha_k}$. Second, the shift is set by $u_k$, or equivalently $-u_k/\sqrt{\alpha_k}$, not by $\tilde h_k=h(m_k)$; for a general threshold law, 7.2 does not imply $m_k=H(-u_k/\sqrt{\alpha_k})$. The later asymptotics should be rebuilt from the corrected expression.

---

### 4. Deterministic Common-Period Updates Are Not Dynamically Equivalent to Equation 3.3

**Status**: [Pending]

**Quote**:
> To show that this is not the case, we define here a completely deterministic dynamic model and show that it leads to exactly the same equations for the mean rates of activity as those given above.

**Feedback**:
The appendix proves less than this opening sentence claims. The common-period deterministic rule yields equation B.2, which has a uniform memory kernel on $[0,\tau_k]$. Equation 3.3 is equivalent to the exponential kernel in B.4. Those kernels are not the same for time-varying inputs: if $F_k(t)=e^{\lambda t}$, B.2 gives the factor $(1-e^{-\lambda \tau_k})/(\lambda \tau_k)$, while B.4 gives $1/(1+\lambda \tau_k)$. They agree only in the stationary limit $\lambda=0$. The appendix should say that the common-period deterministic rule shares the same fixed points, and that full dynamical equivalence requires the heterogeneous update-interval distribution introduced later in B.3-B.4.

---

### 5. The Abstract States the Long Tail Too Broadly

**Status**: [Pending]

**Quote**:
> The activity levels of single cells are broadly distributed, and their distribution exhibits a skewed shape with a long power-law tail.

**Feedback**:
This reads as a generic property of the balanced state itself. The paper does not establish that. The skewed long-tailed rate distribution appears only after threshold heterogeneity is added in section 7, and section 7 then splits the result by the tail behavior of the threshold distribution. The abstract should make that condition explicit instead of presenting the long tail as a general feature of the homogeneous model.

---

### 6. Boundary Clipping Is Not a Solution of Equations 4.17 and 4.18

**Status**: [Pending]

**Quote**:
> Whenever we refer in subsequent figures to explicit values for $K$, we use equations 4.17 and 4.18, unless otherwise stated. Except for thresholding the population rates, the finite $K$ corrections affect only the quantitative results, not the qualitative predictions of the simple large $K$ theory.

**Feedback**:
Equations 4.17 and 4.18 use $h(m)$ from 4.11, which is defined only for $0<m<1$. Once a rate hits 0 or 1, these Gaussian fixed-point equations no longer apply at the boundary. Clipping the output by hand may be useful for plotting, but it is not a solution of the displayed system. Near the edge, the paper should switch back to the exact finite-$K$ fixed-point equation A.5 rather than treat thresholding as part of the same approximation.

---

### 7. Equation 6.4 Does Not Show Decay to the Balanced Point

**Status**: [Pending]

**Quote**:
> In fact, since the perturbation destroys the balance between excitation and inhibition, $H(-u_{k}/\sqrt{\alpha_{k}})$ of equation 3.3 can be approximated by $\Theta(u_{k})$; hence the evolution of the perturbations is described by
>
> $\tau_{k}\frac{d}{dt}\delta m_{k}(t)=-\delta m_{k}(t)+\Theta(\delta m_{E}-J_{k}\delta m_{I})-m_{k}.$ (6.4)
>
> These equations are piecewise linear and therefore can be solved explicitly. One finds that the solution of these equations decays to zero

**Feedback**:
With the paper's convention $\Theta(0)=0$, substituting $\delta m_E=\delta m_I=0$ into 6.4 gives $\tau_k\dot{\delta m}_k=-m_k$, not 0. So the reduced Heaviside system does not have the balanced point as an equilibrium, and its trajectories cannot literally decay to zero. What 6.4 can show is weaker: order-one perturbations are driven back toward the narrow regime where the Heaviside replacement stops being valid. The prose after 6.4 should be narrowed to that claim.

---

### 8. Equation 8.9 Gives Singular Separation, Not Exponential Growth

**Status**: [Pending]

**Quote**:
> Since $\alpha_{k}-\gamma_{k} \propto D_{k}$, equation 8.9 has a growing solution even if $D_{k}(0)=0$. This implies that the Lyapunov exponent $\lambda_{L}$ is infinitely large in the balanced state.

**Feedback**:
Equation 8.9 gives a short-distance law of the form $\dot D_k=c_k\sqrt{D}+o(\sqrt{D})$, not $\dot D_k=\lambda D_k+o(D_k)$. Solving the leading term gives $D_k(t)=\left(\sqrt{D_k(0)}+c_k t/2\right)^2$, which is a singular short-time desynchronization law rather than an exponential one. That is enough to show extreme sensitivity of this binary threshold dynamics, but it is not a standard Lyapunov-exponent derivation of chaos. The wording here should be tightened accordingly.

---

### 9. The Fast-Tracking Timescale Calculation Has a Reciprocal Error

**Status**: [Pending]

**Quote**:
> This initial large response causes a fast rate of increase in the population rates, since $\delta m_k \approx \tau_k^{-1} dt \Delta P_k$, implying that $\delta m_k$ reaches the value $A_k \delta m_0$ in time of order $\tau_k / \delta m_0 \approx \tau_k / \sqrt{K}$; see the dotted line in Figure 13.

**Feedback**:
The middle step scales the wrong way. From $\delta m_k\approx \tau_k^{-1}dt\,\Delta P_k$, the time needed to reach the new balanced value is $dt\approx \tau_k A_k\delta m_0/\Delta P_k$. Under the paper's own assumption $\delta m_0\sqrt{K}=O(1)$ and with $\Delta P_k=O(1)$, this is $O(\tau_k/\sqrt{K})$. The final fast timescale is plausible, but the algebra in this sentence should be corrected.

---

### 10. The $K^{-\alpha}$ Generalization Needs an Explicit External-Input Scaling

**Status**: [Pending]

**Quote**:
> inally, the model can be generalized to a model with synaptic strengths that scale as $K^{-\alpha}$, with $0&lt;\alpha&lt;1$. Of course, these models can be distinguished from the present model only in the large $K$ limit. In this limit, the net average inputs into the populations scale as $K^{1-\alpha}$, while the quenched and temporal fluctuations in the inputs scale as $K^{1/2-\alpha}$. Therefore the leading order in the inputs has to cancel, leading to the balance condition.

**Feedback**:
This paragraph changes the recurrent mean input from $O(\sqrt{K})$ to $O(K^{1-\alpha})$, but it never states a matching rescaling of the external drive. If $u_k^0$ stays at $E_k m_0\sqrt{K}$, then for $\alpha>1/2$ the external term dominates the recurrent mean, while for $\alpha<1/2$ it is subleading. In that case the stated leading-order cancellation is not the right balance condition. The generalized model needs its external-input scaling written down explicitly before the rest of the argument goes through.

---
