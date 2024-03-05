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
        metadata_dict['begin'] = str(start)
        metadata_dict['end'] = str(end + 1)
        tree = ed.add_element(
            tree,
            '{'+namespaces['custom']+'}Metadata',
            metadata_dict,
            position
        )
        position += 1  # Next element gets added after the last one

    return tree


def correct_sentences(tree, namespaces, sentence_begin=2):
    """Corrects the sentences in a tree.

    Args:
        tree (ElementTree object): tree to be corrected
        namespaces (dict): namespace dictionary the tree uses

    Returns:
        ElementTree object: tree with corrected sentences
    """

    sentences = tree.findall('type5:Sentence', namespaces)
    metadata = tree.findall('custom:Metadata', namespaces)
    text = xh.get_sofa_string(tree, namespaces)
    used_sentences = []
    sentences_to_add = []

    for index, metainfo in enumerate(metadata):
        start = int(metainfo.get('begin'))
        for sentence in sentences:
            if start == int(sentence.get('begin')):
                try:
                    end = int(metadata[index+1].get('begin')) - 1
                except IndexError:
                    end = len(text) - 1
                new_coords = xcu.narrow_coords((start, end), text)
                sentence.set('end', str(new_coords[1]))
                used_sentences.append(sentence)
                break
        else:
            try:
                end = int(metadata[index+1].get('begin')) - 1
            except IndexError:
                end = len(text) - 1
            new_coords = xcu.narrow_coords((start, end), text)
            sentences_to_add.append((
                '{'+namespaces['type5']+'}Sentence',
                {
                    '{'+namespaces['xmi']+'}id': str(99),
                    'sofa': '1',
                    'begin': str(start),
                    'end': str(end)
                },
                sentence_begin+index
            ))

    for sentence in sentences:
        if sentence not in used_sentences:
            tree.getroot().remove(sentence)

    for sentence in sentences_to_add:
        tree = ed.add_element(tree, *sentence)

    return tree


def delete_keine_moral(tree, namespaces):
    root = tree.getroot()
    moral_assocs = xcu.sentence_associations(
        'KAT1MoralisierendesSegment', tree, namespaces
    )

    for sentence, annos in moral_assocs.items():
        moralizations = [
            anno for anno in annos
            if anno.get('KAT1MoralisierendesSegment') != 'Keine Moralisierung'
        ]
        nonmorals = [
            anno for anno in annos
            if anno.get('KAT1MoralisierendesSegment') == 'Keine Moralisierung'
        ]

        if len(nonmorals) > 0 and len(moralizations) == 0:
            position = xh.get_position_before_element(
                tree, nonmorals[0].tag, nonmorals[0].attrib
            )
            new_element_dict = nonmorals[0].attrib.copy()
            new_element_dict['begin'] = sentence.get('begin')
            new_element_dict['end'] = sentence.get('end')
            tree = ed.add_element(
                tree, '{'+namespaces['custom']+'}Span',
                new_element_dict, before=position
            )
        for nonmoral in nonmorals:
            root.remove(nonmoral)

    return tree


def include_punctuation(tree, namespaces):
    text = xh.get_sofa_string(tree, namespaces)
    whitespace = ' \n\t'
    sentence_wide_annos = []

    for annotation in tree.findall('custom:Span', namespaces):
        if annotation.get('KAT1MoralisierendesSegment'):
            sentence_wide_annos.append(annotation)
        elif annotation.get('KommunikativeFunktion'):
            sentence_wide_annos.append(annotation)

    for annotation in sentence_wide_annos:
        annotation_end = int(annotation.get('end'))
        while text[annotation_end] not in whitespace:
            annotation_end += 1
        annotation.set('end', str(annotation_end))

    return tree


def element_is_moralization(element):
    attempt = element.get('KAT1MoralisierendesSegment')
    return attempt == 'Moralisierung'


def remove_double_moralizations(tree, namespaces):
    annotations = [
        span for span in tree.findall('custom:Span', namespaces)
        if span.get('KAT1MoralisierendesSegment')
    ]
    root = tree.getroot()
    span_set = set()
    for annotation in annotations:
        coords = tuple(xcu.get_coords(annotation))
        if coords in span_set:
            duplicates = [
                span for span in tree.findall('custom:Span', namespaces)
                if span.get('begin') == str(coords[0])
                and span.get('end') == str(coords[1])
            ]
            non_generic = [
                duplicate for duplicate in duplicates
                if not element_is_moralization(duplicate)
            ]
            for duplicate in duplicates:
                if (
                    element_is_moralization(duplicate)
                    and len(non_generic) > 0
                ):
                    root.remove(duplicate)
        span_set.add(coords)

    return tree
