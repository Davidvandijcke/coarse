# Inference in molecular population genetics

**Date**: 3/3/2026, 8:58:55 PM
**Domain**: Example
**Taxonomy**: Demo
**Filter**: Active comments

---

## Overall Feedback

Here are some high-level reactions to the text.

The paper proceeds in three main stages. First, it establishes a characterisation of the optimal importance sampling proposal for coalescent-based likelihood inference by analysing the time-reversal of the genealogical process. Second, it develops a practical approximation, $Q_\theta^{\mathrm{SD}}$, by substituting heuristic conditional sampling probabilities into the optimal backward rates. Third, it applies this method to simulated sequence data, microsatellites, and infinite-sites models, comparing performance against the Griffiths-Tavaré scheme and existing MCMC approaches.

The methodological core relies on replacing the exact conditional sampling distribution $\pi$ with an approximation $\hat\pi$. While the optimality of the proposal is exact for parent-independent mutation (PIM) and the $n=1$ case, the text extends this to broader mutation models heuristically. Providing a proof for a non-trivial class beyond PIM would bridge the gap between the theoretical characterisation and the practical algorithm. The paper would also benefit from benchmarking against independently validated references and defining specific diagnostic criteria for weight degeneracy.

**Status**: [Pending]

---

## Detailed Comments (15)

### 1. Unclear description of ascertainment correction

**Status**: [Pending]

**Quote**:
> For the IS schemes that we have considered, assuming the infinite sites mutation model, the ascertainment effect can be accommodated by labelling every lineage which leads to any chromosome in the panel as a panel lineage and adapting both $P_{\theta}(\mathcal{H})$ and $Q_{\theta}(\mathcal{H})$ so that mutations can occur only on panel lineages.

**Feedback**:
The description of the SNP ascertainment correction in this paragraph is rather compressed, and the role of the "panel lineage" labelling could be clearer. As written, labelling "every lineage which leads to any chromosome in the panel" as a panel lineage and then allowing mutations "only on panel lineages" would in principle include branches ancestral to all panel members as well as those ancestral to a proper subset. For the two‑stage design you describe, the ascertained sites are specifically those that are polymorphic within the panel, so the mutation for any ascertained SNP must fall on a branch that partitions the panel, not on the trunk ancestral to the entire panel.

In the full inferential framework, consistency with the observed polymorphism in the panel will be enforced via the likelihood factor $\pi_\theta(A_n \mid \mathcal{H})$, and mutations on branches that make the panel monomorphic will automatically be given zero weight. However, the current wording does not spell out this interaction and could be read as if restricting mutations to panel lineages alone were sufficient to encode the ascertainment scheme. It would help readers if you could make explicit how the event "SNP is polymorphic in the panel" is imposed in your IS formulation, and in particular distinguish between branches ancestral to all panel members and those that genuinely partition the panel.

---

### 2. Proposed extension for long sequences is unclear

**Status**: [Pending]

**Quote**:
> The effect of the non-varying sites could then be taken into account by the factor $\pi_{\theta}\left(A_{n} \mid \mathcal{H}^{(i)}\right)$ in estimator (9), which could be calculated by the peeling algorithm (to do this it would be necessary to apply IS to the full typed ancestry $\mathcal{A}$ of the sample).

**Feedback**:
The brief discussion of long sequences in Section 6.2 is difficult to interpret in light of the earlier definitions of $\mathcal{H}$, $\mathcal{A}$ and $\pi_\theta(\cdot \mid \cdot)$. Earlier in the paper, $\mathcal{H}$ is defined as a history without times or topology, and equation (2) defines $\pi_\theta(A_n \mid \mathcal{H})$ as a purely combinatorial term depending only on $H_0$, independent of $\theta$ and of any tree structure. In contrast, the peeling algorithm takes as input a fully specified genealogy with branch lengths (part of $\mathcal{A}$) and computes a sequence likelihood $P_\theta(A_n \mid \mathcal{G})$.

