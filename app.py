from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory
)

import sqlite3
import os
from pathlib import Path
from datetime import datetime, date
from werkzeug.utils import secure_filename


# -------------------------------------------------
# APP CONFIGURATION
# -------------------------------------------------

app = Flask(__name__)

app.secret_key = "transport-management-system-v4-4"

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "database.db"

UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


ALLOWED_EXTENSIONS = {
    "pdf",
    "jpg",
    "jpeg",
    "png"
}


# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# -------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------

def init_database():

    connection = get_db()

    # Vehicles
    connection.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vehicle_no TEXT NOT NULL,

            model TEXT,

            vehicle_type TEXT,

            owner TEXT,

            mobile TEXT

        )
    """)

    # Vehicle Documents
    connection.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_documents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vehicle_id INTEGER NOT NULL,

            document_name TEXT,

            file_name TEXT,

            valid_until TEXT,

            FOREIGN KEY(vehicle_id)
            REFERENCES vehicles(id)

        )
    """)

    # Drivers
    connection.execute("""
        CREATE TABLE IF NOT EXISTS drivers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            mobile TEXT,

            license_no TEXT,

            address TEXT,

            license_file TEXT,

            photo_file TEXT

        )
    """)

    # Driver Documents
    connection.execute("""
        CREATE TABLE IF NOT EXISTS driver_documents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            driver_id INTEGER NOT NULL,

            document_name TEXT,

            file_name TEXT,

            valid_until TEXT,

            FOREIGN KEY(driver_id)
            REFERENCES drivers(id)

        )
    """)

    # Routes
    connection.execute("""
        CREATE TABLE IF NOT EXISTS routes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            trip_date TEXT NOT NULL,

            vehicle_no TEXT NOT NULL,

            driver_name TEXT,

            route_from TEXT NOT NULL,

            route_to TEXT NOT NULL,

            fare REAL DEFAULT 0,

            notes TEXT

        )
    """)

    # Expenses
    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            route_id INTEGER,

            expense_date TEXT NOT NULL,

            expense_type TEXT,

            amount REAL DEFAULT 0,

            description TEXT,

            FOREIGN KEY(route_id)
            REFERENCES routes(id)

        )
    """)

    # Attendance
    connection.execute("""
        CREATE TABLE IF NOT EXISTS attendance (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            attendance_date TEXT NOT NULL,

            driver_name TEXT NOT NULL,

            status TEXT NOT NULL

        )
    """)

    connection.commit()

    connection.close()


# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------

def allowed_file(filename):

    if not filename:
        return False

    extension = filename.rsplit(".", 1)[-1].lower()

    return extension in ALLOWED_EXTENSIONS


def save_file(file):

    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)

    unique_name = (
        datetime.now().strftime("%Y%m%d%H%M%S%f")
        + "_"
        + filename
    )

    file.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_name
        )
    )

    return unique_name


# -------------------------------------------------
# UPLOADED FILE
# -------------------------------------------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# =================================================
# DASHBOARD
# =================================================

@app.route("/")
def dashboard():

    connection = get_db()

    vehicle_count = connection.execute(
        "SELECT COUNT(*) FROM vehicles"
    ).fetchone()[0]

    driver_count = connection.execute(
        "SELECT COUNT(*) FROM drivers"
    ).fetchone()[0]

    route_count = connection.execute(
        "SELECT COUNT(*) FROM routes"
    ).fetchone()[0]

    current_month = date.today().strftime("%Y-%m")

    # -------------------------------------------------
    # MONTHLY FARE
    # -------------------------------------------------

    monthly_fare = connection.execute("""
        SELECT COALESCE(SUM(fare), 0)

        FROM routes

        WHERE substr(trip_date, 1, 7) = ?
    """, (current_month,)).fetchone()[0]


    # -------------------------------------------------
    # MONTHLY EXPENSE
    # -------------------------------------------------

    monthly_expense = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)

        FROM expenses

        WHERE substr(expense_date, 1, 7) = ?
    """, (current_month,)).fetchone()[0]


    # -------------------------------------------------
    # MONTHLY PROFIT
    # -------------------------------------------------

    monthly_profit = (
        monthly_fare -
        monthly_expense
    )


    # -------------------------------------------------
    # MONTHLY DATA
    # -------------------------------------------------

    monthly_data = connection.execute("""
        SELECT

            substr(r.trip_date, 1, 7) AS month,

            COALESCE(SUM(r.fare), 0) AS fare,

            COALESCE(
                (
                    SELECT SUM(e.amount)

                    FROM expenses e

                    WHERE e.route_id IN (

                        SELECT r2.id

                        FROM routes r2

                        WHERE substr(
                            r2.trip_date,
                            1,
                            7
                        ) = substr(
                            r.trip_date,
                            1,
                            7
                        )
                    )

                ),
                0
            ) AS expense

        FROM routes r

        GROUP BY substr(
            r.trip_date,
            1,
            7
        )

        ORDER BY month DESC

    """).fetchall()


    # -------------------------------------------------
    # DOCUMENT NOTIFICATIONS
    # -------------------------------------------------

    today = date.today()

    document_notifications = []

    documents = connection.execute("""
        SELECT

            vd.id,

            vd.document_name,

            vd.valid_until,

            v.vehicle_no

        FROM vehicle_documents vd

        JOIN vehicles v

        ON vd.vehicle_id = v.id

        WHERE vd.valid_until IS NOT NULL

        AND vd.valid_until != ''

        ORDER BY vd.valid_until

    """).fetchall()


    for document in documents:

        try:

            expiry_date = datetime.strptime(
                document["valid_until"],
                "%Y-%m-%d"
            ).date()

            days_left = (
                expiry_date - today
            ).days

            if days_left < 0:

                status = "expired"

            elif days_left <= 30:

                status = "warning"

            else:

                continue

            document_notifications.append({

                "vehicle_no":
                    document["vehicle_no"],

                "document_name":
                    document["document_name"],

                "valid_until":
                    document["valid_until"],

                "days_left":
                    days_left,

                "status":
                    status

            })

        except ValueError:

            pass


    # -------------------------------------------------
    # RECENT ROUTES
    # -------------------------------------------------

    recent_routes = connection.execute("""
        SELECT

            r.*,

            COALESCE(
                (
                    SELECT SUM(e.amount)

                    FROM expenses e

                    WHERE e.route_id = r.id
                ),
                0
            ) AS expense

        FROM routes r

        ORDER BY r.trip_date DESC, r.id DESC

        LIMIT 10

    """).fetchall()


    connection.close()


    # Add profit in Python
    route_list = []

    for route in recent_routes:

        route_list.append({

            "id": route["id"],

            "trip_date": route["trip_date"],

            "vehicle_no": route["vehicle_no"],

            "driver_name": route["driver_name"],

            "route":
                route["route_from"]
                + " → "
                + route["route_to"],

            "fare": route["fare"],

            "expense": route["expense"],

            "profit":
                route["fare"] -
                route["expense"]

        })


    return render_template(

        "dashboard.html",

        vehicle_count=vehicle_count,

        driver_count=driver_count,

        route_count=route_count,

        monthly_fare=monthly_fare,

        monthly_expense=monthly_expense,

        monthly_profit=monthly_profit,

        current_month=current_month,

        monthly_data=monthly_data,

        document_notifications=document_notifications,

        recent_routes=route_list

    )


