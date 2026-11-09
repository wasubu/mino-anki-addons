# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

import os
import json

def check_v2_enable():
    try:
        base_dir = os.path.dirname(__file__)
        meta_json = os.path.join(base_dir, "meta.json")
        if not os.path.exists(meta_json):
            return True

        with open(meta_json, "r", encoding="utf-8") as file:
            meta_config = json.load(file) or {}

        cofig = meta_config.get("config", {}) #type:dict

        return cofig.get("enable_v2", True)

    except Exception as e:
        print(f"[AlwaysOnTop] Error: {e}")
        return True



