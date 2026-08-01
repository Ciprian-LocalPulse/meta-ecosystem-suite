# Architecture

MetaEcosystemSuite is organized as four independent modules that share a
single configuration layer (`config.py`) and are exposed through one
CLI entrypoint (`cli.py`). Each module can be imported and used as a
standalone library without pulling in the others.

## Design principles

- **Data-driven rules over hard-coded logic.** The policy linter's rule
  set (`policy_linter/rules.py`) is plain data, not branching logic —
  new checks can be added without touching the engine.
- **Async-first for I/O.** Anything that talks to the network (Graph
  API client, Ad Library extractor, Status Sentinel probes) is async,
  so batch operations and concurrent health checks don't block on
  each other.
- **Fail soft on malformed data.** The DSA transformer skips malformed
  records instead of aborting a whole batch — useful when pulling
  thousands of ad records from a live, occasionally inconsistent API.
- **Schema validation via Pydantic.** Both the app configuration and
  the DSA ad-record schema are Pydantic models, giving you validation
  errors at the boundary instead of silent type coercion bugs deeper
  in the pipeline.

## Module map

```
                         ┌─────────────┐
                         │   cli.py    │  Typer entrypoint (meta-suite)
                         └──────┬──────┘
           ┌───────────────────┼───────────────────┬─────────────────┐
           ▼                   ▼                   ▼                 ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  ┌───────────────┐
   │  dsa_auditor   │   │ metrics_      │   │ policy_linter │  │ status_       │
   │                │   │ migrator      │   │               │  │ sentinel      │
   ├───────────────┤   ├───────────────┤   ├───────────────┤  ├───────────────┤
   │ extractor.py   │   │ graph_client  │   │ rules.py      │  │ monitors.py   │
   │ transformer.py │   │ normalizer.py │   │ nlp_checker.py│  │ sentinel.py   │
   │ schema.py      │   │ mappings.py   │   │ linter.py     │  │ notifier.py   │
   │ reporter.py    │   └───────────────┘   └───────────────┘  └───────────────┘
   └───────────────┘
           │
           ▼
   config.py (Pydantic Settings, shared by all modules)
```

## Data flow: DSA Auditor

1. `AdLibraryExtractor` paginates through the Meta Ad Library API for a
   given search term, handling Meta's cursor-based pagination.
2. `DSATransformer` maps each raw record onto a `DSAAdRecord` model,
   parsing Meta's range-obfuscated impressions/spend fields and
   discarding anything that fails validation.
3. `DSAReporter` aggregates the validated records into a JSON report,
   flagging any AI-generated ads missing a disclosure label.

## Data flow: Metrics Migrator

`GraphAPIClient` pulls raw insights for an ad object; `MetricsNormalizer`
maps legacy fields (`impressions`, `reach`) onto the unified schema
(`total_views`, `unique_viewers`, `view_frequency`) using the table in
`mappings.py`, which is also exposed publicly so downstream code can
build its own field-name translations.

## Data flow: Status Sentinel

`monitors.py` defines a registry of named HTTP probes. `sentinel.py`
runs them concurrently with `asyncio.gather`, and `notifier.py` posts a
formatted Slack message only when at least one probe is not `HEALTHY`.
