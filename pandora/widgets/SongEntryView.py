import rb, rhythmdb
import gtk

from cellpixbufbutton import *
from pixbufbutton import *

class SongEntryView(rb.EntryView):
    __gsignals__ = {
                  'star': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gtk.TreeModel, gtk.TreeIter)),
    }
    
    def __init__(self, db, player, plugin):
        rb.EntryView.__init__(self,db, player, None, False, False)
        
        self.db = db
        self.plugin = plugin
        self.pixs = [gtk.gdk.pixbuf_new_from_file(self.plugin.find_file('pandora/widgets/star-off.png')),
                     gtk.gdk.pixbuf_new_from_file(self.plugin.find_file('pandora/widgets/star-on.png'))]
            
        self.load_columns()
        
        
    def load_columns(self):
        self.append_column(rb.ENTRY_VIEW_COL_TITLE, True)
        self.append_column(rb.ENTRY_VIEW_COL_ARTIST, True)
        self.append_column(rb.ENTRY_VIEW_COL_ALBUM, True)
        self.append_column(rb.ENTRY_VIEW_COL_DURATION, True)
        
        cell_render = CellPixbufButton()
        #cell_render = PixbufButton()
        cell_render.connect('clicked', self.star_click)
        column = gtk.TreeViewColumn()
        column.pack_start(cell_render)
        column.set_cell_data_func(cell_render, self.star_func)
        column.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(self.pixs[0].get_width() + 5)
        self.append_column_custom(column, "", "STAR")
    
        # column properties
        self.set_columns_clickable(False)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    
    def star_func(self, column, cell, model, iter):
        entry = model.iter_to_entry(iter)
        star = self.db.entry_keyword_has(entry, 'star')

        if star:
            pixbuf = self.pixs[1]
        else:
            pixbuf = self.pixs[0]

        cell.set_property('pixbuf', pixbuf)
        
        
    def star_click(self, cell, model, path, iter):
        entry = model.iter_to_entry(iter)
        star = self.db.entry_keyword_has(entry, 'star')
        if star:
            # user cannot undo "Like Song"
            return
        else:
            self.db.entry_keyword_add(entry, 'star')
        
    
        self.db.commit()
        model.row_changed(path, iter)
        print "Clicked star"
    
        self.emit('star', model, iter)
        