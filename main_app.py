from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, cast
from datetime import timedelta
import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)
app.secret_key = "hello"
app.config['SECRET_KEY'] = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.permanent_session_lifetime = timedelta(minutes=1000)



db = SQLAlchemy(app)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Předpokládáme, že máte vztah mezi uživatelem a jídlem

    def __repr__(self):
        return f'<Food {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    foods = db.relationship('Food', backref='user', lazy=True)
    activities = db.relationship('Activities', backref='user', lazy=True)


class Activities(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    activity_name = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)

    activity_duration = db.Column(db.String(10), nullable=False)  # HH:MM formát

    activity_emoji = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    


with app.app_context():
    db.create_all()




@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username")
        password = request.form.get("password")

        if action == "signin":
            found_user = User.query.filter_by(username=username, password=password).first()
            if found_user:
                session.permanent = True
                session["user"] = username
                session["user_id"] = found_user.id
                flash("Logged in successfully")
                flash(f"Welcome, {username}!", "info")
                return redirect(url_for("user"))
            else:
                flash("Login Unsuccessful. Please check username and password", "danger")
                return redirect(url_for("login"))
        elif action == "signup":
            existing_user = User.query.filter_by(username=username).first()
            if existing_user is None:
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                session.permanent = True
                session["user"] = username
                session["user_id"] = new_user.id
                flash("Account created and logged in successfully", "info")
                return redirect(url_for("user"))
            else:
                flash("User already exists", "danger")
                return redirect(url_for("login"))
    else:
        return render_template("login.html")
    




@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("user"))
    else:
        return render_template("home.html", content="Testing")



@app.route("/chose_date_nuts", methods=["POST"])
def chose_date_nuts():
# vybraný den
    if request.headers.get("Content-Type") == "application/json":
        data = request.get_json()
        if data:
            
            print(data)

            session["chose_date"] = data.get("chose_date")

            
            

            chose_date_str = session["chose_date"]

            chose_date_obj = datetime.datetime.strptime(chose_date_str, "%Y-%m-%d").date()

            chose_date_foods = Food.query.filter_by(user_id=session["user_id"]).all()
            chose_date_foods_list = []

            

            for food in chose_date_foods:
                if food.date_added.date() == chose_date_obj:
                    food_dict = {
                        "id": food.id,
                        "name": food.name,
                        "calories": food.calories,
                        "protein": food.protein,
                        "carbohydrates": food.carbohydrates,
                        "fats": food.fats,
                        "date_added": food.date_added.strftime("%Y-%m-%d"),  # Format datetime as string
                    }
                    print(food)
                    chose_date_foods_list.append(food_dict)
            
            return jsonify(chose_date_foods_list)
        else:
            return jsonify({"error": "No data received"})
@app.route("/send_food")
def send_food():
    # function to send data for today's nutrition
    today = datetime.datetime.today().date()  # Ensure we're comparing just the date part
    today_foods = Food.query.filter_by(user_id=session["user_id"]).all()
    today_foods_list = []
    for food in today_foods:
        if food.date_added.date() == today:
            food_dict = {
                "id": food.id,
                "name": food.name,
                "calories": food.calories,
                "protein": food.protein,
                "carbohydrates": food.carbohydrates,
                "fats": food.fats,
                "date_added": food.date_added.strftime("%Y-%m-%d"),  # Format datetime as string
            }
            
            today_foods_list.append(food_dict)
    
    return jsonify(today_foods_list)


@app.route("/user", methods=["GET", "POST"])
def user():
    if "user" in session:
        user = session["user"]
        

        return render_template("user.html", user=user)

    else:
        # Redirect to login page or show an error if the user is not logged in
        flash("You are not logged in!", "danger")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    session.pop("user", None)
    return redirect(url_for("home"))




@app.route("/receive_data", methods=["POST"])
def receive_data():
    if request.headers.get("Content-Type") == "application/json":
        data = request.get_json()
        if data:
            session["query_name"] = data.get("query_name")
            session["query_weight"] = data.get("query_weight")
        
            

