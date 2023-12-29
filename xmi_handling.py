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
    namespaces = dict([node for _, node in ET.iterparse(
        filepath,
        events=['start-ns']
    )])
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    return namespaces


def default_write(tree, filepath):
    """Creates an xmi file from a tree with default params for the project."""
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
