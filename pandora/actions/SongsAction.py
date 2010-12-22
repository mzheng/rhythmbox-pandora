import webbrowser
from pithos.pandora import *;

class SongsAction(object):
    def __init__(self, pandora_source):
        self.source = pandora_source
        self.songs_list = pandora_source.songs_list
        self.songs_model = pandora_source.songs_model
        self.worker_run = pandora_source.worker_run
        self.action_group = pandora_source.action_group
        
        
    
    def connect(self):
        self.songs_list.connect('star', self.do_star_clicked)
        
        action = self.action_group.get_action('SongInfo')
        action.connect('activate', self.view_song_info)
        action = self.action_group.get_action('LoveSong')
        action.connect('activate', self.love_selected_song)
        action = self.action_group.get_action('BanSong')
        action.connect('activate', self.ban_selected_song)
        action = self.action_group.get_action('TiredSong')
        action.connect('activate', self.tired_selected_song)
        action = self.action_group.get_action('BookmarkSong')
        action.connect('activate', self.bookmark_song)
        action = self.action_group.get_action('BookmarkArtist')
        action.connect('activate', self.bookmark_artist)
        
    def do_star_clicked(self, entryview, model, iter):
        entry = model.iter_to_entry(iter)
        self.love_song(entry) 
        
    def love_song(self, entry):
        url = entry.get_playback_uri()
        song = self.songs_model.get_song(url) 
        def callback(l):
            print "Loved song: %s " %(song.title)
            #TODO: Add feedback
        self.worker_run(song.rate, (RATE_LOVE,), callback, "Loving song...")
        
    def view_song_info(self, *args):
        song = self.selected_song()
        webbrowser.open(song.songDetailURL)
        
    def selected_song(self):
        selected = self.songs_list.get_selected_entries()
        entry = selected[0]
        url = entry.get_playback_uri()
        song = self.songs_model.get_song(url)
        return song
    
    def love_selected_song(self, *args):
        selected = self.songs_list.get_selected_entries()
        for entry in selected:
            if not self.songs_list.has_star(entry):
                self.songs_list.add_star(entry)
                self.love_song(entry)
    
    def ban_selected_song(self, *args):
        song = self.delete_selected_song()
        def callback(l):
            print "Banned song: %s " %(song.title)
        self.worker_run(song.rate, (RATE_BAN,), callback, "Banning song...")
    
    def tired_selected_song(self, *args):
        song = self.delete_selected_song()
        def callback(l):
            print "Tired of song: %s " %(song.title)
        self.worker_run(song.set_tired, (), callback, "Putting song on shelf...")
        
    def delete_selected_song(self):
        song = self.selected_song()
        url = song.audioUrl
        if self.source.is_current_song(song):
            self.source.next_song()
        # Remove from playlist
        self.songs_model.delete_song(url) 
        return song
    
    def bookmark_song(self, *args):
        song = self.selected_song()
        self.worker_run(song.bookmark, (), None, "Bookmarking...")
        print "Bookmarked song: %s" %(song.title)
    
    def bookmark_artist(self, *args):
        song = self.selected_song()
        self.worker_run(song.bookmark_artist, (), None, "Bookmarking...")
        print "Bookmarked artist: %s" %(song.artist)
                
                