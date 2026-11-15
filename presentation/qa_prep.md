# Q&A prep (5 minutes, questions can go to anyone)

Everyone should be able to give every answer below in two or three sentences (T6). The person in
brackets leads if the question is open; anyone may add. All numbers are final (test days, CP4) unless
marked CV. Sources: README §3–§5, ALIGNMENT.md, `results/final/`.

**The 20-second story:** using only what is known when an order is placed, gradient boosting predicts
delivery time with 6.49 min error, 31% better than guessing the median and 3.1 min better than the
platform's own promise. Distance is the main driver. But turning predictions into promises does not
beat the platform, because the platform can still act after the order is placed.

---

## 1. Problem and framing [Lynn]

**Why predict delivery time and not delay?**
Delay is actual minus the platform's promise, so a delay model would partly be learning Meituan's
padding rule. Delivery time is what the customer experiences, and it lets us compare our estimate with
the promise fairly. Delay is used only to describe the data and to count late orders (proposal feedback 1).

**Why only order-time information?**
The promise is shown at checkout, before a courier is assigned. Anything recorded later (courier,
dispatch, pickup) would not exist at that moment, so using it would be leakage.

**What were your success criteria?**
Set before modelling: at least 20% lower MAE than the median predictor (met: 31%, CI excludes 0), and
fewer late orders than the platform at the same average promise (not met; see §5).

## 2. Data and cleaning [Sumaiya]

**How did you clean the data?**
654,343 rows were dispatch attempts, not orders: 85,797 refused attempts repeat an order someone else
delivered, so we kept accepted ones (568,546 orders). Zeros in timestamps mean "not recorded". Pre-booked
orders (22,181) are a different population: their time follows the slot the customer picked, and they
hold 4,073 of the 4,097 deliveries over 3 h. 24 more implausible durations removed → 546,340 orders.

**Why not just drop rows with a missing prep estimate?**
They are not missing at random: those orders are longer trips, and still 2–4 min slower at the same
distance. Dropping them would bias the model, so we impute (inside the pipeline) and add a flag.

**What is the "prep default" thing?**
13.8% of prep "estimates" are under 5 min and almost all equal the moment the order enters the system,
so they are a system default, not a forecast. We treat them as missing and flag them. We checked they
never equal the later dispatch time, so no leakage.

## 3. Method [Lynn, Mahmoud]

**Why a time split instead of a random split?**
A random split lets the model train on orders from the same hour it is tested on, which flatters it. In
practice it only ever sees the past, so we train on 17–22 Oct and test on 23–24 Oct, and use
forward-chaining CV (each fold trains on earlier days and validates on the next).

**Did you look at the test set more than once?**
No. All settings were frozen first, then `final.py` scored all five models on the test days in one run
(9 Nov), and the manifest records the commit. Re-scoring after tuning would make the test set training data (Lec 7).

**Why did you drop the weekend feature?**
Only one training day (Sat 22) is a weekend and the first three CV folds have none, so its effect can't
be learned or validated. With it, Elastic-Net's Saturday-fold error jumped from 6.8 to 18.0 min. We state
weekend as a limitation instead.

**How is time of day encoded?**
Sine and cosine of the minute of the day, so 23:59 and 00:00 are neighbours (proposal feedback 3), plus
lunch and dinner peak flags from the EDA.

**How do you know preprocessing didn't leak?**
Imputer, scaler and encoder are inside each model's pipeline, refitted on the training rows of every
fold. A unit test checks the imputer ignores validation days.

**Why MAE?**
It is in minutes and easy for operations to read, and it is not dominated by a few extreme orders. We
also report RMSE and R². Since we report MAE, the boosting search included the absolute-error loss, and
it won.

**How did you tune?**
Random search on the CV folds: Elastic-Net 30 tries on all rows; boosting 20 and Random Forest 10 tries
on samples (they are slow), then refitted on all rows. The error curve shows bigger trees overfit
(511 leaves: train 2.45 vs CV 6.63).

**Why 16 leaves on the curve but 76 in the final model?**
The curve changes only the number of leaves with everything else at default. The tuned model also has
a smaller learning rate, larger minimum leaf size and strong L2 regularisation, which control
overfitting in other ways, so it can afford more leaves.

## 4. Results [Mahmoud]

