# AI/BI dashboard

Owner: Person 4. A three-page Databricks AI/BI dashboard over the Gold reporting views created by `notebooks/04_bi_gold_views.ipynb`.

## Components

| Path | Content |
| --- | --- |
| [datasets/](datasets/) | One SQL query per dashboard dataset; the reviewed source of every widget |
| [airbnb_price_analytics.lvdash.json](airbnb_price_analytics.lvdash.json) | Importable dashboard definition generated from the datasets |
| `../scripts/build_dashboard.py` | Generator of the definition; holds page headlines and widget layout |
| `../notebooks/04_bi_gold_views.ipynb` | Creates the documented `v_*` views used by the dashboard and Genie |

Regenerate the definition after changing a dataset, headline or layout:

```bash
python3 scripts/build_dashboard.py --catalog workspace --gold-schema airbnb_gold
```

## Pages

| Page | Question answered | Datasets |
| --- | --- | --- |
| City overview | How large, expensive, available and well rated is each city, and what is its room-type mix and neighbourhood price ranking? | `city_overview`, `room_type_mix`, `top_neighbourhoods` |
| London vs Bristol | Which differences remain when comparing the same room type, guest capacity and price band? | `city_comparison`, `room_type_mix`, `capacity_prices`, `price_bands` |
| Model | Does the model beat the room-type × guests median baseline, and where does it under- or over-price? | `model_mae`, `model_performance`, `predicted_vs_actual`, `error_by_room_type`, `error_by_neighbourhood`, `largest_errors` |

Each page opens with a headline stating its finding. Overview and comparison headlines use measured EDA values and are verified against the dashboard after deployment. The model headline is written after the model test metrics are published. Every price aggregate shows its valid-price denominator; availability is labelled as open calendar days, not occupancy.

## Deployment

1. Run the ETL job for London and Bristol, then `notebooks/04_bi_gold_views.ipynb`.
2. In Databricks open **Dashboards > Create dashboard > Import dashboard from file** and select `airbnb_price_analytics.lvdash.json`.
3. Select a serverless SQL warehouse, open each page and confirm every widget renders. Model widgets show an error until `airbnb_gold.predictions` exists and the views notebook is rerun.
4. Check page headlines against the displayed values and edit them in `scripts/build_dashboard.py` if they differ.
5. **Publish** with embedded credentials disabled, so that viewers' own Unity Catalog permissions apply, and share with the team (**Can view**). Record the published URL in the root README.

Refresh: rerun the ETL job and the views notebook; the dashboard reads views and needs no change. Optionally add a dashboard schedule after the ETL job.

Access: viewers need `USE CATALOG`, `USE SCHEMA` on `airbnb_gold`, `SELECT` on the `v_*` views and `CAN USE` on the SQL warehouse.

## Third city

The views contain no city-specific logic. After the release gate and unchanged first run (`reports/city_c_protocol.md`), rerun the views notebook: the transfer city appears on every page, its model rows are labelled `transfer`, and the model-version filter separates the first run from later changes. The model headline is then updated with the transfer result.
