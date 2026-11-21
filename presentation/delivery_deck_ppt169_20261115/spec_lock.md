<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: en
- audience: DSAI 5101 instructor grading against the rubric, plus master's classmates new to this dataset
- objective: Explain how accurately delivery time can be predicted at order time and what drives it, then show a better estimate is not a better promise, so the audience remembers MAE 6.5 min, distance as the driver, and why the app still promises better
- core_message: At ordering, delivery time can be predicted to about 6.5 minutes and distance drives it, but a good promise needs more than an accurate number, and every minute cut from a promise lands on a rider
- consumption_mode: balanced

## mode
- mode: custom
- mode_references: narrative
- mode_behavior: Story arc over five sections (hook and question, order #85188, data, method, results, promise twist and the rider); titles state the finding; each section opens with a numbered '01 ——' kicker; the order ticket card returns on slides 3, 5, 6, 8, 9, 10, 11 with that slide's number; backups answer Q&A plainly.

## visual_style
- visual_style: custom
- visual_style_references: soft-rounded
- visual_style_behavior: Near-white field with large soft navy-to-ice gradient discs bleeding off one corner; rounded cards (16 px radius) with very soft shadows; icons in pale rounded tiles; navy titles with the key word in electric blue; one big KPI tile per results slide; 'Insight' callout cards with a short blue underline; figures on white rounded cards with padding; plenty of white space, one message per slide.

## colors
- background: #FFFFFF
- secondary_bg: #E9F2FA
- primary: #102A43
- accent: #2E6EB8
- secondary_accent: #A7C7E7
- body_text: #1F2937
- secondary_text: #5B6B7F
- divider: #D5E2F0
- platform: #EB6834
- shadow: #102A43

## typography
- font_family: Inter, sans-serif
- title_family: Inter, sans-serif
- body_family: Inter, sans-serif
- body: 24
- title: 42
- subtitle: 32
- annotation: 18
- cover_title: 72
- display: 64
- kicker: 20
- footnote: 14

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: tabler-outline/moped, tabler-outline/clock, tabler-outline/map-pin, tabler-outline/route, tabler-outline/chart-bar, tabler-outline/database, tabler-outline/calendar, tabler-outline/settings, tabler-outline/target-arrow, tabler-outline/receipt, tabler-outline/user, tabler-outline/bulb, tabler-outline/alert-triangle, tabler-outline/check, tabler-outline/x, tabler-outline/trending-up, tabler-outline/scale, tabler-outline/filter, tabler-outline/lock, tabler-outline/help-circle, tabler-outline/brand-github, tabler-outline/luggage, tabler-outline/cloud-rain, tabler-outline/building-skyscraper

## images
- timeline: images/order_timeline.png | source=user | crop=no-crop
- funnel: images/cleaning_funnel.png | source=user | crop=no-crop
- distance: images/delivery_vs_distance.png | source=user | crop=no-crop
- hour: images/delivery_by_hour.png | source=user | crop=no-crop
- split: images/time_split.png | source=user | crop=no-crop
- complexity: images/hgb_complexity_curve.png | source=user | crop=no-crop
- mae: images/test_mae.png | source=user | crop=no-crop
- drivers: images/delay_drivers.png | source=user | crop=no-crop
- err_dist: images/errors_by_distance.png | source=user | crop=no-crop
- err_hour: images/errors_by_hour.png | source=user | crop=no-crop
- gap: images/final_test_gap.png | source=user | crop=no-crop
- padding: images/promise_padding.png | source=user | crop=no-crop
- leakage: images/leakage_audit.png | source=user | crop=no-crop
- err_area: images/errors_by_area.png | source=user | crop=no-crop
- stages: images/stages_by_area.png | source=user | crop=no-crop

## page_rhythm
- P01: anchor
- P02: breathing
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: dense
- P11: dense
- P12: dense
- P13: dense
- P14: anchor
- P15: dense
- P16: dense
- P17: dense
- P18: dense
- P19: breathing
- P20: breathing
- P21: dense
- P22: dense
- P23: dense
- P24: breathing
- P25: breathing
- P26: dense

## page_visualizations
- P15: table/record_table
- P17: table/record_table
- P23: table/comparison_matrix
- P26: table/comparison_matrix

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
