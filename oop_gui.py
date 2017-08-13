import tkinter as tk
import datetime
import os
import os.path
import csv
import pandas as pd
from tkinter import Canvas
from tkinter import *
from tkinter import ttk
from functools import partial
from PIL import Image, ImageTk
from tabulate import tabulate
import http.client, urllib

xxLARGE_FONT = ("Verdana" , 130)
xLARGE_FONT = ("Verdana" , 100)
LARGE_FONT = ('Verdana',30)
MEDIUM_FONT = ('Verdana' , 15)
SMALL_FONT = ('Verdana',9)
dpress = []
keytext=''
temp = 0.0
rate = 55.81
unit = '/KG'
filepath = "C:\\Users\\Anum\\Desktop\\test\\"
key = "EEPNQLIC6COE2UCH"
bit = 0
#pass
mng_pass = '1234'
rt_pass = '5678'
master_key = '0000'


def get_filenames():
    path = r"C:\Users\Anum\Desktop\test"
    return os.listdir(path)

def create_file():
    keytext = ''.join(dpress)
    time = datetime.datetime.now().strftime("%d-%B-%Y")
    with open(filepath + time +".csv", "a", newline = "") as fp:
        a = csv.writer(fp, delimiter = ",")
        data=[(datetime.datetime.now().strftime("%H:%M"),keytext,rate,temp)]
        a.writerows(data)


        #sending data to thingsspeak API

        params = urllib.parse.urlencode({'field1': time, 'field2': keytext, 'field3': rate,'field4': temp, 'key':key }) 
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = http.client.HTTPConnection("api.thingspeak.com",port=80)
        try:
            conn.request("POST", "/update", params, headers)
            response = conn.getresponse()
            res = response.read()
            conn.close()
        except:
            print ("connection failed")
                
def popup_msg():
        popup = tk.Tk()

        popup.wm_title("Authentication")
        popup.wm_geometry("400x600+120+0")


        #msg
        labelframe = tk.LabelFrame(popup , text = "", font = SMALL_FONT)
        labelframe.pack()
        label = tk.Label(labelframe , text = "Enter Pin", font = MEDIUM_FONT)
        label.grid(row = 0, column =0)
        #display
        s = ""
        ps = tk.Label(labelframe , text = s , font = MEDIUM_FONT , relief = tk.RIDGE)
        ps.grid(row = 1, column =0)
             
        #keypad
        keypadframe = tk.LabelFrame(popup , text = "", font = SMALL_FONT)
        keypadframe.pack()
        star = []
        def click(btn):
            global bit
            if btn == 'Del' and len(dpress) > 0 :
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
                ps.config(text = 'wrong pass')

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
            btn[n] = tk.Button(keypadframe, text=label,font = SMALL_FONT , justify = LEFT,
                               fg='white' ,bg='blue',command = cmd, width=7, height=4)
            # position the button
            btn[n].grid(row=r, column=c , padx =5 ,pady =5)
            # increment button index
            n += 1
            # update row/column position
            c += 1
            if c == 3:
                c = 0
                r += 1
##        #back button
##        back = tk.Button(popup , text = "Cancel", font= MEDIUM_FONT, fg = 'white', bg = 'red' , width = 6, height =2, cmd =  )
##        back.pack()

        
        popup.mainloop()






class DispenserGui(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "DispenserGUI")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        if os.path.isfile(filepath + datetime.datetime.now().strftime("%d-%B-%Y")+".csv" ) == False:

            with open("C:\\Users\\Anum\\Desktop\\test\\" +datetime.datetime.now().strftime("%d-%B-%Y")+".csv", "w", newline = "") as fp:
                a = csv.writer(fp, delimiter = ",")
                data=[["TIME","Amount","RATE","temp"]]
                a.writerows(data)
            

        self.frames = {}
        for F in (StartPage, RatePage, FillingPage, ManagerPage):
            
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
            global bit
            frame = self.frames[cont]
            print(rate)
            if str(cont) == "<class '__main__.ManagerPage'>":
                popup_msg()
                print(bit)
                if bit == 1:
                    bit = 0
                    print(bit)
                    frame.tkraise()
                else:
                    return
            if str(cont) == "<class '__main__.RatePage'>":
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
            
            else:
                frame.tkraise()


