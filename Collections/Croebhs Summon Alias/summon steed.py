<drac2>
TYPE = "Steed"
SPELL_NAME = "Find Steed"
SPELL_DESC = "You summon an otherworldly being that appears as a loyal steed in an unoccupied space of your choice within range. This creature uses the Otherworldly Steed stat block. If you already have a steed from this spell, the steed is replaced by the new one.The steed resembles a Large, rideable animal of your choice, such as a horse, a camel, a dire wolf, or an elk. \n\nWhenever you cast the spell, choose the steed’s creature type—Celestial, Fey, or Fiend—which determines certain traits in the stat block.\n\n**Combat.** The steed is an ally to you and your allies. In combat, it shares your Initiative count, and it functions as a controlled mount while you ride it (as defined in the rules on mounted combat). If you have the Incapacitated condition, the steed takes its turn immediately after yours and acts independently, focusing on protecting you.\n\n**Disappearance of the Steed.** The steed disappears if it drops to 0 Hit Points or if you die. When it disappears, it leaves behind anything it was wearing or carrying. If you cast this spell again, you decide whether you summon the steed that disappeared or a different one."
MIN_LEVEL = 2

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
  "hp": 5 + 10 * spell_level,
  "ac": 10 + spell_level,
  "pb": proficiencyBonus,
  "strength": 18,
  "dexterity": 12,
  "constitution": 14,
  "intelligence": 6,
  "wisdom": 12,
  "charisma": 8,
}

attacks = []
extra_effects = []
match summon_type:
  case "celestial" | "cel":
    attacks = [{"name":"Otherworldly Slam","automation":[{"type":"target","target":"each","effects":[{"type":"attack","attackBonus":sab,"hit":[{"type":"damage","damage":f"1d8 + 3 + {spell_level} [radiant]"}],"miss":[],"adv":"0"}]},{"type":"text","text":"*Melee Attack Roll:* Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 plus the spell’s level of Radiant (Celestial), Psychic (Fey), or Necrotic (Fiend) damage."}],"_v":2},{"name":"Healing Touch","automation":[{"type":"target","target":"self","effects":[{"type":"ieffect2","name":"Healing Touch Used","duration":-1,"stacking":True}]},{"type":"target","target":"each","effects":[{"type":"damage","damage":f"-(2d8 + {spell_level}) [heal]"}]},{"type":"text","text":"One creature within 5 feet of the steed regains a number of Hit Points equal to 2d8 plus the spell’s level."}],"_v":2,"verb":"reaches out with"}]
    summon_name = "Celestial Steed"
    TYPE = stat_block["type"] = "Celestial"
  case "fey":
    attacks = [{"name":"Otherworldly Slam","automation":[{"type":"target","target":"each","effects":[{"type":"attack","attackBonus":sab,"hit":[{"type":"damage","damage":f"1d8 + 3 + {spell_level} [psychic]"}],"miss":[],"adv":"0"}]},{"type":"text","text":"*Melee Attack Roll:* Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 plus the spell’s level of Radiant (Celestial), Psychic (Fey), or Necrotic (Fiend) damage."}],"_v":2},{"name":"Fey Step","automation":[{"type":"target","target":"self","effects":[{"type":"ieffect2","name":"Fey step used","duration":-1,"stacking":True}]},{"type":"text","text":"The steed teleports, along with its rider, to an unoccupied space of your choice up to 60 feet away from itself."}],"_v":2,"verb":"fey steps"}]
    summon_name = "Fey Steed"
    TYPE = stat_block["type"] = "Fey"
  case "fiend":
    attacks = [{"name":"Otherworldly Slam","automation":[{"type":"target","target":"each","effects":[{"type":"attack","attackBonus":sab,"hit":[{"type":"damage","damage":f"1d8 + 3 + {spell_level} [necrotic]"}],"miss":[],"adv":"0"}]},{"type":"text","text":"*Melee Attack Roll:* Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 plus the spell’s level of Radiant (Celestial), Psychic (Fey), or Necrotic (Fiend) damage."}],"_v":2},{"name":"Fell Glare","automation":[{"type":"target","target":"each","effects":[{"type":"target","target":"self","effects":[{"type":"ieffect2","name":"Fell glare Used","duration":-1,"stacking":True}]},{"type":"save","stat":"wis","dc":sdc,"fail":[{"type":"ieffect2","name":"Frightened","duration":10,"desc":"Frightened of {{caster.name}}","tick_on_caster" : True,"end" : True, "effects":{"attack_advantage":-1,"check_dis":["all"]}}],"success":[],"adv":0}]},{"type":"text","text":"Wisdom Saving Throw: DC equals your spell save DC, one creature within 60 feet the steed can see. Failure: The target has the **Frightened** condition until the end of your next turn."}],"_v":2,"verb":"takes","activation_type":3}]
    summon_name = "Fiendish Steed"
    TYPE = stat_block["type"] = "Fiend"
  case _:
    return f"""embed -title "Woopsie!" -desc "You didn't select a type!\n\nChoose from Beholder, Slaad or Star Spawn." """

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
s_name = custom_names.get(summon_name, f"Summoned {summon_name} ({init_add.get_initials(name)})")

group_name = args.last('group', combat().me.group or f"{init_add.get_initials(name)}'s Summons")

stat_block['p'] = True
stat_block['group'] = group_name
stat_block['note'] = f"Summoned by {name}"

c.me.set_group(group_name)
useconc = "noconc" not in args
usedur = int(args.get("dur",[600])[0])
c.me.add_effect(f"Summon {TYPE}", concentration=useconc, duration=usedur)

embed_args = {
  "title": f"{name} summoned a {summon_name} {TYPE}!",
  "desc": SPELL_DESC,
  "fields": [{"title": "Spell Slots", "desc": f"{ch.spellbook.slots_str(spell_level)} {'(-1)' if not ignore else ''}"}],
  "footer": f"{ctx.prefix+ctx.alias} | Made by Croebh",
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

