# Classic design patterns — reference

Each entry: what it solves, when to actually reach for it, and where a
version of it already exists in your own codebase if applicable — prefer
matching an existing instance over introducing a second way to do the same
thing.

## Creational

- **Factory Method** — subclasses/callers decide which concrete type to
  instantiate via a method, instead of the caller `new`-ing a concrete
  class directly. Use when a base type has several implementations chosen
  at runtime — e.g. a `DataSourceFactory` picking `InternalDBSource` vs.
  `ExternalAPISource` vs. `StaticListSource` from a `source_config["type"]`
  string.
- **Abstract Factory** — a factory that produces a *family* of related
  objects that must stay consistent with each other (e.g. one factory that
  returns a matched {client, auth, serializer} set for a given payment
  provider, so you can't accidentally mix one provider's client with a
  different provider's auth). Reach for this only when there's genuinely
  more than one product in the family — a single-product "factory" is just
  Factory Method.
- **Builder** — construct a complex object step-by-step when the
  constructor would otherwise need many optional/order-sensitive
  parameters. A report assembled from several independently-optional
  sections is a builder candidate if that assembly logic grows past a few
  fields.
- **Prototype** — create new objects by cloning a configured instance
  instead of re-running full construction. Rare in typical backend code;
  worth it when construction is expensive (e.g. a pre-warmed model/client)
  and you need many near-identical copies with small variations.
- **Singleton** — at most one instance, globally accessible. Use sparingly
  — it's global mutable state by another name. A per-process cached client
  (DB connection pool, model loaded once) is a legitimate case; a singleton
  used to avoid passing a dependency through a call chain is a sign you
  want dependency injection instead.

## Structural

- **Adapter** — convert one interface to another the caller expects,
  without changing either side. The right shape when integrating a
  third-party SDK (a payment provider, an auth provider) behind your own
  interface so the rest of the codebase depends on your interface, not the
  vendor's.
- **Bridge** — decouple an abstraction from its implementation so both can
  vary independently (e.g. a `NotificationSender` abstraction with
  swappable email/SMS/push implementations). Different from Adapter:
  Bridge is designed up front for multiple implementations; Adapter
  retrofits one mismatched interface.
- **Composite** — treat individual objects and groups of them uniformly
  through a shared interface (e.g. a scoring rule and a group of scoring
  rules both expose `.score()`). Fits a scorecard built from combinable
  sub-scores.
- **Decorator** — add behavior to an object without subclassing, by
  wrapping it in something with the same interface. Middleware (auth,
  rate-limiting, logging) is this pattern; prefer composing small
  decorators over one function that does auth-then-logging-then-work
  inline.
- **Facade** — a simple interface in front of a more complex subsystem.
  A `KnowledgeBase` class hiding index setup + embedding calls + DB
  lookups behind `.query(text)` is a facade — callers shouldn't need to
  know the subsystem exists.
- **Flyweight** — share common state across many objects to cut memory,
  splitting out per-instance state. Rarely needed outside
  high-object-count/perf-sensitive code; don't reach for it speculatively.
- **Proxy** — stand in for another object to control access to it (lazy
  loading, access control, caching, remote call). An HTTP client wrapper
  around another service's API that adds retry/timeout/caching in front of
  the real network call is a proxy.

## Behavioral

- **Chain of Responsibility** — pass a request along a chain of handlers
  until one handles it. Framework middleware stacks and validation
  pipelines are this pattern already.
- **Command** — encapsulate a request as an object (so it can be queued,
  logged, undone, or retried). Useful for background jobs where "what to
  do" needs to be serialized and executed later, decoupled from who
  requested it.
- **Interpreter** — define a grammar and evaluate sentences in it. Rare in
  application code; relevant if you're literally building a small
  query/rule language (e.g. a filter DSL for search).
- **Iterator** — traverse a collection without exposing its internal
  structure. Usually just your language's own iterator protocol/generators
  — don't hand-roll this.
- **Mediator** — centralize how a set of objects interact instead of them
  referencing each other directly, reducing many-to-many coupling to
  many-to-one. An orchestrator agent coordinating several tool-calling
  steps is a mediator between the tools (see `agent-patterns.md`).
- **Memento** — capture and restore an object's internal state without
  violating encapsulation. Conversation/chat-history persistence (a
  `chat_history`/`chat_job` model, or a chosen agent framework's own
  checkpointing) is this pattern — use a library's checkpointing rather
  than hand-rolling state snapshots if the project adopts one.
- **Observer** — subscribers react to state changes in a subject without
  the subject knowing who they are. Webhook dispatch (e.g. payment-
  provider events into your backend) is this pattern.
- **State** — an object changes behavior when its internal state changes,
  modeled as a set of state classes rather than a pile of conditionals on a
  status field. A ticket's `status:todo → in-progress → review → done`
  lifecycle, or a payment's pending/settled/failed lifecycle, is a State
  candidate once the conditionals on that field spread across multiple
  places.
- **Strategy** — make an algorithm swappable at runtime behind a shared
  interface. Choosing a data source via a factory (dispatching to
  `InternalDBSource`/`ExternalAPISource`/`StaticListSource`) is Strategy —
  prefer it over a branch on an enum scattered through the codebase.
- **Template Method** — a base class defines an algorithm's skeleton and
  lets subclasses override specific steps. Useful when several agents share
  the same overall flow (validate → fetch → analyze → format) but differ in
  one or two steps.
- **Visitor** — add new operations over a fixed set of types without
  modifying those types, by having each accept a visitor. Rare outside
  compiler/AST-shaped problems; usually a plain function or Strategy is
  simpler for typical backend work.

## Dependency Injection

Not a GoF pattern but the mechanism that makes Dependency Inversion (see
`swe-principles`) real: a component receives its dependencies (a DB
session, an HTTP client, config) from the outside — constructor args,
function params, or a framework's DI system — rather than constructing or
importing them itself. FastAPI's `Depends()` (or your framework's
equivalent) *is* this pattern — use it for anything a test would need to
mock or swap (DB sessions, external clients), rather than importing a
concrete client at module level.

