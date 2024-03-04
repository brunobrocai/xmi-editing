import xml.etree.ElementTree as ET


def xmi_filename_extension(filepath, raise_err=True):
    """Checks a filename/path for .xmi filename extension."""
    if not filepath.endswith('.xmi'):
        if raise_err:
            raise ValueError(
                f'{filepath} is not an xmi according to filename extension.'
            )
        return False
    return True


def parse_xmi(filepath):
    """Gets tree and root of an xmi file."""
    xmi_filename_extension(filepath)
    tree = ET.parse(filepath)
    root = tree.getroot()

    return tree, root


def get_namespaces(filepath):
    """Creates a namespace dict for an xmi file."""
    xmi_filename_extension(filepath)
    namespaces = {
        prefix: uri for _, (prefix, uri)
        in ET.iterparse(filepath, events=['start-ns'])
    }
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    return namespaces


def default_write(tree, filepath):
    """Creates an xmi file from a tree with default params for the project."""
    tree.write(filepath,
               encoding="utf-8",
               xml_declaration=True,
               method='xml')


def get_sofa_string(tree, namespaces):
    """Gets the sofaString from an xmi file."""
    return tree.find('cas:Sofa', namespaces).get('sofaString')


def get_position_before_category(tree, element):

    root = tree.getroot()

    for i, child in enumerate(root):
        if child.tag == element:
            return i

    return None


def get_position_before_element(tree, element, attribute_dict):

    root = tree.getroot()

    for i, child in enumerate(root):
        if child.tag == element:
            child_attribs = child.attrib
            hit = True
            for key in attribute_dict:
                try:
                    if child_attribs[key] != attribute_dict[key]:
                        hit = False
                except KeyError:
                    hit = False
            if hit:
                return i

    return None


def get_everything(filepath):
    tree, root = parse_xmi(filepath)
    namespaces = get_namespaces(filepath)

    return tree, root, namespaces
