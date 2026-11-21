# 01_cover

Our project is predicting food delivery time and its key delay drivers. The question underneath it is simple: can we predict how long your food will take the moment you press order? We used Meituan's data from the INFORMS 2024 challenge.

---

# 02_same_wait

Houston airport had a problem: passengers complained they waited too long for their bags. The airport fixed it without making a single bag faster. They moved the arrival gates further away, so people walked six times longer, and the complaints almost disappeared. Same wait, different feeling. Right now, while I'm talking, about fifty people in one city just pressed order, and every one of them was immediately given a promise. The people who use the answer are the platform's operations team, who decide how long to promise and how many couriers to plan. So our research question is: using only information available when an order is placed, how accurately can we predict delivery time, and what drives long deliveries?

---

# 03_meet_order

Let's follow one of them. Sunday, 23 October, 11:13. Someone orders lunch from a restaurant 3.2 kilometres away. The app says: 51 minutes. Here's everything it knows at that second, and everything it doesn't: the shaded part of the timeline is the future, so we never use it. And note that we predict how long the food actually takes, not the promise. The data covers 546 thousand orders over 8 days in 23 districts.

---

# 04_cleaning

Before we could follow any order, we had to find the real ones. We started from 654 thousand rows and ended with 546 thousand orders. We removed 85,797 refused dispatches, because they are repeat offers of the same order, not new orders. We removed 22,181 pre-booked orders, a different population that holds almost all deliveries over three hours, and 24 implausible durations. The 13.8 percent of orders with a default prep estimate we kept, but flagged as missing, because they are not missing at random.

---

# 05_distance

Our order was 3.2 kilometres away. Every kilometre adds about seven minutes, in every district, so a friend ordering the same dish from one kilometre away would get it about fifteen minutes sooner. The spread also grows with distance, which is why a promise needs a higher percentile than the average. Distance is our core feature.

---

# 06_peaks

And our customer ordered at the slowest hour of the day. Half the city had the same idea: the median delivery at 11:00 is 33.5 minutes, against 27.8 overall. Surprisingly, how busy the area is barely matters once you compare the same district and hour. So we added lunch and dinner peak flags, and a cyclical time of day so that 23:59 sits next to midnight.

---

# 07_models

You know the friend who texts "five minutes away" and arrives twenty minutes later? The app is the opposite friend: it never promises under 30 minutes, promises 38 on average, and food takes 30. Padded, and still late 15 percent of the time. We compare two baselines, the median guess and the app's own promise, with three models: Elastic-Net because it is readable, Random Forest because it is robust, and gradient boosting because it is usually strongest on tabular data. All were tuned by random search on the cross-validation folds. They only see what is known at ordering: distance, prep estimate, time of day, district load and district. Never courier, dispatch or pickup, because those happen after the order.

---

# 08_time_split

We held ourselves to the app's rules. The model learns from earlier days and predicts later ones. The last two days, including our Sunday order, were locked away until the very end and scored once. We report error in minutes, plus RMSE, R squared and bootstrap confidence intervals. We dropped the weekend flag because training had only one weekend day, and all preprocessing is refitted inside each fold, so nothing leaks. Tuning mattered: with 511 leaves the training error was 2.45 minutes but the validation error 6.63.

---

# 09_accuracy

So, our order. The app said 51. Our model said 45. It arrived in 43. Across all 140 thousand test orders, we're off by 6.5 minutes on average: 31 percent better than guessing, and 3 minutes closer than the app. But the app's promise isn't trying to be accurate, so this isn't a fair fight. That's slide 12. The three models land within 0.3 minutes of each other, which tells us the limit is the information, not the model, and the test error is only 0.2 minutes above cross-validation, so it holds up on new days. R squared is 0.49, and we'll come back to why that is not weak.

---

# 10_drivers

So why did our order take 43 minutes? 12.5 minutes until pickup, about average, then 31 on the road. Mostly distance, then lunchtime. In the driver chart, distance at plus 3.10 sits far above time of day, district and prep estimate. The busy-area effect people expect? Almost nothing. Pickup and road each take a median of 13.1 minutes, and both are about 2.7 minutes slower at peaks. So our proposal was right on distance and peaks, and wrong on load.

---

# 11_errors

Lunch is our hardest hour, and long trips are hard too. Under one kilometre we're off by 5.6 minutes, over seven kilometres by 14.4. At 11:00 the error is 7.2 against 6.5 overall. For orders like ours, we're off by 8.4 minutes, not 6.5. Still better than the app's 11. Sunday is a little harder than Monday, and districts range from 4.4 to 9 minutes.

---

