import xml.etree.ElementTree as ET


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


def rename_annotation(tree, attribute_name, old_value, new_value):
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


def change_begin_end(tree, attribute_id, new_begin, new_end):
    """Changes the begin and end attributes of a specific annotation.

    Args:
        tree (ElementTree object): ElementTree tree whose elements are checked
            for attributes to rename
        attribute_id (str): ID of the annotation whose begin and end attributes
            should be changed
        new_begin (str): new value for the begin attribute
        new_end (str): new value for the end attribute

    Returns:
        ElementTree object: tree with changed begin and end attributes
    """

    root = tree.getroot()

    for element in root.iter():
        if (
            'id' in element.attrib
            and element.get('id') == attribute_id
        ):
            element.set('begin', str(new_begin))
            element.set('end', str(new_end))

    return tree


def remove_attribute(tree, attribute_name):
    """Removes a specified attribute
    in all occurences in all elements of a tree.

    Args:
        tree (ElementTree object): ElementTree tree whose elements are checked
            for attributes to remove
        attribute_name (str): self-explainatory

    Returns:
        ElementTree object: tree with removed attributes
    """

    root = tree.getroot()

    for element in root.iter():
        if attribute_name in element.attrib:
            element.attrib.pop(attribute_name, None)

    return tree


def add_element(tree, element_name, attributes, before=None):
    """Adds an element to the tree.

    Args:
        tree (ElementTree object): ElementTree tree to which the element
            should be added
        element_name (str): name of the element to be added
        attributes (dict): dictionary of attributes the element should have

    Returns:
        ElementTree object: tree with the added element
    """

    root = tree.getroot()
    new_element = ET.Element(element_name, attributes)
    new_element.tail = '\n    '
    if before is None:
        root.append(new_element)
    else:
        root.insert(before, new_element)

    return tree


def update_ids(tree, namespaces):
    """Updates the IDs of all annotations in the tree.

    Args:
        tree (ElementTree object): ElementTree tree whose annotations
            should be updated

    Returns:
        ElementTree object: tree with updated IDs
    """

    root = tree.getroot()
    id_counter = 10

    for element in root.iter():
        if '{'+namespaces['xmi']+'}id' in element.attrib:
            element.set('{'+namespaces['xmi']+'}id', str(id_counter))
            id_counter += 10

    index = tree.find('cas:View', namespaces)
    new_members = ' '.join([str(x) for x in range(10, id_counter, 10)])
    index.set('members', new_members)

    return tree
