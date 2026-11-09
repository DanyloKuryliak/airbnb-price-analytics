# Team collaboration

## Source of truth

Repository: https://github.com/DanyloKuryliak/airbnb-price-analytics. The repository covers all four roles: EDA, medallion ETL, price modelling, dashboard/Genie and final reporting. GitHub and Databricks have independent responsibilities: GitHub versions code and reviews; the shared Databricks workspace runs notebooks and stores governed data. A Databricks Git connection is optional.

## Branch ownership

| Branch | Owner and scope |
| --- | --- |
| `main` | Shared scaffold and reviewed integration |
| `eda/london-bristol` | Person 1: EDA, data quality and leakage review |
| `etl/pipeline` | Person 2: architecture and parameterized ETL |
| `ml/price-model` | Person 3: training-only baseline, model and evaluation |
| `bi/dashboard-genie` | Person 4: dashboard and Genie Agent |

The initial scaffold is published on `main`. Person 1's implemented EDA was integrated through [pull request #4](https://github.com/DanyloKuryliak/airbnb-price-analytics/pull/4) and is available on `main`. The other feature branches start from the common scaffold; their notebooks are explicitly unimplemented role entry points.

## Daily workflow

```bash
git switch main
git pull --ff-only
git switch etl/pipeline
# Edit the assigned component and run its validation.
git add <changed-files>
git commit -m "Describe the implemented change"
git push -u origin etl/pipeline
gh pr create --base main --head etl/pipeline
```

Use the branch assigned to the role. Obtain a teammate review before merging. Agree changes to table contracts with affected owners. Never reset or overwrite another contributor's branch. Enforce protection where the free account supports it; otherwise follow the same review convention without upgrading.

## Notebook transfer without Git integration

Edit locally or in the shared Databricks project folder. Before editing a shared notebook, agree ownership with the team; concurrent edits affect the same object. For independent experiments, create a personal working copy.

Import new local notebooks with `databricks workspace import ... --format JUPYTER --file ... -p ucu`. Export a workspace notebook with `databricks workspace export ... --format JUPYTER --file ... -p ucu`. Review exported content, clear outputs and remove raw record previews before committing. Import reviewed changes back into the agreed shared notebook only after checking for newer teammate edits. Overwrite is an explicit update operation, not the default.

## Team access

The repository owner invites verified GitHub usernames using `gh api repos/DanyloKuryliak/airbnb-price-analytics/collaborators/USERNAME --method PUT -f permission=push`; recipients accept invitations. No usernames have been supplied, so invitations are pending. Confirm each member can clone and push the assigned branch. Provide evaluator access before submitting a private repository.

The Databricks administrator adds teammates to the existing workspace, then grants notebook and Unity Catalog access separately. The `airbnb_team` workspace-local group organizes notebook access; it cannot grant Unity Catalog privileges. Use individual data grants for the small team unless an account-level group is available. See `setup_databricks.md`.

## Region and final submission

The team admin confirms availability and registers Team Вишня, United Kingdom, London/Bristol and Greater Manchester in the course Teams thread. Proposed third-city rationale: a distinct metropolitan market tests geographic transfer. The repository is the final submission entry point; attach dashboard/Genie URLs, model metrics, transfer evidence and presentation PDF or link as those deliverables are completed.
