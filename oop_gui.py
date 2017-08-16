import tkinter as tk
import datetime
import os
import os.path
import csv
from tkinter import Canvas
from tkinter import *
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
import http.client, urllib
import pandas  as pd
import minimalmodbus,serial
import struct
import time
#initializing modbus

minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1) 
instrument.serial.baudrate = 9600
instrument.serial.timeout = 1 
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 0.05   
instrument.mode = minimalmodbus.MODE_RTU
instrument.debug = False

xxLARGE_FONT = ("Verdana" , 130)
xLARGE_FONT = ("Verdana" , 100)
LARGE_FONT = ('Verdana',30)
MEDIUM_FONT = ('Verdana' , 15)
SMALL_FONT = ('Verdana',9)

#system variables 
dpress = []
keytext=''
temp = 00.0
rate = 55.81
unit = '/KG'
total = 0 #totalizer gas modbus call
amount = 0

filepath = "/home/pi/Desktop/dispenser/logs/"

key = "EEPNQLIC6COE2UCH"
bit = 0
#pass
mng_pass = '1234'
rt_pass = '5678'
master_keys = '0000'

def reset_total():
    try:
        global temp
        
        values = instrument.write_bit(2,1,5)

    except IOError:
        print("Failed")
def mass_total():
    try:
        global temp
        
        values = instrument.read_registers(258, 2, 3)
        b = struct.pack('HH', values[0],values[1])
        total = int(struct.unpack('f',b)[0])
        return total

    except IOError:
        print("Failed")
       
    
def flow_mass():
    try:
        global temp
        
        values = instrument.read_registers(246, 2, 3)
        b = struct.pack('HH', values[0],values[1])
        flow = int(struct.unpack('f',b)[0])
        return flow

    except IOError:
        print("Failed")
    
def temp_set():
    try:
        global temp
        
        values = instrument.read_registers(250, 2, 3)
        b = struct.pack('HH', values[0],values[1])
        temp = int(struct.unpack('f',b)[0])
        return temp

    except IOError:
        print("Failed")

def get_filename():
    path =r"%s" %filepath
    return os.listdir(path)
def create_file():
    with open(filepath+datetime.datetime.now().strftime("%d-%B-%Y")+".csv","a" , newline = '') as fp:
        a = csv.writer(fp, delimiter = ",")
        data = [datetime.datetime.now().strftime('%H:%M'),amount,rate,temp,unit,total]
        a.writerow(data)

        #sending data to thingsspeak API

        params = urllib.parse.urlencode({'field1':time,'field2':keytext,'field3':rate,'field4':temp,'key':key})
        headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = http.client.HTTPConnection("api.thingspeak.com",port = 80)
        try:
            conn.request("POST", "/update", params, headers)
            response = conn.getrespsone()
            res = response.read()
            conn.close()
        except:
            print("connection failed")

def popup_msg():
    popup = tk.Tk()
    popup.wm_title("Authentication")
    popup.wm_geometry("400x600+120+0")

    #msg
    labelframe = tk.LabelFrame(popup, text = "", font = SMALL_FONT)
    labelframe.pack()
    label = tk.Label(labelframe, text = "Enter Pin", font = MEDIUM_FONT, relief = tk.RIDGE)
    label.grid(row = 0, column =0)
    #display
    s = ""
    ps = tk.Label(labelframe, text = s, font = MEDIUM_FONT, relief = tk.RIDGE)
    ps.grid(row=1, column =0)
    #keypad

    
    star = []
    def click(btn):
        global bit
        if btn == 'DEL' and len(dpress) > 0:
            del dpress[-1]
            del star[-1]
        elif btn == 'Clear':
            del dpress[:]
            del star[:]
        elif btn == 'Cancel':
            del dpress[:]
            bit =0
            popup.quit()
            popup.destroy()

        elif len(dpress) < 4 and btn != 'Del' and btn != 'Clear':
            dpress.append('%s' %btn)
            star.append('*')

        keytext = ''.join(dpress)

        string = ''.join(star)
        ps.config(text = string)
        if keytext == mng_pass:
            del dpress[:]
            bit =1
            popup.quit()
            popup.destroy()
        if keytext == rt_pass:
            del dpress[:]
            bit =2
            popup.quit()
            popup.destroy()
        elif len(keytext) == 4:
            ps.config(text = "wrong text")

    keypadframe = tk.LabelFrame(popup, text = "", font = SMALL_FONT)
    keypadframe.pack()

    #print(dpress)
    #typical keypad
    btn_list = [
            '7',  '8',  '9',
            '4',  '5',  '6',
            '1',  '2',  '3',
            'Clear',  '0',  'Del',
            'Cancel']
    # create and position all buttons with a for-loop
    # r, c used for row, column grid values
    r = 1
    c = 0
    n = 0
    # list(range()) needed for Python3
    btn = list(range(len(btn_list)))
    for label in btn_list:
        # partial takes care of function and argument
        # create the button
        cmd = partial(click,label)
        btn[n] = tk.Button( keypadframe, text=label,font = SMALL_FONT , justify = LEFT,
                           fg='white' ,bg='blue',command = cmd, width=6, height=4)
        # position the button
        btn[n].grid(row=r, column=c , padx =4 ,pady =4)
        # increment button index
        n += 1
        # update row/column position
        c += 1
        if c == 3:
            c = 0
            r += 1

    popup.mainloop()

        

