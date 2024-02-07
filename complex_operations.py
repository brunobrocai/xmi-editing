import element_editing as ed
import xmi_handling as xh
import sofa_editing as se
import xmi_conversion_util as xcu


def add_metadata_tag(
    pattern, metadata_dict, tree, namespaces, position=None
):
    """Adds a metadata tag to the tree.

    Args:
        pattern (str): pattern to be searched for
        metadata_dict (dict): dictionary of metadata to be added
        tree (ElementTree object): tree to which the metadata should be added
        namespaces (dict): namespace dictionary the tree uses

    Returns:
        ElementTree object: tree with added metadata
    """

    sofa_text = xh.get_sofa_string(tree, namespaces)

    for coords in se.next_regex_sofa_coordinates(pattern, tree, namespaces):
        start, end = xcu.narrow_coords(coords, sofa_text)
        metadata_dict['start'] = str(start)
        metadata_dict['end'] = str(end)
        tree = ed.add_element(
            tree,
            '{'+namespaces['custom']+'}Metadata',
            metadata_dict,
            position
        )
        position += 1  # Next element gets added after the last one

    return tree


def correct_sentences(tree, namespaces):
    """Corrects the sentences in a tree.

    Args:
        tree (ElementTree object): tree to be corrected
        namespaces (dict): namespace dictionary the tree uses

    Returns:
        ElementTree object: tree with corrected sentences
    """

    sentences = tree.findall('type5:Sentence', namespaces)
    metadata = tree.findall('custom:Metadata', namespaces)

    for metainfo in metadata:
        start = int(metainfo.get('start'))
        for sentence in sentences:
            if not start == int(sentence.get('begin')) and end <= int(sentence.get('end')):
                sentence.set('begin', str(start))
                sentence.set('end', str(end))

    for sentence in sentences:
        tree = add_metadata_tag(
            sentence,
            {
                '{'+namespaces['xmi']+'}id': '1',
                'sofa': '1'
            },
            tree,
            namespaces
        )

    return tree

