#set page(
    "us-letter",
    margin: 1cm
)
#show title: set align(center)
#set document(
    title: [
        Megadungeon of the Mad Archmage Gary-Stu, Level 5: Crypt
    ]
)
#set text(
    font: "Helvetica Neue",
    weight: "light",
    size: 8pt
)
#set par(
    leading: 0.3em
)
#set heading(numbering: "1.")
#title()
#grid(
    columns: (69%, 2%, 28%),
    grid.cell(
        image(
            "/Users/adam/git/svgmapper/examples/svg/crypt.svg",
             width: 100%
        )
    ),
    grid.cell([]),
    grid.cell(
        [
                #set par(leading: 0.1em)
                *Wandering Monsters*\
                Check every 20 minutes, 1 in 8 chance; then d12:
                1-4. Wraith of character previously slain in dungeon. Causes level drain. Silver or magic weapon to hit.
                5. 1d3 ghouls. Cause paralysis.
                6-7. 1d8 skeleton warriors armed with scimitars.
                8-9. 1d6 zombies with clubs and claws.
                10. 1 wight. Causes level drain. Silver or magic weapon to hit.
                11. Abbot Yorick (see below)
                12. Carlotta (see below)

                *Legend*
                - *S*: Secret door.

                *Subtable A*: Quasqueton Room
                #set enum(numbering: "a")
                + cool water
                + illusory bottom, 30' drop to next level
                + murky water hides angry viper
                + treasure pool with gold and silver
                + firewater: belch flame or hold it in and explode
                + green slime
                + dimensional portal
                + acid pool with gold-plated key at bottom (no matching door)
                + boiling water
                + lair of water weird
                + fake dry pool: looks dry, holds tepid water
                + healing pool, one drink/character/day
                + living, pulsing entrails. Edible (ew!)
                + cold lager
                + blink juice: next five hits received may cause short-range teleport instead of damage
        ]
    )
)
*Room Key*
#set enum(numbering: "1.")
+ *Grand Stairway*: up to surface, down to level 8. Ceilings generally 10' high.
+ *Halls of Bone*: each room has 10 skeleton warriors armed with crossbows behind the iron lattices indicated by dots.
+ *Zombocalypse*: 25 Zombies ("Z"). Appear to be corpses until one of the dotted lines "b" is crossed, then all animate at once. Ruined fountain at "a" with a little silver coinage, some copper coins, rusted _magical dagger_.
+ *Hall of Shadows*: check at each of a-e. Torchlight or less: 4 in 6, lantern 3/6, _Magical Light_ 2/6, of a shadow appearing and attacking. Drains strength.
+ *Catwalk*: Dark Knight (strong skeletal warrior, turn as ghoul) guards bridges, attacks with greatsword. If struck, target may fall in pit to next level (30' fall).  Ceiling is 16' high.
+ *Barrows*: Wights drain levels. A: Wightsnake (4 platinum albums, constrict), B: Wighty Ford (4 world series rings, ranged attack (baseball)), C: Barry Wight (5 gold albums, 5 platinum albums, can charm), D: Great Wight ("Are you ready to rock, Rhode Island?" then self-immolates with fireball, half-melted gold album), E: Wight Zombie (2 platinum albums, dreadlocks, scary eyes). No entry to shaft in column from this level.
+ *Winding Corridor*: nothing special, but roll dice at each corner, purse your lips, and shake your head sadly.
+ *Quasqueton Room*: 15 pools. See subtable A or use Room 31 from B1 if you have it. Domed ceiling is 10' at walls, 16' in center.
+ *Secret Armory*: _magical sqord_, silver-plated warhammer, _magical bracers_.
+ *Unholy Church*: altar at "a", 2 gargoyles attack with horns and claws. Altar furnishings and 3 fairly valuable gems. Spiral staircase down. 16' ceiling.
+ *Parlor*: Comfy couches, bookshelves (books mostly lurid vampire romances). 25% chance Carlotta is here, reading.
+ *Carlotta's Lair*: home to Carlotta the Vampire (75% chance at home). Her bite drains levels. Magic/silver weapons to hit. Can take gaseous or bat form, cannot cross running water, only stays dead with stake through heart, etc. Coffin contains delicately scented scarlet silk pillow, dirt from homeland (local, so stealing it just pisses her off), jade erotic clockwork appurtenance worth a lot to a discerning buyer. Room contains stylish and expensive garments, potion of Giant Strength, Ruby of True Vision, a bit of platinum and gold coinage, and valuable gold jewelry.
+ *Cloister*: 25% chance of encountering Abbot Yorick here.
+ *Kitchen*: Kobold _chef de cuisine_ and 3 halfling line cooks armed with knives. Various foodstuffs.
+ *Kitchen Staff Dormitory*: 3 bottles of cheap wine, a few copper and silver coins, girlie magazines.
+ *Yorick's Cell*: 50% chance of encountering Abbot Yorick, midlevel Evil Priest, here. Wears _magical plate mail_ and _magical shield_, attacks with _magical mace_ or any appropriate priestly spell. Carries some silver coins and an unholy symbol.
+ *Treasury*: 25% chance Abbot Yorick is here. Lots of gold and platinum coins, 6 valuable gems, _Flying Carpet_, _magical dagger "Goblin-bane"_.
+ *Lawn*: Stone tree trunks at "t" ascend to 16' ceiling. Central one has Assassin Vine, which grabs and constricts.
+ *Stairs*: 19-21 are a separate lair not reachable from this level except via teleportation, magical wall-tunneling, or similar.  12' ceilings.
+ *Dining Room*: 30% chance Edgar is here.  Table settings are valuable, bulk, and fragile.
+ *Study/Bedroom*: 70% chance Edgar is here. Edgar, Ogre Mage: attacks with large scimitar, can _fly_, turn _invisible_, _create darkness_, _sleep_, _charm_, _icy blast_. Carries a little platinum, some gold, and a _portable hole_.
+ *Churchyard*: Each crypt "b" holds a ghoul: claws paralyse, stench nauseates for 1-3 minutes.  Crypt "a" holds a ghast (like ghoul but stronger).
+ *Egyptian Temple*: 2 cobras: bite paralyzes immediately/die in 1-3 minutes, spit poison.
+ *Temple Maze*: traps at a) swinging bladed pendulum, b) giant grinding rollers under illusory floor, c) north and south walls slam together, d) sleep gas released, e) corridor pivots longitudinally around centerline dumping party 30' into level below, f) floor-and-ceiling spear trap.
+ *Mummy's Crypt*: Mummy. Vulnerable to fire. Touch causes horrible rotting disease. Gold sarcophagus, scepter, crown.
+ *Toilet*.