class DispenserGui(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "DispenserGUI")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        if os.path.isfile(filepath +datetime.datetime.now().strftime("%d-%B-%Y")+".csv") == False:
            with open(filepath+datetime.datetime.now().strftime("%d-%B-%Y")+".csv" , "w", newline = "") as fp:
                a = csv.writer(fp, delimiter = ",")
                data = [["TIME","AMOUNT","RATE","TEMP","UNIT","GAS"]]
                a.writerows(data)
        self.shared_data = {
            'Rate': tk.StringVar(),
            'Temp': tk.StringVar()}
        self.shared_data['Rate'].set(str(rate))
        temp = temp_set()
        self.shared_data['Temp'].set(str(temp))

        self.frames = {}
        for F in (StartPage, RatePage, FillingPage, ManagerPage):
            
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        global bit
        frame=self.frames[cont]
        if str(cont) == "<class '__main__.ManagerPage'>":
            popup_msg()
            print(bit)
            if bit == 1:
                bit =0
                print(bit)
                frame.tkraise()
            else:
                return
        elif str(cont) == "<class '__main__.RatePage'>":
            popup_msg()
            print(bit)
            if bit == 2:
                bit =0
                print(bit)
                frame.tkraise()
            else:
                return

           
        elif str(cont) == "<class '__main__.FillingPage'>":
            
            keytext = ''.join(dpress)
            if keytext != '':
                frame.tkraise()
                frame.event_generate("<<Filling>>")

        elif str(cont) == "<class '__main__.StartPage'>":
                frame.tkraise()
                frame.event_generate("<<Start>>")
        else:    
            frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.v = StringVar()
        global rate
        #keypad entry frame

        kpad_frame = tk.LabelFrame( self, text = "" ,bd=11 , bg = "grey",
                               width=6, height=3)
        kpad_frame.place(x=420, y=20)

        kpad_unit = tk.Label( kpad_frame, text = "Rs", font = MEDIUM_FONT,
                                  bg = "red", fg = "white" , width = 6, height=3)
        kpad_unit.grid(row=0, column=0)
                                  
        a = Entry(kpad_frame ,font= xxLARGE_FONT, textvariable= self.v , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=4)
        a.insert(0, '0')
        a.grid(row = 0, column =1)

        #keypad position
        kp = tk.LabelFrame(self, text="",fg='Yellow', bd=11 , bg= 'peachpuff')
        kp.place(x=690,y=260)
        #click function of keypad
        def click(btn):
            if btn == 'Del' and len(dpress) > 0 :
                del dpress[-1]
            elif btn == 'Clear':
                del dpress[:]
                self.v.set('0')
            elif len(dpress) < 4 and btn != 'Del' and btn != 'Clear':
                dpress.append('%s' %btn)
            keytext = ''.join(dpress)
            if keytext == '0':
                del dpress[:]
                self.v.set("0")
            else:
                self.v.set(keytext)
        #print(dpress)
        #typical keypad
        btn_list = [
            '7',  '8',  '9',
            '4',  '5',  '6',
            '1',  '2',  '3',
            'Clear',  '0',  'Del']
        # create and position all buttons with a for-loop
        # r, c used for row, column grid values
        r = 1
        c = 0
        n = 0
        # list(range()) needed for Python3
        btn = list(range(len(btn_list)))
        for label in btn_list:
            # partial takes care of function and argument
            # create the button
            cmd = partial(click,label)
            btn[n] = tk.Button(kp, text=label,font = SMALL_FONT , justify = LEFT,
                               fg='white' ,bg='blue',command = cmd, width=6, height=4)
            # position the button
            btn[n].grid(row=r, column=c , padx =4 ,pady =4)
            # increment button index
            n += 1
            # update row/column position
            c += 1
            if c == 3:
                c = 0
                r += 1
                

        #preset buttons

        kp2 = tk.LabelFrame(self, text="",fg='Yellow', bd=11 , bg= 'peachpuff')
        kp2.place(x=420,y=260)
        def click2(prst):
            del dpress [:]
            if prst == 'Full':
                for n in range(4):
                    dpress.append('9')
            elif prst == '50':
                dpress.append('5')
                dpress.append('0')
            elif prst == '100':
                dpress.append('1')
                dpress.append('0')
                dpress.append('0')
            elif prst == '150':
                dpress.append('1')
                dpress.append('5')
                dpress.append('0')
            elif prst == '200':
                dpress.append('2')
                dpress.append('0')
                dpress.append('0')
