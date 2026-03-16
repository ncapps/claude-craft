# Design Principles Reference

These principles form the foundation for good class design. Apply them during Phase 5
(Class Design & Principles) and when answering standalone design questions. Each
principle includes a definition, how to evaluate a design against it, and how to fix
violations.

---

## 1. Single Responsibility Principle (SRP) — Cohesion

**Definition:** A well-designed class has only one primary responsibility. It should
have only one reason to change.

**How to evaluate:**
- List the class's instance variables and methods
- Group them by responsibility (e.g., operation, maintenance, display, persistence)
- If more than one group exists, the class has multiple responsibilities

**How to fix violations:**
- Split the class into smaller classes, each with a single responsibility
- Each new class gets the instance variables and methods for one responsibility
- Establish relationships between the new classes (typically composition)

**Example of violation:** A `Car` class that handles driving, maintenance, and cleaning.
Split into `Car` (driving), `Garage` (maintenance), and `CarWash` (cleaning).

**Key insight:** After splitting, each class's methods should work only with that
class's own instance variables. If a method doesn't operate on any of its class's
state, it may belong elsewhere.

---

## 2. Principle of Least Knowledge (PoLK) — Loose Coupling

**Definition:** Minimize the dependencies among classes. The less class A knows about
the internal implementation of class B, the less likely changes in B will affect A.

**How to evaluate:**
- For each class, count references to other classes (instance variables, parameters,
  local variables, method calls)
- Check if class A accesses internal details of class B (instance variables, private
  methods)
- Fewer dependencies = better coupling

**How to fix violations:**
- Hide implementation details by making instance variables private
- Expose only public getter/setter methods needed by other classes
- Use delegation: class A calls a method on class B rather than reaching into B's
  internals
- Pass only what is needed as parameters rather than entire objects

**Key insight:** Two classes are loosely coupled when changes to one class's
implementation do not force changes in the other. Loose coupling supports
encapsulation.

---

## 3. Open-Closed Principle (OCP)

**Definition:** A class should be open for extension but closed for modification.
Once a class is tested and deployed, avoid modifying its source code. Instead,
extend its behavior through inheritance or composition.

**How to evaluate:**
- Identify where new features or variations might be needed
- Check if adding a new feature requires changing existing class code
- Check if the class uses conditional logic (if/switch) to handle variations

**How to fix violations:**
- Define an abstract superclass or interface for the varying behavior
- Create concrete subclasses for each variation
- Use composition to inject behavior objects rather than hardcoding conditions
- Apply the Strategy or Template Method pattern for algorithm variations

**Key insight:** Conditional logic that selects behavior based on type is often a
sign that inheritance or a design pattern should be used instead.

---

## 4. Principle of Least Astonishment (PoLA)

**Definition:** There should be few, if any, surprises for programmers who use
the code. Surprises cause logic errors, runtime errors, and maintenance difficulty.

**How to evaluate:**
- Check method names: does each name accurately describe what the method does?
- Check for off-by-one errors in loops and range operations
- Check for hidden performance problems (e.g., O(n^2) operations that look simple)
- Check that similar operations behave consistently across the codebase

**How to fix violations:**
- Rename methods to accurately reflect their behavior
- Use clear, consistent naming conventions across all classes
- Document any non-obvious behavior or performance characteristics
- Apply programming by contract: define preconditions, postconditions, and class
  invariants for critical methods

**Programming by contract elements:**
- **Precondition:** What must be true before calling a method
- **Postcondition:** What must be true after the method returns
- **Class invariant:** What must remain true of object states at all times

---

## 5. Liskov Substitution Principle (LSP)

**Definition:** A program that uses a superclass object must be able to replace it
with one of its subclass objects without the program behaving incorrectly.

**How to evaluate:**
- For each superclass-subclass pair, check: can every use of the superclass be
  replaced with the subclass without breaking correctness?
- Check overriding methods: does the subclass method honor the superclass contract?
- Check if subclass adds restrictions that the superclass does not have

**How to fix violations:**
- Rethink the inheritance hierarchy — the subclass may not truly be a specialized
  version of the superclass
- Consider using composition (has-a) instead of inheritance (is-a)
- Ensure overriding methods do not strengthen preconditions or weaken postconditions
- Use the Favor Composition over Inheritance principle as an alternative

**Key insight:** The classic example of LSP violation is making `Square` a subclass
of `Rectangle`. A `Square` constrains width == height, which breaks code that
assumes it can set width and height independently. Use composition instead.

---

## 6. Law of Demeter (LoD)

**Definition:** An object should only communicate with its immediate associates.
Specifically, a method M of class C should only call methods on:
1. Class C itself (its own methods)
2. Objects created within method M
3. Objects passed as parameters to method M
4. Objects stored in instance variables of C

**How to evaluate:**
- Look for method chains: `a.getB().getC().doSomething()` — this violates LoD
  because it reaches through B to access C
- Check if class A accesses objects that are internal to class B

**How to fix violations:**
- Add a delegate method: instead of `a.getB().getC().doSomething()`, add a
  `doSomething()` method to A that delegates to B
- Restructure so each class only talks to its direct collaborators
- Apply the Facade pattern to hide complex subsystem interactions

---

## 7. Favor Composition over Inheritance (FCoI)

**Definition:** Prefer has-a relationships over is-a relationships. Composition
provides more flexibility than inheritance because behavior can be changed at
runtime by swapping composed objects.

**How to evaluate:**
- For each inheritance relationship, ask: is the subclass truly a specialized
  version of the superclass, or does it just need some of its behavior?
- Check if the inheritance hierarchy is deep (more than 2-3 levels)
- Check if subclasses override most superclass methods (sign of weak is-a)

**How to fix violations:**
- Replace inheritance with composition: the class holds a reference to a behavior
  object instead of inheriting from it
- Use interfaces/abstract classes to define behavior contracts
- Apply the Strategy pattern to encapsulate interchangeable behaviors

**Key insight:** Inheritance hardcodes behavior at compile time. Composition allows
behavior to be selected or changed at runtime. Use inheritance when the is-a
relationship is genuinely true and stable. Use composition when flexibility is
needed.

---

## 8. Code to the Interface Principle (CtIP)

**Definition:** Depend on abstractions (interfaces and abstract classes), not on
concrete implementations. This allows swapping implementations without changing
the code that uses them.

**How to evaluate:**
- Check if variables and parameters are typed to concrete classes or to interfaces
- Check if object creation is hardcoded (uses specific class names) vs. delegated
  to factories
- Check if adding a new implementation requires changing existing code

**How to fix violations:**
- Define an interface or abstract class for the behavior
- Type variables and parameters to the interface, not the concrete class
- Use factory methods or factory classes to create objects
- Apply the Factory Method or Abstract Factory pattern

---

## Applying Principles During Design

When evaluating a class design (Phase 5), work through the principles in this order:

1. **SRP first** — Split classes that have multiple responsibilities
2. **PoLK next** — Minimize dependencies between the resulting classes
3. **OCP** — Ensure the design can be extended without modifying existing classes
4. **PoLA** — Check for naming, behavioral, or performance surprises
5. **LSP** — Validate inheritance hierarchies
6. **LoD** — Check for method chains and reaching through objects
7. **FCoI** — Consider replacing fragile inheritance with composition
8. **CtIP** — Depend on abstractions where flexibility is needed

Present findings as a table:

```
| Principle | Status | Finding | Recommendation |
|-----------|--------|---------|----------------|
| SRP       | PASS   | Each class has single responsibility | — |
| PoLK      | WARN   | ClassA accesses ClassB internals | Add getter method |
| ...       | ...    | ... | ... |
```
