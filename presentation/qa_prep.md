# Q&A prep (10–15 minutes; the instructor and classmates ask, and questions can go to anyone)

Everyone should be able to give every answer below in two or three sentences (T6). The person in
brackets leads if the question is open; anyone may add. All numbers are final (test days, CP4) unless
marked CV. Sources: README §3–§5, ALIGNMENT.md, `results/final/`.

**The 20-second story:** using only what is known when an order is placed, gradient boosting predicts
delivery time with 6.49 min error, 31% better than guessing the median and as accurate as the platform's
own estimate once its padding is removed (6.36–6.48). Distance is the main driver; free riders and
each restaurant's track record come next, and with them (CV error 6.25 → 5.92) we beat the app's own
estimate on the validation days. But turning predictions into
promises does not beat the platform, because the platform can still act after the order is placed.

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
They are not missing at random: those orders are longer trips, and still 2–5 min slower at the same
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
be learned or validated. The only fold that could test it trains on just 14 "weekend" rows (Sunday orders
that arrived after midnight). That's also why Elastic-Net's Saturday-fold error jumped from 6.8 to 18.0
min: scaling a near-constant column blew up the linear model. That jump is a symptom, not the reason. We
state weekend as a limitation instead; its cost is the Sunday under-prediction (2.1 min).

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

**Why these three models?**
They're a ladder from simple to flexible, each answering a different question:
- **Elastic-Net:** the simplest model that uses features. It's one weighted sum, so every effect reads in
  minutes (1 km ≈ +6.1 min, lunch peak +4.8). The L1/L2 penalty handles correlated inputs like the 23
  district columns. It answers: how far do straight-line effects get us?
- **Random Forest:** averages many deep trees, so it picks up interactions and curves (distance matters
  more at peaks) without much tuning, and it's robust to outliers. It answers: do non-linear effects help?
- **Gradient boosting:** builds trees one after another, each fixing the last one's errors. It's usually
  the strongest on tabular data, and it can optimise MAE directly (absolute-error loss). It answers: what
  is the best we can get from these features?

All three are standard for tabular regression, fast on 400k rows, and explainable, either directly or
through permutation importance. That's why we didn't use a neural network.

**Why is the app's promise a baseline? Did you make your own baseline?**
We have two baselines, and one is our own:
1. **Median predictor (ours).** It guesses the training median (27.8 min) for every order, so it uses no
   features. It's the "do nothing" bar any model must beat. We use the median rather than the mean because
   the median is the constant that minimises MAE.
2. **The app's promise (business baseline).** It's what customers actually see and what Meituan operates on
   today, so it's the number that matters to the business. It's in the data, so it costs nothing to compare.
   But it's padded on purpose, so we never compare against it naively. We also compare:
   - our estimate against the promise minus its padding (6.48, or 6.36 per distance band)
   - our 80th-percentile model against the promise at the same average length (the promise test)

**Was each step up in complexity worth it?**
Measured on the test days, against the median baseline (9.46):
- Median → Elastic-Net (6.80): −2.66 min. That's 90% of the total gain, from a few simple features.
- Elastic-Net → Random Forest (6.54): −0.26 min more. Non-linearity helps a little.
- Random Forest → boosting (6.49): −0.05 min more. Statistically real but practically nothing.

So complexity pays off once, from "nothing" to a linear model, and then the returns shrink fast. That's
our key finding: the limit is the information available at ordering, not the model. It's confirmed by the
extension, where all three models gain the same −0.31 to −0.33 from the new features.

**If they're so close, why not just use Elastic-Net?**
For explanation, we do: its effects in minutes are in the report (Table VIII). For the headline accuracy
we report boosting, because it's the best and costs nothing extra to run. If a platform wanted something
simple and auditable, Elastic-Net loses only 0.31 min.

**Why 16 leaves on the curve but 76 in the final model?**
The curve changes only the number of leaves with everything else at default. The tuned model also has
a smaller learning rate, larger minimum leaf size and strong L2 regularisation, which control
overfitting in other ways, so it can afford more leaves.

