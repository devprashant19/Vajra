# Phase 1 Plan: Toolchain, monorepo, documentation skeleton, reference import

## Objectives
Create the Vajra monorepo with a verified toolchain, documentation skeleton, quality gates, and reference import records.

## Tasks
1. **Repository Layout**:
   - Create directories: `apps/web`, `apps/api`, `services/*`, `packages/vajra-core`, `packages/vajra-geo`, `packages/vajra-types`, `ml/`, `infra/`, `data/raw`, `data/catalog`, `data/events`, `data/lake`, `data/derived`, `docs/adr`, `docs/data`, `docs/ops`, `docs/api`, `docs/ml`, `docs/presentation`.
   - Setup `README.md` in each component directory following the master template.
   - Setup placeholder tests for each package/service to ensure testing framework is functional.
2. **Toolchain Verification**:
   - Install `uv`.
   - Test installation of data science and geospatial libraries on Python 3.12 and 3.14.
   - Write installation results to `reports/bench/toolchain.json`.
   - Document toolchain decision in `docs/adr/ADR-001-toolchain.md`.
   - Set up `pyproject.toml` (uv workspace) and lock file.
   - Set up Node workspace (`pnpm-workspace.yaml`) for `apps/web` and `packages/vajra-types`.
3. **Developer Experience**:
   - Create `justfile` with standard tasks (setup, lint, format, typecheck, test-fast, test-all, up-lite, up-full, down, clean).
   - Add `.editorconfig`, `.env.example`, `.pre-commit-config.yaml`.
   - Implement custom tools in `tools/`: `check_readme_format.py`, `check_no_secrets.py`, `check_claims.py`.
4. **CI & Docker**:
   - Create `.github/workflows/ci.yml`.
   - Create `docker-compose.yml` with profiles `lite` and `full`.
   - Create `Dockerfile` for geo/ML services.
5. **Reference Import & Documentation**:
   - Format `data/reference/*/README.md` to match the data template.
   - Create `docs/THIRD_PARTY.md` listing reference modules and datasets.
   - Create `docs/KNOWN_REFERENCE_DEFECTS.md` listing bugs found in audit.
   - Initialize project-level docs: `README.md`, `ARCHITECTURE.md`, `PROGRESS.md`, `DECISIONS.md`, `docs/adr/ADR-002-architecture.md`.
6. **Testing**:
   - Write tests: `test_toolchain_smoke`, `test_docker_geo_image`, `test_readme_format`, `test_no_secrets`, `test_reference_untouched`, `test_compose_config`.

## Risks & Mitigations
- **Compatibility**: Geo/ML libraries (Py-ART, cfgrib) often break on newer Python versions or Windows. Mitigation: Use Docker/WSL2 explicitly for these components and pin Python 3.12 if 3.14 fails.
- **Secrets**: Accidentally committing secrets. Mitigation: Strong pre-commit hooks (`gitleaks`, `check_no_secrets.py`).

## Gate Checklist
- [ ] `just setup` and `just test-fast` pass on a clean clone.
- [ ] ADR-001 states the Python decision with evidence in `reports/bench/toolchain.json`.
- [ ] All READMEs pass the format checker; `THIRD_PARTY.md` covers every reference item.
- [ ] pre-commit passes; gitleaks reports nothing.
- [ ] `PROGRESS.md` and `reports/PHASE_1_REPORT.md` written.
