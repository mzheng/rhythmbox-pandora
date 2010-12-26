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

import gobject, gtk
import gnomekeyring as keyring

class PandoraConfigureDialog(object):
    def __init__(self, builder_file, callback):
        self.__builder = gtk.Builder()
        self.__builder.add_from_file(builder_file)
        
        self.callback = callback
        self.dialog = self.__builder.get_object('preferences_dialog')
        self.dialog.connect("response", self.close_button_pressed)
        
        self.__keyring_data = {
            'id' : 0,
            'item': None
        }
        
        self.find_keyring_items()
            
    def get_dialog(self):
        return self.dialog
        
    def close_button_pressed(self, dialog, response):
        if response != gtk.RESPONSE_CLOSE:
            return
        username = self.__builder.get_object("username").get_text()
        password = self.__builder.get_object("password").get_text()
        # TODO: Verify Account
        if self.__keyring_data['item']:
            self.__keyring_data['item'].set_secret('\n'.join((username, password)))
        keyring.item_set_info_sync(None, self.__keyring_data['id'], self.__keyring_data['item'])
        dialog.hide()
        
        if self.callback:
            self.callback()
            self.callback = None
    
    def fill_account_details(self):
        try:
            if self.__keyring_data['item']:
                username, password = self.__keyring_data['item'].get_secret().split('\n')
        except ValueError: # Couldn't parse the secret, probably because it's empty
            return
        self.__builder.get_object("username").set_text(username)
        self.__builder.get_object("password").set_text(password)
        
    def find_keyring_items(self):
        def got_items(result, items):
            def created_item(result, id):
                if result is None: # Item successfully created
                    self.__keyring_data['id'] = id
                    keyring.item_get_info(None, id, got_item)
                else:
                    print "Couldn't create keyring item: " + str(result)
                    
            def got_item(result, item):
                if result is None: # Item retrieved successfully
                    self.__keyring_data['item'] = item
                    self.fill_account_details()
                else:
                    print "Couldn't retrieve keyring item: " + str(result) 
                
            if result is None and len(items) != 0: # Got list of search results
                self.__keyring_data['id'] = items[0].item_id
                keyring.item_get_info(None, self.__keyring_data['id'], got_item)
            elif result == keyring.NoMatchError or len(items) == 0: # No items were found, so we'll create one
                keyring.item_create(None,
                                    keyring.ITEM_GENERIC_SECRET,
                                    "Rhythmbox: Pandora account information",
                                    {'rhythmbox-plugin': 'pandora'},
                                    "", # Empty secret for now
                                    True,
                                    created_item)
            else: # Some other error occurred
                print "Couldn't access keyring: " + str(result)
        # Make asynchronous calls
        keyring.find_items(keyring.ITEM_GENERIC_SECRET, {'rhythmbox-plugin': 'pandora'}, got_items)