## 4. Results [Mahmoud]

**R² is only 0.49. Isn't that weak?**
Half the variation comes from things nobody knows at ordering: traffic, weather, waiting at the door,
which courier takes it. With the real-time features it rises to 0.57 on the validation days. Even a model allowed to cheat with after-order times only reaches 0.72
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
(+0.85), district (+0.84), prep estimate (+0.68) and load (+0.20). The proposal was right on distance and
peaks, wrong on load.

**Where does the model do worst?**
Long trips (over 7 km: MAE 14.4), the lunch peak (11:00: 7.2), some districts (4.4 to 9.0), and the
Sunday test day (6.77 vs 6.17 on Monday).

**Does the model generalise?**
Monday (6.17) sits inside the CV fold range (5.99–6.44); Sunday (6.77) is the outlier, because training
had one weekend day. The model ranking is the same on test and CV.

## 5. Promise test [Lynn]

**How did you compare with the platform's promise fairly?**
We shift our 80th-percentile predictions by a constant so both promise the same average time (38.2 min
on test), then count orders arriving more than 0, 5 and 10 min late, with bootstrap intervals.

**So you lost to the platform?**
At the same average promise, yes, slightly: 6.1% vs 5.0% of orders more than 5 min late. Our proposal
named this risk. The likely reason is that the platform keeps acting after the order (reassigning
couriers, prioritising late orders); the data show a sharp drop at exactly 8 min late. The conclusion is
that better estimates are not automatically better promises. A clear negative result is a finding.

**What's the difference between delivery time, the promise and delay?**
Delivery time is how long the food actually took (order → arrival); that is what we predict. The
promise is the time the app showed at checkout, deliberately padded. Delay is delivery time minus the
promise; we only use it to describe the data and count late orders. We built two things: an estimate
(boosting, "when will it most likely arrive?", so about half of orders arrive after it) and a promise
(the 80th-percentile model, "a time it will almost certainly arrive by"). Only the promise is compared
with the app's promise.

**Arriving early is good, so what's wrong with a padded promise?**
For one customer, nothing. But a long promise loses orders (people choose the app that says 30), makes
customers plan badly (the courier arrives while they're out), and wears down trust in the number.
Operations need the realistic time for courier planning. And the padding is blunt: about the same
buffer for every order, too much for a 1 km trip, not enough for 7 km at lunch, which is why the app
is padded by 8 min on average and still late 15% of the time. Padding is good insurance; our promise
test shows it works. The goal is a buffer that is long where the trip is risky and short where it's easy.

**So did you beat the platform or not?**
Depends on how fair you are to the app. Against the promise as shown we're 3.1 min closer (6.49 vs
9.62), but that's its padding. Take off its average padding (8.2 min, measured on the training days
only) and it ties with us: 6.48 vs 6.49, CI −0.01 to +0.04. Take off each distance band's own padding
(fairer to the app) and it's slightly better, 6.36. Even then we're better under 1 km (5.61 vs 5.86) and
over 3 km (8.73 vs 9.94), 38% of orders; the app is better on 1–3 km trips (63%) and at lunch (6.68 vs
7.22). With the real-time features (riders, restaurant history), our model beats the app's own estimate
on the validation days: 5.92 vs 6.24, better in 5 of 7 segments, level on medium trips, but still not at lunch. Padded vs padded is
the promise test: we win only for shorter promises (average below ~37 min); at the app's own average it
is late less often (5.0% vs 6.1% > 5 min late). In one sentence: from order-time data we reach the
app's own estimate, beat it with real-time features on validation days, and a better promise needs what
the app does after the order. (B11)

**Why remove the padding with an average, not per order?**
A single number measured on the training days is the simplest fair version that uses no test
information. A smarter de-padding (per district or hour) would need its own model of the platform,
which is what our model already is.

