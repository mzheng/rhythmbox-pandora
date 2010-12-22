import rhythmdb

class StationsModel(rhythmdb.QueryModel):
    def __init__(self, db, entry_type):
        rhythmdb.QueryModel.__init__(self)
        self.__db = db
        self.__entry_type = entry_type
        self.__stations_dict = {}
        
        
    def add_station(self, station, name, pos=-1):
        url = station.info_url
        entry = self.__db.entry_new(self.__entry_type, url)
        self.__db.set(entry, rhythmdb.PROP_TITLE, name) 
        
        self.add_entry(entry, pos)
        self.__stations_dict[url] = station
        
        return entry
    
    def get_station(self, url):
        print "Number of stations: %d" %(len(self.__stations_dict))
        return self.__stations_dict[url] 
    
    def delete_station(self, url):
        entry = self.__db.entry_lookup_by_location(url)
        self.__db.entry_delete(entry)
        self.remove_entry(entry)
        del self.__stations_dict[url]
        
    def clear(self):
        for url in self.__stations_dict.keys():
            entry = self.__db.entry_lookup_by_location(url)
            self.__db.entry_delete(entry)
            self.remove_entry(entry)
        self.__stations_dict.clear()
    
    def get_num_entries(self):
        return self.iter_n_children(None)
    
    # Get the first station after "QuickMix"
    def get_first_station(self):
        iter = self.get_iter_first()
        #iter = self.iter_next(iter)
        entry = self.iter_to_entry(iter)
        return entry
        
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