In the quoted sentence you suggest that "the effect of the non‑varying sites could then be taken into account by the factor $\pi_\theta(A_n \mid \mathcal{H}^{(i)})$ … which could be calculated by the peeling algorithm," with a parenthetical remark that this would require applying IS to the full typed ancestry $\mathcal{A}$. As it stands, this mixes two different notions: the earlier $\pi_\theta(A_n \mid \mathcal{H})$ cannot be evaluated by peeling, and peeling cannot be applied at the level of $\mathcal{H}$ alone. The parenthesis hints at a switch of missing data from $\mathcal{H}$ to $\mathcal{A}$ for this extension, but that switch and the associated change in the meaning of the likelihood factor are not made explicit.

For readers interested in implementing such an extension, it would be useful to clarify that the peeling algorithm would be used to compute a full sequence likelihood $P_\theta(A_n \mid \mathcal{A}^{(i)})$ (or the contribution of the non‑varying sites) conditional on a sampled typed ancestry, and that in this context IS would operate on $\mathcal{A}$ rather than on histories $\mathcal{H}$ alone.

---

### 3. Interpretation of the transition matrix in Proposition 1(e)

**Status**: [Pending]

**Quote**:
> The distribution $\hat{\pi}\left(\cdot \mid A_{n}\right)$ is the stationary distribution of the Markov chain on $E$ with transition matrix

$$
T_{\beta \alpha}=\frac{\theta}{n+\theta} P_{\beta \alpha}+\frac{n_{\alpha}}{n+\theta},
$$

i.e. ... Remark 1. ... Property (e) provides a characterization of $\pi$ which is, in some more general settings not considered in this paper, more amenable to generalization than definition 1. The Markov transition matrix (21) is the transition matrix associated with the $(n+1)$ th line of the particle representation described in Section 4 (or the Moran model) when the first $n$ lines are fixed to be $A_{n}$.

**Feedback**:
The identification in Remark 1 of the matrix in equation (21) with "the transition matrix associated with the $(n+1)$th line of the particle representation … when the first $n$ lines are fixed to be $A_n$" appears to be too strong if taken literally. Under the particle representation in Section 4, a single lineage mutates at rate $\theta/2$ and copies from the $n$ fixed lines at total rate $n$, so the embedded jump chain for that lineage has transition probabilities
\[
T'_{\beta\alpha} = \frac{(\theta/2)P_{\beta\alpha} + n_\alpha}{\theta/2 + n},
\]
whereas the matrix (21) is
\[
T_{\beta\alpha} = \frac{\theta}{n+\theta}P_{\beta\alpha} + \frac{n_\alpha}{n+\theta}.
\]
These kernels are not identical for general $n$ and $\theta$; in particular, they differ by a factor of 2 in the relative weight of mutation versus copying events. The algebraic statement of Proposition 1(e) that $\hat\pi(\cdot\mid A_n)$ is the stationary distribution of $T$ is entirely correct, but the genealogical interpretation in Remark 1 seems to conflate this auxiliary chain with the exact jump chain of the $(n+1)$th line in the specified particle representation. It would be helpful to adjust the wording to clarify that (21) corresponds to a Markov chain that mixes mutation and copying steps in proportions governed by $\theta$ and $n$, rather than to the literal embedded chain of the particle representation with mutation rate $\theta/2$.

---

### 4. Justification for the infinite sites proposal distribution

**Status**: [Pending]

**Quote**:
> These problems are not insurmountable, but for simplicity we adapt our earlier approach to this context by analogy with proposition 2: recall that one method of simulating from our IS function $Q^{\mathrm{SD}}$ begins by choosing a chromosome uniformly at random from those present and assuming that this chromosome is involved in the most recent event backwards in time. ... Analogy with proposition 2 then suggests choosing the most recent event backwards in time by drawing a chromosome uniformly at random from those satisfying either (a) or (b). This procedure defines an IS function $Q^{\mathrm{SD}}$ which we note is independent of $\theta$, removing the need to specify a driving value.