##            elif prst == '400':
##                dpress.append('4')
##                dpress.append('0')
##                dpress.append('0')
            else:
                dpress.append('%s' %prst)
            keytext = ''.join(dpress)
            self.v.set(keytext)
        prst_list = [
            '50',  '100',  
            '150', '200',
            'Full']
        prst = list(range(len(prst_list)))
        r2 = 1
        c2 = 0
        n2 = 0
        for label in prst_list:
            cmd2 = partial(click2,label)
            prst[n2]=tk.Button ( kp2, text=label,command =cmd2, font =LARGE_FONT
                                 , width =3, height=1, bg = 'blue' , fg='white')
            prst[n2].grid(row = r2, column =c2 , padx =8, pady=8)
            n2 += 1
            c2 += 1
            if c2 == 2:
                c2 = 0
                r2 +=1
        #clear rs

        def clear_v():
            self.v.set('0')
            
        #startfilling button
        fill_btn = tk.Button(self, text= "Start Filling" , font = MEDIUM_FONT,
                             fg = "white", bg= "green", width =14 , height =3,
                             command= lambda : [controller.show_frame(FillingPage), clear_v()])
        fill_btn.place(x = 690, y=590)

        #Manager button
        fill_btn = tk.Button(self, text= "Manage" , font = MEDIUM_FONT,
                             fg = "white", bg= "green", width =14 , height =3,
                             command= lambda : [controller.show_frame(ManagerPage), clear_v()])
        fill_btn.place(x = 20 , y=590)


        #rate area
        ra_frame = tk.LabelFrame(self, text = "" , fg='Yellow', bd =11 , bg = 'grey')
        ra_frame.place( x = 20, y =20)

        ra = tk.Button( ra_frame, text = 'Rate' , font = MEDIUM_FONT , width= 6
                        , height =2, bg = 'red', fg = 'white', command = lambda: [controller.show_frame(RatePage),clear_v()])
        ra.grid( row=0, column=0, padx=8)
##        r = StringVar()
##        r.set(str(rate))

        ra_value = Entry(ra_frame , font = LARGE_FONT, textvariable = controller.shared_data['Rate'] ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=6)
        ra_value.grid(row= 0, column=1)

        self.ra_unit= tk.Label ( ra_frame, text= "Rs" + unit, font= MEDIUM_FONT ,
                            bg = "grey", fg = "white" , width=6, height =3)
        self.ra_unit.grid(row=0, column=2)
        #temp_area

        temp_frame = tk.LabelFrame(self, text = "" , fg='Yellow',
                                   bd =11 , bg = 'grey')
        temp_frame.place(x=20 , y=125)

