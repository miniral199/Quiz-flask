from flask import Flask,request, render_template_string,session, redirect,url_for

app=Flask(__name__)
app.secret_key="секретный ключ для сесcий"

questions =[
    {"question":"Столица Франции?","answer":"париж"},
    {"question":"Столица Италии?","answer":"рим"},
    {"question":"Столица Японии?","answer":"токио"}
]

HTML_TEMPLATE = """

<!DOCTYPE html>
<html>
<head>
    <title>Викторина</title>
    <style>
        body{
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 100px;
        }
        input{
            font-size:18px;
            padding: 10px;
            width:250px;
        }    
        button{
            font-size:18px;
            padding: 10px 20px;
            cursor: pointer;
        }
        .result{
            font-size:20px;
            margin-top: 20px;
        }
        .correct{color:green;}
        .wrong{color:red;}
        .score{
            font-size:16px;
            color:gray;
            margin-top:10px;
        }
    </style>
</head>
<body>
    {% if finished %}
        <h1>Викторина окончена!</h1>
        <p class="result" style="color:blue;">Итог: {{score}} из {{total}}</p>
        <a href="{{url_for('restart')}}">Пройти заново</a>
    {% else %}
        <h1> {{question}} </h1>
        <p class="score"> Вопрос {{current}} из {{ total }} | Счёт: {{score}}</p>
        <form method="POST">
            <input type="text" name="answer" placeholder="Ваш ответ" autofocus>
            <br><br>
            <button type="submit"> Проверить </button>
        </form>
        {% if result %}
            <p class= "result {{color}}"> {{result}}</p>
        {%endif%}
    {%endif%}
</body>
</html>
"""


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
        return render_template_string(
            HTML_TEMPLATE,
            finished=True,
            score=score,
            total=total
        )
    result = session.get("result")
    color= session.get("color")

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

    #Очищение результата для нового вопроса
    session["result"]=None
    session["color"]=None

    return render_template_string(
        HTML_TEMPLATE,
        finished=False,
        question=questions[current]["question"],
        current=current+1,
        total=total,
        score=score,
        result=result,
        color=color
    )

@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("quiz"))

if __name__=="__main__":
    app.run(debug=True)