def inside_of_list(coord_list_outer, coord_inner):
    """
    Checks whether the specific coordinates
    are inside any of the coordinates on the list
    Returns the first match, or None if there is no match.
    """

    for coord_outer in coord_list_outer:
        if inside_of(coord_outer, coord_inner):
            return coord_outer
    return False


def inside_of(coord_outer, coord_inner):
    """
    Checks whether the specific coordinates
    are inside any of the coordinates on the list
    Returns the first match, or None if there is no match.
    """

    if ((coord_outer[0] <= coord_inner[0])
            and (coord_inner[1] <= coord_outer[1])):
        return True
    return False


def sentence_associations(category, tree, namespaces):

    sentences = tree.findall('type5:Sentence', namespaces)
    annotations = [
        span for span in tree.findall('custom:Span', namespaces)
        if span.get(category)
    ]

    associations_dict = {
        sentence: [] for sentence in sentences
    }
    for sentence in sentences:
        sentence_range = (
            int(sentence.get('begin')), int(sentence.get('end'))
        )
        for annotation in annotations:
            moral_range = (
                int(annotation.get('begin')), int(annotation.get('end'))
            )
            if inside_of(sentence_range, moral_range):
                associations_dict[sentence].append(annotation)

    return associations_dict


def get_span(text, coordinates):
    try:
        span = text[coordinates[0]:(coordinates[1])]
        return span
    except TypeError:
        print("Error getting span.")
        return None


def narrow_coords(coordinates, text, whitespace=' \n\t'):

    start = coordinates[0]
    end = coordinates[1]

    if start > len(text):
        start = len(text) - 1
    if end > len(text):
        end = len(text)

    while text[start] in whitespace and start < len(text) - 1:
        start += 1
    while text[end-1] in whitespace:
        end -= 1

    return (start, end)


def get_coords(element):
    try:
        coords = [int(element.get('begin')), int(element.get('end'))]
        return coords
    except Exception as e:
        print(e)
        return None
