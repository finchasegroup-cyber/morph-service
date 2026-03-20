import os
from flask import Flask, request, jsonify
import pymorphy3
from cachetools import TTLCache

app = Flask(__name__)
morph = pymorphy3.MorphAnalyzer()

cache = TTLCache(maxsize=10000, ttl=43200)

CUSTOM_DICT = {
    "генеральный директор": "генерального директора",
    "действующий на основании устава": "действующего на основании устава",
    "индивидуальный предприниматель": "индивидуального предпринимателя",
    "представитель по доверенности": "представителя по доверенности"
}

def decline_word(word):
    p = morph.parse(word)[0]
    inf = p.inflect({'gent'})
    return inf.word if inf else word

def decline_fio(text):
    parts = text.split()
    if len(parts) == 3:
        try:
            s = decline_word(parts[0])
            n = decline_word(parts[1])
            p = decline_word(parts[2])
            return f"{s} {n} {p}"
        except:
            pass
    return None

def decline_phrase(text):
    text_l = text.lower().strip()

    if text_l in CUSTOM_DICT:
        return CUSTOM_DICT[text_l]

    fio = decline_fio(text)
    if fio:
        return fio

    words = text.split()
    result = [decline_word(w) for w in words]
    return " ".join(result)

@app.route("/decline", methods=["POST"])
def decline():
    data = request.json
    if not data:
        return jsonify({"error": "no json"}), 400

    if "texts" in data:
        results = []
        for text in data["texts"]:
            if text in cache:
                results.append(cache[text])
            else:
                declined = decline_phrase(text)
                cache[text] = declined
                results.append(declined)
        return jsonify({"results": results})

    text = data.get("text")
    if not text:
        return jsonify({"error": "no text"}), 400

    if text in cache:
        return jsonify({"result": cache[text]})

    declined = decline_phrase(text)
    cache[text] = declined
    return jsonify({"result": declined})

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
