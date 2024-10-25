<drac2>
TYPE = "Insect"
SPELL_NAME = "Giant Insect"
SPELL_DESC = "You summon a giant centipede, spider, or wasp (chosen when you cast the spell). It manifests in an unoccupied space you can see within range and uses the Giant Insect stat block. The form you choose determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n\nThe creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger."
MIN_LEVEL = 4

using(init_add="f48672c2-8f25-4170-ba39-d5f6ffd38bd3")

args = argparse(["-type"] + &ARGS&)
c = combat()
ch = character()
sab = ch.spellbook.sab
sdc = ch.spellbook.dc
true, false, null = True, False, None

warlock = ch.levels.get('Warlock')
min_slot = max(MIN_LEVEL, ((warlock >= 9) + (warlock >= 7) + (warlock >= 5) + (warlock >= 3) + 1))

if not (c and c.me):
  return f"""embed -title "Woopsie!" -desc "You're not in initiative!" """

open_b, close_b = "<"+"drac2"+">", "</"+"drac2"+">"
pf = ctx.prefix

spell_level = args.last('l', min_slot, int)
summon_type = args.last('type', "", str).lower()
ignore  = args.last('i')

stat_block = {
  "hp": 10 * spell_level - 10,
  "ac": 11 + spell_level,
  "pb": proficiencyBonus,
  "strength": 17,
  "dexterity": 13,
  "constitution": 15,
  "intelligence": 4,
  "wisdom": 14,
  "charisma": 3,
  "type": "beast",
}

attacks = [{"name":"Poison Jab","automation":[{"type":"target","target":"each","effects":[{"type":"attack","attackBonus":sab,"hit":[{"type":"damage","damage":f"1d6 + 3 + {spell_level} [piercing] + 1d4 [poison]"}],"miss":[],"adv":"0"}]},{"type":"text","text":"*Melee Weapon Attack:* your spell attack modifier to hit, reach 10 ft., one target. *Hit:* 1d6 + 3 + the spell's level Piercing damage plus 1d4 Poison damage."}],"_v":2,"verb":None,"proper":False,"activation_type":None}]
extra_effects = []
match summon_type:
  case "spider":
    attacks.extend([{"name":"Web Bolt ","automation":[{"type":"target","target":"each","effects":[{"type":"attack","attackBonus":sab,"hit":[{"type":"damage","damage":f"1d10 + 3 + {spell_level} [bludgeoning]"},{"type":"ieffect2","name":"Web Bolt","duration":1,"end":True,"desc":"Move reduced to 0"}],"miss":[],"adv":"0"}],"sortBy":None},{"type":"text","text":"*Ranged Attack Roll:* Bonus equals your spell attack modifier, range 60 ft. Hit: 1d10 + 3 plus the spell’s level Bludgeoning damage, and the target’s Speed is reduced to 0 until the start of the insect’s next turn."}],"_v":2,"verb":None,"proper":False,"activation_type":None}])
    summon_name = "Spider"
  case "centipede" | "cent" :
    attacks.extend([{"name":"Venomous Spew","automation":[{"type":"target","target":"each","effects":[{"type":"save","stat":"con","dc":sdc,"fail":[{"type":"ieffect2","name":"Poisoned","duration":1,"desc":"Poisoned until the start f {{caster.name}} next turn","tick_on_caster" : True ,"effects":{"attack_advantage":-1,"check_dis":["all"]}}],"success":[],"adv":0}]},{"type":"text","text":"Your spell save DC, one creature the insect can see within 10 feet. Failure: The target has the Poisoned condition until the start of the insect’s next turn."}],"_v":2,"verb":"takes","activation_type":3}])
    summon_name = "Centipede"
  case "wasp" :
    summon_name = "Wasp"
  case _:
    return f"""embed -title "Woopsie!" -desc "You didn't select a type!\n\nSelect from Ghostly, Putrid, or Skeletal." """

if not ignore:
  if not ch.spellbook.get_slots(spell_level):
    return f"""embed -title "Woopsie!" -desc "You don't have any slots left!" -f "Spell Slots|{ch.spellbook.slots_str(spell_level)}" """
  if not ch.spellbook.can_cast(SPELL_NAME, spell_level):
    return f"""embed -title "Woopsie!" -desc "You don't have that spell prepared!" """
  ch.spellbook.use_slot(spell_level)

custom_names = load_yaml(get('summon_names', '{}'))
s_name = args.last('name')
if s_name == 'reset':
  custom_names.pop(summon_name, None)
elif s_name:
  custom_names[summon_name] = s_name
ch.set_cvar('summon_names', dump_yaml(custom_names))
s_name = custom_names.get(summon_name, f"Summoned {summon_name} {TYPE} ({init_add.get_initials(name)})")

group_name = args.last('group', combat().me.group or f"{init_add.get_initials(name)}'s Summons")

stat_block['p'] = True
stat_block['group'] = group_name
stat_block['note'] = f"Summoned by {name}\nMultiattack: {max(1, spell_level//2)}"

c.me.set_group(group_name)
c.me.add_effect(f"Summon {TYPE}", concentration=True, duration=600)

embed_args = {
  "title": f"{name} summoned a {summon_name} {TYPE}!",
  "desc": SPELL_DESC,
  "fields": [{"title": "Spell Slots", "desc": f"{ch.spellbook.slots_str(spell_level)} {'(-1)' if not ignore else ''}"}],
  "footer": f"{ctx.prefix+ctx.alias} | Made by vaguely_happy",
  "color": color,
  "thumb": image
}

summon_command = init_add.build_init_add(s_name, c.me.init, stat_block)
embed = init_add.build_tembed(**embed_args, init_name=s_name, attacks=attacks, effect_name=f"Summon {TYPE}", extra_effects=extra_effects)

return f"""multiline
{summon_command}
{embed}
"""
</drac2>
