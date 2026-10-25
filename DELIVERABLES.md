# Deliverables

Everything we must hand in, mapped to the rubric row it earns marks on, with an owner and a due checkpoint.
Tick items off as they are **finished**. Before CP6 and before submitting, mark yourselves against every rubric row:
anything not honestly in the top band is the cheapest mark available.

Sources: `requirements_rubric/DSAI5101_Project_Info.pdf` and the three rubric PDFs.

## 0. Already done
- [x] Project proposal (5%), submitted 28 Sep 2026: `proposal/DSAI5101_ProjectProposal.pdf`. **Approved, 90/100**
- [x] Feedback mapped to actions: [ALIGNMENT.md §2](ALIGNMENT.md) (FB1–FB4). FB3 is fixed in code. FB1, FB2 and FB4 are carried by the report rows below

## 1. Presentation & Q&A: 10% · **Sun 22 Nov** · 10 min talk + 5 min Q&A

| Deliverable | Rubric row (marks) | Owner | Due |
|---|---|---|---|
| Slides: problem, who it matters to, guiding question, stakes clear in the first minute | Problem & Motivation (1) | Lynn | CP5 |
| Slides: data source, size, quality issues, cleaning decisions, 2–3 EDA findings that shaped modelling | Data & EDA (1.5) | Sumaiya | CP5 |
| Slides: baselines (median, promise) + 3 models, time-based CV, metrics and why | Methods & Evaluation (1.5) | Lynn | CP5 |
| Slides: comparison chart vs baselines, delay drivers, error by segment, promise test, ≥ 1 limitation | Results & Insights (2) | Mahmoud (+ Lynn for the promise test) | CP5 |
| Timed under 10 min, all three speak, readable slides, logical flow | Delivery (1) | All | Rehearsals 18 + 20 Nov |
| Q&A prep sheet: ~15 likely questions with short answers (why time split? why MAE? why not courier features? what if weather? leakage?) | Q&A: Understanding (1.5) + Reasoning (1) | All | CP6 |
| Every member can answer about the **whole** project; notebook + figures open during Q&A | Group Engagement (0.5) | All | 20 Nov |

Slide-by-slide plan (titles, figures, speakers, timing): [presentation/outline.md](presentation/outline.md). Deck built in
Canva. Speaking order: Lynn (problem) → Sumaiya (data + EDA) → Lynn (methods) → Mahmoud (results) → Lynn (promise
test) → Mahmoud (conclusion), about 3 min each.

## 2. Final report: 15% · submit **Sun 29 Nov** (deadline Thu 3 Dec) · IEEE two-column, 4–6 pages excl. references

| Section | Rubric row (marks) | Owner | Due |
|---|---|---|---|
| Title, all names + student IDs, course | Format (1) | Lynn | CP5 |
| Abstract, 150–250 words: problem, approach, **specific** findings with numbers | Abstract (1) | Lynn | CP5 |
| Introduction: motivation, **the research question as one sentence** (predict delivery time at placement, ALIGNMENT §1), bullet list of contributions | Introduction (1.5) · **FB1** | Lynn | CP5 |
| Related Work: **≥ 5 scholarly sources**, compared and positioned against us | Related Work (2) | Sumaiya (sources from all, T1) | CP5 |
| Data & EDA: source, collection, size, variables; every cleaning step with its reason (missing, outliers, refused dispatches, pre-booked, leakage) **with before → after counts, shown in the EDA**; EDA figures that each make a point and visibly inform modelling | Data & EDA (2.5) · **FB2** | Sumaiya | CP5 |
| Methodology: features (cyclical time, train-only fitting, why `is_weekend` was dropped), baselines, 3 models, hyperparameters + how they were tuned, forward-chaining CV, metrics and why. Enough detail to reproduce; **numbered steps + one table, not dense prose** | Methodology (3) · **FB3, FB4** | Lynn | CP5 |
| Results & Discussion: comparison table vs baselines with bootstrap CIs, error analysis by segment, delay drivers, leakage audit, stage analysis, promise test, robustness (test days, weekend caution) | Results & Discussion (3) | Mahmoud (+ Sumaiya: audit/stages, Lynn: promise) | CP5 |
| Conclusion: answers the question, concrete limitations (8 days, no weather/traffic/courier data, obfuscated coordinates), ethics (courier pressure from tighter promises), specific future work | Conclusion (1) | Lynn | CP5 |
| References: papers, the dataset (+ Meituan's required acknowledgement), libraries (scikit-learn, pandas, LightGBM) | Format (1) | Lynn | Submit |
| Acknowledgement of generative-AI use (required by the guidelines) | Academic integrity | Lynn (from README §6) | Submit |
| Every figure/table numbered, captioned and referenced in the text | Format (1) | All | CP6 |

## 3. Code and data (part of the report's Format, Code & Data mark)

| Deliverable | Owner | Due |
|---|---|---|
| Repository link accessible to the instructor (public, or instructor invited). **Check permissions before submitting** | Lynn | CP6 |
| Code runs top to bottom: `python -m unittest` + `python -m experiments.final` + notebooks 01–05 | All | CP4 |
| README with setup and reproduce commands; `requirements.txt` pinned; seeds fixed | Lynn | CP4 |
| Working link to the dataset (Meituan GitHub), plus a note that the CSV isn't redistributed (licence) | Lynn | CP4 |
| Fresh-clone check in a new folder (T5) | Mahmoud | CP6 |

## 4. Final pre-submission checklist (from the guidelines §6)
- [ ] IEEE two-column conference format (Overleaf template)
- [ ] 4–6 pages excluding references and appendices
- [ ] Title, all member names and student IDs
- [ ] Every figure and table numbered, captioned and referred to in the text
- [ ] Code runs top to bottom, README, dependencies listed, seeds fixed
- [ ] Links to code and every dataset included **and accessible**
- [ ] Uploaded to the D2L dropbox, one submission per group
- [ ] Checked against the Final Report Rubric, row by row