**Feedback**:
Statement "for simplicity we adapt our earlier approach to this context by analogy with proposition 2 … This procedure defines an IS function $Q^{\mathrm{SD}}$ which we note is independent of $\theta$" initially made me wonder how closely the infinite‑sites sampler is tied to the general construction of $Q^{\mathrm{SD}}$ via Theorem 1 and Definition 2. The text does indicate that, because of technical complications (uncountable type space, non‑reversibility), you are now using a more heuristic, analogy‑based design: uniform choice over the chromosomes that could have been involved in the last event, rather than an explicit approximation to $Q^*_\theta$ built from a surrogate $\hat\pi$.

However, since $Q^{\mathrm{SD}}$ was earlier defined quite precisely as the θ‑dependent sampler obtained by substituting $\hat\pi$ into Theorem 1, reusing the symbol for this θ‑independent, heuristic infinite‑sites proposal may cause some readers to momentarily conflate the two constructions and to overestimate how directly Section 4's theory applies here.

It might therefore be helpful to make the nature of this extension more explicit: to state clearly that in the infinite‑sites case you are no longer working within the Theorem 1/Definition 2 framework but are instead introducing a separate, genealogically motivated proposal that happens to share the same notation; and perhaps to add a short remark on why you expect this uniform‑over‑eligible‑chromosomes choice to be a reasonable approximation in practice. This would clarify the relationship between the main theoretical development and the infinite‑sites special case without altering the substance of the method.

---

### 5. Formulation of the Griffiths-Tavaré estimator

**Status**: [Pending]

**Quote**:
> In the Griffiths-Tavaré method, view the problem of finding $\{p(\mathbf{n})\}$ as solving the system of linear
equations (34). Importance sampling techniques were used to obtain a solution of the equations. Rescale $P\left(H_{j} \mid H_{j-1}^{\prime}\right)$ and interpret as a probability distribution

$$
q\left(H_{j-1}^{\prime} \mid H_{j}\right)=p\left(H_{j} \mid H_{j-1}^{\prime}\right) / f\left(H_{j}\right)
$$

where $f\left(H_{j}\right)=\Sigma p\left(H_{j} \mid H_{j-1}^{\prime}\right)$. Then

$$
p\left(H_{j}\right)=f\left(H_{j}\right) \sum q\left(H_{j-1}^{\prime} \mid H_{j}\right) p\left(H_{j-1}^{\prime}\right),
$$

leading to an importance sampling representation

$$
p\left(H_{0}\right)=E_{q}\left\{f\left(H_{0}\right) f\left(H_{-1}\right) \ldots f\left(H_{-m}\right)\right\}
$$

with absorption at $-m$, where there first is a single ancestor of the sample. The proposal distribution for importance sampling is $q(\cdot \mid \cdot)$.

**Feedback**:
In the displayed importance sampling representation for the Griffiths–Tavaré method,
\[
p(H_0)=E_q\{f(H_0) f(H_{-1}) \ldots f(H_{-m})\},
\]
I found it difficult to reconcile the indexing with the recursion that precedes it. From
\[
p(H_j)=\sum_{H_{j-1}'} P(H_j\mid H_{j-1}')\,p(H_{j-1}')=f(H_j)\sum_{H_{j-1}'} q(H_{j-1}'\mid H_j)\,p(H_{j-1}'),
\]
iterating backwards until the first single-ancestor state \(H_{-m}\) leads to
\[
p(H_0)=E_q\Big\{p(H_{-m})\,f(H_0) f(H_{-1}) \cdots f(H_{-(m-1)})\Big\}.
\]
That is, the product over the normalising factors \(f(H_j)\) stops at the last non-absorbing configuration, and the terminal factor should be the boundary probability \(p(H_{-m})\) of the ancestral state. As written, the expression appears to include an extra factor \(f(H_{-m})\), which is not defined by \(f(H_j)=\sum_{H_{j-1}'} P(H_j\mid H_{j-1}')\) at the absorbing single-ancestor state. Clarifying that the final factor is \(p(H_{-m})\) (or that \(f(H_{-m})\) is being used as shorthand for this boundary term) would make the connection between the linear system (34) and the importance sampling representation precise.

