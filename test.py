import xmi_handling as xh
import xml.etree.ElementTree as ET

# Token Test
tree = ET.parse('Gerichtsurteile-neg-AW-neu-optimiert-BB_optimized.xmi')
namespaces = xh.get_namespaces('Gerichtsurteile-neg-AW-neu-optimiert-BB_optimized.xmi')

corpus = xh.get_sofa_string(tree, namespaces)
tokens = tree.findall('type5:Token', namespaces)

for token in tokens:
    trange = (
        int(token.get('begin')),
        int(token.get('end'))
    )
    print(corpus[trange[0]:trange[1]], end='')
    print('|', end='')

