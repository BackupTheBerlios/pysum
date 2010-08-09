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


########### START EDIT HERE ###########

# Directory with the files (*.glade)
GUI_DIR = "/usr/share/pysum"

# Directory with the images (icons)
IMG_DIR = "/usr/share/pysum"

########### STOP EDIT HERE ############

# ===================================================================
# Importamos los modulos necesarios

import hashlib
import zlib
import os.path
from os import pardir
from os import curdir
import gettext
import threading

# importamos los modulos para la parte grafica
try:
    import pygtk
    pygtk.require('2.0')
except:
    pass  # Some distributions come with GTK2, but not pyGTK (or pyGTKv2)

try:
    import gtk
    import gtk.glade
    import gobject
except:
    print "You need to install pyGTK or GTKv2 or set your PYTHONPATH correctly"
    sys.exit(1)

# ===================================================================
# Informacion del programa que se modifica con cierta frecuencia
# (para no escribir tanto al sacar nuevas versiones)

__version__ = "0.6 beta2"
AUTHOR = "Daniel Fuentes Barría <dbfuentes@gmail.com>"
WEBSITE = "http://pysum.berlios.de/"
LICENCE = "This program is free software; you can redistribute it \
and/or modify it under the terms of the GNU General Public License \
as published by the Free Software Foundation; either version 2 of the \
License, or (at your option) any later version.\n\nThis program is \
distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; \
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A \
PARTICULAR PURPOSE. See the GNU General Public License for more details.\
\n\nYou should have received a copy of the GNU General Public License \
along with this program; if not, write to the Free Software Foundation, \
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA."

# Algunas cosas para gettext (i18n / traducciones)
_ = gettext.gettext

gettext.textdomain("pysum")
gtk.glade.textdomain("pysum")

# ===================================================================
# La siguiente Clase calcula los hash de un archivo.
# El .read() hay que realizarlo por partes para no llenar la memoria
# Nota: hay 2 modulos para CRC32 en python: de zlib y de binascii
# de las dos anteriores, zlib es más rapida (por lo que se usa esa)


class GetHash(threading.Thread):
    """Clase para calcular distintos hashs mediante threads"""

    def __init__(self, filename, hashtype, text_mode, text_buffer,
            hash_esperado=None, label=None):
        super(GetHash, self).__init__()
        self.filename = filename
        self.hashtype = hashtype
        self.text_mode = text_mode  # modo texto o binario (para leer)
        self.text_buffer = text_buffer
        # la etiqueta y hash_esperado se usan en la comparacion:
        self.hash_esperado = hash_esperado
        self.label = label
        self.quit = False

    def update_textbuffer(self, resultado):
        # Nota: resultado es una cadena de texto con el hash obtenido
        self.text_buffer.set_text(resultado)
        return False

    def update_label(self, mensaje):
        # actualizar etiqueta (que se usa en la ventana de la comparacion)
        self.label.set_text(mensaje)
        return False

    def run(self):
        # metodo que se llama cuando se hace un start() sobre un thread
        while not self.quit:
            # Intenta leer el archivo
            try:
                if self.text_mode == True:
                    self.archivo = open(self.filename, "r")
                else:  # read in binary mode
                    self.archivo = open(self.filename, "rb")
            except:
                self.archivo = None
                print _("Can't open the file:"), self.filename
            # Dependiendo del tipo de hash, crea la suma adecuada
            if self.hashtype == "md5":
                suma = hashlib.md5()
            elif self.hashtype == "sha1":
                suma = hashlib.sha1()
            elif self.hashtype == "sha224":
                suma = hashlib.sha224()
            elif self.hashtype == "sha256":
                suma = hashlib.sha256()
            elif self.hashtype == "sha384":
                suma = hashlib.sha384()
            elif self.hashtype == "sha512":
                suma = hashlib.sha512()
            elif self.hashtype == "crc32":  # caso especial se usa zlib
                suma = 0
            # calculamos el hash (crc32 es un caso especial)
            if self.hashtype == "crc32":
                while True:
                    data = self.archivo.read(10240)
                    if not data:
                        break
                    suma = zlib.crc32(data, suma)
                self.archivo.close()
                # python 2.x muestra un valor entre : -2147483648,
                # 2147483648 (32-bit) y 0, 4294967296 (64-bit)
                # arreglar con este if (http://bugs.python.org/issue1202)
                if suma < 0:
                    #suma = (long(suma) + 4294967296L)
                    suma = suma & 0xffffffffL
                # Obtener cadena de texto con el hash
                resultado = "%08x" % (suma)
                # Actualizar ventana (textbuffer)
                gobject.idle_add(self.update_textbuffer, resultado)
            # Calculamos el hash para los demas casos
            else:
                while True:
                    data = self.archivo.read(10240)
                    if not data:
                        break
                    suma.update(data)
                self.archivo.close()
                resultado = str(suma.hexdigest())
                gobject.idle_add(self.update_textbuffer, resultado)
            # comparamos el hash hesperado con el obtenido (segunda tab)
            if self.hash_esperado != None:
                if resultado == self.hash_esperado:
                    mensaje = _("%s checksums are the same") % (self.hashtype)
                else:
                    mensaje = (_("Checksums are diferent\nFile: ") +
                        resultado + _("\nExpected: ") + self.hash_esperado)
                gobject.idle_add(self.update_label, mensaje)
            self.quit = True  # Terminar la ejecucion del run()


