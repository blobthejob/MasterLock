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


# #encryption

import base64


CIPHER_PREFIX = "NX1:"

CIPHER_KEY_1 = 0x5B
CIPHER_KEY_2 = 0xA7


def rotate_left(value, amount):
    amount %= 8

    if amount == 0:
        return value

    return (
        (value << amount)
        | (value >> (8 - amount))
    ) & 0xFF


def rotate_right(value, amount):
    amount %= 8

    if amount == 0:
        return value

    return (
        (value >> amount)
        | (value << (8 - amount))
    ) & 0xFF


def encrypt_text(text):

    data = text.encode("utf-8")

    encrypted = []
    previous = 0

    for position, byte in enumerate(data):

        # Stage 1
        value = (
            byte
            + CIPHER_KEY_1
            + (17 * position)
        ) & 0xFF

        # Stage 2
        value ^= (
            CIPHER_KEY_2
            + (31 * position)
        ) & 0xFF

        # Stage 3
        value = rotate_left(
            value,
            3 + (position % 5)
        )

        # Stage 4
        multiplier = 5 + (2 * (position % 5))

        value = (
            (value * multiplier)
            + (19 * position)
            + 23
        ) & 0xFF

        # Stage 5
        value = (
            value + previous
        ) & 0xFF

        # Stage 6
        previous = value
        encrypted.append(value)

    encoded = base64.urlsafe_b64encode(
        bytes(encrypted)
    ).decode("ascii").rstrip("=")

    return CIPHER_PREFIX + encoded


def decrypt_text(text):

    if not text.startswith(CIPHER_PREFIX):
        return None

    encoded = text[len(CIPHER_PREFIX):]

    padding = "=" * (
        (4 - len(encoded) % 4) % 4
    )

    try:
        raw = base64.urlsafe_b64decode(
            encoded + padding
        )
    except Exception:
        return None

    encrypted = list(raw)

    # Undo Stage 5
    values = []
    previous = 0

    for value in encrypted:

        original_value = (
            value - previous
        ) & 0xFF

        values.append(original_value)
        previous = value

    decrypted = []

    for position, value in enumerate(values):

        # Undo Stage 4
        multiplier = 5 + (2 * (position % 5))

        inverse = pow(
            multiplier,
            -1,
            256
        )

        value = (
            (
                value
                - (19 * position)
                - 23
            ) * inverse
        ) & 0xFF

        # Undo Stage 3
        value = rotate_right(
            value,
            3 + (position % 5)
        )
        # Undo Stage 2
        value ^= (
            CIPHER_KEY_2
            + (31 * position)
        ) & 0xFF
        # Undo Stage 1
        value = (
            value
            - CIPHER_KEY_1
            - (17 * position)
        ) & 0xFF
        decrypted.append(value)
    try:
        return bytes(decrypted).decode("utf-8")
    except UnicodeDecodeError:
        return None


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

        elif "operation shi" in code:
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
                # #encryption commands

        elif code.startswith("encrypt "):

            text = original[8:]

            return jsonify({
                "type": "result",
                "text": encrypt_text(text)
            })


        elif code.startswith("decrypt "):

            text = original[8:]

            decrypted = decrypt_text(text)

            if decrypted is None:
                return jsonify({
                    "type": "result",
                    "text": "Invalid encryption code."
                })

            return jsonify({
                "type": "result",
                "text": decrypted
            })


        elif code.startswith("cipher "):

            text = original[7:]

            if text.startswith(CIPHER_PREFIX):

                decrypted = decrypt_text(text)

                if decrypted is None:
                    return jsonify({
                        "type": "result",
                        "text": "Invalid encryption code."
                    })

                return jsonify({
                    "type": "result",
                    "text": decrypted
                })

            return jsonify({
                "type": "result",
                "text": encrypt_text(text)
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
