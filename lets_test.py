from xml.etree import ElementTree as ET
from automatic_editing import xmi_handling as xh
from automatic_editing import xmi_conversion_util as xcu


def print_all_spans(span_list, text):
    for span in span_list:
        start = int(span.get('begin'))
        end = int(span.get('end'))
        print(xcu.get_span(text, (start, end)))
        print('-'*30)


tree, root = xh.parse_xmi('output.xmi')
namespaces = xh.get_namespaces('output.xmi')
text = xh.get_sofa_string(tree, namespaces)

sents = tree.findall('type5:Sentence', namespaces)
meta = tree.findall('custom:Metadata', namespaces)
morals = tree.findall('custom:Morals', namespaces)
morals = [m for m in morals if m.get('KAT1MoralisierendesSegment')]


def print_dups(spans, text):
    dups = []
    uniqs = set()
    for sent in spans:
        span_range = (int(sent.get('begin')), int(sent.get('end')))
        spantext = xcu.get_span(text, span_range)
        if spantext not in uniqs:
            uniqs.add(spantext)
        else:
            dups.append(spantext)
            print('Duplicate sentence found.')
    for dup in dups:
        print(dup)
        print('-'*30)


def print_tokens(file):
    tree = ET.parse(file)
    namespaces = xh.get_namespaces(file)

    corpus = xh.get_sofa_string(tree, namespaces)
    tokens = tree.findall('type5:Token', namespaces)

    for token in tokens:
        trange = (
            int(token.get('begin')),
            int(token.get('end'))
        )
        print(corpus[trange[0]:trange[1]], end='')
        print('|', end='')


print_all_spans(sents, text)
