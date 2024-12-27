import pandas as pd

def compute_co(df, coq):
    results = {
        'CO1': {
            'attained': 0,
            'total': None,
            'questions': {},
        },
        'CO2': {
            'attained': 0,
            'total': None,
            'questions': {},
        },
        'CO3': {
            'attained': 0,
            'total': None,
            'questions': {},
        },
        'CO4': {
            'attained': 0,
            'total': None,
            'questions': {},
        },
        'CO5': {
            'attained': 0,
            'total': None,
            'questions': {},
        },
        'CO6': {
            'attained': 0,
            'total': None,
            'questions': {},
        },
    }
    for co in coq:
        # if co['data'] is None:
        #     continue
        results[co['name']]['total'] = len(df) * co['total']
        for q in co['data']:
            values = df.loc[df[q] > 0, q].values.astype(int)
            values_sum = int(sum(values))
            results[co['name']]['questions'][q] = len(values)
            results[co['name']]['attained'] += values_sum
    return results