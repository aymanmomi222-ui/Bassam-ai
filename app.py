import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# ما تحطش API Key هنا
# غادي ناخدو من Environment Variable ديال الاستضافة
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Bassam AI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #101614;
    color: white;
}

header {
    background: #18231f;
    padding: 18px;
    text-align: center;
    font-size: 25px;
    font-weight: bold;
}

#chat {
    height: calc(100vh - 145px);
    overflow-y: auto;
    padding: 15px;
}

.message {
    max-width: 88%;
    padding: 12px 15px;
    margin: 10px 0;
    border-radius: 15px;
    line-height: 1.7;
    white-space: pre-wrap;
}

.user {
    background: #285b48;
    margin-right: auto;
}

.ai {
    background: #202b27;
    margin-left: auto;
}

.message img {
    max-width: 240px;
    max-height: 240px;
    display: block;
    margin-top: 8px;
    border-radius: 12px;
}

#bottom {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #18231f;
    padding: 10px;
    display: flex;
    gap: 7px;
}

#input {
    flex: 1;
    min-width: 0;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid #40564d;
    background: #101614;
    color: white;
    outline: none;
}

button,
label {
    border: none;
    background: #2f7058;
    color: white;
    padding: 11px 14px;
    border-radius: 12px;
    cursor: pointer;
    font-size: 16px;
}

#file {
    display: none;
}

#imageBox {
    position: fixed;
    bottom: 70px;
    right: 10px;
    display: none;
    background: #202b27;
    padding: 8px;
    border-radius: 12px;
}

#preview {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 10px;
}

#removeImage {
    display: block;
    width: 100%;
    margin-top: 5px;
    background: #8b3a3a;
}

</style>
</head>


<body>

<header>
🤖 Bassam AI
</header>


<div id="chat">

<div class="message ai">
سلام 👋 أنا Bassam AI
كيفاش نقدر نعاونك؟
</div>

</div>


<div id="imageBox">

<img id="preview">

<button id="removeImage">
حذف الصورة
</button>

</div>


<div id="bottom">

<label for="file">
📷
</label>

<input
id="file"
type="file"
accept="image/*"
>

<input
id="input"
type="text"
placeholder="كتب رسالتك هنا..."
>

<button id="send">
إرسال
</button>

</div>


<script>

let selectedImage = null;

const input =
document.getElementById("input");

const send =
document.getElementById("send");

const file =
document.getElementById("file");

const preview =
document.getElementById("preview");

const imageBox =
document.getElementById("imageBox");

const removeImage =
document.getElementById("removeImage");

const chat =
document.getElementById("chat");


function addMessage(text, type, image = null) {

    const div =
    document.createElement("div");

    div.className =
    "message " + type;

    if (text) {
        div.textContent = text;
    }

    if (image) {

        const img =
        document.createElement("img");

        img.src = image;

        div.appendChild(img);
    }

    chat.appendChild(div);

    chat.scrollTop =
    chat.scrollHeight;
}


file.addEventListener(
"change",
function () {

    const selectedFile =
    this.files[0];

    if (!selectedFile) {
        return;
    }

    const reader =
    new FileReader();

    reader.onload =
    function (event) {

        selectedImage =
        event.target.result;

        preview.src =
        selectedImage;

        imageBox.style.display =
        "block";
    };

    reader.readAsDataURL(selectedFile);
});


removeImage.addEventListener(
"click",
function () {

    selectedImage = null;

    file.value = "";

    imageBox.style.display =
    "none";
});


async function sendMessage() {

    const text =
    input.value.trim();

    if (!text && !selectedImage) {
        return;
    }

    const image =
    selectedImage;

    addMessage(
        text || "حلل ليا هاد الصورة",
        "user",
        image
    );

    input.value = "";

    selectedImage = null;

    file.value = "";

    imageBox.style.display =
    "none";


    const loading =
    document.createElement("div");

    loading.className =
    "message ai";

    loading.textContent =
    "⏳ كنوجد الجواب...";

    chat.appendChild(loading);

    chat.scrollTop =
    chat.scrollHeight;


    try {

        const response =
        await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type":
                "application/json"
            },

            body: JSON.stringify({

                message: text,

                image: image

            })

        });


        const data =
        await response.json();

        loading.remove();


        if (data.error) {

            addMessage(
                "❌ " + data.error,
                "ai"
            );

        } else {

            addMessage(
                data.reply,
                "ai"
            );

        }


    } catch (error) {

        loading.remove();

        addMessage(
            "❌ مشكل فالاتصال بالسيرفر.",
            "ai"
        );

    }

}


send.addEventListener(
"click",
sendMessage
);


input.addEventListener(
"keydown",
function (event) {

    if (event.key === "Enter") {

        sendMessage();

    }

});

</script>

</body>
</html>
"""


@app.route("/")
def home():

    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():

    if not client:

        return jsonify({
            "error":
            "GROQ_API_KEY ما تحطش فـSecrets ديال الاستضافة."
        }), 500


    try:

        data = request.get_json() or {}

        message = data.get(
            "message",
            ""
        ).strip()

        image = data.get(
            "image"
        )


        if not message:

            message = (
                "حلل ليا هاد الصورة "
                "وشرح ليا شنو فيها."
            )


        content = [

            {
                "type": "text",
                "text": message
            }

        ]


        if image:

            content.append({

                "type": "image_url",

                "image_url": {
                    "url": image
                }

            })


        completion = client.chat.completions.create(

            model="qwen/qwen3.8-27b",

            messages=[

                {
                    "role": "system",

                    "content":
                    "أنت Bassam AI. "
                    "جاوب بوضوح وبطريقة مفهومة. "
                    "استعمل العربية أو الدارجة أو الفرنسية "
                    "حسب لغة المستخدم."
                },

                {
                    "role": "user",
                    "content": content
                }

            ],

            temperature=0.7,

            max_completion_tokens=2048

        )


        reply = (
            completion
            .choices[0]
            .message
            .content
        )


        return jsonify({
            "reply": reply
        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "5000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )