from automatic_editing import (
    xmi_handling as xh,
    sofa_editing as se,
    element_editing as ed,
    complex_operations as co,
    regexes
)


GENRE = 'Leserbriefe-pos-BB-neu-optimiert-RR'
FILE_ = f'/home/bruno/Desktop/Databases/Moralization/Zeitungstexte/{GENRE}.xmi'


tree, root = xh.parse_xmi(FILE_)
namespaces = xh.get_namespaces(FILE_)

tree = ed.rename_annotation(
    tree, 'Protagonistinnen', 'Adresassat:in', 'Adressat:in'
)

tree = se.sofa_regex_replace_if(
    regexes.ZEITUNG_PATTERN,
    "###",
    "+++",
    tree,
    namespaces
)

tree = se.sofa_regex_replace(
    " ###",
    '',
    tree,
    namespaces
)

tree = se.sofa_regex_replace(
    "#",
    '',
    tree,
    namespaces
)


before = xh.get_position_before_category(
    tree, '{'+namespaces['custom']+'}Span')

tree = co.add_metadata_tag(
    regexes.ZEITUNG_PATTERN_EDIT,
    {
        '{'+namespaces['xmi']+'}id': '1',
        'sofa': '1'
    },
    tree,
    namespaces,
    before
)

tree = co.correct_sentences(tree, namespaces)

tree = ed.push_out_annotations(
    tree, namespaces,
    'custom:Metadata',
    ['custom:Span']
)
tree = ed.push_out_annotations(
    tree, namespaces,
    'custom:Metadata',
    ['custom:Span']
)
tree = co.delete_keine_moral(
    tree, namespaces
)
tree = ed.push_out_annotations(
    tree, namespaces,
    'custom:Metadata',
    ['custom:Span']
)

tree = ed.narrow_all_tag_cords('custom:Span', tree, namespaces)
tree = co.include_punctuation(tree, namespaces)
tree = co.remove_double_moralizations(tree, namespaces)

tree = ed.delete_empty_tags(tree, namespaces)
tree = ed.delete_whitespace_tokens(tree, namespaces)
tree = ed.delete_overlap_tokens(tree, namespaces)
tree = ed.delete_outside_sentence(tree, namespaces)

tree = ed.update_ids(tree, namespaces)
tree = ed.set_sofa_one(tree, namespaces)
tree = ed.delete_group_annotation(tree, namespaces)

xh.default_write(tree, f'{GENRE}_optimized.xmi')
