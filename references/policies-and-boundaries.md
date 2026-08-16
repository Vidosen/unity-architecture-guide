# Policies And Boundaries

## Table of Contents

1. Proportional architecture
2. Pressure before pattern
3. Direct implementations
4. Layers as optional vocabulary
5. Contracts and adapters
6. Modules, asmdefs, composition, and visibility
7. Naming and review risks

## Proportional Architecture

Let code structure grow with real feature behavior. A small feature may remain one component or a few directly connected types. A mature subsystem may eventually need explicit layers, contracts, assemblies, adapters, and composition roots. Both shapes are valid when their cost matches their current job.

Keep architecture on a continuum. Do not label code with maturity stages or require a subsystem to pass through a fixed sequence. Adopt techniques independently as their pressures appear.

Use these defaults:

- keep behavior together while it changes for the same reason;
- prefer direct calls and concrete dependencies while ownership is local and obvious;
- extract the smallest useful boundary when change reasons diverge;
- tolerate small duplication until a stable shared concept is visible;
- preserve an existing simple design when a rewrite would only improve theoretical extensibility.

## Pressure Before Pattern

Match observed pressure to the least expensive response.

| Observed pressure | Smallest response to try first |
| --- | --- |
| One method is hard to read | Extract a named method or value, not a service layer |
| A component has independent change reasons | Extract one focused collaborator |
| Important rules are difficult to verify | Move those rules into a plain C# type |
| Two real callers repeat one scenario | Extract one shared operation or use case |
| A second implementation exists | Introduce a contract at that substitution boundary |
| An SDK is volatile or spread across callers | Localize it behind one adapter |
| State transitions have invalid paths or complex entry and exit work | Introduce an explicit state machine |
| Object construction and lifetimes are difficult to follow | Centralize composition; add a DI container only if manual wiring remains costly |
| Assembly dependencies are unclear or cyclic | Introduce an asmdef or contract assembly at the proven boundary |
| Runtime cost is measured in a hot path | Optimize locally; introduce jobs or ECS only where measurements support it |
| Multiplayer intent and authority diverge | Separate authority decisions from transport callbacks |

Do not infer pressure from a hypothetical second implementation, possible reuse, folder aesthetics, or generic best practice. Line count may prompt inspection, but it does not prove that a type has more than one responsibility.

## Direct Implementations

Allow a cohesive local feature to use direct Unity code.

A `MonoBehaviour` may reasonably:

- hold serialized scene references;
- receive a small set of Unity callbacks or user events;
- coordinate a local operation;
- own state with the same GameObject or scene lifetime;
- update its own presentation.

Keep this shape while the behavior remains easy to locate, change, and verify at its actual risk level. Do not split a component merely because input, orchestration, state, and rendering can be named separately in theory.

Extract from it when there is evidence such as:

- rules reused outside the component;
- several views sharing one workflow;
- state surviving the component lifetime;
- async work requiring a different cancellation owner;
- external APIs spreading through unrelated methods;
- repeated regressions in branching or invariants;
- independent teams or assemblies changing the same surface.

Unity and SDK types are not automatically leaks. They become architectural problems when they cross a boundary that needs independent evolution, portability, reuse, testing, or authority.

## Layers As Optional Vocabulary

Use presentation, application, domain, and infrastructure as names for responsibilities that already need separation. Do not require each feature to contain all four.

### Presentation

Use a distinct presentation role when rendering and user interaction change independently from the underlying workflow. Typical types include `View`, `Presenter`, and selectively `ViewModel`.

A tiny screen may keep rendering and orchestration in one `MonoBehaviour`. Introduce a presenter when view state, loading, error mapping, multiple views, or workflow coordination makes that component difficult to own.

### Application

Use a distinct application role for a complete scenario that coordinates several dependencies, is reused by multiple entry points, or needs a stable result independent from one concrete UI.

Do not wrap each button click or model method in a `UseCase`. A direct method call is preferable when the scenario is local and trivial.

### Domain

