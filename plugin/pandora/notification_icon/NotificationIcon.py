import gtk
class NotificationIcon:
    def __init__(self, plugin, songs_action):
	self.plugin = plugin
	self.songs_action = songs_action
	icon_file = 'pandora/notification_icon/pandora.png'
	self.tray_icon = TrayIcon(self.plugin.find_file(icon_file))
	self.build_context_menu();
	#TODO: Disable actions when they're N/A
	#TODO: Hide when not applicable
    def build_context_menu(self):
	menu = self.tray_icon.popup
        def button(text, action, icon):
        	item = gtk.ImageMenuItem(text)
		image = gtk.image_new_from_stock(icon, gtk.ICON_SIZE_MENU)
        	item.set_image(image)
        	item.connect('activate', action) 
        	item.show()
        	menu.append(item)
		print "Added item"
        	return item
	# Action callbacks
	def love_song_callback(ignore):
		self.songs_action.love_current_song()
	def ban_song_callback(ignore):
		self.songs_action.ban_current_song()
	def tire_song_callback(ignore):
		self.songs_action.tire_current_song()
	button("_Love Song", love_song_callback, gtk.STOCK_ABOUT)
	button("_Ban Song", ban_song_callback, gtk.STOCK_CANCEL)
	button("_Tired of this song", tire_song_callback, gtk.STOCK_JUMP_TO)
        
	self.tray_icon.set_visible(True)
	
	#TODO: Clean up
	
class TrayIcon(gtk.StatusIcon):
    def __init__(self, iconfile):
        gtk.StatusIcon.__init__(self)
        self.set_from_file(iconfile)        
        self.popup = gtk.Menu()
        self.bpe_id = self.connect("button-press-event", self.icon_clicked)
        
    def icon_clicked(self, statusicon, event):
        self.popup.popup(None, None, gtk.status_icon_position_menu, event.button, event.time, self)
        
    def destroy(self):
        self.popup.destroy(); del self.popup
        self.disconnect(self.bpe_id);
