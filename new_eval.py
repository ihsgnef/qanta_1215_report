import os
import json
import numpy as np
import pickle
from collections import defaultdict

class CurveScore:

    def __init__(self, curve_pkl='curve_pipeline.pkl'):
        with open(curve_pkl, 'rb') as f:
            self.pipeline = pickle.load(f)

    def get_weight(self, x):
        return self.pipeline.predict(np.asarray([[x]]))[0]

    def score(self, guesses, question):
        '''guesses is a list of {'guess': GUESS, 'buzz': True/False}
        '''
        char_length = len(question['text'])
        buzzes = [x['buzz'] for x in guesses]
        if True not in buzzes:
            return 0
        buzz_index = buzzes.index(True)
        rel_position = (1.0 * guesses[buzz_index]['char_index']) / char_length
        weight = self.get_weight(rel_position)
        result = guesses[buzz_index]['guess'] == question['page']
        return weight * result

    def score_optimal(self, guesses, question):
        '''score with an optimal buzzer'''
        char_length = len(question['text'])
        buzz_index = char_length
        for g in guesses[::-1]:
            if g['guess'] != question['page']:
                buzz_index = g['char_index']
                break
        rel_position = (1.0 * buzz_index) / char_length
        return self.get_weight(rel_position)


def eval_one(answers, questions):
    for question_idx, guesses in enumerate(answers):
        question = questions[question_idx]
        answer = question['page']
        first_guess = None
        for g in guesses:
            if g['sent_index'] == 1:
                first_guess = g['guess']
                break
        first_acc.append(first_guess == answer)
        end_acc.append(guesses[-1]['guess'] == answer)
        ew.append(curve_score.score(guesses, question))
        ew_opt.append(curve_score.score_optimal(guesses, question))
    eval_out = {
        'first_acc': sum(first_acc) * 1.0 / len(first_acc),
        'end_acc': sum(end_acc) * 1.0 / len(end_acc),
        'expected_wins': sum(ew) * 1.0 / len(ew),
        'expected_wins_optimal': sum(ew_opt) * 1.0 / len(ew_opt),
    }
    # with open(score_dir, 'w') as f:
    #     json.dump(eval_out, f)
    # print(json.dumps(eval_out))
    return eval_out


if __name__ == '__main__':
    rounds = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'f1', 'f2', 'f3']
    teams = [
        'CMSC723_FYY_2',
        'CMSC723_Technical_Wizards_2',
        'CMSC723_FowardRethinking_2',
        'CMSC723_Working_Title_1',
    ]
    questions_dir = '20181215_rounds_questions'
    predictions_dir = '20181215_rounds_predictions'
    curve_score = CurveScore()

    first_acc = []
    end_acc = []
    ew = []
    ew_opt = []

    team_scores = {team: defaultdict(list) for team in teams}

    for rnd in rounds:
        questions = json.load(open(os.path.join(questions_dir, rnd + '.json')))
        questions = questions['questions']
        for team in teams:
            answers = json.load(open(os.path.join(predictions_dir, rnd, team + '.json')))
            scores = eval_one(answers, questions)
            for key, value in scores.items():
                team_scores[team][key].append(value)

    # print(team_scores)
    for team, scores in team_scores.items():
        print(team)
        for key, value in scores.items():
            team_scores[team][key] = sum(value) / len(value)
            print(sum(value) / len(value))
