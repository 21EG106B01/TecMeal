import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from scipy.stats import mode

def scaling(dataframe):
    scaler = StandardScaler()
    prep_data = scaler.fit_transform(dataframe.iloc[:, 6:15].to_numpy())
    return prep_data, scaler

def rf_predictor(prep_data, labels):
    rf = RandomForestClassifier()
    rf.fit(prep_data, labels)
    return rf

def build_pipeline(model, scaler):
    pipeline = Pipeline([
        ('std_scaler', scaler),
        ('rf_model', model)
    ])
    return pipeline

def extract_data(dataframe, ingredients):
    extracted_data = dataframe.copy()
    extracted_data = extract_ingredient_filtered_data(extracted_data, ingredients)
    return extracted_data
    
def extract_ingredient_filtered_data(dataframe, ingredients):
    regex_string = ''.join(map(lambda x: f'(?=.*{x})', ingredients))
    extracted_data = dataframe[dataframe['RecipeIngredientParts'].str.contains(regex_string, regex=True, flags=re.IGNORECASE)]
    return extracted_data

def apply_pipeline(pipeline, _input, extracted_data, n_neighbors=5):
    _input = np.array(_input).reshape(1, -1)
    predictions = pipeline.predict(_input)
    predicted_class = predictions[0]
    matching_indices = np.where(extracted_data['Name'] == predicted_class)[0]
    recommended_indices = matching_indices[:n_neighbors] if len(matching_indices) >= n_neighbors else matching_indices

    return extracted_data.iloc[recommended_indices]

def recommend(dataframe, _input, ingredients=[], params={}):
    extracted_data = extract_data(dataframe, ingredients)
    if extracted_data.shape[0] > 0:
        prep_data, scaler = scaling(extracted_data)
        labels = extracted_data['Name'] 
        model = rf_predictor(prep_data, labels)
        pipeline = build_pipeline(model, scaler)
        return apply_pipeline(pipeline, _input, extracted_data, n_neighbors=params.get('n_neighbors', 5))
    else:
        return None

def extract_quoted_strings(s):
    return re.findall(r'"([^"]*)"', s)

def output_recommended_recipes(dataframe):
    if dataframe is not None:
        output = dataframe.copy()
        output = output.to_dict("records")
        for recipe in output:
            recipe['RecipeIngredientParts'] = extract_quoted_strings(recipe['RecipeIngredientParts'])
            recipe['RecipeInstructions'] = extract_quoted_strings(recipe['RecipeInstructions'])
    else:
        output = None
    return output
