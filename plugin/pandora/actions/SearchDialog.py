
"""
    rhythmbox-pandora plugin for rhythmbox application.
    Copyright (C) 2010  Meng Jun Zheng <mzheng@andrew.cmu.edu>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gtk, gobject
import cgi

class SearchDialog(gtk.Dialog):
    __gtype_name__ = "SearchDialog"

    def __init__(self):
        """__init__ - This function is typically not called directly.
        Creation of a SearchDialog requires redeading the associated ui
        file and parsing the ui definition extrenally, 
        and then calling SearchDialog.finish_initializing().
    
        Use the convenience function NewSearchDialog to create 
        a SearchDialog object.
    
        """
        pass

    def finish_initializing(self, builder, worker_run):
        """finish_initalizing should be called after parsing the ui definition
        and creating a SearchDialog object with it in order to finish
        initializing the start of the new SearchDialog instance.
    
        """
        #get a reference to the builder and set up the signals
        self.builder = builder
        self.builder.connect_signals(self)
        
        self.entry = self.builder.get_object('entry')
        self.treeview = self.builder.get_object('treeview')
        self.okbtn = self.builder.get_object('okbtn')
        self.searchbtn = self.builder.get_object('searchbtn')
        self.model = gtk.ListStore(gobject.TYPE_PYOBJECT, str)
        self.treeview.set_model(self.model)
        
        self.worker_run = worker_run
        
        self.result = None


    def ok(self, widget, data=None):
        """ok - The user has elected to save the changes.
        Called before the dialog returns gtk.RESONSE_OK from run().

        """
        

    def cancel(self, widget, data=None):
        """cancel - The user has elected cancel changes.
        Called before the dialog returns gtk.RESPONSE_CANCEL for run()

        """         
        pass
        
    def search_clicked(self, widget):
        self.search(self.entry.get_text())
        
    def search(self, query):
        if not query: return
        def callback(results):
            self.model.clear()
            for i in results:
                if i.resultType is 'song':
                    mk = "<b>%s</b> by %s"%(cgi.escape(i.title), cgi.escape(i.artist))
                elif i.resultType is 'artist':
                    mk = "<b>%s</b> (artist)"%(cgi.escape(i.name))
                self.model.append((i, mk))
            self.treeview.show()
            self.searchbtn.set_sensitive(True)
            self.searchbtn.set_label("Search")
        self.worker_run('search', (query,), callback, "Searching...")
        self.searchbtn.set_sensitive(False)
        self.searchbtn.set_label("Searching...")
        
    def get_selected(self):
        sel = self.treeview.get_selection().get_selected()
        if sel:
            return self.treeview.get_model().get_value(sel[1], 0)
            
    def cursor_changed(self, *ignore):
        self.result = self.get_selected()
        self.okbtn.set_sensitive(not not self.result)
        

def NewSearchDialog(plugin, worker_run):
    """NewSearchDialog - returns a fully instantiated
    dialog-camel_case_nameDialog object. Use this function rather than
    creating SearchDialog instance directly.
    
    """

    #look for the ui file that describes the ui
    ui_filename = plugin.find_file("pandora/actions/SearchDialog.ui")

    
    builder = gtk.Builder()
    builder.add_from_file(ui_filename)    
    dialog = builder.get_object("search_dialog")
    dialog.finish_initializing(builder, worker_run)
    return dialog