# když je weight 1 serving
            if session.get("query_weight") == "1 serving":
                query = "1 serving" + " " + session.get("query_name")
                
                if query != None:
                    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
                    response = requests.get(api_url, headers={'X-Api-Key': 'FQaci+ynPatuFRCh5oYQgQ==cAVWBbtpxIOQcReX'})
                    
                    if response.status_code == requests.codes.ok:
                        data = response.json()

                        name = data[0]["name"]

                        protein = round((data[0]["protein_g"]) , 4)
                        
                        carbohydrates = round((data[0]["carbohydrates_total_g"]), 4)

                        fats = round((data[0]["fat_total_g"]) , 4)

                        calorie = round((data[0]["calories"]) , 4)

                        new_food = Food(name=name, protein=protein, carbohydrates=carbohydrates, fats=fats, calories=calorie, date_added=datetime.date.today(), user_id=session.get("user_id"))

                        db.session.add(new_food)
                        db.session.commit()

                        data = {"protein": protein, "fats": fats, "carbohydrates": carbohydrates, "calorie":calorie, "name": name}

                    

                    return jsonify(data)
                


# když je weight číslo

            else:
                query = session.get("query_name")
                    
                if query != None:
                    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
                    response = requests.get(api_url, headers={'X-Api-Key': 'FQaci+ynPatuFRCh5oYQgQ==cAVWBbtpxIOQcReX'})
                    
                    if response.status_code == requests.codes.ok:
                        
                        data = response.json()
                        
                    
                        name = data[0]["name"]

                        

                        weight = float(session["query_weight"])

                        protein = round((data[0]["protein_g"]) /100 * weight, 4)
                        
                        carbohydrates = round((data[0]["carbohydrates_total_g"]) /100 * weight, 4)

                        fats = round((data[0]["fat_total_g"]) /100 * weight, 4)

                        calorie = round((data[0]["calories"]) /100 * weight, 4)

                        new_food = Food(name=name, protein=protein, carbohydrates=carbohydrates, fats=fats, calories=calorie, date_added=datetime.date.today(), user_id=session.get("user_id"))

                        db.session.add(new_food)
                        db.session.commit()

                        data = {"protein": protein, "fats": fats, "carbohydrates": carbohydrates, "calorie":calorie, "name": name}

                        

                        return jsonify(data)
                
                    
        
            
        
        
@app.route('/addfood', methods=['GET', 'POST'])
def addfood():
    if "user" in session:
                # Handle other nutrition data similarly
        return render_template("addfood.html")
    else:
        flash("You are not logged in!", "danger")
        return redirect(url_for("home"))

    
        

@app.route('/debug/user_foods')
def debug_user_foods():
    user_id = session.get("user_id")
    if not user_id:
        return "No user logged in", 400

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    foods = Food.query.filter_by(user_id=user_id).all()
    # Update this line to use the correct attributes
    foods_str = ", ".join([f"{food.name} (Date: {food.date_added}Protein: {food.protein}g, Carbohydrates: {food.carbohydrates}g, Fats: {food.fats}g Calories: {food.calories})" for food in foods])
    print(f"Foods for user {user.username}: {foods_str}")
    return f"Foods printed to console for user {user.username}"





@app.route('/activitydata', methods=['GET', 'POST'])
def activitydata():
    if request.headers.get("Content-Type") == "application/json":
        data = request.get_json()
        if data:
            session["activity_name"] = data.get("activity_name")
            session["activity_duration"] = data.get("activity_duration")
            session["activity_emoji"] = data.get("activity_emoji")


            print(data)
            
            new_activity = Activities(activity_name=session.get("activity_name"), activity_duration=session.get("activity_duration"), date_added=datetime.date.today(), activity_emoji=session.get("activity_emoji"), user_id=session.get("user_id"))
            db.session.add(new_activity)
            db.session.commit()
            

            return jsonify(data)
        


@app.route("/activity_chose_date", methods=["GET", "POST"])
def activity_chose_date():
    if request.headers.get("Content-Type") == "application/json":
        data = request.get_json()
        if data:
            
            print(data)

            session["chose_date"] = data.get("chose_date")

            chose_date_str = session["chose_date"]

            chose_date_obj = datetime.datetime.strptime(chose_date_str, "%Y-%m-%d").date()

            chose_date_activities = Activities.query.filter_by(user_id=session.get("user_id")).all()

            chose_date_activities_list = []

            for activity in chose_date_activities:
                if activity.date_added.date() == chose_date_obj:
                    chose_date_activities_dict = {
                        "activity_name": activity.activity_name,
                        "activity_duration": activity.activity_duration,
                        "date_added": activity.date_added.strftime('%Y-%m-%d'),
                        "activity_emoji": activity.activity_emoji
                    }
                    chose_date_activities_list.append(chose_date_activities_dict)



            return jsonify(chose_date_activities_list)