---

### 6. Inverted description of microsatellite boundary conditions

**Status**: [Pending]

**Quote**:
> The implementation of our IS scheme is facilitated by centring the sample distribution near 10 repeats and truncating the type space $E$ to $\{0,1, \ldots, 19\}$ by insisting that all mutations to alleles of length 0 or 19 involve the gain or loss respectively of a single repeat.

**Feedback**:
The sentence

"The implementation of our IS scheme is facilitated by centring the sample distribution near 10 repeats and truncating the type space $E$ to $\{0,1, \ldots, 19\}$ by insisting that all mutations to alleles of length 0 or 19 involve the gain or loss respectively of a single repeat."

appears to have the gain/loss description at the boundaries reversed relative to the stepwise model defined just above. Under that model, the only forward-time mutation yielding allele 0 is 1→0, which is a loss of a repeat, and the only mutation yielding 19 is 18→19, which is a gain. As written, "gain or loss respectively" suggests the opposite mapping. This is very likely just an inversion in wording (for example, "loss or gain" or "from" instead of "to" would match the usual reflecting-boundary convention), and since the observed alleles are far from 0 and 19 the precise boundary behaviour has negligible effect on the examples. Nonetheless, it would be helpful to correct or clarify this sentence so that the intended direction of gain and loss at the lower and upper boundaries is unambiguous for readers wishing to reproduce the implementation.

---

### 7. Incorrect recursive weight formula in SIS discussion

**Status**: [Pending]

**Quote**:
> As with many SIS applications, both Stephens and Donnelly, and Griffiths and Tavaré (1994) propose trial densities $q_{0}(\mathcal{H})$ of the form

$$
q_{\theta}(\mathcal{H})=\prod_{i=0}^{-(m-1)} q_{\theta}\left(H_{i-1} \mid H_{i}\right)
$$

For such constructions we define the current weight (for $t \leqslant m$ )

$$
w_{-t}=\frac{p_{\theta}\left(H_{-(t-1)} \mid H_{-t}\right) \ldots p_{\theta}\left(H_{0} \mid H_{-1}\right)}{q_{0}\left(H_{-t} \mid H_{-(t-1)}\right) \ldots q_{0}\left(H_{-1} \mid H_{0}\right)} \equiv w_{-(t-1)} \frac{p_{\theta}\left(H_{-(t-1)} \mid H_{-1}\right)}{q_{0}\left(H_{-t} \mid H_{-(t-1)}\right)}
$$

**Feedback**:
The recursive definition of the current weight $w_{-t}$ in the Chen–Liu discussion appears to contain a small indexing typo. From the explicit product expression,
\[
w_{-t}=\frac{p_{\theta}\left(H_{-(t-1)} \mid H_{-t}\right)\cdots p_{\theta}\left(H_{0} \mid H_{-1}\right)}{q_{0}\left(H_{-t} \mid H_{-(t-1)}\right)\cdots q_{0}\left(H_{-1} \mid H_{0}\right)},
\]
one obtains the recursion
\[
w_{-t}=w_{-(t-1)}\,\frac{p_{\theta}\left(H_{-(t-1)} \mid H_{-t}\right)}{q_{0}\left(H_{-t} \mid H_{-(t-1)}\right)}.
\]
The printed version instead has $p_{\theta}\left(H_{-(t-1)} \mid H_{-1}\right)$ in this last factor, which is inconsistent with both the preceding line and the Markov structure, and should be corrected to condition on $H_{-t}$. In addition, the product notation $\prod_{i=0}^{-(m-1)} q_{\theta}(H_{i-1}\mid H_i)$ is somewhat non-standard; since $i$ is running over $0,-1,\dots,-(m-1)$ this is still correct, but a brief clarification or reindexing would improve readability.

---

### 8. Ambiguity in the stopping rule of Algorithm 1

**Status**: [Pending]

**Quote**:
> Step 3: if there are fewer than n+1 lines in the ancestry return to step 2 . Otherwise go back to the last time at which there were n lines in the ancestry and stop.

