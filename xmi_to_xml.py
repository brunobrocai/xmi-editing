import xml.etree.ElementTree as ET
import re
import xmi_conversion_util as xcu


ZEITUNG_PATTERN = " *[A-Z0-9]{3,}/.*?S.(\n| )[A-Z]?[0-9]+.*?\n?###"
PLENAR_PATTERN = " *[A-Z0-9]{3,}/.*Plenarprotokoll,.*[0-9]{4} ###"


def get_span(text, coordinates):
    """
    Takes a corpus string and a 2-tuple. Returns the slice
    of the 2-tuple if possible;
    otherwise prints an Error message and returns None.
    """

    try:
        span = text[coordinates[0]:(coordinates[1])]
        return span
    except TypeError:
        print("Error getting span.")
        return None


def text_from_xmi(filepath):
    """
    Extracts from the xmi the corpus that the annotations are based on.
    It is necessary to call this function if you want to output
    annotated text at some point.

    Parameters:
        filepath: The xmi file you want to open.
    Returns:
        The corpus as a string
    """

    # Open the XMI file
    tree = ET.parse(filepath)
    root = tree.getroot()

    text = root.find("{http:///uima/cas.ecore}Sofa").get('sofaString')

    return text


def find_split_indices(pattern, text):
    """
    Given a regex pattern, matches all occurences of that pattern
    in a string and lists the start and end indices of these occurences

    Args:
        pattern (str): python regex pattern
        text (str): string that is going to be matched

    Returns:
        list: 2d array of start and end indices of the matches
    """

    indices_end = [match.end() for match in re.finditer(pattern, text)]
    indices_begin = [match.start() for match in re.finditer(pattern, text)]

    return list(zip(indices_begin, indices_end))


def get_inbetween(tuples, last):
    """
    Given a list of indices, returns a similar list of indices indexing
    all text that the original list did not index, except the text before
    the first index

    Args:
        tuples (list): 2d array of start and end indices
        last (int): index of final char

    Returns:
        list: 2d array of start and end indices of all everything not in
            the original list (except anything before the first entry)
    """

    tuples_inbetween = []

    for i in range(len(tuples) - 1):
        start = tuples[i][1] + 1
        end = tuples[i + 1][0] - 1
        tuples_inbetween.append((start, end))

    try:
        tuples_inbetween.append((tuples[-1][1], last-1))
    except IndexError:
        print("IndexError with get_inbetween()")

    return tuples_inbetween


def narrow_tuples(tuples, text):
    """
    Given a list of 2-tuples of (begin and end) indices and a string to which
    these indices apply, narrows there tuples until they do no longer start
    or end with space, # or newline.

    Args:
        tuples (list): 2d array of start and end indices
        text (string): string that the tuples-list applies to

    Returns:
        list: 2d array of start and end indices
    """

    new_tuples = []
    for tuple in tuples:
        begin = tuple[0]
        end = tuple[1]

        whitespace = [' ', '#', '\n']

        while text[begin] in whitespace:
            begin += 1
        while text[end] in whitespace:
            end -= 1
        try:
            end += 1
        except IndexError:
            pass

        new_tuples.append((begin, end))

    return new_tuples


def list_moralizations_from_xmi(filepath):
    """
    Takes an xmi file and returns a list with 2-tuples.
    The tuples mark the beginning and ending of spans that were
    categorized as "moralizing speechacts".

    Parameters:
        filepath: The xmi file you want to open.
    Returns:
        List of 2-tuples.
    """

    # Open the XMI file
    tree = ET.parse(filepath)
    root = tree.getroot()

    span_list = root.findall("{http:///custom.ecore}Span")

    # Get all moralizing instances
    moral_spans_list = []
    for span in span_list:
        category = span.get('KAT1MoralisierendesSegment')

        if category:
            if category != "Keine Moralisierung":
                data_dict = {
                    "Coordinates":
                        (int(span.get("begin")), int(span.get("end"))),
                    "Category":
                        category
                }
                moral_spans_list.append(data_dict)

    return moral_spans_list


def list_obj_moral_from_xmi(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    span_list = root.findall("{http:///custom.ecore}Span")

    # Get all moralizing instances
    morals_list = []
    for span in span_list:
        category = span.get('Moralwerte')

        if category:
            data_dict = {
                "Coordinates":
                    (int(span.get("begin")), int(span.get("end"))),
                "Category":
                    category
            }
            morals_list.append(data_dict)

    return morals_list


def ranges_overlap(range1, range2):
    """
    Checks whether two 2-tuples overlap at least by one element,
    assuming slicing. This means that the end index is not counted.
    """
    start1, end1 = range1
    start2, end2 = range2

    return end1 > start2 and end2 > start1


create_xml_element


if __name__ == "__main__":
    text = text_from_xmi('test.xmi')
    metas_tuples = find_split_indices(ZEITUNG_PATTERN, text)
    spans_tuples = get_inbetween(metas_tuples, len(text))

    metas_narrow = narrow_tuples(metas_tuples, text)
    spans_narrow = narrow_tuples(spans_tuples, text)

    moralizations = list_moralizations_from_xmi('test.xmi')
    for element in moralizations:
        element['Coordinates'] = narrow_tuples([element['Coordinates']], text)[0]

    sm_associations = xcu.protagonist_associations(spans_narrow, moralizations)

    obj_morals = list_obj_moral_from_xmi('test.xmi')
    mom_associations = xcu.protagonist_associations(sm_associations.values(), obj_morals)

    root = ET.Element('root')

    xml_text = text
    for morals in mom_associations.items():
        xml_text = 
