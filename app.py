from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, db, auth
from werkzeug.utils import secure_filename
import os

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smartparkingsystem-715a8-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if 'user' in session:
        # Fetch the current user's data from Firebase
        user = auth.get_user(session['user'])
        user_ref = db.reference(f'users/{user.uid}').get() or {}
        user_data = {
            'email': user.email,
            'staff_number': user_ref.get('staff_number', 'N/A'),
            'mobile_number': user_ref.get('mobile_number', 'N/A'),
            'role': user_ref.get('role', 'N/A')
        }
        return render_template('index.html', user=user_data)
    else:
        return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Create user in Firebase Authentication
            user = auth.create_user(email=request.form['email'], password=request.form['password'])
            session['user'] = user.uid

            # Store user details in pendingRegistrations (waiting for admin approval)
            user_data = {
                'email': request.form['email'],
                'staff_number': request.form['staff_number'],
                'mobile_number': request.form['mobile_number'],
                'role': request.form['role'],
                'photo_url': 'https://via.placeholder.com/150',  # Default profile picture
                'status': 'pending'  # Waiting for admin approval
            }
            db.reference(f'pendingRegistrations/{user.uid}').set(user_data)

            return redirect(url_for('home'))  # Redirect to home page after registration
        except auth.EmailAlreadyExistsError:
            return "Email already exists", 400
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = auth.get_user_by_email(request.form['email'])
            session['user'] = user.uid
            return redirect(url_for('get_slots'))
        except auth.UserNotFoundError:
            return "User not found", 400
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        user = auth.get_user(session['user'])
        user_ref = db.reference(f'users/{user.uid}').get() or {}
        user_data = {
            'staff_number': user_ref.get('staff_number', 'N/A'),
            'mobile_number': user_ref.get('mobile_number', 'N/A'),
            'role': user_ref.get('role', 'N/A'),
            'photo_url': user_ref.get('photo_url', 'https://via.placeholder.com/150')
        }
        return render_template('profile.html', user={**user.__dict__, **user_data})
    except Exception as e:
        print("Error fetching user:", e)
        return "An error occurred while fetching user data", 500

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'profile_picture' not in request.files:
        return "No file uploaded", 400

    file = request.files['profile_picture']
    if file.filename == '':
        return "No file selected", 400

    if file and allowed_file(file.filename):
        # Save the file to the upload folder
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Update the user's profile picture URL in Firebase
        photo_url = f"/static/uploads/{filename}"
        db.reference(f'users/{session["user"]}').update({'photo_url': photo_url})

        return redirect(url_for('profile'))
    else:
        return "Invalid file type", 400

@app.route('/slots')
def get_slots():
    if 'user' not in session:
        return redirect(url_for('login'))
    slots = db.reference('parkingSlots').get() or {}
    slots = {slot_id: slot['status'] for slot_id, slot in slots.items()}
    return render_template('slots.html', slots=slots)

@app.route('/book/<slot_id>', methods=['POST'])
def book_slot(slot_id):
    if 'user' not in session:
        return "Unauthorized", 401
    db.reference(f'parkingSlots/{slot_id}').update({'status': 'Booked'})
    return redirect(url_for('get_slots'))

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not authenticated

    # Fetch the current user's role from Firebase
    user = auth.get_user(session['user'])
    user_ref = db.reference(f'users/{user.uid}').get()
    if user_ref and user_ref.get('role') == 'Admin':
        # Fetch all pending registrations
        pending_registrations = db.reference('pendingRegistrations').get() or {}
        # Fetch all registered users
        registered_users = db.reference('users').get() or {}
        return render_template('admin.html', pending_registrations=pending_registrations, registered_users=registered_users)
    else:
        return "Unauthorized", 403  # Only admins can access this page

@app.route('/admin/approve', methods=['POST'])
def admin_approve():
    if 'user' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not authenticated

    # Fetch the current user's role from Firebase
    user = auth.get_user(session['user'])
    user_ref = db.reference(f'users/{user.uid}').get()
    if user_ref and user_ref.get('role') == 'Admin':
        user_id = request.form['user_id']
        action = request.form['action']  # 'approve' or 'reject'

        if action == 'approve':
            # Move the user from pendingRegistrations to users
            pending_user = db.reference(f'pendingRegistrations/{user_id}').get()
            db.reference(f'users/{user_id}').set(pending_user)
            db.reference(f'pendingRegistrations/{user_id}').delete()
            return redirect(url_for('admin'))  # Redirect back to the admin page
        elif action == 'reject':
            # Delete the user from pendingRegistrations
            db.reference(f'pendingRegistrations/{user_id}').delete()
            return redirect(url_for('admin'))  # Redirect back to the admin page
        else:
            return "Invalid action", 400
    else:
        return "Unauthorized", 403  # Only admins can perform this action

@app.route('/assign_admin_role')
def assign_admin_role():
    try:
        # Set custom claims for the user
        auth.set_custom_user_claims('https://console.firebase.google.com/project/smartparkingsystem-715a8/database/smartparkingsystem-715a8-default-rtdb/data/~2Fusers~2F4DEGFxQhGVMgcOX2k2Vzpocg5Nl2', {'role': 'Admin'})
        return "Admin role assigned successfully."
    except Exception as e:
        return f"Error assigning Admin role: {e}"

@app.route('/edit_user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    # Fetch the current user's role from Firebase
    user = auth.get_user(session['user'])
    user_ref = db.reference(f'users/{user.uid}').get()
    if user_ref and user_ref.get('role') == 'Admin':
        if request.method == 'POST':
            # Update user details
            updated_data = {
                'email': request.form['email'],
                'staff_number': request.form['staff_number'],
                'mobile_number': request.form['mobile_number'],
                'role': request.form['role']
            }
            db.reference(f'users/{user_id}').update(updated_data)
            return redirect(url_for('admin'))

        # Fetch user details for editing
        user_data = db.reference(f'users/{user_id}').get()
        return render_template('edit_user.html', user=user_data)
    else:
        return "Unauthorized", 403

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Fetch the current user's role from Firebase
    user = auth.get_user(session['user'])
    user_ref = db.reference(f'users/{user.uid}').get()
    if user_ref and user_ref.get('role') == 'Admin':
        user_id = request.form['user_id']
        db.reference(f'users/{user_id}').delete()
        return redirect(url_for('admin'))
    else:
        return "Unauthorized", 403

if __name__ == '__main__':
    app.run(debug=True)