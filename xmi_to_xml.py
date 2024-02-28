import sofa_editing as se
import xmi_handling as xh


def retrieve_labels(items):
    irrelevant_list = [
        ':id',
        'sofa',
        'begin',
        'end'
    ]
    relevant_items = []
    for item in items:
        relevant = True
        for end in irrelevant_list:
            if item[0].endswith(end):
                relevant = False
        if relevant:
            relevant_items.append(item)


def tag_moralizations(tree, namespaces):
    root = tree.getroot()
    custom_list = root.findall('custom:Span', namespaces)
    for custom in custom_list:
        moraliz = custom.get('KAT1MoralisierendesSegment')
        if moraliz and moraliz != 'Keine Moralisierung':
            insertion_begin = f'<Moralization label="{moraliz}">'
            insertion_end = '</Moralization>'
            tree = se.sofa_string_insert(
                tree, namespaces, insertion_begin, int(custom.get('begin'))
            )
            tree = se.sofa_string_insert(
                tree, namespaces, insertion_end, int(custom.get('end'))
            )
    return tree


def tag_subj_values(tree, namespaces):
    root = tree.getroot()
    custom_list = root.findall('custom:Span', namespaces)
    for custom in custom_list:
        moraliz = custom.get('KAT2Subjektive_Ausdrcke')
        if moraliz:
            insertion_begin = (
                f'<MoralValue type="subjective expression"'
                f'label="{moraliz}">'
            )
            insertion_end = '</MoralValue>'
            tree = se.sofa_string_insert(
                tree, namespaces, insertion_begin, int(custom.get('begin'))
            )
            tree = se.sofa_string_insert(
                tree, namespaces, insertion_end, int(custom.get('end'))
            )
    return tree


if __name__ == "__main__":
    FILE = 'text.xmi'
    tree, root = xh.parse_xmi(FILE)
    namespaces = xh.get_namespaces(FILE)

    tree = tag_moralizations(tree, namespaces)
    tree = tag_subj_values(tree, namespaces)

    sofa = tree.find('cas:Sofa', namespaces)
    sofa_string = sofa.get('sofaString')
    print(sofa_string)
