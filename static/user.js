let fetchedData = []

// dostání a výpis jídel dnešního dne
fetch('/send_food')
  .then(response => response.json())
  .then(data => {
    fetchedData = data

    let area = document.getElementById('displayArea')
    
    let calorieSum = 0
    let proteinSum = 0
    let carbsSum = 0
    let fatSum = 0

    for (let i = 0; i < data.length; i++) {
        calorieSum += data[i].calories
        proteinSum += data[i].protein
        carbsSum += data[i].carbohydrates
        fatSum += data[i].fats
      
        let food = document.createElement('li')
        food.className="foodToday"
        food.id = data[i].id
        food.textContent = data[i].name
        area.appendChild(food)


    }

    // vypsaání sumy nutrientu
    let nutrientSum = document.createElement('li')
    nutrientSum.className = "nutrientSum"
    nutrientSum.innerHTML = `Total: <br>Calorie: ${parseFloat(calorieSum.toFixed(1))} kcal <br>Protein: ${parseFloat(proteinSum.toFixed(1))}g <br>Fat: ${parseFloat(fatSum.toFixed(1))}g <br>Carbs: ${parseFloat(carbsSum.toFixed(1))}g `
    area.appendChild(nutrientSum)

  })


  // fce na dostání a výpis dat jídla pro určený den
  let foodDate = (date) => {
  fetch('/chose_date_nuts', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ chose_date: date }), // nahraďte těmito daty
})

.then(response => response.json())
.then(data => {
  
  let area1 = document.getElementById('displayArea1')
  area1.innerHTML = ''
  for (let i = 0; i < data.length; i++) {
      let food = document.createElement('li')
      food.className="foodDateTest"
      food.textContent = data[i].name
      area1.appendChild(food)
  }
})
}


// vybírání dne na výpis jídel
document.getElementById('dateChoice').addEventListener('change', function(e) {

  let date_choice = document.getElementById('dateChoice').value
  if (date_choice !== "") {
    foodDate(date_choice)

}else{
  document.getElementById("displayArea1").innerHTML = ''
}
})


// funkce na kliknutí na jídlo v dnešku
let list = document.getElementById('displayArea')
list.addEventListener('click', function(e) {
  
  if (e.target.classList.contains('foodToday')) {

    if(e.target.firstElementChild) {
      
  
      e.target.firstElementChild.remove()
      
        
      
    } else {

            let jidloIndex = fetchedData.findIndex(element => element.id == e.target.id)

              // uložení podseznamu informací o jídle
              let foodInfoSeznam = document.createElement('ul')
              foodInfoSeznam.className = "foodInfoSeznam"
              
      
              let foodCalorie = document.createElement('li')
              foodCalorie.textContent = `Calorie: ${fetchedData[jidloIndex].calories} kcal`
              foodCalorie.className = "testInfo"
              foodInfoSeznam.appendChild(foodCalorie)
            
              let foodProtein = document.createElement('li')
              foodProtein.textContent = `Protein: ${fetchedData[jidloIndex].protein}g`
              foodProtein.className = "testInfo"
              foodInfoSeznam.appendChild(foodProtein)
      
              let foodFats = document.createElement('li')
              foodFats.textContent = `Fat: ${fetchedData[jidloIndex].fats}g`
              foodFats.className = "testInfo"
              foodInfoSeznam.appendChild(foodFats)
      
              let foodCarbs = document.createElement('li')
              foodCarbs.textContent = `Carbs: ${fetchedData[jidloIndex].carbohydrates}g`
              foodCarbs.className = "testInfo"
              foodInfoSeznam.appendChild(foodCarbs)

              e.target.classList.add('newFoodInfo')


              setTimeout(() => {
                e.target.classList.remove('newFoodInfo')
              }, 1500)

              e.target.appendChild(foodInfoSeznam)
       
    }
  } else if (e.target.className === 'testInfo') {
  
    e.target.parentElement.remove()

    
      
  }

  if (e.target.className === 'nutrientSum') {
    window.location.href = 'http://127.0.0.1:5000/hall_of_fame'
  }
})


// activity dneska
fetch('/activity_today')
  .then(response => response.json())
  .then(data => {
    let activityList = document.getElementById('displayAreaActivity')
    
    data.forEach(activity => {
    let activityDisplay = document.createElement('li')
    activityDisplay.className = 'activityToday'
    activityDisplay.textContent = `${activity.activity_emoji} ${activity.activity_name} ${activity.activity_duration}`
    activityList.appendChild(activityDisplay)

    })
  })

// fce na dostání a výpis dat aktivit na určený den

  let activityDate = (date) => {
    fetch('/activity_chose_date', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ chose_date: date }), // nahraďte těmito daty
  })
  
  .then(response => response.json())
  .then(data => {
    console.log(data)

    let activityArea1 = document.getElementById('displayAreaActivity1')
    activityArea1.innerHTML = ''
    for (let i = 0; i < data.length; i++) {
        let activity = document.createElement('li')
        activity.className = 'activityDay'
        activity.textContent = `${data[i].activity_emoji} ${data[i].activity_name} ${data[i].activity_duration}`
        activityArea1.appendChild(activity)
    }
  })
  }

// activity pro určený den
document.getElementById('dateChoiceActivity').addEventListener('change', function(e) {

  let activity_date_choice = document.getElementById('dateChoiceActivity').value
  if (activity_date_choice !== "") {
    activityDate(activity_date_choice)

}else{
  document.getElementById("displayAreaActivity1").innerHTML = ''
}
})
