"""Compare literature search approaches for the targeting interventions paper.

Tests:
1. Current arXiv-based approach (literature.py)
2. perplexity/sonar via OpenRouter
3. perplexity/sonar-pro-search via OpenRouter

Reports: results + cost for each.
"""
import json
import os
import time

import litellm

# Paper metadata
TITLE = "Targeting Interventions in Networks"
ABSTRACT = (
    "We study games in which a network mediates strategic spillovers and "
    "externalities among the players. How does a planner optimally target "
    "interventions that change individuals' private returns to investment? "
    "We analyze this question by decomposing any intervention into orthogonal "
    "principal components, which are determined by the network and are ordered "
    "according to their associated eigenvalues. There is a close connection "
    "between the nature of spillovers and the representation of various "
    "principal components in the optimal intervention. In games of strategic "
    "complements (substitutes), interventions place more weight on the top "
    "(bottom) principal components, which reflect more global (local) network "
    "structure. For large budgets, optimal interventions are simple — they "
    "involve a single principal component."
)

LIT_SEARCH_PROMPT = """\
You are a research librarian specializing in academic economics and network theory.

Given the following paper, find the most relevant related work. Focus on:
1. **Methodological precursors**: Papers that developed the spectral/eigenvalue decomposition techniques for networks used here
2. **Direct competitors**: Other papers on optimal targeting/intervention in networks
3. **Key citations**: Foundational papers this work likely builds on (network games, key player problems)
4. **Recent extensions**: Papers that extend or apply similar techniques

For each paper found, provide:
- Full title
- Authors
- Year
- Where published (journal/arXiv)
- 1-sentence explanation of relevance

**Paper title**: {title}

**Abstract**: {abstract}
"""


def test_current_arxiv():
    """Test current arXiv-based literature search."""
    from coarse.agents.literature import search_literature
    from coarse.llm import LLMClient

    print("=" * 70)
    print("TEST 1: Current arXiv approach")
    print("=" * 70)

    client = LLMClient()
    start = time.time()
    result = search_literature(TITLE, ABSTRACT, client)
    elapsed = time.time() - start

    print(f"\nTime: {elapsed:.1f}s")
    print(f"Cost: ${client.cost_usd:.4f}")
    print(f"\nResults:\n{result}")
    return {"method": "arxiv", "time": elapsed, "cost": client.cost_usd, "result": result}


def test_perplexity_sonar(model: str):
    """Test Perplexity Sonar via OpenRouter."""
    print("=" * 70)
    print(f"TEST: {model}")
    print("=" * 70)

    prompt = LIT_SEARCH_PROMPT.format(title=TITLE, abstract=ABSTRACT)

    start = time.time()
    response = litellm.completion(
        model=f"openrouter/{model}",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.3,
    )
    elapsed = time.time() - start

    content = response.choices[0].message.content

    # Cost from litellm
    try:
        cost = litellm.completion_cost(completion_response=response)
    except Exception:
        cost = None

    # Also check OpenRouter's reported cost from response headers/usage
    usage = response.usage
    openrouter_cost = None
    if hasattr(usage, "cost") and usage.cost is not None:
        openrouter_cost = usage.cost

    print(f"\nTime: {elapsed:.1f}s")
    print(f"Cost (litellm): ${cost:.6f}" if cost else "Cost (litellm): unknown")
    print(f"Cost (OpenRouter): ${openrouter_cost:.6f}" if openrouter_cost else "Cost (OpenRouter): unknown")
    print(f"Tokens in: {usage.prompt_tokens}, out: {usage.completion_tokens}")
    print(f"\nResults:\n{content}")

    return {
        "method": model,
        "time": elapsed,
        "cost_litellm": cost,
        "cost_openrouter": openrouter_cost,
        "tokens_in": usage.prompt_tokens,
        "tokens_out": usage.completion_tokens,
        "result": content,
    }


def main():
    results = []

    # Test 1: Current arXiv approach
    try:
        results.append(test_current_arxiv())
    except Exception as e:
        print(f"arXiv test failed: {e}")

    print("\n\n")

    # Test 2: Perplexity Sonar (lightweight)
    try:
        results.append(test_perplexity_sonar("perplexity/sonar"))
    except Exception as e:
        print(f"Sonar test failed: {e}")

    print("\n\n")

    # Test 3: Perplexity Sonar Pro Search (agentic)
    try:
        results.append(test_perplexity_sonar("perplexity/sonar-pro-search"))
    except Exception as e:
        print(f"Sonar Pro Search test failed: {e}")

    # Summary
    print("\n\n")
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results:
        cost_str = f"${r.get('cost', r.get('cost_litellm', '?'))}"
        print(f"  {r['method']:40s}  time={r['time']:.1f}s  cost={cost_str}")


if __name__ == "__main__":
    main()
