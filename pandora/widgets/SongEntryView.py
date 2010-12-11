import rb
import gtk
class SongEntryView(rb.EntryView):
    def __init__(self, db, player):
        rb.EntryView.__init__(self,db, player, None, False, False)
        self.load_columns()
        
        
    def load_columns(self):
        self.append_column(rb.ENTRY_VIEW_COL_TITLE, True)
        self.append_column(rb.ENTRY_VIEW_COL_ARTIST, True)
        self.append_column(rb.ENTRY_VIEW_COL_ALBUM, True)
        self.append_column(rb.ENTRY_VIEW_COL_DURATION, True)
        
        # column properties
        self.set_columns_clickable(False)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)