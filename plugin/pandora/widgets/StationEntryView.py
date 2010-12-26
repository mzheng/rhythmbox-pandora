
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

import rb
import gtk
class StationEntryView(rb.EntryView):
    def __init__(self, db, player):
        rb.EntryView.__init__(self,db, player, None, False, False)
        self.load_columns()
    
    def load_columns(self):
        self.append_column(rb.ENTRY_VIEW_COL_TITLE, True)
        self.append_column(rb.ENTRY_VIEW_COL_LAST_PLAYED, True)
        
        # column properties
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)