# Frozen model settings (committed at CP3)

`python -m experiments.final` reads `<model>.json` from here. Without a file, that model runs with its
defaults and the manifest says so, which is fine for plumbing checks and wrong for the report.

At **CP3** each owner freezes their model by copying the best tuning result here:

```bat
copy results\tuning\elasticnet_base.json experiments\final_params\elasticnet.json   :: Lynn
copy results\tuning\hgb_q80_base.json    experiments\final_params\hgb_q80.json      :: Lynn
copy results\tuning\hgb_base.json        experiments\final_params\hgb.json          :: Mahmoud
copy results\tuning\rf_base.json         experiments\final_params\rf.json           :: Mahmoud
```

(`results/tuning/` is git-ignored, so this folder is the only committed record of the final settings.)
After CP3 these files change only for a bug fix, agreed by all three.
