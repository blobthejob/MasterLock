from flask import Flask, render_template, request, jsonify
from urllib.parse import quote

app = Flask(__name__)

UNLOCK_CODE = "everybody wants to rule the world"

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        original = request.form["code"].strip()
        code = original.lower()

        if code == "operation shitstorm":
            return jsonify({
                "type": "lock"
            })
        
        elif code == UNLOCK_CODE.lower():
            return jsonify({
                "type": "unlock"
            })

        elif code == "hello":
            return jsonify({
                "type": "result",
                "text": "Hello!"
            })


        elif code == "no one in the world ever gets what they want and that is beautiful":
            return jsonify({
                "type": "result",
                "text": "CODE ACCEPTED"
            })

        elif "867" in code and "5309" in code:
            return jsonify({
                "type": "result",
                "text": "CODE ACCEPTED"
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

        else:
            return jsonify({
                "type": "url",
                "url": "https://www.google.com/search?q=" + quote(original)
            })

    return render_template("index.html")


if __name__ == "__main__":
    app.run()
