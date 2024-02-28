import re
import xmi_handling as xh


def positional_insert(original_string, insertion, position):
    """Inserts a string into another string at a given position.

    Args:
        original_string (str): string receiving the insertion
        insertion (str): string to be inserted
        position (positive int): position/slice at which
            the insertion takes place

    Raises:
        ValueError: if insertion at the specified position is not possible
            because it falls outside the string (when negative or too big)

    Returns:
        str: modified original string containing the insertion
    """

    if len(original_string) < position:
        raise ValueError('Position out of range.')
    if position < 0:
        raise ValueError('Position must be greater or equal to 0.')

    modified_string = ''.join((
        original_string[:position],
        insertion,
        original_string[position:]
    ))
    return modified_string


def positional_delete(original_string, deletion_len, position):
    """Deletes deletion_len characters at a given position in a string.

    Args:
        original_string (str): string whose characters get deleted
        deletion_len (positive int): amount of characters to delete
        position (positive int): position/slice at which
            the deletion takes place

    Raises:
        ValueError: if deletion is not possible because the int
            deletion_len or position do not fit (when negative or too big)

    Returns:
        str: modified original_string with the characters deleted
    """
    if deletion_len > len(original_string) - position:
        raise ValueError(
            'Deletion length greater than string length.'
        )
    if len(original_string) < position:
        raise ValueError(
            'Position out of range.'
        )
    if position < 0 or deletion_len < 0:
        raise ValueError(
            'Position and deletion_len must be greater or equal to 0.'
        )

    modified_string = ''.join((
        original_string[:position],
        original_string[position+deletion_len:]
    ))
    return modified_string


def adjust_annotations(tree, namespaces, change_len, position,
                       annotations=None):
    """Adjusts annotations to correctly map onto a modified sofaString.

    Modification can take two forms: insertion and deletion.
    With a deletion, the change_len should be negative.

    Args:
        tree (ElementTree object): tree whose annotations will be adjusted
        namespaces (dict): namespace dictionary the tree uses
        change_len (int): length of the inserted or deleted part of the
            string. If a deletion took place, change_len should be negative
        position (int): position/slice in the string
            at which the insertion or deletion took place

    Returns:
        ElementTree object: tree with adjusted annotations
    """

    if annotations is None:
        annotations = ['type5:Token', 'type5:Sentence', 'custom:Span']

    for annotation in annotations:
        for element in tree.findall(annotation, namespaces):
            if int(element.get('begin')) >= position:
                element.set(
                    'begin',
                    str(int(element.get('begin')) + change_len)
                )
            if int(element.get('end')) >= position + 1:
                element.set(
                    'end',
                    str(int(element.get('end')) + change_len)
                )

    return tree


def sofa_string_insert(tree, namespaces, insertion, position):
    """Inserts a string into the sofaString, adjusting annotations accordingly

    Args:
        tree (ElementTree object): tree whose sofaString and annotations will
            be adjusted
        namespaces (dict): namespace dictionary the tree uses
        insertion (str): the string to be inserted
        position (positive int): position/slice at which
            the insertion takes place

    Returns:
        ElementTree object: tree with adjusted sofaString and annotations
    """

    sofa = tree.find('cas:Sofa', namespaces)
    sofa_string = sofa.get('sofaString')
    new_string = positional_insert(sofa_string, insertion, position)
    sofa.set('sofaString', new_string)

    tree = adjust_annotations(tree, namespaces, len(insertion), position)

    return tree


def sofa_string_delete(tree, namespaces, deletion_len, position):
    """Deletes chars in the sofaString, adjusting annotations accordingly.

    Args:
        tree (ElementTree object): tree whose sofaString and annotations will
            be adjusted
        namespaces (dict): namespace dictionary the tree uses
        deletion (int): amount of chars to delete
        position (positive int): position/slice at which
            the deletion takes place

    Returns:
        ElementTree object: tree with adjusted sofaString and annotations
    """

    sofa = tree.find('cas:Sofa', namespaces)
    sofa_string = sofa.get('sofaString')
    new_string = positional_delete(sofa_string, deletion_len, position)
    sofa.set('sofaString', new_string)

    tree = adjust_annotations(tree, namespaces, -deletion_len, position)

    return tree


def next_regex_sofa_coordinates(regex, tree, namespaces):

    start = 0
    while True:
        sofa = tree.find('cas:Sofa', namespaces)
        sofa_string = sofa.get('sofaString')
        match_ = re.search(regex, sofa_string[start:])
        if not match_:
            break

        start += match_.start()
        end = start + len(match_.group())
        yield start, end
        start = end - 5


def sofa_regex_delete(regex, tree, namespaces):

    for match_ in next_regex_sofa_coordinates(regex, tree, namespaces):
        tree = sofa_string_delete(
            tree,
            namespaces,
            match_[1]-match_[0],
            match_[0]
        )
        match_ = next_regex_sofa_coordinates(regex, tree, namespaces)

    return tree


def sofa_regex_replace(regex, insertion, tree, namespaces):

    for match_ in next_regex_sofa_coordinates(regex, tree, namespaces):
        tree = sofa_string_delete(
            tree,
            namespaces,
            match_[1]-match_[0],
            match_[0]
        )
        tree = sofa_string_insert(
            tree,
            namespaces,
            insertion,
            match_[0]
        )
        match_ = next_regex_sofa_coordinates(regex, tree, namespaces)

    return tree


def sofa_regex_replace_if(regex, capture, replacement, tree, namespaces):

    for match_ in next_regex_sofa_coordinates(regex, tree, namespaces):
        sofa = tree.find('cas:Sofa', namespaces)
        sofa_string = sofa.get('sofaString')
        new_string = (
            sofa_string[:match_[0]]
            + sofa_string[match_[0]:match_[1]].replace(capture, replacement)
            + sofa_string[match_[1]:]
        )
        sofa.set('sofaString', new_string)

    return tree