@app.route("/activity_today", methods=["GET", "POST"])
def activity_today():
    user_id = session.get("user_id")
    today = datetime.datetime.today().date()
    today_activities = Activities.query.filter_by (user_id=user_id).all()
    today_activities_list = []

    for activity in today_activities:
        if activity.date_added.date() == today:
            today_activities_dict = {
                "activity_name": activity.activity_name,
                "activity_duration": activity.activity_duration,
                "date_added": activity.date_added.strftime('%Y-%m-%d'),
                "activity_emoji": activity.activity_emoji
            }
            today_activities_list.append(today_activities_dict)

    return jsonify(today_activities_list)

@app.route('/debug/user_activities')
def debug_user_activities():
    user_id = session.get("user_id")
    if not user_id:
        return "No user logged in", 400

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    activities = Activities.query.filter_by(user_id=user_id).all()
    activities_str = ", ".join([f"Activity Name: {activity.activity_name}, Date Added: {activity.date_added.strftime('%Y-%m-%d')}, Duration: {activity.activity_duration}" for activity in activities])
    print(f"Activities for user {user.username}: {activities_str}")
    return f"Activities printed to console for user {user.username}"


@app.route("/activities", methods=["GET", "POST"])
def activities():
    if "user" not in session:
        flash("You are not logged in!", "danger")
        return redirect(url_for("home"))    

    else:
        return render_template("activities.html")






@app.route("/receive_key", methods=["POST"])
def receive_key():
    if request.headers.get("Content-Type") == "application/json":
        data = request.get_json()
        if data:
            
            print(data)

            session["key"] = data.get("key")
            users_totals = []
            all_users = User.query.all()
            
        for user in all_users:
            user_foods = Food.query.filter_by(user_id=user.id).all()
            user_foods_count = len(user_foods) 

            user_calories_total = sum(round(food.calories) for food in user_foods)
            user_protein_total = sum(round(food.protein) for food in user_foods)
            user_carbohydrates_total = sum(round(food.carbohydrates) for food in user_foods)
            user_fats_total = sum(round(food.fats) for food in user_foods)

            users_totals.append({
                "user_id": user.id,
                "username": user.username,
                "foods_count": user_foods_count,  
                "calories_total": user_calories_total,
                "protein_total": user_protein_total,
                "carbohydrates_total": user_carbohydrates_total,
                "fats_total": user_fats_total,
            })

        key_to_sort_by = session.get("key", "foods_count")
        print (key_to_sort_by)

        users_totals_sorted = sorted(users_totals, key=lambda x: x.get(key_to_sort_by, 0), reverse=False)


        print (users_totals_sorted)

        return render_template("hall_of_fame.html",  all_users=all_users, users_totals=users_totals, users_totals_sorted=users_totals_sorted)

    

