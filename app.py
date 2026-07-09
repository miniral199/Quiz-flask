from flask import Flask, request, render_template, session, redirect, url_for
from questions import questions
import random

app = Flask(__name__)
app.secret_key = "секретный ключ для сессий"


@app.route("/", methods=["GET", "POST"])
def quiz():
    # Если нет order или current — полная инициализация
    if "current" not in session or "order" not in session:
        session["current"] = 0
        session["score"] = 0
        session["result"] = None
        session["color"] = None
        shuffled = questions.copy()
        random.shuffle(shuffled)
        session["order"] = [q["question"] for q in shuffled]
        session["answers"] = [q["answer"] for q in shuffled]

    current = session["current"]
    score = session["score"]
    total = len(session["order"])
    question_text = session["order"][current] if current < total else ""
    correct_answer = session["answers"][current] if current < total else ""

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
        prev_question = session["order"][current - 1]
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
        question=question_text,
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
    return redirect(url_for("quiz"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")