**Why are you better on short and long trips but worse in between?**
The app's padding is close to a fixed rule with a 30-min minimum: about 10 min under 1 km, 7 at 1–3 km,
12–14 beyond 4 km. Our model scales with distance. Even when we remove each distance band's own padding
(the fairest version for the app), we stay better on short and long trips. For the common 1–3 km trips
at lunch, the app's real-time information (riders, what happens after ordering) likely helps.

**Did re-tuning help?**
No: re-running the same 20-try search on the new features picked the same settings, so the frozen
settings still fit. All the gain comes from the features.

**Isn't order #85188 cherry-picked?**
No: it sits at the median of the 634 Sunday 11:xx orders 3–5 km away (actual 45.3, promise 52.2, our
prediction 45.2). In that group we're off by 8.4 min on average and the app by 11.0. Our 80th-percentile
promise for it would have been about 53 min before the +2.7 shift, longer than the app's 51: at the
lunch peak our model is more cautious, which fits the promise-test result. Honest note: the de-padded
promise for this order (51 − 8.2 = 42.8) was even closer than ours to the actual 43, which is the tie on the
Results slide in one order.

**Then what is your model useful for?**
An estimate as good as the platform's own from public order-time data alone, built and checked openly;
a ranked list of what makes orders slow; an estimate that scales with distance; and a starting point
for promises that are then updated after dispatch (future work).

## 5b. Instructor feedback, new analyses [Lynn]

**Do weekends behave differently? Do you need a weekday feature?**
Same daily shape (hourly medians correlate at 0.92), but weekends run 1–3.5 min slower from noon to
18:00. With one weekend day in training we can't learn or validate that (fold 4 trains on only 14
"weekend" rows), so it stays a limitation; the Sunday test day was our hardest (6.77, predicted 2.1 min too
short). With more weeks, a day-of-week feature would be the first thing to add. (B14)

**Is the pattern drifting over time?**
Not within the week: Monday 17 and Monday 24 differ by 0.5 min per busy hour on average (max 1.3).
Eight days can't show longer drift, so deployment would need monitoring and retraining. (B14)

**What about rider availability?**
We counted, for each order, the riders who finished a delivery in its district in the last 30 min and
the orders still waiting, using only deliveries finished before the order (a unit test checks this).
When more than three orders wait per free rider (19% of orders), the median delivery is 35.6 min vs 26.4.
Riders are scarcest at 11:00 and 17–18:00, much more in some districts (B13). New orders alone (our load
feature) barely matter; orders per free rider do.

**Did more features help?**
Yes, on the validation folds: riders + each restaurant's past delivery and pickup times take CV MAE from
6.25 to 5.92 (CI −0.34 to −0.32), R² 0.51 → 0.57, and beat the app's de-padded promise overall (5.92 vs
6.24), in 5 of 7 segments and level on medium trips, not at lunch. Restaurant history gives most of it (−0.24), riders
−0.05. We did **not** re-score the test days with them: they were designed after the single test run, and
using the test set twice would make it training data. (B15)

**How does this compare with industry?**
Ele.me's deployed model (KDD 2020) uses the same kinds of inputs we added (real-time supply–demand,
orders waiting at the restaurant, nearby couriers) and cut MAE by 9.8% in an online test. Uber's
DeepETA uses an asymmetric loss so late predictions cost more than early ones, the same idea as the
platform's padding. Errors can't be compared across companies (different data and targets). (B16)

**How much of the data was missing or duplicated?**
No exact duplicate rows. 13.1% of raw rows were refused dispatch attempts repeating an order (removed).
Of accepted orders, 3.9% were pre-booked (excluded) and 1 had no arrival time. Of modelling orders, 1.4%
had no prep estimate and 13.8% a default one (both imputed + flagged, since they are not missing at
random). (B17)

