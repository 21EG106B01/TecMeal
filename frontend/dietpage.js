document.addEventListener('DOMContentLoaded', async function () {
    const params = new URLSearchParams(window.location.search);
    const age = params.get('age');
    const height = params.get('height');
    const weight = params.get('weight');
    const gender = params.get('gender');
    const activity = params.get('activity');
    const plan = params.get('plan');
    
    const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ age: parseInt(age), height: parseInt(height), weight: parseInt(weight), gender: parseInt(gender), activity: parseInt(activity)})
    });
    const result = await response.json();

    const breakfastList = result.breakfast;
    const lunchList = result.lunch;
    const dinnerList = result.dinner;

    function displayMeal(mealType, mealList, index) {
        const mealContent = document.getElementById(`${mealType}Content`);
        const timeList = document.querySelectorAll(".totaltime");
        const ingredientList = document.querySelectorAll(".ingredients");

        const meal = mealList[index];
        mealContent.innerText = `${meal.Recipe_name}`;

        let totaltime = meal.TotalTime;
        let str = meal.Ingredients.replace(/'/g, '"');
        let ingredients = JSON.parse(str);
        const mealIngredients = ingredientList[['breakfast', 'lunch', 'dinner'].indexOf(mealType)];

        mealIngredients.innerHTML = '';
        ingredients.forEach(ingredient => {
            let listItem = document.createElement("li");
            listItem.textContent = ingredient;
            mealIngredients.appendChild(listItem);
        });

        timeList[['breakfast', 'lunch', 'dinner'].indexOf(mealType)].innerHTML = `Prep Time:<br>${totaltime}`;
    }

    displayMeal('breakfast', breakfastList, 0);
    displayMeal('lunch', lunchList, 0);
    displayMeal('dinner', dinnerList, 0);

    function rerollMeal(mealType, mealList) {
        let index = 0;
        let button = document.getElementById(`${mealType}Reroll`);
        button.addEventListener('click', function () {
            index = (index + 1) % mealList.length;
            displayMeal(mealType, mealList, index);
        });
    }

    rerollMeal('breakfast', breakfastList);
    rerollMeal('lunch', lunchList);
    rerollMeal('dinner', dinnerList);

    const mealBoxes = document.querySelectorAll(".meal-box");
    mealBoxes.forEach(meal => meal.addEventListener("click", function() {
        mealBoxes.forEach(mealBox => {
            let recipe = mealBox.querySelector(".recipe-info");
            if (!recipe.classList.contains("hidden")) {
                recipe.classList.toggle("hidden");
            }
        });
        let recipe = meal.querySelector(".recipe-info");
        recipe.classList.toggle("hidden");
    }));
});
