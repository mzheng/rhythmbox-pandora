import gtk, gobject

class PixbufButton(gtk.CellRendererPixbuf):

  __gsignals__ = {
                  'clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gtk.TreeModel, str, gtk.TreeIter)),
  }
  def __init__(self):
    gtk.CellRendererPixbuf.__init__(self)
    
  def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
    model = widget.get_model()
    iter = model.get_iter(path)
    
    self.emit('clicked', model, iter)

  def on_activate(self, event, widget, path, background_area, cell_area, flags):
    model = widget.get_model()
    iter = model.get_iter(path)
    
    self.emit('clicked', model, path, iter)

    return True

gobject.type_register(PixbufButton)