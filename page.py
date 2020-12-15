from flask import Flask , render_template, request, redirect, flash, url_for
from flask_wtf import FlaskForm , Form
from wtforms import StringField,PasswordField,DateField,SubmitField,validators,IntegerField
from wtforms.validators import DataRequired, InputRequired, Length
import yagmail as yagmail
import os
import sqlite3 
from sqlite3 import Error

app= Flask(__name__)
app.secret_key=os.urandom(24)

class Login_Form(FlaskForm):
    username=StringField('usuario',validators=[validators.Length(min=4, max=25),InputRequired()])
    password=PasswordField('password',validators=[validators.Length(min=4, max=25),InputRequired()])
    loginbtn=SubmitField('Ingresar')
    

class Register_Form(FlaskForm):
    signupbtn=SubmitField('Registrarse')
    forgotbtn=SubmitField('Recuperar Password')

class Signup_Form(FlaskForm):
    username=StringField('usuario',validators=[validators.Length(min=1, max=50),validators.DataRequired()])
    name=StringField('nombre',validators=[validators.Length(min=1, max=50),validators.DataRequired()])
    password=PasswordField('password',validators=[validators.DataRequired(), validators.EqualTo('repassword', message='Contraseña no son Iguales')])
    repassword=PasswordField('repassword')
    email=StringField('email',validators=[validators.DataRequired()])
    telefono=StringField('telefono',validators=[validators.DataRequired()])
    born= DateField('Naciemiento',validators=[validators.DataRequired()],format='%d/%m/%Y')
    nextbtn= SubmitField('Siguiente')

class Delete_Form(FlaskForm):
    userid= StringField('userid',validators=[validators.DataRequired()]) 
    deletebtn= SubmitField('Borrar Usuario')





@app.route('/',methods=["GET","POST"])

def index():
    login_form = Login_Form()
    register_form= Register_Form()
    

    return render_template('login.html',login_form = login_form, register_form=register_form)                


@app.route('/forgot',methods=["GET","POST"])
def forgot():
    try:
        if request.method=="POST":
            if request.form['btnforgot'] == "Recuperar":
               email= request.form['email']
               print(email)
               yag=yagmail.SMTP('uninortegrupo6@gmail.com','%Grupo6%')
               yag.send(to=email,subject='Activa tu Cuenta',contents='Usa este vinculo para activar tu cuenta('+request.method+')')
               if (email== None):
                   flash('Escribe un correo')
               else:
                   flash('Revisa tu Correo para activar Cuenta')

            if request.form['btnforgot']=="Ingresar":
                return redirect('login')

        else:
            email= request.args.get('email')

        return render_template('forgot.html') 

    except: return render_template('forgot.html')          

    return render_template('forgot.html')

@app.route('/login',methods=["GET","POST"])
def login():
    login_form = Login_Form()
    register_form= Register_Form()
    try:
        if request.method =='POST':
            if login_form.is_submitted():
                if login_form.loginbtn.data and login_form.validate(): 
                    usuario= login_form.username.data
                    contraseña= login_form.password.data
                    
                    if usuario =="prueba" and contraseña=="prueba1234":
                        return redirect('main')
                    elif usuario =="admin" and contraseña=="admin":
                        return redirect('admin')    
           
        return render_template('login.html',login_form = login_form, register_form=register_form)         

    except:
        return render_template('login.html',login_form = login_form, register_form=register_form)


@app.route('/register',methods=["GET","POST"])
def register():
    try:
        login_form = Login_Form()
        register_form= Register_Form()
        if request.method =='POST':
            
            if register_form.is_submitted:
                if register_form.forgotbtn.data:
                    return redirect('forgot')
                elif register_form.signupbtn.data:
                    return redirect('signup')    

        return render_template('login.html',login_form = login_form, register_form=register_form)   

    except:
        return render_template('login.html',login_form = login_form, register_form=register_form)



@app.route('/signup',methods=["GET","POST"])
def signup():
   
    signup_form = Signup_Form()
    try:
        if request.method=="POST":
            
            if signup_form.is_submitted():
                
                if signup_form.nextbtn.data and signup_form.validate(): 
                       
                    try:
                        usuario = signup_form.username.data
                        nombre = signup_form.username.data
                        password = signup_form.password.data
                        correo = signup_form.email.data
                        telefono = signup_form.telefono.data
                        date = signup_form.born.data
                        link_user = "link"
                        rol = "usuario"
                        
                        con = sqlite3.connect("BaseDatos.db")
                        cur = con.cursor()
                        cur.execute("INSERT into usuarios (usuario,nombre,password,correo,telefono,date,link_user,rol) values (?,?,?,?,?,?,?,?)",(usuario,nombre,password,correo,telefono,date,link_user,rol))
                        con.commit()
                    except:
                        con.rollback()  
                    finally:
                        con.close()
                        return redirect('main')
                          

        return render_template('signup.html',signup_form=signup_form)
    except:render_template('signup.html',signup_form=signup_form)

@app.route('/view')
def view():
    con = sqlite3.connect("BaseDatos.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios")
    rows = cur.fetchall()
    con.close()
    return render_template("view.html", rows=rows)
    

@app.route("/delete", methods=["GET","POST"])
def delete():
    delete_form= Delete_Form()
    if request.method=="POST":
        if delete_form.is_submitted():
            print("submitted")
            if delete_form.deletebtn.data and delete_form.validate():
                userid = delete_form.userid.data
                print(userid)
                con = sqlite3.connect("BaseDatos.db")
                try:
                    cur=con.cursor()
                    cur.execute("DELETE FROM usuarios where id = ?", userid)
                    con.commit()
                    msg = "Registro eliminado exitosamente"
                except:
                    con.rollback()  
                    msg = "No se pudo eliminar el registro"
                finally:
                    con.close() 
                    return redirect('view')              

    return render_template('delete.html',delete_form=delete_form)


@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/search')
def search():
    return render_template('search.html')  

@app.route('/edit')
def edit():
    return render_template('edit.html')    


@app.route('/admin')
def admin():
    return render_template('admin.html')       





if __name__=="__main__":
    app.run(debug=True)   



