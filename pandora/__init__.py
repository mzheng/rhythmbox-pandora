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
        print "activating sample python plugin"
        db = shell.props.db
        entry_type = db.entry_register_type("PandoraEntryType")
        
        width, height = gtk.icon_size_lookup(gtk.ICON_SIZE_LARGE_TOOLBAR)
        icon = gtk.gdk.pixbuf_new_from_file_at_size(self.find_file("pandora.png"), width, height)
        self.source = gobject.new (PandoraSource, 
                                   shell=shell, 
                                   name=_("Pandora"),
                                   icon=icon, 
                                   entry_type=entry_type)

        shell.append_source(self.source, None)
        shell.register_entry_type_for_source(self.source, entry_type)
        
        self.pec_id = shell.get_player().connect_after('playing-song-changed', self.playing_entry_changed)
        

    def deactivate(self, shell):
        #TODO: CLEANUP
        print "deactivating sample python plugin"
        shell.get_player().disconnect (self.pec_id)
        self.source.delete_thyself()
        self.source = None
        
    def create_configure_dialog(self, dialog=None):
        if not dialog:
            builder_file = self.find_file("pandora-prefs.ui")
            dialog = PandoraConfigureDialog(builder_file).get_dialog()
        dialog.present()
        return dialog
    
    def playing_entry_changed(self, sp, entry):
        self.source.playing_entry_changed(entry)
        

            

        

        
            
gobject.type_register(PandoraSource)