# =================================================
# VEHICLES
# =================================================

@app.route("/vehicles")
def vehicles():

    connection = get_db()

    vehicles = connection.execute("""
        SELECT *

        FROM vehicles

        ORDER BY id DESC

    """).fetchall()

    connection.close()

    return render_template(
        "vehicles.html",
        vehicles=vehicles
    )


# -------------------------------------------------
# ADD VEHICLE
# -------------------------------------------------

@app.route("/vehicles/add", methods=["GET", "POST"])
def add_vehicle():

    if request.method == "POST":

        vehicle_no = request.form["vehicle_no"]

        model = request.form["model"]

        vehicle_type = request.form["vehicle_type"]

        owner = request.form["owner"]

        mobile = request.form["mobile"]


        connection = get_db()

        cursor = connection.execute("""
            INSERT INTO vehicles
            (
                vehicle_no,
                model,
                vehicle_type,
                owner,
                mobile
            )

            VALUES (?, ?, ?, ?, ?)

        """, (
            vehicle_no,
            model,
            vehicle_type,
            owner,
            mobile
        ))

        vehicle_id = cursor.lastrowid

        connection.commit()

        connection.close()


        # Multiple documents
        document_names = request.form.getlist(
            "document_name"
        )

        valid_dates = request.form.getlist(
            "valid_until"
        )

        files = request.files.getlist(
            "documents"
        )


        connection = get_db()


        for index, file in enumerate(files):

            filename = save_file(file)

            if filename:

                document_name = (

                    document_names[index]

                    if index < len(document_names)

                    else "Vehicle Document"

                )

                valid_until = (

                    valid_dates[index]

                    if index < len(valid_dates)

                    else ""

                )


                connection.execute("""
                    INSERT INTO vehicle_documents
                    (
                        vehicle_id,
                        document_name,
                        file_name,
                        valid_until
                    )

                    VALUES (?, ?, ?, ?)

                """, (
                    vehicle_id,
                    document_name,
                    filename,
                    valid_until
                ))


        connection.commit()

        connection.close()

        flash(
            "Vehicle added successfully!"
        )

        return redirect(
            url_for("vehicles")
        )


    return render_template(
        "vehicle_form.html"
    )


