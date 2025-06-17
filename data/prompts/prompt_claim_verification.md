## **Claim Verification Instructions**

### Your task:

You need to determine whether the database contains enough information to fact-check the claim, and then decide whether the claim is **Supported**, **Contradicted**, or **Inconclusive** based on that information. 
You need to cite specific laws or legal chapters to justify your decision.

1. **Use only the information in the `Context` below** to fact-check the claim.
2. **Verify that the context refers to the correct country** by checking the `'metadata':'country'` or `'metadata':'title'` fields.
3. **Does the database provide enough information to fact-check the claim?**
   - If **no**, label the claim as **Inconclusive**
   - If **yes**, state the judgment as one of the following categories:
4. Decide whether the claim is:
   * **Supported**: Clearly supported by specific information in the context, and nothing is contradicted by the information in the database. There can be some results that are not fully related to the claim.
   * **Contradicted**: if some part of it directly conflicts with information in the database.
   * **Inconclusive**: if 
     - A part of the claim cannot be verified with the available information,  
   - A part of the claim is both supported and contradicted by different sources,  
   - The claim contains unclear references (e.g., "the person", "the law", "they").No clear support or contradiction found
5. **Explain your decision**, citing the relevant part of the context.

---

### Important:

* **Do not use outside knowledge or assumptions**, even if the claim seems obviously true or false.
* **You must cite the exact source** (e.g., article number, law name, or chapter title) from the context used to verify or reject the claim.
* If no such source is available, choose **Inconclusive**.

---


### Input

**Claim:**  
`{claim}`

**Context:**  
`{context}`



