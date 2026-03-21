SOPHY support files

- `.sophy/recollection-export/recollection-export.sh` — script that generates hourly recollection markdown files and pushes them to a branch.
- `.sophy/scenarios/` — scenario YAML files for roleplay/testing.
- `.sophy/recollections/` — generated recollection files (kept in branches via workflow PRs).

**Notes and gotchas**
- The workflow uses `actions/checkout@v4` and `peter-evans/create-pull-request@v5` to generate PRs for each recollection.
- The GitHub runner will need `GITHUB_TOKEN` (provided automatically) to create branches and PRs. If you require a personal access token with broader scopes, add it to repository secrets as `PERSONAL_ACCESS_TOKEN` and update the workflow.
- Scheduler restrictions: GitHub Actions scheduled workflows run in UTC; cron granularity is 5 minutes minimum but many workflows prefer top-of-hour triggers.
