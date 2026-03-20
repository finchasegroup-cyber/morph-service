{\rtf1\ansi\ansicpg1251\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from flask import Flask, request, jsonify\
import pymorphy2\
from cachetools import TTLCache\
\
app = Flask(__name__)\
morph = pymorphy2.MorphAnalyzer()\
\
# \uc0\u1050 \u1077 \u1096  \u1085 \u1072  10 000 \u1092 \u1088 \u1072 \u1079  \u1085 \u1072  12 \u1095 \u1072 \u1089 \u1086 \u1074 \
cache = TTLCache(maxsize=10000, ttl=43200)\
\
# \uc0\u1055 \u1086 \u1083 \u1100 \u1079 \u1086 \u1074 \u1072 \u1090 \u1077 \u1083 \u1100 \u1089 \u1082 \u1080 \u1081  \u1089 \u1083 \u1086 \u1074 \u1072 \u1088 \u1100  (\u1084 \u1086 \u1078 \u1085 \u1086  \u1076 \u1086 \u1087 \u1086 \u1083 \u1085 \u1103 \u1090 \u1100 )\
CUSTOM_DICT = \{\
    "\uc0\u1075 \u1077 \u1085 \u1077 \u1088 \u1072 \u1083 \u1100 \u1085 \u1099 \u1081  \u1076 \u1080 \u1088 \u1077 \u1082 \u1090 \u1086 \u1088 ": "\u1075 \u1077 \u1085 \u1077 \u1088 \u1072 \u1083 \u1100 \u1085 \u1086 \u1075 \u1086  \u1076 \u1080 \u1088 \u1077 \u1082 \u1090 \u1086 \u1088 \u1072 ",\
    "\uc0\u1076 \u1077 \u1081 \u1089 \u1090 \u1074 \u1091 \u1102 \u1097 \u1080 \u1081  \u1085 \u1072  \u1086 \u1089 \u1085 \u1086 \u1074 \u1072 \u1085 \u1080 \u1080  \u1091 \u1089 \u1090 \u1072 \u1074 \u1072 ": "\u1076 \u1077 \u1081 \u1089 \u1090 \u1074 \u1091 \u1102 \u1097 \u1077 \u1075 \u1086  \u1085 \u1072  \u1086 \u1089 \u1085 \u1086 \u1074 \u1072 \u1085 \u1080 \u1080  \u1091 \u1089 \u1090 \u1072 \u1074 \u1072 ",\
    "\uc0\u1080 \u1085 \u1076 \u1080 \u1074 \u1080 \u1076 \u1091 \u1072 \u1083 \u1100 \u1085 \u1099 \u1081  \u1087 \u1088 \u1077 \u1076 \u1087 \u1088 \u1080 \u1085 \u1080 \u1084 \u1072 \u1090 \u1077 \u1083 \u1100 ": "\u1080 \u1085 \u1076 \u1080 \u1074 \u1080 \u1076 \u1091 \u1072 \u1083 \u1100 \u1085 \u1086 \u1075 \u1086  \u1087 \u1088 \u1077 \u1076 \u1087 \u1088 \u1080 \u1085 \u1080 \u1084 \u1072 \u1090 \u1077 \u1083 \u1103 ",\
    "\uc0\u1087 \u1088 \u1077 \u1076 \u1089 \u1090 \u1072 \u1074 \u1080 \u1090 \u1077 \u1083 \u1100  \u1087 \u1086  \u1076 \u1086 \u1074 \u1077 \u1088 \u1077 \u1085 \u1085 \u1086 \u1089 \u1090 \u1080 ": "\u1087 \u1088 \u1077 \u1076 \u1089 \u1090 \u1072 \u1074 \u1080 \u1090 \u1077 \u1083 \u1103  \u1087 \u1086  \u1076 \u1086 \u1074 \u1077 \u1088 \u1077 \u1085 \u1085 \u1086 \u1089 \u1090 \u1080 "\
\}\
\
def decline_word(word):\
    p = morph.parse(word)[0]\
    inf = p.inflect(\{'gent'\})\
    return inf.word if inf else word\
\
def decline_fio(text):\
    parts = text.split()\
    if len(parts) == 3:\
        try:\
            s = decline_word(parts[0])\
            n = decline_word(parts[1])\
            p = decline_word(parts[2])\
            return f"\{s\} \{n\} \{p\}"\
        except:\
            pass\
    return None\
\
def decline_phrase(text):\
    text_l = text.lower().strip()\
    \
    # 1. \uc0\u1057 \u1083 \u1086 \u1074 \u1072 \u1088 \u1100 \
    if text_l in CUSTOM_DICT:\
        return CUSTOM_DICT[text_l]\
    \
    # 2. \uc0\u1060 \u1048 \u1054  (\u1090 \u1088 \u1080  \u1089 \u1083 \u1086 \u1074 \u1072 )\
    fio = decline_fio(text)\
    if fio:\
        return fio\
    \
    # 3. \uc0\u1054 \u1073 \u1097 \u1080 \u1081  \u1089 \u1083 \u1091 \u1095 \u1072 \u1081 \
    words = text.split()\
    result = [decline_word(w) for w in words]\
    return " ".join(result)\
\
@app.route("/decline", methods=["POST"])\
def decline():\
    data = request.json\
    if not data:\
        return jsonify(\{"error": "no json"\}), 400\
\
    # Batch-\uc0\u1088 \u1077 \u1078 \u1080 \u1084 \
    if "texts" in data:\
        results = []\
        for text in data["texts"]:\
            if text in cache:\
                results.append(cache[text])\
            else:\
                declined = decline_phrase(text)\
                cache[text] = declined\
                results.append(declined)\
        return jsonify(\{"results": results\})\
\
    # \uc0\u1054 \u1076 \u1080 \u1085 \u1086 \u1095 \u1085 \u1099 \u1081  \u1088 \u1077 \u1078 \u1080 \u1084 \
    text = data.get("text")\
    if not text:\
        return jsonify(\{"error": "no text"\}), 400\
\
    if text in cache:\
        return jsonify(\{"result": cache[text]\})\
\
    declined = decline_phrase(text)\
    cache[text] = declined\
    return jsonify(\{"result": declined\})\
\
@app.route("/health")\
def health():\
    return "OK"\
\
if __name__ == "__main__":\
    app.run(host="0.0.0.0", port=5000)}