**R² is only 0.49. Isn't that weak?**
Half the variation comes from things nobody knows at ordering: traffic, weather, waiting at the door,
which courier takes it. Even a model allowed to cheat with after-order times only reaches 0.72
(leakage audit, S5: CV MAE 6.25 → 4.53). Our three very different models all land within 0.3 min of each other, which says
the limit is the information, not the model. MAE in minutes is our main metric, and there we beat both
baselines clearly.

**Is boosting really better than Random Forest?**
By 0.05 min on test, CI −0.056 to −0.039: statistically real, practically the same. We pick boosting for
the lower MAE and speed; RF has slightly fewer big misses (lower RMSE).

**Why does the platform promise have a worse MAE than just guessing the median?**
It is padded on purpose (never under 30 min, mean 37.8 vs actual 29.6), so it is not trying to be an
unbiased estimate. That's why we also compare promises fairly in the promise test.

**What drives long deliveries?**
Grouped permutation importance (CV): distance +3.10 min MAE when shuffled, far ahead of time of day
(+0.86), district (+0.83), prep estimate (+0.67) and load (+0.19). The proposal was right on distance and
peaks, wrong on load.

**Where does the model do worst?**
Long trips (over 7 km: MAE 14.4), the lunch peak (11:00: 7.2), some districts (4.4 to 9.0), and the
Sunday test day (6.77 vs 6.17 on Monday).

**Does the model generalise?**
Every model is about 0.2 min worse on test than in CV, with the same ranking, so no sign of overfitting
to the validation folds.

## 5. Promise test [Lynn]

**How did you compare with the platform's promise fairly?**
We shift our 80th-percentile predictions by a constant so both promise the same average time (38.2 min
on test), then count orders arriving more than 0, 5 and 10 min late, with bootstrap intervals.

**So you lost to the platform?**
At the same average promise, yes, slightly: 6.1% vs 5.0% of orders more than 5 min late. Our proposal
named this risk. The likely reason is that the platform keeps acting after the order (reassigning
couriers, prioritising late orders); the data show a sharp drop at exactly 8 min late. The conclusion is
that better estimates are not automatically better promises. A clear negative result is a finding.

**Then what is your model useful for?**
A 3-minute-better estimate of when food will arrive, a ranked list of what makes orders slow, and a
starting point for promises that are then updated after dispatch (future work).

## 6. Leakage audit and stages [Sumaiya]

**What is the leakage audit?**
The same frozen models with after-order times (dispatch, courier accepts, pickup) added. CV MAE drops
from 6.25 to 4.53 for boosting (CI −1.74 to −1.71) and 6.60 to 4.84 for Elastic-Net; R² 0.51 → 0.72.
Added one at a time, dispatch (5.86) and accept (5.83) barely help; pickup (4.55) gives almost the whole
gap, partly by construction, since pickup time contains the other two. It shows how tempting leakage is
and how much error is information that does not exist at ordering.

**Which part of the delivery causes delays: the restaurant or the road?**
Neither dominates. Order → pickup and pickup → arrival each take a median 13.1 min, and after
accounting for distance the model's error splits about evenly (51% / 47%). Both run ~2.7 min longer at
meal peaks. Where it differs: late orders lose more on the road in the 7 big areas with longer trips
(72% of late orders), and more at pickup in the other areas and at night.

## 7. Limitations, ethics, next steps [Lynn]

**Limitations?** Eight days, one weekend day for training, one platform in one city, no weather, traffic
or courier data at ordering, coordinates shifted for privacy.

**Ethical concerns?** Errors differ by district (4.4 to 9.0 min), so some areas get less reliable
estimates. Shorter promises pressure couriers; padded promises shift the cost to customers.

**What would you do next?** Restaurant history and busy-courier counts as features (computed inside
folds), combining the estimate with updates after dispatch, and testing over several weeks for drift
with retraining and input monitoring.

**Why not deep learning?** 11 tabular features and a few hundred thousand rows: tree ensembles are the
standard strong choice there, and the three model families already agree within 0.3 min, so a more
complex model would chase the same information ceiling.

**Can we reproduce your results?** Yes: clone, install the pinned requirements, run the tests, then
`python -m experiments.final`; the data download automatically. Seed 42 throughout.
