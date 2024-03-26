import time
from automatic_editing import xmi_handling as xh
from automatic_editing import xmi_conversion_util as xcu


def get_moral_prompt():
    new_annotation = 'XXXXXXXXX'
    while new_annotation not in {'W', 'K', 'E', 'I'}:
        if new_annotation != 'XXXXXXXXX':
            print('You did not enter a valid option.')

        print(
            'You have the following options:\n',
            'If the span is "Moralisierung Weltwissen", type     W\n',
            'If the span is "Moralisierung Kontext", type        K\n',
            'If the span is "Moralisierung explizit", type       E\n',
            'If the span is "Moralisierung interpretativ", type  I\n'
        )

        new_annotation = input("What type of moralization is present here? ")

    return new_annotation


def get_context(element, tree, namespaces):
    sentences = tree.findall('type5:Sentence', namespaces)
    element_coords = xcu.get_coords(element)

    for sentence in sentences:
        sentence_coords = xcu.get_coords(sentence)
        if xcu.inside_of(sentence_coords, element_coords):
            return sentence

    return None


def get_confirmation():
    while True:
        user_input = input('Confirm by typing "Y", and cancel by typing "n". ')

        match user_input:
            case 'Y':
                print('Confirmed!')
                return True
            case 'n':
                print('Cancelled!')
                return False
            case _:
                print('Not a valid input. Please try again.\n')
                continue


def input_to_annotation(letter):
    match letter:
        case 'W':
            return 'Moralisierung Weltwissen'
        case 'K':
            return 'Moralisierung Kontext'
        case 'E':
            return 'Moralisierung explizit'
        case 'I':
            return 'Moralisierung interpretativ'
        case _:
            raise ValueError('Could not handle annotation input string.')


def sleepif(boolean, waittime):
    if boolean:
        time.sleep(waittime)