# -------------------------------------------------
# EDIT VEHICLE
# -------------------------------------------------

@app.route(
    "/vehicles/edit/<int:vehicle_id>",
    methods=["GET", "POST"]
)
def edit_vehicle(vehicle_id):

    connection = get_db()

    vehicle = connection.execute("""
        SELECT *

        FROM vehicles

        WHERE id = ?

    """, (vehicle_id,)).fetchone()


    if not vehicle:

        connection.close()

        flash("Vehicle not found!")

        return redirect(
            url_for("vehicles")
        )


    if request.method == "POST":

        connection.execute("""
            UPDATE vehicles

            SET

                vehicle_no = ?,

                model = ?,

                vehicle_type = ?,

                owner = ?,

                mobile = ?

            WHERE id = ?

        """, (

            request.form["vehicle_no"],

            request.form["model"],

            request.form["vehicle_type"],

            request.form["owner"],

            request.form["mobile"],

            vehicle_id

        ))


        connection.commit()

        connection.close()

        flash(
            "Vehicle updated successfully!"
        )

        return redirect(
            url_for("vehicles")
        )


    documents = connection.execute("""
        SELECT *

        FROM vehicle_documents

        WHERE vehicle_id = ?

        ORDER BY id DESC

    """, (vehicle_id,)).fetchall()


    connection.close()


    return render_template(

        "vehicle_form.html",

        vehicle=vehicle,

        documents=documents,

        edit=True

    )


# -------------------------------------------------
# ADD MORE VEHICLE DOCUMENTS
# -------------------------------------------------

@app.route(
    "/vehicles/<int:vehicle_id>/documents",
    methods=["POST"]
)
def add_vehicle_documents(vehicle_id):

    document_names = request.form.getlist(
        "document_name"
    )

    valid_dates = request.form.getlist(
        "valid_until"
    )

    files = request.files.getlist(
        "documents"
    )


    connection = get_db()


    for index, file in enumerate(files):

        filename = save_file(file)

        if filename:

            document_name = (

                document_names[index]

                if index < len(document_names)

                else "Vehicle Document"

            )

            valid_until = (

                valid_dates[index]

                if index < len(valid_dates)

                else ""

            )


            connection.execute("""
                INSERT INTO vehicle_documents
                (
                    vehicle_id,
                    document_name,
                    file_name,
                    valid_until
                )

                VALUES (?, ?, ?, ?)

            """, (

                vehicle_id,

                document_name,

                filename,

                valid_until

            ))


    connection.commit()

    connection.close()

    flash(
        "Vehicle documents uploaded!"
    )

    return redirect(
        url_for(
            "edit_vehicle",
            vehicle_id=vehicle_id
        )
    )


# -------------------------------------------------
# DELETE VEHICLE
# -------------------------------------------------

