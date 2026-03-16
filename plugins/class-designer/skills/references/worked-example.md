# Worked Example: Book Catalogue Application

This reference shows the complete class design process applied to a library book
catalogue application. Use it as a model for the tables, reasoning style, and
level of detail expected at each phase.

---

## Phase 1: Problem Statement

```
APPLICATION: Book Catalogue
PROBLEM: Automate a library's card catalogue so librarians can manage books
         and customers can search for them by attributes.
ACTORS: Librarian (manages books), Customer (searches for books),
        Database (backend storage)
SCOPE NOTES: The database system is external. Web browsers are external.
             The application manages the catalogue logic, search, and forms.
```

---

## Phase 2: Requirements

### Functional Requirements

1. The book catalogue shall store different kinds of books and their attributes.
2. A librarian must be able to add new books to the catalogue.
3. A librarian must be able to update and delete existing books in the catalogue.
4. The kinds of books shall include fiction, cookbooks, and how-to.
5. All books must have title, author's last name, and author's first name.
6. Fiction books must include the publication year and genre attributes.
7. Genre must include adventure, classics, detective, fantasy, historic, horror,
   romance, and science fiction.
8. Cookbooks must include the region attribute.
9. How-to books must include the subject attribute.
10. A customer must be able to search the catalogue by providing any number of
    desired target attribute values.
11. A customer must complete a web browser-based form to specify target attributes.
12. A customer's input in the form must be verified for correct format and values.
13. String attribute matches during searches shall be case-insensitive.
14. A customer must be able to specify don't-care (wildcard) target attributes.
15. Each don't-care attribute must match the corresponding attribute in all books.
16. A book shall match if all corresponding attribute values are equal or the
    target attribute is don't-care.

### Nonfunctional Requirements

1. A book search must take under 2 seconds.
2. The application must run on Windows, macOS, and Linux.
3. The user interface shall be similar to the previous version's UI.
4. Displayed messages shall be customizable in English, Spanish, or Vietnamese.

---

## Phase 4a: Noun Analysis

| Noun        | Class? | Reasoning                                                   |
|-------------|--------|-------------------------------------------------------------|
| catalogue   | Yes    | The application implements a book catalogue.                |
| book        | Yes    | The catalogue stores book objects.                          |
| attribute   | Yes    | Each book has a set of attributes with matching behavior.   |
| librarian   | No     | An actor external to the application.                       |
| customer    | No     | An actor external to the application.                       |
| kind        | No     | An attribute value (enumeration constant).                  |
| title       | No     | An attribute value (string).                                |
| name        | No     | An attribute value (string).                                |
| year        | No     | An attribute value (integer).                               |
| genre       | No     | An attribute value (enumeration constant).                  |
| region      | No     | An attribute value (enumeration constant).                  |
| subject     | No     | An attribute value (enumeration constant).                  |
| browser     | No     | External system the application works with.                 |
| form        | Yes    | The application manages a user input form.                  |
| input       | No     | A value entered by a user into a form.                      |
| format      | No     | Not a separate entity in the application.                   |
| value       | No     | An integer, string, or enumeration constant.                |
| string      | No     | Built-in Python type.                                       |

**Result:** Four initial classes — Catalogue, Book, Attributes, Form.

---

## Phase 4b: Class State Table

| Class       | State (what it tracks)     | Instance Variables                             |
|-------------|----------------------------|------------------------------------------------|
| Catalogue   | List of books              | `_booklist` (list of Book objects)             |
| Book        | Book attributes            | `_attributes` (Attributes object)              |
| Attributes  | Attribute key-value pairs  | `_dictionary` (dict of key-value pairs)        |
| Form        | User input values          | Individual instance variables per form field    |

---

## Phase 4c: Verb-to-Method Table

| Verb     | Class       | Method                                              |
|----------|-------------|-----------------------------------------------------|
| store    | Catalogue   | (handled by add — storing is the act of adding)     |
| add      | Catalogue   | `add()` — add a book to the booklist                |
| update   | Catalogue   | `update()` — update a book in the booklist          |
| delete   | Catalogue   | `delete()` — delete a book from the booklist        |
| search   | Catalogue   | `find()` — find matching books in the booklist      |
| verify   | Form        | `verify()` — verify user input in the form fields   |
| match    | Attributes  | `is_match()` — check if attributes match            |

Note: Each class's methods work with that class's own instance variables.
For example, Catalogue.add() appends Book objects to _booklist.

---

## Phase 5: Final Class Design

### Class: Catalogue
- **Purpose:** Manages the collection of books and provides search operations.
- **State:** The list of all books currently in the catalogue.
- **Instance Variables:**

  | Variable    | Type              | Description                         |
  |-------------|-------------------|-------------------------------------|
  | `_booklist` | list[Book]        | Collection of Book objects           |

- **Methods:**

  | Method     | Parameters            | Description                              |
  |------------|-----------------------|------------------------------------------|
  | `add()`    | `attrs: Attributes`   | Create a Book and append to _booklist    |
  | `update()` | `book: Book, attrs`   | Update an existing book's attributes     |
  | `delete()` | `book: Book`          | Remove a book from _booklist             |
  | `find()`   | `target: Attributes`  | Return list of books matching target     |

### Class: Book
- **Purpose:** Represents a single book with its attributes.
- **State:** The set of attribute key-value pairs for this book.
- **Instance Variables:**

  | Variable       | Type         | Description                           |
  |----------------|--------------|---------------------------------------|
  | `_attributes`  | Attributes   | The book's attribute set               |

- **Methods:**

  | Method          | Parameters   | Description                            |
  |-----------------|------------- |----------------------------------------|
  | `attributes`    | (property)   | Return the Attributes object            |
  | `__str__()`     |              | String representation of the book       |

### Class: Attributes
- **Purpose:** Stores and matches attribute key-value pairs.
- **State:** A dictionary mapping attribute keys to their values.
- **Instance Variables:**

  | Variable       | Type              | Description                        |
  |----------------|-------------------|------------------------------------|
  | `_dictionary`  | dict[Key, value]  | Key-value pairs of attributes       |

- **Methods:**

  | Method        | Parameters             | Description                          |
  |---------------|------------------------|--------------------------------------|
  | `is_match()`  | `target: Attributes`   | True if all target attrs match        |

### Class: Form
- **Purpose:** Manages user input for book search attributes.
- **State:** The current values entered by the user in each form field.
- **Instance Variables:**

  | Variable           | Type  | Description                            |
  |--------------------|-------|----------------------------------------|
  | Per-field variables | mixed | One instance variable per form field    |

- **Methods:**

  | Method      | Parameters   | Description                                 |
  |-------------|------------- |---------------------------------------------|
  | `verify()`  |              | Validate all form field values               |

### Class Relationships

- Catalogue **contains** a list of Book objects (composition).
- Each Book **has** one Attributes object (composition).
- Form is **independent** — it collects input that gets converted to an Attributes
  object for searching.

### Design Notes

- This is an initial design from textual analysis. Later iterations will likely
  discover additional classes (e.g., enum classes for Kind, Genre, Region, Subject).
- The Form class's instance variables depend on the UI framework chosen, which is
  a design decision deferred to the implementation phase.
- The relationship between Form input and the Attributes class used for searching
  will need a conversion or factory mechanism.
