from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import date

from config import SECRET_KEY
from db import cursor, conn

app = Flask(__name__)
app.secret_key = SECRET_KEY


# =====================================================
# LOGIN REQUIRED
# =====================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# =====================================================
# ROLE REQUIRED
# =====================================================

def role_required(*roles):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if "user_id" not in session:
                flash("Please login first.")
                return redirect(url_for("login"))

            if session.get("role") not in roles:
                flash("Access Denied")
                return redirect(url_for("dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        cursor.execute("""
            SELECT *
            FROM Users
            WHERE username=%s
            AND status='Active'
        """, (username,))

        user = cursor.fetchone()

        if user:

            # Support both hashed and plain-text passwords
            valid = False

            try:
                valid = check_password_hash(user["password"], password)
            except Exception:
                pass

            if not valid:
                valid = (user["password"] == password)

            if valid:

                session["user_id"] = user["user_id"]
                session["name"] = user["full_name"]
                session["role"] = user["role"]

                flash(f"Welcome {user['full_name']}")

                return redirect(url_for("dashboard"))

        flash("Invalid Username or Password")

    return render_template("login.html")


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect(url_for("home"))


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    cursor.execute("SELECT COUNT(*) AS total FROM Guests")
    total_guests = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM Rooms")
    total_rooms = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM Bookings")
    total_bookings = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COALESCE(SUM(amount),0) AS revenue
        FROM Payments
    """)
    revenue = cursor.fetchone()["revenue"]

    return render_template(
        "dashboard.html",
        total_guests=total_guests,
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        revenue=revenue,
        username=session.get("name"),
        role=session.get("role")
    )


# =====================================================
# USER MANAGEMENT
# =====================================================

@app.route("/users")
@login_required
@role_required("Chief")
def users():

    cursor.execute("""
        SELECT
            ROW_NUMBER() OVER (ORDER BY user_id) AS serial_no,
            user_id,
            full_name,
            username,
            email,
            phone,
            role,
            status,
            created_at
        FROM Users
        ORDER BY user_id
    """)

    users = cursor.fetchall()

    return render_template(
        "users.html",
        users=users,
        role=session.get("role")
    )


# ======================================
# ADD USER
# ======================================

@app.route("/add_user", methods=["POST"])
@login_required
@role_required("Chief")
def add_user():

    full_name = request.form.get("full_name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    phone = request.form.get("phone")
    role = request.form.get("role")

    if not all([full_name, username, password, email, phone, role]):
        flash("Please fill all fields.")
        return redirect(url_for("users"))

    cursor.execute(
        "SELECT user_id FROM Users WHERE username=%s",
        (username,)
    )

    if cursor.fetchone():
        flash("Username already exists.")
        return redirect(url_for("users"))

    hashed_password = generate_password_hash(password)

    cursor.execute("""
        INSERT INTO Users
        (
            full_name,
            username,
            password,
            email,
            phone,
            role,
            status
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,'Active')
    """,
    (
        full_name,
        username,
        hashed_password,
        email,
        phone,
        role
    ))

    conn.commit()

    flash("Employee Added Successfully")

    return redirect(url_for("users"))


# ======================================
# EDIT USER
# ======================================

@app.route("/edit_user/<int:user_id>", methods=["POST"])
@login_required
@role_required("Chief")
def edit_user(user_id):

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    role = request.form.get("role")

    cursor.execute("""
        UPDATE Users
        SET
            full_name=%s,
            email=%s,
            phone=%s,
            role=%s
        WHERE user_id=%s
    """,
    (
        full_name,
        email,
        phone,
        role,
        user_id
    ))

    conn.commit()

    flash("Employee Updated Successfully")

    return redirect(url_for("users"))


# ======================================
# RESET PASSWORD
# ======================================

@app.route("/reset_password/<int:user_id>", methods=["POST"])
@login_required
@role_required("Chief")
def reset_password(user_id):

    new_password = request.form.get("password")

    if not new_password:
        flash("Password cannot be empty.")
        return redirect(url_for("users"))

    hashed_password = generate_password_hash(new_password)

    cursor.execute("""
        UPDATE Users
        SET password=%s
        WHERE user_id=%s
    """,
    (
        hashed_password,
        user_id
    ))

    conn.commit()

    flash("Password Reset Successfully")

    return redirect(url_for("users"))


# ======================================
# ACTIVATE USER
# ======================================

@app.route("/activate_user/<int:user_id>")
@login_required
@role_required("Chief")
def activate_user(user_id):

    cursor.execute("""
        UPDATE Users
        SET status='Active'
        WHERE user_id=%s
    """,
    (user_id,))

    conn.commit()

    flash("Employee Activated Successfully")

    return redirect(url_for("users"))


# ======================================
# DEACTIVATE USER
# ======================================

@app.route("/deactivate_user/<int:user_id>")
@login_required
@role_required("Chief")
def deactivate_user(user_id):

    if user_id == session.get("user_id"):
        flash("You cannot deactivate your own account.")
        return redirect(url_for("users"))

    cursor.execute("""
        UPDATE Users
        SET status='Inactive'
        WHERE user_id=%s
    """,
    (user_id,))

    conn.commit()

    flash("Employee Deactivated Successfully")

    return redirect(url_for("users"))


# ======================================
# DELETE USER
# ======================================

@app.route("/delete_user/<int:user_id>")
@login_required
@role_required("Chief")
def delete_user(user_id):

    if user_id == session.get("user_id"):
        flash("You cannot delete your own account.")
        return redirect(url_for("users"))

    cursor.execute(
        "DELETE FROM Users WHERE user_id=%s",
        (user_id,)
    )

    conn.commit()

    flash("Employee Deleted Successfully")

    return redirect(url_for("users"))


# ======================================
# SEARCH USERS
# ======================================

@app.route("/search_users")
@login_required
@role_required("Chief")
def search_users():

    keyword = request.args.get("keyword", "").strip()

    cursor.execute("""
        SELECT
            user_id,
            full_name,
            username,
            email,
            phone,
            role,
            status,
            created_at
        FROM Users
        WHERE
            full_name LIKE %s
            OR username LIKE %s
            OR role LIKE %s
        ORDER BY user_id
    """,
    (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    users = cursor.fetchall()

    return render_template(
        "users.html",
        users=users,
        role=session.get("role")
    )
# ======================================
# GUESTS MODULE
# ======================================

@app.route("/guests")
@login_required
@role_required("Chief", "Manager", "Receptionist")
def guests():

    cursor.execute("""
        SELECT *
        FROM Guests
        ORDER BY guest_id DESC
    """)

    guests = cursor.fetchall()

    return render_template(
        "guests.html",
        guests=guests,
        role=session.get("role")
    )


# ======================================
# ADD GUEST
# ======================================

@app.route("/add_guest", methods=["POST"])
@login_required
@role_required("Chief", "Manager", "Receptionist")
def add_guest():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    id_proof = request.form.get("id_proof")

    if not all([name, email, phone, address, id_proof]):
        flash("Please fill all fields.")
        return redirect(url_for("guests"))

    cursor.execute("""
        INSERT INTO Guests
        (
            name,
            email,
            phone,
            address,
            id_proof
        )
        VALUES
        (%s,%s,%s,%s,%s)
    """,
    (
        name,
        email,
        phone,
        address,
        id_proof
    ))

    conn.commit()

    flash("Guest Added Successfully")

    return redirect(url_for("guests"))


# ======================================
# EDIT GUEST
# ======================================

@app.route("/edit_guest/<int:guest_id>", methods=["POST"])
@login_required
@role_required("Chief", "Manager", "Receptionist")
def edit_guest(guest_id):

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    id_proof = request.form.get("id_proof")

    cursor.execute("""
        UPDATE Guests
        SET
            name=%s,
            email=%s,
            phone=%s,
            address=%s,
            id_proof=%s
        WHERE guest_id=%s
    """,
    (
        name,
        email,
        phone,
        address,
        id_proof,
        guest_id
    ))

    conn.commit()

    flash("Guest Updated Successfully")

    return redirect(url_for("guests"))


# ======================================
# DELETE GUEST
# ======================================

@app.route("/delete_guest/<int:guest_id>")
@login_required
@role_required("Chief", "Manager")
def delete_guest(guest_id):

    cursor.execute(
        "DELETE FROM Guests WHERE guest_id=%s",
        (guest_id,)
    )

    conn.commit()

    flash("Guest Deleted Successfully")

    return redirect(url_for("guests"))


# ======================================
# SEARCH GUEST
# ======================================

@app.route("/search_guest")
@login_required
@role_required("Chief", "Manager", "Receptionist")
def search_guest():

    keyword = request.args.get("keyword", "").strip()

    cursor.execute("""
        SELECT *
        FROM Guests
        WHERE
            name LIKE %s
            OR phone LIKE %s
            OR email LIKE %s
            OR address LIKE %s
        ORDER BY guest_id DESC
    """,
    (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    guests = cursor.fetchall()

    return render_template(
        "guests.html",
        guests=guests,
        role=session.get("role")
    )
# ======================================
# ROOMS MODULE
# ======================================

@app.route("/rooms")
@login_required
@role_required("Chief", "Manager", "Receptionist", "Housekeeping")
def rooms():

    cursor.execute("""
        SELECT *
        FROM Rooms
        ORDER BY room_id
    """)

    rooms = cursor.fetchall()

    return render_template(
        "rooms.html",
        rooms=rooms,
        role=session.get("role")
    )


# ======================================
# ADD ROOM
# ======================================

@app.route("/add_room", methods=["POST"])
@login_required
@role_required("Chief", "Manager")
def add_room():

    room_id = request.form.get("room_id")
    room_type = request.form.get("room_type")
    price = request.form.get("price")
    status = request.form.get("status")

    if not all([room_id, room_type, price, status]):
        flash("Please fill all fields.")
        return redirect(url_for("rooms"))

    cursor.execute(
        "SELECT room_id FROM Rooms WHERE room_id=%s",
        (room_id,)
    )

    if cursor.fetchone():
        flash("Room ID already exists.")
        return redirect(url_for("rooms"))

    cursor.execute("""
        INSERT INTO Rooms
        (
            room_id,
            room_type,
            price,
            status
        )
        VALUES
        (%s,%s,%s,%s)
    """,
    (
        room_id,
        room_type,
        price,
        status
    ))

    conn.commit()

    flash("Room Added Successfully")

    return redirect(url_for("rooms"))


# ======================================
# EDIT ROOM
# ======================================

@app.route("/edit_room/<int:room_id>", methods=["POST"])
@login_required
@role_required("Chief", "Manager")
def edit_room(room_id):

    room_type = request.form.get("room_type")
    price = request.form.get("price")
    status = request.form.get("status")

    cursor.execute("""
        UPDATE Rooms
        SET
            room_type=%s,
            price=%s,
            status=%s
        WHERE room_id=%s
    """,
    (
        room_type,
        price,
        status,
        room_id
    ))

    conn.commit()

    flash("Room Updated Successfully")

    return redirect(url_for("rooms"))


# ======================================
# DELETE ROOM
# ======================================

@app.route("/delete_room/<int:room_id>")
@login_required
@role_required("Chief")
def delete_room(room_id):

    cursor.execute(
        "DELETE FROM Rooms WHERE room_id=%s",
        (room_id,)
    )

    conn.commit()

    flash("Room Deleted Successfully")

    return redirect(url_for("rooms"))


# ======================================
# SEARCH ROOM
# ======================================

@app.route("/search_room")
@login_required
@role_required("Chief", "Manager", "Receptionist", "Housekeeping")
def search_room():

    keyword = request.args.get("keyword", "").strip()

    cursor.execute("""
        SELECT *
        FROM Rooms
        WHERE
            room_type LIKE %s
            OR status LIKE %s
            OR CAST(room_id AS CHAR) LIKE %s
        ORDER BY room_id
    """,
    (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    rooms = cursor.fetchall()

    return render_template(
        "rooms.html",
        rooms=rooms,
        role=session.get("role")
    )
# ======================================
# BOOKINGS MODULE
# ======================================

@app.route("/bookings")
@login_required
@role_required("Chief", "Manager", "Receptionist")
def bookings():

    cursor.execute("""
        SELECT
            b.booking_id,
            g.guest_id,
            g.name,
            r.room_id,
            r.room_type,
            b.check_in,
            b.check_out,
            b.booking_status
        FROM Bookings b
        JOIN Guests g
            ON b.guest_id = g.guest_id
        JOIN Rooms r
            ON b.room_id = r.room_id
        ORDER BY b.booking_id DESC
    """)

    bookings = cursor.fetchall()

    cursor.execute("""
        SELECT guest_id, name
        FROM Guests
        ORDER BY name
    """)
    guests = cursor.fetchall()

    cursor.execute("""
        SELECT room_id, room_type
        FROM Rooms
        WHERE status='Available'
        ORDER BY room_id
    """)
    rooms = cursor.fetchall()

    return render_template(
        "bookings.html",
        bookings=bookings,
        guests=guests,
        rooms=rooms,
        role=session.get("role")
    )


# ======================================
# ADD BOOKING
# ======================================

@app.route("/add_booking", methods=["POST"])
@login_required
@role_required("Chief", "Manager", "Receptionist")
def add_booking():

    guest_id = request.form.get("guest_id")
    room_id = request.form.get("room_id")
    check_in = request.form.get("check_in")
    check_out = request.form.get("check_out")

    if not all([guest_id, room_id, check_in, check_out]):
        flash("Please fill all fields.")
        return redirect(url_for("bookings"))

    if check_in > check_out:
        flash("Check-out date must be after check-in date.")
        return redirect(url_for("bookings"))

    cursor.execute(
        "SELECT * FROM Rooms WHERE room_id=%s",
        (room_id,)
    )

    room = cursor.fetchone()

    if not room:
        flash("Room not found.")
        return redirect(url_for("bookings"))

    if room["status"] != "Available":
        flash("Selected room is already booked.")
        return redirect(url_for("bookings"))

    cursor.execute("""
        INSERT INTO Bookings
        (
            guest_id,
            room_id,
            check_in,
            check_out,
            booking_status
        )
        VALUES
        (%s,%s,%s,%s,'Booked')
    """,
    (
        guest_id,
        room_id,
        check_in,
        check_out
    ))

    cursor.execute("""
        UPDATE Rooms
        SET status='Booked'
        WHERE room_id=%s
    """,
    (room_id,))

    conn.commit()

    flash("Booking Added Successfully")

    return redirect(url_for("bookings"))


# ======================================
# EDIT BOOKING
# ======================================

@app.route("/edit_booking/<int:booking_id>", methods=["POST"])
@login_required
@role_required("Chief", "Manager", "Receptionist")
def edit_booking(booking_id):

    check_in = request.form.get("check_in")
    check_out = request.form.get("check_out")
    booking_status = request.form.get("booking_status")

    if not all([check_in, check_out, booking_status]):
        flash("Please fill all fields.")
        return redirect(url_for("bookings"))

    if check_in > check_out:
        flash("Invalid booking dates.")
        return redirect(url_for("bookings"))

    cursor.execute("""
        UPDATE Bookings
        SET
            check_in=%s,
            check_out=%s,
            booking_status=%s
        WHERE booking_id=%s
    """,
    (
        check_in,
        check_out,
        booking_status,
        booking_id
    ))

    conn.commit()

    flash("Booking Updated Successfully")

    return redirect(url_for("bookings"))
# ======================================
# CANCEL BOOKING
# ======================================

@app.route("/cancel_booking/<int:booking_id>")
@login_required
@role_required("Chief", "Manager")
def cancel_booking(booking_id):

    cursor.execute("""
        SELECT room_id
        FROM Bookings
        WHERE booking_id=%s
    """, (booking_id,))

    booking = cursor.fetchone()

    if not booking:
        flash("Booking not found.")
        return redirect(url_for("bookings"))

    cursor.execute("""
        UPDATE Bookings
        SET booking_status='Cancelled'
        WHERE booking_id=%s
    """, (booking_id,))

    cursor.execute("""
        UPDATE Rooms
        SET status='Available'
        WHERE room_id=%s
    """, (booking["room_id"],))

    conn.commit()

    flash("Booking Cancelled Successfully")

    return redirect(url_for("bookings"))


# ======================================
# DELETE BOOKING
# ======================================

@app.route("/delete_booking/<int:booking_id>")
@login_required
@role_required("Chief")
def delete_booking(booking_id):

    cursor.execute("""
        SELECT room_id
        FROM Bookings
        WHERE booking_id=%s
    """, (booking_id,))

    booking = cursor.fetchone()

    if not booking:
        flash("Booking not found.")
        return redirect(url_for("bookings"))

    cursor.execute("""
        UPDATE Rooms
        SET status='Available'
        WHERE room_id=%s
    """, (booking["room_id"],))

    cursor.execute("""
        DELETE FROM Bookings
        WHERE booking_id=%s
    """, (booking_id,))

    conn.commit()

    flash("Booking Deleted Successfully")

    return redirect(url_for("bookings"))


# ======================================
# SEARCH BOOKINGS
# ======================================

@app.route("/search_booking")
@login_required
@role_required("Chief", "Manager", "Receptionist")
def search_booking():

    keyword = request.args.get("keyword", "").strip()

    cursor.execute("""
        SELECT
            b.booking_id,
            g.guest_id,
            g.name,
            r.room_id,
            r.room_type,
            b.check_in,
            b.check_out,
            b.booking_status
        FROM Bookings b
        JOIN Guests g
            ON b.guest_id = g.guest_id
        JOIN Rooms r
            ON b.room_id = r.room_id
        WHERE
            g.name LIKE %s
            OR CAST(r.room_id AS CHAR) LIKE %s
            OR r.room_type LIKE %s
            OR b.booking_status LIKE %s
        ORDER BY b.booking_id DESC
    """,
    (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    bookings = cursor.fetchall()

    cursor.execute("""
        SELECT guest_id, name
        FROM Guests
        ORDER BY name
    """)
    guests = cursor.fetchall()

    cursor.execute("""
        SELECT room_id, room_type
        FROM Rooms
        WHERE status='Available'
        ORDER BY room_id
    """)
    rooms = cursor.fetchall()

    return render_template(
        "bookings.html",
        bookings=bookings,
        guests=guests,
        rooms=rooms,
        role=session.get("role")
    )
# ======================================
# PAYMENTS MODULE
# ======================================

@app.route("/payments")
@login_required
@role_required("Chief", "Accountant")
def payments():

    cursor.execute("""
        SELECT
            p.payment_id,
            p.booking_id,
            g.name,
            p.amount,
            p.payment_date,
            p.method,
            p.payment_status
        FROM Payments p
        JOIN Bookings b
            ON p.booking_id = b.booking_id
        JOIN Guests g
            ON b.guest_id = g.guest_id
        ORDER BY p.payment_id DESC
    """)

    payments = cursor.fetchall()

    cursor.execute("""
        SELECT booking_id
        FROM Bookings
        WHERE booking_status='Booked'
        ORDER BY booking_id DESC
    """)

    bookings = cursor.fetchall()

    return render_template(
        "payments.html",
        payments=payments,
        bookings=bookings,
        role=session.get("role")
    )


# ======================================
# ADD PAYMENT
# ======================================

@app.route("/add_payment", methods=["POST"])
@login_required
@role_required("Chief", "Accountant")
def add_payment():

    booking_id = request.form.get("booking_id")
    amount = request.form.get("amount")
    payment_date = request.form.get("payment_date")
    method = request.form.get("method")

    if not all([booking_id, amount, payment_date, method]):
        flash("Please fill all fields.")
        return redirect(url_for("payments"))

    cursor.execute(
        "SELECT payment_id FROM Payments WHERE booking_id=%s",
        (booking_id,)
    )

    if cursor.fetchone():
        flash("Payment already exists for this booking.")
        return redirect(url_for("payments"))

    cursor.execute("""
        INSERT INTO Payments
        (
            booking_id,
            amount,
            payment_date,
            method,
            payment_status
        )
        VALUES
        (%s,%s,%s,%s,'Paid')
    """,
    (
        booking_id,
        amount,
        payment_date,
        method
    ))

    conn.commit()

    flash("Payment Added Successfully")

    return redirect(url_for("payments"))


# ======================================
# EDIT PAYMENT
# ======================================

@app.route("/edit_payment/<int:payment_id>", methods=["POST"])
@login_required
@role_required("Chief", "Accountant")
def edit_payment(payment_id):

    amount = request.form.get("amount")
    payment_date = request.form.get("payment_date")
    method = request.form.get("method")
    payment_status = request.form.get("payment_status")

    cursor.execute("""
        UPDATE Payments
        SET
            amount=%s,
            payment_date=%s,
            method=%s,
            payment_status=%s
        WHERE payment_id=%s
    """,
    (
        amount,
        payment_date,
        method,
        payment_status,
        payment_id
    ))

    conn.commit()

    flash("Payment Updated Successfully")

    return redirect(url_for("payments"))


# ======================================
# DELETE PAYMENT
# ======================================

@app.route("/delete_payment/<int:payment_id>")
@login_required
@role_required("Chief")
def delete_payment(payment_id):

    cursor.execute(
        "DELETE FROM Payments WHERE payment_id=%s",
        (payment_id,)
    )

    conn.commit()

    flash("Payment Deleted Successfully")

    return redirect(url_for("payments"))


# ======================================
# SEARCH PAYMENT
# ======================================

@app.route("/search_payment")
@login_required
@role_required("Chief", "Accountant")
def search_payment():

    keyword = request.args.get("keyword", "").strip()

    cursor.execute("""
        SELECT
            p.payment_id,
            p.booking_id,
            g.name,
            p.amount,
            p.payment_date,
            p.method,
            p.payment_status
        FROM Payments p
        JOIN Bookings b
            ON p.booking_id=b.booking_id
        JOIN Guests g
            ON b.guest_id=g.guest_id
        WHERE
            g.name LIKE %s
            OR p.method LIKE %s
            OR p.payment_status LIKE %s
            OR CAST(p.payment_id AS CHAR) LIKE %s
        ORDER BY p.payment_id DESC
    """,
    (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    payments = cursor.fetchall()

    cursor.execute("""
        SELECT booking_id
        FROM Bookings
        WHERE booking_status='Booked'
        ORDER BY booking_id DESC
    """)

    bookings = cursor.fetchall()

    return render_template(
        "payments.html",
        payments=payments,
        bookings=bookings,
        role=session.get("role")
    )
# ======================================
# REPORTS MODULE
#=======================================
@app.route("/reports")
@login_required
@role_required("Chief", "Manager", "Accountant")
def reports():

    # ---------------- SUMMARY CARDS ----------------

    cursor.execute("SELECT COALESCE(SUM(amount),0) AS revenue FROM Payments")
    revenue = cursor.fetchone()["revenue"]

    cursor.execute("SELECT COUNT(*) AS guests FROM Guests")
    guests = cursor.fetchone()["guests"]

    cursor.execute("SELECT COUNT(*) AS rooms FROM Rooms")
    rooms = cursor.fetchone()["rooms"]

    cursor.execute("SELECT COUNT(*) AS bookings FROM Bookings")
    bookings = cursor.fetchone()["bookings"]

    cursor.execute("SELECT COUNT(*) AS payments FROM Payments")
    payments = cursor.fetchone()["payments"]

    # ---------------- ROOM STATUS ----------------

    cursor.execute("""
        SELECT status, COUNT(*) AS total
        FROM Rooms
        GROUP BY status
        ORDER BY status
    """)
    room_status = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM Rooms WHERE status='Available'")
    available_rooms = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM Rooms WHERE status='Occupied'")
    occupied_rooms = cursor.fetchone()["total"]

    if rooms > 0:
        occupancy_rate = round((occupied_rooms / rooms) * 100, 2)
    else:
        occupancy_rate = 0

    # ---------------- PAYMENT METHODS ----------------

    cursor.execute("""
        SELECT method, COUNT(*) AS total
        FROM Payments
        GROUP BY method
        ORDER BY total DESC
    """)
    payment_methods = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Payments
        WHERE payment_status='Pending'
    """)
    pending_payments = cursor.fetchone()["total"]

    # ---------------- MONTHLY REVENUE ----------------

    cursor.execute("""
        SELECT
            MONTH(payment_date) AS month_no,
            MONTHNAME(payment_date) AS month,
            COALESCE(SUM(amount),0) AS total
        FROM Payments
        GROUP BY MONTH(payment_date), MONTHNAME(payment_date)
        ORDER BY MONTH(payment_date)
    """)

    db_data = cursor.fetchall()

    months = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    revenue_dict = {month: 0 for month in months}

    for row in db_data:
        revenue_dict[row["month"]] = float(row["total"] or 0)

    chart_labels = list(revenue_dict.keys())
    revenue_chart = list(revenue_dict.values())

    monthly_revenue = [
        {
            "month": month,
            "total": revenue_dict[month]
        }
        for month in months
    ]

    # ---------------- RENDER TEMPLATE ----------------

    return render_template(
        "reports.html",
        revenue=revenue,
        guests=guests,
        rooms=rooms,
        bookings=bookings,
        payments=payments,
        room_status=room_status,
        payment_methods=payment_methods,
        monthly_revenue=monthly_revenue,
        chart_labels=chart_labels,
        revenue_chart=revenue_chart,
        available_rooms=available_rooms,
        occupied_rooms=occupied_rooms,
        occupancy_rate=occupancy_rate,
        pending_payments=pending_payments,
        role=session.get("role"),
        username=session.get("name")
    )
# ======================================
# PROFILE
# ======================================

@app.route("/profile")
@login_required
def profile():

    cursor.execute("""
        SELECT
            user_id,
            full_name,
            username,
            email,
            phone,
            role,
            status,
            created_at
        FROM Users
        WHERE user_id=%s
    """, (session["user_id"],))

    user = cursor.fetchone()

    return render_template(
        "profile.html",
        user=user,
        role=session.get("role"),
        username=session.get("name")
    )


# ======================================
# CHANGE PASSWORD
# ======================================

@app.route("/change_password", methods=["POST"])
@login_required
def change_password():

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not old_password or not new_password or not confirm_password:

        flash("Please fill all password fields.")

        return redirect(url_for("profile"))

    if new_password != confirm_password:

        flash("New Password and Confirm Password do not match.")

        return redirect(url_for("profile"))

    cursor.execute("""
        SELECT password
        FROM Users
        WHERE user_id=%s
    """, (session["user_id"],))

    user = cursor.fetchone()

    if not user:

        flash("User not found.")

        return redirect(url_for("logout"))

    valid = False

    try:
        valid = check_password_hash(user["password"], old_password)
    except:
        pass

    if not valid:
        valid = (user["password"] == old_password)

    if not valid:

        flash("Old Password is incorrect.")

        return redirect(url_for("profile"))

    hashed_password = generate_password_hash(new_password)

    cursor.execute("""
        UPDATE Users
        SET password=%s
        WHERE user_id=%s
    """,
    (
        hashed_password,
        session["user_id"]
    ))

    conn.commit()

    flash("Password Changed Successfully")

    return redirect(url_for("profile"))


# ======================================
# ACCESS DENIED
# ======================================

@app.route("/access_denied")
def access_denied():

    return render_template("access_denied.html")


# ======================================
# ERROR HANDLER 404
# ======================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# ======================================
# ERROR HANDLER 500
# ======================================

@app.errorhandler(500)
def internal_server_error(error):

    conn.rollback()

    return render_template("500.html"), 500


# ======================================
# CONTEXT PROCESSOR
# ======================================

@app.context_processor
def inject_user():

    return dict(

        current_user=session.get("name"),

        current_role=session.get("role")

    )


# ======================================
# BEFORE REQUEST
# ======================================

@app.before_request
def keep_session():

    session.permanent = True


# ======================================
# RUN APPLICATION
# ======================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )