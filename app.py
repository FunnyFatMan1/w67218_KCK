from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
from riot_api import get_puuid, get_match_ids, get_match_data, analyze_matches

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")
REGION_ROUTING = "europe"
REGION_PLATFORM = "eun1"  # domyślnie EUNE

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        tagline = request.form.get("tagline")

        if not nickname or not tagline:
            return redirect(url_for("error"))

        puuid = get_puuid(nickname, tagline, API_KEY)
        if not puuid:
            return redirect(url_for("error"))

        try:
            match_ids = get_match_ids(puuid, 20, REGION_ROUTING, API_KEY)
            matches = [get_match_data(mid, REGION_ROUTING, API_KEY) for mid in match_ids]
            analysis = analyze_matches(matches, puuid)

            return render_template("result.html", nickname=nickname, tagline=tagline, analysis=analysis)

        except Exception as e:
            print(f"Błąd: {e}")
            return redirect(url_for("error"))

    return render_template("index.html")


@app.route("/error")
def error():
    return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True)
