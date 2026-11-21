<!-- ppt-master-schema: design-spec/v1 -->
# Delivery Time Prediction - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | delivery_deck |
| Canvas Format | ppt169 (1280 × 720) |
| Page Count | 26 |
| Primary Language | en |
| Target Audience | DSAI 5101 instructor grading against the Part A rubric, plus master's classmates who know ML basics but not this dataset or delivery platforms |
| Communication Intent | Explain how accurately delivery time can be predicted at order time and what drives long deliveries, then persuade that a better estimate is not automatically a better promise; follow one real order (#85188) through the whole talk |
| Desired Audience Outcome | The audience can state the research question, trust the leakage-free time-split evaluation, remember MAE 6.5 min (3.1 closer than the app) and distance as the main driver, and understand why the app still makes better promises |
| Core Message / Ask / Action | At ordering, delivery time can be predicted to about 6.5 minutes and distance drives it, but a good promise needs more than an accurate number, and every minute cut from a promise lands on a rider |
| Delivery Context | Primary: presenter-led 10-minute live class talk by three speakers plus 5-minute Q&A on Sun 22 Nov; the deck is imported into Canva and edited there. Secondary: backup slides to point at during Q&A |
| Artifact Afterlife | Editable in Canva by three teammates; exported to PDF and PPTX, slides.pdf committed to the repo |
| Reading Mode | balanced |
| Content Strategy | balanced default (outline is a Reference; its slide order, finding-titles and numbers are kept) |
| Design Style | Follow the Order — reference-sheet blues, soft rounded cards, gradient discs, order #85188 ticket motif |
| AI Image Acquisition Path | not applicable — no image backend or host image tool available; per the confirmed image_notes fallback the cover phone, baggage-claim disc and map textures are native vector shapes |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — final Stage-2 proactive policy |
| Custom Animations | disabled — final Stage-2 proactive policy |
| Narration Audio | disabled — final Stage-2 proactive policy |
| Created Date | 2026-11-15 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px left/right, 48 px top/bottom |
| Content Area | x 64–1216, y 48–672 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: narrative
- **Mode Behavior**: Story arc over the outline's five sections: Houston hook and question, meet order #85188, data and EDA, method, results, then the promise twist and the rider. Titles state the finding, not the topic. Each section opens with the reference's '01 ——' numbered kicker, and the order card returns on slides 3, 5, 6, 8, 9, 10, 11 with the one number that slide adds. Backup slides answer Q&A plainly.
- **Visual style**: custom
- **Visual Style References**: soft-rounded
- **Visual Style Behavior**: Reference-sheet look: near-white field with large soft navy-to-ice gradient discs bleeding off one corner; generous rounded cards (about 16 px radius) with very soft shadows; icons inside pale rounded tiles; navy titles with the key word in electric blue; one big KPI tile per results slide (e.g. '6.49 min MAE'); 'Insight' callout cards with a short blue underline. Figures sit on white rounded cards with comfortable padding. Plenty of white space, one message per slide.
- **Theme**: a delivery app's own launch deck — calm blues, floating cards, the order ticket as the recurring motif (continuity job: shows the talk following one delivery; reuse mode: same card shape, new number each time)
- **Tone**: calm, confident, honest about limits

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FFFFFF | page field |
| Secondary background | #E9F2FA | ice-blue cards, icon tiles, KPI tiles, gradient end |
| Primary | #102A43 | titles, section discs, cover gradient start |
| Accent | #2E6EB8 | key word in titles, KPI numbers, "our model" |
| Secondary accent | #A7C7E7 | gradient mid-stop, soft discs, underlines |
| Body text | #1F2937 | body copy |
| Secondary text | #5B6B7F | captions, kickers, footers |
| Divider | #D5E2F0 | hairlines, card borders |
| Platform (data role) | #EB6834 | "the app / platform" — matches the figures; used only for platform numbers |
| Card shadow | #102A43 | soft shadow at 8% opacity |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | geometric-humanist sans, bold (SF Pro Display stand-in) | Inter | — | sans-serif |
| Body | same family, regular | Inter | — | sans-serif |

- **Typography upgrade (Reference)**: reference sheet names SF Pro Display for titles; Inter is used because Canva and Windows PowerPoint can render it
- **Title stack**: Inter, sans-serif
- **Body stack**: Inter, sans-serif

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 24 |
| Title | 42 |
| Subtitle | 32 |
| Annotation | 18 |
| Cover title | 72 |
| Display (KPI hero number) | 64 |
| Kicker (section number) | 20 |
| Footnote (source line, page number) | 14 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: kicker → finding title (key word in accent) → figure or KPI → one short takeaway; eye lands on the figure
- **Composition tendency**: figure on a white rounded card taking about 60% of the width, a narrow text column with at most three short points, the order ticket floating at a card edge where it applies; a gradient disc bleeds off one corner on every page
- **Cross-page continuity**: numbered kicker per section, the order #85188 ticket, the corner gradient disc, the footer line (course · page number)
- **Spacing posture**: open on anchor pages, moderate on figure pages
- **Spacing anchors**: margin 64 · block gap 32 · column gutter 32 · corner radius 16 · body leading 1.4

## VI. Icon Usage Specification

- **Primary bundled library**: tabler-outline
- **Stroke Width**: 2

| Icon Path | Suitable Scenarios |
| --- | --- |
| icons/tabler-outline/moped.svg | |
| icons/tabler-outline/clock.svg | |
| icons/tabler-outline/map-pin.svg | |
| icons/tabler-outline/route.svg | |
| icons/tabler-outline/chart-bar.svg | |
| icons/tabler-outline/database.svg | |
| icons/tabler-outline/calendar.svg | |
| icons/tabler-outline/settings.svg | |
| icons/tabler-outline/target-arrow.svg | |
| icons/tabler-outline/receipt.svg | |
| icons/tabler-outline/user.svg | |
| icons/tabler-outline/bulb.svg | |
| icons/tabler-outline/alert-triangle.svg | |
| icons/tabler-outline/check.svg | |
| icons/tabler-outline/x.svg | |
| icons/tabler-outline/trending-up.svg | |
| icons/tabler-outline/scale.svg | |
| icons/tabler-outline/filter.svg | |
| icons/tabler-outline/lock.svg | |
| icons/tabler-outline/help-circle.svg | |
| icons/tabler-outline/brand-github.svg | |
| icons/tabler-outline/luggage.svg | |
| icons/tabler-outline/cloud-rain.svg | |
| icons/tabler-outline/building-skyscraper.svg | |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| P15 | table | record_table | every cleaning rule with rows affected and reason |
| P17 | table | record_table | final settings and tuning budget per model |
| P23 | table | comparison_matrix | three terms × definition and example value |
| P26 | table | comparison_matrix | order vs segment medians and MAE |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| order_timeline.png | 1173x700 | 1.68 | order #85188 timeline, known-at-ordering shaded | Chart | figure on a white rounded card | no-crop | user | Existing | project figure figures/eda/order_timeline.png | none | local |
| cleaning_funnel.png | 1371x838 | 1.64 | 654k rows → 546k orders | Chart | figure card beside step list | no-crop | user | Existing | figures/eda/cleaning_funnel.png | none | local |
| delivery_vs_distance.png | 1053x820 | 1.28 | ~7 min per km | Chart | figure card, takeaway beside | no-crop | user | Existing | figures/eda/delivery_vs_distance.png | none | local |
| delivery_by_hour.png | 995x959 | 1.04 | peak at 11:00 | Chart | near-square figure card | no-crop | user | Existing | figures/eda/delivery_by_hour.png | none | local |
| time_split.png | 2247x1094 | 2.05 | forward-chaining CV and test days | Chart | wide figure card across the page | no-crop | user | Existing | figures/results/time_split.png | none | local |
| hgb_complexity_curve.png | 1659x1119 | 1.48 | tuning inset on P08, full on B3 | Chart | small inset card (P08), figure card (B3) | no-crop | user | Existing | figures/results/hgb_complexity_curve.png | none | local |
| test_mae.png | 2794x1159 | 2.41 | test MAE by model | Chart | wide figure card under KPI tiles | no-crop | user | Existing | figures/results/test_mae.png | none | local |
| delay_drivers.png | 1797x1027 | 1.75 | driver importance | Chart | figure card | no-crop | user | Existing | figures/results/delay_drivers.png | none | local |
| errors_by_distance.png | 1815x1025 | 1.77 | error by distance, test days | Chart | figure card | no-crop | user | Existing | figures/results/errors_by_distance.png | none | local |
| errors_by_hour.png | 1799x1074 | 1.68 | error by hour, test days | Chart | figure card | no-crop | user | Existing | figures/results/errors_by_hour.png | none | local |
| final_test_gap.png | 687x532 | 1.29 | promise test: share late | Chart | main figure card | no-crop | user | Existing | figures/promise/final_test_gap.png | none | local |
| promise_padding.png | 1102x797 | 1.38 | 8-min cliff inset (P12) and B8 | Chart | small inset (P12), figure card (B8) | no-crop | user | Existing | figures/eda/promise_padding.png | none | local |
| leakage_audit.png | 1471x705 | 2.09 | honest vs leaky model (B2) | Chart | wide figure card | no-crop | user | Existing | figures/eda/leakage_audit.png | none | local |
| errors_by_area.png | 1823x1302 | 1.40 | error by district (B4) | Chart | figure card | no-crop | user | Existing | figures/results/errors_by_area.png | none | local |
| stages_by_area.png | 1605x1120 | 1.43 | stages by district (B7) | Chart | figure card | no-crop | user | Existing | figures/eda/stages_by_area.png | none | local |

## IX. Content Outline

### Part 1: Problem & Motivation

#### Slide 01 - Cover

- **Audience move**: no context → curious about how long food takes and why
- **Relationships**: none
- **Composition**: left: title block; right: phone hero with floating "Estimated arrival 51 min" ticket; gradient disc behind
- **Cover impact**: hook — the app's "51 min" promise on a phone, the order we follow
- **Title**: Predicting Food Delivery Time and Its Key Delay Drivers
- **Core message**: one order, one promise, one prediction
- **Content**: subtitle "Can we predict delivery time the moment you order?" · team: Lynn Younes (60107070) · Sumaiya Rizwan (60102626) · Mahmoud Abdelaziz (60328910) · DSAI 5101 · 22 Nov 2026 · Meituan INFORMS TSL 2024 data
- **Images**: none — native vector phone frame with a stylised map (street lines, route, pin) and the floating ETA ticket

#### Slide 02 - Same wait, different feeling

- **Audience move**: neutral → sees waiting as a perception problem and hears the research question
- **Relationships**: contrast between real wait and felt wait; the question follows from it
- **Composition**: left text with boxed research question; right a large gradient disc holding a native luggage/carousel motif (luggage icon, conveyor arc)
- **Title**: Same wait, different feeling
- **Core message**: can we predict delivery time the moment you order?
- **Content**: Houston fixed bag complaints without faster bags · ~50 orders a minute, in one city · who uses it: the platform's operations team (promise length, courier planning) · boxed question: "Using only information available when an order is placed, how accurately can we predict delivery time, and what drives long deliveries?"

#### Slide 03 - Meet order #85188

- **Audience move**: abstract question → one concrete order to follow
- **Relationships**: order — known at ordering precedes the future (leakage) part of the timeline
- **Composition**: figure card with the order ticket floating at its corner; three small fact chips below
- **Title**: Meet order #85188: what the app knew at 11:13
- **Core message**: we predict how long it actually takes, not the promise
- **Content**: ticket: Sun 23 Oct · 11:13 · 3.2 km · app promise 51 min · chips: 546k orders · 8 days · 23 districts · note: anything after the shaded part is the future (never used)
- **Images**: order_timeline.png
- **Motion suggestion**: order ticket is introduced here and recurs on later slides (Morph candidate)

### Part 2: Data & EDA

#### Slide 04 - Cleaning

- **Audience move**: trusts the dataset was handled carefully
- **Relationships**: order — three removal steps from raw rows to orders; membership — default prep estimates flagged, not dropped
- **Composition**: section kicker 02; funnel figure card left; three numbered steps with reasons right
- **Title**: The raw data needed real cleaning: 654k rows → 546k orders
- **Content**: refused dispatches −85,797 (repeat offers, not new orders) · pre-booked −22,181 (different population, almost all >3 h deliveries) · implausible durations −24 · default prep estimates (13.8%) flagged as missing, not dropped
- **Images**: cleaning_funnel.png

#### Slide 05 - Distance

- **Audience move**: sees distance as the core feature
- **Relationships**: link — distance raises delivery time; spread grows with distance
- **Composition**: figure card; KPI tile "+7 min / km"; order ticket "3.2 km"
- **Title**: Delivery time rises ~7 min per km, in every district
- **Content**: a friend 1 km away gets the same dish ~15 min sooner · spread grows with distance → promises need a higher percentile · → distance is the core feature
- **Images**: delivery_vs_distance.png

#### Slide 06 - Peaks

- **Audience move**: sees time of day matters; area load barely does
- **Relationships**: contrast — 11:00 median vs overall median
- **Composition**: near-square figure card; KPI tile "33.5 vs 27.8 min"; order ticket "11:13"
- **Title**: Slowest at meal peaks: median 33.5 min at 11:00 vs 27.8 overall
- **Content**: area load barely matters within the same district and hour · → lunch/dinner peak flags + cyclical time of day (23:59 sits next to 00:00)
- **Images**: delivery_by_hour.png

### Part 3: Methods & Evaluation

#### Slide 07 - Models

- **Audience move**: knows what was compared and what information was allowed
- **Relationships**: membership — two baselines, three models; contrast — allowed features vs forbidden after-order features
- **Composition**: section kicker 03; five rounded cards in two groups (baselines | models) each with a one-line reason; a feature strip below with allowed and excluded chips
- **Title**: Two baselines, three models, order-time information only
- **Content**: baselines: median guess · the platform's own promise · models: Elastic-Net (readable) · Random Forest (robust) · gradient boosting (strongest on tabular data) · tuned by random search on the CV folds · features: distance, prep estimate, time of day, district load, district · never: courier, dispatch, pickup · insight: "Padded, and still late 15% of the time."

#### Slide 08 - Time split

- **Audience move**: trusts evaluation has no leakage
- **Relationships**: order — training days precede validation day precede locked test days
- **Composition**: wide time-split figure card on top; three short points and a small complexity-curve inset below
- **Title**: Tested like real life: the model only ever sees the past
- **Content**: forward-chaining CV on 17–22 Oct · test 23–24 Oct scored once (our Sunday order is in it) · MAE in minutes (also RMSE, R², bootstrap 95% CIs) · weekend flag dropped (one weekend day in training) · preprocessing refitted inside each fold · tuning mattered: 511 leaves → train 2.45 vs CV 6.63
- **Images**: time_split.png, hgb_complexity_curve.png (inset)

### Part 4: Results & Insights

#### Slide 09 - Accuracy

- **Audience move**: remembers 6.5 min and 3.1 min closer than the app
- **Relationships**: contrast — our model vs the app's promise vs median baseline
- **Composition**: section kicker 04; three KPI tiles (app said 51 · we said 45 · arrived 43) then the wide test-MAE figure card; one honest caveat line
- **Title**: Our model misses by 6.5 min: 3.1 min closer than the app's promise
- **Content**: test MAE: promise 9.62 · median 9.46 · Elastic-Net 6.80 · RF 6.54 · boosting 6.49 · 31% better than guessing · three models within 0.3 min → the limit is the information · test ≈ CV + 0.2 min · R² 0.49 shown openly · caveat: "The app's promise isn't trying to be accurate — slide 12."
- **Images**: test_mae.png

#### Slide 10 - Drivers

- **Audience move**: knows distance dominates and load barely matters
- **Relationships**: order — drivers ranked by effect size
- **Composition**: figure card; order ticket "12.5 min to pickup + 31 on the road"; insight card
- **Title**: Distance drives delivery time; how busy the area is barely matters
- **Content**: distance +3.10 ≫ time +0.86 ≈ district +0.83 > prep +0.67 > load +0.19 · pickup and road each a median 13.1 min; both ~2.7 min slower at peaks · proposal: right on distance and peaks, wrong on load
- **Images**: delay_drivers.png

#### Slide 11 - Errors

- **Audience move**: sees where the model is weak
- **Relationships**: contrast — short vs long trips, lunch vs overall
- **Composition**: two figure cards side by side; order ticket "8.4 vs app 11.0"
- **Title**: Our model struggles with long trips and the lunch rush
- **Content**: < 1 km 5.6 vs > 7 km 14.4 · 11:00 7.2 vs 6.5 overall · Sunday 6.77 vs Monday 6.17 · districts 4.4–9.0
- **Images**: errors_by_distance.png, errors_by_hour.png

#### Slide 12 - Promise twist

- **Audience move**: understands better estimates ≠ better promises
- **Relationships**: contrast — our promise vs the app's promise at equal average length
- **Composition**: main figure card; KPI pair 5.0% (app, orange) vs 6.1% (ours, blue); small cliff inset; one-line takeaway
- **Title**: Same average promise: the app is still late less often
- **Content**: forecast vs promise are different jobs · our q80 boosting promise shifted +2.7 min to the app's 38.2-min average · >5 min late: app 5.0% vs ours 6.1% · late orders more than halve at exactly 8 min late → someone rushes after ordering · "Except for shorter promises." · better estimates ≠ better promises
- **Images**: final_test_gap.png, promise_padding.png (inset)

### Part 5: Conclusion

#### Slide 13 - Meaning and limits

- **Audience move**: holds the answer, its ceiling, and the human cost
- **Relationships**: membership — answer, ceiling, limitations, ethics, next steps
- **Composition**: section kicker 05; four rounded cards with icons (Answer · Ceiling · Limits · Ethics) and a next-steps strip
- **Title**: What it means, and what it can't tell us
- **Content**: answer: ~6.5 min at ordering, distance the main driver · ceiling: with after-order times MAE 6.25 → 4.53, R² 0.51 → 0.72 · limits: 8 days, one weekend day; no weather, traffic or courier data · ethics: error uneven across districts (4.4–9.0); every minute cut lands on a rider · next: update after dispatch; restaurant history

#### Slide 14 - Closing

- **Audience move**: leaves with the takeaway, ready for questions
- **Relationships**: none
- **Composition**: navy gradient field, one large takeaway line, questions + repo link + names
- **Closing impact**: takeaway — a good promise needs more than an accurate number
- **Title**: A good promise needs more than an accurate number
- **Content**: Thank you · Questions? · github.com/lynn60107070/dsai5101-delivery-eta · Lynn Younes · Sumaiya Rizwan · Mahmoud Abdelaziz
- **Hyperlinks**: "github.com/lynn60107070/dsai5101-delivery-eta" → https://github.com/lynn60107070/dsai5101-delivery-eta

### Part 6: Backup (Q&A only)

#### Slide 15 - B1 Cleaning table

- **Audience move**: sees every cleaning rule with counts
- **Relationships**: order — rules applied in sequence
- **Title**: B1 · Every cleaning rule, with counts
- **Content**: table: keep grabbed dispatches −85,797 · timestamp 0 → missing (prep 9,874; arrival 1) · prep < 5 min → missing, flagged (75,361; 13.8%) · no arrival time −1 · pre-booked excluded −22,181 · > 180 min excluded −24 · missing prep → training median inside each model
- **Visualization**: cleaning-rules table/record_table
- **Native-ready**: cleaning-rules=yes

#### Slide 16 - B2 Leakage audit

- **Audience move**: sees missing information is the ceiling
- **Relationships**: contrast — honest vs leaky model
- **Title**: B2 · With after-order times, error drops from 6.25 to 4.53 min
- **Content**: R² 0.51 → 0.72 · why R² 0.49 is not a weak model
- **Images**: leakage_audit.png

#### Slide 17 - B3 Tuning

- **Audience move**: sees settings and search budget
- **Relationships**: membership — four models with settings and budget
- **Title**: B3 · Final settings and tuning budget
- **Content**: table: Elastic-Net α 0.002, L1 ratio 0.66 (30 tries, all rows) · Random Forest 200 trees, min leaf 6, 31% features, depth 20 (10 tries, 100k rows) · Boosting absolute-error loss, lr 0.038, 76 leaves, min leaf 70, L2 7.9, 800 iterations (20 tries, 150k) · Boosting q80 quantile loss, lr 0.055, 29 leaves, min leaf 126, 200 iterations (20 tries, 150k) · complexity curve
- **Visualization**: model-settings table/record_table
- **Native-ready**: model-settings=yes
- **Images**: hgb_complexity_curve.png

#### Slide 18 - B4 Error by district

- **Audience move**: sees uneven error across all 23 districts
- **Relationships**: contrast across districts
- **Title**: B4 · Error ranges from 4.4 to 9.0 min across districts
- **Images**: errors_by_area.png
- **Content**: test days, all 23 districts

#### Slide 19 - B5 Weekend flag

- **Audience move**: understands why is_weekend was dropped
- **Relationships**: link — one weekend day in training → unstable Saturday fold
- **Title**: B5 · Why we dropped the weekend flag
- **Content**: one weekend day in training, none in CV folds 1–3 · Saturday fold: Elastic-Net MAE 6.8 → 18.0 · weekend kept as EDA finding and a limitation

#### Slide 20 - B6 Distance metric

- **Audience move**: sees distance choice barely matters
- **Relationships**: contrast — Haversine vs Manhattan
- **Title**: B6 · Haversine vs Manhattan: no real difference
- **Content**: CV MAE 6.282 (Haversine) vs 6.284 (Manhattan) · difference −0.002 min, 95% CI −0.007 to +0.003, includes 0 · kept Haversine (simpler)

#### Slide 21 - B7 Stages by area

- **Audience move**: sees pickup vs road time by district
- **Relationships**: membership — two stages per district
- **Title**: B7 · Pickup and road time by district
- **Images**: stages_by_area.png
- **Content**: pickup and road each a median 13.1 min

#### Slide 22 - B8 Promise padding

- **Audience move**: sees the 30-min floor and the 8-min cliff
- **Relationships**: contrast — before vs after 8 min late
- **Title**: B8 · 35% of promises sit at the 30-min minimum
- **Images**: promise_padding.png
- **Content**: the 8-min cliff: late orders more than halve at exactly 8 min late

#### Slide 23 - B9 Three words

- **Audience move**: separates delivery time, promise and delay
- **Relationships**: membership — three definitions with the example order; contrast — estimate vs promise
- **Title**: B9 · Delivery time, promise, delay
- **Content**: table: delivery time = order → arrival (43 min, what we predict) · promise = time shown at checkout (51 min, padded commitment) · delay = delivery − promise (−8 min) · estimate aims at the middle; promise aims at the 80th percentile
- **Visualization**: three-words table/comparison_matrix
- **Native-ready**: three-words=yes

#### Slide 24 - B10 Padding isn't free

- **Audience move**: sees why early arrival still has a cost
- **Relationships**: membership — four costs; contrast — same buffer too much at 1 km, too little at 7 km
- **Title**: B10 · Why a padded promise isn't free
- **Content**: lost orders · bad customer planning · trust wears off · operations need the real time · same buffer for every order → too much at 1 km, too little at 7 km

#### Slide 25 - B11 Scorecard

- **Audience move**: sees exactly what we won and lost
- **Relationships**: contrast — won vs lost
- **Title**: B11 · Scorecard: what we won and lost
- **Content**: ✓ accuracy (6.49 vs 9.62) · ✓ explains why · ✓ shorter promises (below ~37 min) · ✗ promises at the app's own length (6.1% vs 5.0% > 5 min late)

#### Slide 26 - B12 Typical order

- **Audience move**: trusts order #85188 isn't cherry-picked
- **Relationships**: contrast — the order vs its segment medians
- **Title**: B12 · Order #85188 is a typical one
- **Content**: segment: 634 Sunday orders at 11:xx, 3–5 km · medians: actual 45.3 · promise 52.2 · ours 45.2 · segment MAE: ours 8.4 · app 11.0 · 26% arrived after the promise
- **Visualization**: typical-order table/comparison_matrix
- **Native-ready**: typical-order=yes

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: use the outline's spoken scripts and hooks for each slide where given (Houston, "right now", the friend, weather forecast, Trapped in the System, closing); keep their wording; add one-line answers on backup slides from the outline
- **Total duration**: ~9 min 5 s main slides (per-slide timings from the outline), backups on demand
- **Notes style**: conversational
- **Presentation purpose**: explain predictability at order time and its drivers, then persuade that a better estimate is not a better promise
