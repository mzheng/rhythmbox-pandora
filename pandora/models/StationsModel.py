import rhythmdb

class StationsModel(rhythmdb.QueryModel):
    def __init__(self, db, entry_type):
        rhythmdb.QueryModel.__init__(self)
        self.__db = db
        self.__entry_type = entry_type
        self.__stations_dict = {}
        
        
    def add_station(self, station, name):
        url = station.info_url
        entry = self.__db.entry_new(self.__entry_type, url)
        self.__db.set(entry, rhythmdb.PROP_TITLE, name) 
        
        self.add_entry(entry, -1)
        self.__stations_dict[url] = station
    
    def get_station(self, url):
        return self.__stations_dict[url] 
    
    def clear(self):
        for url in self.__stations_dict.keys():
            entry = self.__db.entry_lookup_by_location(url)
            self.__db.entry_delete(entry)
            self.remove_entry(entry)
        self.__stations_dict.clear()