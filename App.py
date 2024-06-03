from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'car_rental.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            license TEXT NOT NULL,
            car_model TEXT NOT NULL,
            rental_hours INTEGER NOT NULL,
            total_cost REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_car')
def select_car():
    return render_template('select_car.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    car_model = request.args.get('car_model')
    price_per_hour = request.args.get('price_per_hour')
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        phone = request.form['phone']
        license = request.files['license']
        
        filename = license.filename
        license.save(os.path.join('static/uploads', filename))
        
        rental_hours = request.form.get('rental_hours')  # Use request.form.get() to avoid KeyError
        if rental_hours is None:
            # Handle case when rental_hours is not provided
            flash('Rental hours not provided!', 'error')
            return redirect(url_for('booking'))
        
        total_cost = int(rental_hours) * float(price_per_hour)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookings (name, age, email, phone, license, car_model, rental_hours, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, email, phone, filename, car_model, rental_hours, total_cost))
        conn.commit()
        conn.close()
        
        flash('Booking successful!', 'success')
        return redirect(url_for('payment', car_model=car_model, price_per_hour=price_per_hour, rental_hours=rental_hours, total_cost=total_cost))
    return render_template('booking.html', car_model=car_model, price_per_hour=price_per_hour)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    car_model = request.args.get('car_model')
    price_per_hour = request.args.get('price_per_hour')
    rental_hours = request.args.get('rental_hours')
    total_cost = request.args.get('total_cost')
    
    if request.method == 'POST':
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']

        flash('Payment successful!', 'success')
        return redirect(url_for('thank_you'))
    
    return render_template('payment.html', car_model=car_model, price_per_hour=price_per_hour, rental_hours=rental_hours, total_cost=total_cost)

@app.route('/thank_you')
def thank_you():
    return render_template('thankyou.html')

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
