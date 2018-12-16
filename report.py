import re
import os
import json

rounds = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'f1', 'f2', 'f3']
teams = [
    'CMSC723_FYY_2',
    'CMSC723_Technical_Wizards_2',
    'CMSC723_FowardRethinking_2',
    'CMSC723_Working_Title_1',
]

shapes = {
    'CMSC723_FYY_2': '\\tdiamond{{{}}}',
    'CMSC723_Technical_Wizards_2': '\\tcircle{{{}}}',
    'CMSC723_FowardRethinking_2': '\\tsquare{{{}}}',
    'CMSC723_Working_Title_1': '\\ttriangle{{{}}}',
}

color_correct = 'xgreen'
color_wrong = 'xred'
color_wrong_end = 'gray'
color_optimal = 'xyellow'

frame_header = '\\begin{{frame}}{{Packet {} Question {}}}'
frame_footer = '\\end{frame}'

questions_dir = '20181215_rounds_questions'
predictions_dir = '20181215_rounds_predictions'


def texify_single_quote(in_string):
    in_string = ' ' + in_string
    return re.sub(r"(?<=\s)'(?!')(.*?)'", r"`\1'", in_string)[1:]


def texify_double_quote(in_string):
    return re.sub(r'"(.*?)"', r"``\1''", in_string)


def get_first(idx_mapping, predictions, answer):
    for p in predictions:
        if p['buzz']:
            return idx_mapping[p['char_index']], p['guess']
    return get_last(idx_mapping, predictions, answer)


def get_last(idx_mapping, predictions, answer):
    return idx_mapping[predictions[-1]['char_index']], predictions[-1]['guess']


def get_optimal(idx_mapping, predictions, answer):
    for p in predictions:
        if p['guess'] == answer:
            return idx_mapping[p['char_index']], p['guess']
    return 999, None


for rnd in rounds:
    outfile = open('sections/{}.tex'.format(rnd), 'w')
    questions = json.load(open(os.path.join(questions_dir, rnd + '.json')))
    questions = questions['questions']
    team_predictions = {
        team: json.load(open(os.path.join(predictions_dir, rnd, team + '.json')))
        for team in teams}

    for qidx in range(len(questions)):
        question_text = questions[qidx]['text']
        answer = questions[qidx]['page']

        # map indices to the end of words such that they don't break tokens
        char_index_mapping = {}
        curr_index = 0
        for x in question_text.split(' '):
            for i in range(curr_index, curr_index + len(x) + 1):
                char_index_mapping[i] = curr_index + len(x) + 1
            curr_index += len(x) + 1

        # list of (char index, latex snippet, guess [or None])
        inserts = []
        for team, predictions in team_predictions.items():
            first_idx, first_guess = get_first(char_index_mapping, predictions[qidx], answer)
            last_idx, last_guess = get_last(char_index_mapping, predictions[qidx], answer)
            optimal_idx, _ = get_optimal(char_index_mapping, predictions[qidx], answer)

            if first_idx < last_idx:
                color = color_correct if first_guess == answer else color_wrong
                guess = None if first_guess == answer else first_guess
                inserts.append((first_idx, shapes[team].format(color), guess))
                if first_guess != answer:
                    if optimal_idx < last_idx:
                        inserts.append((optimal_idx, shapes[team].format(color_optimal), None))
                    else:
                        color = color_correct if last_guess == answer else color_wrong_end
                        guess = None if last_guess == answer else first_guess
                        inserts.append((last_idx, shapes[team].format(color), guess))
            else:
                if optimal_idx < last_idx:
                    inserts.append((optimal_idx, shapes[team].format(color_optimal), None))
                else:
                    color = color_correct if last_guess == answer else color_wrong_end
                    guess = None if last_guess == answer else first_guess
                    inserts.append((last_idx, shapes[team].format(color), guess))

        inserts = sorted(inserts, key=lambda x: x[0])
        inserted = []
        for i, (idx, snippet, guess) in enumerate(inserts):
            prev_idx = inserts[i - 1][0] if i > 0 else 0
            inserted.append(question_text[prev_idx: idx])
            inserted.append(snippet)
        inserted.append(question_text[inserts[-1][0]:])

        def canonicalize(s):
            s = s.replace('$', '\$')
            s = s.replace('_', '\_')
            s = texify_single_quote(s)
            s = texify_double_quote(s)
            return s

        inserted = canonicalize(' '.join(inserted))
        outfile.write(frame_header.format(rnd.upper(), qidx + 1) + '\n')
        outfile.write(inserted + '\n\n')
        outfile.write('\\textbf{{Answer}}: {}\\\\\n'.format(canonicalize(answer).replace('_', ' ')))

        for i, (idx, snippet, guess) in enumerate(inserts):
            if guess is None:
                continue
            outfile.write(snippet + ' ' + guess.replace('_', ' ') + '\n')

        outfile.write(frame_footer + '\n\n')
