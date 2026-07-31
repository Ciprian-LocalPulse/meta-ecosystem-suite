# System Architecture Blueprint

This document outlines the architectural design of the MetaEcosystemSuite, detailing its components, their interactions, and the underlying technologies.

## Overview

The MetaEcosystemSuite is a unified Python repository comprising four main modules, each addressing a specific aspect of Meta's ecosystem: DSA Compliance, Metrics Normalization, Ad Policy Linting, and API Monitoring. The suite is designed for modularity, scalability, and ease of deployment.

## Core Components

### 1. DSA Compliance Auditor

- **Purpose:** Extracts data from Meta Ad Library API and transforms it into a format compliant with EU Digital Services Act (DSA) transparency requirements.
- **Key Sub-components:**
    - `extractor.py`: Handles API calls to Meta Ad Library.
    - `transformer.py`: Maps raw API data to the EU DSA database schema.
    - `schema.py`: Defines Pydantic models for DSA database schema validation.
    - `reporter.py`: Generates JSON/PDF reports for DSA compliance.

### 2. Metrics Migrator

- **Purpose:** Normalizes legacy Meta advertising metrics (e.g., Reach, Impressions) into the unified Meta reporting model (e.g., Views, Viewers).
- **Key Sub-components:**
    - `graph_client.py`: Wrapper for Meta Graph API v19.0+.
    - `normalizer.py`: Engine for converting and calculating new metrics.
    - `mappings.py`: Dictionary defining field mappings between old and new metrics.

### 3. Ad Policy Linter

- **Purpose:** Provides pre-launch validation for advertisements against Meta's ad policies and AI guidelines.
- **Key Sub-components:**
    - `rules.py`: Defines various Meta policy rules (e.g., Policy 4.3).
    - `nlp_checker.py`: Utilizes NLP and regex for text compliance checks.
    - `linter.py`: Main engine for ad audit and policy enforcement.

### 4. Status Sentinel

- **Purpose:** Monitors Meta API latency and endpoint status in real-time, dispatching alerts for outages or degradations.
- **Key Sub-components:**
    - `monitors.py`: Contains logic for latency and status checks.
    - `sentinel.py`: Asynchronous health monitoring engine.
    - `notifier.py`: Handles dispatching alerts via Slack or email.

## Technology Stack

- **Language:** Python 3.11+
- **Dependency Management:** Poetry / Hatch (pyproject.toml)
- **CLI Framework:** Typer / Rich
- **Configuration Management:** Pydantic BaseSettings
- **HTTP Client:** httpx (async)
- **Data Processing:** Polars
- **Templating:** Jinja2
- **Scheduler:** APScheduler
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions

## Data Flow and Interactions

(Diagram or detailed flow description would go here, illustrating how data moves between modules and external Meta APIs.)

## Deployment

The suite is designed for containerized deployment using Docker, ensuring consistent environments across development, testing, and production. GitHub Actions facilitate automated testing, linting, and publishing to PyPI.
