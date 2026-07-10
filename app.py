from flask import Flask, request, render_template, session, redirect, url_for
from gigachat import GigaChat
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = "секретный ключ для сессий"


def get_questions(topic, count):
    """Генерирует вопросы через GigaChat"""
    client = GigaChat(
        credentials=os.getenv("GIGACHAT_SECRET"),
        user=os.getenv("GIGACHAT_CLIENT_ID"),
        verify_ssl_certs=False
    )

    prompt = f"""
    Сгенерируй {count} вопросов для викторины на тему "{topic}".
    Верни ТОЛЬКО JSON-массив в таком формате:
    [{{"question": "Вопрос?", "answer": "правильный ответ"}}]
    Ответы должны быть краткими (1-3 слова).
    Не добавляй комментарии, только JSON.
    """

    response = client.chat(prompt)
    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]

    return json.loads(raw)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        count = int(request.form.get("count", 5))

        if not topic:
            return render_template("index.html", error="Введите тему")

        try:
            questions = get_questions(topic, count)
        except Exception as e:
            return render_template("index.html", error=f"Ошибка генерации: {e}")

        session["questions"] = questions
        session["current"] = 0
        session["score"] = 0
        session["result"] = None
        session["color"] = None
        session["topic"] = topic

        return redirect(url_for("quiz"))

    return render_template("index.html")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "questions" not in session:
        return redirect(url_for("index"))

    questions = session["questions"]
    current = session["current"]
    score = session["score"]
    total = len(questions)

    if current >= total:
        return render_template(
            "quiz.html",
            finished=True,
            score=score,
            total=total
        )

    result = session.get("result")
    color = session.get("color")

    if result:
        prev_question = questions[current - 1]["question"]
        return render_template(
            "quiz.html",
            show_result=True,
            question=prev_question,
            current=current,
            total=total,
            score=score,
            result=result,
            color=color
        )

    if request.method == "POST":
        user_answer = request.form.get("answer", "").strip().lower()
        correct_answer = questions[current]["answer"]

        if user_answer == correct_answer.lower():
            result = "Правильно!"
            color = "correct"
            session["score"] += 1
        else:
            result = f"Неправильно. Правильный ответ: {correct_answer.title()}"
            color = "wrong"

        session["result"] = result
        session["color"] = color
        session["current"] += 1
        session.modified = True
        return redirect(url_for("quiz"))

    return render_template(
        "quiz.html",
        show_result=False,
        question=questions[current]["question"],
        current=current + 1,
        total=total,
        score=score,
        result=None,
        color=None
    )


@app.route("/next")
def next_question():
    session["result"] = None
    session["color"] = None
    return redirect(url_for("quiz"))


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")