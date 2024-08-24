import pandas as pd

def compute_co_attainment(filename, coq):
    results = {
        'CO1': 0,
        'CO2': 0,
        'CO3': 0,
        'CO4': 0,
        'CO5': 0,
        'CO6': 0,
    }
    if filename[-4:].lower() != '.csv':
        return None
    df = pd.read_csv(filename, dtype=str)
    for co in coq:
        for q in co['data']:
            values = df.loc[df[q].notna(), q].values.astype(int)
            results[co['name']] += int(sum(values))
    return results
