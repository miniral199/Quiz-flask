from flask import Flask,request, render_template,session, redirect,url_for
from questions import questions

app=Flask(__name__)
app.secret_key="секретный ключ для сесcий"





@app.route("/", methods=["GET","POST"])
def quiz():
    if "current" not in session:
        session["current"]=0
        session["score"]=0
        session["result"]=None
        session["color"]=None

    current=session["current"]
    score=session["score"]
    total=len(questions)

    #если викторина закончена
    if current >= total:
        return render_template(
            "quiz.html",
            finished=True,
            score=score,
            total=total
        )
    result = session.get("result")
    color= session.get("color")

    if result:
        return render_template(
            "quiz.html",
            show_result=True,
            question=questions[current-1]["question"],
            current=current,
            total=total,
            score=score,
            result=result,
            color=color
        )


    if request.method=="POST":
        user_answer=request.form.get("answer","").strip().lower()
        correct_answer=questions[current]["answer"]

        if user_answer == correct_answer:
            result="Правильно!"
            color="correct"
            session["score"]+=1
        else:
            result=f"Неправильно. Правильный ответ:{correct_answer.title()}"
            color="wrong"

        session["result"]=result
        session["color"]=color
        session["current"]+=1
        session.modified=True
        return redirect(url_for("quiz"))

    return render_template(
        "quiz.html",
        show_result=False,
        question=questions[current]["question"],
        current=current+1,
        total=total,
        score=score,
        result=None,
        color=None
    )

@app.route("/next")
def next_question():
    # Очищаем результат и переходим на главную
    session['result']=None
    session["color"]=None
    return redirect(url_for("quiz"))

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("quiz"))

if __name__=="__main__":
    app.run(debug=True)