**Did the new features only help the complex model?**
No. On the validation days Elastic-Net goes 6.60 → 6.27, Random Forest 6.32 → 6.00 and boosting 6.25 →
5.92: all about −0.3, same order. The gain is the information in the features, not extra model
complexity. (B15, `extension_models.tex`)

**So can more features close the gap to the leaky model?**
Only partly. The leakage audit says after-order times are worth 1.72 min (6.25 → 4.53). Our leakage-safe
real-time features recover 0.33 of that, about a fifth. The rest (pickup time, what happens on the road)
only exists after the order.

**How many features do you have?**
Main model (scored on test): 10 engineered features + district one-hot = 33 inputs. Extended model: 23
engineered features = 46 inputs. Every one is built from raw columns (distance from coordinates, cyclical
time, flags, rolling past-only counts and averages); none is a raw column used as is.

**Which model is interpretable, and what does it say?**
Elastic-Net, in minutes: +6.1 per km, +4.8 at the lunch peak, +3.6 at dinner, +0.66 per estimated prep
minute, +2.0–2.5 for an order with no real prep estimate, and only +1.1 when the district runs at twice its
usual load. Its test error (6.80) is only 0.31 above boosting, so the readable model captures most of it.
(`elasticnet_effects.tex`)

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

**Limitations?** Eight days, one weekend day for training, one platform in one city, no weather or
traffic, rider availability only approximated from past deliveries, coordinates shifted for privacy,
extra features checked on validation days only.

**Ethical concerns?** Errors differ by district (4.4 to 9.0 min), so some areas get less reliable
estimates. Shorter promises pressure couriers; padded promises shift the cost to customers.

**What would you do next?** Confirm the rider and restaurant features on new days, add a day-of-week
feature once several weekends are available, combine the estimate with updates after dispatch, and
test over several weeks for drift with retraining and input monitoring.

**Why not deep learning?** 10–23 tabular features and a few hundred thousand rows: tree ensembles are the
standard strong choice there, and the three model families already agree within 0.3 min, so a more
complex model would chase the same information ceiling.

**Can we reproduce your results?** Yes, with one command: `python -m experiments.reproduce` runs the
tests, downloads the data, rebuilds every final result, table and figure and re-executes every notebook
(`--tune` also reruns the hyperparameter searches). Pinned requirements, seed 42 throughout. The test
days are never re-scored: their predictions were written once.

## 8. Hard questions (classmates get bonus marks for asking: expect these)

**How to answer:** two or three sentences, a number, and a backup slide if one fits. Admit limits openly;
"we didn't test that, but we'd expect…" is a good answer. Never guess a number: say where it is.

**Two test days, one of them a Sunday: is that enough to trust the result?**
It's 139,787 orders, but they're two days, so the real uncertainty is day to day, not order to order
(see the first question in section 9). Monday (6.17) sits inside the CV fold range (5.99–6.44) and
Sunday (6.77) is the outlier, with the same model ranking, so nothing broke. What two days can't show is drift over weeks or
seasons; that's a stated limitation, and deployment would need monitoring and retraining.

**Your extended model was never tested on the test days. How do you know it's not overfit?**
It was checked the same way the main model was chosen: forward-chaining CV, where every fold trains only
on earlier days. It improves on every validation day, all three model types gain the same, and re-tuning
picked the same settings. We didn't score the test days again on purpose, because we designed those
features after seeing test results. The honest claim is "better on validation days, to be confirmed on new
data".

**Isn't restaurant history leakage? It uses delivery times.**
Only of *other* orders that had already been delivered before this one was placed, which the platform
knows live. A unit test checks it on hand-computed cases. Sumaiya's review even found a subtle case:
open-order counts were skipping orders that would later take over 3 h, which you can't know yet. We fixed
that.

**Removing the padding uses actual delivery times. Isn't that cheating for the app?**
It uses the same information our model trains on: the six training days only, never the test days. And
we show the stricter version (padding per distance band), where the app does slightly better (6.36 vs
6.49). We report both, so nobody has to trust one choice.