class StartPage(tk.Frame):

    

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        global rate
        self.v = StringVar()
        #keypad entry frame

        self.kpad_frame = tk.LabelFrame( self, text = "" ,bd=11 , bg = "grey",
                               width=6, height=3)
        self.kpad_frame.place(x=420, y=20)

        self.kpad_unit = tk.Label( self.kpad_frame, text = "Rs", font = MEDIUM_FONT,
                                  bg = "red", fg = "white" , width = 6, height=3)
        self.kpad_unit.grid(row=0, column=0)
                                  
        self.a = Entry(self.kpad_frame ,font= xxLARGE_FONT, textvariable= self.v , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=4)
        self.a.grid(row = 0, column =1)

        #keypad position
        self.kp = tk.LabelFrame(self, text="",fg='Yellow', bd=11 , bg= 'peachpuff')
        self.kp.place(x=720,y=260)

        #key function
        def click(btn):
            if btn == 'Del' and len(dpress) > 0 :
                del dpress[-1]
            elif btn == 'Clear':
                del dpress[:]
            elif len(dpress) < 4 and btn != 'Del' and btn != 'Clear':
                dpress.append('%s' %btn)
            keytext = ''.join(dpress)
            if keytext == '0':
                del dpress[:]
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
            btn[n] = tk.Button(self.kp, text=label,font = SMALL_FONT , justify = LEFT,
                               fg='white' ,bg='blue',command = cmd, width=7, height=4)
            # position the button
            btn[n].grid(row=r, column=c , padx =5 ,pady =5)
            # increment button index
            n += 1
            # update row/column position
            c += 1
            if c == 3:
                c = 0
                r += 1

##        #click function of keypad
##        v.set(keytext = ''.join(dpress))

        #preset buttons

        self.kp2 = tk.LabelFrame(self, text="",fg='Yellow', bd=11 , bg= 'peachpuff')
        self.kp2.place(x=420,y=260)
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
            elif prst == '250':
                dpress.append('2')
                dpress.append('5')
                dpress.append('0')
##            elif prst == '400':
##                dpress.append('4')
##                dpress.append('0')
##                dpress.append('0')
            else:
                dpress.append('%s' %prst)
            keytext = ''.join(dpress)
            v.set(keytext)
        prst_list = [
            '50',  '100',  
            '150', '250',
            'Full']
        prst = list(range(len(prst_list)))
        r2 = 1
        c2 = 0
        n2 = 0
        for label in prst_list:
            cmd2 = partial(click2,label)
            prst[n2]=tk.Button ( self.kp2, text=label,command =cmd2, font =LARGE_FONT
                                 , width =4, height=1, bg = 'blue' , fg='white')
            prst[n2].grid(row = r2, column =c2 , padx =10, pady=10)
            n2 += 1
            c2 += 1
            if c2 == 2:
                c2 = 0
                r2 +=1

        #clear_V
        def clear_v():
            self.v.set('')
        #startfilling button
        self.fill_btn = tk.Button(self, text= "Start Filling" , font = MEDIUM_FONT,
                             fg = "white", bg= "green", width =14 , height =3,
                             command= lambda : [controller.show_frame(FillingPage), clear_v()])
        self.fill_btn.place(x = 720, y=590)

        #Manager button
        self.mng_btn = tk.Button(self, text= "Manage" , font = MEDIUM_FONT,
                             fg = "white", bg= "green", width =14 , height =3,
                             command= lambda : controller.show_frame(ManagerPage))
        self.mng_btn.place(x = 20 , y=590)
        

        #Rate Area
        self.ra_frame = tk.LabelFrame(self, text = "" , fg='Yellow', bd =11 , bg = 'grey')
        self.ra_frame.place( x = 20, y =20)

        self.ra = tk.Button( self.ra_frame, text = 'Rate' , font = MEDIUM_FONT , width= 6
                        , height =2, bg = 'red', fg = 'white', command = lambda: controller.show_frame(RatePage))
        self.ra.grid( row=0, column=0, padx=10)

        self.r = StringVar()
        self.r.set(str(rate))

        self.ra_value = Entry(self.ra_frame , font = LARGE_FONT, textvariable = self.r ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=6)
        self.ra_value.grid(row= 0, column=1)

        self.ra_unit= tk.Label (self.ra_frame, text= "Rs/Kg", font= MEDIUM_FONT ,
                            bg = "grey", fg = "white" , width=6, height =3)
        self.ra_unit.grid(row=0, column=2)


        #temp_area

        self.temp_frame = tk.LabelFrame(self, text = "" , fg='Yellow',
                                   bd =11 , bg = 'grey')
        self.temp_frame.place(x=20 , y=125)

        ##        temp_label1 = tk.Label(temp_frame, text ="TEMP", , fg ="white", bg = "red",
        ##                                   height = 3 , width =6 )
        ##        temp_label1.grid(row=0, column =0 , padx =10)

        self.temp_label = tk.Label(self.temp_frame, text = "Temp", font = MEDIUM_FONT,
                              bg = "red", fg = "white" , width=6, height =2)
        self.temp_label.grid(row=0,column=0, padx =12)

        self.t=StringVar()
        self.t.set(temp)

        self.temp_value = Entry(self.temp_frame , font = LARGE_FONT, textvariable = self.t ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=6)
        self.temp_value.grid(row=0, column=1)

        self.temp_unit= tk.Label ( self.temp_frame, text= "°C", font= MEDIUM_FONT ,
                            bg = "grey", fg = "white", width=6, height =3)
        self.temp_unit.grid(row=0, column=2)



    
        
        

class RatePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        global unit
        label = tk.Label(self, text="Set Rate here", font= LARGE_FONT)
        label.place(x=700, y=20)

        button1 = tk.Button( self, text="back to home" , font= LARGE_FONT,
                             command= lambda: controller.show_frame(StartPage))
        button1.place(x=700, y=600)

        v = StringVar()
        #keypad entry frame

        kpad_frame = tk.LabelFrame( self, text = "" ,bd=11 , bg = "grey",
                               width=6, height=3)
        kpad_frame.place(x=20, y=20)

        kpad_unit = tk.Label( kpad_frame, text = "Rs", font = MEDIUM_FONT,
                                  bg = "red", fg = "white" , width = 6, height=3)
        kpad_unit.grid(row=0, column=0)
                                  
        a = Entry(kpad_frame ,font= xLARGE_FONT, textvariable= v , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=5)
        a.grid(row = 0, column =1)

        def unit_kg():
            global unit
            unit = "/KG"

        def unit_ltr():
            global unit
            unit = "/LTR"

        dp_unit = tk.Button(self, text = "KG", font = MEDIUM_FONT , width =3, height =1 ,fg = "black",
                         command = lambda: unit_kg)
        dp_unit.place(x = 700 , y = 20)

        dp_unit1 = tk.Button(self, text = "LTR", font = MEDIUM_FONT , width =3, height =1 ,fg = "black",
                          command = lambda: unit_ltr )
        dp_unit1.place(x = 700 , y = 100)

        kpad_unit1 = tk.Label( kpad_frame, text = unit, font = MEDIUM_FONT,
                                  bg = "red", fg = "white" , width = 6, height=3)
        kpad_unit1.grid(row=0, column=2)

        

        

                

        #keypad position
        kp = tk.LabelFrame(self, text="",fg='Yellow', bd=11 , bg= 'peachpuff')
        kp.place(x=20,y=260)

        #key function
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
                v.set(keytext)
            rate = float(keytext)
            

        #print(dpress)
        #typical keypad
        btn_list = [
            '7',  '8',  '9',
            '4',  '5',  '6',
            '1',  '2',  '3',
            'Clear',  '0',  '.']
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
                               fg='white' ,bg='blue',command = cmd, width=7, height=4)
            # position the button
            btn[n].grid(row=r, column=c , padx =5 ,pady =5)
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
        #RS display area
        fill_frame = tk.LabelFrame(self, text = "" , fg='Yellow', bd =11, bg ="grey" )
        fill_frame.place( x=450, y=20)
        
        fill_var = StringVar()

        fill_entry = Entry(fill_frame ,font= xLARGE_FONT, textvariable= fill_var , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=6)
        fill_entry.grid(row = 0, column =0)

        fill_unit = tk.Label(fill_frame , text = "RS.", font = MEDIUM_FONT, bg = "grey", fg = "white",
                             width =6)
        fill_unit.grid(row =1 , column =0)

        #Gas Unit display area

        gas_frame = tk.LabelFrame( self, text = "", bd =11, bg= "grey")
        gas_frame.place( x = 20, y =20)

        gas_var = StringVar()

        gas_entry = Entry(gas_frame ,font= xLARGE_FONT, textvariable= fill_var , justify= RIGHT
                  , bg= 'black', fg= 'blue' , width=5)
        gas_entry.grid(row=0, column=0)

        gas_unit = tk.Label(gas_frame , font = MEDIUM_FONT, text ="KG",
                            bg = "grey", fg = "white")
        gas_unit.grid(row=1, column=0)

        #Status bar

        status_frame = tk.LabelFrame( self, text = "", bd = 11,
                                       bg ="tan1")
        status_frame.place(x=450 , y =260)
        
        status = StringVar()

        status_entry = Entry( status_frame, textvariable= status , font = LARGE_FONT,
                              fg = "lawn green", bg = "tan1", width = 20)
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

        canvas = Canvas(fill_canvas , width=150, height =300)

        canvas.create_rectangle(15,25,135,275, outline = "lawn green", width =2)


        canvas.create_text(75,150,font = MEDIUM_FONT, text=str(temp))
        canvas.create_arc ( 15,5,135,45, start=0, extent=180 , outline = "lawn green", width =2)
        canvas.create_arc ( 15,290,135,260, start=0, extent=-180 , outline = "lawn green", width =2, fill = "lawn green")

        img = Image.open('1.png')
        canvas.image = ImageTk.PhotoImage(img)
        canvas.create_image(52, 30, image=canvas.image, anchor='nw')
        


        
        canvas.pack(fill=BOTH, expand=1)

        #rate rs area
        #Rate
        ra_frame = tk.LabelFrame(self, text = "" , fg='Yellow', bd =11 )
        ra_frame.place( x = 630, y =500)

        ra = tk.Label( ra_frame, text = 'Rate' , font = SMALL_FONT , width= 6
                    , height =3,  fg = 'blue')
        ra.grid( row=0, column=0 , padx =1, pady=1)

        r = StringVar()
        r.set(rate)

        ra_value = Entry(ra_frame , font = MEDIUM_FONT, textvariable = r ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=5)
        ra_value.grid(row= 0, column=1, padx =1, pady=1)

        ra_unit= tk.Label ( ra_frame, text= "Rs/Kg", font= SMALL_FONT ,
                            bg = "grey", fg = "white" , width=6, height =3)
        ra_unit.grid(row=0, column=2, padx =1, pady=1)

        #RS
        
        rs = tk.Label( ra_frame, text = 'RS' , font = SMALL_FONT , width= 6
                    , height =3, fg = 'blue')
        rs.grid( row=1, column=0 )

        r = StringVar()

        rs_value = Entry(ra_frame , font = MEDIUM_FONT, textvariable = r ,
                         justify = RIGHT , bg = 'black',fg = 'red' , width=5)
        rs_value.grid(row= 1, column=1, padx =1, pady=1)

        #Light Canvas

        light_canvas = tk.LabelFrame( self, text = "" ,font = LARGE_FONT, bd = 5)
        light_canvas.place(x =20 ,y=260)

        canvas = Canvas(light_canvas , width=400, height =250)

        main_lightoff = "green4"
        main_lighton = "green1"

        canvas.create_oval(120,15,260,155 , fill = "grey" , outline = "grey")
        canvas.create_oval(125,20,255,150 , fill = main_lightoff , outline = main_lightoff )

        low_lightoff = "tan4"
        low_lighton = "yellow"

        canvas.create_oval(70,190,120,240 , fill = "grey" , outline = "grey")
        canvas.create_oval(73,193,117,237 , fill = low_lightoff , outline = low_lightoff )

        med_lightoff = "tan4"
        med_lighton = "yellow"

        canvas.create_oval(160,190,210,240 , fill = "grey" , outline = "grey")
        canvas.create_oval(163,193,207,237 , fill = med_lighton , outline = med_lighton )

        hi_lightoff = "tan4"
        hi_lighton = "yellow"

        canvas.create_oval(250,190,300,240 , fill = "grey" , outline = "grey")
        canvas.create_oval(253,193,297,237 , fill = hi_lightoff , outline = hi_lightoff )

        #light text canvas

        canvas.create_text(95,180,font = SMALL_FONT, text="LOW")

        canvas.create_text(185,180,font = SMALL_FONT, text="MEDIUM")

        canvas.create_text(275,180,font = SMALL_FONT, text="HIGH")

        canvas.pack(fill=BOTH, expand=1)

        #clear_dpress()
        def clear_dpress():
            del dpress[:]
        
        #stop button
        stop_button = tk.Button( self, text="STOP" , font= MEDIUM_FONT, bg ="red", fg = "white" ,
                             width = 14, height =3 ,command= lambda: [create_file(), controller.show_frame(StartPage),clear_dpress()])
        stop_button.place(x=20 , y=540)


class ManagerPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
##        label = tk.Label(self, text="Managing Page", font= LARGE_FONT)
##        label.pack(padx=10,pady=10)



        button1 = tk.Button( self, text="Go back to Main Page" , font= SMALL_FONT,
                             command= lambda: controller.show_frame(StartPage))
        button1.place( x=800, y =600)



        #file place
        hide = tk.LabelFrame(self , width =500,height= 600)
        hide.place(x=250, y =20)
        file_label = tk.LabelFrame(self, text ="FILES", font =MEDIUM_FONT, bd = 10)
        file_label.place(x=18, y= 10)
        l = Listbox(file_label, height=15 , selectmode = BROWSE, font =SMALL_FONT)
        l.grid(column=0, row=0, sticky=(N,W,E,S))
        s = ttk.Scrollbar(file_label, orient=VERTICAL, command=l.yview)
        s.grid(column=1, row=0, sticky=(N,S))
        l['yscrollcommand'] = s.set
        
        for filename in get_filenames():
            l.insert(END, filename)


        


        Totalizer_frame = tk.LabelFrame(self,text = "totalizer")
        Totalizer_frame.place(x=780,y=10)
        
        amount_label = tk.Label(Totalizer_frame, text= "Total Amount" , font = MEDIUM_FONT, relief = tk.RIDGE)
        amount_label.grid(row=0, column=0, sticky=(N,E,S,W), padx =5, pady =5)

        gaskg_label = tk.Label(Totalizer_frame, text= "Total Gas(KG)" , font = MEDIUM_FONT, relief = tk.RIDGE)
        gaskg_label.grid(row=1, column=0, sticky=(N,E,S,W), padx =5, pady =5)

        gasltr_label = tk.Label(Totalizer_frame, text= "Total Gas(ltr)" , font = MEDIUM_FONT, relief = tk.RIDGE)
        gasltr_label.grid(row=2, column=0, sticky=(N,E,S,W), padx =5, pady =5)


        amount = tk.Label(Totalizer_frame, text = '0' , font= MEDIUM_FONT, relief = tk.RIDGE )
        amount.grid(row =0 , column = 1, sticky = (N,E,S,W), padx =5, pady=5)

        gaskg = tk.Label(Totalizer_frame, text = '0' , font= MEDIUM_FONT, relief = tk.RIDGE )
        gaskg.grid(row =1 , column = 1, sticky = (N,E,S,W), padx =5, pady=5)

        gaskg = tk.Label(Totalizer_frame, text = '0' , font= MEDIUM_FONT, relief = tk.RIDGE )
        gaskg.grid(row =2 , column = 1, sticky = (N,E,S,W), padx =5, pady=5)

        canvas_frame = tk.LabelFrame (self)
        canvas_frame.place(x=260, y=18)
        canvas_reader = tk.Canvas(canvas_frame,width = 500, height = 600, scrollregion = (0,0,500,10000) )


        scrollb=Scrollbar(canvas_frame, orient="vertical",command=canvas_reader.yview)
        scrollb.pack(side= "right",fill = 'y')  #grid scrollbar in master, but

        canvas_reader['yscrollcommand'] = scrollb.set
        canvas_reader.pack(side = "left",fill = 'y')

        hide = tk.LabelFrame(canvas_reader , width =500,height= 600)
        hide.place(x=0, y =0)


        def callback():
            items =l.curselection()
            item_name = l.get(items)
            hide.tkraise()

            freader_label = tk.LabelFrame(canvas_reader, text ="", font =MEDIUM_FONT, bd = 10, fg='red')
            freader_label.place(x=0, y=0)

            def onFrameConfigure(self):
                canvas_reader.configure(scrollregion = canvas_reader.bbox("all"))

            canvas_reader.create_window((4,4), window=freader_label, anchor="nw", 
                                  tags="freader_label")
            freader_label.bind("<Configure>", onFrameConfigure)


            #adding amount column
            df = pd.read_csv( "C:\\Users\\Anum\\Desktop\\test\\"+ item_name)
            total_amount = df["Amount"].sum()

            amount = tk.Label(Totalizer_frame, text = total_amount , font= MEDIUM_FONT, relief = tk.RIDGE )
            amount.grid(row =0 , column = 1, sticky = (N,E,S,W), padx =5, pady=5)

            with open ("C:\\Users\\Anum\\Desktop\\test\\" + item_name , newline ="") as file:
                reader = csv.reader(file)


                r =0
                for col in reader:
                    c=0
                    for row in col:


                        
                        label = tk.Label(freader_label, width =10, height =2,
                                          text = row, relief = tk.RIDGE)
                        label.grid(row =r ,column=c)

                        c +=1
                    r +=1

             
        button = tk.Button(file_label, text= "show", command = lambda :  callback() )
        button.grid(row =0, column =2 , sticky=(N,E,S,W))

        
        


if __name__== "__main__":

    app = DispenserGui()
    app.wm_geometry("1024x768+0+0")
    app.mainloop()