def valor_combobox(combobox):
    # Funcion que obtiene el texto de la opcion seleccionada en un ComboBox
    model = combobox.get_model()
    activo = combobox.get_active()
    if activo < 0:
        return None
    return model[activo][0]

# ===================================================================
# Clase para el Loop principal de la interfaz grafica (gtk-glade)


class MainGui:
    "GTK/Glade User interface to pysum application. This is a pyGTK window"

    def __init__(self):
        # Le indicamos al programa que archivo XML de glade usar
        # la comprobación es para que funcione el paquete debian
        if os.path.exists(os.path.join(GUI_DIR, "pysum.glade")):
            self.widgets = gtk.glade.XML(os.path.join(GUI_DIR, "pysum.glade"))
        else:
            self.widgets = gtk.glade.XML("pysum.glade")

        # Creamos un diccionario con los manejadores definidos en glade
        # y sus respectivas llamadas.
        signals = {"on_buttonopen1_clicked": self.on_buttonopen1_clicked,
                   "on_buttonok1_clicked": self.on_buttonok1_clicked,
                   "on_buttonopen2_clicked": self.on_buttonopen2_clicked,
                   "on_buttonok2_clicked": self.on_buttonok2_clicked,
                   "on_about1_activate": self.on_about1_activate,
                   "gtk_main_quit": gtk.main_quit}

        # Autoconectamos las signals.
        self.widgets.signal_autoconnect(signals)

        # Del archivo glade obtenemos los widgets a usar
        # estas widgets son de las pestaña para obtener hash
        self.entry1 = self.widgets.get_widget("entry1")
        self.combobox1 = self.widgets.get_widget("combobox1")
        self.radiobutton1 = self.widgets.get_widget("radiobutton1")
        self.radiobutton2 = self.widgets.get_widget("radiobutton2")
        self.textview1 = self.widgets.get_widget("textview1")
        # los widgets de la segunda pestaña (la usada para comparar)
        self.entry2 = self.widgets.get_widget("entry2")
        self.combobox2 = self.widgets.get_widget("combobox2")
        self.radiobutton3 = self.widgets.get_widget("radiobutton3")
        self.radiobutton4 = self.widgets.get_widget("radiobutton4")
        self.entry3 = self.widgets.get_widget("entry3")

        # En los ComboBox, seleccionar por defecto la segunda opcion (md5)
        self.combobox1.set_active(1)
        self.combobox2.set_active(1)

    ## Similar al .glade, hay que determinar donde esta el icono del programa
        # probamos buscar la imagen en la ruta definida en IMG_DIR
        if os.path.exists(os.path.join(IMG_DIR, "pysum.png")):
            self.icono = os.path.join(IMG_DIR, "pysum.png")
        # probamos buscar la imagen en ~/src/img/pysum.png
        elif os.path.exists(os.path.join(os.curdir, "img", "pysum.png")):
            self.icono = os.path.join(os.curdir, "img", "pysum.png")
        # probamos en ~/src/pysum.png
        elif os.path.exists(os.path.join(os.curdir, "pysum.png")):
            self.icono = os.path.join(os.curdir, "pysum.png")
        # luego probamos si esta en el directorio de las fuentes (~/img/)
        elif os.path.exists(os.path.join(os.pardir, "img", "pysum.png")):
            self.icono = os.path.join(os.pardir, "img", "pysum.png")
        else:
            self.icono = "pysum.png"
        # Ahora le agregamos el icono a la ventana principal
        self.mainwindow = self.widgets.get_widget("mainwindow")
        try:
            self.mainwindow.set_icon_from_file(self.icono)
        except:
            print (_("Error: unable to load icon: %s") % (self.icono))

