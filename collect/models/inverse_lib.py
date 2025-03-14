from .regression import RunONNX
from .inverse import Inverse
from io import BytesIO
import numpy as np
import pandas as pd
import optuna
import joblib

def LoadModel(data):
    buf = BytesIO(data)
    buf.write(data)
    model = joblib.load(buf)
    buf.close()
    return model

class InverseObjective:
    def __init__(self, regdata, suggests):
        self.regdata = regdata
        self.suggests = suggests

    def __call__(self, trial):
        scores = []
        for regd in self.regdata:
            features = []
            columns = []
            for sug in self.suggests:
                if sug['name'] != regd['objective'] and sug['name'] not in regd['drop']:
                    features.append(trial.suggest_float(sug['name'], sug['min'], sug['max']))
                    columns.append(sug['name'])
            if regd['type'] == 0:
                model = LoadModel(regd['model'])
                pred = model.predict([features])[0]
            elif regd['type'] == 1:
                pred = RunONNX(regd['model'], np.array([features]))[0]
            scores.append((pred-regd['target'])**2)
        return tuple(scores)

def InverseExec(regdata, suggests, seed, ntrials, task_id):
    num = len(regdata)
    if num == 1:
        directions = ['minimize']
        sampler = optuna.samplers.TPESampler(seed=seed)
        vcolumns = ['_SquaredError1']
        pcolumns = ['_Predict1']
    elif num == 2:
        directions = ['minimize', 'minimize']
        sampler = optuna.samplers.NSGAIISampler(seed=seed)
        vcolumns = ['_SquaredError1', '_SquaredError2']
        pcolumns = ['_Predict1', '_Predict2']
    elif num == 3:
        directions = ['minimize', 'minimize', 'minimize']
        sampler = optuna.samplers.NSGAIISampler(seed=seed)
        vcolumns = ['_SquaredError1', '_SquaredError2', '_SquaredError3']
        pcolumns = ['_Predict1', '_Predict2', '_Predict3']
    study = optuna.create_study(directions=directions, sampler=sampler)
    objective = InverseObjective(regdata, suggests)
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study.optimize(objective, n_trials=ntrials)
    ids = pd.Series([t._trial_id for t in study.get_trials()], name='_TrialID')
    values = pd.DataFrame([t.values for t in study.get_trials()], columns=vcolumns)
    if num == 2:
        values['_SquaredError12'] = values['_SquaredError1'] + values['_SquaredError2']
    elif num == 3:
        values['_SquaredError123'] = values['_SquaredError1'] + values['_SquaredError2'] + values['_SquaredError3']
    if num == 1:
        best = [study.best_trial._trial_id]
    else:
        best = [t._trial_id for t in study.best_trials]
    bestflag = np.full(ntrials, False)
    bestflag[best] = True
    values['_BestTrial'] = bestflag
    params = pd.DataFrame([t.params for t in study.get_trials()])
    predicts = []
    for regd in regdata:
        cols = []
        if regd['objective'] in params.columns:
            cols.append(regd['objective'])
        for col in regd['drop']:
            if col in params.columns:
                cols.append(col)
        dparams = params.drop(columns=cols)
        if regd['type'] == 0:
            model = LoadModel(regd['model'])
            pred = model.predict(dparams.values)
        elif regd['type'] == 1:
            pred = RunONNX(regd['model'], dparams.values)
        predicts.append(pred)
    predicts = pd.DataFrame(predicts, index=pcolumns).T
    df = pd.concat([ids, values, predicts, params], axis=1)
    if num == 1:
        df = df.sort_values(['_SquaredError1'], ascending=[True])
    elif num == 2:
        df = df.sort_values(['_SquaredError12'], ascending=[True])
    elif num == 3:
        df = df.sort_values(by=['_SquaredError123'], ascending=[True])
    model = Inverse.objects.get(task_id=task_id)
    model.save_csv(df)
    model.save()



