import xml.etree.ElementTree as ET
import xmi_conversion_util as xcu
import xmi_handling as xh


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


def set_sofa_one(tree, namespaces):
    tree.find('cas:Sofa', namespaces).set('{'+namespaces['xmi']+'}id', '1')
    return tree


def is_inside_coords(coords, possible_inside):
    inside = [False, False, False]  # begin_inside, end_inside, wrapped_outside
    if possible_inside[0] > coords[1]:
        return False
    if possible_inside[0] <= coords[1] and possible_inside[0] >= coords[0]:
        inside[0] = True
    if possible_inside[1] <= coords[1] and possible_inside[1] >= coords[0]:
        inside[1] = True
    if possible_inside[0] < coords[0] and possible_inside[1] > coords[1]:
        inside[2] = True
    return inside


def push_out_annotations(tree, namespaces, bouncer_tag, annotation_tags):

    # We need all of this later
    bouncers = tree.findall(bouncer_tag, namespaces)
    annotations = []
    for tag in annotation_tags:
        annotations.extend(tree.findall(tag, namespaces))
    text = xh.get_sofa_string(tree, namespaces)
    root = tree.getroot()

    # Sort annotations by begin attribute
    annotations.sort(key=lambda x: int(x.get('begin')))
    bouncers.sort(key=lambda x: int(x.get('begin')))

    for bouncer in bouncers:
        bouncer_range = (int(bouncer.get('begin')), int(bouncer.get('end')))
        for annotation in annotations:
            annotation_range = [
                int(annotation.get('begin')), int(annotation.get('end'))
            ]
            inside = is_inside_coords(bouncer_range, annotation_range)

            # We don't need to check the rest of the annotations
            # if the annotations come after the bouncer (they are sorted)
            if inside is False:
                break

            # If the annotation wraps arround the bouncer, we must split it
            if inside[2]:
                tag = annotation.tag
                attrib = annotation.attrib.copy()
                position = xh.get_position_before_element(
                    tree, tag, attrib
                )
                attrib['begin'] = str(bouncer_range[1])
                tree = add_element(
                    tree, tag, attrib, position+1
                )
                annotation.set('end', str(bouncer_range[0] - 1))

            # Push the annotations out of bouncer range where possible
            if inside[0] and inside[1]:
                root.remove(annotation)
            if inside[0] and not inside[1]:
                annotation_range[0] = bouncer_range[1]
                new_coords = xcu.narrow_coords(annotation_range, text)
                annotation.set('begin', str(new_coords[0]))
            if inside[1] and not inside[0]:
                annotation_range[1] = bouncer_range[0] - 1
                new_coords = xcu.narrow_coords(annotation_range, text)
                annotation.set('end', str(new_coords[1]))

    return tree


def narrow_all_tag_cords(tag, tree, namespaces):
    text = xh.get_sofa_string(tree, namespaces)
    root = tree.getroot()

    for element in root.findall(tag, namespaces):
        if 'begin' in element.attrib and 'end' in element.attrib:
            begin = int(element.get('begin'))
            end = int(element.get('end'))
            new_coords = xcu.narrow_coords((begin, end), text)
            element.set('begin', str(new_coords[0]))
            element.set('end', str(new_coords[1]))

    return tree


def delete_empty_tags(tree, namespaces):
    tag_list = tree.findall('custom:Span', namespaces)
    tag_list += tree.findall('custom:Metadata', namespaces)
    tag_list += tree.findall('type5:Sentence', namespaces)
    tag_list += tree.findall('type5:Token', namespaces)

    root = tree.getroot()

    for element in tag_list:
        try:
            if (
                int(element.get('begin')) >= int(element.get('end'))
                or int(element.get('begin')) < 0
                or int(element.get('end')) < 0
            ):
                # print(element.tag, element.get('begin'), element.get('end'))
                root.remove(element)
        except ValueError:
            pass

    return tree


def delete_overlap_tokens(tree, namespaces):
    token_list = tree.findall('type5:Token', namespaces)
    to_delete = set()
    root = tree.getroot()

    for i, token in enumerate(token_list):
        token_range = (int(token.get('begin')), int(token.get('end')))
        if token_range[1] - token_range[0] <= 2:
            for prev_token in token_list[:i]+token_list[i+1:]:
                if (
                        int(prev_token.get('end')) >= token_range[1]
                        and int(prev_token.get('begin')) <= token_range[0]
                ):
                    to_delete.add(token)

    for token in to_delete:
        root.remove(token)

    return tree


def delete_outside_sentence(tree, namespaces):
    tag_list = tree.findall('custom:Span', namespaces)
    tag_list += tree.findall('custom:Metadata', namespaces)
    tag_list += tree.findall('type5:Token', namespaces)
    sentences = tree.findall('type5:Sentence', namespaces)

    root = tree.getroot()

    for tag in tag_list:
        inside = False
        for sentence in sentences:
            if int(tag.get('begin')) >= int(sentence.get('begin')) and int(tag.get('end')) <= int(sentence.get('end')):
                inside = True
                break
        if not inside:
            print(tag.tag, tag.get('begin'), tag.get('end'))
            root.remove(tag)

    return tree


def delete_group_annotation(tree, namespaces):
    annos = tree.findall('custom:Span', namespaces)
    protagonists = [anno for anno in annos if anno.get('Protagonistinnen3')]

    for protagonist in protagonists:
        protagonist.attrib.pop('Protagonistinnen3')

    return tree


def delete_whitespace_tokens(tree, namespaces):
    tokens = tree.findall('type5:Token', namespaces)
    root = tree.getroot()
    sofa_string = xh.get_sofa_string(tree, namespaces)

    for token in tokens:
        if sofa_string[
            int(token.get('begin')):
            int(token.get('end'))
        ] == ' ':
            root.remove(token)

    return tree
