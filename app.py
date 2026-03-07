from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MongoDB Connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['booking_website']
users_collection = db['users']
bookings_collection = db['bookings']
lectures_collection = db['lectures']

# Create indexes for better performance
users_collection.create_index('email', unique=True)

# ==================== HELPER FUNCTIONS ====================

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Verify password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page - redirects to login if not logged in"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            flash('Email already registered! Please login.', 'error')
            return render_template('register.html')
        
        # Create new user
        hashed_password = hash_password(password)
        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.now(),
            'booking_history': []
        }
        
        try:
            users_collection.insert_one(user_data)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation
        if not all([email, password]):
            flash('Email and password are required!', 'error')
            return render_template('login.html')
        
        # Find user
        user = users_collection.find_one({'email': email})
        
        if user and check_password(password, user['password']):
            # Login successful
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User Logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard - Upcoming Lectures Page"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    # Get filter and sort parameters
    sort_by = request.args.get('sort', 'date')  # default: sort by date
    filter_week = request.args.get('week', 'all')  # this_week, next_week, all
    search_query = request.args.get('search', '').strip()
    
    # Fetch lectures from database
    query = {}
    
    # Filter by week
    if filter_week == 'this_week':
        start_of_week = datetime.now()
        end_of_week = start_of_week + timedelta(days=7)
        query['date'] = {'$gte': start_of_week, '$lte': end_of_week}
    elif filter_week == 'next_week':
        start_of_next_week = datetime.now() + timedelta(days=7)
        end_of_next_week = start_of_next_week + timedelta(days=7)
        query['date'] = {'$gte': start_of_next_week, '$lte': end_of_next_week}
    
    # Search functionality (Linear Search concept)
    if search_query:
        query['$or'] = [
            {'youtuber_name': {'$regex': search_query, '$options': 'i'}},
            {'topic': {'$regex': search_query, '$options': 'i'}},
            {'lecture_title': {'$regex': search_query, '$options': 'i'}}
        ]
    
    # Fetch lectures
    lectures = list(lectures_collection.find(query))
    
    # Sorting (Bubble Sort / Shell Sort implementation in Python)
    lectures = sort_lectures(lectures, sort_by)
    
    # Debug: Print to console
    print(f"Found {len(lectures)} lectures")
    print(f"Sort by: {sort_by}, Filter: {filter_week}")
    
    return render_template('dashboard.html', 
                         user_name=session.get('user_name', 'Guest'),
                         lectures=lectures,
                         current_sort=sort_by,
                         current_filter=filter_week,
                         search_query=search_query)

def sort_lectures(lectures, sort_by):
    """Bubble Sort implementation for sorting lectures"""
    n = len(lectures)
    
    if sort_by == 'date':
        # Bubble Sort by date
        for i in range(n):
            for j in range(0, n-i-1):
                if lectures[j]['date'] > lectures[j+1]['date']:
                    lectures[j], lectures[j+1] = lectures[j+1], lectures[j]
    
    elif sort_by == 'price':
        # Sort by lowest price (back seats)
        for i in range(n):
            for j in range(0, n-i-1):
                if lectures[j]['price_back'] > lectures[j+1]['price_back']:
                    lectures[j], lectures[j+1] = lectures[j+1], lectures[j]
    
    elif sort_by == 'popularity':
        # Sort by seats booked (total_seats - available_seats)
        for i in range(n):
            for j in range(0, n-i-1):
                booked_j = lectures[j]['total_seats'] - lectures[j]['available_seats']
                booked_j1 = lectures[j+1]['total_seats'] - lectures[j+1]['available_seats']
                if booked_j < booked_j1:
                    lectures[j], lectures[j+1] = lectures[j+1], lectures[j]
    
    elif sort_by == 'seats':
        # Sort by available seats (descending)
        for i in range(n):
            for j in range(0, n-i-1):
                if lectures[j]['available_seats'] < lectures[j+1]['available_seats']:
                    lectures[j], lectures[j+1] = lectures[j+1], lectures[j]
    
    return lectures

