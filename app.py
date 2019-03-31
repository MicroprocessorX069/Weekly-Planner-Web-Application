from flask import Flask,render_template,flash ,redirect,url_for, session, logging,request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, DateField, TextAreaField, PasswordField, validators,SubmitField, Field
from wtforms import TextField
from passlib.hash import sha256_crypt
from functools import wraps


app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_DB']='tasks_temp'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)


# @app.route('/week')
# def index():
#     cur=mysql.connection.cursor()
#     result=cur.execute("SELECT * FROM task")
#     tasks=cur.fetchall()
#     if result>0:
#         return render_template('list_tasks.html',tasks=tasks)
#     else:
#         return "Rohan Vinenet todo"
#
#     cur.close()


@app.route('/week')
def weekTasks():
    percentages=[]
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM TASKS")
    tasks=cur.fetchall()
    for task in tasks:
        completed_no=cur.execute("SELECT COUNT(*) FROM SUBTASKS WHERE (task_id=%s AND subtask_status='Done')",[task['task_id']])
        completed_no=cur.fetchone()
        total_no=cur.execute("SELECT COUNT(*) FROM SUBTASKS WHERE (task_id=%s)",[task['task_id']])
        total_no=cur.fetchone()
        if int(total_no['COUNT(*)'])!=0:
            temp=int(completed_no['COUNT(*)'])*100/int(total_no['COUNT(*)'])
        else:
            temp=0
        percentages.append(int(temp))

    if result>0:

        return render_template('list_tasks.html',tasks=zip(tasks,percentages))
        #return task_ids
        #return ''.join(percentages)
    else:
        return "Rohan Vinenet todo"
    cur.close()

@app.route('/week/<string:task_id>',methods=['GET','POST'])
def taskInfo(task_id):
    st_done_ids=[]
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * from SUBTASKS where (task_id=%s AND subtask_status='Not Done') ",[task_id])
    subtask_info=cur.fetchall()
    cur.close()
    #
    if request.method == "POST":
         st_done_ids = request.form.getlist("subtask_checkbox")
         cur=mysql.connection.cursor()
         for id in st_done_ids:
             cur.execute("UPDATE SUBTASKS SET subtask_status='Done' WHERE subtask_id=%s;",[id])
             print(id)
         mysql.connection.commit()
         result=cur.execute("SELECT * from SUBTASKS where (task_id=%s AND subtask_status='Not Done') ",[task_id])
         subtask_info=cur.fetchall()
         cur.close()
         return render_template('task.html',subtasks=subtask_info )
         #return ''.join(st_done_ids)
    return render_template('task.html',subtasks=subtask_info)

class TaskForm(Form):
    task=StringField('Task')

@app.route('/addtask',methods=['GET','POST'])
def addTask():
    form=TaskForm(request.form)
    if request.method=="POST":
        task_title=form.task.data
        task_date="19.04.06"
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO TASKS(task_title, task_date) VALUES(%s,%s)",(task_title,task_date))
        mysql.connection.commit()
        cur.close()
        flash("Task added",'success')
        return redirect(url_for('index'))
    return render_template('addtask.html',form=form)


class SubTaskForm(Form):
    subtask_text=StringField('Add your Subtask here')
    subtask_date=DateField('By when can you complete it?',id="datepick")

@app.route('/week/<string:task_id>/addsubtask',methods=['GET','POST'])
def addSubTask(task_id):
    form=SubTaskForm(request.form)
    if request.method=="POST":
        subtask_text=form.subtask_text.data
        subtask_date=form.subtask_date.data

        #Adding to the database
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO SUBTASKS(task_id, subtask_text, subtask_date) VALUES(%s,%s,%s)",(task_id,subtask_text,subtask_date))
        mysql.connection.commit()
        cur.close()
        flash("SubTask added",'success')
        #url = "taskInfo("+task_id+")"
        return redirect(url_for('weekTasks'))
    return render_template('addsubtask.html',form=form)



@app.route('/addTask2',methods=['GET','POST'])
def login1():
    # form=TaskForm(request.form)
    if request.method=="POST":
        task=request.form['task']
        # task=form.task.data
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO task(text) VALUES(%s)",[task])
        mysql.connection.commit()
        cur.close()
        flash("Task added",'success')
        return redirect(url_for('index'))
    return render_template('temp.html')








if __name__=="__main__":
    app.secret_key='secret123'
    app.run(debug=True)
