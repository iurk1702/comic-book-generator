"""
Character database with predefined comic book characters and role definitions.
"""
# Role options for character assignment
CHARACTER_ROLES = [
    "main character 1",
    "main character 2", 
    "side character 1",
    "side character 2",
    "main villain 1",
    "main villain 2",
    "supporting character 1",
    "supporting character 2",
    "mentor",
    "ally",
    "neutral character",
    "background character"
]

# Predefined comic book characters database
PREDEFINED_CHARACTERS = {
    # Marvel Characters
    "Iron Man": {
        "description": "Tony Stark, a genius billionaire inventor in a high-tech red and gold powered armor suit with arc reactor chest piece",
        "visual_traits": "red and gold armor, arc reactor on chest, helmet with glowing eyes, repulsor beams"
    },
    "Captain America": {
        "description": "Steve Rogers, a super-soldier with enhanced strength and agility, wearing a red, white, and blue costume with a star on chest and shield",
        "visual_traits": "red white blue costume, star on chest, circular shield, A on helmet"
    },
    "Spider-Man": {
        "description": "Peter Parker, a young hero with spider-like abilities, wearing a red and blue spandex suit with web patterns and spider symbol",
        "visual_traits": "red and blue suit, web patterns, spider symbol on chest, white eye lenses"
    },
    "Hulk": {
        "description": "Bruce Banner transformed into a massive green-skinned muscular giant with incredible strength",
        "visual_traits": "green skin, massive muscular build, torn purple pants, angry expression"
    },
    "Thor": {
        "description": "God of Thunder with long blonde hair, red cape, and wielding the mystical hammer Mjolnir",
        "visual_traits": "blonde long hair, red cape, silver armor, Mjolnir hammer, helmet with wings"
    },
    "Black Widow": {
        "description": "Natasha Romanoff, a highly skilled spy and assassin with red hair, wearing a black tactical suit",
        "visual_traits": "red hair, black tactical suit, widow's bite gauntlets, athletic build"
    },
    "Wolverine": {
        "description": "Logan, a mutant with retractable adamantium claws, sideburns, and a gruff appearance",
        "visual_traits": "sideburns, adamantium claws, yellow and blue costume, gruff face, short stature"
    },
    "Doctor Strange": {
        "description": "Master of the mystic arts with a red cape, gray hair, and mystical artifacts",
        "visual_traits": "gray hair with white streaks, red cape, Eye of Agamotto amulet, mystical symbols"
    },
    "Black Panther": {
        "description": "T'Challa, king of Wakanda, wearing a sleek black vibranium suit with panther motifs",
        "visual_traits": "black suit, panther mask, vibranium claws, purple energy effects"
    },
    "Captain Marvel": {
        "description": "Carol Danvers, a powerful hero with energy-based powers, wearing a red, blue, and gold suit",
        "visual_traits": "red blue gold suit, star symbol, short blonde hair, glowing energy aura"
    },
    "Deadpool": {
        "description": "Wade Wilson, a wisecracking mercenary in a red and black suit with mask covering scarred face",
        "visual_traits": "red and black suit, full face mask, dual katanas, chimichanga references"
    },
    "Storm": {
        "description": "Ororo Munroe, a mutant with weather control powers, white hair, and regal presence",
        "visual_traits": "white hair, white eyes, flowing cape, weather effects around her"
    },
    "Magneto": {
        "description": "Master of magnetism wearing a red and purple helmet and cape, controlling metal",
        "visual_traits": "red purple helmet, cape, gray hair, metal manipulation powers"
    },
    "Loki": {
        "description": "God of Mischief with black hair, green and gold Asgardian armor, and a horned helmet",
        "visual_traits": "black hair, green gold armor, horned helmet, mischievous smile, daggers"
    },
    "Thanos": {
        "description": "A massive purple-skinned titan with a golden gauntlet, seeking to balance the universe",
        "visual_traits": "purple skin, massive build, golden gauntlet, chin ridges, armor"
    },
    
    # DC Characters
    "Batman": {
        "description": "Bruce Wayne, a dark vigilante in a black cape and cowl with bat symbol, using gadgets and martial arts",
        "visual_traits": "black cape and cowl, bat symbol on chest, utility belt, pointy ears, dark and brooding"
    },
    "Superman": {
        "description": "Clark Kent, the Man of Steel with blue suit, red cape, and S shield, symbol of hope",
        "visual_traits": "blue suit, red cape, S shield, black hair with curl, flying pose"
    },
    "Wonder Woman": {
        "description": "Diana Prince, an Amazon warrior princess with red, blue, and gold armor, wielding a lasso and shield",
        "visual_traits": "red blue gold armor, tiara, lasso of truth, shield, dark hair"
    },
    "The Flash": {
        "description": "Barry Allen, the fastest man alive in a red suit with lightning bolt symbol and yellow boots",
        "visual_traits": "red suit, lightning bolt symbol, yellow boots, speed lines, lightning effects"
    },
    "Green Lantern": {
        "description": "Hal Jordan, a space cop wielding a power ring that creates green energy constructs",
        "visual_traits": "green suit, black mask, power ring, green energy constructs, symbol on chest"
    },
    "Aquaman": {
        "description": "Arthur Curry, king of Atlantis with blonde hair, orange and green suit, wielding a trident",
        "visual_traits": "blonde hair, orange green suit, trident, scales, water effects"
    },
    "Green Arrow": {
        "description": "Oliver Queen, a skilled archer in a green hood with goatee, using trick arrows",
        "visual_traits": "green hood, goatee, bow and arrows, quiver, athletic build"
    },
    "Joker": {
        "description": "The Clown Prince of Crime with green hair, white skin, red lips, and purple suit",
        "visual_traits": "green hair, white skin, red lips, purple suit, maniacal laugh, playing cards"
    },
    "Harley Quinn": {
        "description": "Former psychiatrist turned villain with red and black jester outfit and pigtails",
        "visual_traits": "red black jester suit, pigtails, white face paint, mallet, playful expression"
    },
    "Lex Luthor": {
        "description": "Bald genius billionaire in a business suit or power armor, Superman's arch-nemesis",
        "visual_traits": "bald head, business suit or green power armor, calculating expression"
    },
    "Catwoman": {
        "description": "Selina Kyle, a skilled thief in a black catsuit with cat ears and whip",
        "visual_traits": "black catsuit, cat ears, whip, goggles, athletic and agile"
    },
    "Robin": {
        "description": "Batman's young sidekick in a red, green, and yellow costume with cape",
        "visual_traits": "red green yellow costume, cape, mask, young appearance, acrobatic"
    },
    "Nightwing": {
        "description": "Former Robin, now independent hero in a blue and black suit with bird symbol",
        "visual_traits": "blue black suit, bird symbol, no cape, acrobatic, escrima sticks"
    },
    "The Riddler": {
        "description": "Edward Nygma, a criminal mastermind obsessed with riddles, wearing green suit with question marks",
        "visual_traits": "green suit, question marks, bowler hat, cane, green mask"
    },
    "Two-Face": {
        "description": "Harvey Dent, a former district attorney with half-scarred face, using a two-headed coin",
        "visual_traits": "half-scarred face, two-tone suit, coin, dual personality"
    },
    "Poison Ivy": {
        "description": "Pamela Isley, an eco-terrorist with plant control powers, green skin and red hair",
        "visual_traits": "green skin, red hair, plant-themed costume, vines, seductive"
    },
    "Bane": {
        "description": "A massive masked villain with super strength, wearing a mask with tubes",
        "visual_traits": "massive build, mask with tubes, venom tubes, tactical gear"
    },
    "Darkseid": {
        "description": "A god-like tyrant with gray skin, red eyes, and Omega Beams",
        "visual_traits": "gray skin, red eyes, armor, Omega symbol, massive and imposing"
    },
    
    # Additional Popular Characters
    "Wolverine": {
        "description": "Logan, a mutant with retractable adamantium claws, sideburns, and a gruff appearance",
        "visual_traits": "sideburns, adamantium claws, yellow and blue costume, gruff face"
    },
    "Venom": {
        "description": "A black symbiote suit with white spider symbol, sharp teeth, and elongated tongue",
        "visual_traits": "black suit, white spider symbol, sharp teeth, elongated tongue, massive build"
    },
    "Doctor Octopus": {
        "description": "Otto Octavius, a scientist with four mechanical tentacle arms attached to his body",
        "visual_traits": "four mechanical tentacles, green yellow suit, round glasses, bald with mustache"
    },
    "The Punisher": {
        "description": "Frank Castle, a vigilante with a white skull symbol on black tactical gear",
        "visual_traits": "white skull symbol, black tactical gear, weapons, grim expression"
    },
    "Gambit": {
        "description": "Remy LeBeau, a Cajun mutant with brown hair, trench coat, and kinetic energy powers",
        "visual_traits": "brown hair, trench coat, playing cards, red eyes, staff"
    },
    "Rogue": {
        "description": "A southern mutant with white streak in brown hair, green and yellow suit, touch-based powers",
        "visual_traits": "brown hair with white streak, green yellow suit, gloves, southern accent"
    },
    "Cyclops": {
        "description": "Scott Summers, leader of X-Men with red visor and optic blast powers",
        "visual_traits": "red visor, blue yellow X-Men suit, X symbol, controlled expression"
    },
    "Jean Grey": {
        "description": "A powerful telepath and telekinetic with red hair and Phoenix powers",
        "visual_traits": "red hair, green yellow suit, telekinetic aura, Phoenix effects"
    },
    "Professor X": {
        "description": "Charles Xavier, a powerful telepath in a wheelchair, founder of X-Men",
        "visual_traits": "bald head, wheelchair, suit, calm expression, telepathic"
    },
    "Mystique": {
        "description": "A blue-skinned shape-shifter with red hair and yellow eyes",
        "visual_traits": "blue skin, red hair, yellow eyes, scales, shape-shifting"
    },
    "Sabretooth": {
        "description": "Victor Creed, a feral mutant with claws, fangs, and animal-like features",
        "visual_traits": "long hair, fangs, claws, animal features, yellow eyes, feral"
    },
    "Silver Surfer": {
        "description": "A silver-skinned cosmic being on a surfboard, herald of Galactus",
        "visual_traits": "silver skin, surfboard, cosmic powers, sleek appearance"
    },
    "Galactus": {
        "description": "A massive cosmic entity in purple and blue armor, devourer of worlds",
        "visual_traits": "massive size, purple blue armor, helmet, cosmic powers"
    },
    "Doctor Doom": {
        "description": "Victor Von Doom, ruler of Latveria in green metal armor and hood",
        "visual_traits": "green metal armor, hood, mask, cape, mystical and tech powers"
    },
    "Red Skull": {
        "description": "Johann Schmidt, a Nazi villain with a red skull face",
        "visual_traits": "red skull face, Nazi uniform, sinister expression"
    },
    "Ultron": {
        "description": "An AI robot with red glowing eyes and metallic body",
        "visual_traits": "metallic body, red glowing eyes, robotic, menacing"
    },
    "Vision": {
        "description": "A synthezoid with red face, yellow gem on forehead, and cape",
        "visual_traits": "red face, yellow gem, green yellow suit, cape, synthetic"
    },
    "Scarlet Witch": {
        "description": "Wanda Maximoff, a powerful mutant with reality-warping powers, red costume",
        "visual_traits": "red costume, headpiece, reality-warping effects, red energy"
    },
    "Quicksilver": {
        "description": "Pietro Maximoff, a speedster with silver hair and blue suit",
        "visual_traits": "silver hair, blue suit, speed lines, super speed"
    },
    "Ant-Man": {
        "description": "Scott Lang, a hero who can shrink and grow, wearing red and black suit",
        "visual_traits": "red black suit, helmet, size-changing powers"
    },
    "Wasp": {
        "description": "Hope van Dyne, a hero with wings and size-changing powers, yellow and black suit",
        "visual_traits": "yellow black suit, wings, size-changing, stinger blasts"
    },
    "Hawkeye": {
        "description": "Clint Barton, a master archer with purple suit and bow",
        "visual_traits": "purple suit, bow and arrows, quiver, athletic"
    },
    "Black Widow": {
        "description": "Natasha Romanoff, a highly skilled spy and assassin with red hair, wearing a black tactical suit",
        "visual_traits": "red hair, black tactical suit, widow's bite gauntlets"
    },
    "Falcon": {
        "description": "Sam Wilson, a hero with mechanical wings and red white suit",
        "visual_traits": "mechanical wings, red white suit, goggles, flight"
    },
    "Winter Soldier": {
        "description": "Bucky Barnes, a former assassin with metal arm and tactical gear",
        "visual_traits": "metal arm, tactical gear, long hair, mask, weapons"
    },
    "Star-Lord": {
        "description": "Peter Quill, leader of Guardians with red mask and blasters",
        "visual_traits": "red mask, jacket, blasters, walkman, space adventurer"
    },
    "Gamora": {
        "description": "A green-skinned assassin with sword and tactical suit",
        "visual_traits": "green skin, sword, tactical suit, assassin"
    },
    "Drax": {
        "description": "A massive warrior with gray skin and tattoos seeking revenge",
        "visual_traits": "gray skin, massive build, tattoos, knives, warrior"
    },
    "Rocket Raccoon": {
        "description": "A genetically engineered raccoon with cybernetic enhancements and guns",
        "visual_traits": "raccoon appearance, cybernetic, guns, small size, snarky"
    },
    "Groot": {
        "description": "A tree-like alien with limited vocabulary, can grow and regenerate",
        "visual_traits": "tree-like, brown bark, branches, limited speech, regenerative"
    },
    "Nebula": {
        "description": "A cyborg assassin with blue skin and cybernetic enhancements",
        "visual_traits": "blue skin, cybernetic parts, bald, assassin, blue"
    },
    "Mantis": {
        "description": "An empath with antennae and green skin, can sense emotions",
        "visual_traits": "green skin, antennae, empathic powers, gentle"
    },
    "Shazam": {
        "description": "Billy Batson transformed into an adult hero with red suit and lightning powers",
        "visual_traits": "red suit, cape, lightning symbol, adult form, magic"
    },
    "Black Adam": {
        "description": "An anti-hero with black suit and lightning powers, ancient Egyptian origin",
        "visual_traits": "black suit, lightning powers, ancient, powerful, anti-hero"
    },
    "Supergirl": {
        "description": "Kara Zor-El, Superman's cousin with similar powers, red blue suit with skirt",
        "visual_traits": "red blue suit, skirt, S symbol, blonde hair, flying"
    },
    "Batgirl": {
        "description": "Barbara Gordon, a skilled fighter in a purple and yellow bat-themed suit",
        "visual_traits": "purple yellow suit, bat symbol, cape, tech-savvy"
    },
    "Red Hood": {
        "description": "Jason Todd, a vigilante with red helmet and dual pistols",
        "visual_traits": "red helmet, black suit, dual pistols, aggressive"
    },
    "Deathstroke": {
        "description": "Slade Wilson, a master assassin with orange and black mask and sword",
        "visual_traits": "orange black mask, sword, tactical gear, one eye, assassin"
    },
    "Ra's al Ghul": {
        "description": "An immortal mastermind with long life, green robes, and sword",
        "visual_traits": "green robes, sword, ancient, mastermind, Lazarus Pit"
    },
    "Scarecrow": {
        "description": "Jonathan Crane, a villain using fear gas, wearing a burlap sack mask",
        "visual_traits": "burlap sack mask, fear gas, tattered clothes, psychological"
    },
    "Penguin": {
        "description": "Oswald Cobblepot, a crime boss with penguin-like appearance and umbrella",
        "visual_traits": "short stature, top hat, monocle, umbrella, penguin-like"
    },
    "Mr. Freeze": {
        "description": "Victor Fries, a scientist in a cryogenic suit with freeze gun",
        "visual_traits": "blue suit, helmet, freeze gun, cold powers, tragic"
    },
    "Killer Croc": {
        "description": "Waylon Jones, a mutant with crocodile-like features and super strength",
        "visual_traits": "crocodile skin, massive build, claws, reptilian features"
    },
    "Harley Quinn": {
        "description": "Former psychiatrist turned villain with red and black jester outfit and pigtails",
        "visual_traits": "red black jester suit, pigtails, white face paint, mallet"
    },
    "Zatanna": {
        "description": "A magician with top hat, fishnets, and backwards-spoken spells",
        "visual_traits": "top hat, fishnets, stage magician outfit, magic spells"
    },
    "Constantine": {
        "description": "John Constantine, a chain-smoking occult detective with trench coat",
        "visual_traits": "trench coat, blonde hair, cigarette, occult detective, British"
    },
    "Swamp Thing": {
        "description": "A plant elemental with moss and vegetation covering his body",
        "visual_traits": "plant body, moss, vegetation, green, nature powers"
    },
    "Hellboy": {
        "description": "A demon with red skin, filed-down horns, and Right Hand of Doom",
        "visual_traits": "red skin, filed horns, Right Hand of Doom, tail, supernatural"
    },
    "Spawn": {
        "description": "Al Simmons, a hellspawn with cape, chains, and necroplasmic powers",
        "visual_traits": "black suit, cape, chains, mask, hellspawn, dark"
    },
    "The Crow": {
        "description": "Eric Draven, an undead vigilante with white face paint and black outfit",
        "visual_traits": "white face paint, black outfit, undead, gothic, tragic"
    },
    "Judge Dredd": {
        "description": "A law enforcement officer in futuristic armor with helmet covering face",
        "visual_traits": "helmet, armor, badge, law enforcement, futuristic"
    },
    "The Tick": {
        "description": "A blue superhero with antennae and naive personality",
        "visual_traits": "blue suit, antennae, massive build, naive, comedic"
    },
    "Invincible": {
        "description": "Mark Grayson, a young hero with blue and yellow suit, son of Omni-Man",
        "visual_traits": "blue yellow suit, young, flying, super strength, coming of age"
    },
    "Omni-Man": {
        "description": "Nolan Grayson, a powerful Viltrumite with mustache and red suit",
        "visual_traits": "red suit, mustache, powerful, Viltrumite, complex"
    },
    "Atom Eve": {
        "description": "Samantha Eve Wilkins, a hero with matter manipulation and pink energy",
        "visual_traits": "pink energy, matter manipulation, young, powerful"
    },
    "Robot": {
        "description": "Rudy Connors, a genius in a robot body with advanced technology",
        "visual_traits": "robot body, advanced tech, genius, strategic"
    },
    "Allen the Alien": {
        "description": "A large alien with green skin and friendly personality",
        "visual_traits": "green skin, large build, friendly, alien, strong"
    },
    "Battle Beast": {
        "description": "A massive warrior alien with lion-like features and battle armor",
        "visual_traits": "lion features, massive, battle armor, warrior, fierce"
    },
    "The Immortal": {
        "description": "An ancient hero with long life and classic superhero appearance",
        "visual_traits": "classic hero look, long life, experienced, powerful"
    },
    "Darkwing": {
        "description": "A hero with dark suit and cape, similar to Batman",
        "visual_traits": "dark suit, cape, vigilante, dark and brooding"
    },
    "Rex Splode": {
        "description": "A hero with explosive powers and reckless personality",
        "visual_traits": "explosive powers, reckless, young, energetic"
    },
    "Dupli-Kate": {
        "description": "A hero who can create multiple copies of herself",
        "visual_traits": "duplication powers, multiple selves, young, team member"
    },
    "Shrinking Rae": {
        "description": "A hero who can shrink to tiny size",
        "visual_traits": "shrinking powers, small size, young, team member"
    }
}

def get_character_list():
    """Get sorted list of all character names."""
    return sorted(PREDEFINED_CHARACTERS.keys())

def get_character_info(character_name: str):
    """Get character information by name."""
    return PREDEFINED_CHARACTERS.get(character_name, None)

def get_roles():
    """Get list of available roles."""
    return CHARACTER_ROLES.copy()