##        temp_label1 = tk.Label(temp_frame, text ="TEMP", , fg ="white", bg = "red",
##                                   height = 3 , width =6 )
##        temp_label1.grid(row=0, column =0 , padx =10)

        temp_label = tk.Label(temp_frame, text = "Temp", font = MEDIUM_FONT,
                              bg = "red", fg = "white" , width=6, height =2)
        temp_label.grid(row=0,column=0, padx =12)

        self.t=StringVar()
        #extracting data from modbusregisters
        temp_set()
        
        self.t.set(temp)
        
        temp_value = Entry(temp_frame , font = LARGE_FONT, textvariable = self.t ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=6)
        temp_value.grid(row=0, column=1)

        temp_unit= tk.Label ( temp_frame, text= "°C", font= MEDIUM_FONT ,
                            bg = "grey", fg = "white", width=6, height =3)
        temp_unit.grid(row=0, column=2)
        
        self.bind("<<Start>>", self.on_show_frame)

    def on_show_frame(self,event):
        print("working")
        self.v.set('0')
        temp_set()
        self.t.set(temp)
        self.ra_unit["text"] = "Rs%s"%unit 
        
        


 
        

        
        
        
        

class RatePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        global unit
        label = tk.Label(self, text="Set Rate here", font= LARGE_FONT)
        label.place(x=700, y=20)

        button1 = tk.Button( self, text="back to home" , font= LARGE_FONT,
                             command= lambda: controller.show_frame(StartPage))
        button1.place(x=700, y=600)

##        v = StringVar()
        #keypad
        #keypad entry frame

        self.kpad_frame = tk.LabelFrame( self, text = "" ,bd=11 , bg = "grey",
                               width=6, height=3)
        self.kpad_frame.place(x=20, y=20)

        kpad_unit = tk.Label( self.kpad_frame, text = "Rs", font = MEDIUM_FONT,
                                  bg = "red", fg = "white" , width = 6, height=3)
        kpad_unit.grid(row=0, column=0)

        self.kpad_unit1 = tk.Label( self.kpad_frame, text = unit, font = MEDIUM_FONT,
                                  bg = "red", fg = "white" , width = 6, height=3)
        self.kpad_unit1.grid(row=0, column=2)
                                  
        a = Entry(self.kpad_frame ,font= xLARGE_FONT, textvariable= controller.shared_data['Rate'] , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=5)
        a.grid(row = 0, column =1)

        def unit_kg():
            global unit
            unit = "/KG"
            self.kpad_unit1.configure(text = unit)
##            print("unit changed to kg")
            
        def unit_ltr():
            global unit
            unit = "/LTR"
            self.kpad_unit1.configure(text = unit)
##            print("unit changed to ltr")

        dp_unit = tk.Button(self, text = "KG", font = MEDIUM_FONT, width =3, height =1 , fg = "black",
                            command = lambda : unit_kg())
        dp_unit.place(x= 700, y =20)

        dp_unit1 = tk.Button(self, text = "LTR", font = MEDIUM_FONT, width =3, height =1 , fg = "black",
                            command = lambda : unit_ltr())
        dp_unit1.place(x= 700, y =100)


        

            

        #keypad position
        kp = tk.LabelFrame(self, text="",fg='Yellow', bd=11 , bg= 'peachpuff')
        kp.place(x=20,y=260)
        #click function of keypad
        def click(btn):
            global rate
            if btn == 'Del' and len(dpress) > 0 :
                del dpress[-1]
            elif btn == 'Clear':
                del dpress[:]
            elif len(dpress) < 5 and btn != 'Del' and btn != 'Clear':
                dpress.append('%s' %btn)
            keytext = ''.join(dpress)
            if keytext == '0':
                del dpress[:]
            else:
                controller.shared_data['Rate'].set(keytext)
                rate = float(controller.shared_data['Rate'].get())
        #print(dpress)
        #typical keypad
        btn_list = [
            '7',  '8',  '9',
            '4',  '5',  '6',
            '1',  '2',  '3',
            '.',  '0',  'Del']
        # create and position all buttons with a for-loop
        # r, c used for row, column grid values
        r = 1
        c = 0
        n = 0
        # list(range()) needed for Python3
        btn = list(range(len(btn_list)))
        for label in btn_list:
            # partial takes care of function and argument
            # create the button
            cmd = partial(click,label)
            btn[n] = tk.Button(kp, text=label,font = SMALL_FONT , justify = LEFT,
                               fg='white' ,bg='blue',command = cmd, width=6, height=4)
            # position the button
            btn[n].grid(row=r, column=c , padx =4 ,pady =4)
            # increment button index
            n += 1
            # update row/column position
            c += 1
            if c == 3:
                c = 0
                r += 1

class FillingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        #RS display area
        fill_frame = tk.LabelFrame(self, text = "" , fg='Yellow', bd =11, bg ="grey" )
        fill_frame.place( x=450, y=20)
        
        self.fill_var = StringVar()

        fill_entry = Entry(fill_frame ,font= xLARGE_FONT, textvariable= self.fill_var , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=6)
        fill_entry.grid(row = 0, column =0)

        fill_unit = tk.Label(fill_frame , text = "RS.", font = MEDIUM_FONT, bg = "grey", fg = "white",
                             width =6)
        fill_unit.grid(row =1 , column =0)

        #Gas Unit display area

        self.gas_frame = tk.LabelFrame( self, text = "", bd =11, bg= "grey")
        self.gas_frame.place( x = 20, y =20)

        self.gas_var = StringVar()

        gas_entry = Entry(self.gas_frame ,font= xLARGE_FONT, textvariable= self.gas_var , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=5)
        gas_entry.grid(row=0, column=0)

        self.gas_unit = tk.Label(self.gas_frame , font = MEDIUM_FONT, text =unit,
                            bg = "grey", fg = "white")
        self.gas_unit.grid(row=1, column=0)

        #Status bar

        status_frame = tk.LabelFrame( self, text = "", bd = 11,
                                       bg ="tan1")
        status_frame.place(x=450 , y =260)
        
        self.status = StringVar()

        status_entry = Entry( status_frame, textvariable= self.status , font = LARGE_FONT,
                              fg = "red", bg = "tan1", width = 20)
        status_entry.grid(row =0 , column=0)

        #GAS Status

        gState_frame = tk.LabelFrame( self, text = "Gas Status" ,font = MEDIUM_FONT, bd = 5)
        gState_frame.place(x=630, y=350)

        gState_pr = tk.Label( gState_frame , text = "PRESSURE" , font = MEDIUM_FONT, fg = "black" )
        gState_pr.grid(row =1, column =0 , stick= "w")

        
        pressure= StringVar()
        gState_prentry = Entry (gState_frame, textvariable = pressure, font= LARGE_FONT,
                                bg="black", fg="maroon1", width =10 , justify = "right")
        gState_prentry.grid(row=2 ,column=0)

        gState_pr = tk.Label( gState_frame , text = "bar" , font = MEDIUM_FONT, fg = "black" )
        gState_pr.grid(row =2, column = 1)
        

##        gState_temp = tk.Label( gState_frame, text = "TEMPRATURE", font = MEDIUM_FONT , fg = "black")
##        gState_temp.grid(row =3 ,column=0 , sticky = "w")
##
##        temp= StringVar()
##        gState_prentry = Entry (gState_frame, textvariable = temp, font= LARGE_FONT,
##                                bg="black", fg="maroon1", width =10 , justify = "right")
##        gState_prentry.grid(row=4 ,column=0)

        #Tank Canvas

        fill_canvas = tk.LabelFrame( self, text = "TANK" ,font = MEDIUM_FONT, bd = 5)
        fill_canvas.place(x =450 ,y=350)

        self.canvas = Canvas(fill_canvas , width=150, height =300)

        self.canvas.create_rectangle(15,25,135,275, outline = "lawn green", width =2)
        temp_set()
        temp_entry = Entry(self.canvas, textvariable = controller.shared_data['Temp'] , font = MEDIUM_FONT,width = 3)
        temp_entry.pack()
        self.canvas.create_window( 75, 150, window = temp_entry)
##        canvas.create_text(75,150,font = MEDIUM_FONT, text=temp)333333
        self.canvas.create_arc ( 15,5,135,45, start=0, extent=180 , outline = "lawn green", width =2)
        self.canvas.create_arc ( 15,290,135,260, start=0, extent=-180 , outline = "lawn green", width =2, fill = "lawn green")

        img = Image.open('1.png')
        self.canvas.image = ImageTk.PhotoImage(img)
        self.canvas.create_image(52, 30, image=self.canvas.image, anchor='nw')
        


        
        self.canvas.pack(fill=BOTH, expand=1)

        #rate rs area
        #Rate
        ra_frame = tk.LabelFrame(self, text = "" , fg='Yellow', bd =11 )
        ra_frame.place( x = 630, y =500)

        ra = tk.Label( ra_frame, text = 'Rate' , font = SMALL_FONT , width= 6
                    , height =3,  fg = 'blue')
        ra.grid( row=0, column=0 , padx =1, pady=1)

