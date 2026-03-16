---
name: oop-designer
description: >
  This skill should be used when the user asks to design an application or classes
  using OOP, gather or write requirements, perform textual analysis on requirements,
  identify classes from nouns or methods from verbs, create UML diagrams (class,
  use case, state, sequence), apply or evaluate design patterns (Strategy, Observer,
  Factory, Adapter, etc.), check design principles (SRP, cohesion, coupling, LSP,
  OCP, Law of Demeter, composition over inheritance), iterate on a design, or
  review an existing class design for quality.
---

# OOP Designer — From Requirements to UML

A disciplined, iterative process for designing object-oriented applications. Guide users
from problem understanding through requirements, textual analysis, class design, design
principle evaluation, and design pattern application — producing text-based UML diagrams
as the deliverable.

The methodology follows two governing rules: first build the **right application** (get
requirements right), then build the **application right** (design classes well using
principles and patterns). Output is language-agnostic — no code generation, only design
artifacts.

---

## Design Document

Maintain a running Design Document as a markdown file throughout the process. After
completing each phase, save or update the file. Ask the user for a file name and
location at the start (default: `design-document.md` in the current working directory).
The document accumulates all phases and is the primary deliverable.

Structure the document with these sections, added progressively:

```markdown
# Design Document: <Application Name>
## Problem Statement
## Requirements
### Functional Requirements
### Nonfunctional Requirements
## Use Cases
## Textual Analysis
### Noun Analysis
### Class State
### Verb-to-Method Analysis
## Class Design
## Design Principle Evaluation
## Design Patterns Applied
## UML Diagrams
### Class Diagram
### Use Case Diagram
### State Diagram (if applicable)
### Sequence Diagram (if applicable)
## Design Notes & Open Questions
## Iteration Log
```

---

## Workflow Phases

Work through phases in order. If the user already has partial work, pick up at the
appropriate phase. After each phase, update the Design Document on disk.

### Phase 1: Understand the Problem

Establish context before writing requirements. Ask the user:
1. What is the application? Get a name and one-sentence problem statement.
2. Who are the actors? Identify people or external systems that interact with it.
3. What is the scope? What is inside the application boundary vs. outside?

Summarize back to the user before proceeding. The user is the domain expert.

### Phase 2: Gather Requirements

Guide the user through functional and nonfunctional requirements using must/shall
language. For functional requirements, ask about each actor's needs, data, and
operations. Watch for implied requirements. For nonfunctional requirements, prompt
for performance, platform, security, usability, reliability, maintainability, and
scalability constraints.

Run a quality check before proceeding. Evaluate each requirement for: clarity,
consistency, correctness, completeness, realism, verifiability, and traceability.
Flag issues for the user.

### Phase 3: Use Cases

Create UML use case diagrams (Mermaid format) and structured use case descriptions.
Each description includes: name, goal, summary, actors, preconditions, trigger,
primary sequence (max 10 steps), alternate sequences, postconditions, nonfunctional
requirements. Use cases often reveal missing requirements — circle back to Phase 2
if gaps appear.

### Phase 4: Textual Analysis

Extract nouns from functional requirements and evaluate each as a candidate class.
Present a Noun Analysis Table with columns: Noun, Class?, Reasoning. Decision criteria:
YES if it has its own state and behavior; NO if it is an actor, simple attribute, or
built-in type; MAYBE for judgment calls.

For each identified class, determine state and instance variables (Class State Table).
Then extract verbs and assign to classes as methods (Verb-to-Method Table). Each
class's methods must operate on that class's own instance variables.

### Phase 5: Class Design & Principles

Evaluate the design against these principles (see `references/design-principles.md`):
- **Single Responsibility Principle** — Each class has one primary responsibility
- **Principle of Least Knowledge** — Minimize dependencies between classes
- **Open-Closed Principle** — Open for extension, closed for modification
- **Principle of Least Astonishment** — No surprises in behavior or performance
- **Liskov Substitution Principle** — Subclass objects replace superclass objects
- **Law of Demeter** — Only talk to immediate friends
- **Favor Composition over Inheritance** — Prefer has-a over is-a when flexible
- **Code to the Interface Principle** — Depend on abstractions, not implementations

Flag violations and propose fixes. Iterate until the design satisfies all applicable
principles.

### Phase 6: Design Patterns

Proactively evaluate the class design for pattern opportunities. Consult
`references/design-patterns.md` for the full pattern catalog. For each recommended
pattern, explain: what architecture problem it solves, how it applies, and show the
generic model adapted to the user's design. Multiple patterns may apply to a single
application.

### Phase 7: UML Output

Produce all UML diagrams in **Mermaid** syntax. See `references/uml-notation.md` for
the full notation guide. Generate at minimum:
- **Class diagram** with relationships (dependency, aggregation, composition,
  generalization, interface implementation)
- **Use case diagram** showing actors and use cases

Also generate when applicable:
- **State diagram** for objects with important runtime state transitions
- **Sequence diagram** for complex object interactions during a use case

### Phase 8: Design Iteration

Explicitly support multiple iterations. After producing the initial design, ask the
user to review. Track each iteration in the Design Document's Iteration Log with:
iteration number, what changed, and why.

Support backtracking — if a design decision proves problematic, revert and try a
different approach. This is expected and healthy. Update all affected sections of the
Design Document when backtracking.

---

## Standalone Design Questions

When the user asks a standalone question (not a full workflow) — such as "is this class
cohesive?" or "what pattern fits here?" — answer directly using the design principles
and patterns from the reference files. No need to run the full workflow.

---

## Additional Resources

### Reference Files

Consult these for detailed content. Do not duplicate their contents in responses —
read and apply them.

- **`references/design-principles.md`** — Definitions, evaluation criteria, and
  examples for all design principles
- **`references/design-patterns.md`** — Catalog of design patterns with when to use,
  generic models, Mermaid UML, and selection guidance between related patterns
- **`references/uml-notation.md`** — Complete Mermaid UML notation guide for class,
  use case, state, and sequence diagrams with relationship types and conventions
- **`references/worked-example.md`** — Complete end-to-end design walkthrough for a
  task management application, demonstrating all phases
