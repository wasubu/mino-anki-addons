# AlwaysOnTop
# Copyright (C) Damien Elmes 2009 <anki@ichi2.net>
#   https://github.com/ankitects/anki-addons/blob/690d552ae1ccafe0469684b9ef8198752da90724/alwaysontop.py
# Copyright (C) Glutanimate 2017 <github.com/glutanimate>
#   https://github.com/glutanimate/anki-addons-dae/blob/all-windows-on-top/alwaysontop.py
# Copyright (C) Unknow 2019 <https://ankiweb.net/shared/info/1760080335>
# Copyright (C) Shigeyuki 2025 <http://patreon.com/Shigeyuki>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .manually_config import check_v2_enable
from .shige_config.popup_config import set_gui_hook_change_log

if check_v2_enable():
    from .always_on_top_v2 import set_hooks
    set_hooks()
else:
    from . import always_on_top_v1

set_gui_hook_change_log()


