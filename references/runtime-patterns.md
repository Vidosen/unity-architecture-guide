# Runtime Patterns

## Table of Contents

1. Async and cancellation
2. Events, Rx, and R3
3. Gameplay runtime boundaries
4. ECS and hybrid architecture
5. Physics and jobs boundaries
6. Network boundaries

## Async And Cancellation

- Use one async style consistently within a project, usually `async/await` or `UniTask`.
- Pass `CancellationToken` into long-running operations.
- Avoid uncontrolled fire-and-forget work.
- Let the `Presenter` or runtime coordinator own cancellation and disposal.
- Keep async business logic out of `View`.

Practical default:

- `UseCase` accepts `CancellationToken` if it can outlive a frame.
- `Presenter` owns the lifetime token.
- `View` only forwards user intent and renders result.

## Events, Rx, And R3

Both plain C# events and Rx or R3 are valid. Choose based on problem shape, not fashion.

Prefer simple events for:

- basic UI callbacks;
- local notifications;
- small modules with obvious ownership.

Prefer Rx or R3 for:

- state-heavy UI;
- derived state;
- complex async or event pipelines;
- stream composition involving timers, input, and external state.

Rules for Rx or R3:

- subscription ownership must be explicit;
- lifecycle and disposal must be explicit;
- avoid hiding core scenario logic inside long operator chains;
- do not force reactive types into domain or broad application contracts without a strong reason.

Use one dominant approach per module or bounded context. Mixing `event` and `R3` inside one module should be a conscious exception.

## Gameplay Runtime Boundaries

Split gameplay into three concerns that Unity code often mixes together:

- runtime adapters at the Unity boundary;
- application orchestration;
- domain rules and state.

### Runtime adapters

Own:

- `MonoBehaviour` lifecycle;
- input readers;
- animation and VFX drivers;
- collision or trigger callbacks;
- scene object references;
- network object views.

Do not place business rules here.

### Gameplay application

Use:

- `UseCase` for discrete actions;
- `StateMachine` for phased flows;
- systems for recurring or tick-based orchestration;
- coordinators when several subsystems must move together.

### Gameplay domain

Own:

- health;
- stamina;
- cooldowns;
- score rules;
- damage rules;
- action validity;
- state invariants.

### Practical composition rules

- keep `MonoBehaviour` at the edge of the system;
- give important state one explicit owner;
- per-frame logic does not justify mixing layers;
- end Unity-specific dependencies at the adapter boundary;
- do not default to global singleton services for module communication.

## ECS And Hybrid Architecture

Hybrid architecture is valid when boundaries are clear:

- UI and screen flow can use presentation plus application;
- gameplay runtime can use OO patterns;
- high-scale subsystems can use ECS or jobs;
- integrations stay in infrastructure.

Use ECS when:

- there are many similar entities;
- the subsystem benefits from data-oriented execution;
- Burst or jobs materially matter;
- the task scales poorly in classic `MonoBehaviour` form.

Do not use ECS just for future-proofing.

### Position ECS correctly

ECS is an execution model, not a replacement for domain or application. Treat it as:

- a specialized simulation core;
- an execution engine for part of gameplay;
- an internal runtime subsystem.

The outside world should talk to an ECS module through narrow contracts, not through `EntityManager`, `SystemAPI`, `EntityCommandBuffer`, concrete systems, or component layouts.

### Ownership and synchronization

Define explicitly:

- who owns source of truth;
- who may mutate it;
- where synchronization happens between OO runtime and ECS;
- what data is authoritative versus derived cache.

Two valid models:

1. Source of truth outside ECS: ECS computes results from snapshots and returns DTO results.
2. Source of truth inside ECS module: the rest of the project uses only the module API.

## Physics And Jobs Boundaries

Domain may know:

- physical meaning of data;
- movement parameters;
- gameplay constraints;
- calculation results.

Domain must not know:

- `Rigidbody`
- `Collider`
- `Transform`
- `RaycastHit`
- `EntityManager`
- `JobHandle`
- memory container lifetime details

Keep Unity runtime references at runtime boundaries such as:

- hitbox or hurtbox adapters;
- physics listeners;
- mapping layers like `Collider -> ProjectEntityId`;
- adapters that gather physics facts.

Convert them to clean project-level data such as:

- `HitContext`
- `GroundContactInfo`
- `MovementIntent`
- `MotorCommand`
- `TargetScanRequest`
- `TrackingCandidate`

Jobs and Burst are execution details. Do not leak `NativeArray`, `JobHandle`, or ECS component access types into architectural contracts.

## Network Boundaries

Separate these concerns explicitly:

- domain intent;
- runtime representation;
- authority;
- transport and replication details.

Recommended roles:

- `Bootstrapper` to register network callbacks;
- `Handler` for specific network events;
- `UseCase` for gameplay scenario logic;
- adapter or wrapper around Netcode, Photon, FishNet, or another SDK.

Rules:

- do not let `NetworkManager.Singleton` spread everywhere;
- do not let transport callbacks mutate UI or domain state directly;
- keep authority checks explicit;
- keep network SDK references inside infrastructure or runtime adapter boundaries.