@app.route('/book/<lecture_id>')
def book_lecture(lecture_id):
    """Seat Booking Page"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    from bson.objectid import ObjectId
    
    # Fetch lecture details
    try:
        lecture = lectures_collection.find_one({'_id': ObjectId(lecture_id)})
        if not lecture:
            flash('Lecture not found!', 'error')
            return redirect(url_for('dashboard'))
    except:
        flash('Invalid lecture ID!', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate seat layout (Array visualization)
    seats = generate_seat_layout(lecture)
    
    return render_template('booking.html',
                         user_name=session['user_name'],
                         lecture=lecture,
                         lecture_id=lecture_id,
                         seats=seats)

def generate_seat_layout(lecture):
    """Generate 60 seats with array structure"""
    seats = []
    seat_number = 1
    
    # Front rows (20 seats) - Rows A, B, C, D
    for row in ['A', 'B', 'C', 'D']:
        row_seats = []
        for col in range(1, 6):  # 5 seats per row
            seat_id = f"{row}{col}"
            row_seats.append({
                'id': seat_id,
                'number': seat_number,
                'row': row,
                'section': 'front',
                'price': lecture['price_front'],
                'status': 'available'  # available, selected, booked
            })
            seat_number += 1
        seats.append(row_seats)
    
    # Middle rows (20 seats) - Rows E, F, G, H
    for row in ['E', 'F', 'G', 'H']:
        row_seats = []
        for col in range(1, 6):
            seat_id = f"{row}{col}"
            row_seats.append({
                'id': seat_id,
                'number': seat_number,
                'row': row,
                'section': 'mid',
                'price': lecture['price_mid'],
                'status': 'available'
            })
            seat_number += 1
        seats.append(row_seats)
    
    # Back rows (20 seats) - Rows I, J, K, L
    for row in ['I', 'J', 'K', 'L']:
        row_seats = []
        for col in range(1, 6):
            seat_id = f"{row}{col}"
            row_seats.append({
                'id': seat_id,
                'number': seat_number,
                'row': row,
                'section': 'back',
                'price': lecture['price_back'],
                'status': 'available'
            })
            seat_number += 1
        seats.append(row_seats)
    
    return seats

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    """Process booking and generate QR code + Receipt"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    from bson.objectid import ObjectId
    import qrcode
    from io import BytesIO
    import base64
    import json
    from datetime import datetime
    
    # Get booking data
    lecture_id = request.form.get('lecture_id')
    selected_seats = json.loads(request.form.get('selected_seats'))
    total_amount = int(request.form.get('total_amount'))
    
    # Fetch lecture details
    try:
        lecture = lectures_collection.find_one({'_id': ObjectId(lecture_id)})
        if not lecture:
            flash('Lecture not found!', 'error')
            return redirect(url_for('dashboard'))
    except:
        flash('Invalid booking!', 'error')
        return redirect(url_for('dashboard'))
    
    # Create booking record
    booking_data = {
        'user_id': session['user_id'],
        'user_name': session['user_name'],
        'user_email': session['user_email'],
        'lecture_id': lecture_id,
        'lecture_title': lecture['lecture_title'],
        'youtuber_name': lecture['youtuber_name'],
        'lecture_date': lecture['date'],
        'venue': lecture['venue'],
        'seats': selected_seats,
        'total_amount': total_amount,
        'booking_date': datetime.now(),
        'booking_id': f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'status': 'confirmed'
    }
    
    # Insert booking
    result = bookings_collection.insert_one(booking_data)
    booking_id = str(result.inserted_id)
    
    # Generate QR Code
    qr_data = {
        'booking_id': booking_data['booking_id'],
        'user': session['user_name'],
        'lecture': lecture['lecture_title'],
        'seats': [seat['id'] for seat in selected_seats],
        'amount': total_amount
    }
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Update lecture seats (decrease available_seats)
    lectures_collection.update_one(
        {'_id': ObjectId(lecture_id)},
        {'$inc': {'available_seats': -len(selected_seats)}}
    )
    
    flash('Booking confirmed successfully!', 'success')
    return render_template('booking_success.html',
                         booking=booking_data,
                         qr_code=qr_code_base64,
                         booking_id=booking_id)

