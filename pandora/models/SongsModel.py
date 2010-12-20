import rhythmdb
import pandora

class SongsModel(rhythmdb.QueryModel):
    MAX = 20
    def __init__(self, db, entry_type):
        rhythmdb.QueryModel.__init__(self)
        self.__db = db
        self.__entry_type = entry_type
        self.__last_entry = None
        self.__songs_dict = {} # Map from url to song
        
    def add_song(self, song, duration=None):
        url = song.audioUrl
        entry = self.__db.entry_new(self.__entry_type, url)
        self.__db.set(entry, rhythmdb.PROP_TITLE, song.title)
        self.__db.set(entry, rhythmdb.PROP_ARTIST, song.artist)
        self.__db.set(entry, rhythmdb.PROP_ALBUM, song.album)
        if duration != None:
            self.__db.set(entry, rhythmdb.PROP_DURATION, duration/1000000000)
        if song.rating == pandora.RATE_LOVE:
            self.__db.entry_keyword_add(entry, 'star')
        self.__db.commit()
        self.add_entry(entry, -1)
        self.__last_entry = entry
        
        self.__songs_dict[url] = song
        
        num_entries = self.get_num_entries()
        print "Number of entries: %d" %(num_entries)
             
        if num_entries > SongsModel.MAX:
            self.remove_old_songs()
        
        return entry
    
    def get_song(self, url):
        return self.__songs_dict[url]
    
    def is_last_entry(self, entry):
        return self.__last_entry == entry
    
    def get_num_entries(self):
        return self.iter_n_children(None)
    
    def remove_old_songs(self, count = 4):
        removing = []
        if (self.get_num_entries() < count):
            return
        iter = self.get_iter_first()
        entry = self.iter_to_entry(iter)
        removing.append(entry)
        for i in range(count - 1):
            iter = self.iter_next(iter)
            entry = self.iter_to_entry(iter)
            removing.append(entry)
            
        #Remove from the model
        for removing_entry in removing:
            print "Removing Song %s" % (self.__db.entry_get(removing_entry, rhythmdb.PROP_TITLE))
            url = removing_entry.get_playback_uri()
            del self.__songs_dict[url]
            self.remove_entry(removing_entry)
            self.__db.entry_delete(removing_entry)
        self.__db.commit()
    
    def clear(self):
        self.remove_old_songs(self.get_num_entries())
        
    #HACK around Python's QueryModel binding problem 
    def iter_to_entry(self, iter):
        db = self.__db
        id = self.get(iter, 0)[0]
        if not id:
            raise Exception('Bad id' + id)
  
        eid = db.entry_get(id, rhythmdb.PROP_ENTRY_ID)
        if not eid:
            raise Exception('Bad eid' + eid)
  
        entry = db.entry_lookup_by_id(eid)
  
        if not entry:
            raise Exception('iter_to_entry: bad entry ' + repr(eid) + ' ' + repr(id))

        return entry