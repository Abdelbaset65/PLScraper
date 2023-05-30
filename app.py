# Import libraries
from flask import Flask, request, url_for, redirect, render_template
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import DataRequired, Email, EqualTo
import mysql.connector
import os

# Create an instance of Flask and connect to the database
app = Flask(__name__)

# Get MySQL credentials from environment variables
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

# Create MySQL connection
mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)
# This is the main page


@app.route('/')
def home():
    return render_template("home.html")

# Register a user


@app.route("/addUser", methods=["POST", "GET"])
def addUser():
    message = ''
    if (request.method == "POST"):
        email = request.form["userEmail"]
        username = request.form["username"]
        gender = request.form["gander"]
        age = request.form["Age"]
        dob = request.form["DOB"]
        fTeam = request.form["Favorite Team"]
        cur = mydb.cursor()
        try:
            cur.execute("INSERT INTO user VALUES (%s, %s, %s, %s, %s, %s)",
                        (email, username, gender, age, dob, fTeam))
            mydb.commit()
            message = "User Added successfully"
        except Exception as e:
            mydb.rollback()
            message = "Failure to add the student<br>Problem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("addUser.html")

# User login


@app.route('/UserLogin', methods=["POST", "GET"])
def UserLogin():
    if request.method == "POST":
        email = request.form["email"]
        return redirect(url_for('User', email=email))
    else:
        return render_template("UserLogin.html")


# Query and view a given team information
@app.route('/Clubs', methods=['POST', 'GET'])
def Clubs():
    message = ''
    if request.method == "POST":
        clubName = request.form["Club"]
        cur = mydb.cursor()
        try:
            cur.execute("SELECT * FROM club WHERE Name = %s", (clubName))
            resultClub = cur.fetchall()
            if len(resultClub) > 0:
                message = render_template("ClubInfo.html", Club=clubName)
            else:
                message = "No Club Exists with this name."
        except Exception as e:
            mydb.rollback()
            message = "Failure to view the club<br>Problem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("Clubs.html")

# Query and view a given player information (by their first and last name)


@app.route('/Players', methods=['POST', 'GET'])
def Players():
    message = ''
    if request.method == "POST":
        playerName = request.form["Player_Name"]
        cur = mydb.cursor()
        try:
            cur.execute(
                "SELECT * FROM player WHERE Name = %s", (playerName))
            resultPlayer = cur.fetchall()
            if len(resultPlayer) > 0:
                message = render_template("PlayerInfo.html", Player=playerName)
            else:
                message = "No Club Exists with this name."
        except Exception as e:
            mydb.rollback()
            message = "Failure to view the player<br>Problem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("Players.html")


# Add a new user review on a match
@app.route("/Matches/<HTeam>_<ATeam>_<MDate>/Reviews/addReview", methods=["POST","GET"])
def addReview():
    message = ''
    if (request.method == "POST"):
        uEmail = request.form["User Email"]
        mDate = request.form["Match Date"]
        mHTeam = request.form["Match Home Team"]
        mATeam = request.form["Match Away Team"]
        rating = request.form["Rating"]
        review = request.form["Review"]
        cur = mydb.cursor()
        try:
            cur.execute("INSERT INTO `match review` VALUES (%s, %s, %s, %s, %s)",
                        (uEmail, mDate, mHTeam, mATeam, rating, review))
            mydb.commit()
            message = "Review Added successfully"
        except Exception as e:
            mydb.rollback()
            message = "Failure to add the review\nProblem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("addReview.html")

# View all the reviews for a match


@app.route("/Matches/Reviews/<HTeam>_<ATeam>_<MDate>", methods=["POST", "GET"])
def ShowReviews(ATeam, HTeam, MDate):
    message = ''
    cur = mydb.cursor()
    try:
        cur.execute("SELECT `User Email`, Rating, Review FROM `match review` WHERE `Match Home Team` = "
                    "%s AND `Match Away Team` = %s AND `Match Date` = %s", (HTeam, ATeam, MDate))
        reviews = cur.fetchall()
        if len(reviews) > 0:
            message = render_template("DisplayReviews.html", reviews=reviews)
        else:
            message = "<tr>No Review Exists for this match</tr>"
    except Exception as e:
        mydb.rollback()
        message = "Failure to view the reviews<br>Problem Description: " + \
            str(e)
    finally:
        cur.close()
        return message

# Show all the players from a certain nationality and their home teams history


@app.route('/Players/byNationality', methods=["POST", "GET"])
def getPlayerByNationality():
    message = ''
    if request.method == "POST":
        nationality = request.form["Nationality"]
        cur = mydb.cursor()
        try:
            cur.execute(
                "SELECT * from player as P JOIN `previous seasons` as PS ON P.Name = PS.PlayerName WHERE P.Nationality = %s", (nationality))
            resultPlayers = cur.fetchall()
            if len(resultPlayers) > 0:
                message = render_template(
                    "Players.html", Nationality=nationality)
            else:
                message = "No Players exist with this nationality."
        except Exception as e:
            mydb.rollback()
            message = "Failure to view the players by the natonality<br>Problem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("Players.html")

# Show the top 10 teams by matches won, home matches won, yellow cards, fouls, and shots


@app.route('/Clubs/Top10', methods=["POST", "GET"])
def getTop10():
    message = ''
    if request.method == "POST":
        top10 = request.form["Top10"]
        cur = mydb.cursor()
        try:
            cur.execute(
                "SELECT Name FROM club ORDER BY %s DESC LIMIT 10", (top10))
            resultTop10 = cur.fetchall()
            if len(resultTop10) > 0:
                message = render_template("Top10.html", Top10=top10)
            else:
                message = "No Teams exist with this statistic."
        except Exception as e:
            mydb.rollback()
            message = "Failure to view the top 10 teams<br>Problem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("Top10.html")

# Identify the home team for a given stadium name


@app.route('/Clubs/<clubName>', methods=["POST", "GET"])
def getStadiumHomeTeam():
    message = ''
    if request.method == "POST":
        stadiumName = request.form["Stadium"]
        cur = mydb.cursor()
        try:
            cur.execute(
                "SELECT C.Name from club AS C JOIN stadium AS S ON C.`Home Stadium` = S.Name WHERE S.Name = %s", (stadiumName))
            resultClub = cur.fetchall()
            if len(resultClub) > 0:
                message = render_template(
                    "Players.html", Stadium=stadiumName)
            else:
                message = "No Players exist with this position."
        except Exception as e:
            mydb.rollback()
            message = "Failure to view the players by the position<br>Problem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("Players.html")

# Show all the players who played a certain position


@app.route('/Players/byPosition', methods=["POST", "GET"])
def getPlayerByPosition():
    message = ''
    if request.method == "POST":
        pos = request.form["Position"]
        cur = mydb.cursor()
        try:
            cur.execute(
                "SELECT * from player WHERE Position = %s", (pos))
            resultPlayers = cur.fetchall()
            if len(resultPlayers) > 0:
                message = render_template(
                    "Players.html", Position=pos)
            else:
                message = "No Players exist with this position."
        except Exception as e:
            mydb.rollback()
            message = "Failure to view the players by the position<br>Problem Description: " + \
                str(e)
        finally:
            cur.close()
            return message
    else:
        return render_template("Players.html")


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
