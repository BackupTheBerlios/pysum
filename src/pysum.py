#! /usr/bin/env python
# -*- coding: UTF-8 -*-

# pysum - A pygtk app to create and check md5 and other checksum
# Copyright (C) 2008-2010 Daniel Fuentes Barría <dbfuentes@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


####### START EDIT HERE ###########

# Directory with the files (*.glade, icons, etc.)
resources_dir = "/usr/share/pysum"
img_dir = "/usr/share/pysum"

####### STOP EDIT HERE ############


# Informacion del programa que se modifica con cierta frecuencia
# (para no escribir tanto)

__version__ = "rev19"

authors = "Daniel Fuentes Barría <dbfuentes@gmail.com>"
website = "http://pysum.berlios.de/"
license = "This program is free software; you can redistribute \
it and/or modify it under the terms of the GNU General Public License as \
published by the Free Software Foundation; either version 2 of the \
License, or (at your option) any later version. \n\nThis program is \
distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; \
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A \
PARTICULAR PURPOSE. \
See the GNU General Public License for more details. \n\nYou should have \
received a copy of the GNU General Public License along with this program; \
if not, write to the Free Software Foundation, Inc., 51 Franklin Street, \
Fifth Floor, Boston, MA 02110-1301, USA."

# ---------------------------------------------------------------------
# Importamos los modulos necesarios

import hashlib
import gettext
import os.path
from os import pardir

# importamos los modulos para la parte grafica
try:
    import pygtk
    pygtk.require('2.0')
except:
    # Some distributions come with GTK2, but not pyGTK (or pyGTKv2)
    pass

try:
    import gtk
    import gtk.glade
except:
    print "You need to install pyGTK or GTKv2 or set your PYTHONPATH correctly"
    sys.exit(1)


# Algunas cosas para gettext (i18n / traducciones)
_ = gettext.gettext

gettext.textdomain("pysum")
gtk.glade.textdomain("pysum")


# Las siguientes Clases/funciones calculan los hash del un archivo.
# Es importante que el .read() se realice por partes para no
# llenar la memoria


class hashfile():
    """Clase para calcular los diferentes hashs"""

    def __init__(self, filename):
        try:
            self.archivo = open(filename, "rb")
        except:
            print _("Can't open the file:"), filename

    def getmd5(self):
    # Definimos una funcion para obtener el hash md5 de los archivos
        suma = hashlib.md5()
        while True:
            data = self.archivo.read(10240)
            if not data:
                break
            suma.update(data)
        self.archivo.close()
        return suma.hexdigest()

    def getsha1(self):
    # Definimos una funcion para obtener el hash sha1 de los archivos
        suma = hashlib.sha1()
        while True:
            data = self.archivo.read(10240)
            if not data:
                break
            suma.update(data)
        self.archivo.close()
        return suma.hexdigest()

    def getsha256(self):
    # Definimos una funcion para obtener el hash sha256 de los archivos
        suma = hashlib.sha256()
        while True:
            data = self.archivo.read(10240)
            if not data:
                break
            suma.update(data)
        self.archivo.close()
        return suma.hexdigest()

    def getsha512(self):
    # Definimos una funcion para obtener el hash sha512 de los archivos
        suma = hashlib.sha512()
        while True:
            data = self.archivo.read(10240)
            if not data:
                break
            suma.update(data)
        self.archivo.close()
        return suma.hexdigest()


# Función que obtiene el texto de la opcion seleccionada en un ComboBox

def valor_combobox(combobox):
    model = combobox.get_model()
    activo = combobox.get_active()
    if activo < 0:
        return None
    return model[activo][0]


# Interfaz grafica (gtk-glade)
# Clase para el Loop principal (de la interfaz grafica)


