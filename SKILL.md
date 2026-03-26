---
name: unity-architecture-guide
description: Unity architecture guidance for designing, refactoring, reviewing, and documenting Unity codebases. Use when Codex needs to choose or enforce module boundaries, presentation/application/domain/infrastructure layering, asmdef dependency rules, public vs internal visibility, MVP or MVVM UI structure, gameplay runtime composition, ECS or hybrid subsystem boundaries, network authority boundaries, Rx or R3 discipline, lifecycle or DI ownership, testing strategy, or code review heuristics for Unity projects.
---

# Unity Architecture Guide

## Overview

Use this skill to turn vague Unity architecture requests into concrete module boundaries, type roles, dependency directions, and reviewable rules. Keep the result pragmatic: choose the smallest architecture that preserves clarity, testability, and change safety.

## Core Workflow

1. Classify the request before giving advice.
2. Load only the minimum reference files needed for that class of problem.
3. Answer with concrete structure: layers, entry points, contracts, type names, folder layout, and review risks.
4. Prefer explicit ownership and explicit boundaries over generic abstractions.

## Choose the Right Reference File

- Read `references/policies-and-boundaries.md` for layer responsibilities, dependency direction, naming rules, visibility, module boundaries, asmdef policy, and anti-patterns.
- Read `references/runtime-patterns.md` for async, events, Rx or R3, gameplay runtime, ECS, hybrid modules, physics boundaries, jobs, and network integration.
- Read `references/reference-architectures.md` when the user needs a starting shape, recommended folder layout, or a reference module design.
- Read `references/engineering-practice.md` for testing strategy, lifecycle or DI ownership, Result vs exceptions, and code review checklists.

## Architecture Selection Heuristics

- UI screen or admin panel: default to MVP with Passive View. Use MVVM only when the UI is genuinely state-heavy.
- Gameplay runtime: keep `MonoBehaviour` at the runtime boundary; put orchestration in application; put rules and invariants in domain.
- Phase-based process: prefer a `StateMachine` over scattered booleans and callback chains.
- Large-scale or high-frequency subsystem: isolate ECS or jobs behind a narrow project-level API.
- Networked logic: separate gameplay intent, authority rules, runtime representation, and transport adapters.
- Unknown or messy legacy code: start from explicit entry points, source of truth, and forbidden dependencies; only then choose patterns.

## Output Contract

When using this skill, produce a concrete recommendation instead of abstract theory:

- identify the module or subsystem type;
- assign responsibilities to presentation, application, domain, and infrastructure;
- state allowed and forbidden dependency directions;
- suggest better type names if the current names are vague;
- call out required contracts, adapters, and composition roots;
- recommend visibility (`internal` vs `public`);
- include testing and review implications.

## Review Mode

When reviewing an existing Unity design or code slice:

1. Identify the real source of truth and ownership of state.
2. Trace entry points and exits across layers.
3. Check whether Unity, SDK, or transport details leaked inward.
4. Check whether orchestration lives in the right place.
5. Flag god objects, generic managers, accidental singletons, hidden side effects, and over-generalized interfaces.
6. End with a small refactor plan ordered by highest architectural risk.

## Dynamic Search Helper

If the request spans several topics or the right section is not obvious, run:

```bash
python scripts/find_guidance.py "query text"
```

The helper ranks relevant sections from the bundled references and prints file names, headings, and short excerpts.

## Pragmatic Defaults

- Prefer one clear pattern per module instead of mixing patterns casually.
- Prefer a narrow API and hidden internals over a reusable-looking but leaky module.
- Prefer DTOs and value types at boundaries instead of Unity or ECS internals.
- Prefer explicit orchestration over event-bus magic.
- Prefer justification by load, state complexity, or lifecycle constraints instead of architecture by fashion.
