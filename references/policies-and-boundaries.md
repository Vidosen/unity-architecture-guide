# Policies And Boundaries

## Table of Contents

1. Core principles
2. Layer model
3. Type roles and naming
4. Dependency rules
5. Modules, asmdef, and visibility
6. Anti-patterns

## Core Principles

### Explicit module boundaries

Each module needs:

- one primary responsibility;
- a minimal public API;
- hidden internal implementation;
- explicit entry and exit points.

### Internal by default

Use `internal` for most implementation types. Make a type `public` only when it is:

- official module API;
- a cross-module contract;
- a Unity-facing class that must be visible outside the assembly;
- a DTO or contract that crosses module boundaries.

### Dependencies point inward

The default direction is:

`Presentation -> Application -> Domain`

Infrastructure sits outside the core and implements contracts required by inner layers.

Domain must not depend on Unity UI, scenes, SDKs, network stacks, storage, analytics, IAP, or other external details.

### One term, one role

Do not hide architecture behind vague names like `Manager`, `Handler`, `Processor`, or `Logic` unless the role is truly that narrow.

Prefer precise names such as:

- `View`
- `Presenter`
- `UseCase`
- `Query`
- `Repository`
- `Factory`
- `StateMachine`
- `Bootstrapper`
- `Adapter`

## Layer Model

### Presentation

Own Unity runtime interaction, UI rendering, and input boundaries.

Typical types:

- `View`
- `Presenter`
- `ViewModel` for selectively state-heavy UI
- input adapters
- screen controllers
- `MonoBehaviour` components that only render state and proxy events

Presentation should:

- accept user input;
- render state;
- react to Unity lifecycle;
- forward commands inward.

Presentation should not:

- own business rules;
- call repositories directly;
- talk to SDKs directly.

### Application

Own complete application scenarios and orchestration.

Typical types:

- `UseCase`
- `Command`
- `Query`
- coordinators
- orchestrators
- process managers or sagas for long-running flows
- state orchestration for multi-step workflows

Application should:

- coordinate dependencies;
- define transaction or scenario boundaries;
- return results;
- stay independent from concrete UI.

### Domain

Own business meaning, invariants, and core behavior.

Typical types:

- `Entity`
- `ValueObject`
- `DomainService`
- aggregates
- domain rules

Domain should not know about Unity runtime types, SDK APIs, or transport details.

### Infrastructure

Own external integrations and implementations of inner contracts.

Typical types:

- repository implementations;
- network gateways;
- Firebase or analytics adapters;
- save or load implementations;
- IAP wrappers;
- Netcode wrappers.

Infrastructure should not become a second domain layer.

## Type Roles And Naming

### Presentation-side roles

- `View`: render state, expose user events, hold scene references.
- `Presenter`: subscribe to view events, call `UseCase` or `Query`, map results to `ViewState`.

### Application-side roles

- `UseCase`: one complete scenario with input, orchestration, and result.
- `Query`: read data for presentation without inventing meaningless getter services.
- `Repository`: contract for data access needed by application or domain.
- `Factory`: use only when creation has meaningful complexity or variation.
- `StateMachine`: use when a process has explicit stages.
- `Handler`: use only for narrow event or message handling.

### Domain-side roles

- `Entity`: identity plus behavior and invariants.
- `ValueObject`: immutable value without identity.
- `DomainService`: domain logic that does not belong to a single entity.

### Infrastructure-side roles

- `Adapter`: wrapper around SDK or external API.
- `Installer`: DI composition root for bindings.
- `Bootstrapper`: startup and wiring for a module or scene.
- `Config`: data-only configuration, often `ScriptableObject`.
- `Registry`: serialized catalog or lookup of definitions.

## Dependency Rules

Allowed:

- `Presentation -> Application`
- `Application -> Domain`
- `Infrastructure -> Application/Domain contracts`
- `Composition Root -> all layers`

Forbidden:

- `Domain -> Presentation`
- `Domain -> Infrastructure SDK`
- `View -> Repository`
- `View -> SDK wrapper`
- `Presenter -> concrete Firebase/IAP/Netcode implementation`

If an external service is needed, depend on an interface, not on the SDK implementation.

## Modules, Asmdef, And Visibility

Each module should usually have:

- its own asmdef;
- a narrow API;
- internal implementation;
- its own tests;
- its own installer or bootstrap entry point if needed.

Asmdef policy:

- depend only on other modules' API or contract assemblies;
- keep `Domain` and `Application` independent from other modules' `Infrastructure`;
- move truly shared DTOs or value objects into `SharedKernel` or `Contracts`;
- forbid cyclic asmdef references.

When a cycle appears, prefer one of:

1. extract a dedicated contracts assembly;
2. move shared types into `SharedKernel`;
3. replace direct dependency with an application boundary event or command.

Visibility defaults:

- interfaces: `public` only for real cross-module contracts;
- presenters, use cases, queries, factories, configs: usually `internal`;
- entities and value objects: usually `internal` unless they are part of module API;
- installers: `public` only when they must be called from outside the module.

## Anti-Patterns

- generic `Rule` types instead of precise roles;
- `GetXService` or `SetXService` around every model property;
- `GameManager`, `UiManager`, `DataManager`, or `LogicManager` without a narrow responsibility;
- ScriptableObject used as the default business model;
- hidden side effects from arbitrary services;
- domain types depending on `MonoBehaviour`, `Transform`, `Animator`, `NetworkManager.Singleton`, Firebase SDK, or `PlayerPrefs`.
