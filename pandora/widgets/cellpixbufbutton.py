"""
  rhythmbox-shoutcast plugin for rhythmbox application.
  Copyright (C) 2009  Alexey Kuznetsov <ak@axet.ru>
  
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

import gtk, gobject

class CellPixbufButton(gtk.GenericCellRenderer):

  __gsignals__ = {
                  'clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gtk.TreeModel, str, gtk.TreeIter)),
  }

  __gproperties__ = {
                     'pixbuf': (gtk.gdk.Pixbuf, 'pixbuf', 'pixbuf', gobject.PARAM_WRITABLE),
  }

  pixbuf = None

  def __init__(self):
    gtk.GenericCellRenderer.__init__(self)
    
    self.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)

  def do_set_property(self, property, value):
    if property.name == 'pixbuf':
      self.pixbuf = value
    else:
      raise AttributeError, 'unknown property %s' % property.name

  def on_get_size(self, widget, cell_area):
    x_offset = 0
    y_offset = 0
    pixbuf_width = self.pixbuf.get_width()
    pixbuf_height = self.pixbuf.get_height()

    calc_width = self.get_property('xpad') * 2 + pixbuf_width;
    calc_height = self.get_property('ypad') * 2 + pixbuf_height;

    if cell_area and pixbuf_width > 0 and pixbuf_height > 0:
      x_offset = self.get_property('xalign')  * (cell_area.width - calc_width - (2 * self.get_property('xpad')))
      x_offset = max(x_offset, 0) + self.get_property('xpad')
      x_offset = int(x_offset)
      y_offset = self.get_property('yalign') * (cell_area.height - calc_height - (2 * self.get_property('ypad')))
      y_offset = max(y_offset, 0) + self.get_property('ypad')
      y_offset = int(y_offset)
    
    return (x_offset, y_offset, calc_width, calc_height)

  def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
    (xoffset, yoffset, width, height) = self.get_size(widget, cell_area)
  
    xoffset += cell_area.x;
    yoffset += cell_area.y;
    width -= self.get_property('xpad') * 2;
    height -= self.get_property('ypad') * 2;
  
    draw_rect = cell_area.intersect((xoffset, yoffset, width, height)) 
    window.draw_pixbuf(None,
      self.pixbuf,
      draw_rect.x - xoffset,
      draw_rect.y - yoffset,
      draw_rect.x,
      draw_rect.y,
      draw_rect.width,
      draw_rect.height,
      gtk.gdk.RGB_DITHER_NORMAL,
      0, 0);

  def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
    model = widget.get_model()
    iter = model.get_iter(path)
    
    self.emit('clicked', model, iter)

  def on_activate(self, event, widget, path, background_area, cell_area, flags):
    model = widget.get_model()
    iter = model.get_iter(path)
    
    self.emit('clicked', model, path, iter)

    return True

gobject.type_register(CellPixbufButton)
