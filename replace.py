import os
import json
from collections import defaultdict

rounds = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'f1', 'f2', 'f3']
teams = [
    'CMSC723_FYY_2',
    'CMSC723_Technical_Wizards_2',
    'CMSC723_FowardRethinking_2',
    'CMSC723_Working_Title_1',
]

all_predictions = defaultdict(dict)
all_questions = dict()
for rnd in rounds:
    all_questions[rnd] = json.load(open(os.path.join('20181215_rounds_questions', rnd + '.json')))
    for team in teams:
        all_predictions[rnd][team] = json.load(open(
            os.path.join('20181215_rounds_predictions', rnd, team + '.json')))

replacements = [
    (2000288, 'CMSC723_Technical_Wizards_2', 'Reductions', 'Wolff-Kishner_reduction'),
    (2000298, 'CMSC723_FowardRethinking_2', 'Pyotr_Ilyich_Tchaikovsky', 'Symphony_No._6_(Tchaikovsky)'),
    (2000303, 'CMSC723_FYY_2', 'Better_Call_Saul', 'Saul_Goodman'),
    (2000309, 'CMSC723_Technical_Wizards_2', 'Robot', 'R.U.R.'),
    (2000309, 'CMSC723_FowardRethinking_2', 'Robot', 'R.U.R.'),
    (2000309, 'CMSC723_Working_Title_1', 'Robot', 'R.U.R.'),
    (2000318, 'CMSC723_FowardRethinking_2', 'Virginia_Woolf', "A_Room_of_One's_Own"),
    (2000334, 'CMSC723_FowardRethinking_2', 'Confucius', 'Analects'),
    (2000385, 'CMSC723_FYY_2', 'Tiananmen_Square', 'Tiananmen_Square_protests_of_1989'),
    (2000401, 'CMSC723_Technical_Wizards_2', 'Pearl', 'Attack_on_Pearl_Harbor'),
]

replace_ids = [x[0] for x in replacements]

for rnd in rounds:
    for qidx, question in enumerate(all_questions[rnd]['questions']):
        if question['qanta_id'] not in replace_ids:
            continue

        for qid, team, answer, guess in replacements:
            if qid != question['qanta_id']:
                continue
            for row in all_predictions[rnd][team][qidx]:
                if row['guess'] == guess:
                    print(rnd, question['qanta_id'], team, guess)
                    row['guess'] = answer

for rnd in rounds:
    for team in teams:
        with open(os.path.join('20181215_rounds_predictions', rnd, team + '.json'), 'w') as f:
            json.dump(all_predictions[rnd][team], f)