# -------------------------------------------------------------------
# En adelante comienza las ventanas y acciones propias del programa
# -------------------------------------------------------------------

    # Funcion para abrir archivos (dialogo abrir archivo)
    def file_browse(self):
        "This function is used to browse for a file. Is a open dialog"
        dialog_buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        file_open = gtk.FileChooserDialog(title=_("Select a file"),
                action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=dialog_buttons)
        resultado = ""  # Aqui almacenamos la ruta del archivo
        if file_open.run() == gtk.RESPONSE_OK:
            resultado = file_open.get_filename()
        file_open.destroy()
        return resultado

    # Ventana Acerca de (los creditos).
    def about_info(self, data=None):
        "Display the About dialog"
        about = gtk.AboutDialog()
        about.set_name("pySum")
        about.set_version(__version__)
        about.set_comments(_("A pygtk application for create and \
verify md5 and other checksum"))
        about.set_copyright("Copyright © 2008-2010 Daniel Fuentes B.")

        def openHomePage(widget, url, url2):  # Para abrir el sitio
            import webbrowser
            webbrowser.open_new(url)

        gtk.about_dialog_set_url_hook(openHomePage, WEBSITE)
        try:
            about.set_logo(gtk.gdk.pixbuf_new_from_file(self.icono))
        except:
            print _("Error: unable to load icon: %s") % (self.icono)
        about.set_website(WEBSITE)
        about.set_authors([AUTHOR])
        about.set_license(LICENCE)
        about.set_wrap_license(True)  # Adapta el texto a la ventana
        about.run()
        about.destroy()

    # Ventana generica de para entregar informacion (errores, avisos, etc.)
    def info(self, message, title="Error"):
        "Display the info dialog"
        dialogo = gtk.MessageDialog(parent=None, flags=0,
                    buttons=gtk.BUTTONS_OK)
        dialogo.set_title(title)
        label = message  # el message tiene que ser un gtk.Label()
        dialogo.vbox.pack_start(label, True, True, 0)
        label.show()
        dialogo.run()
        dialogo.destroy()