**In the promise test, isn't shifting your promises by +2.7 min tuning on the test set?**
No: the shift only matches the *average promise* of the two systems (ours vs the app's), using promises,
never actual delivery times. It makes the comparison fair at equal length; it can't see who was late.

**Why the 80th percentile?**
A promise has to cover most orders. The app's own promises cover about 85%, so q80 is in the same range.
The test then equalises the average promise anyway, so the exact quantile matters less than the shape of
the predictions.

**Why MAE when late deliveries hurt more than early ones?**
MAE answers "how far off is the estimate", in minutes. Lateness is handled separately: we report the share
of orders more than 5 min late, and the promise test uses a quantile model built for "being late is
worse". Uber's DeepETA makes the same split with an asymmetric loss.

**Why not XGBoost, LightGBM or CatBoost?**
We tried LightGBM with the same settings: 6.247 vs 6.251, the same. Random Forest and Elastic-Net are
within 0.3 min too. The limit is information, not the algorithm.

**Why not a neural network like Uber?**
Uber has a routing engine, live traffic and billions of trips. We have 23 tabular features and 400k
training rows, where tree ensembles are the standard strong choice. And when we added features, Elastic-Net,
RF and boosting all gained ~0.3 min: features matter more than model complexity here.

**What if you had weather and traffic data?**
They'd help, but only up to a point. Even after-order times (pickup, dispatch) only take the error from 6.25
to 4.53, and our real-time features already recover a fifth of that gap. Live rider pressure partly acts
as a congestion signal already. We'd add weather as a past-only or forecast feature.

**Coordinates are shifted for privacy. Aren't your distances wrong?**
They're approximate, which we state. But distance still has a strong, steady effect: about 7 min per km,
positive in all 23 districts, and the top driver by far. So the distances keep enough information to rank
trips.

**Did you check for Simpson's paradox?**
Yes: the distance slope stays positive inside every one of the 23 districts (4.9 to 7.7 min/km), so it's
not created by mixing districts.

**Permutation importance is unreliable with correlated features.**
That's why we shuffle related features *as groups* (all time features together, etc.). We also checked the
interaction: time and load shuffled together cost 1.44 min vs 1.05 separately. And two other methods,
Elastic-Net effects and partial dependence, give a consistent picture (distance first, load weak).

**Why is load weak, when busy obviously means slow?**
Raw load mostly measures district size and hour: within the same district and hour the correlation is
only 0.09. What matters is *riders*: when more than 3 orders wait per free rider, median delivery is 35.6
vs 26.4 min. New orders don't slow things down; too few riders does.

**Why are orders with a default prep estimate slower?**
We don't know the cause, and we didn't guess: they're 2–5 min slower at the same distance, so they're not
missing at random. That's why we flagged them instead of deleting them.

**Why a 30-minute window for riders and recent delays?**
A reasonable single choice, not tuned; we kept it fixed to avoid fitting the validation days with many
variants. It's a fair next experiment.

**Your model ties the app. So what's the point?**
Three things. It reaches the app's own accuracy from public data alone, openly and reproducibly. It
explains *why* orders are slow, which the app doesn't. And with real-time features it beats the app's
estimate on validation days, except at lunch, which tells the platform where post-order actions matter.

**How would this be deployed?**
Score at checkout (milliseconds), show an order-specific buffer instead of a flat one, retrain on a
schedule, and monitor input drift (distance mix, missing prep estimates). Combine it with the app's
after-order updates rather than replacing them.

**Couldn't better predictions be used to push riders harder?**
Yes, that's the ethics risk we name. Shorter promises put pressure on riders, and the 2020 "Delivery Riders,
Trapped in the System" article covered Meituan, the platform behind our data (and Ele.me). Errors also differ by district (4.4–9.0
min), so some areas get worse estimates. We'd judge any deployment on rider workload too, not just lateness.