**Feedback**:
Statement of Step 3 initially made me pause, because the algorithm is run forward until there are $n+1$ lines and then the configuration is taken at the last time there were $n$ lines, rather than simply stopping when $n$ lines are first reached. The rule is unambiguous and is standard in the Ethier–Griffiths/Donnelly–Kurtz urn and look-down constructions that the paper cites, but its role in ensuring that the resulting ancestry has the stationary $n$‑coalescent distribution is not explained in the text. A brief remark indicating that this particular stopping rule corresponds to sampling the configuration of $n$ lines at a random split time in the stationary forward process would help readers who are less familiar with these constructions.

---

### 9. Inconsistent notation for the sample type space

**Status**: [Pending]

**Quote**:
> The history $\mathcal{H}$ thus includes a record of the states $\left(H_{-m}, H_{-(m-1)}, \ldots, H_{1}, H_{0}\right)$ visited by a Markov process beginning with the genetic type $H_{-m} \in E$ of the MRCA and ending with the genetic types $H_{0} \in E^{n}$ corresponding to the genetic types of a random sample. Here $m$ is random, and the $H_{i}$ are unordered lists of genetic types.

**Feedback**:
In the formal definition of the history $\mathcal{H}$, the state $H_{0}$ is described as belonging to $E^{n}$, which in the rest of the paper (and in standard notation) denotes ordered $n$-tuples. The very next sentence, however, says that the $H_{i}$ are 'unordered lists' (multisets), and later formulae and Fig. 1 consistently treat $H_{0}$ in this unordered, count-based way. This creates a small notational inconsistency in this sentence. It would be clearer either not to write $H_{0} \in E^{n}$ here, or to state explicitly that $H_{0}$ is an unordered multiset of $n$ types from $E$, reserving $E^{n}$ for ordered samples such as $A_{n}$.

---

### 10. Unproven normalization constant in Theorem 1

**Status**: [Pending]

**Quote**:
> The constant of proportionality $C$ is given by

$$
C=\frac{n(n-1+\theta)}{2},
$$

where $n$ is the number of chromosomes in $H_{i}$.
Proof. That $Q_{\theta}^{*}$ is in the class $\mathcal{M}$ follows from the Markov nature of $\mathcal{H}$... The value of $C$ follows from the fact that events must occur at total rate $k(k-1+\theta) / 2$ when there are $k$ lineages in the ancestry (see Stephens (2000)).

**Feedback**:
At first the sentence "The value of $C$ follows from the fact that events must occur at total rate $k(k-1+\theta)/2$ when there are $k$ lineages in the ancestry (see Stephens (2000))" made me think that more justification was needed, since the normalisation of the backward transition probabilities in (15) is not shown by direct summation. Then I understood that this step is simply using the standard fact for time-reversed continuous-time Markov chains observed at stationarity: the total exit rate from a state is unchanged under time reversal, so given that events in the (forward) ancestry occur at rate $k(k-1+\theta)/2$ when there are $k$ lineages, the same constant must normalise the backward rates. You might consider adding a brief remark or pointer that makes this Markov-process argument explicit, as readers who do not immediately recall this general result could pause at this point in the proof of Theorem 1.

---

### 11. Ambiguous notation in discussion of methods

**Status**: [Pending]

**Quote**:
> In the Stephens-Donnelly method,

$$
p\left(H_{j}\right)=\sum \frac{p\left(H_{j} \mid H_{j-1}^{\prime}\right)}{\hat{p}\left(H_{j-1}^{\prime} \mid H_{j}\right)} \hat{p}\left(H_{j-1}^{\prime} \mid H_{j}\right) p\left(H_{j-1}^{\prime}\right)
$$

The importance sampling representation is

$$
\begin{aligned}
p\left(H_{0}\right) & =E_{\hat{p}}\left\{\frac{p\left(H_{0} \mid H_{-1}\right)}{\hat{p}\left(H_{-1} \mid H_{0}\right)} \cdots \frac{p\left(H_{-m+1} \mid H_{-m}\right)}{\hat{p}\left(H_{-m} \mid H_{-m+1}\right)} p\left(H_{-m}\right)\right\} \\
& =E_{\hat{p}}\left\{\frac{p\left(\mathcal{H}_{\rightarrow}\right)}{\hat{p}\left(\mathcal{H}_{\leftarrow}\right)}\right\} .
\end{aligned}
$$

