import rhythmdb

class SongsModel(rhythmdb.QueryModel):
    def __init__(self, db, entry_type):
        rhythmdb.QueryModel.__init__(self)
        self.__db = db
        self.__entry_type = entry_type
        self.__last_entry = None
    
    def add_song(self, song, duration=None):
        entry = self.__db.entry_new(self.__entry_type, song.audioUrl)
        self.__db.set(entry, rhythmdb.PROP_TITLE, song.title)
        self.__db.set(entry, rhythmdb.PROP_ARTIST, song.artist)
        self.__db.set(entry, rhythmdb.PROP_ALBUM, song.album)
        if duration != None:
            self.__db.set(entry, rhythmdb.PROP_DURATION, duration/1000000000)
        self.__db.commit()
        self.add_entry(entry, -1)
        self.__last_entry = entry
        return entry
        
    def is_last_entry(self, entry):
        return self.__last_entry == entry