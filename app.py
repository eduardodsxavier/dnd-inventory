from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functions import login_required


# configure the Flask server
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# open the database as db
db = SQL("sqlite:///inventory.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# homepage
@app.route("/")
@login_required
def index():
    # pick every character of that user
    session["characters"] = db.execute("SELECT * FROM characters WHERE user_id = ?", session["user_id"])
    return render_template("index.html")

# login the user
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # pick the user inputs
        username = request.form.get("username")
        password = request.form.get("password")

        # verify if they are validy inputs
        if not username:
            return render_template("login.html", alert="must provide a username")
        elif not password:
            return render_template("login.html", alert="must provide a password")

        # pick the in the database the row with the give username
        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # verify if username and password given by the user are valids
        if len(user) != 1 or not check_password_hash(
            user[0]["hash"], password
        ):
            return render_template("login.html", alert="invalid username or password")

        # set session id to the id of given account
        session["user_id"] = user[0]["id"]

        return redirect("/")

    return render_template("login.html")


# register users
@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # pick the inputs given to create a account
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # verify if the user give all necessary inputs
        if not username:
            return render_template("register.html", alert="must provide a username")
        elif not password:
            return render_template("register.html", alert="must provide a password")
        elif not confirmation:
            return render_template("register.html", alert="must provide the password confirmation")
        # verify if password and password confirmation are iquals
        elif password != confirmation:
            return render_template("register.html", alert="invalid password confirmation")

        # verify if that username is already in the data base
        if len(db.execute("SELECT * FROM users WHERE username = ?", username)) != 0:
            return render_template("register.html", alert="must provide a diferent username")

        # if not insert the account informartion in the data base
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, generate_password_hash(password, method='pbkdf2', salt_length=16))

        # save the actual session
        session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]

        return redirect("/")

    return render_template("register.html")


@app.route("/inventory")
@login_required
def inventory():

    # see if the charact id have be given
    if "char_id" in request.args:
        char_id = request.args["char_id"]
    else:
        return redirect("/")

    # open the arrays for the diferents items types
    charWeapons = []
    charArmors = []
    charItems = []

    # create a variable with the id of all the items in the char inventory
    inventory = db.execute("SELECT * FROM inventory WHERE char_id = ?", char_id)

    # pass for every item in char inventory
    for row in inventory:
        # pick the item information
        item = db.execute("SELECT * FROM items WHERE id = ?", row["item_id"])[0]

        item.update({"quantity": row["quantity"]})

        # verify what is the item type and put in the array
        if item["type"] == "weapon":
            charWeapons.append(item)
        elif item["type"] == "armor":
            charArmors.append(item)
        else:
            charItems.append(item)

        allitems = db.execute("SELECT * FROM items;")

        weapons = []
        armors = []
        items = []

        for item in allitems:
            if item["type"] == "weapon":
                weapons.append(item)
            if item["type"] == "armor":
                armors.append(item)
            if item["type"] == "item":
                items.append(item)

    return render_template("inventory.html", charWeapons=charWeapons, charArmors=charArmors, charItems=charItems, weapons=weapons, armors=armors, items=items)


@app.route("/additem")
@login_required
def additem():
    if request.method == "POST":
        if request.form.get("weapon"):
            item = request.form.get("weapon")
        elif request.form.get("armor"):
            item = request.form.get("armor")
        elif request.form.get("item"):
            item = request.form.get("item")
        else:
            return redirect("/")

        char_id = request.args["char_id"]

        itemInInventory = db.execute("SELECT * FROM inventory WHERE char_id = ? AND item_id = ?", char_id, item["id"])

        if len(itemInInventory) != 0:
            db.execute("UPDATE inventory SET quantity = ? WHERE char_id = ? AND item_id = ?",
                       itemInInventory[0]["quantity"] + 1, char_id, item["id"])
        else:
            db.execute("INSERT INTO inventory(char_id, item_id) VALUES(?, ?)", char_id, item_id)

        return redirect("/inventory")

@app.route("/logout")
@login_required
def logout():

    # Forget any user_id
    session.clear()

    return redirect("/login")
