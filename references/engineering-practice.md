# Engineering Practice

## Table of Contents

1. Testing strategy
2. Lifecycle and DI
3. Errors and Result pattern
4. Review checklist
5. Unity-specific smell list
6. Glossary

## Testing Strategy

Minimum expected test matrix:

- domain unit tests for invariants, value objects, and rules;
- application unit tests for use cases, branching, and orchestration;
- integration tests for adapters, repositories, and SDK wrappers;
- contract tests to ensure infrastructure implementations obey interfaces.

Mock:

- storage, network, IAP, analytics, and transport adapters;
- time through `IClock` or `ITimeProvider`.

Do not mock:

- domain entities and their invariants;
- simple DTOs or value objects without side effects.

Core rule: core logic must be testable without a scene and without `MonoBehaviour`.

## Lifecycle And DI

Recommended scopes:

- project scope for long-lived services;
- scene scope for scene composition;
- session or match scope for a concrete gameplay run.

Lifecycle ownership must be explicit:

- creation belongs to composition root;
- cancellation belongs to the presenter, state machine, or runtime coordinator that started the work;
- destruction must cancel async work and dispose subscriptions.

Practical default:

- read scene references at the boundary;
- pass clean data and contracts inward;
- avoid hidden singleton access as a lifecycle mechanism.

## Errors And Result Pattern

Project-level consistency matters.

- return expected business failures through a typed `Result` pattern;
- use exceptions for exceptional or infrastructural failures;
- make presenter or coordinator map user-facing failures separately from technical failures.

Useful default:

- `Result<TSuccess, TError>` or an equivalent discriminated union;
- typed domain or application errors;
- one mapping rule from `Error -> UI + telemetry`.

## Review Checklist

Use this list during design review or code review:

1. Does the class have one clear responsibility?
2. Are presentation, application, domain, and infrastructure roles separated cleanly?
3. Did Unity, SDK, ECS, or transport details leak inward unnecessarily?
4. Did `View` start making business decisions?
5. Did `UseCase` turn into a UI controller?
6. Did a generic `Manager` become the owner of unrelated logic?
7. Is each interface justified by a real extension point?
8. Is each `public` type actually required to be public?
9. Are entry points, exits, and lifecycle ownership explicit?
10. Can the core behavior be tested without a scene?
11. If Rx or R3 is used, is subscription lifecycle obvious?
12. Is reactive complexity justified, or did it replace simpler callbacks without benefit?
13. Are Rx types leaking into layers that do not need them?

## Unity-Specific Smell List

Strong warning signs:

- `PlayerController` or another core class growing into a 1000+ line god object;
- `GameManager` knowing everything;
- input, damage, animation, network, and UI mixed in one class;
- domain rules inside `OnTriggerEnter` or `Update`;
- `NetworkManager.Singleton` called from many unrelated locations;
- a global event bus as the default integration mechanism;
- models that are only `get/set` bags while logic is spread across services;
- `ScriptableObject` used as the default mutable business model;
- stage logic represented by unrelated booleans instead of formal states.

## Glossary

- `View`: rendering and user events.
- `Presenter`: screen orchestration.
- `UseCase`: complete application scenario.
- `Query`: read model or projection for presentation.
- `Entity`: domain object with identity.
- `ValueObject`: immutable value without identity.
- `DomainService`: domain logic not owned by one entity.
- `Repository`: contract for data access.
- `Adapter`: wrapper over SDK or external system.
- `Factory`: complex or variable object creation.
- `Config`: tunable data, often editor-owned.
- `Registry`: collection of definitions or configs.
- `Installer`: DI composition root.
- `Bootstrapper`: startup orchestration for a scene or module.
- `StateMachine`: explicit process-stage controller.
- `Handler`: narrow event or message handler.