**Feedback**:
Statement (35) initially gave me the impression that \(p(H_j\mid H'_{j-1})\) was being used both for the recursion coefficients in equation (34) and for the forward transition probabilities \(p_\theta(H_i\mid H_{i-1})\) of the history-generating process defined earlier. Since these objects are distinct, this overloading of the symbol \(p(\cdot\mid\cdot)\) could momentarily mislead a reader trying to relate (35) directly to the coalescent dynamics. It might help if the discussion explicitly stated that in (35) the terms \(p(H_i\mid H_{i-1})\) are still the coefficients from the linear system (34), and that \(\hat p(\cdot\mid\cdot)\) is a probability kernel constructed from \(\hat\pi\) used purely as a proposal for solving those equations, rather than as an approximation to the forward transition kernel in equation (1).

---

### 12. Possible notational inconsistency in proof of Theorem 1

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> P\left\{\Upsilon_{\mathrm{m}} \cap A_{k}(t-\delta)=\left(\alpha_{1}, \ldots, \alpha_{k-1}, \beta\right) \mid A_{k}(t)=\left(\alpha_{1}, \ldots, \alpha_{k-1}, \alpha\right)\right\} & \\
\quad= & \frac{P\left\{\Upsilon_{\mathrm{m}} \cap A_{k}(t-\delta)=\left(\alpha_{1}, \ldots, \alpha_{k-1}, \beta\right) \cap A_{k}(t)=\left(\alpha_{1}, \ldots, \alpha_{k-1}, \alpha\right)\right\}}{P\left\{A_{k}(t)=\left(\alpha_{1}, \ldots, \alpha_{k-1}, \alpha\right)\right\}} \\
& =\frac{\pi\left(\alpha_{1}, \ldots, \alpha_{n-1}, \beta\right) \delta \theta P_{\beta \alpha} / 2}{\pi\left(\alpha_{1}, \ldots, \alpha_{n-1}, \alpha\right)}+o(\delta)

**Feedback**:
At first the appearance of $\pi(\alpha_1,\ldots,\alpha_{n-1},\beta)$ and $\pi(\alpha_1,\ldots,\alpha_{n-1},\alpha)$ in the middle line of this display made me think that the stationary distribution was being evaluated on an $n$-dimensional argument, even though the surrounding setup is explicitly for $k$ ancestral lineages with $A_k(t)=(\alpha_1,\ldots,\alpha_{k-1},\alpha)$. Then I understood from the preceding and following lines, and from the rewrite in terms of $\pi(\beta\mid A_k-\alpha)$ and $\pi(\alpha\mid A_k-\alpha)$, that these factors must correspond to $\pi(\alpha_1,\ldots,\alpha_{k-1},\beta)$ and $\pi(\alpha_1,\ldots,\alpha_{k-1},\alpha)$ and that the use of $n-1$ here is simply an indexing slip. It might nevertheless be helpful to correct these subscripts (and, if you wish, to note that $\pi$ is being used generically for the appropriate $k$-dimensional marginal of the stationary distribution) so that the dimension of the state space is completely consistent within the proof.

---

### 13. Unclear step in the proof of Proposition 2

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Thus

$$
\begin{aligned}
\frac{n_{\alpha}}{n} & =\sum_{\beta \in E} \frac{\hat{\pi}\left(\beta \mid H_{i}-\alpha\right)}{\hat{\pi}\left(\alpha \mid H_{i}-\alpha\right)}\left(\frac{\theta}{n-1+\theta} \frac{n_{\alpha}}{n} P_{\beta \alpha}+\frac{n_{\alpha}}{n} \frac{n_{\alpha}-1}{n-1+\theta}\right) \\
& =\sum_{\beta \in E} \frac{\hat{\pi}\left(\beta \mid H_{i}-\alpha\right)}{\hat{\pi}\left(\alpha \mid H_{i}-\alpha\right)} C^{-1} \frac{\theta}{2} n_{\alpha} P_{\beta \alpha}+\frac{1}{\hat{\pi}\left(\alpha \mid H_{i}-\alpha\right)} C^{-1}\binom{n_{\alpha}}{2} \\
& =p_{\mathrm{m}}(\alpha)+p_{\mathrm{c}}(\alpha)
\end{aligned}
$$

**Feedback**:
At first this step in the proof of Proposition 2 made me think that the authors were simply replacing the summand
\[
\frac{\theta}{n-1+\theta} \frac{n_{\alpha}}{n} P_{\beta \alpha}+\frac{n_{\alpha}}{n} \frac{n_{\alpha}-1}{n-1+\theta}
\]
by the two terms in the next line, which would not hold termwise. Then I understood that the first part is just rewritten using $C^{-1}=2/\{n(n-1+\theta)\}$, and that the second part has been summed over $\beta$ using $\sum_{\beta}\hat{\pi}(\beta\mid H_i-\alpha)=1$, giving the term involving $C^{-1}\binom{n_\alpha}{2}$. It might help the reader if this use of the normalisation of $\hat{\pi}(\cdot\mid\cdot)$ and the separation of the two contributions (the sum and the already-summed term) were mentioned explicitly at this point.

---

### 14. Use of a further approximation for $\hat{\pi}$ in applications

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> Note that this model has $2^{10}$ different alleles, and so the calculation of the quantities $\hat{\pi}\left(\beta \mid A_{n}\right)$ using equations (18) and (19) appears to be computationally daunting. In fact the special structure of this model allows an efficient approximation of these quantities, as described in Appendix A.

**Feedback**:
I initially had trouble seeing exactly what version of $\hat{\pi}(\cdot\mid\cdot)$ was used in the simulated sequence example, because the main text only refers to an "efficient approximation" and then moves on to the numerical results. However, I later saw that Appendix A makes clear that a numerical quadrature scheme is used to approximate the expression for $\hat{\pi}$ from Definition 1, and that the resulting proposal is a valid IS function in its own right. To make the link between Sections 4 and 5.2 entirely explicit, it might be helpful to state directly in Section 5.2 that the performance reported there for $Q_\theta^{\mathrm{SD}}$ is based on this practical numerical approximation to $\hat{\pi}$ as described in Appendix A.

---

### 15. Clarity of the rooted tree sampler modification (Sec 5.5)

**Importance**: Nitpick
**Status**: [Pending]

**Quote**:
> To facilitate a comparison with published estimates, we modified our IS function to analyse rooted trees, by adding to conditions (a) and (b) above a condition that no mutation can occur backwards in time from the type of the MRCA. Note that this does not take full account of the information contained in the position of the root, and the modified sampler is likely to be less efficient for roots which are relatively unlikely given the data.

**Feedback**:
Statement "we modified our IS function to analyse rooted trees … by adding … a condition that no mutation can occur backwards in time from the type of the MRCA" caused me some initial uncertainty about exactly how the backward moves were constrained for the rooted case. At first it was not obvious whether "from the type of the MRCA" referred to forbidding proposals that originate on lineages of the designated MRCA type, or to some other restriction, and one also has to keep in mind that in the rooted–tree setting a particular MRCA type has been fixed in advance.

After reading the surrounding discussion on rooted trees and outgroup information, it becomes clear that the intent is to condition on a chosen root type and then forbid any backward mutation steps that originate from a lineage currently carrying that root type, while still allowing coalescences between such lineages. This ensures that the proposal is restricted to histories in which the designated root type is ancestral rather than created by mutation.

Because this is the only change needed to adapt the unrooted sampler to the rooted setting, it may be worth stating explicitly that the algorithm conditions on a particular MRCA type and then disallows backward mutation moves that originate on lineages of that type. This would make the nature of the additional constraint fully transparent to readers implementing the rooted sampler.

---