@app.route('/hall_of_fame', methods=['POST', 'GET'])
def hall_of_fame():
    if "user" not in session:
        flash("You are not logged in!", "danger")
        return redirect(url_for("home"))
    
    sort_by = request.args.get('sort_by', 'foods_count')

    sort_order = session.get('sort_order', True)  # Defaultní hodnota False pro vzestupné řazení

    current_sort_by = request.args.get('sort_by', 'foods_count')
    session['previous_sort_by'] = current_sort_by
    session['sort_order'] = sort_order    
    previous_sort_by = session.get('previous_sort_by')

    if current_sort_by == previous_sort_by:
        sort_order = not sort_order
    else:
        # Pokud je sort_by jiný, resetujeme směr řazení na vzestupný
        sort_order = False

    session['previous_sort_by'] = current_sort_by 


    session['sort_order'] = sort_order

    user_id = session.get("user_id")
    user = User.query.get(user_id)
    username = user.username
    foods_total = Food.query.filter_by(user_id=user_id).all()

    calories_total = 0
    protein_total = 0
    carbohydrates_total = 0
    fats_total = 0

    all_users = User.query.all()


    for food in foods_total:
        calories_total += round(food.calories)
        protein_total += round(food.protein)
        carbohydrates_total += round(food.carbohydrates)
        fats_total += round(food.fats)
    foods_count = len(foods_total)

    users_totals = []

    for index, user in enumerate(all_users, start=1):
        user_foods = Food.query.filter_by(user_id=user.id).all()
        user_foods_count = len(user_foods) 

        user_calories_total = sum(round(food.calories) for food in user_foods)
        user_protein_total = sum(round(food.protein) for food in user_foods)
        user_carbohydrates_total = sum(round(food.carbohydrates) for food in user_foods)
        user_fats_total = sum(round(food.fats) for food in user_foods)

        users_totals.append({
            "rank": index,
            "user_id": user.id,
            "username": user.username,
            "foods_count": user_foods_count,  
            "calories_total": user_calories_total,
            "protein_total": user_protein_total,
            "carbohydrates_total": user_carbohydrates_total,
            "fats_total": user_fats_total,
        })


    if sort_by in ['username', 'foods_count', 'calories_total', 'protein_total', 'carbohydrates_total', 'fats_total']:
        users_totals_sorted = sorted(users_totals, key=lambda x: x[current_sort_by], reverse=not sort_order)
    else:
        users_totals_sorted = users_totals


    print (users_totals_sorted)

    return render_template("hall_of_fame.html", calories_total=calories_total, protein_total=protein_total, carbohydrates_total=carbohydrates_total, fats_total=fats_total, foods_count=foods_count, user_id=user_id, username=username, foods_total=foods_total, all_users=all_users, users_totals=users_totals, users_totals_sorted=users_totals_sorted)




@app.route('/is_logged_in')
def is_logged_in():
    return jsonify({'logged_in': 'user' in session})


# session["activity_name"]

@app.route("/receive_data_act", methods=["POST", "GET"])
def receive_data_act():
        if request.headers.get("Content-Type") == "application/json":
            data = request.get_json()
            if data:

                session["activity_nam"] = data.get("activity_nam")
                query = session.get("activity_nam", None)
                print(query)
                    
                if query != None:
                    access_key = "igI0JnlEtoM2o2tp5sX14_O58so39jdgu9fqviSjJjw"
                    api_url = f'https://api.unsplash.com/search/photos?page=1&query={query}'
                    response = requests.get(api_url, headers={'Authorization': f'Client-ID {access_key}'})
                    
                    if response.status_code == requests.codes.ok:
                        data = response.json()


                        url = data["results"][0]["urls"]["regular"]

                        data = {"url": url}
                        session["activity_nam"] = None

                        print(data)

                        return jsonify(data)
                    else:
                        # Handle the case where the API call was not successful
                        return jsonify({"error": "Failed to fetch image from Unsplash"}), response.status_code
                else:
                    # Handle the case where 'query' is None
                    return jsonify({"error": "Query not provided"}), 400





@app.route("/receive_data_obr", methods=["POST", "GET"])
def receive_data_obr():
    if request.headers.get("Content-Type") == "application/json":
        data = request.get_json()
        if data:
            session["picture_name"] = data.get("picture_name")
            query = session.get("picture_name", None)

            print(query)
                
            if query != None:
                access_key = "igI0JnlEtoM2o2tp5sX14_O58so39jdgu9fqviSjJjw"
                api_url = f'https://api.unsplash.com/search/photos?page=1&query={query}'
                response = requests.get(api_url, headers={'Authorization': f'Client-ID {access_key}'})
                
                if response.status_code == requests.codes.ok:
                    data = response.json()


                    url = data["results"][0]["urls"]["regular"]

                    data = {"url": url}
                    session["picture_name"] = None

                    print(data)

                    return jsonify(data)
                else:
                    # Handle the case where the API call was not successful
                    return jsonify({"error": "Failed to fetch image from Unsplash"}), response.status_code
            else:
                # Handle the case where 'query' is None
                return jsonify({"error": "Query not provided"}), 400



if __name__ == '__main__':
    app.run(debug=True)