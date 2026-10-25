# 07 — Awards fit, honesty rules, and interview preparation

## Where this stands against top-award criteria
Top ISEF awards reward rigorous inquiry, innovation/impact, and the student's own mastery. As of now:
- Strong: methodology hygiene, honest negative results, validated simulator, ablations, pre-registration discipline (once you freeze it).
- Missing: verified novelty, theory, physical validation, a clear real-world impact story, your demonstrated command of every part.
- Realistic framing: an **empirical regime map with a validated testbed and a hardware replication**; a theorem or mechanistic law would
  raise the ceiling considerably. Do not force a "breakthrough" narrative; the Moore Award in particular rewards demonstrable
  positive impact for future generations — tie to a real application only if it is genuine (e.g. degraded-network sensing for search and
  rescue), and only if you can quantify it.

## Ownership and AI-use disclosure (non-negotiable)
Much of this package was produced with AI assistance. Competitions require that the work be yours and often require disclosure of AI use —
**read the current ISEF Rules Book / your fair's rules and follow them exactly.** Practically: rewrite the docs in your own words, re-derive the maths,
reproduce every number yourself, keep a dated journal of what *you* decided, and be ready to explain any line live. If you cannot, simplify the
project until you can.

## Interview questions you must be able to answer cold
1. Why can a Kalman filter fuse independent measurements by adding information matrices? Derive it.
2. Why is sharing *measurements* exact but sharing *estimates* not? What does covariance intersection give up?
3. How does your filter handle a measurement that arrives 3 steps late? Why is the result identical to the batch solution?
4. Why does every policy tie with periodic when the model is right? Is that obvious? Is it a theorem or an observation?
5. What is "negative information" and why might it break your optimality argument?
6. What is NEES/NIS and why does NEES ≈ 17 in the mismatch scenario?
7. Why use common random numbers and paired tests? What would go wrong with unpaired?
8. What did the v1 experiment get wrong, and how do you know now? (seed overlap, stale fusion, noise triggers)
9. Which of your results were exploratory and which confirmatory? What failed to confirm?
10. What is the closest prior work and exactly how does yours differ?
11. What would convince you the method does *not* work?
12. What are the assumptions of PSA-VoI (common-knowledge sensors, nominal link probabilities) and when do they break?
13. How do you know the hardware result isn't just clock error? How did you synchronise clocks?
14. What is the sim-to-real gap and what explains it?
15. If you had 6 more months, what is the first experiment you would run?

## Honest odds
A top award is a low-probability outcome for any project; this one can become a solid, defensible entry. What you control: correctness,
honesty, depth of understanding, and a clean story. Spend the next weeks on the literature check, a mentor, theory, and hardware — not on more features.
