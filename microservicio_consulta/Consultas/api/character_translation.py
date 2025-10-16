
character_translation = {
    1339: "Young Link",
    1275: "Cloud",
    1302: "Mario",
    1532: "Terry",
    1406: "Incineroar",
    1285: "Falco",
    1328: "Samus",
    1321: "Pokemon Trainer",
    1279: "Diddy Kong",
    1282: "Doctor Mario",
    1314: "Olimar",
    1338: "Yoshi",
    1326: "Roy",  
    1304: "Marth",  
    1286: "Fox",
    1292: "King Dedede",
    1795: "Pyra & Mythra",
    1273: "Bowser",
    1323: "R.O.B.",
    1295: "Kirby",
    1412: "Ritcher",
    1327: "Ryu",
    1410: "Ken",
    1311: "Mii Brawler",
    1777: "Sephiroth",    
    1299: "Ness",
    1313: "Lucas",
    1337: "Wolf",
    1335: "Wario",
    1293: "Jigglypuff", 
    1407: "King K. Rool",
    
    # Agrega más traducciones aquí
}

def get_character_name(character_id):
    return character_translation.get(character_id, "Unknown Character")
