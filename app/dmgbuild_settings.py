
import os.path
import re

import biplist

# .. Useful stuff ..............................................................

APP = "pypolona"
GUI = "PyPolona"
CLI = "ppolona"


def get_version(*args):
    ver = ""
    verstrline = open(os.path.join("..", APP, "__init__.py")).read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        ver = mo.group(1)
    return ver


application = defines.get("app", os.path.join("build", "dist-mac", f"{GUI}.app")) # type: ignore[name-defined]
appname = os.path.basename(application)


def icon_from_app(app_path):
    plist_path = os.path.join(app_path, "Contents", "Info.plist")
    plist = biplist.readPlist(plist_path)
    icon_name = plist["CFBundleIconFile"]
    icon_root, icon_ext = os.path.splitext(icon_name)
    if not icon_ext:
        icon_ext = ".icns"
    icon_name = icon_root + icon_ext
    return os.path.join(app_path, "Contents", "Resources", icon_name)


# .. Basics ....................................................................

filename = os.path.join("..", "download", f"{APP}-mac.dmg")
volume_name = f"{GUI} {get_version()}" # type: ignore[name-defined]

# Volume format (see hdiutil create -help)
format = defines.get("format", "UDBZ") # type: ignore[name-defined]

# Volume size
size = defines.get("size", None) # type: ignore[name-defined]

# Files to include
files = [application]

# Symlinks to create
symlinks = {"Applications": "/Applications"}

# Volume icon
#
# You can either define icon, in which case that icon file will be copied to the
# image, *or* you can define badge_icon, in which case the icon file you specify
# will be used to badge the system's Removable Disk icon.
badge_icon = icon_from_app(application)

# Where to put the icons
icon_locations = {appname: (140, 120), "Applications": (500, 120)}

# .. Window configuration ......................................................

# Background: Use 'builtin-arrow' or specify a custom image/color.
# For more details on background options, see dmgbuild documentation.
background = "builtin-arrow"

show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# Window position in ((x, y), (w, h)) format
window_rect = ((100, 100), (640, 280))

# Select the default view; must be one of
#
#    'icon-view'
#    'list-view'
#    'column-view'
#    'coverflow'
#
default_view = "icon-view"

# General view configuration
show_icon_preview = False

# Set these to True to force inclusion of icon/list view settings (otherwise
# we only include settings for the default view)
include_icon_view_settings = "auto"
include_list_view_settings = "auto"

# .. Icon view configuration ...................................................

arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = "bottom"  # or 'right'
text_size = 16
icon_size = 128

# .. List view configuration ...................................................
# These settings are for the list view, if selected as default_view or if
# include_list_view_settings is True. Refer to dmgbuild docs for details.
list_icon_size = 16
list_text_size = 12
list_scroll_position = (0, 0)
list_sort_by = "name"
list_use_relative_dates = True
list_calculate_all_sizes = (False,)
list_columns = ("name", "date-modified", "size", "kind", "date-added")
list_column_widths = {
    "name": 300,
    "date-modified": 181,
    "date-created": 181,
    "date-added": 181,
    "date-last-opened": 181,
    "size": 97,
    "kind": 115,
    "label": 100,
    "version": 75,
    "comments": 300,
}
list_column_sort_directions = {
    "name": "ascending",
    "date-modified": "descending",
    "date-created": "descending",
    "date-added": "descending",
    "date-last-opened": "descending",
    "size": "descending",
    "kind": "ascending",
    "label": "ascending",
    "version": "ascending",
    "comments": "ascending",
}

# .. License configuration .....................................................
# License configuration is not used by PyPolona.
# For details on how to set this up, see dmgbuild documentation.
# license = { ... }
