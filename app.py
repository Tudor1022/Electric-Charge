import hashlib
from sqlite3 import IntegrityError
from tkinter import Image
import articles as art
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import openai
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import generate_password_hash
from emailSender import send_email

api_key = "f45d2cc26b2e44428f9f14b0336bd7e0"
base_url = "https://api.aimlapi.com/v1"
system_prompt = "conversation related to electric cars"

openai.api_key = api_key
openai.api_base = base_url

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

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

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
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    product_url = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Add email column
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

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_start = db.Column(db.String(20), nullable=False)
    date_end = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha256(user_password.encode()).hexdigest()



def add_new_products():
    new_products = [
        Produse(id=3, name="WALLBOX PULSAR PLUS EV 48A CHARGING STATION",
                image_url="https://amprevolt.com/cdn/shop/products/ScreenShot2022-01-29at11.47.33AM_1800x1800.png?v=1643474982",
                product_url="https://amprevolt.com/collections/charging-stations/products/wallbox-pulsar-plus-ev-charging-station",
                price=649.00),
        Produse(id=4, name="Charging Inlet",
                image_url="https://amprevolt.com/cdn/shop/products/J1772.2.optimized_1800x1800.jpg?v=1595801419",
                product_url="https://amprevolt.com/collections/charging-accessories/products/j1772-inlet-port",
                price=125.00),
        Produse(id=5, name="BUSBARS FOR STACKED TESLA BATTERY MODULES",
                image_url="https://amprevolt.com/cdn/shop/products/tesla-battery-module-bus-bar-1-white_540x.jpg?v=1593228568",
                product_url="https://amprevolt.com/collections/electrical/products/busbars-for-stacked-tesla-battery-modules",
                price=45.00),
        Produse(id=6, name="Percharge Resistor",
                image_url="https://amprevolt.com/cdn/shop/products/battery-module-right-angle-busbar-1-white_540x.jpg?v=1593228886",
                product_url="https://www.google.com/url?q=https://amprevolt.com/collections/motor-accessories/products/precharge-resistor&sa=D&source=editors&ust=1731763582927313&usg=AOvVaw2KwFN3lq8qcPAzjZnrnuSXLT",
                price=32.00),
        Produse(id=7, name="Tesla Battery Module Right Angle Busbar",
                image_url="https://amprevolt.com/cdn/shop/products/CALBoptimized_1800x1800.jpg?v=1593216270",
                product_url="https://www.google.com/url?q=https://amprevolt.com/collections/battery-accessories/products/tesla-battery-module-right-angle-busbar&sa=D&source=editors&ust=1731763582927994&usg=AOvVaw1AUqzhvIL5k4m7NBX7bOFB",
                price=15.70),
        Produse(id=8, name="CALB LITHIUM IRON PHOSPHATE CELL-CA SERIES",
                image_url="https://amprevolt.com/cdn/shop/products/CALBoptimized_1800x1800.jpg?v=1593216270",
                product_url="https://www.google.com/url?q=https://amprevolt.com/collections/batteries/products/calb-lithium-iron-phosphate-cell&sa=D&source=editors&ust=1731763582928630&usg=AOvVaw0ZNT4coB314n0lY3krKjgS",
                price=150.00),
        Produse(id=9, name="LECTRON TESLA/J1772 ADAPTER",
                image_url="https://amprevolt.com/cdn/shop/products/IMG_20220920_130903_480_1800x1800.jpg?v=1669043588",
                product_url="https://www.google.com/url?q=https://amprevolt.com/collections/charging-stations/products/tesla-j1772-adapter&sa=D&source=editors&ust=1731763582929239&usg=AOvVaw338F8lTvVj-apIhWwdTBf_",
                price=159.00),
        Produse(id=10, name="TSM 600W DC-DC CONVERTER",
                image_url="https://amprevolt.com/cdn/shop/products/tsm-dc-converter-1-white_540x.jpg?v=1593229382",
                product_url="https://www.google.com/url?q=https://amprevolt.com/collections/brakes/products/vacuum-switch&sa=D&source=editors&ust=1731763582930636&usg=AOvVaw14D9_8OxW2kutOGioT-lia",
                price=200.00),
        Produse(id=11, name="CVR VACUUM SWITCH",
                image_url="https://amprevolt.com/cdn/shop/products/ScreenShot2022-05-18at6.22.19PM_1800x1800.png?v=1652912561",
                product_url="https://www.google.com/url?q=https://amprevolt.com/collections/brakes/products/vacuum-switch&sa=D&source=editors&ust=1731763582930636&usg=AOvVaw14D9_8OxW2kutOGioT-lia",
                price=76.00),
        Produse(id=12, name="Ampseal 23-pin Connector",
                image_url="https://amprevolt.com/cdn/shop/products/ampseal-23-pin-connector-optimized_1800x1800.jpg?v=1681392103",
                product_url="https://amprevolt.com/collections/controller-accessories/products/ampseal-23-pin-connector",
                price=16.40),
        Produse(id=13, name="NetGain Micro 840 System",
                image_url="https://amprevolt.com/cdn/shop/files/Micro840_Motor_image1_1800x1800.png?v=1725036157",
                product_url="https://amprevolt.com/collections/motors/products/netgain-micro-840-system",
                price=2825.00),
        Produse(id=14, name="2/0 AWG Cable",
                image_url="https://amprevolt.com/cdn/shop/files/OrangeCable20_1800x1800.png?v=1727368098",
                product_url="https://amprevolt.com/collections/electrical/products/2-0-awg-cable",
                price=7.25),
        Produse(id=15, name="12V Power Supply",
                image_url="https://amprevolt.com/cdn/shop/files/MFG_WSU-Series_360x.jpg?v=1711139642",
                product_url="https://amprevolt.com/collections/electrical/products/12v-power-supply",
                price=13.00),
        Produse(id=16, name="J+ Booster Portable EVSE, 21 ft. cable",
                image_url="https://amprevolt.com/cdn/shop/products/IMG_20220920_132041_898_1800x1800.jpg?v=1669044692",
                product_url="https://amprevolt.com/collections/charging-stations/products/j-booster-portable-evse-21-ft-cable",
                price=745.00),
        Produse(id=17, name="TBS E-Xpert Pro Display",
                image_url="https://amprevolt.com/cdn/shop/products/tbs-expert-pro-1-white_1800x1800.jpg?v=1593228374",
                product_url="https://amprevolt.com/collections/instrumentation/products/tbs-e-xpert-pro",
                price=225.00),
        Produse(id=18, name="CVR Vacuum Switch",
                image_url="https://amprevolt.com/cdn/shop/products/ScreenShot2022-05-18at6.22.19PM_360x.png?v=1652912561",
                product_url="https://amprevolt.com/collections/brakes/products/vacuum-switch",
                price=76.00)
    ]

    # Add new products, avoiding duplicates
    for product in new_products:
        existing_product = Produse.query.filter_by(name=product.name).first()
        if not existing_product:
            db.session.add(product)
            print(f"Added {product.name} to the database.")
        else:
            print(f"{product.name} already exists in the database.")

    # Commit the changes to the database
    db.session.commit()
    print("All new products added successfully!")


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