def prompt_moralizations(filepath, wait=True):

    while True:
        tree, _, namespaces = xh.get_everything(filepath)
        sofa_string = xh.get_sofa_string(tree, namespaces)
        annotations = tree.findall('custom:Span', namespaces)

        faulty_moralizations = [
            annotation for annotation in annotations
            if annotation.get('KAT1MoralisierendesSegment') == "Moralisierung"
        ]

        if len(faulty_moralizations) < 1:
            print(f"Done with {filepath}!")
            break

        next_issue = faulty_moralizations[0]
        issue_coords = xcu.get_coords(next_issue)
        print('Found a span whose moralization type was not specified.\n')
        print(
            'The span is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, issue_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        context = get_context(next_issue, tree, namespaces)
        context_coords = xcu.get_coords(context)
        print(
            'The entire context is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, context_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        user_input = get_moral_prompt()
        translation = input_to_annotation(user_input)

        sleepif(wait, 0.2)

        print(
            f'\nYour input was {user_input}.',
            f'This corresponds to "{translation}".',
            'Please make sure this is correct.\n'
        )

        confirmation = get_confirmation()

        sleepif(wait, 0.2)

        if confirmation:
            next_issue.set('KAT1MoralisierendesSegment', translation)
            xh.default_write(tree, filepath)
            print('Correction written to file!\n')

        else:
            print('Nothing was changed.')
            print('You will be prompted to re-do the annotation.\n')

        print('-' * 70, '\n')
        sleepif(wait, 2)


def protagonist_tuple(element):
    protagonist = (
        bool(element.get('Protagonistinnen')),
        bool(element.get('Protagonistinnen2')),
    )
    return protagonist


def missing_annotation(protagonist_tuple):
    if any(protagonist_tuple):
        if not all(protagonist_tuple):
            return True
    return False


def input_to_protagonist_anno(letter, category):
    if category == 0:
        match letter:
            case 'A':
                return 'Adressat:in'
            case 'B':
                return 'Benefizient:in'
            case 'F':
                return 'Forderer:in'
            case 'M':
                return 'Malefizient:in'
            case 'KB':
                return 'Kein Bezug'
            case _:
                raise ValueError('Could not handle annotation input string.')
    match letter:
        case 'sG':
            return 'soziale Gruppe'
        case 'Ist':
            return 'Institution'
        case 'Ivd':
            return 'Individuum'
        case 'Mn':
            return 'Mensch'
        case 'O':
            return 'OTHER'
        case _:
            raise ValueError('Could not handle annotation input string.')


def get_protagonist_prompt(protagonist_tuple):
    categories = (
        ('Protagonistinnen', 'Rolle'),
        ('Protagonistinnen2', 'Gruppe')
    )
    valid_letters = ({'A', 'B', 'F', 'M', 'KB'}, {'sG', 'Ist', 'Ivd', 'Mn', 'O'})
    new_annotation = 'XXXXXXXXX'
    for i, category in enumerate(protagonist_tuple):
        if not category:
            print(f'Label {categories[i][1]} is missing.')
            new_annotation = 'XXXXXXXXX'
            while new_annotation not in valid_letters[i]:
                if new_annotation != 'XXXXXXXXX':
                    print('You did not enter a valid option.')

                print(
                    'You have the following options:'
                )
                for letter in valid_letters[i]:
                    print(f'If the span is "{input_to_protagonist_anno(letter, i)}", type {letter}')

                new_annotation = input("What type of protagonist is present here? ")
    return new_annotation


def get_possible_malefiz():
    valid_letters = {'A', 'B', 'F', 'M', 'KB'}
    new_annotation = 'XXXXXXXXX'
    while new_annotation not in valid_letters:
        if new_annotation != 'XXXXXXXXX':
            print('You did not enter a valid option.')
        print(
            'Consider whether the label might have some relevance for the moralization. '
            'Specifically, it could be a "Malefizient:in".\n'
        )
        print(
            'You have the following options:'
        )
        for letter in valid_letters:
            print(
                f'If the span is "{input_to_protagonist_anno(letter, 0)}", type {letter}'
            )
        print(
            '(If you think the label "Kein Bezug" is correct, '
            'type KB and nothing will be changed.)\n'
        )
        new_annotation = input("What type of protagonist is present here? ")
    return new_annotation



def prompt_missing(filepath, wait=True):

    while True:
        tree, _, namespaces = xh.get_everything(filepath)
        sofa_string = xh.get_sofa_string(tree, namespaces)
        annotations = tree.findall('custom:Span', namespaces)

        faulty_moralizations = [
            annotation for annotation in annotations
            if missing_annotation(protagonist_tuple(annotation))
        ]

        if len(faulty_moralizations) < 1:
            print(f"Done with {filepath}!")
            break

        next_issue = faulty_moralizations[0]
        issue_coords = xcu.get_coords(next_issue)
        print('Found a protagonist with missing annotations.\n')
        print(
            'The protagonist span is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, issue_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        context = get_context(next_issue, tree, namespaces)
        context_coords = xcu.get_coords(context)
        print(
            'The entire context is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, context_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        category = 0 if not protagonist_tuple(next_issue)[0] else 1
        user_input = get_protagonist_prompt(protagonist_tuple(next_issue))
        translation = input_to_protagonist_anno(user_input, category)

        sleepif(wait, 0.2)

        print(
            f'\nYour input was {user_input}.',
            f'This corresponds to "{translation}".',
            'Please make sure this is correct.\n'
        )

        confirmation = get_confirmation()

        sleepif(wait, 0.2)

        if confirmation and category == 0:
            next_issue.set('Protagonistinnen', translation)
            xh.default_write(tree, filepath)
            print('Correction written to file!\n')
        elif confirmation and category == 1:
            next_issue.set('Protagonistinnen2', translation)
            xh.default_write(tree, filepath)
            print('Correction written to file!\n')

        else:
            print('Nothing was changed.')
            print('You will be prompted to re-do the annotation.\n')

        print('-' * 70, '\n')
        sleepif(wait, 2)


def prompt_bezug(filepath, wait=True):

    seen_bezuglos = set()

    while True:
        tree, _, namespaces = xh.get_everything(filepath)
        sofa_string = xh.get_sofa_string(tree, namespaces)
        annotations = tree.findall('custom:Span', namespaces)

        faulty_moralizations = [
            annotation for annotation in annotations
            if annotation.get('Protagonistinnen') == "Kein Bezug"
            and (annotation.get('begin'), annotation.get('end'))
            not in seen_bezuglos
        ]

        if len(faulty_moralizations) < 1:
            print(f"Done with {filepath}!")
            break

        next_issue = faulty_moralizations[0]
        issue_coords = xcu.get_coords(next_issue)
        print('Found a protagonist with "Kein Bezug".\n')
        print(
            'The protagonist span is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, issue_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        context = get_context(next_issue, tree, namespaces)
        context_coords = xcu.get_coords(context)
        print(
            'The entire context is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, context_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        user_input = get_possible_malefiz()
        translation = input_to_protagonist_anno(user_input, 0)

        sleepif(wait, 0.2)

        print(
            f'\nYour input was {user_input}.',
            f'This corresponds to "{translation}".',
            'Please make sure this is correct.\n'
        )

        confirmation = get_confirmation()

        sleepif(wait, 0.2)

        if confirmation:
            next_issue.set('Protagonistinnen', translation)
            xh.default_write(tree, filepath)
            print('Correction written to file!\n')
            seen_bezuglos.add(
                (next_issue.get('begin'), next_issue.get('end'))
            )

        else:
            print('Nothing was changed.')
            print('You will be prompted to re-do the annotation.\n')

        print('-' * 70, '\n')
        sleepif(wait, 2)


def input_to_other_anno(letter):
    match letter:
        case 'Pr':
            return 'Protagonistinnen2'
        case 'Mw':
            return 'Moralwerte'
        case 'SA':
            return 'KAT2Subjektive_Ausdrcke'
        case _:
            raise ValueError('Could not handle annotation input string.')


def get_possible_other():
    valid_letters = {'Pr', 'Mw', 'SA'}
    new_annotation = 'XXXXXXXXX'
    while new_annotation not in valid_letters:
        if new_annotation != 'XXXXXXXXX':
            print('You did not enter a valid option.')
        print(
            'Consider whether this "OTHER" is actually a different type of annotation. '
            'Specifically, it could be a "Protagonisten-Gruppe", "Moralwerte" or "Subjektiver Ausdruck".\n'
        )
        print(
            'You have the following options:'
        )
        for letter in valid_letters:
            print(
                f'If the span is "{input_to_other_anno(letter)}", type {letter}'
            )
        print('If "OTHER" is correctly annotated already, just type the current label and nothing will be changed.\n')
        new_annotation = input('What type of "OTHER" is present here? ')
    return new_annotation


def prompt_other(filepath, wait=True):
    seen_other = set()

    while True:
        tree, _, namespaces = xh.get_everything(filepath)
        sofa_string = xh.get_sofa_string(tree, namespaces)
        annotations = tree.findall('custom:Span', namespaces)

        faulty_moralizations = [
            annotation for annotation in annotations
            if (annotation.get('Protagonistinnen2') == "OTHER" or annotation.get('KAT2Subjektive_Ausdrcke') == 'OTHER' or annotation.get('Moralwerte') == 'OTHER')
            and (annotation.get('begin'), annotation.get('end'))
            not in seen_other
        ]

        if len(faulty_moralizations) < 1:
            print(f"Done with {filepath}!")
            break

        next_issue = faulty_moralizations[0]

        issue_coords = xcu.get_coords(next_issue)
        print('Found a span with "OTHER".')
        print('"OTHER" was annotated in the context of: ', end="")
        if next_issue.get('Protagonistinnen2') == 'OTHER':
            print('Protagonistinnen2')
        elif next_issue.get('KAT2Subjektive_Ausdrcke\n') == 'OTHER':
            print('KAT2Subjektive_Ausdrcke\n')
        elif next_issue.get('Moralwerte') == 'OTHER':
            print('Moralwerte\n')
        else:
            print(next_issue.attrib)
        print(
            'The span is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, issue_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        context = get_context(next_issue, tree, namespaces)
        context_coords = xcu.get_coords(context)
        print(
            'The entire context is:\n',
            '+' * 30 + '\n',
            xcu.get_span(sofa_string, context_coords).strip(),
            '\n' + '+' * 30 + '\n',
            sep=''
        )

        sleepif(wait, 0.1)

        user_input = get_possible_other()
        translation = input_to_other_anno(user_input)

        sleepif(wait, 0.2)

        print(
            f'\nYour input was {user_input}.',
            f'This corresponds to "{translation}".',
            'Please make sure this is correct.\n'
        )

        confirmation = get_confirmation()

        sleepif(wait, 0.2)

        if confirmation:
            if translation == 'Protagonistinnen2':
                next_issue.set('Protagonistinnen2', 'OTHER')
                next_issue.attrib.pop('KAT2Subjektive_Ausdrcke', None)
                next_issue.attrib.pop('Moralwerte', None)
            elif translation == 'Moralwerte':
                next_issue.set('Moralwerte', 'OTHER')
                next_issue.attrib.pop('Protagonistinnen2', None)
                next_issue.attrib.pop('Protagonistinnen', None)
                next_issue.attrib.pop('KAT2Subjektive_Ausdrcke', None)
            elif translation == 'KAT2Subjektive_Ausdrcke':
                next_issue.set('KAT2Subjektive_Ausdrcke', 'OTHER')
                next_issue.attrib.pop('Protagonistinnen', None)
                next_issue.attrib.pop('Protagonistinnen2', None)
                next_issue.attrib.pop('Moralwerte', None)
            xh.default_write(tree, filepath)
            print('Correction written to file!\n')
            seen_other.add(
                (next_issue.get('begin'), next_issue.get('end'))
            )

        else:
            print('Nothing was changed.')
            print('You will be prompted to re-do the annotation.\n')

        print('-' * 70, '\n')
        sleepif(wait, 2)


if __name__ == '__main__':
    FILEPATH = '/home/brunobrocai/Desktop/Code/xmi-editing/inputs/Gerichtsurteile-neg-AW-neu-optimiert-BB.xmi'
    prompt_other(FILEPATH)
