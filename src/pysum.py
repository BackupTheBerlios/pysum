#! /usr/bin/env python
# -*- coding: UTF-8 -*-

# pysum - A pygtk app to create and check md5 and other checksum 
# Copyright (C) 2008 Daniel Fuentes B. <dbfuentes@gmail.com>
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


# Importamos los modulos necesarios
import md5
import gettext
import locale

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
from SimpleGladeApp import SimpleGladeApp

# Algunas cosas para gettext (i18n - traducciones)

_ = gettext.gettext

gettext.textdomain("pysum")
gtk.glade.textdomain("pysum")

# Definimos una funcion para obtener el hash de los archivos
def getmd5(filename):
    "Calculate MD5 hash for a file without full-load in memory"
    try:
        fichero = open(filename, "rb")
    except:
        print _("Can't open the file:"), filename

    suma = md5.new()

    while True:
        data = fichero.read(10240)
        if not data:
            break
        suma.update(data)

    fichero.close()
    return suma.hexdigest()
	
# Interfaz grafica (gtk-glade)
# Clase para el Loop principal (de la interfaz grafica)

class Gui(SimpleGladeApp):

    # Funcion para abrir archivos (dialogo abrir archivo)
    def file_browse(self):
        "This function is used to browse for a file. Is a open dialog"
        dialog_buttons = (gtk.STOCK_CANCEL
                        , gtk.RESPONSE_CANCEL
                        , gtk.STOCK_OPEN
                        , gtk.RESPONSE_OK)
        file_open = gtk.FileChooserDialog(title=_("Select a file")
                    , action=gtk.FILE_CHOOSER_ACTION_OPEN
                    , buttons=dialog_buttons)

        # regresar la ruta del archivo
        resultado = ""
        if file_open.run() == gtk.RESPONSE_OK:
            resultado = file_open.get_filename()
        file_open.destroy()
        return resultado

    # Ventana de error
    def error(self, message):
        "Display the error dialog "
        dialog_error = gtk.MessageDialog(parent=None, flags=0, buttons=gtk.BUTTONS_OK)
        dialog_error.set_title(_("Error"))
        label = gtk.Label(message)
        dialog_error.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog_error.run()
        dialog_error.destroy()

    # Ventana Acerca de.
    def about_info(self,data=None):
        "Display the About dialog "
        about = gtk.AboutDialog()
        about.set_name("pySum")
        about.set_version("0.1")
        about.run()
        about.destroy()

# Declaramos las acciones a realizar (menus, botones, etc.):

    # Definimos las acciones de los menus
    def on_abrir1_activate(self, widget):
        "Called when the user wants to open a file"
        ruta_archivo = self.file_browse() #Obtiene el archivo 
        self.entry1.set_text(ruta_archivo)

    # Definimos las acciones de los botones:
    def on_button1_clicked(self, widget):# Boton abrir
        ruta_archivo = self.file_browse() 
        self.entry1.set_text(ruta_archivo)

    def on_button2_clicked(self, widget): #Boton calcular hash
        archivo = self.entry1.get_text() #obtiene la ruta desde la entrada
        text_buffer=gtk.TextBuffer()
        try:
            text_buffer.set_text(str(getmd5(archivo)))#fija el hash en el buffer
        except:
            if (len(archivo) == 0):
                self.error(_("Please choose a file"))
            else:
                self.error(_("Can't open the file: ") + archivo)
        self.textview1.set_buffer(text_buffer)

    def on_about1_activate(self, widget):
        self.about_info()

app = Gui("pysum.glade")
app.run()
