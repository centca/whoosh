from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox

import os
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, ID, KEYWORD
from whoosh.qparser import QueryParser
from whoosh import qparser
from docutils.nodes import Part
from _cffi_backend import string
from whoosh.query import *
from whoosh import index
from whoosh.qparser import QueryParser


def extraer_jornadas():
    f = urllib.request.urlopen("https://resultados.as.com/resultados/futbol/primera/2017_2018/calendario/")
    s = BeautifulSoup(f,"lxml")
    
    l = s.find_all("div", class_= ["cont-modulo","resultados"])
    return l

def add_doc(writer):
    try:
        f = extraer_jornadas()
       
        for i in f: 
            totalNumJ = i.find_all("h2", class_="tit-modulo")
            jornada = totalNumJ[0].find("a")
            numJ = jornada["title"]
            partido = i.find_all("tr", id = True)
            """Jornadas que quieres que te muestre"""
            
            if numJ == "Jornada 1" or "Jornada 2" or "Jornada 3":
                for p in partido:
                    
                    """Equipo : Local - Visitante"""
                    equipos = p.find_all("span", class_="nombre-equipo")
                    local = str(equipos[0].string)
                    visitante = str(equipos[1].string)
                    """Resultado"""
                    resultado = p.find_all("a", class_="resultado")
                    resFinal = str(resultado[0].string.strip())
                    
                    """Cronica"""
                    fUrl = urllib.request.urlopen("https://resultados.as.com"+resultado[0]["href"])
                    conica = BeautifulSoup(fUrl,"lxml")
                    
                    fecha = conica.find_all("span", class_="s-inb-sm")
                    fechaFinal = datetime.strptime(str(fecha[0].string),'%d/%m/%Y')
                    """fechaFinal = str(fecha[0].string)"""
                    
                    autor = conica.find_all("p", class_="ntc-autor")
                    autorFinal = str(autor[0].find_all("a")[0].string) 
                    
                    titulo = conica.find_all("h2", class_="live-title")
                    tituloFinal = str(titulo[0].find_all("a")[0].string)
                    
                    resumen = conica.find_all("div", class_="cont-cuerpo-noticia principal")
                    resumenTagDiv = resumen[0].find_all("div", class_="cf")
                    resumenFinal = str(resumenTagDiv[0].find_all("p")[0].string)
                    
                    print(numJ) 
                    print(local)
                    print(visitante)
                    print(resFinal)
                    print("-------------------Cronica---------------")
                    print(fechaFinal)
                    print(autorFinal)
                    print(tituloFinal)
                    print(resumenFinal)
                    
                    writer.add_document(numeroJornada = numJ, equipoLocal=local, equipoVisitante=visitante, resultado=resFinal
                                        , fecha=fechaFinal, autor=autorFinal, titulo= tituloFinal, resumen = resumenFinal)
            
        print ("Creado indice para fichero " )
    except:
        print ("Error: No se ha podido añadir el documento ")                       

"""Modelo"""
def get_schema():
    return Schema(equipoLocal=TEXT(stored=True), equipoVisitante=TEXT(stored=True), numeroJornada=TEXT(stored=True), fecha=DATETIME(stored=True), titulo=TEXT(stored=True), 
                  resumen=TEXT(stored=True), autor=TEXT(stored=True), resultado =TEXT(stored=True))

"""Creación del indice"""
  
def crea_index(dirindex):
    """Creación del índice"""
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    
    if not len(os.listdir(dirindex))==0:
        sn=input("Indice no vacío. Desea reindexar?(s/n)")
    else:
        sn='s' 
    if sn == 's':
            ix = create_in(dirindex, schema=get_schema())
            writer = ix.writer()
            add_doc(writer)                  
            writer.commit()
  
  
def main():
    
    """TKINTER ===> Ventana"""
    root = Tk()
    root.geometry("250x150+300+300")
    app = menu()
    root.mainloop()