@app.route(
    "/vehicles/delete/<int:vehicle_id>"
)
def delete_vehicle(vehicle_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM vehicle_documents

        WHERE vehicle_id = ?

    """, (vehicle_id,))


    connection.execute("""
        DELETE FROM vehicles

        WHERE id = ?

    """, (vehicle_id,))


    connection.commit()

    connection.close()

    flash(
        "Vehicle deleted!"
    )

    return redirect(
        url_for("vehicles")
    )


# =================================================
# DRIVERS
# =================================================

@app.route("/drivers")
def drivers():

    connection = get_db()

    drivers = connection.execute("""
        SELECT *

        FROM drivers

        ORDER BY id DESC

    """).fetchall()

    connection.close()

    return render_template(
        "drivers.html",
        drivers=drivers
    )


# -------------------------------------------------
# ADD DRIVER
# -------------------------------------------------

@app.route(
    "/drivers/add",
    methods=["GET", "POST"]
)
def add_driver():

    if request.method == "POST":

        license_file = save_file(
            request.files.get("license_file")
        )

        photo_file = save_file(
            request.files.get("photo_file")
        )


        connection = get_db()

        connection.execute("""
            INSERT INTO drivers
            (
                name,
                mobile,
                license_no,
                address,
                license_file,
                photo_file
            )

            VALUES (?, ?, ?, ?, ?, ?)

        """, (

            request.form["name"],

            request.form["mobile"],

            request.form["license_no"],

            request.form["address"],

            license_file,

            photo_file

        ))


        connection.commit()

        connection.close()

        flash(
            "Driver added successfully!"
        )

        return redirect(
            url_for("drivers")
        )


    return render_template(
        "driver_form.html"
    )


# -------------------------------------------------
# EDIT DRIVER
# -------------------------------------------------

@app.route(
    "/drivers/edit/<int:driver_id>",
    methods=["GET", "POST"]
)
def edit_driver(driver_id):

    connection = get_db()

    driver = connection.execute("""
        SELECT *

        FROM drivers

        WHERE id = ?

    """, (driver_id,)).fetchone()


    if request.method == "POST":

        connection.execute("""
            UPDATE drivers

            SET

                name = ?,

                mobile = ?,

                license_no = ?,

                address = ?

            WHERE id = ?

        """, (

            request.form["name"],

            request.form["mobile"],

            request.form["license_no"],

            request.form["address"],

            driver_id

        ))


        connection.commit()

        connection.close()

        flash(
            "Driver updated successfully!"
        )

        return redirect(
            url_for("drivers")
        )


    connection.close()

    return render_template(

        "driver_form.html",

        driver=driver,

        edit=True

    )


# -------------------------------------------------
# DELETE DRIVER
# -------------------------------------------------

@app.route(
    "/drivers/delete/<int:driver_id>"
)
def delete_driver(driver_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM driver_documents

        WHERE driver_id = ?

    """, (driver_id,))


    connection.execute("""
        DELETE FROM drivers

        WHERE id = ?

    """, (driver_id,))


    connection.commit()

    connection.close()

    flash(
        "Driver deleted!"
    )

    return redirect(
        url_for("drivers")
    )


# =================================================
# ROUTES
# =================================================

@app.route("/routes")
def routes():

    connection = get_db()

    routes = connection.execute("""
        SELECT *

        FROM routes

        ORDER BY trip_date DESC, id DESC

    """).fetchall()

    connection.close()

    return render_template(
        "routes.html",
        routes=routes
    )


# -------------------------------------------------
# ADD ROUTE
# -------------------------------------------------

@app.route(
    "/routes/add",
    methods=["GET", "POST"]
)
def add_route():

    connection = get_db()

    vehicles = connection.execute(
        "SELECT * FROM vehicles"
    ).fetchall()

    drivers = connection.execute(
        "SELECT * FROM drivers"
    ).fetchall()


    if request.method == "POST":

        connection.execute("""
            INSERT INTO routes
            (
                trip_date,
                vehicle_no,
                driver_name,
                route_from,
                route_to,
                fare,
                notes
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """, (

            request.form["trip_date"],

            request.form["vehicle_no"],

            request.form["driver_name"],

            request.form["route_from"],

            request.form["route_to"],

            float(
                request.form.get(
                    "fare",
                    0
                ) or 0
            ),

            request.form["notes"]

        ))


        connection.commit()

        connection.close()

        flash(
            "Route added successfully!"
        )

        return redirect(
            url_for("routes")
        )


    connection.close()


    return render_template(

        "route_form.html",

        vehicles=vehicles,

        drivers=drivers

    )


# -------------------------------------------------
# DELETE ROUTE
# -------------------------------------------------

