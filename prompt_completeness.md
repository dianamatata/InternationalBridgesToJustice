**Prompt:**

You are tasked with evaluating whether the following wiki chapter provides sufficient and legally grounded information to address the key point: **{keypoint}**.

Before classifying the chapter, critically examine **both** the wiki content and the legal database. Even if the wiki seems complete, verify whether additional laws from the database could strengthen it. Prioritize **clarity, specificity**, and **legal accuracy** in your assessment.

**Classify the wiki chapter as one of the following:**


- **Complete**: The chapter clearly addresses the key point with sufficient legal detail — such as citing specific legal provisions, explaining relevant protections and procedures, and using accurate legal terminology. No major improvements from the database are necessary.

- **Needs refinement**: The chapter touches on the topic but lacks:
  - Clear definitions of legal terms or rights,
  - Specific references to legal texts (e.g. constitutions, penal codes, procedures),
  - Or relevant details about exceptions, procedures, or implementation mechanisms.

  If so, **use the legal database** to:
  - Identify **specific legal articles** or sections that strengthen or clarify the point,
  - Summarize their relevance (what they say and how they apply),
  - And then **REWRITE the chapter directly**, integrating those legal references into a clear and informative form.

  The rewrite should **not use vague phrases** like “under legal conditions” without explaining **what those legal conditions are**. Instead, specify which law or article sets the conditions and what they entail.

- **Missing**: The chapter does not address the key point at all.

Your output must include:

1. **Classification**: One of the three categories above.
2. **What’s missing or unclear** (if applicable).
3. **Summary of relevant laws** (with articles cited and explained).
   - If **no relevant legal provisions** are found in the database to support or enhance the key point, **clearly state this**, and explain why the chapter still needs refinement (e.g., it lacks definitions, examples, or legal context).
4. **REWRITTEN wiki chapter** (if possible), fully incorporating the legal content from the database.
- Avoid generic suggestions — provide a critical and well-sourced rewrite that a reader can rely on to understand their rights or obligations in legal terms.
- If relevant legal texts are available, rewrite the chapter to fully incorporate those laws with proper explanation.
- If no legal references are available, clearly state this.

**If the wiki chapter seems complete but legal support from the database could clarify or reinforce its points, classify it as *Needs refinement*.**


Wiki_content (chapter to be evaluated):
{wiki_content}

Database_content (legal text for potential support):
{database_content}


