
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

import gtk

class ErrorView(object):
    def __init__(self, plugin, callback):
        self.__plugin = plugin
        self.callback = callback
        
        builder_file = self.__plugin.find_file("pandora/widgets/error_area.ui")
        builder = gtk.Builder()
        builder.add_from_file(builder_file)
        self.error_frame = builder.get_object('error_frame')
        error_area = builder.get_object('error_event_box')
        self.primary_error = builder.get_object('primary_message')
        self.secondary_error = builder.get_object('secondary_message')
        # Hack to get the tooltip background color
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_name("gtk-tooltip")
        window.ensure_style()
        style = window.get_style()
        error_area.set_style(style)
        self.error_frame.set_style(style)
        
        account_button = builder.get_object("account_settings")
        account_button.connect("clicked", self.on_account_settings_clicked)
    
    def get_error_frame(self):
        return self.error_frame
    
    def show(self, primary_message, secondary_message=None):
        self.primary_error.set_text(primary_message)
        if secondary_message is None:
            self.secondary_error.hide()
        else:
            self.secondary_error.set_text(secondary_message)
            self.secondary_error.show()
        self.error_frame.show()
    
    def hide(self):
        self.error_frame.hide()
    
    def on_account_settings_clicked(self, *args):
        self.__plugin.create_configure_dialog(callback=self.callback)