##        r = StringVar()
##        r.set(rate)

        ra_value = Entry(ra_frame , font = MEDIUM_FONT, textvariable = controller.shared_data['Rate'] ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=5)
        ra_value.grid(row= 0, column=1, padx =1, pady=1)

        ra_unit= tk.Label ( ra_frame, text= "Rs/Kg", font= SMALL_FONT ,
                            bg = "grey", fg = "white" , width=6, height =3)
        ra_unit.grid(row=0, column=2, padx =1, pady=1)

        #RS
        
        rs = tk.Label( ra_frame, text = 'RS' , font = SMALL_FONT , width= 6
                    , height =3, fg = 'blue')
        rs.grid( row=1, column=0 )

        self.r = StringVar()

        rs_value = Entry(ra_frame , font = MEDIUM_FONT, textvariable = self.r ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=5)
        rs_value.grid(row= 1, column=1, padx =1, pady=1)

        #Light Canvas

        light_canvas = tk.LabelFrame( self, text = "" ,font = LARGE_FONT, bd = 5)
        light_canvas.place(x =20 ,y=260)

        self.canvas = Canvas(light_canvas , width=400, height =250)

        self.main_lightoff = "green4"
        self.main_lighton = "green1"

        self.canvas.create_oval(120,15,260,155 , fill = "grey" , outline = "grey")
        self.canvas.create_oval(125,20,255,150 , fill = self.main_lightoff , outline = self.main_lightoff )

        self.low_lightoff = "tan4"
        self.low_lighton = "yellow"

        self.canvas.create_oval(70,190,120,240 , fill = "grey" , outline = "grey")
        self.canvas.create_oval(73,193,117,237 , fill = self.low_lighton , outline = self.low_lighton )

        self.med_lightoff = "tan4"
        self.med_lighton = "yellow"

        self.canvas.create_oval(160,190,210,240 , fill = "grey" , outline = "grey")
        self.canvas.create_oval(163,193,207,237 , fill = self.med_lightoff , outline = self.med_lightoff )

        self.hi_lightoff = "tan4"
        self.hi_lighton = "yellow"

        self.canvas.create_oval(250,190,300,240 , fill = "grey" , outline = "grey")
        self.canvas.create_oval(253,193,297,237 , fill = self.hi_lightoff , outline = self.hi_lightoff )

        #light text canvas

        self.canvas.create_text(95,180,font = SMALL_FONT, text="LOW")

        self.canvas.create_text(185,180,font = SMALL_FONT, text="MEDIUM")

        self.canvas.create_text(275,180,font = SMALL_FONT, text="HIGH")

        self.canvas.pack(fill=BOTH, expand=1)
        
        #clear_dpress()
        def clear_dpress():
            del dpress[:]

        #stop button
        stop_button = tk.Button( self, text="STOP" , font= MEDIUM_FONT, bg ="red", fg = "white" ,
                             width = 14, height =3 ,command= lambda: [create_file(),controller.show_frame(StartPage),clear_dpress()])
        stop_button.place(x=20 , y=540)
        self.bind("<<Filling>>", self.on_show_frame)
        
    def on_show_frame(self,event):
        global rate
        global total
        global amount
        #update unit kg or ltr
        self.gas_unit.config(text = unit)
        #status
        self.status.set("LOW VAVLE OPEN")
        #VALVE
        self.canvas.create_oval(73,193,117,237 , fill = self.low_lighton , outline = self.low_lighton )
        #reset main light
        self.canvas.create_oval(125,20,255,150 , fill = self.main_lightoff , outline = self.main_lightoff )
        #reset totalizer
        reset_total()
        self.fill_var.set('0')
        flow = flow_mass()
        total =  float("{0:.3f}".format(mass_total()/1000))
        Amount = ''.join(dpress)
        amount = 0
        print("Amount :%s"%Amount)
        print("Rate %s" %rate)
        gas = float("{0:.3f}".format(float(Amount)/rate))
        print("GAS : %s" %gas)
        while(total <= gas and amount <= int(Amount)):

            total = float("{0:.4f}".format(mass_total()/1000))
            amount = int(total * rate)
            self.fill_var.set(str(amount))
            self.gas_var.set(str("{0:.2f}".format(total)))
            app.update()
            
        #turning on main light
        self.canvas.create_oval(125,20,255,150 , fill = self.main_lighton , outline = self.main_lighton )
        self.canvas.create_oval(73,193,117,237 , fill = self.low_lightoff , outline = self.low_lightoff )
        #status update
        self.status.set("COMPLETE, SAFE TO DISCONNECT")
            
            
        
        
        



class ManagerPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
##        label = tk.Label(self, text="Managing Page", font= LARGE_FONT)
##        label.pack(padx=10,pady=10)

        button1 = tk.Button( self, text="EXIT" , font= LARGE_FONT, bg= "red",fg = 'white',
                             command= lambda: controller.show_frame(StartPage))
        button1.place(x=780,y=560)

        #File place
        file_label = tk.LabelFrame(self, text= "FILES" ,font =MEDIUM_FONT, bd=10)
        file_label.place(x=20,y=20)

        l= Listbox(file_label, height =5, selectmode = BROWSE , font = SMALL_FONT)
        l.grid(column=0, row=0, sticky=(N,S))
        s= ttk.Scrollbar(file_label, orient = VERTICAL, command = l.yview)
        s.grid(column =1, row =0, sticky=(N,S))
        l['yscrollcommand'] = s.set

        for filename in get_filename():
            l.insert(END, filename)


        Totalizer_frame = tk.LabelFrame(self, text = "totalizer")
        Totalizer_frame.place(x=780 , y=10)

        amount_label = tk.Label(Totalizer_frame, text = "Total Amount", font = MEDIUM_FONT, relief = tk.RIDGE)
        amount_label.grid(row=0, column = 0, sticky = (N,E,S,W))

        gaskg_label = tk.Label(Totalizer_frame, text = "Total Gas(KG)", font = MEDIUM_FONT, relief = tk.RIDGE)
        gaskg_label.grid(row=1, column = 0, sticky = (N,E,S,W))

        self.amount = tk.Label(Totalizer_frame, text = "0", font = MEDIUM_FONT, relief = tk.RIDGE)
        self.amount.grid(row=0, column = 1, sticky = (N,E,S,W))

        self.gaskg = tk.Label(Totalizer_frame, text = "0", font = MEDIUM_FONT, relief = tk.RIDGE)
        self.gaskg.grid(row=1, column = 1, sticky = (N,E,S,W))


        canvas_frame =tk.LabelFrame(self)
        canvas_frame.place(x=260, y =18)

        canvas_reader = tk.Canvas(canvas_frame, width=500, height=600, scrollregion = (0,0,500,10000))

        scrollb=tk.Scrollbar(canvas_frame, orient = "vertical", command=canvas_reader.yview)
        scrollb.pack(side = "right", fill = "y")

        canvas_reader['yscrollcommand'] = scrollb.set
        canvas_reader.pack(side = 'right', fill = 'y')

        hide = tk.LabelFrame(canvas_reader, width =500, height=600)
        hide.place(x=0,y=0)
        
        def callback():
            items = l.curselection()
            item_name = l.get(items)
            hide.tkraise()
            freader_label = tk.LabelFrame(canvas_reader, text = "", font = MEDIUM_FONT, bd =10, fg= 'red')
            freader_label.place(x=0, y=0)

            def onFrameConfigure(self):
                canvas_reader.configure(scrollregion = canvas_reader.bbox('all'))

            canvas_reader.create_window((4,4) ,window=freader_label, anchor = "nw",
                                    tags = "freader_label")
            freader_label.bind("<Configure>", onFrameConfigure)

            #adding amount column
            df=pd.read_csv(filepath + item_name)
            total_amount = df['AMOUNT'].sum()
            total_gas = df['GAS'].sum()

            self.amount.config(text = total_amount)
            self.gaskg.config(text = "{0:.1f}".format(total_gas))

            
            with open(filepath +item_name, newline = '') as file:
                reader = csv.reader(file)

                r=0
                for col in reader:
                        c=0
                        for row in col:

                            label = tk.Label(freader_label, width =10, height =2,
                                             text= row, relief = tk.RIDGE)
                            label.grid(row=r, column=c)
                            c +=1
                        r+=1

        button = tk.Button(file_label, text= "show", command = callback)
        button.grid(row=0, column=2)
                

app = DispenserGui()
app.wm_geometry("1024x768+0+0")
app.mainloop()
