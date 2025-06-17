## **Claim Extraction Instructions**

### Very important:

Here is an improved version of your prompt with clearer structure, more concise language, and a stronger ending that reinforces the constraints:

---

You are tasked with verifying how factual a sentence is. To do this, extract **fine-grained, verifiable facts** from the sentence marked between `<SOS>` and `<EOS>`.

Each extracted fact should:

* Be **independently verifiable** using reliable sources (e.g., Wikipedia)
* Describe a **single event or state** (e.g., "Nvidia was founded in 1993 in Sunnyvale, California, U.S.", or "UMass Amherst has existed for 161 years.")
* Include necessary **named entities, numbers, time, and location** details
* Be **fully understandable on its own**, without referring to prior sentences

Avoid extracting:

* **Opinions, suggestions, instructions, or hypotheticals** (e.g., subjunctive or conditional statements like “would be”)
* **Stories, personal experiences**, or **quoted narratives** unless the quotation is sourced and factual
* **Definite noun phrases** (e.g., "the president") unless fully specified or modified (e.g., "the president of the United States in 2020")
* **References or citations** (e.g., “Article 12 of the Constitution”)

If a definite phrase is used (e.g., “the teacher”), add modifiers to fully identify it (e.g., “the teacher who led the 2019 protest in Chile”).
If a quotation is included, it must be **verbatim** and attributed to its **source** if available.

🛑 **If the sentence contains no independently verifiable facts**, output:
`No verifiable claim.`

**Do not extract vague or context-dependent statements. Every extracted fact must stand alone.**
example:
"Provisions for regular reviews of minors' detention status are outlined in Articles 288-290.",
'These provisions ensure that minors are not held longer than necessary.',
In this second claim, "these" does not refer to anything out of its context, and cannot be verified.

---

### Here are some examples:

Text: The sweet potato or sweetpotato (Ipomoea batatas) is a dicotyledonous plant that belongs to the bindweed or morning glory family, Convolvulaceae. `<SOS>`Its large, starchy, sweet-tasting tuberous roots are used as a root vegetable.`<EOS>` The young shoots and leaves are sometimes eaten as greens.
Sentence to be focused on: Its large, starchy, sweet-tasting tuberous roots are used as a root vegetable.
Facts:
- Sweet potatoes' roots are large.
- Sweet potatoes' roots are starchy.
- Sweet potatoes' roots are sweet-tasting.
- Sweet potatoes' roots are tuberous.
- Sweet potatoes' roots are used as a root vegetable.

Text: `<SOS>`After the success of the David in 1504, Michelangelo’s work consisted almost entirely of vast projects.`<EOS>` He was attracted to these ambitious tasks while at the same time rejecting the use of assistants, so that most of these projects were impractical and remained unfinished.
Sentence to be focused on: After the success of the David in 1504, Michelangelo’s work consisted almost entirely of vast projects.
Facts:
- Michelangelo achieved the success of the David in 1504.
- After 1504, Michelangelo’s work consisted almost entirely of vast projects.

Text: After the success of the David in 1504, Michelangelo’s work consisted almost entirely of vast projects. He was attracted to these ambitious tasks while at the same time rejecting the use of assistants, so that most of these projects were impractical and remained unfinished. `<SOS>`In 1504 he agreed to paint a huge fresco for the Sala del Gran Consiglio of the Florence city hall to form a pair with another just begun by Leonardo da Vinci.`<EOS>` Both murals recorded military victories by the city (Michelangelo’s was the Battle of Cascina), but each also gave testimony to the special skills of the city’s much vaunted artists.
Sentence to be focused on: In 1504 he agreed to paint a huge fresco for the Sala del Gran Consiglio of the Florence city hall to form a pair with another just begun by Leonardo da Vinci.
Facts:
- In 1504, Michelangelo agreed to paint a huge fresco for the Sala del Gran Consiglio of the Florence city hall.
- Around 1504, Leonardo da Vinci just began with a mural for the Florence city hall.

Text: After the success of the David in 1504, Michelangelo’s work consisted almost entirely of vast projects. He was attracted to these ambitious tasks while at the same time rejecting the use of assistants, so that most of these projects were impractical and remained unfinished. In 1504 he agreed to paint a huge fresco for the Sala del Gran Consiglio of the Florence city hall to form a pair with another just begun by Leonardo da Vinci. `<SOS>`Both murals recorded military victories by the city (Michelangelo’s was the Battle of Cascina), but each also gave testimony to the special skills of the city’s much vaunted artists.`<EOS>` Leonardo’s design shows galloping horses, Michelangelo’s active nudes—soldiers stop swimming and climb out of a river to answer an alarm.
Sentence to be focused on: Both murals recorded military victories by the city (Michelangelo’s was the Battle of Cascina), but each also gave testimony to the special skills of the city’s much vaunted artists.
Facts:
- Michelangelo’s murals for the Florence city hall recorded military victories by the city.
- Leonardo da Vinci’s murals for the Florence city hall recorded military victories by the city.
- Michelangelo’s mural for the Florence city hall was the Battle of Cascina.