## Architecture-level patterns

- **Repository** — one type per aggregate that mediates between domain
  logic and the data store, hiding SQL/ORM details behind domain-shaped
  methods. Worth establishing as a convention early (e.g. `services/*/
  repository.py`) — new data access should follow it rather than calling
  the ORM directly from a service/agent module.
- **Unit of Work** — group a set of repository operations into one
  transaction that commits or rolls back together. Relevant whenever a
  ticket touches more than one table that must stay consistent (e.g. a
  record and its linked reference-data rows).
- **Hexagonal / Ports & Adapters** — keep domain logic independent of
  frameworks and external services by defining ports (interfaces) the
  domain depends on, with adapters implementing them for your web
  framework, database, payment provider, etc. Useful framing when a module
  is getting hard to test because it's entangled with a specific
  framework/SDK.
- **CQRS** — separate the read model from the write model when they have
  genuinely different shapes/scaling needs (e.g. a denormalized search
  index vs. the normalized write-side schema). Adds real complexity —
  justify it against an actual read/write mismatch, don't apply it by
  default.
- **Event Sourcing** — store state as a sequence of events rather than
  current values, replaying to derive state. Heavy; only worth it when an
  auditable history of *how* state changed (not just its current value) is
  itself a requirement — e.g. a full payment/ledger history, not general
  CRUD.
- **Saga** — coordinate a multi-step transaction across services where a
  single ACID transaction isn't possible, with explicit compensating
  actions if a later step fails. Relevant to any multi-step operation
  spanning two of your workspace's services (e.g. an analysis call that
  also triggers a payment charge) that needs to be rolled back consistently
  on partial failure.
