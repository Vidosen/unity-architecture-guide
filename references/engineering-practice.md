# Engineering Practice

## Table of Contents

1. Proportional testing
2. Lifecycle, composition, and DI
3. Errors and results
4. Review checklist
5. Unity-specific risk list
6. Glossary

## Proportional Testing

Choose tests from behavior risk, not from an architectural layer matrix.

Useful starting points:

| Current behavior | Proportional verification |
| --- | --- |
| Inspector wiring or simple visual response | Focused manual or PlayMode check |
| Pure calculation or invariant with meaningful branches | Plain unit tests |
| Unity lifecycle, physics, serialization, or scene interaction | PlayMode or integration test |
| External adapter with important mapping or failure behavior | Adapter integration test |
| Stable contract with multiple implementations | Shared contract tests |
| Regression in a specific path | Smallest automated test that reproduces it |

Do not extract a domain layer, interface, repository, or presenter solely to satisfy a preferred mocking style. First ask whether the behavior is risky enough to justify isolated tests and whether a smaller seam exists.

Mock or fake external time, storage, network, IAP, analytics, and transport only when controlling that dependency makes a valuable test deterministic. Do not mock passive values, domain entities, or direct collaborators whose real behavior is simpler than the mock setup.

Core logic should become scene-independent when it has meaningful invariants, reuse, or regression risk. A trivial Unity-bound feature does not need a pure core merely to claim testability.

## Lifecycle, Composition, And DI

Identify the owner before introducing lifecycle infrastructure.

Common scopes include:

- GameObject or component;
- screen;
- scene;
- session or match;
- project or application.

Create, cancel, and dispose from the owner of the relevant scope. Do not automatically cancel work because one view was destroyed if the operation belongs to a session or project service. Conversely, do not let component-owned work survive its object accidentally.

Start composition directly:

- serialized references for scene objects;
- constructors for plain C# collaborators;
- one local setup method when creation order matters.

Centralize manual composition when several objects share lifetimes or construction becomes difficult to trace. Add a DI container or installer only when it reduces demonstrated wiring, scope, configuration, or replacement complexity. Do not introduce a container for a small obvious object graph.

Avoid service location and hidden singleton access when they obscure ownership. A deliberately global project service can still be direct if its lifetime and mutation policy are explicit.

## Errors And Results

Use the smallest error representation callers need.

- return a value, boolean, or small status when there is one simple expected outcome;
- use a typed `Result` or equivalent when callers must distinguish several expected failures;
- use exceptions for exceptional failures that the current layer cannot handle locally;
- map technical failures to UI and telemetry only where that mapping is actually needed.

Do not introduce a generic project-wide `Result<TSuccess, TError>` for one operation with no meaningful recovery branches. Do not hide expected purchase, validation, authority, or connectivity outcomes inside undifferentiated exceptions when callers must react differently.

Keep error policy consistent across a real boundary, not necessarily across every module in the project.

## Review Checklist

Use this order during design or code review:

1. What current behavior or maintenance problem is being solved?
2. Is the existing direct implementation still cohesive and understandable?
3. Does each proposed type or boundary have a present job?
4. Can a method, value, or focused collaborator solve the problem before a new layer?
5. Is there one explicit source of truth and mutation owner?
6. Are lifetime, cancellation, and subscription owners correct for their real scopes?
7. Have Unity, SDK, ECS, or transport details spread beyond the code that owns them?
8. Are meaningful invariants or scenarios hidden inside difficult Unity callbacks?
9. Are interfaces backed by real substitution, isolation, consumer, or test value?
10. Are asmdefs and public APIs enforcing an actual module boundary?
11. Is reactive, DI, state-machine, jobs, or ECS complexity justified by current behavior or measurement?
12. Would no refactor be safer and cheaper right now?
13. What observable change should trigger reconsideration later?

End with the smallest risk-ordered change set. Do not prescribe the mature reference architecture when one local extraction resolves the issue.

## Unity-Specific Risk List

Inspect for under-structured code:

- a global controller owning unrelated input, damage, animation, network, persistence, and UI;
- several objects mutating the same gameplay state;
- domain-significant rules duplicated across callbacks;
- network callbacks making hidden authority decisions;
- subscriptions or async work without a lifetime owner;
- mutable `ScriptableObject` assets unintentionally acting as global runtime state.

Inspect for over-structured code:

- a presenter and use case around a single local button action;
- one-to-one interfaces without a real boundary;
- repositories that add no persistence semantics;
- state classes with no meaningful state-specific behavior;
- DTOs copying identical data through adjacent layers;
- installers and asmdefs for tiny isolated features;
- Rx pipelines replacing a direct call or one event;
- pure domain wrappers around values with no invariants;
- speculative extension points justified only by possible future requirements.

Treat names such as `Manager`, `Controller`, `Service`, or `Handler` as review prompts, not automatic defects. Rename or split them only when their current responsibilities are vague or unrelated.

## Glossary

- `View`: rendering and user events when presentation deserves separation.
- `Presenter`: screen orchestration when view state and workflows outgrow a local component.
- `UseCase`: a complete application scenario shared or complex enough to stand alone.
- `Query`: a purposeful read model or projection, not a renamed getter.
- `Entity`: a domain object with identity and meaningful behavior.
- `ValueObject`: an immutable value with rules or semantics beyond primitive storage.
- `DomainService`: domain behavior that cannot belong naturally to one entity.
- `Repository`: a persistence contract with meaningful storage semantics.
- `Adapter`: a boundary around an independently changing SDK, platform, transport, or runtime surface.
- `Factory`: variable or non-trivial object creation.
- `Config`: tunable data, often editor-owned.
- `Registry`: an intentional catalog or lookup of definitions.
- `Installer`: DI composition for a graph and scope that justify it.
- `Bootstrapper`: startup wiring when initialization is a real responsibility.
- `StateMachine`: explicit transition ownership for a behaviorally significant flow.
- `Handler`: one narrow event or message responsibility.
