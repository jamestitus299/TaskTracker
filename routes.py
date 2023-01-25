from flask import current_app, Blueprint, render_template, request, redirect, url_for
import datetime
import uuid

pages = Blueprint("tasks", __name__, template_folder="templates", static_folder="Static")


@pages.context_processor
def addCalcDateRnge():
    def dateRange(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff)
                 for diff in range(-3, 4)]
        return dates
    return {"dateRange": dateRange}


def todayMidnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)


def Cday():
    return datetime.datetime.today()


@pages.route("/", methods=["GET", "POST"])
def index():
    dateStr = request.args.get("date")
    if dateStr:
        selectedDate = datetime.datetime.fromisoformat(dateStr)
    else:
        selectedDate = todayMidnight()

    today = todayMidnight()
    if request.method == "POST":
        data = request.form.get("task")
        if (data):
            if( len(list(current_app.db.tasks.find({"name" : data}))) == 0 ):
                current_app.db.tasks.insert_one(
                    {"_id": uuid.uuid4().hex, "added": today, "name": data}
                )

    tasksOnDay = current_app.db.tasks.find({"added" : {"$lte" : selectedDate}})
    completions = [
        taskD["name"]
        for taskD in current_app.db.completions.find({"date" : {"$eq" : selectedDate}})
    ]

    return render_template("index.html", tasks=tasksOnDay, title="Task Tracker - Home",
                           selectedDate=selectedDate, completions=completions, CurrentDay=Cday())


@pages.route("/add", methods=["GET", "POST"])
def addTask():
    today = todayMidnight()
    return render_template("addTask.html", title="Task Tracker - Add Task",
                           CurrentDay=Cday(), selectedDate=today)


@pages.route("/complete", methods=["POST"])
def complete():
    dateStr = request.form.get("date")
    task = request.form.get("taskName")
    date = datetime.datetime.fromisoformat(dateStr)
    current_app.db.completions.insert_one({"date": date, "name": task})
    current_app.db.tasks.delete_one({"name": task})

    return redirect(url_for("tasks.index", date=date))
