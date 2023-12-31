
def rename_attribute(tree, old_attribute_name, new_attribute_name):
    root = tree.getroot()

    for element in root.iter():
        old_value = element.get(old_attribute_name)
        if old_value is not None:
            element.set(new_attribute_name, old_value)
            element.attrib.pop(old_attribute_name, None)

    return tree


def rename_attribute_value(tree, attribute_name, old_value, new_value):
    root = tree.getroot()

    for element in root.iter():
        if (
            attribute_name in element.attrib
            and element.get(attribute_name) == old_value
        ):
            element.set(attribute_name, new_value)

    return tree
