
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

import webbrowser
import SearchDialog
import DeleteDialog

class StationsAction(object):
    def __init__(self, pandora_source, plugin):
        self.source = pandora_source
        self.__plugin = plugin
        self.stations_list = pandora_source.stations_list
        self.stations_model = pandora_source.stations_model
        self.worker_run = pandora_source.worker_run
        self.action_group = pandora_source.action_group
        self.searchDialog = None
        self.deleteDialog = DeleteDialog.NewDeleteDialog(self.__plugin)
        return
    
    def connect(self):
        self.stations_list.connect('entry-activated', self.station_activated_cb)
        self.stations_list.connect('selection-changed', self.station_selected_cb)
        
        action = self.action_group.get_action('StationInfo')
        action.connect('activate', self.view_station_info)
        action = self.action_group.get_action('AddStation')
        action.connect('activate', self.show_search_dialog)
        
        action = self.action_group.get_action('DeleteStation')
        action.connect('activate', self.show_delete_dialog)
        
    def station_activated_cb(self, entry_view, station_entry):
        self.source.play_station(station_entry)
        
    def station_selected_cb(self, entry_view):
        print "Station selected"
        if not self.source.is_current_station(None):
            return
        selected = entry_view.get_selected_entries()
        if not selected:
            return
        station_entry = selected[0]
        self.source.play_station(station_entry)
    
    def view_station_info(self, *args):
        station = self.selected_station()
        webbrowser.open(station.info_url)
        
    def selected_station(self):
        selected = self.stations_list.get_selected_entries()
        station_entry = selected[0]
        url = station_entry.get_playback_uri()
        station = self.stations_model.get_station(url)
        return station
    
    def show_search_dialog(self, *args):
        if self.searchDialog:
            self.searchDialog.present()
        else:
            self.searchDialog = SearchDialog.NewSearchDialog(self.__plugin, self.worker_run)
            self.searchDialog.show_all()
            self.searchDialog.connect("response", self.add_station_cb)
            
    
    def add_station_cb(self, dialog, response):
        print "in add_station_cb", dialog.result, response
        if response == 1:
            self.worker_run("add_station_by_music_id", (dialog.result.musicId,), self.station_added, "Creating station...")
        dialog.hide()
        dialog.destroy()
        self.searchDialog = None
        
    #TODO: Play station
    def station_added(self, station):
        # Add station to list and start playing it
        print "Added and switching to station: %s" %(repr(station))
        station_entry = self.stations_model.add_station(station, station.name, 0) #1) # After QuickMix
        self.source.play_station(station_entry)
        
        
    def show_delete_dialog(self, *args):
        selected = self.stations_list.get_selected_entries()
        station_entry = selected[0]
        url = station_entry.get_playback_uri()
        station = self.stations_model.get_station(url)
        
        # Show Delete Confirmation Dialog
        self.deleteDialog.set_property("text", "Are you sure you want to delete the station \"%s\"?"%(station.name))
        response = self.deleteDialog.run()
        self.deleteDialog.hide()

        if response:
            # delete station, if it is currently playing, play the first station instead
            self.worker_run(station.delete, context='net', message="Deleting Station...")
            self.stations_model.delete_station(url)
            print "Deleted station %s " %(repr(station))
            if self.source.is_current_station(station):
                # exclude "QuickMix"
                if self.stations_model.get_num_entries() <= 0: #1:
                    return
                first_station_entry = self.stations_model.get_first_station()
                print "Deleted current station, play first station instead"
                self.source.play_station(first_station_entry)