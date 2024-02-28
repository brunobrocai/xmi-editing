import xml.etree.ElementTree as ET
import xmi_handling as xh


FILE = 'Gerichtsurteile-neg-AW-neu-optimiert-BB_optimized.xmi'

# Token Test
tree = ET.parse(FILE)
namespaces = xh.get_namespaces(FILE)

corpus = xh.get_sofa_string(tree, namespaces)
tokens = tree.findall('type5:Token', namespaces)

for token in tokens:
    trange = (
        int(token.get('begin')),
        int(token.get('end'))
    )
    print(corpus[trange[0]:trange[1]], end='')
    print('|', end='')
