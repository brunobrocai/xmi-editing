import xmi_handling as xh
import sofa_editing as se
import element_editing as ed
import complex_operations as co
import regexes


tree, root = xh.parse_xmi('test.xmi')
namespaces = xh.get_namespaces('test.xmi')

# tree = se.sofa_regex_replace_if(
#     regexes.ZEITUNG_PATTERN,
#     "###",
#     "+++++",
#     tree,
#     namespaces
# )

# tree = se.sofa_regex_replace(
#     "#",
#     '',
#     tree,
#     namespaces
# )

# xh.default_write(tree, 'output.xmi')

before = xh.get_position_before_element(
    tree, '{'+namespaces['custom']+'}Span',
    {'{'+namespaces['xmi']+'}Span': '150518'})

tree = co.add_metadata_tag(
    regexes.ZEITUNG_PATTERN,
    {
        '{'+namespaces['xmi']+'}id': '1',
        'sofa': '1'
    },
    tree,
    namespaces,
    before
)


tree = ed.update_ids(tree, namespaces)



xh.default_write(tree, 'output.xmi')
