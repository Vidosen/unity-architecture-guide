# Reference Architectures

## Table of Contents

1. How to use these examples
2. UI screen
3. Gameplay runtime
4. Multi-step flow
5. ECS or jobs subsystem
6. Networked gameplay
7. Hybrid UI, gameplay, and network
8. Selection questions

## How To Use These Examples

Read every example from the smallest useful shape toward a possible mature shape. Stop as soon as the current pressures are resolved. Do not create the final folders and types in advance.

The examples describe a continuum, not architecture stages. Different parts of one subsystem may need different techniques at the same time. A feature may also become simpler again after requirements disappear.

For every extraction, ask:

- What current problem does the new type solve?
- Which code becomes easier to change or own?
- What new navigation, wiring, lifetime, or mapping cost appears?
- What evidence would make this extraction unnecessary?

## UI Screen

### Start Direct

For a small settings, diagnostics, pause, or shop screen, begin with one cohesive component:

```text
ShopScreen (MonoBehaviour)
  - serialized controls and labels
  - click handlers
  - one local async purchase flow
  - loading, success, and error rendering
```

Keep this shape while one screen owns the behavior, the state remains small, and the external call is localized.

### Extract Only Under Pressure

| Current pressure | Smallest useful extraction |
| --- | --- |
| Rendering branches obscure the workflow | Add a local `ShopViewState` or focused render methods |
| Several views initiate the same purchase flow | Extract `PurchasePremium` as one shared operation |
| IAP calls spread or another implementation exists | Introduce `IIapGateway` and one adapter |
| Loading, retries, navigation, and error mapping change independently from widgets | Introduce `ShopPresenter` |
| Offer and purchase rules have meaningful invariants | Extract plain C# domain values and rules |

Do not create a presenter, query, use case, repository, and analytics interface merely because the screen is called a module.

### Possible Mature Shape

When all of those pressures actually coexist, the shape may become:

```text
ShopScreenView
  -> ShopPresenter
      -> GetShopOffersQuery
      -> PurchasePremiumUseCase
          -> IShopRepository
          -> IIapGateway
          -> ShopOffer / PurchaseRules

Infrastructure
  - RemoteShopRepository
  - UnityIapAdapter
```

Keep only the roles justified by the current screen and integrations.

## Gameplay Runtime

### Start Direct

A small player or interactable feature may begin as one component or a few direct collaborators:

```text
CharacterController (MonoBehaviour)
  - reads input
  - moves a Rigidbody
  - updates Animator
  - owns local health and cooldown state
```

This is acceptable while rules are simple, one runtime object owns the state, and changes remain local.

### Extract Only Under Pressure

| Current pressure | Smallest useful extraction |
| --- | --- |
| Movement math is complex or repeatedly regresses | Extract a plain movement calculation or focused motor |
| Health or cooldown rules are reused or invariant-heavy | Extract `Health`, `CooldownSet`, or one rule object |
| Input sources vary | Introduce an input contract at that boundary |
| Physics callbacks and gameplay decisions are difficult to reason about together | Convert callbacks into a small fact such as `HitContext` |
| Several actions coordinate shared state | Introduce one runtime coordinator or focused use case |
| HUD mapping grows independently | Extract a HUD presenter, leaving gameplay state authoritative elsewhere |

Do not convert every `Update`, `FixedUpdate`, or trigger callback into a separate application service. Unity callbacks may orchestrate local behavior until independent ownership becomes useful.

### Possible Mature Shape

```text
PlayerInputReader (MonoBehaviour)
  -> CharacterRuntimeController
      -> MoveCharacter
      -> UseAbility
      -> Character / Health / Cooldowns

GroundProbeAdapter -> GroundContactInfo
RigidbodyMotorAdapter <- MotorCommand
CharacterHudPresenter -> CharacterHudView
```

Use this fuller separation only when rules, physics, input, and presentation genuinely evolve on different axes.

## Multi-Step Flow

### Start Direct

Represent a short, linear flow in one owner:

```text
TrainingFlowController
  - current phase field
  - explicit transition methods
  - local enter and exit actions
```

An enum and a small switch are often enough. Avoid one class per state when transitions are few and phase behavior remains easy to inspect together.

### Extract Only Under Pressure

Introduce a state machine when current behavior includes several of these concerns:

- invalid transitions must be prevented;
- phases own non-trivial enter, exit, or cancellation work;
- transitions branch from events or async results;
- phase logic is reused or independently tested;
- multiple objects currently believe they own the active phase.

First centralize transition ownership. Extract separate state objects only when their behavior is large or independently variable.

### Possible Mature Shape

```text
TrainingFlowController
  -> TrainingFlowStateMachine
      -> WarmupState
      -> ActiveTrainingState
      -> ResultsState

Supporting operations
  - StartTraining
  - CompleteTraining
  - SubmitResults
```

Keep simple transitions in the state machine itself; do not add use cases that only rename state entry methods.

## ECS Or Jobs Subsystem

### Start Direct

Keep a subsystem in ordinary `MonoBehaviour` or plain C# form until profiling shows a relevant scale or scheduling problem. Prefer a local algorithm or data-layout improvement before changing execution models.

### Extract Only Under Pressure

Use jobs or Burst when measured hot work is parallelizable and data-oriented containers provide a clear benefit. Use ECS when entity count, homogeneous processing, system scheduling, or data locality materially improves the target workload.

Do not introduce ECS for future scale, architectural purity, or a small number of heterogeneous actors.

If the optimized implementation has one local caller, a direct integration may remain sufficient. Add a project-level API when callers, ownership, or representation must evolve independently from ECS internals.

### Possible Mature Shape

```text
Callers
  -> ITargetTrackingModule
      -> TargetTrackingModule
          -> ECS components, systems, jobs, and Burst kernels

Boundary data
  - ScanRequest
  - TrackingCandidate
  - TargetRegistration
```

Choose one source of truth. Either feed snapshots into ECS and return results, or keep authoritative state inside the module and expose only its API. Do not mirror mutable truth in OO and ECS without an explicit synchronization owner.

## Networked Gameplay

### Start Direct

A prototype or isolated network behavior may use one network-aware component that receives callbacks, checks authority, and updates its owned runtime state. Keep SDK access localized even before introducing abstractions.

### Extract Only Under Pressure

| Current pressure | Smallest useful extraction |
| --- | --- |
| Authority checks are duplicated or inconsistent | Centralize one authority policy or service |
| Transport callbacks contain gameplay decisions | Forward intent into one focused gameplay operation |
| Replication code spreads across unrelated objects | Introduce one replication adapter |
| Another transport is real or the SDK changes independently | Introduce a narrow transport contract |
| Session lifecycle has several event sources | Add one bootstrapper or callback coordinator |
| Serialization shape differs from gameplay state | Add boundary DTOs and explicit mapping |

Authority is often a real boundary earlier than generic layering. Separate it when incorrect ownership can change game state, not simply because the project uses networking.

### Possible Mature Shape

```text
NetworkBootstrapper
  -> transport callback adapters
      -> ClientConnectedHandler
      -> OwnershipChangedHandler
      -> SpawnPlayerUseCase
      -> MatchStateSynchronizer

Contracts
  - IAuthorityService
  - INetworkReplicationAdapter

Domain
  - MatchState
  - PlayerSession
  - AuthorityRules
```

Keep gameplay intent and rules independent from transport only to the degree required by authority, reuse, testing, or transport volatility.

## Hybrid UI, Gameplay, And Network

Do not start with a dedicated hybrid architecture. Combine boundaries already justified in their own areas.

A simple ability button may call a local gameplay component directly. Add a presenter when UI state becomes non-trivial. Add an authority boundary when the action can be rejected or owned remotely. Add replication mapping when transport state differs from gameplay state.

A mature path may look like:

```text
AbilityPanelView
  -> AbilityPanelPresenter
      -> GetAbilityPanelState
      -> UseAbility
          -> Character
          -> IAuthorityService
          -> INetworkReplicationAdapter
```

The UI must not become authoritative gameplay state. Beyond that invariant, keep the path as short as current behavior allows.

## Selection Questions

Before recommending any reference shape, answer:

- What is the smallest shape that implements today's behavior?
- Where is the current source of truth?
- Which responsibilities actually change independently?
- Which lifetimes or owners conflict today?
- Which external boundary is volatile, repeated, or replaceable now?
- Which rule or scenario has enough risk to deserve isolation?
- Which performance problem has been measured?
- Which proposed types can be omitted without losing current behavior or safety?

If the last answer removes every proposed abstraction, recommend the direct implementation and record only the trigger for reconsideration.
