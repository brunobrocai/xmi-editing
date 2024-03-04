import time
import xmi_handling as xh
import xmi_conversion_util as xcu


def get_first_promt():
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


def prompt_moralizations(filepath, verbose=True, wait=True):

    while True:
        tree, _, namespaces = xh.get_everything(filepath)
        sofa_string = xh.get_sofa_string(tree, namespaces)
        annotations = tree.findall('custom:Span', namespaces)

        faulty_moralizations = [
            annotation for annotation in annotations
            if annotation.get('KAT1MoralisierendesSegment') == "Moralisierung"
        ]

        if len(faulty_moralizations) < 1:
            if verbose:
                print(f"Done with {filepath}!")
                break

        else:
            next_issue = faulty_moralizations[0]
            issue_coords = xcu.get_coords(next_issue)
            print('Found a span whose moralization type was not specified.\n')
            print(
                'The span is:\n',
                '+' * 30 + '\n',
                xcu.get_span(sofa_string, issue_coords),
                '\n' + '+' * 30 + '\n\n',
                sep=''
            )

            sleepif(wait, 0.1)

            context = get_context(next_issue, tree, namespaces)
            context_coords = xcu.get_coords(context)
            print(
                'The entire context is:\n',
                '+' * 30 + '\n',
                xcu.get_span(sofa_string, context_coords),
                '\n' + '+' * 30 + '\n\n',
                sep=''
            )

            sleepif(wait, 0.1)

            user_input = get_first_promt()
            translation = input_to_annotation(user_input)

            sleepif(wait, 0.2)

            print(
                f'\n\nYour input was {user_input}.',
                f'This corresponds to "{translation}".',
                'Please make sure this is correct.\n'
            )

            confirmation = get_confirmation()

            sleepif(wait, 0.2)

            if confirmation:
                next_issue.set('KAT1MoralisierendesSegment', translation)
                xh.default_write(tree, filepath)
                print('Correction written to file!\n\n')

            else:
                print('Nothing was changed.')
                print('You will be prompted to re-do the annotation.\n\n')

            print('-' * 70, '\n')
            sleepif(wait, 2)


if __name__ == '__main__':
    FILEPATH = 'test1.xmi'
    prompt_moralizations(FILEPATH)
