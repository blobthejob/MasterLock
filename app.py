from flask import Flask, render_template, request, jsonify
from urllib.parse import quote
import re
import json
COLOURS = {
    "black": "black",
    "white": "white",
    "red": "red",
    "green": "green",
    "blue": "blue",
    "yellow": "yellow",
    "purple": "purple",
    "pink": "pink",
    "orange": "orange",
    "gray": "gray",
    "grey": "gray"
}

def get_colour(value):
    value = value.strip().lower()
    if value in COLOURS:
        return COLOURS[value]
    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value
    return None

app = Flask(__name__)

UNLOCK_CODE = "everybody wants to rule the world"
RESET_CODE = "reset puzzle"
CODES = {

    "nos ossos que aqui estamos pelos vossos esperamos": {
        "text": "You've found the first clue:\n\nWhere you now stand, seek words of Latin stone\nUpon this place, a secret waits alone\nLook up and find the message carved in bone\nAnd speak its meaning once the words are known",
        "unlocks": ["melior est dies mortis die nativitatis"]
    },

    "melior est dies mortis die nativitatis":{
        "text":"Sub palmā viridis fōns dēserta per arva clāret,\nFrīgida vallis habet dulcem relevāta ardōrem;\nMurmure dulcī aqua per saxa serēna sonāret,\nHīc viātor bibit et relinquit errorem.",
        "unlocks": []
    }
}
START_UNLOCKED = ["nos ossos que aqui estamos pelos vossos esperamos"]

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        original = request.form["code"].strip()
        code = original.lower().replace(",", "").replace(".", "").replace("'","")

        locked = request.form.get("locked") == "true"

        if locked and code == RESET_CODE.lower():
            return jsonify({
                "type": "reset"
            })

        elif locked and code == UNLOCK_CODE.lower():
            return jsonify({
                "type": "unlock"
            })

        elif code == "operation shitstorm":
            return jsonify({
                "type": "lock"
            })

        elif code == "hello":
            return jsonify({
                "type": "result",
                "text": "Hello!"
            })
        
        elif code == "no one in the world ever gets what they want and that is beautiful":
            return jsonify({
                "type": "decrypt",
                "text": "everybody dies frustrated and sad\nbut that is beautiful"
            })

        elif "867" in code and "5309" in code:
            return jsonify({
                "type": "result",
                "text": "Jenny, Jenny, here's my number:\n+447935307551\nNow I just need to make you mine..."
            })
        
        elif code in CODES:
            unlocked = request.form.get("unlocked", "[]")
            unlocked = json.loads(unlocked)

            if code not in unlocked:
                search = original
                return jsonify({
                    "type": "url",
                    "url": "https://www.google.com/search?q=" + quote(search)
                })

            return jsonify({
                "type": "code",
                "text": CODES[code]["text"],
                "unlocks": CODES[code]["unlocks"]
            })

        elif code.startswith("yt "):
            search = original[3:]

            return jsonify({
                "type": "url",
                "url": "https://www.youtube.com/results?search_query=" + quote(search)
            })

        elif code.startswith("youtube "):
            search = original[8:]

            return jsonify({
                "type": "url",
                "url": "https://www.youtube.com/results?search_query=" + quote(search)
            })

        elif code.startswith("wiki "):
            search = original[5:]

            return jsonify({
                "type": "url",
                "url": "https://en.wikipedia.org/wiki/Special:Search?search=" + quote(search)
            })

        elif code.startswith("g "):
            search = original[2:]
            return jsonify({
                "type": "url",
                "url": "https://www.google.com/search?q=" + quote(search)
            })
        elif code.startswith("bg "):
            colour = get_colour(original[3:])
            if colour:
                return jsonify({
                    "type": "css",
                    "target": "bg",
                    "value": colour
                })
            return jsonify({
                "type": "result",
                "text": "Invalid background colour."
            })


        elif code.startswith("text "):
            colour = get_colour(original[5:])
            if colour:
                return jsonify({
                    "type": "css",
                    "target": "text",
                    "value": colour
                })
            return jsonify({
                "type": "result",
                "text": "Invalid text colour."
            })
        
        elif code.startswith("btn "):
            colour = get_colour(original[4:])
            if colour:
                return jsonify({
                    "type": "css",
                    "target": "btn",
                    "value": colour
                })

            return jsonify({
                "type": "result",
                "text": "Invalid button colour."
            })


        elif code.startswith("input "):
            colour = get_colour(original[6:])
            if colour:
                return jsonify({
                    "type": "css",
                    "target": "input",
                    "value": colour
                })

            return jsonify({
                "type": "result",
                "text": "Invalid input colour."
            })

        else:
            return jsonify({
                "type": "url",
                "url": "https://www.google.com/search?q=" + quote(original)
            })

    return render_template("index.html")


if __name__ == "__main__":
    app.run()
