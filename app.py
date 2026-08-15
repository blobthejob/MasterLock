from flask import Flask, render_template, request, jsonify
from urllib.parse import quote

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        original = request.form["code"].strip()
        code = original.lower()

        if code == "hello":
            return jsonify({
                "type": "result",
                "text": "Hello!"
            })

        elif code == "ursjgduffsjhpjprywbxmho1573711627384937261738jdhx":
            return jsonify({
                "type": "result",
                "text": "CLUE 2: You have unlocked the next clue!"
            })

        elif code.startswith("yt "):
            search = original[3:]
            url = "https://www.youtube.com/results?search_query=" + quote(search)

            return jsonify({
                "type": "url",
                "url": url
            })

        elif code.startswith("youtube "):
            search = original[8:]
            url = "https://www.youtube.com/results?search_query=" + quote(search)

            return jsonify({
                "type": "url",
                "url": url
            })

        elif code.startswith("wiki "):
            search = original[5:]
            url = "https://en.wikipedia.org/wiki/Special:Search?search=" + quote(search)

            return jsonify({
                "type": "url",
                "url": url
            })

        elif code.startswith("g "):
            search = original[2:]
            url = "https://www.google.com/search?q=" + quote(search)

            return jsonify({
                "type": "url",
                "url": url
            })

        else:
            url = "https://www.google.com/search?q=" + quote(original)

            return jsonify({
                "type": "url",
                "url": url
            })

    return render_template("index.html")


if __name__ == "__main__":
    app.run()