def add_new_events():
    new_events = [
        Event(
            name="Green Car Expo 2025",
            date_start="2024-11-15",
            date_end="2024-11-17",
            location="Iași, Palas Mall",
            description="Expoziție dedicată vehiculelor electrice și hibrid, cu posibilitatea de a testa diverse modele și de a participa la workshop-uri despre mobilitatea sustenabilă."
        ),
        Event(
            name="Salonul Auto București 2025",
            date_start="2024-12-20",
            date_end="2024-07-30",
            location="București, Romexpo",
            description="Expoziție auto de anvergură, cu o secțiune specială dedicată vehiculelor electrice și hibrid, unde producătorii își prezintă cele mai noi modele și tehnologii."
        ),
        Event(
            name="Electric Drive 2025",
            date_start="2025-01-10",
            date_end="2025-01-12",
            location="Cluj-Napoca, Sala Polivalentă",
            description="Conferință și expoziție axată pe infrastructura de încărcare, inovații în baterii și soluții de mobilitate electrică urbană."
        ),
        Event(
            name="E-Mobility Forum 2025",
            date_start="2025-02-05",
            date_end="2025-02-06",
            location="Timișoara, Centrul Regional de Afaceri",
            description="Forum ce reunește experți în mobilitate electrică, autorități locale și investitori, discutând despre dezvoltarea infrastructurii și adoptarea vehiculelor electrice în România."
        ),
        Event(
            name="Conferința Națională de Mobilitate Electrică 2025",
            date_start="2025-02-15",
            date_end="2025-02-16",
            location="București, Palatul Parlamentului",
            description="Eveniment dedicat politicilor și strategiilor naționale privind mobilitatea electrică, reunind factori de decizie, producători auto și experți în domeniu."
        )
    ]

    # Add new events, avoiding duplicates
    for event in new_events:
        existing_event = Event.query.filter_by(name=event.name).first()
        if not existing_event:
            db.session.add(event)
            print(f"Added {event.name} to the database.")
        else:
            print(f"{event.name} already exists in the database.")

    # Commit the changes to the database
    db.session.commit()
    print("All new events added successfully!")


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
        email = request.form.get('email')  # Fetch the email field
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields are required!")
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Add user to the database
        new_user = User(username=username, email=email, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("This email is already registered.")
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  # Use werkzeug's check_password_hash
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')



@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        # Check if email exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a new password
            new_password = generate_random_password()
            hashed_password = hash_password(new_password)

            # Update user's password in the database
            user.password = hashed_password
            db.session.commit()

            # Send the new password to the user's email
            send_email(email, new_password)  # Define the send_email function below

            flash("A new password has been sent to your email.")
            return redirect(url_for('login'))
        else:
            flash("No account found with this email.")

    return render_template('forgotPassword.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/guide')
def guide():
    return "Guide page"

@app.route('/atractii')
def atractii():
    return render_template("atractii.html")

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/api/events')
def get_events():
    events = Event.query.all()
    event_data = [
        {
            "title": event.name,
            "start": event.date_start,
            "end": event.date_end,
            "location": event.location,
            "description": event.description
        }
        for event in events
    ]
    return jsonify(event_data)

@app.route('/news')
def news():
    return render_template("stiri.html")

@app.route('/hyumdaiArticle')
def hyumdaiArticle():
    return render_template("artico.html", title="Noutati Kia", content=art.articolKia, image_url="https://assets.newatlas.com/dims4/default/e5bd2b3/2147483647/strip/true/crop/6000x4000+0+0/resize/840x560!/quality/90/?url=http%3A%2F%2Fnewatlas-brightspot.s3.amazonaws.com%2Fad%2Fa9%2Fb8f822d94e85a60c8d81defdae5c%2F2022-kia-ev6-2.JPG")

@app.route('/viitorEvArticle')
def viitorEvArticle():
    return render_template("artico.html", title="Cum ar putea arata viitorul masinilor EV?", content=art.viitor, image_url="https://cdn.g4media.ro/wp-content/uploads/2023/07/masina-viitorului.jpeg")

@app.route('/indiaArticle')
def indiaArticle():
    return render_template("artico.html", title="Cele mai durabile masini cu range electric in India .", content=art.india, image_url="https://spn-sta.spinny.com/blog/20230907221752/Tata-Nexon-EV-5-jpg.webp?compress=true&quality=80&w=1100&dpr=1.3")

@app.route('/cybertruckArticle')
def cybertruckArticle():
    return render_template("artico.html", title="Cybertruck pe strazile din Romania", content=art.cybertruck, image_url="https://hips.hearstapps.com/hmg-prod/images/2025-tesla-cybertruck-3-672e75cce7814.jpg?crop=0.607xw:0.512xh;0.0994xw,0.399xh&resize=1200:*")


@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/market', methods=['GET'])
def market():
    products = Produse.query.all()
    return render_template('market.html', products=products)


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query', '').strip()
    if query:
        filtered_products = Produse.query.filter(Produse.name.contains(query)).all()
        return render_template('market.html', products=filtered_products, query=query)
    else:
        flash("Enter a valid search term!", "warning")
        return redirect(url_for('market'))


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
        db.drop_all()
        db.create_all()
        add_new_cars()
        add_new_events()
        add_new_products()
    app.run(debug=True)