# 12_promise

A weather forecast tells you it will probably rain. A promise says you'll stay dry. Those are different jobs. We turned our forecast into promises with the same average length as the app's, 38.2 minutes, using boosting at the 80th percentile shifted by 2.7 minutes. And the app was still late less often: 5.0 percent of orders more than five minutes late, against our 6.1. Look at this cliff: late orders more than halve at exactly 8 minutes late. Something happens after the order is placed. Someone starts rushing, and a model at ordering can't see that. Except for shorter promises. Better estimates are not automatically better promises.

---

# 13_meaning

That someone rushing is a real person. In 2020 a Chinese magazine published a viral article, Delivery Riders, Trapped in the System, on algorithms shortening delivery times until riders ran red lights to keep up. The company in that story is the one whose data we used. Our answer: at ordering, delivery time can be predicted to about 6.5 minutes, and distance is the main driver. The ceiling is missing information: with after-order times the error drops from 6.25 to 4.53 and R squared rises from 0.51 to 0.72, which is why 0.49 is not a weak model. Our limits are eight days with one weekend day, and no weather, traffic or courier data. The error is uneven across districts, and every minute cut from a promise lands on a rider. Next, we would update the estimate after dispatch and add restaurant history.

---

# 14_closing

Houston didn't make the bags faster, it changed the wait. Since we started talking, about 500 people in one city were given a promise. We can make that number more accurate. What we learned is that a good promise needs more than an accurate number. Thank you.

---

# 15_b1_cleaning_table

Here is every cleaning rule with its count and reason, from 654,343 rows to 546,340 orders, split into 406,553 training and 139,787 test orders.

---

# 16_b2_leakage

If the model were allowed to know dispatch and pickup times, its error would drop from 6.25 to 4.53 minutes and R squared would rise from 0.51 to 0.72. That information doesn't exist at ordering, so missing information is the ceiling, and R squared 0.49 is not a weak model.

---

# 17_b3_tuning

These are the final settings and the search budget for each model, chosen by random search on cross-validated error, and pinball loss for the 80th-percentile model. The slower tree models were tuned on a sample of rows and then refitted on all of them. Bigger trees overfit: 511 leaves gives training error 2.45 against validation 6.63.

---

# 18_b4_error_by_district

On the test days, error ranges from 4.4 to 9 minutes across the 23 districts. The same model is about twice as wrong in some districts as in others, which is the ethics point on slide 13. The figure shown is the cross-validation version.

---

# 19_b5_weekend

We dropped the weekend flag because training had only one weekend day, and none in the first three folds. On the Saturday fold, Elastic-Net's error jumped from 6.8 to 18 minutes. Weekend stays an EDA finding and a stated limitation.

---

# 20_b6_distance_metric

Straight-line and street-grid distance give the same cross-validated error, 6.282 against 6.284 minutes. The difference is minus 0.002 minutes with a confidence interval that includes zero, so we kept Haversine, the simpler default.

---

# 21_b7_stages_by_area

Pickup and road each take a median of 13.1 minutes, and both run about 2.7 minutes slower at meal peaks. This figure breaks the two stages down by district.

---

# 22_b8_promise_padding

35 percent of promises sit exactly at the 30-minute minimum; the app never promises less. And late orders more than halve at exactly 8 minutes late, which suggests someone starts rushing once an order is about to be very late.

---

# 23_b9_three_words

Three words we use precisely. Delivery time is order to arrival, what we predict: 43 minutes for our order. The promise is the time shown at checkout, a padded commitment: 51 minutes. Delay is delivery time minus promise, minus 8 minutes here, and we only use it to describe the data. Our estimate aims at the middle; our promise aims at the 80th percentile, and only the promise is compared with the app's.

---

# 24_b10_padding_cost

Arriving early sounds good, but a padded promise isn't free. Long promises lose orders, customers plan around a wrong time, trust wears off once people learn the number is padded, and operations still need the real time. And the same buffer for every order is too much at one kilometre and too little at seven.

---

# 25_b11_scorecard

Did we beat the app? On accuracy, yes: 6.49 against 9.62. We also explain why. For shorter promises, below about 37 minutes, we come out ahead. But for promises at the app's own length, we are late more often: 6.1 against 5.0 percent more than five minutes late.

---

# 26_b12_typical_order

Our order isn't cherry-picked. Among the 634 Sunday orders placed at 11 o'clock and three to five kilometres away, the medians are 45.3 actual, 52.2 promised and 45.2 predicted, close to our order's 43, 51 and 45. In that group we're off by 8.4 minutes on average and the app by 11, and 26 percent arrived after the promise.
