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
import random


# #cipher variants

CIPHER_VARIANTS = {

    "iubdsvi:": {
        "key1": 0x5B,
        "key2": 0xA7,
        "rotate": 3,
        "multiplier": 5,
        "position_key": 17,
        "xor_position": 31,
        "add_position": 19,
        "add_constant": 23
    },

    "nxvkrta:": {
        "key1": 0x91,
        "key2": 0x3D,
        "rotate": 5,
        "multiplier": 7,
        "position_key": 23, 
        "xor_position": 47,
        "add_position": 11,
        "add_constant": 41
    },

    "qzlmepo:": {
        "key1": 0x2F,
        "key2": 0xC1,
        "rotate": 2,
        "multiplier": 9,
        "position_key": 13,
        "xor_position": 37,
        "add_position": 29,
        "add_constant": 67
    },

    "rjvhtkc:": {
        "key1": 0xD4,
        "key2": 0x68,
        "rotate": 7,
        "multiplier": 11,
        "position_key": 31,
        "xor_position": 19,
        "add_position": 43,
        "add_constant": 17
    },

    "wpxfona:": {
        "key1": 0x46,
        "key2": 0xB9,
        "rotate": 4,
        "multiplier": 13,
        "position_key": 29,
        "xor_position": 53,
        "add_position": 7,
        "add_constant": 89
    },

    "bqydrmu:": {
        "key1": 0xE3,
        "key2": 0x27,
        "rotate": 6,
        "multiplier": 15,
        "position_key": 41,
        "xor_position": 23,
        "add_position": 31,
        "add_constant": 53
    },

    "kcgzvei:": {
        "key1": 0x74,
        "key2": 0xDA,
        "rotate": 1,
        "multiplier": 17,
        "position_key": 37,
        "xor_position": 61,
        "add_position": 17,
        "add_constant": 71
    },

    "tmsxjup:": {
        "key1": 0xBC,
        "key2": 0x52,
        "rotate": 3,
        "multiplier": 19,
        "position_key": 47,
        "xor_position": 29,
        "add_position": 53,
        "add_constant": 37
    },

    "fhrqkdl:": {
        "key1": 0x18,
        "key2": 0xF3,
        "rotate": 5,
        "multiplier": 21,
        "position_key": 19,
        "xor_position": 43,
        "add_position": 61,
        "add_constant": 97
    },

    "zavnbic:": {
        "key1": 0xC7,
        "key2": 0x84,
        "rotate": 7,
        "multiplier": 23,
        "position_key": 53,
        "xor_position": 67,
        "add_position": 37,
        "add_constant": 79
    }

}


# #rotate left

def rotate_left(value, amount):

    amount %= 8

    if amount == 0:
        return value

    return (
        (value << amount) |
        (value >> (8 - amount))
    ) & 0xFF


# #rotate right

def rotate_right(value, amount):

    amount %= 8

    if amount == 0:
        return value

    return (
        (value >> amount) |
        (value << (8 - amount))
    ) & 0xFF


# #encrypt

def encrypt_text(text):

    prefix = random.choice(
        list(CIPHER_VARIANTS.keys())
    )

    variant = CIPHER_VARIANTS[prefix]

    data = text.encode("utf-8")

    encrypted = []

    previous = 0

    for position, byte in enumerate(data):

        # stage 1

        value = (
            byte +
            variant["key1"] +
            (
                variant["position_key"] *
                position
            )
        ) & 0xFF

        # stage 2

        value ^= (
            variant["key2"] +
            (
                variant["xor_position"] *
                position
            )
        ) & 0xFF

        # stage 3

        rotation = (
            variant["rotate"] +
            (position % 5)
        )

        value = rotate_left(
            value,
            rotation
        )

        # stage 4

        multiplier = (
            variant["multiplier"] +
            (2 * (position % 5))
        )

        value = (
            (
                value *
                multiplier
            ) +
            (
                variant["add_position"] *
                position
            ) +
            variant["add_constant"]
        ) & 0xFF

        # stage 5

        value = (
            value +
            previous
        ) & 0xFF

        previous = value

        encrypted.append(value)

    encoded = base64.urlsafe_b64encode(
        bytes(encrypted)
    ).decode("ascii").rstrip("=")

    return prefix + encoded


# #decrypt

def decrypt_text(text):

    prefix = None

    for possible_prefix in CIPHER_VARIANTS:

        if text.startswith(possible_prefix):

            prefix = possible_prefix

            break

    if prefix is None:
        return None

    variant = CIPHER_VARIANTS[prefix]

    encoded = text[len(prefix):]

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

    values = []

    previous = 0

    # #reverse stage 5

    for value in encrypted:

        original_value = (
            value -
            previous
        ) & 0xFF

        values.append(original_value)

        previous = value

    decrypted = []

    for position, value in enumerate(values):

        # reverse stage 4

        multiplier = (
            variant["multiplier"] +
            (2 * (position % 5))
        )

        try:

            inverse = pow(
                multiplier,
                -1,
                256
            )

        except ValueError:

            return None

        value = (
            (
                value -
                (
                    variant["add_position"] *
                    position
                ) -
                variant["add_constant"]
            ) *
            inverse
        ) & 0xFF

        # reverse stage 3

        rotation = (
            variant["rotate"] +
            (position % 5)
        )

        value = rotate_right(
            value,
            rotation
        )

        # reverse stage 2

        value ^= (
            variant["key2"] +
            (
                variant["xor_position"] *
                position
            )
        ) & 0xFF

        # reverse stage 1

        value = (
            value -
            variant["key1"] -
            (
                variant["position_key"] *
                position
            )
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


        # #cipher command

        elif code.startswith("cipher "):

            text = original[7:]

            # If it already has one of the known prefixes,
            # decrypt it.

            if any(
                text.startswith(prefix)
                for prefix in CIPHER_VARIANTS
            ):

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

            # Otherwise encrypt it.

            return jsonify({
                "type": "result",
                "text": encrypt_text(text)
            })
        # #text commands

        elif code.startswith("upper "):

            text = original[6:]

            return jsonify({
                "type": "result",
                "text": text.upper()
            })


        elif code.startswith("lower "):

            text = original[6:]

            return jsonify({
                "type": "result",
                "text": text.lower()
            })


        elif code.startswith("length "):

            text = original[7:]

            return jsonify({
                "type": "result",
                "text": str(len(text))
            })


        elif code.startswith("reverse "):

            text = original[8:]

            return jsonify({
                "type": "result",
                "text": text[::-1]
            })


        elif code.startswith("words "):

            text = original[6:]

            return jsonify({
                "type": "result",
                "text": str(len(text.split()))
            })


        elif code.startswith("chars "):

            text = original[6:]

            return jsonify({
                "type": "result",
                "text": str(len(text))
            })


        elif code.startswith("trim "):

            text = original[5:]

            return jsonify({
                "type": "result",
                "text": text.strip()
            })


        elif code.startswith("title "):

            text = original[6:]

            return jsonify({
                "type": "result",
                "text": text.title()
            })


        elif code.startswith("swap "):

            text = original[5:]

            return jsonify({
                "type": "result",
                "text": text.swapcase()
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
