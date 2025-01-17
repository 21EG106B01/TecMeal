import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import pickle
import os

MODEL_PATH = 'backend/model.pkl'
recipes_df = pd.read_csv('data/True_Data2.bz2', compression='bz2')

def train_model():
    user_data = pd.read_csv('data/user_data.csv')
    
    X = user_data[['Age', 'Weight', 'Height', 'Gender', 'Physical exercise']]
    y = user_data[['Calories', 'Protein', 'Fat', 'Carbs', 'Sodium', 'Sugar', 'Fiber', 'SaturatedFat']]
    
    preprocessor = ColumnTransformer(transformers=[('num', StandardScaler(), ['Age', 'Weight', 'Height'])])

    model_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                     ('regressor', XGBRegressor(tree_method='hist', n_estimators=100))])
    
    model_pipeline.fit(X, y)

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_pipeline, f)

    return model_pipeline

def load_model():
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

if os.path.exists(MODEL_PATH):
    model = load_model()
else:
    model = train_model()

def predict_nutrition(age, weight, height, gender, activity):
    input_data = np.array([[age, height, weight, gender, activity]])
    input_df = pd.DataFrame(input_data, columns=['Age', 'Height', 'Weight', 'Gender', 'Physical exercise'])

    predicted_nutrition = model.predict(input_df)[0]

    return {
        'calories': predicted_nutrition[0],
        'protein': predicted_nutrition[1],
        'fat': predicted_nutrition[2],
        'carbs': predicted_nutrition[3],
        'sodium': predicted_nutrition[4],
        'sugar': predicted_nutrition[5],
        'fiber': predicted_nutrition[6],
        'saturated_fat': predicted_nutrition[7],
        'meals': get_meal_recommendations(predicted_nutrition),
    }

def get_meal_recommendations(predicted_nutrition):
    breakfast_factor = [0.2, 0.3, 0.1, 0.2, 0.15, 0.1, 0.05, 0.05]
    lunch_factor = [0.4, 0.4, 0.3, 0.3, 0.25, 0.2, 0.15, 0.1]
    dinner_factor = [0.4, 0.3, 0.6, 0.5, 0.6, 0.7, 0.8, 0.85]

    def apply_multiplicative_factor(factor, nutrition):
        return [
            nutrition[0] * factor[0],
            nutrition[1] * factor[1],
            nutrition[2] * factor[2],
            nutrition[3] * factor[3],
            nutrition[4] * factor[4],
            nutrition[5] * factor[5],
            nutrition[6] * factor[6],
            nutrition[7] * factor[7],
        ]

    def get_closest_recipes(adjusted_nutrition, excluded_recipes):
        recipes_df['calorie_diff'] = (recipes_df['Calories'] - adjusted_nutrition[0]).abs()
        recipes_df['protein_diff'] = (recipes_df['ProteinContent'] - adjusted_nutrition[1]).abs()
        recipes_df['fat_diff'] = (recipes_df['FatContent'] - adjusted_nutrition[2]).abs()
        recipes_df['carb_diff'] = (recipes_df['CarbohydrateContent'] - adjusted_nutrition[3]).abs()
        recipes_df['sodium_diff'] = (recipes_df['SodiumContent'] - adjusted_nutrition[4]).abs()
        recipes_df['sugar_diff'] = (recipes_df['SugarContent'] - adjusted_nutrition[5]).abs()
        recipes_df['fiber_diff'] = (recipes_df['FiberContent'] - adjusted_nutrition[6]).abs()
        recipes_df['saturated_fat_diff'] = (recipes_df['SaturatedFatContent'] - adjusted_nutrition[7]).abs()

        recipes_df['total_diff'] = (recipes_df['calorie_diff'] + recipes_df['protein_diff'] +
                                     recipes_df['fat_diff'] + recipes_df['carb_diff'] +
                                     recipes_df['sodium_diff'] + recipes_df['sugar_diff'] +
                                     recipes_df['fiber_diff'] + recipes_df['saturated_fat_diff'])

        available_recipes = recipes_df[~recipes_df['Name'].isin(excluded_recipes)]
        closest_recipes = available_recipes.nsmallest(10, 'total_diff')

        adjusted_recipes = []
        for _, recipe in closest_recipes.iterrows():
            adjusted_recipes.append(dict(recipe))

        return adjusted_recipes

    excluded_recipes = []

    breakfast_nutrition = apply_multiplicative_factor(breakfast_factor, predicted_nutrition)
    breakfast_meals = get_closest_recipes(breakfast_nutrition, excluded_recipes)
    excluded_recipes.extend([meal['Name'] for meal in breakfast_meals])

    lunch_nutrition = apply_multiplicative_factor(lunch_factor, predicted_nutrition)
    lunch_meals = get_closest_recipes(lunch_nutrition, excluded_recipes)
    excluded_recipes.extend([meal['Name'] for meal in lunch_meals])

    dinner_nutrition = apply_multiplicative_factor(dinner_factor, predicted_nutrition)
    dinner_meals = get_closest_recipes(dinner_nutrition, excluded_recipes)
    excluded_recipes.extend([meal['Name'] for meal in dinner_meals])

    return {
        'breakfast': breakfast_meals,
        'lunch': lunch_meals,
        'dinner': dinner_meals,
    }
