# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 14:10:46 2025

@author: e2201445
"""
import json
import hashlib
dico={}

file = "H:\SAE601_2025\data_collection\output\67a0a9543b814c326f970c20.json"
def hashage(player_id):
    return hashlib.sha256(player_id.encode()).hexdigest()[:8]

dico = {}

with open(file, 'r+') as f:
    tournament = json.load(f)

    for player in tournament['players']:
        original_id = player['id']
        if original_id not in dico:
            anonymisation_id = hashage(original_id)
            dico[original_id] = anonymisation_id
        player['id'] = dico[original_id]

    for match in tournament["matches"]:
        for result in match["match_results"]:
            original_player_id = result["player_id"]
            if original_player_id not in dico:
                dico[original_player_id] = hashage(original_player_id)
            result["player_id"] = dico[original_player_id]

    f.seek(0)         
    f.truncate()     
    json.dump(tournament, f, indent=2)  
print(dico)

        





