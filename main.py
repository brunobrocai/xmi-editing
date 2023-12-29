import xmi_handling as xh
import sofa_editing as se
import element_editing as ed


tree, root = xh.parse_xmi('test.xmi')
namespaces = xh.get_namespaces('test.xmi')

tree = ed.rename_attribute_value(
    tree,
    'Protagonistinnen',
    'Adresassat:in',
    'Adressat:in'
)

xh.default_write(tree, 'output.xmi')
