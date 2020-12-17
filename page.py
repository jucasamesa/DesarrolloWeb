from flask import Flask , render_template, request, redirect, flash, url_for, session
from flask_wtf import FlaskForm , Form
from wtforms.fields.html5 import DateField, EmailField, TelField
from wtforms import StringField,PasswordField,SubmitField,validators,IntegerField, Label
from wtforms.validators import DataRequired, InputRequired, Length
import yagmail as yagmail
import os
import sqlite3 
from sqlite3 import Error
from werkzeug.security import generate_password_hash , check_password_hash
from werkzeug.datastructures import MultiDict

app= Flask(__name__)
app.secret_key=os.urandom(24)

class Login_Form(FlaskForm):
    username=StringField('usuario',validators=[InputRequired(message="Campo Requerido")])
    password=PasswordField('password',validators=[InputRequired(message="Campo Requerido")])
    loginbtn=SubmitField('Ingresar')
    
class Register_Form(FlaskForm):
    signupbtn=SubmitField('Registrarse')
    forgotbtn=SubmitField('Recuperar Password')

class Signup_Form(FlaskForm):
    username=StringField('usuario',validators=[validators.Length(min=3, max=20,message="Debe tener más de 3 caracteres"),validators.DataRequired(message="Campo Requerido")])
    name=StringField('nombre',validators=[validators.Length(min=3, max=20,message="Debe tener más de 3 caracteres"),validators.DataRequired(message="Campo Requerido")])
    password=PasswordField('password',validators=[validators.Length(min=6, max=50,message="Debe tener más de 6 caracteres"),validators.DataRequired(message="Campo Requerido"), validators.EqualTo('repassword', message='Contraseña no son Iguales')])
    repassword=PasswordField('repassword')
    email=EmailField('email',validators=[validators.DataRequired(message="Campo Requerido")])
    telefono=TelField('telefono',validators=[validators.DataRequired(message="Campo Requerido"),validators.Length(min=10, max=10,message="Debe tener diez dígitos")])
    born= DateField('Naciemiento',validators=[validators.DataRequired(message="Campo Requerido")],format='%Y-%m-%d')
    nextbtn= SubmitField('Siguiente')

class Delete_Form(FlaskForm):
    userid= StringField('userid',validators=[validators.DataRequired(message="Id de usuario Requerido")]) 
    deletebtn= SubmitField('Borrar Usuario')

class Configuracion_Form(FlaskForm):
    
    name=StringField('nombre',validators=[validators.Length(min=3, max=20,message="Debe tener más de 3 caracteres"),validators.DataRequired(message="Campo Requerido")])
    password=PasswordField('password',validators=[validators.Length(min=6, max=50,message="Debe tener más de 6 caracteres"),validators.DataRequired(message="Campo Requerido"), validators.EqualTo('repassword', message='Contraseña no son Iguales')])
    repassword=PasswordField('repassword')
    email=EmailField('email',validators=[validators.DataRequired(message="Campo Requerido")])
    telefono=TelField('telefono',validators=[validators.DataRequired(message="Campo Requerido"),validators.Length(min=10, max=10,message="Debe tener diez dígitos")])
    born= DateField('Naciemiento',validators=[validators.DataRequired(message="Campo Requerido")],format='%Y-%m-%d')
    nextbtn= SubmitField('Siguiente')   


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
                    password= login_form.password.data
                                                               
                    if usuario !="" and password !="":
                               
                        try:
                            con = sqlite3.connect('BaseDatos.db')
                            cur = con.cursor()
                            print("Connected to SQLite")
                            
                            cur.execute("SELECT password,rol FROM usuarios WHERE usuario = ? ",[usuario])
                            records = cur.fetchall()
                            size = len(records)
                            print("Total rows are:  ", size)
                            print("Printing each row")
                            
                            if size == 0:
                                flash("Usuario o contraseña incorrectos") 
                            else:
                                for row in records:
                                    print("password: ", row[0])
                                    print("rol: ", row[1])
                                    temp = row[0]
                                    rol = row[1]
                                    
                                    print(check_password_hash(temp,password))
                                
                                if check_password_hash(temp,password) is True:
                                
                                    if rol == "admin":
                                        session["admin"] = usuario 
                                        return redirect('view')
                                    else:
                                        session["usuario"] = usuario 
                                        return redirect('main') 
                                    cur.close()                            

                        except sqlite3.Error as error:
                            print("Failed to read data from table", error)
                        
                        finally:
                            if (con):
                                con.close()
                                print("The Sqlite connection is closed")
                       
                    else:
                        flash("Usuario o contraseña invalidos")    
                                  
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
                        nombre = signup_form.name.data
                        password = signup_form.password.data
                        clavehash = generate_password_hash(password)
                        correo = signup_form.email.data
                        telefono = signup_form.telefono.data
                        date = signup_form.born.data
                        link_user = "link"
                        rol = "usuario"
                        
                        con = sqlite3.connect('BaseDatos.db')
                        cur = con.cursor()
                        print("Connected to SQLite")

                        cur.execute("SELECT DISTINCT usuario FROM usuarios WHERE usuario = ?", [usuario])
                        records = cur.fetchall()
                        print("Total rows are:  ", len(records))
                        print("Printing each row")
                        temp = ""
                        for row in records:
                            print("Usuario: ", row[0])
                            temp = row[0]
                            
                        if temp == usuario:
                            flash("El usuario ya existe")
                            cur.close()
                        else:
                            print("Entro al else")
                            cur.execute("INSERT into usuarios (usuario,nombre,password,correo,telefono,date,link_user,rol) values (?,?,?,?,?,?,?,?)",[usuario,nombre,clavehash,correo,telefono,date,link_user,rol])
                            con.commit()
                            session["usuario"] = usuario 
                            return redirect('main')        

                    except sqlite3.Error as error:
                        print("Failed to read data from table", error)
                    
                    finally:
                        if (con):
                            con.close()
                            print("The Sqlite connection is closed")   
                    
        return render_template('signup.html',signup_form=signup_form)
    except:render_template('signup.html',signup_form=signup_form)

