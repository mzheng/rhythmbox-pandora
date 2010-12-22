import rhythmdb, rb
import gobject, gtk
import gst
import gnomekeyring as keyring
from time import time

from pithos.pandora import *;
from pithos.gobject_worker import GObjectWorker

import widgets
import models
import actions


class PandoraSource(rb.StreamingSource):
    __gproperties__ = {
            'plugin': (rb.Plugin,
            'plugin',
            'plugin',
            gobject.PARAM_WRITABLE | gobject.PARAM_CONSTRUCT_ONLY)
    }
      
    def __init__(self):
        #rb.BrowserSource.__init__(self)
        rb.StreamingSource.__init__(self)
        
        # source state
        self.__activated = False
        self.__db = None # rhythmdb
        self.__player = None
        
        
        self.worker = GObjectWorker()
    
    def do_set_property(self, property, value):
        if property.name == 'plugin':
            self.__plugin = value
        else:
            raise AttributeError, 'unknown property %s' % property.name
    
    def do_impl_get_entry_view(self):
        return self.songs_list
    
    def do_impl_can_pause(self):
        return True
    
    def do_impl_handle_eos(self):
        return rb.SourceEOFType(3) #next
    
    def do_impl_try_playlist(self):
        return False
    
    def do_impl_show_popup(self):
        self.show_source_popup("/PandoraSourceMainPopup")
        
    def do_songs_show_popup(self, view, over_entry):
        self.show_single_popup(view, over_entry, "/PandoraSongViewPopup")
            
    def do_stations_show_popup(self, view, over_entry):
        self.show_single_popup(view, over_entry, "/PandoraStationViewPopup")
                
    def show_single_popup(self, view, over_entry, popup):
        if (over_entry):
            selected = view.get_selected_entries()
            if len(selected) == 1:
                self.show_source_popup(popup)
    
    #Override            
    def playing_entry_changed(self, entry):
        print "Playing Entry changed"
        if not self.__db or not entry:
            return
        if entry.get_entry_type() != self.__entry_type:
            return
        self.get_metadata(entry)
        
        url = entry.get_playback_uri()
        self.current_song = self.songs_model.get_song(url)
        if self.songs_model.is_last_entry(entry):
            self.get_playlist()
    
    def create_window(self):
        if self.vbox_main:
            self.remove(self.vbox_main)
            self.vbox_main.hide_all()
            self.vbox_main = None

        self.stations_list = widgets.StationEntryView(self.__db, self.__player)
        self.songs_list = widgets.SongEntryView(self.__db, self.__player, self.__plugin)
        
        self.vbox_main = gtk.VPaned()
        vbox_1 = gtk.VBox()
        vbox_1.pack_start(self.stations_list)
        self.vbox_main.pack1(vbox_1, True, False)
        vbox_2 = gtk.VBox()
        vbox_2.pack_start(self.songs_list)
        self.vbox_main.pack2(vbox_2, True, False)
        self.vbox_main.show_all()
    
        self.add(self.vbox_main)

    def connect_all(self):
        self.stations_list.connect('show_popup', self.do_stations_show_popup)
        self.songs_list.connect('show_popup', self.do_songs_show_popup)
        self.songs_action.connect()
        self.stations_action.connect()

    def create_popups(self):
        manager = self.__player.get_property('ui-manager')
        self.action_group = gtk.ActionGroup('PandoraPluginActions')
        action = gtk.Action('SongInfo', _('Song Info...'), _('View song information in browser'), 'gtk-info')
        self.action_group.add_action(action)
        action = gtk.Action('LoveSong', _('Love Song'), _('I love this song'), 'gtk-about')
        self.action_group.add_action(action)
        action = gtk.Action('BanSong', _('Ban Song'), _("I don't like this song"), 'gtk-cancel')
        self.action_group.add_action(action)
        action = gtk.Action('TiredSong', _('Tired of this song'), _("I'm tired of this song"), 'gtk-jump-to')
        self.action_group.add_action(action)
        action = gtk.Action('Bookmark', _('Bookmark'), _('Bookmark...'), 'gtk-add')
        self.action_group.add_action(action)
        action = gtk.Action('BookmarkSong', _('Song'), _("Bookmark this song"), None)
        self.action_group.add_action(action)
        action = gtk.Action('BookmarkArtist', _('Artist'), _("Bookmark this artist"), None)
        self.action_group.add_action(action)
        
        action = gtk.Action('AddStation', _('Create a New Station'), _('Create a new Pandora station'), 'gtk-add')
        self.action_group.add_action(action)
        
        action = gtk.Action('StationInfo', _('Station Info...'), _('View station information in browser'), 'gtk-info')
        self.action_group.add_action(action)
        action = gtk.Action('DeleteStation', _('Delete this Station'), _('Delete this Pandora Station'), 'gtk-remove')
        self.action_group.add_action(action)
         
        manager.insert_action_group(self.action_group, 0)
        popup_file = self.__plugin.find_file("pandora-ui.xml")
        self.ui_id = manager.add_ui_from_file(popup_file)
        manager.ensure_update()
        
    def do_impl_activate(self):
        if not self.__activated:
            shell = self.get_property('shell')
            self.__db = shell.get_property('db')
            self.__player = shell.get_player()
            self.__entry_type = self.get_property('entry-type')
            
            
            self.vbox_main = None
            
            self.create_window()
            self.create_popups()
            
            
            
            
            self.username, self.password = self.get_pandora_account_info()
            #Pandora
            self.pandora = make_pandora()
            self.stations_model = models.StationsModel(self.__db, self.__entry_type)
            self.songs_model = models.SongsModel(self.__db, self.__entry_type)
            self.songs_list.set_model(self.songs_model)
            self.current_station = None
            self.current_song = None
            
            self.songs_action = actions.SongsAction(self)
            self.stations_action = actions.StationsAction(self, self.__plugin)
            self.connect_all()
            
            # Enables skipping
            self.set_property('query-model', self.songs_model)
            
            self.retrying = False
            self.waiting_for_playlist = False
            self.pandora_connect()

            
            self.__activated = True
            
    # TODO: Update UI and Error Msg
    def worker_run(self, fn, args=(), callback=None, message=None, context='net'):
        
        if isinstance(fn,str):
            fn = getattr(self.pandora, fn)
            
        def cb(v):
            if callback: callback(v)
            
        def eb(e):
                
            def retry_cb():
                self.retrying = False
                if fn is not self.pandora.connect:
                    self.worker_run(fn, args, callback, message, context)
                
            if isinstance(e, PandoraAuthTokenInvalid) and not self.retrying:
                self.retrying = True
                print "Automatic reconnect after invalid auth token"                
                self.pandora_connect("Reconnecting...", retry_cb)
            elif isinstance(e, PandoraError):
                print e.message
            else:
                print e.traceback
                
        self.worker.send(fn, args, cb, eb)
  
    def get_pandora_account_info(self):
        try:
            result_list = keyring.find_items_sync(keyring.ITEM_GENERIC_SECRET, {'rhythmbox-plugin': 'pandora'})
        except gk.NoMatchError:
            print "Pandora Account Info not found"
            #TODO: Ask User to configure account
            return None, None
        result = result_list[0]
        secret = result.secret
        return tuple(secret.split('\n'))
      
    def pandora_connect(self, message="Logging in...", callback=None):
        args = (self.username,
                self.password)
                
        def pandora_ready(*ignore):
            #TODO: Selected station
            self.stations_model.clear()
            
            print "Pandora connected"
            #TODO: Station already exists
            #FIXME: Leave out QuickMix for now
            #for i in self.pandora.stations:
            #    if i.isQuickMix:
            #        self.stations_model.add_station(i, "QuickMix")
            
            for i in self.pandora.stations:
                if not i.isQuickMix:
                    self.stations_model.add_station(i, i.name)
            self.stations_list.set_model(self.stations_model)
            if callback:
                callback()       
                
        self.worker_run('connect', args, pandora_ready, message, 'login')
        
    def play_station(self, station_entry):
        prev_station = self.current_station
        
        url = station_entry.get_playback_uri()
        self.current_station = self.stations_model.get_station(url)
        
        if prev_station != None and prev_station != self.current_station:
            self.songs_model.clear()
        
        self.get_playlist(start = True)
        print "Station activated %s" %(url)

        now = int(time.time())
        self.__db.set(station_entry, rhythmdb.PROP_LAST_PLAYED, now)
        
    def get_playlist(self, start = False):
        if self.waiting_for_playlist: return
            
        def callback(songs):
            print "Got playlist"
            first_entry = None
            for song in songs:
                entry = self.songs_model.add_song(song)
                if first_entry == None:
                    first_entry = entry
                print "Title: %s" %(song.title)
                print "URL: %s" %(song.audioUrl)
            self.waiting_for_playlist = False
            if start:
                self.songs_list.scroll_to_entry(first_entry)
                self.__player.play_entry(first_entry, self)
                
            
            
        self.waiting_for_playlist = True
        self.worker_run(self.current_station.get_playlist, (), callback, "Getting songs...")

    def get_metadata(self, entry):
        if entry == None:
            print "Track not found in DB"
            return True
        duration = gst.CLOCK_TIME_NONE
        try:
            playerbin = self.__player.get_property ('player').get_property('playbin')
            duration, format = playerbin.query_duration(gst.FORMAT_TIME)
            if(duration != gst.CLOCK_TIME_NONE):
                self.__db.set(entry, rhythmdb.PROP_DURATION, duration/1000000000)
                self.__db.commit()
            print "duration: %s" %(duration)
        except Exception,e:
            print "Could not query duration"
            print e
            pass 
        
    def next_song(self):
        self.__player.do_next()
    
    def is_current_song(self, song):
        return song is self.current_song
    
    def is_current_station(self, station):
        return station is self.current_station
        

        