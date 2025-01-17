document.getElementById('generateButton').addEventListener('click', async function () {
    const age = document.getElementById('age').value;
    const height = document.getElementById('height').value;
    const weight = document.getElementById('weight').value;
    const gender = document.getElementById('gender').value;
    const activity = document.getElementById('activity').value;
    const plan = document.getElementById('plan').value;

    let userdata = { 
        age: parseInt(age), 
        height: parseInt(height), 
        weight: parseInt(weight), 
        gender: parseInt(gender), 
        activity: parseInt(activity), 
        plan: parseInt(plan) 
    };

    let redirectUrl = "/dietpage"; 
    let queryString = new URLSearchParams(userdata).toString();
    window.location.href = `${redirectUrl}?${queryString}`;
});
