import hashlib
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import openai  # Correct import

# Set your OpenAI API details
api_key = "f45d2cc26b2e44428f9f14b0336bd7e0"
base_url = "https://api.aimlapi.com/v1"  # Optional, only if using a custom endpoint
system_prompt = "simple conversation"

openai.api_key = api_key
openai.api_base = base_url  # Only include this if you're using a custom API endpoint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

def generate_response(user_prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=256,
        )
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"API Error: {e}")
        return "Sorry, I am having trouble responding right now."

class ElectricCar(db.Model):
    __tablename__ = 'electric_cars'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    battery_capacity = db.Column(db.Float, nullable=False)
    range_km = db.Column(db.Integer, nullable=False)
    top_speed = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<ElectricCar {self.name}>'


class Produse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', cascade='all, delete-orphan', lazy=True))


# Hashing password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check if the hashed password matches
def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha256(user_password.encode()).hexdigest()


def add_new_cars():
    # Define the new cars to add
    new_cars = [
        ElectricCar(name="Tesla Model S", manufacturer="Tesla", battery_capacity=100, range_km=600, top_speed=250,
                    price=79999, image_url="https://www.tesla.com/ownersmanual/images/GUID-5543BA62-932F-46C5-B1EF-44707D4726B2-online-en-US.png"),
        ElectricCar(name="Nissan Leaf", manufacturer="Nissan", battery_capacity=40, range_km=270, top_speed=144,
                    price=30000, image_url="https://www-europe.nissan-cdn.net/content/dam/Nissan/global/vehicles/leaf/b12p/eulhd/0_all_new/overview/18tdieulhd-leafhelios121.jpg.ximg.l_6_m.smart.jpg"),
        ElectricCar(name="Chevrolet Bolt", manufacturer="Chevrolet", battery_capacity=66, range_km=417, top_speed=150,
                    price=36000, image_url="https://autolatest.ro/wp-content/uploads/2023/04/r687o089.jpg"),
        ElectricCar(name="BMW i3", manufacturer="BMW", battery_capacity=42.2, range_km=285, top_speed=150, price=45000,
                    image_url="https://masini-electrice.ro/images/modele/bmw-i3-smaller.webp"),
        ElectricCar(name="Audi e-tron", manufacturer="Audi", battery_capacity=95, range_km=400, top_speed=200,
                    price=70000, image_url="https://static.automarket.ro/img/auto_resized/db/article/099/791/136766l-1000x640-b-c8b7c564.jpg"),
        ElectricCar(name="Mercedes EQC", manufacturer="Mercedes-Benz", battery_capacity=80, range_km=400, top_speed=180,
                    price=80000, image_url="https://static.automarket.ro/v5/img/auto_resized/db/model/005/253/676585-1000x637-b-76abfab8/--af724c92/mercedes-benz-eqc.jpg"),
        ElectricCar(name="Porsche Taycan", manufacturer="Porsche", battery_capacity=93, range_km=450, top_speed=260,
                    price=150000, image_url="https://stimg.cardekho.com/images/carexteriorimages/630x420/Porsche/Taycan-2024/11515/1707404051019/front-left-side-47.jpg?tr=w-664"),
        ElectricCar(name="Hyundai Kona Electric", manufacturer="Hyundai", battery_capacity=64, range_km=484,
                    top_speed=167, price=37000, image_url="https://ev-database.org/img/auto/Hyundai_Kona_Electric_2024/Hyundai_Kona_Electric_2024-02@2x.jpg"),
        ElectricCar(name="Jaguar I-Pace", manufacturer="Jaguar", battery_capacity=90, range_km=470, top_speed=200,
                    price=80000, image_url="https://www.autocar.co.uk/sites/autocar.co.uk/files/styles/gallery_slide/public/01-jaguar-i-pace-sport-400-rt-2023-lead-driving.jpg?itok=2sXMYz9-"),
        ElectricCar(name="Kia Soul EV", manufacturer="Kia", battery_capacity=64, range_km=452, top_speed=167,
                    price=35000, image_url="https://www.topgear.com/sites/default/files/2023/06/Large-22108-SoulEVExplore.jpg?w=976&h=549"),
        ElectricCar(name="Volkswagen ID.4", manufacturer="Volkswagen", battery_capacity=77, range_km=520, top_speed=180,
                    price=45000, image_url="https://masini-electrice.ro/images/modele/ID4-Reveal-Quiz-Results-Hero-M.webp"),
        ElectricCar(name="Ford Mustang Mach-E", manufacturer="Ford", battery_capacity=88, range_km=500, top_speed=180,
                    price=60000, image_url="https://hips.hearstapps.com/hmg-prod/images/2025-ford-mustang-mach-e-premium-sport-appearance-exterior-104-67166e9edffb1.jpg?crop=1.00xw:0.970xh;0,0.0303xh&resize=1200:*"),
        ElectricCar(name="Renault Zoe", manufacturer="Renault", battery_capacity=52, range_km=395, top_speed=140,
                    price=25000, image_url="https://upload.wikimedia.org/wikipedia/commons/c/c6/2018_Renault_ZOE.jpg"),
        ElectricCar(name="Honda e", manufacturer="Honda", battery_capacity=35.5, range_km=220, top_speed=145,
                    price=30000, image_url="https://upload.wikimedia.org/wikipedia/commons/1/16/Honda_e_Advance_%E2%80%93_f_18102020.jpg"),
        ElectricCar(name="Mazda MX-30", manufacturer="Mazda", battery_capacity=35.5, range_km=200, top_speed=140,
                    price=34000, image_url="https://upload.wikimedia.org/wikipedia/commons/f/fb/2021_Mazda_MX-30_Front.jpg"),
        ElectricCar(name="Mini Electric", manufacturer="Mini", battery_capacity=32.6, range_km=235, top_speed=150,
                    price=32000, image_url="https://upload.wikimedia.org/wikipedia/commons/2/29/Mini_Hatch_%28F56%29_Electric_IMG_2679.jpg"),
        ElectricCar(name="Lucid Air", manufacturer="Lucid Motors", battery_capacity=113, range_km=830, top_speed=270,
                    price=95000, image_url="https://upload.wikimedia.org/wikipedia/commons/2/26/2022_Lucid_Air_Grand_Touring_in_Zenith_Red%2C_front_left.jpg"),
        ElectricCar(name="Tesla Model X", manufacturer="Tesla", battery_capacity=100, range_km=560, top_speed=250,
                    price=90000, image_url="https://upload.wikimedia.org/wikipedia/commons/9/92/2017_Tesla_Model_X_100D_Front.jpg"),
        ElectricCar(name="Tesla Model 3", manufacturer="Tesla", battery_capacity=82, range_km=580, top_speed=233,
                    price=55000, image_url="https://upload.wikimedia.org/wikipedia/commons/9/91/2019_Tesla_Model_3_Performance_AWD_Front.jpg"),
        ElectricCar(name="Peugeot e-208", manufacturer="Peugeot", battery_capacity=50, range_km=340, top_speed=150,
                    price=31000, image_url="https://upload.wikimedia.org/wikipedia/commons/c/ca/Peugeot_e-208_facelift_Auto_Zuerich_2023_1X7A1204.jpg"),
        ElectricCar(name="Opel Corsa-e", manufacturer="Opel", battery_capacity=50, range_km=337, top_speed=150,
                    price=30000, image_url="https://upload.wikimedia.org/wikipedia/commons/3/35/Opel_Corsa_1.3_CDTI_ecoFLEX_Innovation_%28E%29_%E2%80%93_Frontansicht%2C_24._Dezember_2015%2C_Ratingen.jpg"),
        ElectricCar(name="Volvo XC40 Recharge", manufacturer="Volvo", battery_capacity=78, range_km=418, top_speed=180,
                    price=55000, image_url="https://upload.wikimedia.org/wikipedia/commons/2/2b/Volvo_XC40_Recharge_Facelift_Leonberg_2022_1X7A0435.jpg"),
        ElectricCar(name="Skoda Enyaq iV", manufacturer="Skoda", battery_capacity=77, range_km=510, top_speed=160,
                    price=45000, image_url="https://upload.wikimedia.org/wikipedia/commons/2/24/Skoda_Enyaq_iV_80_%E2%80%93_f1_03052021_%28colour_corrected%29.jpg"),
        ElectricCar(name="Dacia Spring", manufacturer="Dacia", battery_capacity=27.4, range_km=230, top_speed=125,
                    price=22000,
                    image_url="https://upload.wikimedia.org/wikipedia/commons/0/02/2023_Dacia_Spring_1X7A6325.jpg")

    ]



    # Filter out cars that are already in the database
    for car in new_cars:
        existing_car = ElectricCar.query.filter_by(name=car.name).first()
        if not existing_car:
            db.session.add(car)
            print(f"Added {car.name} to the database.")
        else:
            print(f"{car.name} already exists in the database.")

    # Commit the new cars to the database
    db.session.commit()