Text: I (27f) and my fiance "Leo" (27m) decided to let my FSIL "Maya" (32f) stay at our house because she needed space from her husband due to some relationship struggles they're having. Leo and I had gotten wedding cake samples from an expensive bakery specializing in wedding cakes. We planned to test them along with Maya after we finished up some other wedding plans yesterday. `<SOS>`However, when I came home from work to see Leo yelling at Maya, the box the samples came in wide open on the living room table, and Maya arguing with him.`<EOS>` I asked what was happening, and Leo angrily told me that while we were both at work, Maya had some friends over and they ended up eating almost all of our cake samples.
Sentence to be focused on: However, when I came home from work to see Leo yelling at Maya, the box the samples came in wide open on the living room table, and Maya arguing with him.
Facts:
No verifiable claim.

Text: I was a catholic school kid, educated by nuns and somehow on a spring day in 1972, I was called down to the principal’s office by Sister Mary Roberts, who informed me that I had gained admission to Stuyvesant High School. `<SOS>`I was excited to be freshman in one of New York City’s elite public schools but soon came to realize that my catholic school education did not provide the groundwork for abstract concepts like science and algebra.`<EOS>` My parochial education in Science at St. Joseph’s was essentially “God made it, what else do you need to know?”
Sentence to be focused on: I was excited to be freshman in one of New York City’s elite public schools but soon came to realize that my catholic school education did not provide the groundwork for abstract concepts like science and algebra.
Facts:
- Stuyvesant High School is in New York City.
- Stuyvesant High School is an elite high school.
- Stuyvesant High School is a public school.
- In 1972, St. Joseph's catholic school education did not provide the groundwork for abstract concepts like science and algebra.

Text: `<SOS>`Major depressive disorder (MDD), also known as depression, is a mental disorder.`<EOS>`
Sentence to be focused on: Major depressive disorder (MDD), also known as depression, is a mental disorder.
Facts:
- Major depressive disorder is also known as depression.
- Major depressive disorder is a mental disorder.

Text: The 1937 Fox vault fire was a major fire in a 20th Century Fox film storage facility in Little Ferry, New Jersey on 9 July 1937. It was caused by the spontaneous combustion of nitrate film stored in inadequately-ventilated vaults. The fire resulted in one death and two injuries, and destroyed all of the film present. `<SOS>`This fire was responsible for the loss of most of the silent films produced by Fox Film Corporation before 1932.`<EOS>` Also destroyed were Educational Pictures negatives and films of several other studios.
Sentence to be focused on: This fire was responsible for the loss of most of the silent films produced by Fox Film Corporation before 1932.
Facts:
- Fox Film Corporation produced silent films before 1932.
- The 1937 Fox vault fire caused the loss of most of the silent films produced by Fox Film Corporation before 1932.

Text: `<SOS>`Garnett had spent well over a decade with the Minnesota Timberwolves, and while he stayed loyal to that team, he found little success there.`<EOS>` When he said “you can’t get your youth back,” he meant it - because from a human standpoint, had he been able to apply his talents somewhere else, NBA history might have been different.
Sentence to be focused on:  Garnett had spent well over a decade with the Minnesota Timberwolves, and while he stayed loyal to that team, he found little success there.
Facts:
- Kevin Garnett spent over a decade with the Minnesota Timberwolves.
- Kevin Garnett was loyal to the Minnesota Timberwolves.
- Kevin Garnett found little success with the Minnesota Timberwolves.

Text: Unity. Unity. In another January in Washington, on New Year’s Day 1863, Abraham Lincoln signed the Emancipation Proclamation. `<SOS>`When he put pen to paper, the President said, “If my name ever goes down into history it will be for this act and my whole soul is in it.”`<EOS>` My whole soul is in it.
Sentence to be focused on: When he put pen to paper, the President said, “If my name ever goes down into history it will be for this act and my whole soul is in it.”
Facts:
- On New Year’s Day 1863, Abraham Lincoln said, “If my name ever goes down into history it will be for this act and my whole soul is in it.”

Text: Ãcariya Mun related the story of a dhutanga monk (ascetic monk) who inadvertently went to stay in a forest located next to a charnel ground. He arrived on foot at a certain village late one afternoon and, being unfamiliar with the area, asked the villagers where he could find a wooded area suitable for meditation. They pointed to a tract of forest, claiming it was suitable, but neglected to tell him that it was situated right on the edge of a charnel ground. `<SOS>`They then guided him to the forest, where he passed the first night peacefully.`<EOS>` On the following day he saw the villagers pass by carrying a corpse, which they soon cremated only a short distance from where he was staying.
Sentence to be focused on: They then guided him to the forest, where he passed the first night peacefully.
Facts:
No verifiable claim.

Text: {snippet}
Sentence to be focused on: {sentence}
Facts: