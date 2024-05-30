let activityPageBtn = (value) => {
    if (value !== "") {
    document.querySelector("#activitySubmit").style.display = 'block';
    document.querySelector("#durationInput").style.display = 'inline-block';
    } else {
        document.querySelector("#activitySubmit").style.display = 'none';
        document.querySelector("#durationInput").style.display = 'none';
    }
}


document.getElementById("activitySubmit").addEventListener("click", function(e) {

    document.querySelector(".obrActivity").innerHTML = ""

    document.getElementById("added").style.display = 'block';
    let activityName = document.getElementById("activityInput").value
    let activityDuration = document.getElementById("durationInput").value

    let activityEmoji = ""
    if (activityName.includes("run")) {
        activityEmoji = "🏃"
    } else if (activityName.includes("swim")) {
        activityEmoji = "🏊"
    } else if (activityName.includes("walk")) {
        activityEmoji = "🚶"
    } else if (activityName.includes("bike")) {
        activityEmoji = "🚴"
    } else if (activityName.includes("gym")) {
        activityEmoji = "💪"
    } else {
        activityEmoji = "🤷‍♀️"
    }

    let activityDisplay = document.getElementById("added")
    activityDisplay.textContent = ''

    fetch('/activitydata', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ activity_name :activityName, activity_duration :activityDuration, activity_emoji :activityEmoji}), 
})

if (activityDuration !== "") {
    activityDisplay.innerHTML = `Activity added: ${activityEmoji} ${activityName} <br> Duration: ${activityDuration}`
}else {
    activityDisplay.innerHTML = `Activity added: ${activityEmoji} ${activityName} <br> Duration: 🤷‍♀️`
}


    fetch('/receive_data_act', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ activity_nam :activityName}), 
    }) 

    .then(response => response.json())
    .then(data => {
        
        document.querySelector(".obrActivity").innerHTML = `<img src=${data.url} alt="image not found">`

    })
    
    document.getElementById("activityInput").value = ""
    document.getElementById("durationInput").value = ""

})