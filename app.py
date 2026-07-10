from flask import Flask, request, render_template, session, redirect, url_for
from gigachat import GigaChat
from dotenv import load_dotenv
import os
import json
import random

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
    [{{"question": "Вопрос?", "answer": "правильный ответ", "options": ["неправильный1", "неправильный2", "неправильный3"]}}]
    Правила:
    - "answer" — правильный ответ, КРАТКИЙ: 1-3 слова.
    - "options" — ТРИ неверных, но правдоподобных варианта ответа, тоже кратких.
    - Всего 4 варианта: 1 правильный + 3 неверных.
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

    result = session.get("result")
    color = session.get("color")

    # Если есть результат и викторина окончена — показываем итог
    if current >= total and result:
        return render_template(
            "quiz.html",
            finished=True,
            score=score,
            total=total,
            last_result=result,
            last_color=color
        )

    # Если викторина окончена без результата (после /next)
    if current >= total:
        return render_template(
            "quiz.html",
            finished=True,
            score=score,
            total=total,
            last_result=None,
            last_color=None
        )

    # Показываем результат текущего ответа
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

        # Умная проверка
        correct_lower = correct_answer.lower().strip()

        stop_words = {"в", "на", "из", "под", "над", "около", "возле", "это", "город", "страна", "государство"}
        user_words = [w for w in user_answer.split() if w not in stop_words]
        user_clean = " ".join(user_words)

        is_correct = (
            user_answer == correct_lower or
            user_clean == correct_lower or
            user_answer in correct_lower or
            correct_lower in user_answer or
            user_clean in correct_lower or
            correct_lower in user_clean or
            any(word in correct_lower for word in user_words if len(word) > 2) or
            any(word in user_clean for word in correct_lower.split() if len(word) > 2)
        )

        if is_correct:
            result = "Правильно!"
            color = "correct"
            session["score"] += 1
        else:
            result = f"Неправильно. Правильный ответ: {correct_answer}"
            color = "wrong"

        session["result"] = result
        session["color"] = color
        session["current"] += 1
        session.modified = True
        return redirect(url_for("quiz"))

    # Перемешиваем варианты ответов
    options = [questions[current]["answer"]] + questions[current].get("options", [])
    random.shuffle(options)

    return render_template(
        "quiz.html",
        show_result=False,
        question=questions[current]["question"],
        options=options,
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