@app.route('/view')
def view():
    if "admin" in session:
        con = sqlite3.connect("BaseDatos.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM usuarios")
        rows = cur.fetchall()
        con.close()
        return render_template("view.html", rows=rows)
    else:
        return redirect('login')

@app.route("/delete", methods=["GET","POST"])
def delete():
    if "admin" in session:
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
                        cur.execute("DELETE FROM usuarios where id = ?", [userid])
                        con.commit()
                        msg = "Registro eliminado exitosamente"
                    except:
                        con.rollback()  
                        msg = "No se pudo eliminar el registro"
                    finally:
                        con.close() 
                        return redirect('view')              

        return render_template('delete.html',delete_form=delete_form)
    
    else:
        return redirect('login')

@app.route('/add')
def add():
    if "usuario" in session:
        return render_template('add.html')
    else:
        return redirect('login')

@app.route('/main')
def main():
    
    if "usuario" in session:
        return render_template('main.html')
    else:
        return redirect('login')

@app.route('/search')
def search():
    
    if "usuario" in session:
        return render_template('search.html')
    else:
        return redirect('login')

@app.route('/edit')
def edit():
    if "usuario" in session:
        return render_template('edit.html')
    else:
        return redirect('login')



@app.route('/logout')
def logout():
    session.pop("usuario",None)
    return redirect('login') 

@app.route('/configuracion')
def configuracion():
    
    try:
        con = sqlite3.connect('BaseDatos.db')
        cur = con.cursor()
        print("Connected to SQLite")
        
        cur.execute("SELECT nombre,correo,telefono,date FROM usuarios WHERE usuario = ? ",[session['usuario']])
        records = cur.fetchall()
        size = len(records)
        print("Total rows are:  ", size)
        print("Printing each row")
        
        
        for row in records:
           
            nombre = row[0]
            correo=row[1]
            telefono=row[2]
            fecha=row[3]

        configuracion_form = Configuracion_Form(formdata=MultiDict({'name':nombre,'email':correo,'telefono':telefono,'born':fecha}))        
        

    except sqlite3.Error as error:
        print("Failed to read data from table", error)

    finally:
        if (con):
            con.close()
            print("The Sqlite connection is closed")
           
    return render_template('configuracion.html',configuracion_form=configuracion_form)     

     
    

@app.route('/update',methods=["GET","POST"])
def update():
    
    configuracion_form = Configuracion_Form()
    try:
        if request.method=="POST":
            print("Entro 1 ")
            if configuracion_form.is_submitted():
                print("Entro 2")
                if configuracion_form.nextbtn.data and configuracion_form.validate(): 
                    print("Entro 3")
                    try:
                        print("Entro 4 ")
                        nombre = configuracion_form.name.data
                        password = configuracion_form.password.data
                        clavehash = generate_password_hash(password)
                        correo = configuracion_form.email.data
                        telefono = configuracion_form.telefono.data
                        date = configuracion_form.born.data
                        link_user = "link"
                        rol = "usuario"

                        print(nombre,password,correo,telefono,date,link_user,rol)
                        
                        con = sqlite3.connect('BaseDatos.db')
                        cur = con.cursor()
                        cur.execute("UPDATE usuarios SET nombre=(?),password=(?),correo=(?),telefono=(?),date=(?),link_user=(?),rol=(?) WHERE usuario=(?)",[nombre,clavehash,correo,telefono,date,link_user,rol,session['usuario']])
                        con.commit()
                         
                                  

                    except sqlite3.Error as error:
                        print("Failed to read data from table", error)
                        redirect('configuracion')
                    
                    finally:
                        if (con):
                            con.close()
                            print("The Sqlite connection is closed") 
                        return redirect('configuracion')        
                    
        return redirect('configuracion')
    except:redirect('configuracion')


if __name__=="__main__":
    app.run(debug=True)   




