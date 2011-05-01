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

import rhythmdb, rb
import gobject, gtk
import gst
import gnomekeyring as keyring

from pithos.pandora import *;
from pithos.gobject_worker import GObjectWorker

from PandoraConfigureDialog import PandoraConfigureDialog
from PandoraSource import PandoraSource



class PandoraPlugin(rb.Plugin):

    def __init__(self):
        rb.Plugin.__init__(self)
            
    def activate(self, shell):
        print "activating pandora plugin"
        db = shell.props.db
	try:
		entry_type = db.entry_register_type("PandoraEntryType")
	except AttributeError:
		entry_type = rhythmdb.EntryType()
        
        width, height = gtk.icon_size_lookup(gtk.ICON_SIZE_LARGE_TOOLBAR)
        icon = gtk.gdk.pixbuf_new_from_file_at_size(self.find_file("pandora.png"), width, height)
	# rhythmbox api break up (0.13.2 - 0.13.3)
	if hasattr(rb, 'rb_source_group_get_by_name'):
        	self.source = gobject.new (PandoraSource, 
	                                   shell=shell,
        	                           plugin=self, 
        	                           name=_("Pandora"),
        	                           icon=icon, 
        	                           entry_type=entry_type)

        	shell.append_source(self.source, None)
	else:
		group = rb.rb_display_page_group_get_by_id ("library")
		self.source = gobject.new (PandoraSource, 
	                                   shell=shell,
        	                           plugin=self, 
        	                           name=_("Pandora"),
        	                           pixbuf=icon, 
        	                           entry_type=entry_type)

        	shell.append_display_page(self.source, group)

        shell.register_entry_type_for_source(self.source, entry_type)
        
        # hack, should be done within gobject constructor
        self.source.init()
        
        self.pec_id = shell.get_player().connect_after('playing-song-changed', self.playing_entry_changed)
        

    def deactivate(self, shell):
        #TODO: CLEANUP
        print "deactivating pandora plugin"
        shell.get_player().disconnect (self.pec_id)
        self.source.delete_thyself()
        self.source = None
        
    def create_configure_dialog(self, dialog=None, callback=None):
        if not dialog:
            builder_file = self.find_file("pandora-prefs.ui")
            dialog_wrapper = PandoraConfigureDialog(builder_file, callback)
            dialog = dialog_wrapper.get_dialog()
        dialog.present()
        return dialog
    
    
    def playing_entry_changed(self, sp, entry):
        self.source.playing_entry_changed(entry)
        

            

        

        
            
gobject.type_register(PandoraSource)

