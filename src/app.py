import json
from collections import OrderedDict

import requests
from flask import Flask, render_template, request, redirect

NTFY_CHANNEL = "bf2-dropping-2024"

teams = ["Mario", "Waluigi", "Joshi", "Daisy"]

stages = OrderedDict(
    {  # Template, password, Name for notification
        "start": ("start.html", "password", "Start"),
        "1-1": ("1-1.html", "Take road A", "Mariokart"),
        "tournament": ("tournament.html", "Only9th", "Tournament"),
        "1-4": ("smallproblems.html", "WhiteRabbit", "Small Puzzles"),
        "braille": ("braille.html", "Down At E", "Braille"),
        "whoswho": ("Photos.html", "Votos", "Pictures"),
        "final": ("Final.html", "You won", "Final markings"),
        "done": ("Done.html", "", "Done"),
    }
)

app = Flask(__name__)


@app.get("/<stage>")
def stage(stage):
    if stage in stages.keys():
        return render_template(stages[stage][0], fail=False, stage=stage, teams=teams)
    else:
        return render_template("404.html")


@app.post("/<stage>")
def stage_post(stage):
    if request.form["password"].lower() == stages[stage][1].lower():

        r = requests.post(
            "https://ntfy.sh/",
            data=json.dumps(
                {
                    "topic": NTFY_CHANNEL,
                    "message": f"Team {request.form['team']} has solved stage {stages[stage][2]} at location {request.form['location']}",
                    "title": "Stage solved",
                    "priority": 4,
                    "tags": ["white_check_mark"],
                    "Actions": [
                        {
                            "action": "view",
                            "label": "Open in map",
                            "url": f"geo:{request.form['location']}",
                        }
                    ],
                }
            ),
        )
        print(r.status_code, r.text, request.form["location"])

        next_stage = list(stages.keys())[list(stages.keys()).index(stage) + 1]
        return redirect(f"/{next_stage}")
    else:
        r = requests.post(
            "https://ntfy.sh/",
            data=json.dumps(
                {
                    "topic": NTFY_CHANNEL,
                    "message": f"""Team {request.form['team']} has failed stage {stages[stage][2]} 
                                   They filled in {request.form['password']}
                                   But it should have been {stages[stage][1]}""",
                    "title": "Stage failed",
                    "priority": 4,
                    "tags": ["x"],
                    "Actions": [
                        {
                            "action": "view",
                            "label": "Open in map",
                            "url": f"geo:{request.form['location']}",
                        }
                    ],
                },
            ),
        )

        print(r.status_code, r.text, request.form["location"])

        return render_template(stages[stage][0], fail=True, stage=stage, teams=teams)
