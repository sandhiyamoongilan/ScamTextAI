from flask import Flask, render_template, redirect, session, request, url_for
from authlib.integrations.flask_client import OAuth
import pickle

app = Flask(__name__, template_folder="templates")
app.secret_key = "super_secret_key"

# ---------------- GOOGLE OAUTH CONFIG ----------------
app.config['GOOGLE_CLIENT_ID'] = "YOUR_GOOGLE_CLIENT_ID"
app.config['GOOGLE_CLIENT_SECRET'] = "YOUR_GOOGLE_CLIENT_SECRET"

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ---------------- LOGIN PAGES ----------------
@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/login_google")
def login_google():
    return google.authorize_redirect(url_for("auth_google", _external=True))

@app.route("/auth_google")
def auth_google():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session["user"] = user_info.get("name")
    session["email"] = user_info.get("email")
    session["picture"] = url_for('static', filename='images/dhiya.png')
    session["history"] = []
    return redirect("/")

@app.route("/login_manual", methods=["POST"])
def login_manual():
    email = request.form.get("email")
    password = request.form.get("password")
    session["user"] = email.split("@")[0]
    session["email"] = email
    session["picture"] = url_for('static', filename='images/dhiya.png')
    session["history"] = []
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login_page")

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login_page")
    return render_template(
        "home.html",
        user=session.get("user"),
        email=session.get("email"),
        picture=session.get("picture")
    )

# ---------------- CHECK PAGE ----------------
@app.route("/check")
def check():
    if "user" not in session:
        return redirect("/login_page")
    return render_template(
        "check.html",
        user=session.get("user"),
        email=session.get("email"),
        picture=session.get("picture"),
        history=session.get("history", []),
        prediction_text=session.get("last_result"),
        last_message=session.get("last_message")
    )

# ---------------- PREDICT ----------------
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/login_page")

    message = request.form["message"]
    data = vectorizer.transform([message])
    prediction = model.predict(data)
    result = "🚨 Scam Message" if prediction[0] == 1 else "✅ Safe Message"

    session["last_result"] = result
    session["last_message"] = message

    history = session.get("history", [])
    history.insert(0, {"message": message, "result": result})
    session["history"] = history[:10]  # last 10 messages

    return redirect("/check")

if __name__ == "__main__":
    app.run(debug=True)