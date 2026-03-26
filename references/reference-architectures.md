# Reference Architectures

## Table of Contents

1. UI screen module
2. Gameplay runtime module
3. Phase-based gameplay flow
4. ECS-backed subsystem
5. Networked gameplay module
6. Hybrid UI plus gameplay plus network
7. Selection guide

## UI Screen Module

Use for settings, profile, shop, leaderboard, onboarding, diagnostics, and similar screens.

### Shape

```text
ShopScreenView (MonoBehaviour)
  -> ShopPresenter
      -> GetShopOffersQuery
      -> PurchasePremiumUseCase
      -> RestorePurchasesUseCase
          -> IShopRepository
          -> IIapService
          -> IAnalyticsService
```

### Rules

- `View` exposes events and renders `ViewState`.
- `Presenter` owns loading, error, and content orchestration.
- `UseCase` and `Query` own application logic, not UI controls.
- SDK access stays in infrastructure.

### Folder layout

```text
Shop/
  Presentation/
    ShopScreenView.cs
    ShopPresenter.cs
    ShopViewState.cs
  Application/
    GetShopOffersQuery.cs
    PurchasePremiumUseCase.cs
    RestorePurchasesUseCase.cs
    Contracts/
      IShopRepository.cs
      IIapService.cs
  Domain/
    ShopOffer.cs
    SubscriptionState.cs
  Infrastructure/
    RemoteShopRepository.cs
    UnityIapAdapter.cs
    ShopInstaller.cs
```

## Gameplay Runtime Module

Use for player controller, combat loop, interactables, training gameplay, and small-to-medium runtime systems.

### Shape

```text
PlayerInputReader (MonoBehaviour)
  -> CharacterRuntimeController
      -> MoveCharacterUseCase
      -> JumpUseCase
      -> UseAbilityUseCase
      -> CharacterPresenter / HudPresenter

GroundProbeAdapter
  -> GroundContactInfo

RigidbodyMotorAdapter
  <- MotorCommand
```

### Rules

- `OnTriggerEnter`, `Update`, and `FixedUpdate` should not hold business rules.
- runtime controller should not become a god object.
- gameplay state needs an explicit owner.
- Unity physics stays at adapter boundaries.

### Folder layout

```text
Combat/
  Presentation/
    Runtime/
      PlayerInputReader.cs
      CharacterAnimatorView.cs
      CharacterHudView.cs
      HitboxAdapter.cs
    Hud/
      CharacterHudPresenter.cs
      CharacterHudViewState.cs
  Application/
    UseCases/
      MoveCharacterUseCase.cs
      JumpUseCase.cs
      UseAbilityUseCase.cs
      ApplyDamageUseCase.cs
    Systems/
      CooldownTickSystem.cs
    Contracts/
      ICharacterRepository.cs
      IAuthorityService.cs
      IHitVfxAdapter.cs
  Domain/
    Character.cs
    Health.cs
    Stamina.cs
    CooldownSet.cs
    MovementRules.cs
  Infrastructure/
    RuntimeCharacterRepository.cs
    HitVfxAdapter.cs
    CombatInstaller.cs
```

## Phase-Based Gameplay Flow

Use for match lifecycle, onboarding, training session, wave combat, or any staged process.

### Shape

```text
TrainingSceneBootstrapper
  -> TrainingFlowStateMachine
      -> WarmupState
      -> ActiveSessionState
      -> ResultsState
      -> CompletedState
```

### Rules

- represent phases as formal states, not scattered booleans;
- keep state transitions explicit;
- keep state machine independent from concrete widgets;
- keep per-phase actions in use cases or state entry and exit handlers.

### Folder layout