**Why not just use the app's promise as an input, like Uber corrects its routing ETA?**
It would probably win, but it changes the question from "what can be predicted from the order itself?" to
"how do we adjust Meituan's number?", and the model would partly learn Meituan's padding rule. It's a design choice: see §9 Q2.

**What surprised you most?**
The 8-minute cliff: late arrivals more than halve exactly 8 minutes after the promise, at every promise
level. That's an operational rule kicking in after ordering, and it explains why the app wins the promise
test.

**If you had another week?**
Confirm the extended model on fresh days, add a day-of-week feature with more weekends, and try combining
our estimate with the app's after-order updates.

## 9. The five hardest questions from the report review (21 Nov) [everyone should know these]

From a mock harsh-instructor review of the 21 Nov report. These target its weakest points, so expect them.

**1. "Your intervals are ±0.03 on 140k orders. Are those orders independent? What's the real uncertainty?"**
No, they aren't independent: orders share days, districts, hours, couriers and restaurants. The bootstrap
resamples orders, so it only shows order-level noise on those days (the report now says so). The honest
view is per day:
- Boosting beats Random Forest on 5 of 6 held-out days (CV: −0.09, −0.09, −0.05, −0.04).
- It ties on Sunday (0.00) and wins on Monday (−0.10).
- Day-to-day variation (Sunday 6.77 vs Monday 6.17) is far bigger than any model gap.

So the claim is: boosting ≈ Random Forest, and both clearly beat the median, by 30% on Sunday and 33% on Monday.

**2. "The promise is shown at checkout. Why isn't it an input, when the platform's prep estimate is?"**
It's a choice, not leakage. We kept the promise out so our estimate stays independent of it and can be
compared with it. Feeding it in would mostly copy the platform's own internal estimate, which defeats
the question of what public order-time data can do. Combining the two would probably beat both on MAE,
and that's fair future work.

**3. "Why did you drop the weekend flag? A jump from 6.8 to 18 minutes looks like a bug."**
Admit it: the jump was a symptom, not the reason.
- In the fold that validates on Saturday, the training days hold only 14 "weekend" rows (Sunday orders
  that arrived after midnight).
- Scaling that near-constant column blew up the linear model.
- The real reason is that there's one weekend day in training and only one fold that could test it.
- The cost shows on Sunday: predicted 2.1 min too short, MAE 6.77.
- With more weeks, a day-of-week feature is the first thing to add.

**4. "Your q80 promise loses to the platform. Is that a fair test?"**
Not fully, and the report says so. The actual delivery times were produced by a dispatcher working to
the platform's own promise; the cliff at exactly +8 min late shows it acting after the order. So any
other promise is judged on the platform's turf. Unshifted, our q80 model also covers only 76.6% of test
orders, not 80%, mostly because Sunday ran slow. With average promises under about 37 minutes, our
model is late less often at the 0-minute threshold.

**5. "The extension was designed after the test run and scored on the folds you tuned on. How much of the
0.33 is real?"**
- Every extension feature uses only deliveries finished before the order.
- The hyperparameters stayed frozen, and re-tuning picked the same settings.
- Elastic-Net, Random Forest and boosting all gain the same (−0.33, −0.31, −0.33), so it's the
  information in the features, not extra model capacity.
- We deliberately didn't re-score the test days.

The honest claim: "better on validation days, to be confirmed on new days", which is future work (1).

**"Is the prep estimate really known when the order is placed?"**
The file doesn't timestamp it, so we assume it is (the report says so). The placeholder defaults are
written within seconds of the order and none equals the dispatch time. If real estimates were set later,
prep's +0.68 importance would be optimistic.

**"Your target is skewed. Did you try a log transform?"**
Yes. On CV the raw target beat the log one (Elastic-Net 6.59 vs 6.73), and since we report MAE, which
targets the median, the skew matters less.

**"Why 6.24 on the drivers slide but 6.25 everywhere else?"**
6.24 is the average of the four fold MAEs; 6.25 is pooled over all CV orders. Same model, two ways of
averaging.
