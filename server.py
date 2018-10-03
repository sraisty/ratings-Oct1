"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    if session.get('user_id'):
        # user is logged in already, so show the homepage 
        return render_template("homepage.html")

    # user needs to log  in first before seeing the homepage
    return redirect('/login')

@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:myuser_id>')
def get_user_info(myuser_id):
    """ Display the user info (age, zip) and the list of 
    all the movie titles and scores that this user rated
    """
    user = User.query.filter(User.user_id == myuser_id).first()
    rating_a = db.session.query(Movie.title, Rating.score)
    rating_b = rating_a.filter(Rating.user_id == myuser_id)
    ratings = rating_b.join(Rating).all()
    
    return render_template("user_detail.html", user=user, ratings=ratings)

@app.route('/register', methods=["GET"])
def display_register_form():
    """ Displays the user registration form """
    return render_template("registration_form.html")


@app.route("/register", methods=['POST'])
def get_register_info():
    # email and password are coming back from form
    # and then we need to insert them into the Users database
    email = request.form.get("email")
    password = request.form.get("password")
    
    # first see if the user already exists.  
    if User.query.filter(User.email==email).first():
        flash("the email already exists. Please enter another one")
        return redirect("/register")
   
    # if the user doesn't already exist in the database, add the user
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash(f"User Added: {email}, {password}")
    return redirect ('/')

@app.route("/login")
def display_login_form():
    return render_template('login.html')

@app.route("/do-login")
def login_user():
    """ Get user's email and password, make sure that password matches database """
    email = request.args.get("email")
    password = request.args.get("password")

    user = User.query.filter(User.email==email).first()
    if user is None:
        flash("Login failed: invalid user. Please register.")
        return redirect('/register')

    if user.password==password:
        # Login succeeded
        session['user_id'] = user.user_id
        flash("Login succeeded")
        return redirect('/')

    # login didn't succeed because of either bad email or bad password
    flash("Bad password. Please try again.")
    return redirect('/login')

@app.route("/logout")
def logout_user():
    session.pop('user_id', None)
    flash("You logged out. Bye!")
    return redirect("/login")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
