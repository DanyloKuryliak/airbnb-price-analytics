# Databricks Free Edition setup

## Verified environment

Verification date: 9 November 2026. The authenticated workspace identifies itself as Databricks Free Edition. CLI profile `ucu` is valid, catalog `workspace` exists, and the Repos API is accessible. The Users screen offers Add user, but only the current user is listed; four-person access is not yet verified. GitHub is managed independently through the CLI; Databricks Git integration is optional.

Provisioned team objects:

- Shared project root: `/Workspace/Shared/airbnb-price-analytics`, with a `00_team_start` notebook and role folders `00_project`, `02_etl`, `03_model`, `04_dashboard`, `05_genie`, `06_reports`.
- Reserved lakehouse schemas: `workspace.airbnb_bronze`, `workspace.airbnb_silver`, `workspace.airbnb_gold`. They contain no production tables.
- Workspace-local notebook collaboration group: `airbnb_team`. Only the project administrator is currently a member.

- Schema: `workspace.airbnb_eda`.
- Managed volumes: `workspace.airbnb_eda.raw` and `workspace.airbnb_eda.artifacts`.
- Notebook: `/Workspace/Shared/airbnb-price-analytics/01_eda_london_bristol`.
- [Open notebook](https://dbc-9d87a163-804c.cloud.databricks.com/editor/notebooks/3663423795722864?o=7474649631277855).

Only London and Bristol inputs are permitted. The production schemas are reserved; table interfaces remain proposals in [data_contract.md](data_contract.md). Existing immutable A/B inputs are available for all roles after access is granted; the ETL owner decides whether to reuse these input paths or establish a Bronze raw volume.

## Verified execution

The final notebook completed successfully on Databricks Free Edition on 9 November 2026: [run 462135459584852](https://dbc-9d87a163-804c.cloud.databricks.com/?o=7474649631277855#job/782438016558836/run/462135459584852). Runtime: Python 3.11.10, pandas 1.5.3 and NumPy 1.23.5. Both source SHA-256 checks passed. Counts: London 91,954; Bristol 2,932; raw rows removed: zero. The reports and figures in `docs/` are copied from this successful run. Notebook source contains no saved outputs.

## Shared team entry point

Workspace browser location: **Workspace → Shared → airbnb-price-analytics**. This project is a shared folder in the existing Free Edition workspace, whose displayed name is `workspace`; it is not a second workspace in the workspace switcher.

[Open the team-start notebook](https://dbc-9d87a163-804c.cloud.databricks.com/editor/notebooks/2436275107746855?o=7474649631277855). Share this URL after adding teammates to this workspace. The URL is navigation, not an access token or invitation; recipients must have their own authenticated accounts and the required data privileges.

## Workspace access

The team uses the existing Free Edition workspace; a second workspace is not required. A shared project folder is the collaboration entry point. The root inherits `CAN MANAGE` for workspace `users` from `/Shared`; the explicit `airbnb_team` group grant is `CAN_EDIT`. The inherited permission is broader and remains effective. Changing the project ACL does not remove parent permissions.

1. The workspace administrator opens Settings → Identity and access → Users (the home page also offers Invite friends).
2. Add verified teammate email addresses if the account permits invitations. Each member signs in and confirms the same workspace hostname and workspace ID.
3. Add contributors to the `airbnb_team` workspace-local group for notebook organization. Workspace-local groups cannot receive Unity Catalog privileges; grant data privileges to individual teammate identities or an available account-level group. Grant access to the project folder through Share. For raw reading, grant `USE CATALOG` on `workspace`, `USE SCHEMA` on `workspace.airbnb_eda`, and `READ VOLUME` on `raw`. Grant `WRITE VOLUME` and `READ VOLUME` on `artifacts` to contributors who run the report. Grant only the permissions required by each role.
4. For ETL/model contributors, grant `USE SCHEMA` and `CREATE TABLE` on the reserved schemas; grant `SELECT` and `MODIFY` on the relevant schema/table scope, and `CREATE VOLUME` or `CREATE MODEL` only where required. Dashboard/Genie readers need `SELECT` on Gold outputs. No teammate-specific grants have been made because teammate identities are pending.
5. Each member opens the notebook and confirms they can read the manifest and write an aggregate artifact. An invitation alone does not prove access.

If invitations or common workspace access are unavailable, each member uses a separate Free Edition workspace. Import the same notebooks and manifest, create the same schemas/volumes under an available catalog, and upload only London/Bristol files with identical checksums. Parameterize paths rather than embedding personal workspace locations. Share code through GitHub; agree which workspace hosts the integrated dashboard and Genie. Never assume catalog objects are shared across workspaces.

## GitHub CLI workflow

GitHub integration inside Databricks is optional and is not configured. Use local Git and `gh` for branches, reviews and repository administration. Import/export `.ipynb` files between the local checkout and shared workspace as documented in [collaboration.md](collaboration.md). No browser GitHub sign-in is required for this workflow.

```bash
gh repo clone DanyloKuryliak/airbnb-price-analytics
cd airbnb-price-analytics
git switch etl/pipeline
```

Each contributor uses the branch assigned to their role. Clear notebook outputs before committing. Do not overwrite a shared notebook until checking for newer teammate edits.

## Raw input layout

```text
/Volumes/workspace/airbnb_eda/raw/
├── sources.json
└── data/raw/
    ├── london/2026-09-17/listings.csv.gz
    └── bristol/2026-09-22/listings.csv.gz
```

Local acquisition uses `scripts/download_sources.py`. It verifies current A/B publication dates and pinned checksums and refuses to overwrite existing raw files. Use Catalog Explorer → volume → Upload, preserving the layout above. Internet access from Free Edition is restricted, so local download plus volume upload avoids assuming Inside Airbnb is reachable from compute.

Equivalent upload commands, after creating the schema and managed volumes in Catalog Explorer:

```bash
databricks fs mkdir dbfs:/Volumes/workspace/airbnb_eda/raw/data/raw/london/2026-09-17 -p ucu
databricks fs mkdir dbfs:/Volumes/workspace/airbnb_eda/raw/data/raw/bristol/2026-09-22 -p ucu
databricks fs cp sources.json dbfs:/Volumes/workspace/airbnb_eda/raw/sources.json -p ucu
databricks fs cp data/raw/london/2026-09-17/listings.csv.gz dbfs:/Volumes/workspace/airbnb_eda/raw/data/raw/london/2026-09-17/listings.csv.gz -p ucu
databricks fs cp data/raw/bristol/2026-09-22/listings.csv.gz dbfs:/Volumes/workspace/airbnb_eda/raw/data/raw/bristol/2026-09-22/listings.csv.gz -p ucu
```

These commands intentionally omit overwrite. Existing files require checksum verification rather than replacement. Keep dataset records out of GitHub.

## Notebook execution

Open the imported notebook, select Serverless compute, and set widgets:

| Widget | Value |
| --- | --- |
| `input_root` | `/Volumes/workspace/airbnb_eda/raw` |
| `output_root` | `/Volumes/workspace/airbnb_eda/artifacts` |

Run all cells in order. The notebook validates both source hashes and rejects manifests outside the two permitted cities. Outputs are `eda_findings.md`, `eda_profile.md`, `eda_run.json` and two PNG figures under `artifacts/figures/`. Copy reviewed aggregate artifacts into `docs/` before publication; never export raw record previews.

pandas and matplotlib are used without notebook-scoped package installation. The reproducible one-time job specification is `databricks/eda_validation_run.json`. Submit it with `databricks jobs submit --json @databricks/eda_validation_run.json --no-wait -p ucu` and check the returned run until its terminal result is `SUCCESS`. This is EDA validation, not the production ETL job. Do not create classic clusters, paid endpoints or a paid cloud account. If quota is exhausted, wait for the free quota reset rather than upgrading.

## Documentation

- [Free Edition and serverless quotas](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).
- [Workspace folder permissions](https://docs.databricks.com/aws/en/security/auth/access-control/).
- [Unity Catalog privileges](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/).
- [Workspace-local group limitations](https://docs.databricks.com/aws/en/admin/users-groups/workspace-local-groups).
- [Files in Unity Catalog volumes](https://docs.databricks.com/aws/en/volumes/volume-files).