class MainGui:
    "GTK/Glade User interface to pysum application. This is a pyGTK window"

    def __init__(self):
        # Le indicamos al programa que archivo XML de glade usar
        # la comprobación es para que funcione el paquete debian
        if os.path.exists("pysum.glade"):
            self.widgets = gtk.glade.XML("pysum.glade")
        else:
            self.widgets = gtk.glade.XML(os.path.join(resources_dir,
            "pysum.glade"))

        # Creamos un diccionario con los manejadores definidos en glade
        # y sus respectivas llamadas.
        signals = {"on_buttonopen1_clicked": self.on_buttonopen1_clicked,
                   "on_buttonok1_clicked": self.on_buttonok1_clicked,
                   "on_about1_activate": self.on_about1_activate,
                   "gtk_main_quit": gtk.main_quit}

        # Autoconectamos las signals.
        self.widgets.signal_autoconnect(signals)

        ## Del archivo glade obtenemos los widgets a usar
        # estas widgets son de las pestaña para obtener hash
        self.entry1 = self.widgets.get_widget("entry1")
        self.textview1 = self.widgets.get_widget("textview1")

        # En el ComboBox hay que seleccionar por defecto la primera opcion
        self.combobox1 = self.widgets.get_widget("combobox1")
        self.combobox1.set_active(0) # Fijamos el primer elemento de la lista


        # Similar al .glade, hay que determinar donde esta el icono del programa
        # primero asumimos que esta en el directorio de las fuentes (trunk/img/)
        self.icono = os.path.join(os.pardir, "img", "pysum.png")
        if os.path.exists(self.icono) == False:
            # si no esta alli, cambiamos la ruta a la definida en img_dir
            self.icono = os.path.join(img_dir, "pysum.png")

        # Ahora le agregamos el icono a la ventana
        self.mainwindow = self.widgets.get_widget("mainwindow")
        try:
            self.mainwindow.set_icon_from_file(self.icono)
        except:
            print "Error: no se puede cargar el icono: %s" % (self.icono)


    # De aqui en adelante comienza las acciones propias del programa
    # Como las ventanas especiales y las acciones a realizar

    # Funcion para abrir archivos (dialogo abrir archivo)
    def file_browse(self):
        "This function is used to browse for a file. Is a open dialog"
        dialog_buttons = (gtk.STOCK_CANCEL,
                         gtk.RESPONSE_CANCEL,
                         gtk.STOCK_OPEN,
                         gtk.RESPONSE_OK)
        file_open = gtk.FileChooserDialog(title=_("Select a file"),
                    action=gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons=dialog_buttons)
        resultado = "" # Aquí almacenamos la ruta del archivo
        if file_open.run() == gtk.RESPONSE_OK:
            resultado = file_open.get_filename()
        file_open.destroy()
        return resultado

    # Ventana generica de error
    def error(self, message):
        "Display the error dialog "
        dialog_error = gtk.MessageDialog(parent=None, flags=0,
                       buttons=gtk.BUTTONS_OK)
        dialog_error.set_title(_("Error"))
        label = gtk.Label(message)
        dialog_error.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog_error.run()
        dialog_error.destroy()

    # Ventana Acerca de (los creditos).
    def about_info(self, data=None):
        "Display the About dialog"
        about = gtk.AboutDialog()
        about.set_name("pySum")
        about.set_version(__version__)
        about.set_comments(_("A pygtk application for create and \
verify md5 and other checksum"))
        about.set_copyright("Copyright © 2008-2010 Daniel Fuentes B.")

        def openHomePage(widget, url, url2): # Para abrir el sitio
            import webbrowser
            webbrowser.open_new(url)

        gtk.about_dialog_set_url_hook(openHomePage, website)
        try:
            about.set_logo(gtk.gdk.pixbuf_new_from_file(self.icono))
        except:
            print "Error: no se puede cargar el icono: %s" % (self.icono)
        about.set_website(website)
        about.set_authors([authors])
        about.set_license(license)
        about.set_wrap_license(True) # Adapta el texto a la ventana

        about.run()
        about.destroy()


# Declaramos las acciones a realizar (menus, botones, etc.):

    # Definimos las acciones de los menus #
    def on_about1_activate(self, widget):
        "Open the About windows"
        self.about_info()

    # Definimos las acciones de los botones #
    # Pestaña que obtiene los hash

    def on_buttonopen1_clicked(self, widget): # Boton abrir
        "Called when the user wants to open a file"
        ruta_archivo = self.file_browse()
        self.entry1.set_text(ruta_archivo)

    def on_buttonok1_clicked(self, widget): #Boton aceptar, para calcular hash
        "This button generate the hash"
        text_buffer = gtk.TextBuffer()
        # Comprobamos la opcion elegida en el ComboBox
        combobox_selec = valor_combobox(self.combobox1)
        # Se obtiene la ruta del archivo desde la entrada y crea un buffer
        texto_entry1 = self.entry1.get_text()
        archivo = hashfile(texto_entry1)
        # Se intenta obtener el hash, dependiendo de la opcion escogida en
        # el ComboBox hay que obtener el hash correcto (md5, sha-1, etc)
        try:
            if combobox_selec == "md5":
                text_buffer.set_text(str(archivo.getmd5()))
            elif combobox_selec == "sha1":
                text_buffer.set_text(str(archivo.getsha1()))
            elif combobox_selec == "sha256":
                text_buffer.set_text(str(archivo.getsha256()))
            elif combobox_selec == "sha512":
                text_buffer.set_text(str(archivo.getsha512()))
        except:
            if (len(texto_entry1) == 0):
                self.error(_("Please choose a file"))
            else:
                self.error(_("Can't open the file:") + texto_entry1)
        # Se muestra el buffer (hash obtenido) en textview
        self.textview1.set_buffer(text_buffer)


if __name__ == "__main__":
    MainGui()
    gtk.main()
