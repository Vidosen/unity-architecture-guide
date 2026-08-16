---
name: unity-architecture-guide
description: Right-size Unity architecture by evolving code only in response to observed complexity. Use when designing, reviewing, refactoring, or documenting Unity codebases; deciding whether to keep a feature direct or introduce module boundaries, layers, asmdefs, MVP or MVVM, DI, repositories, state machines, Rx or R3, ECS or jobs, network boundaries, lifecycle ownership, visibility rules, or tests. Prefer present feature pressure over speculative extensibility and allow no-change recommendations.
---

# Unity Architecture Guide

## Core Rule

Make every architectural cost earn its place. Start with the smallest coherent implementation that satisfies current behavior. Add a layer, interface, assembly, pattern, or indirection only when it resolves an observed problem.

Treat architecture as a continuum, not a sequence of mandatory stages. Do not create maturity enums, scores, phase objects, empty folders, or future-facing extension points to represent possible growth. The mature shapes in the references are destinations that a subsystem may approach selectively; they are not starting templates.

## Workflow

1. Inspect the current feature or code before selecting a pattern.
2. Identify concrete pressure: conflicting responsibilities, real reuse, multiple implementations or consumers, unstable external integration, non-trivial state or lifetime ownership, valuable isolated tests, measured performance limits, or authority constraints.
3. If no material pressure exists, recommend keeping the current direct design.
4. Choose the smallest extraction that removes the current pain. Prefer a method or focused collaborator before a new layer or framework.
5. State the runtime, cognitive, testing, and maintenance cost introduced by the recommendation.
6. Name future signals that could justify the next extraction, but do not scaffold for them now.

## Evidence Rules

Do not treat these as sufficient reasons to add architecture:

- a future variant might exist;
- a class might grow later;
- a pattern is considered best practice;
- an interface would make mocking convenient;
- a folder layout looks cleaner;
- a line-count threshold was crossed.

Treat them as clues only. Require a present behavior, ownership, change, integration, performance, or collaboration problem before restructuring code.

Allow a cohesive local `MonoBehaviour` to receive input, coordinate a small workflow, hold local state, and render output. Split it when those concerns begin changing independently or create real lifecycle, reuse, testing, or ownership friction.

## Choose the Right Reference File

- Read `references/policies-and-boundaries.md` for proportional boundaries, optional layering vocabulary, interfaces, modules, asmdefs, visibility, and naming.
- Read `references/runtime-patterns.md` for async, events, Rx or R3, gameplay runtime, physics, ECS, jobs, and network integration.
- Read `references/reference-architectures.md` for examples that grow from direct implementations toward selectively mature shapes.
- Read `references/engineering-practice.md` for proportional testing, lifecycle and DI ownership, error handling, and review checks.

## Output Contract

Produce a recommendation grounded in current evidence:

- describe the current shape and the pressure that actually exists;
- say explicitly when no architectural change is justified;
- list the smallest changes worth doing now;
- list tempting abstractions that should stay out for now;
- give observable triggers for reconsidering them later;
- include testing implications proportional to behavior risk.

Discuss presentation, application, domain, and infrastructure only when those distinctions solve the problem at hand. Do not force every feature into all four roles.

## Review Mode

When reviewing an existing Unity design or code slice:

1. Identify the real source of truth, state owner, entry points, exits, and lifetime.
2. Find current defects and change friction before proposing patterns.
3. Check both directions: responsibilities that are dangerously mixed and abstractions that have no current job.
4. Preserve direct code when it remains cohesive and locally understandable.
5. Require a present reason for every proposed interface, DTO, use case, presenter, repository, installer, assembly, or state object.
6. End with the smallest risk-ordered refactor plan, including a valid no-refactor outcome.

## Dynamic Search Helper

If the request spans several topics or the right section is not obvious, run this from the skill directory:

```bash
python scripts/find_guidance.py "query text"
```

The helper ranks bundled guidance for English or common Russian architecture queries and prints contextual section headings with short excerpts.
