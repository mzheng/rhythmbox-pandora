import gtk
def NewDeleteDialog(plugin):
    ui_filename = plugin.find_file("pandora/DeleteDialog.ui")

    builder = gtk.Builder()
    builder.add_from_file(ui_filename)    
    dialog = builder.get_object("delete_confirm_dialog")
    return dialog