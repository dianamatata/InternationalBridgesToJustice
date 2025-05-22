## **Claim Verification Instructions**

You need to determine whether the database contains enough information to fact-check the claim, and then decide whether the claim is **Supported**, **Contradicted**, or **Inconclusive** based on that information. You can cite specific laws or legal chapters to justify your decision.

---

### Very important:
Make sure that the information used for verification comes from the **correct country**.  
You can find the country name in the `'metadata':'title'` or `'metadata':'country'` fields of the context.

---

### Is there enough information?

**Does the database provide enough information to fact-check the claim?**

- If **no**, label the claim as `###Inconclusive###`
- If **yes**, state the judgment as one of the following categories, marked with ###:

#### `###Supported###`
A claim is **supported** by the database if everything in the claim is supported and nothing is contradicted by the information in the database.  
There can be some results that are not fully related to the claim.

#### `###Contradicted###`
A claim is **contradicted** if some part of it directly conflicts with information in the database, and no supporting evidence is provided for that part.

#### `###Inconclusive###`
A claim is **inconclusive** if:
- A part of the claim cannot be verified with the available information,  
- A part of the claim is both supported and contradicted by different sources,  
- The claim contains unclear references (e.g., "the person", "the law", "they").

---

### Input

**Claim:**  
`{claim}`

**Context:**  
`{context}`
