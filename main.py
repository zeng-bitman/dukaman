from flask import Flask, render_template, request, redirect, flash, session, url_for
from database import conn, cur
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Secret key for session management

# 🔹 Custom login_required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):    
        if 'logged_in' not in session:  # Check if user is logged in
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contactus")
def contact():
    return render_template("contactus.html")

@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "GET":
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        return render_template("products.html", products=products)
    else:
        name = request.form["name"]
        buying_price = float(request.form["bp"])
        selling_price = float(request.form["sp"])
        stock_quantity = int(request.form["sq"])

        query = """
        INSERT INTO products (name, buying_price, selling_price, stock_quantity) 
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (name, buying_price, selling_price, stock_quantity))
        conn.commit()
        return redirect("/products")

@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    if request.method == "GET":
        cur.execute("SELECT id, pid, quantity, TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at FROM sales")
        sales = cur.fetchall()

        cur.execute("SELECT * FROM products")
        products = cur.fetchall()

        return render_template("sales.html", sales=sales, products=products)
    else:
        pid = request.form["pid"]
        quantity = request.form["quant"]

        query = "INSERT INTO sales (pid, quantity, created_at) VALUES (%s, %s, NOW())"
        cur.execute(query, (pid, quantity))
        conn.commit()
        return redirect("/sales")

@app.route("/dashboard")
@login_required
def dashboard():
    cur.execute("""
        SELECT products.name AS product_name, 
               SUM(sales.quantity * (products.selling_price - products.buying_price)) AS total_profit 
        FROM sales 
        JOIN products ON products.id = sales.pid 
        GROUP BY products.name
    """)
    sales_result = cur.fetchall()

    x = [i[0] for i in sales_result]
    y = [float(i[1]) for i in sales_result]

    cur.execute("""
        SELECT products.name AS product_name, 
               SUM(sales.quantity * (products.selling_price - products.buying_price)) AS total_profit 
        FROM sales 
        JOIN products ON products.id = sales.pid 
        GROUP BY products.name;
    """)
    profit_results = cur.fetchall()

    return render_template("dashboard.html", x=x, y=y, profit_results=profit_results)

# 🔹 Registration with password hashing
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["name"]
        email_address = request.form["Email"]
        password = request.form["Pass"]

        hashed_password = generate_password_hash(password)  # 🔹 Hash the password

        cur.execute("INSERT INTO users (full_name, email_address, password) VALUES (%s, %s, %s)", 
                    (full_name, email_address, hashed_password))  # Store hashed password
        conn.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect("/login")
    
    return render_template("register.html")

# 🔹 Secure login with hashed password check
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_address = request.form["emailaddress"]
        password = request.form["password"]

        cur.execute("SELECT id, password FROM users WHERE email_address = %s", (email_address,))
        user = cur.fetchone()

        if user and check_password_hash(user[1], password):  # Verify hashed password
            session["logged_in"] = True
            session["user_id"] = user[0]
            flash("Login successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
    
    return render_template("login.html")

# 🔹 Logout route
@app.route("/logout")
@login_required
def logout():
    session.clear()  # Clears all session data
    flash("You have been logged out.", "info")
    return redirect("/login")

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "GET":
        cur.execute("SELECT * FROM expenses")
        expenses = cur.fetchall()
        return render_template("expenses.html", expenses=expenses)
    else:
        expense_category = request.form["expense_category"]
        description = request.form["description"]
        amount = float(request.form["amount"])

        query_create_expense = """
            INSERT INTO expenses (expense_category, description, amount, purchase_date) 
            VALUES (%s, %s, %s, NOW())
        """
        cur.execute(query_create_expense, (expense_category, description, amount))
        conn.commit()

        return redirect("/expenses")
    

@app.route("/stock", methods=["GET", "POST"])
def stock():
    if request.method == "GET":
        cur.execute("SELECT * FROM stock")
        stock = cur.fetchall()

        # return render_template("stock.html", stock=stock)
        
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()

        return render_template("stock.html", stock=stock, products=products)
    
    else:
        pid = request.form["pid"]
        stock_quantity = int(request.form["sq"])

        cur.execute("SELECT id FROM stock WHERE pid = %s", (pid,))
        existing_stock = cur.fetchone()

        if existing_stock:
            query_update_stock = "UPDATE stock SET stock_quantity = %s WHERE pid = %s" 
            cur.execute(query_update_stock, (stock_quantity, pid))
            conn.commit()
        else:
            query_create_stock = "INSERT INTO stock (pid, stock_quantity) VALUES (%s, %s)"
            cur.execute(query_create_stock, (pid, stock_quantity))
            conn.commit()

        return redirect("/stock")
if __name__ == "__main__":
    app.run(debug=True)