Use a distinct domain role when business or gameplay invariants deserve an explicit model independent from Unity runtime details. Typical types include entities, value objects, and focused domain services.

Do not manufacture a domain layer from passive property bags. Keep simple local state near its owner until meaningful rules, reuse, or invariants emerge.

### Infrastructure

Use a distinct infrastructure role when storage, network, analytics, IAP, platform, or SDK behavior must be isolated from code that should evolve independently.

One localized SDK call does not require a full infrastructure folder. Introduce an adapter when the dependency is volatile, repeated, replaceable, or harmful to the caller's ownership.

### Mature Dependency Direction

When these roles exist as real boundaries, prefer:

`Presentation -> Application -> Domain`

Let infrastructure implement contracts owned by the code that needs them. Keep the composition root outside the inner behavior.

Apply this direction only across boundaries that have earned separation. Do not create placeholder layers to complete the diagram.

## Contracts And Adapters

Introduce an interface when at least one present need justifies substitution or isolation:

- two implementations exist now;
- an external dependency changes independently and has meaningful behavior to isolate;
- multiple consumers require a stable cross-module API;
- a high-value behavior needs a controllable boundary for deterministic tests.

Do not create one interface per class, mirror every concrete type with an `I` type, or add a contract solely because a DI container accepts one. Testing convenience can support a boundary decision, but a preferred mocking style is not enough by itself.

Introduce other boundary types only for a current job:

- `DTO`: stabilize or translate data across a real boundary;
- `Repository`: express meaningful persistence semantics, alternate storage, caching, or offline behavior;
- `Adapter`: contain an SDK, transport, platform, or Unity runtime surface that would otherwise spread;
- `Factory`: own genuinely variable or non-trivial creation;
- `Query`: build a read model used by more than a trivial local getter;
- `Result`: represent expected failures that callers must distinguish and handle.

Avoid copying identical fields through several DTOs when no boundary is independently changing.

## Modules, Asmdefs, Composition, And Visibility

Start with folders and direct references. Introduce a module boundary when ownership, reuse, packaging, dependency control, compilation, or collaboration requires one.

Add an asmdef when it provides a present benefit such as:

- enforcing a dependency boundary;
- packaging or reusing a subsystem independently;
- isolating tests or platform-specific code;
- reducing meaningful compilation scope;
- breaking an observed assembly cycle through a stable contract.

Do not create an assembly for every feature. Do not extract `SharedKernel` or `Contracts` as a dumping ground; move only stable concepts with real cross-module ownership.

Prefer manual composition through serialized references or constructors while the object graph and lifetimes remain obvious. Add an installer, bootstrapper, or DI container when several objects share non-trivial project, scene, session, or match scopes and manual wiring has become error-prone.

Choose visibility at the assembly boundary that actually exists:

- keep implementation types `internal` when callers are in the same assembly;
- make a type `public` only for a real cross-assembly API, Unity requirement, or serialized contract;
- do not create an asmdef merely to make internal visibility meaningful.

When a cycle appears, first question the ownership and direction of the dependency. Extract a contract or shared value only when it represents a stable concept, not simply to silence the cycle.

## Naming And Review Risks

Name a type after the job it performs now. Use `View`, `Presenter`, `UseCase`, `Repository`, `StateMachine`, `Adapter`, `Installer`, or `Bootstrapper` only when the corresponding responsibility exists.

Watch for under-structured code:

- unrelated input, animation, persistence, networking, and UI owned by one global object;
- hidden global mutable state;
- rules duplicated with divergent behavior;
- transport callbacks making authority decisions;
- several owners mutating the same source of truth;
- lifecycle and cancellation without an identifiable owner.

Watch equally for speculative structure:

- one implementation behind a one-to-one interface without an external boundary;
- `UseCase` classes that only forward one call;
- repositories that merely rename `PlayerPrefs` operations;
- DTO chains that copy the same shape without translation;
- empty layer folders and assemblies created from a template;
- DI installers for an otherwise obvious two-object graph;
- state objects for a flow with no meaningful transition behavior;
- shared abstractions built before duplicated behavior has stabilized.