# -------------------------------------------------------------------
# Declaramos las acciones a realizar (por los menus, botones, etc.):
# -------------------------------------------------------------------

    # Definimos las acciones de los menus
    def on_about1_activate(self, widget):
        "Open the About windows"
        self.about_info()

    # ---------------------------------------------------------------
    # Pestaña que obtiene el hash de un archivo
    # ---------------------------------------------------------------

    def on_buttonopen1_clicked(self, widget):  # Boton abrir 1
        "Called when the user wants to open a file"
        ruta_archivo = self.file_browse()
        self.entry1.set_text(ruta_archivo)

    def on_buttonok1_clicked(self, widget):  # Boton ok para calcular hash
        "This button generate the hash"
        # Se obtiene la ruta del archivo (entry1) y el tipo de hash (ComboBox)
        texto_entry1 = self.entry1.get_text()
        combobox_selec = valor_combobox(self.combobox1)
        # obtener el modo de lectura segun el radiobutton seleccionado
        # RadioButton.get_active() returns True if the button is checked
        if self.radiobutton1.get_active() == True:
            text_mode = True
        elif self.radiobutton2.get_active() == True:
            text_mode = False
        else:
            text_mode = False
        # Se crea un buffer de texto (para el resultado del hash)
        text_buffer = gtk.TextBuffer()
        # Se intenta obtener el hash, dependiendo de la opcion escogida
        if (len(texto_entry1) == 0):  # No se especifica archivo
            mensaje = gtk.Label(_("Please choose a file"))
            self.info(mensaje, _("Error"))
        else:
            # Comprobar si el archivo existe:
            if os.path.exists(texto_entry1):
                if combobox_selec == "md5":
                    hashtype = "md5"
                elif combobox_selec == "sha1":
                    hashtype = "sha1"
                elif combobox_selec == "sha224":
                    hashtype = "sha224"
                elif combobox_selec == "sha256":
                    hashtype = "sha256"
                elif combobox_selec == "sha384":
                    hashtype = "sha384"
                elif combobox_selec == "sha512":
                    hashtype = "sha512"
                elif combobox_selec == "crc32":
                    hashtype = "crc32"
                # Calcular el hash con estos datos
                hilo = GetHash(texto_entry1, hashtype, text_mode, text_buffer)
                hilo.start()
                # Se muestra el buffer (hash obtenido) en textview
                self.textview1.set_buffer(text_buffer)
                hilo.quit = True
            else:
                mensaje = gtk.Label((_("Can't open the file:") + texto_entry1))
                self.info(mensaje, _("Error"))

    # ---------------------------------------------------------------
    # Pestaña que compara el hash de un archivo con un valor experado
    # ---------------------------------------------------------------

    def on_buttonopen2_clicked(self, widget):  # Boton abrir 2
        "Called when the user wants to open a file"
        ruta_archivo = self.file_browse()
        self.entry2.set_text(ruta_archivo)

    def on_buttonok2_clicked(self, widget):
        # Obtenemos el texto del hash esperado (del entry3)
        hash_esperado = str(self.entry3.get_text())
        # Al hacer split se pierde el doble, triple o mas espacios (que pueden
        # haber antes o despues del texto) y luego joint unen los textos
        hash_esperado = hash_esperado.lower()
        hash_esperado = hash_esperado.split()
        hash_esperado = "".join(hash_esperado)
        # Ahora obtenemos el nombre del archivo y tipo de hash
        texto_entry2 = self.entry2.get_text()
        combobox_selec = valor_combobox(self.combobox2)
        # comprobar el modo de lectura a usar (text/binary)
        if self.radiobutton3.get_active() == True:
            text_mode = True
        else:  # en caso de estar el radiobutton4 seleccionado
            text_mode = False
        # iniciamos un buffer de texto y una etiqueta
        text_buffer = gtk.TextBuffer()
        label = gtk.Label()
        # Se intenta obtener el hash (primero comprobar el archivo)
        if (len(texto_entry2) == 0):
            label.set_text(_("Please choose a file"))
            self.info(label, _("Error"))
        else:
            if os.path.exists(texto_entry2):
                if combobox_selec == "md5":
                    hashtype = "md5"
                elif combobox_selec == "sha1":
                    hashtype = "sha1"
                elif combobox_selec == "sha224":
                    hashtype = "sha224"
                elif combobox_selec == "sha256":
                    hashtype = "sha256"
                elif combobox_selec == "sha384":
                    hashtype = "sha384"
                elif combobox_selec == "sha512":
                    hashtype = "sha512"
                elif combobox_selec == "crc32":
                    hashtype = "crc32"
                # Comprobamos si el resultado coincide con lo esperado
                hilo = GetHash(texto_entry2, hashtype, text_mode, text_buffer,
                    hash_esperado, label)
                hilo.start()
                # crear una ventana que entrege el resultado de la comparacion
                self.info(label, _("Result"))
                hilo.quit = True
            else:
                label.set_text(_("Can't open the file:") + texto_entry2)
                self.info(label, _("Error"))


if __name__ == "__main__":
    gobject.threads_init()
    MainGui()
    gtk.main()