@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('User exists')
        else:
            hashed_password = hash_password(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/guide')
def guide():
    return "Guide page"

@app.route('/news')
def news():
    return render_template("stiri.html")

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/market')
def market():
    return render_template('market.html')

@app.route('/recenzii')
def recenzii():
    return render_template('market.html')

@app.route("/chatbot", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.json.get("message")
        if user_input:
            ai_response = generate_response(user_input)
            return jsonify({"response": ai_response})
    return render_template("chat.html")

@app.route('/forumMenu')
def forumMenu():
    return render_template("meniuri.html", heading1='COMUNITATE\nENTUZIAȘTI EV', heading2='ȘTIRI \n ȘI ACTUALIZĂRI', heading3='CHATBOT \n SUPPORT', button1='forum',
                           button2='news', button3='chat', image_url1="/static/images/forum.png", image_url2="/static/images/benNews.jpg", image_url3="/static/images/chatBot.jpeg")

@app.route('/marketMenu')
def marketMenu():
    return render_template("meniuri.html", heading1='COMPARĂ \n MAȘINI EV', heading2='GĂSEȘTE \n PIESE',
                           heading3='RECENZII \n SPECIALIȘTI', button1='cars',
                           button2='market', button3='chat',image_url1="/static/images/comp.png", image_url2="/static/images/magazin.png", image_url3="/static/images/rec.png")

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_post = Post(content=content, user_id=session['user_id'])
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('forum'))

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    user = User.query.filter_by(id=session['user_id']).first()
    return render_template('forum.html', posts=posts, user=user)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)

    # Check if the user is the owner of the post
    if post.user_id != session['user_id']:
        flash("You are not authorized to delete this post.")
        return redirect(url_for('forum'))

    # Delete the post and all related comments
    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully.")
    return redirect(url_for('forum'))


@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    content = request.form.get('content')
    if content:
        new_comment = Comment(content=content, user_id=session['user_id'], post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()

    return redirect(url_for('forum'))

@app.route('/cars')
def cars():
    all_cars = ElectricCar.query.all()
    cars_data = [
        {
            "id": car.id,
            "name": car.name,
            "manufacturer": car.manufacturer,
            "battery_capacity": car.battery_capacity,
            "range_km": car.range_km,
            "top_speed": car.top_speed,
            "price": car.price,
            "image_url": car.image_url,
        }
        for car in all_cars
    ]
    return render_template('cars.html', cars=cars_data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_new_cars()# Populează baza de date doar dacă este necesar
    app.run(debug=True)
