document.getElementById('foodInput').addEventListener('input', function(e) {
    if (e.target.value.length > 0) {
    document.getElementById("submitFood").style.display = 'inline-block';
    }else {
        document.getElementById("submitFood").style.display = 'none';
    }
})

document.getElementById('weight5').addEventListener('click', (e) => {
    document.getElementById('weightInput').value = 50
})

document.getElementById('weight10').addEventListener('click', (e) => {
    document.getElementById('weightInput').value = 100
})

document.getElementById('weightPort').addEventListener('click', (e) => {
    document.getElementById('weightInput').value = "1 serving"
})

document.getElementById('weight20').addEventListener('click', (e) => {
    document.getElementById('weightInput').value = 200
})


document.getElementById('submitFood').addEventListener('click', function(e) {
    e.preventDefault()

    document.getElementById('foodDisplay').innerHTML = ''

    document.getElementById('obrTest').innerHTML = ""

    document.getElementById('loadingAnimation').style.display = 'block';

    let food_name = document.getElementById('foodInput').value
    let food_weight = document.getElementById('weightInput').value


    fetch('/receive_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query_name: food_name, query_weight: food_weight }), // nahraďte těmito daty
    })
    .then(response => {
        if (!response.ok) {
            alert("Provided information are not in the database")
            document.getElementById('foodInput').value = ''
            document.getElementById('weightInput').value = ''
            document.getElementById('loadingAnimation').style.display = 'none';
            throw new Error('Chyba při komunikaci se serverem')
            
        }
        
        return response.json();
    })
    .then(data => {


        /***********************************
         * todo aby obrazek nepredbihal
         ***********************************/
        
        // zobrazení obrázku
        fetch('/receive_data_obr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ picture_name: food_name }), // nahraďte těmito daty
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Chyba při komunikaci se serverem')
                }
                return response.json();
            })
            .then(data => {
                console.log(data)
                
            
                document.getElementById('obrTest').innerHTML = `<img src=${data.url} alt="image not found">`
                
                
        })

        document.getElementById('loadingAnimation').style.display = 'none';
        document.getElementById('foodInput').value = ''
        document.getElementById('weightInput').value = ''
        document.getElementById('submitFood').style.display = 'none'
        
        let container = document.getElementById('foodDisplay')
        let foodHeading = document.createElement('h3')
        foodHeading.textContent = `Food added: ${data.name}`
        
        let calorie = document.createElement('p')
        calorie.textContent = `Calories: ${data.calorie} kcal`
        let protein = document.createElement('p')
        protein.textContent = `Protein: ${data.protein} g`
        let carbs = document.createElement('p')
        carbs.textContent = `Carbs: ${data.carbohydrates}g`
        let fat = document.createElement('p')
        fat.textContent = `Fat: ${data.fats}g`

        container.appendChild(foodHeading)
        container.appendChild(calorie)
        container.appendChild(protein)
        container.appendChild(carbs)
        container.appendChild(fat)


        })
    .catch((error) => {
        console.error('Chyba při odesílání dat:', error);
    });



})
