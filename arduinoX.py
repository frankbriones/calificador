import serial
import json
import sys
import os
import time
from tkinter import *
from tkinter import messagebox as mb
from datetime import datetime
import MySQLdb
# import mysql.connector


bEncontrado = False
#verifica si existe un arduino disponible.
for iPuerto in range(0, 20):
  try:
    PUERTO = 'COM' + str(iPuerto)
    VELOCIDAD = '9600'
    Arduino = serial.Serial(PUERTO, VELOCIDAD)
    Arduino.close()
    bEncontrado = True
    break
  except :
    pass
if bEncontrado:
    print("el puerto del arduino es {}".format(PUERTO))
else:
    print("Arduino no encontrado.")

'''inicializar la ventana de tkinter'''
def run():
    window = Tk()
    var1 = StringVar() #variable que contendra el mensaje o calificacion
    var2 = StringVar() #mensaje de inactivacion
    var2.set('Inactivo')

    var3 = StringVar() 
    var3.set('Conectado')

    window.title("Sistema de Calificaion Orocash V1.0 ")#titulo de la ventana
    window.geometry('480x250')#dimensiones de la interfaz
    #icono
    #icono = window.iconbitmap(default='oroc.ico')
    font = "-family {@Arial Unicode MS} -size 12 -weight bold -slant roman  -overstrike 0"#establecer un fromato al boton de salir


    '''intentar una conexion, luego de haber buscado el puerto'''

    try:

        conexion = serial.Serial(PUERTO, VELOCIDAD, timeout=.2)#realiza la comunicacion entre el cpu y el arduino

        '''funcion para activar el calificador'''
        def activar():
            conexion.write(b'1')
            x = var2.get()

            if x == 'Inactivo':
                var2.set('Activo')
                lbl1.config(textvariable=var2, font = font, bg = 'yellow', fg = 'black', highlightbackground= 'black',
                    borderwidth = 3, relief=RAISED)
            window.after(10000, desactivar)
        '''descativar el calificador''' 
        def desactivar():
            conexion.write(b'0')
            y = var2.get()
            print(y)
            if y == 'Activo':
                var2.set('Inactivo')
                lbl1.config(textvariable=var2, font = font, bg = 'azure4', fg = 'black', highlightbackground= 'black',
                    borderwidth = 3, relief=RAISED)

        def salir():
            conexion.write(b'0') # set Arduino output pin 13 low and quit
            conexion.close() # close serial port
            quit()
                    
        '''realizar una lectura constante, para revisar si existe algun dato en la variable 
        de calificacion'''
        def calificacion_label(label):
            def calificacion():
                #verifica el envio de datos del arduino
                
                var1.set(conexion.readline().decode('utf-8').strip())

                #label.config(text="CALIFICACION ALMACENADA", fg="blue", font=("Arial Bold", 20))
                if var1.get() == '':
                    '''mensaje que se muestra en el label al iniciar el ejecutable'''
                    label.config(text="MODULO DE CALIFICACION", fg="red", font=("Arial Bold", 15))
                    label.after(1000, calificacion)
                else:
                    '''si se recibe una lectura desde el arduin, se procede a realizar el registro
                    en un arhcivo, o enviar directamente a la base de datos los pendientes mas el nuevo
                    registro o tan solo el nuevo registro'''
                    print (var1.get())
                    hora = time.strftime('%X')
                    hora = (hora[:8])
                    clf = var1.get()[4:]
                    identificador = var1.get()[:4]
                    hoy = datetime.now().date()

                    
                    archivo = open("test.txt", "a")
                    archivo.write(clf + ',')
                    archivo.write(str(hoy )+',')
                    archivo.write(str(0)+',')
                    archivo.write(hora +',')
                    archivo.write(identificador+',')
                    archivo.write(str(1)+',')
                    archivo.write(str(1)+',')
                    archivo.write('\n')
                    archivo.close()
                    lineas = open("test.txt", "r")            
                    longitud  = len(lineas.readlines())
                    lineas.close()
                    
                    '''verficamos si en  el archivo tiene alguna longitud, con respecto a las calificaciones 
                    almacenadaas'''
                    if longitud >= 1:
                        '''intentamos realizar una conexion a la base de datos, raspberry en nuestro caso'''
                        try:
                            desactivar()
                            # db = MySQLdb.connect(
                            #     host="localhost",
                            #     user="root",
                            #     passwd="ROOT",
                            #     db="prueba"
                            # )
                            # cursor = db.cursor()
                            
                            #raspberry

                            db = MySQLdb.connect(
                                host="192.168.100.92",
                                user="frank",
                                passwd="frank",
                                db="prueba2"
                            )
                            cursor = db.cursor()
                            '''si existe mas de un registro en el archivo, y se mantiene una conexion con la bd,
                            procedemos a realizar el INSERT de los datos y luego se desactiva el calificador'''
                            for row in open("test.txt", "r"):
                                lista = row.split(',')
                                cursor.execute("INSERT INTO registro_registro(calificacion, created, estado, hora, identificador, tienda_id, usuario_id) VALUES ('{}', '{}', '{}', '{}', '{}', '{}','{}')".format(lista[0], lista[1], lista[2], lista[3], lista[4], lista[5], lista[6]))
                                db.commit()
                            db.close()
                            label.config(text="Registro realizado", font=font)
                            print("registro exitoso.")
                            '''ponemos el archivo en blanco, sin opcion a recuperar la informacion'''
                            remplazo = open('test.txt', 'w')
                            remplazo.close()
                        except:
                            '''si no se realiza la conexion con la base, muestra un mensaje
                            de conexion fallida y desactivamos el calificador'''
                            label.config(text="Conexion con la Base de Datos, fallida!", font=font)
                            print("Fallo la conexion con la base de datos.")
                            # desactivar()
                        # except MySQLdb.Error as error
                        #     print("Failed to insert record into MySQL table {}".format(error))
                            
                    else:
                        '''si no existe registro en el archivo, no procedemos hacer nada'''
                        pass
                    
                    #mb.showinfo("informacion", "Cerrar Ventana")
                    # window.destroy()
                    label.after(1000, calificacion)
                    '''actualizamos cada segundo,
                    el mensaje para cambiar su informacion,
                    como se muestra en la linea de codigo en la parte de arriba'''

            calificacion()


        def update():
            '''creamos el label que mostrar los mensajes en pantalla'''
            label = Label(window, fg="green", font=("Arial Bold", 20))
            label.pack()
            calificacion_label(label)
            

        btn2 = Button(window, text="Activar", bg="dark goldenrod", fg="white", overrelief="raised",command=activar, font=font)
        btn2.place(relx=0.10, rely=0.50, height=40, width=80)
        

        # btn3 = Button(window, text="Desactivar", bg="red", fg="white", overrelief="raised", command=desactivar, font=font)
        # btn3.place(relx=0.45, rely=0.50, height=40, width=85)

        btn = Button(window, text="Salir", command=salir, font=font, bg="steel blue",fg="white", cursor="hand2", overrelief="raised")
        btn.place(relx=0.75, rely=0.50, height=40, width=80)

        lbl1 = Label (window, textvariable=var2, font = font, bg = 'azure4', fg = 'black', highlightbackground= 'black',
            borderwidth = 3, relief=RAISED)
        lbl1.pack()

        lblx = Label (window, textvariable=var3, fg = 'black', highlightbackground= 'black',
            borderwidth = 3)
        lblx.place(relx=0.38, rely=0.80, height=30, width=120)
        

        window.after(100, update)
        window.mainloop()

    except serial.SerialException:
        ''' si no se establece comunicacion con el arduino, 
        se muesttra una ventana diferente con el error '''
        print("Intento de conexion fallida.")
        window.title("Sistema de Calificaion Orocash V1.0 ")
        window.geometry("480x120")
        textito = Label(window, text="Calificador No encontrado,\n Verifique la conexion.", font=font)
        textito.pack()
        btn = Button(window, text="Salir", command="exit", font=font, bg="CadetBlue",fg="white", cursor="hand2", overrelief="raised")
        btn.place(relx=0.40, rely=0.60, height=40, width=80)
        window.mainloop()


if __name__ == '__main__':
    print('Ejecutando Programa')
    run()