class menu(Frame):
    
    index = ""
  
    def __init__(self):
        super().__init__()   
        self.initUI()
        
        
    def initUI(self):
      
        self.master.title("menu")
        
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        
        
        """Datos"""
        datos = Menu(menubar)
        menubar.add_cascade(label="Datos", menu=datos)
        datos.add_command(label="Cargar", command=self.crearDatos)
        datos.add_command(label="Salir", command=self.onExit)
        
        """Buscar"""
        
        buscar = Menu(menubar)
        menubar.add_cascade(label="Buscar", menu=buscar)
        buscar.add_command(label="Noticia", command=self.buscar_notica)
        buscar.add_command(label="Equipo", command=self.buscar_equipo)
        buscar.add_command(label="Fecha", command=self.buscar_fecha)
        
        
        
    """Cerrar Ventana Principal"""
    def onExit(self):
        
        self.quit()
        
        
    """Creación de Indice"""
    def crearDatos(self):
        
        """Ruta del directorio INDEX"""
        self.index = crea_index("/home/centca/Escritorio/ws/Examen/Index")
    
    """Buqueda Noticias"""
    """------------------"""
    def buscar_notica(self):
        
        
        """Listar las busquedas"""  
        def imprimir_noticia(event):
            v = Toplevel()
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, width=200, yscrollcommand=sc.set)
            
            """Busqueda en eñ Entry"""
            query = "%"+en.get()+"%" 
            ix=open_dir("Index")   
    
            with ix.searcher() as searcher:
                myquery = QueryParser("resumen", ix.schema).parse(query)
                results = searcher.search(myquery)
                for r in results:

                    lb.insert(END, r['fecha'])
                    lb.insert(END, r['titulo'])
                    lb.insert(END, r['autor'])
                    lb.insert(END, "---------------------------------------")
                    lb.insert(END, r['resumen'])
            

            lb.pack(side = LEFT, fill = BOTH)
            sc.config(command = lb.yview)

        """Ventana Entry"""
        v = Toplevel()
        lb = Label(v, text="Consulta en el resumen del partido ")
        lb.pack(side = LEFT)
        en = Entry(v)
        en.bind("<Return>", imprimir_noticia)
        en.pack(side = LEFT)
    
    
    
    
    
    """Buqueda Equipo"""
    """------------------"""
    def buscar_equipo(self):
        
        
        """Listar las busquedas"""  
        def imprimir_equipo(event):
            v = Toplevel()
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, width=200, yscrollcommand=sc.set)
            
            """Busqueda en eñ Entry"""
            query = "%"+en.get()+"%" 
            ix=open_dir("Index")   
    
            with ix.searcher() as searcher:
                myquery = QueryParser("equipoLocal", ix.schema).parse(query)
                results = searcher.search(myquery)
                for r in results:
                    lb.insert(END, r['numeroJornada'])
                    lb.insert(END, r['equipoLocal'])
                    lb.insert(END, r['equipoVisitante'])
                    lb.insert(END, r['resultado'])
                    lb.insert(END, "---------------------------------------")
                    
            

            lb.pack(side = LEFT, fill = BOTH)
            sc.config(command = lb.yview)

        """Ventana Entry"""
        v = Toplevel()
        lb = Label(v, text="Equipo:")
        lb.pack(side = LEFT)
        en = Entry(v)
        en.bind("<Return>", imprimir_equipo)
        en.pack(side = LEFT)
        
        
    """Buqueda Fecha"""
    """------------------"""
    def buscar_fecha(self):
        """20170820"""
        
        """Listar las busquedas"""  
        def imprimir_fecha(event):
            v = Toplevel()
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, width=200, yscrollcommand=sc.set)
            
            """Busqueda en eñ Entry"""
           
            ix=open_dir("Index")

            with ix.searcher() as searcher:
                """Busqueda mediante rango"""
                
                p = QueryParser("resumen", schema=ix.schema).parse(u"fecha:["+en.get()+ "to" +en1.get()+"]")

                
                results = searcher.search( p , limit=None)
                
                for r in results:
                    
                    lb.insert(END, r['fecha'])
                    lb.insert(END, r['titulo'])
                    lb.insert(END, r['autor'])
                    lb.insert(END, r['resumen'])
                    lb.insert(END, "---------------------------------------")
                    
            

            lb.pack(side = LEFT, fill = BOTH)
            sc.config(command = lb.yview)

        """Ventana Entry"""
        v = Toplevel()
        lb = Label(v, text="Fecha desde (YYYYMMDD):")
        lb.pack(side = LEFT)
        en = Entry(v)
        en.bind("<Return>", imprimir_fecha)
        en.pack(side = LEFT)
        lb1 = Label(v, text="a:")
        lb1.pack(side = LEFT)
        en1 = Entry(v)
        en1.bind("<Return>", imprimir_fecha)
        en1.pack(side = LEFT)
        
    
    

if __name__ == '__main__':
    main()
    
  
  
    
    

