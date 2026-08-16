# Runtime Patterns

## Table of Contents

1. Async and cancellation
2. Direct calls, events, Rx, and R3
3. Gameplay runtime boundaries
4. Physics boundaries
5. Jobs, ECS, and hybrid execution
6. Network authority boundaries

## Async And Cancellation

Match cancellation ownership to the lifetime of the work.

A local component may start and await an operation directly when the operation exists only for that component. Cancel it on destruction or disable only if the work should truly end with that Unity lifetime.

Introduce a presenter, coordinator, or session owner when async work:

- survives a view or GameObject;
- is shared by several entry points;
- coordinates retries, navigation, or several dependencies;
- must transfer between scene, session, or match lifetimes;
- has produced stale completions or unclear cancellation behavior.

Pass `CancellationToken` across an async boundary that can outlive its caller or be intentionally interrupted. Do not add tokens to immediate synchronous operations or create a coordinator solely to hold one token.

Use `async/await` or `UniTask` consistently within the local dependency surface. Avoid uncontrolled fire-and-forget work. If fire-and-forget behavior is intentional, assign error reporting and lifetime ownership explicitly.

Do not assume destruction always cancels work. Cancel and dispose from the owner of the relevant lifetime scope, which may be a component, screen, scene, session, match, or project service.

## Direct Calls, Events, Rx, And R3

Start with a direct method call when the caller knows the callee and the relationship is local. Direct dependencies are easier to trace than a notification mechanism.

Use a plain C# event when:

- a source should not know one or more current listeners;
- the notification is local and ownership is obvious;
- subscribers can dispose or unsubscribe reliably.

Use Rx or R3 when current behavior benefits from stream composition, such as:

- several changing values forming derived state;
- timers, input, and external state combined over time;
- cancellation or switching between asynchronous streams;
- state-heavy UI where operators materially reduce coordination code.

Do not introduce Rx for a single click callback or simple notification. Do not add an event bus to avoid a direct dependency that is already appropriate.

When Rx or R3 is justified:

- assign subscription ownership to a concrete lifetime;
- make disposal visible;
- keep important scenario decisions out of opaque operator chains;
- avoid leaking reactive types into contracts that do not need stream semantics.

Mix direct calls, events, and reactive streams where each solves a different current relationship. Do not enforce one mechanism across an entire project for aesthetic consistency.

## Gameplay Runtime Boundaries

Allow Unity runtime interaction, orchestration, and simple state to remain together while one object owns and changes them coherently.

Extract only the concern under pressure:

- move reusable or invariant-heavy rules into plain C# values or models;
- move repeated multi-dependency actions into a focused operation;
- centralize transitions when several objects compete to own flow state;
- isolate animation, VFX, input, or physics only when it varies or obscures gameplay decisions;
- separate HUD mapping when presentation complexity grows independently.

Do not create a `UseCase` for every action or ban business decisions from all Unity callbacks. A callback may perform a small local rule. Extract when the rule has independent meaning, reuse, branching risk, or testing value.

Keep one explicit source of truth even in a direct design. Avoid global singleton access when it hides ownership or lets unrelated objects mutate the same state.

## Physics Boundaries

Use Unity physics types directly inside a local runtime feature when no independent boundary needs clean data.

Convert physics observations to project-level facts when:

- rules must run without the physics scene;
- several physics sources feed the same decision;
- ECS, networking, replay, or tests consume the result;
- `Collider`, `RaycastHit`, or `Rigidbody` details have spread into unrelated logic.

Useful boundary values may include `HitContext`, `GroundContactInfo`, `MovementIntent`, `MotorCommand`, or `TrackingCandidate`. Introduce only the values that cross a current boundary; do not mirror every Unity type pre-emptively.

Keep mapping such as `Collider -> ProjectEntityId` near the physics integration that owns it.

## Jobs, ECS, And Hybrid Execution

Treat jobs, Burst, and ECS as execution techniques, not architectural maturity badges.

Before adopting them:

- measure the relevant workload;
- identify the data and operation that dominate cost;
- confirm that simpler algorithm, allocation, batching, or update-frequency changes are insufficient;
- define who owns authoritative state during and after execution.

Use jobs or Burst for a local parallel or numeric hot path without moving the surrounding feature to ECS. Use ECS when entity count, homogeneous processing, data locality, and scheduling justify its broader model.

Expose a narrow project API only when callers must remain independent from ECS storage or when the subsystem has several consumers. A local caller may integrate directly while ownership remains obvious.

Do not leak `EntityManager`, `SystemAPI`, `EntityCommandBuffer`, `NativeArray`, `JobHandle`, component layouts, or allocator lifetimes across an earned module boundary.

Choose one synchronization model:

1. Keep source of truth outside the optimized subsystem, pass snapshots in, and return results.
2. Keep source of truth inside the subsystem and let callers use only its API.

Do not maintain two mutable authoritative copies without an explicit synchronization owner.

## Network Authority Boundaries

Keep a small network interaction direct and localized. Introduce boundaries in response to actual authority, transport, replication, serialization, or lifecycle pressure.

Separate authority decisions from transport callbacks when incorrect ownership can mutate game state. Separate gameplay intent from transport when the same action originates locally and remotely, is tested independently, or survives an SDK change.

Introduce:

- a focused handler for a network event with non-trivial coordination;
- an authority policy or service when checks repeat or vary;
- a replication adapter when SDK calls spread across gameplay code;
- a transport contract when another transport exists or independent evolution is valuable now;
- a bootstrapper when callback registration and session lifetime are no longer obvious locally.

One localized call to `NetworkManager.Singleton` does not require a wrapper. Repeated access across unrelated locations is a signal to centralize ownership.

Do not let transport callbacks mutate UI or shared domain state through hidden side effects. Keep the path from incoming message to authority decision and state mutation traceable, whether it uses two types or a mature module.