@app.route(
    "/routes/delete/<int:route_id>"
)
def delete_route(route_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM expenses

        WHERE route_id = ?

    """, (route_id,))


    connection.execute("""
        DELETE FROM routes

        WHERE id = ?

    """, (route_id,))


    connection.commit()

    connection.close()

    flash(
        "Route deleted!"
    )

    return redirect(
        url_for("routes")
    )


# =================================================
# EXPENSES
# =================================================

@app.route("/expenses")
def expenses():

    connection = get_db()

    expenses = connection.execute("""
        SELECT

            e.*,

            r.route_from,

            r.route_to

        FROM expenses e

        LEFT JOIN routes r

        ON e.route_id = r.id

        ORDER BY e.expense_date DESC

    """).fetchall()


    connection.close()


    return render_template(

        "expenses.html",

        expenses=expenses

    )


# -------------------------------------------------
# ADD EXPENSE
# -------------------------------------------------

@app.route(
    "/expenses/add",
    methods=["GET", "POST"]
)
def add_expense():

    connection = get_db()

    routes = connection.execute("""
        SELECT *

        FROM routes

        ORDER BY trip_date DESC

    """).fetchall()


    if request.method == "POST":

        connection.execute("""
            INSERT INTO expenses
            (
                route_id,
                expense_date,
                expense_type,
                amount,
                description
            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            request.form["route_id"],

            request.form["expense_date"],

            request.form["expense_type"],

            float(
                request.form.get(
                    "amount",
                    0
                ) or 0
            ),

            request.form["description"]

        ))


        connection.commit()

        connection.close()

        flash(
            "Expense added successfully!"
        )

        return redirect(
            url_for("expenses")
        )


    connection.close()


    return render_template(

        "expense_form.html",

        routes=routes

    )


# -------------------------------------------------
# DELETE EXPENSE
# -------------------------------------------------

@app.route(
    "/expenses/delete/<int:expense_id>"
)
def delete_expense(expense_id):

    connection = get_db()

    connection.execute("""
        DELETE FROM expenses

        WHERE id = ?

    """, (expense_id,))


    connection.commit()

    connection.close()

    flash(
        "Expense deleted!"
    )

    return redirect(
        url_for("expenses")
    )


# =================================================
# ATTENDANCE
# =================================================

@app.route("/attendance")
def attendance():

    connection = get_db()

    attendance_data = connection.execute("""
        SELECT *

        FROM attendance

        ORDER BY attendance_date DESC

    """).fetchall()


    summary = connection.execute("""
        SELECT

            driver_name,

            SUM(
                CASE
                    WHEN status = 'Full Day'
                    THEN 1
                    ELSE 0
                END
            ) AS full_days,

            SUM(
                CASE
                    WHEN status = 'Half Day'
                    THEN 1
                    ELSE 0
                END
            ) AS half_days

        FROM attendance

        GROUP BY driver_name

    """).fetchall()


    connection.close()


    return render_template(

        "attendance.html",

        attendance_data=attendance_data,

        summary=summary

    )


# -------------------------------------------------
# ADD ATTENDANCE
# -------------------------------------------------

@app.route(
    "/attendance/add",
    methods=["GET", "POST"]
)
def add_attendance():

    connection = get_db()

    drivers = connection.execute("""
        SELECT *

        FROM drivers

        ORDER BY name

    """).fetchall()


    if request.method == "POST":

        connection.execute("""
            INSERT INTO attendance
            (
                attendance_date,
                driver_name,
                status
            )

            VALUES (?, ?, ?)

        """, (

            request.form["attendance_date"],

            request.form["driver_name"],

            request.form["status"]

        ))


        connection.commit()

        connection.close()

        flash(
            "Attendance saved!"
        )

        return redirect(
            url_for("attendance")
        )


    connection.close()


    return render_template(

        "attendance_form.html",

        drivers=drivers

    )


# =================================================
# ROUTE SUMMARY
# =================================================

@app.route("/route-summary")
def route_summary():

    connection = get_db()

    rows = connection.execute("""
        SELECT

            r.id,

            r.trip_date,

            r.vehicle_no,

            r.driver_name,

            r.route_from,

            r.route_to,

            r.fare,

            COALESCE(
                SUM(e.amount),
                0
            ) AS expense

        FROM routes r

        LEFT JOIN expenses e

        ON r.id = e.route_id

        GROUP BY r.id

        ORDER BY r.trip_date DESC

    """).fetchall()


    connection.close()


    data = []


    for row in rows:

        data.append({

            "id": row["id"],

            "date": row["trip_date"],

            "vehicle":
                row["vehicle_no"],

            "driver":
                row["driver_name"],

            "route":
                row["route_from"]
                + " → "
                + row["route_to"],

            "fare":
                row["fare"],

            "expense":
                row["expense"],

            "profit":
                row["fare"]
                -
                row["expense"]

        })


    return render_template(

        "route_summary.html",

        rows=data

    )


# =================================================
# START APP
# =================================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True
    )