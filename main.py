from flask import Flask,render_template,request,redirect,flash
from database import conn,cur
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contactus")
def contact():
    return render_template("contactus.html")

@app.route("/products",methods=["GET","POST"])
def products():
    if request.method == "GET":
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        return render_template("products.html",products=products)
    else:
        name = request.form["name"]
        buying_price = float(request.form["bp"])
        selling_price = float(request.form["sp"])
        stock_quantity = int(request.form["sq"])
        # print(name, buying_price, selling_price, stock_quantity)
        query ="insert into products(name,buying_price,selling_price,stock_quantity)"\
        "values('{}',{},{},{})".format(name,buying_price,selling_price,stock_quantity)
        cur.execute(query)
        conn.commit()
        return redirect("/products")


@app.route("/sales",methods=["GET","POST"])
def sales():
    if request.method == "GET":
        cur.execute("SELECT * FROM sales")
        sales = cur.fetchall()

        cur.execute("SELECT * from products")
        # print(sales)
        products=cur.fetchall()

        return render_template("sales.html",sales=sales, products=products)
        
    else:
        pid =request.form["pid"]
        Quantity=request.form["quant"]
        

        # print(pID, quantity,created_at)

        query ="insert into sales(pid,quantity, created_at)"\
        "values({},{},now())".format(pid, Quantity)
        cur.execute(query)
        conn.commit()
        return redirect("/sales")


@app.route("/dashboard")
def dashboard():
    cur.execute("SELECT products.name AS product_name, SUM(sales.quantity * (products.selling_price - products.buying_price)) AS total_profit FROM sales JOIN products ON products.id = sales.pid GROUP BY products.name")
    sales_result= cur.fetchall()
    x = []
    y = []
    for i in sales_result:
        x.append(i[0])
        y.append(float(i[1]))

    cur.execute("select products.name as product_name, sum(sales.quantity*(products.selling_price - products.buying_price )) as total_profit from sales join products on products.id=sales.pid group by products.name;")
    profit_results= cur.fetchall()

    return render_template("dashboard.html", x=x,y=y, profit_results=profit_results)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # Fetch all users from the database
        cur.execute("SELECT * FROM users")  
        users = cur.fetchall()  

        print("GET request received. Users fetched:", users)  # Debugging output
        return render_template("register.html", users=users)  

    else:
        # Get form data
        full_name = request.form["name"]
        email_address = request.form["Email"]
        password = request.form["Pass"]  # Consider hashing before storing

        # Insert user into database safely
        query = """
    INSERT INTO users (full_name, email_address, password) 
    VALUES (%s, %s, %s) RETURNING id;
    """

        cur.execute(query, (full_name, email_address, password))
        user_id = cur.fetchone()[0]  # Retrieve inserted user ID

        conn.commit()

        print(f"User registered with ID: {user_id}")
        
        # Redirect back to /register after successful registration
        return redirect("/register")

@app.route("/login", methods =["POST", "GET"])
def login():
    if request.method == 'POST':
        email_address = request.form["emailaddress"]
        password = request.form["password"]

        querylogin = "SELECT id from users where email_address = '{}' and password = '{}'".format(email_address, password)
        cur.execute(querylogin)
        row = cur.fetchone()

        if row is None:
            flash("Invalid credentials")
            return render_template("login.html")

        else:
            return redirect("/dashboard")
    else:
        return render_template("login.html")



app.run(debug=True)