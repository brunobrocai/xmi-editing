
def rename_attribute(tree, old_attribute_name, new_attribute_name):
    """Renames a specified attribute
    in all occurences in all elements of a tree.

    Args:
        tree (ElementTree object): ElementTree tree whose elements are checked
            for attributes to rename
        old_attribute_name (str): self-explainatory
        new_attribute_name (str): self-explainatory

    Returns:
        ElementTree object: tree with renamed attributes
    """

    root = tree.getroot()

    for element in root.iter():
        old_value = element.get(old_attribute_name)
        if old_value is not None:
            element.set(new_attribute_name, old_value)
            element.attrib.pop(old_attribute_name, None)

    return tree


def rename_attribute_value(tree, attribute_name, old_value, new_value):
    """Renames a specific value of a specific attribute
    in all occurences in all elements of a tree.

    Args:
        tree (ElementTree object): ElementTree tree whose elements are checked
            for attributes to rename
        attribute_name (str): attribute whose values should be changed
        old_value (str): self-explainatory
        new_value (str): self-explainatory

    Returns:
        ElementTree object: tree with renamed attribute values
    """

    root = tree.getroot()

    for element in root.iter():
        if (
            attribute_name in element.attrib
            and element.get(attribute_name) == old_value
        ):
            element.set(attribute_name, new_value)

    return tree
