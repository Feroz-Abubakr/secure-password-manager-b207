from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "change-this-secret-key-later"


@app.route("/")
def home():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)