```text
TrainingFlow/
  Presentation/
    TrainingHudView.cs
    TrainingHudPresenter.cs
  Application/
    StateMachines/
      TrainingFlowStateMachine.cs
      States/
        WarmupState.cs
        ActiveTrainingState.cs
        ResultsState.cs
    UseCases/
      StartTrainingUseCase.cs
      CompleteTrainingSessionUseCase.cs
      SubmitResultsUseCase.cs
  Domain/
    TrainingSession.cs
    TrainingScore.cs
    TrainingRules.cs
  Infrastructure/
    TrainingFlowBootstrapper.cs
    TrainingFlowInstaller.cs
```

## ECS-Backed Subsystem

Use for projectile simulation, target tracking, crowd simulation, large scans, and other high-scale subsystems.

### Shape

```text
Application layer
  -> ITargetTrackingModule
      -> TargetTrackingModule
          -> ECS World / Systems / Jobs / Burst kernels
```

### Rules

- expose narrow project-level requests and results;
- keep ECS internals private to the module;
- define source of truth explicitly;
- let the rest of the project depend on the API, not on ECS storage.

### Folder layout

```text
TargetTracking/
  Api/
    ITargetTrackingModule.cs
    ScanRequest.cs
    TrackingCandidate.cs
    TargetRegistration.cs
  Application/
    RequestTrackingScanUseCase.cs
  Domain/
    TargetDescriptor.cs
    TrackingRules.cs
  Runtime/
    TargetTrackingBootstrapper.cs
    TargetViewAdapter.cs
    ColliderTargetRegistry.cs
  Ecs/
    Components/
    Systems/
    Jobs/
    Bakers/
    Internal/
  Infrastructure/
    TargetTrackingModule.cs
    TargetTrackingInstaller.cs
```

## Networked Gameplay Module

Use for authoritative multiplayer logic, ownership-based interaction, and replicated session flows.

### Shape

```text
NetworkBootstrapper
  -> Netcode callback adapters
      -> ClientConnectedHandler
      -> OwnershipChangedHandler
      -> SpawnPlayerUseCase
      -> DespawnPlayerUseCase
      -> MatchStateSynchronizer
```

### Rules

- keep transport callbacks at the boundary;
- make authority explicit;
- keep gameplay rules independent from transport;
- isolate replication and serialization behind adapters.

### Folder layout

```text
Multiplayer/
  Presentation/
    NetworkStatusView.cs
    MatchHudPresenter.cs
  Application/
    UseCases/
      SpawnPlayerUseCase.cs
      DespawnPlayerUseCase.cs
      SubmitPlayerActionUseCase.cs
    Handlers/
      ClientConnectedHandler.cs
      OwnershipChangedHandler.cs
    Contracts/
      IAuthorityService.cs
      INetworkReplicationAdapter.cs
  Domain/
    MatchState.cs
    PlayerSession.cs
    AuthorityRules.cs
  Infrastructure/
    NetcodeAuthorityAdapter.cs
    NetcodeReplicationAdapter.cs
    NetworkBootstrapper.cs
```

## Hybrid UI Plus Gameplay Plus Network

Use for HUD in a live match, in-game inventory, equipment panels, and pause overlays that reflect gameplay state.

### Shape

```text
AbilityPanelView
  -> AbilityPanelPresenter
      -> GetAbilityPanelStateQuery
      -> UseAbilityUseCase
          -> IAuthorityService
          -> Character
          -> INetworkReplicationAdapter
```

### Rules

- UI does not talk to the network SDK directly;
- UI is not the source of truth for gameplay state;
- gameplay runtime does not mutate buttons directly;
- presenter or query layer maps gameplay state into UI state.

## Selection Guide

- regular UI screen: use the UI screen module.
- local gameplay runtime: use the gameplay runtime module.
- multi-stage flow: use a phase-based state machine.
- high-scale performance island: use the ECS-backed subsystem.
- authoritative transport-aware flow: use the networked gameplay module.
- live UI over gameplay or network: use the hybrid module.

If none fits perfectly, still answer these questions explicitly:

- where is the source of truth;
- where are the boundaries;
- who owns orchestration;
- what layer integrates with Unity or transport details.
