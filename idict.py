"""The idict module contains functions implementing the immutable dictionary
(IDict) data abstraction for CS61A at UC Berkeley.

IDicts are (immutable) dictionaries, a common data structure in computer
science which maps keys to values.

One might notice that none of the doctests for either ADT actually "show" an
IDict. This is because this ADT is meant to be treated as a black box: the
tests do not assume any specific implementation for IDicts.
"""


# Immutable Dictionaries Abstraction


def make_idict(*mappings):
    """Construct a new immutable dictionary using the mappings provided."""
    return mappings


def idict_keys(idict):
    """Return a tuple of the keys belonging to idict.

    >>> test_idict = make_idict(("A", 1),
    ...                         ("B", 2),
    ...                         ("C", 3))
    ...
    >>> idict_keys(test_idict)
    ('A', 'B', 'C')
    >>> idict_keys(make_idict())
    ()
    """
    return tuple(mapping[0] for mapping in idict)


def idict_select(idict, key):
    """Return the value that key maps to in immutable dictionary idict.

    Returns None if the key is not present in idict.
    
    >>> test_idict = make_idict(("A", 1),
    ...                         ("B", 2),
    ...                         ("C", 3))
    ...
    >>> idict_select(test_idict, "Z")
    >>> idict_select(test_idict, "A")
    1
    >>> idict_select(test_idict, "B")
    2
    """
    for mapping in idict:
        if mapping[0] == key:
            return mapping[1]


def could_be_idict(x):
    """Returns True if x could be an idict."""
    if type(x) is not tuple:
        return False
    for mapping in x:
        if type(mapping) is not tuple or len(mapping) != 2:
            return False
    return True


# Immutable Dictionaries Utility Functions


def idict_insert(idict, key, value):
    """Return a copy of idict updated with key mapped to value.

    Replaced keys will show up at the end of the dictionary.

    >>> test_idict = make_idict(("A", 1),
    ...                         ("B", 2),
    ...                         ("C", 3))
    ...
    >>> idict_str(test_idict)
    "('A' -> 1, 'B' -> 2, 'C' -> 3)"
    >>> idict_select(test_idict, "Z")
    >>> idict_select(test_idict, "A")
    1
    >>> idict_select(test_idict, "B")
    2
    >>> test_idict = idict_insert(test_idict, "A", 42)
    >>> idict_str(test_idict)
    "('B' -> 2, 'C' -> 3, 'A' -> 42)"
    >>> test_idict = idict_insert(test_idict, "Z", 7)
    >>> idict_str(test_idict)
    "('B' -> 2, 'C' -> 3, 'A' -> 42, 'Z' -> 7)"
    >>> idict_select(test_idict, "Z")
    7
    >>> idict_select(test_idict, "A")
    42
    >>> idict_select(test_idict, "B")
    2
    """
    new_mappings = ()
    for old_key in idict_keys(idict):
        if old_key != key:
            new_mappings += ((old_key, idict_select(idict, old_key)),)
    new_mappings += ((key, value),)
    return make_idict(*new_mappings)


def idict_len(idict):
    """Return the number of mappings in idict.

    >>> idict_len(make_idict(("A", 1), ("B", 2)))
    2
    >>> idict_len(make_idict(("A", 1)))
    1
    >>> idict_len(make_idict())
    0
    """
    return len(idict_keys(idict))


def idict_values(idict):
    """Return a tuple of the values mapped to in idict.

    >>> idict_values(make_idict(("A", 1), ("B", 2), ("C", 3)))
    (1, 2, 3)
    >>> idict_values(make_idict())
    ()
    """
    return tuple(idict_select(idict, key) for key in idict_keys(idict))


def idict_str(idict):
    """Return a string representation of the idict.
    
    >>> idict_str(make_idict())
    '()'
    >>> idict_str(make_idict(("A", 1), ("B", 2), ("C", 3)))
    "('A' -> 1, 'B' -> 2, 'C' -> 3)"
    >>> idict_str(make_idict(("A", 1)))
    "('A' -> 1)"
    """
    result = "("
    is_first = True
    for key in idict_keys(idict):
        # Add comma if necessary
        if not is_first:
            result += ", "
        else:
            is_first = False

        result += repr(key) + " -> " + repr(idict_select(idict, key))
    return result + ")"

def idict_items(idict):
    """Return a tuple of key:value pairs from the idict."""

    return tuple(zip(idict_keys(idict), idict_values(idict)))