@app.route('/my-bookings')
def my_bookings():
    """User's Booking History (Linked List Visualization)"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    # Fetch user's bookings (Array/Linked List concept)
    bookings = list(bookings_collection.find({'user_id': session['user_id']}).sort('booking_date', -1))
    
    return render_template('booking_history.html',
                         user_name=session['user_name'],
                         bookings=bookings)

@app.route('/download-receipt/<booking_id>')
def download_receipt(booking_id):
    """Generate and download PDF receipt"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from bson.objectid import ObjectId
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from flask import make_response
    import io
    
    # Fetch booking
    try:
        booking = bookings_collection.find_one({'_id': ObjectId(booking_id)})
        if not booking or booking['user_id'] != session['user_id']:
            flash('Booking not found!', 'error')
            return redirect(url_for('my_bookings'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('my_bookings'))
    
    # Create PDF in memory
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Draw header with color
    pdf.setFillColorRGB(0.86, 0, 0)  # Red color #DC0000
    pdf.rect(0, height - 100, width, 100, fill=True)
    
    pdf.setFillColorRGB(1, 1, 1)  # White text
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawString(width/2 - 120, height - 65, "BOOKING RECEIPT")
    
    # Reset to black
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 12)
    y = height - 140
    
    # Booking Details
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, f"Booking ID: {booking['booking_id']}")
    y -= 25
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Date: {booking['booking_date'].strftime('%d %B %Y, %I:%M %p')}")
    y -= 40
    
    # Lecture Details
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Lecture Details:")
    y -= 25
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, f"Title: {booking['lecture_title']}")
    y -= 20
    pdf.drawString(70, y, f"Instructor: {booking['youtuber_name']}")
    y -= 20
    pdf.drawString(70, y, f"Date: {booking['lecture_date'].strftime('%d %B %Y')}")
    y -= 20
    pdf.drawString(70, y, f"Venue: {booking['venue']}")
    y -= 40
    
    # Passenger Details
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Passenger Details:")
    y -= 25
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, f"Name: {booking['user_name']}")
    y -= 20
    pdf.drawString(70, y, f"Email: {booking['user_email']}")
    y -= 40
    
    # Seats
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Seats Booked:")
    y -= 25
    pdf.setFont("Helvetica", 11)
    seats_str = ", ".join([seat['id'] for seat in booking['seats']])
    pdf.drawString(70, y, seats_str)
    y -= 40
    
    # Total
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColorRGB(0.86, 0, 0)
    pdf.drawString(50, y, f"Total Amount: ₹{booking['total_amount']}")
    
    # Footer
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Italic", 10)
    pdf.drawString(50, 50, "Thank you for booking with us!")
    pdf.drawString(50, 35, "Show this receipt and QR code at the venue entrance.")
    
    pdf.save()
    buffer.seek(0)
    
    # Create response
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=receipt_{booking["booking_id"]}.pdf'
    
    return response

@app.route('/career-path')
def career_path():
    """Career Path Finder using Dijkstra's Algorithm"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    return render_template('career_path.html', user_name=session['user_name'])

@app.route('/qr-scanner')
def qr_scanner():
    return render_template('qr_scanner.html')


@app.route('/subject-navigator')
def subject_navigator():
    """Multi-Subject Learning Navigator using BFS/DFS"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    return render_template('subject_navigator.html', user_name=session['user_name'])

@app.route('/priority-heap')
def priority_heap():
    """Priority Queue and Heap Visualization"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    return render_template('priority_heap.html', user_name=session['user_name'])

@app.route('/resources')
def resources():
    """YouTube Playlists and Books"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    return render_template('resources.html', user_name=session['user_name'])

# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)