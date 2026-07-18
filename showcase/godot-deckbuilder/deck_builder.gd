class_name DeckBuilder
extends Node

signal state_changed(state: String)

const PLAYER_TURN := "PLAYER_TURN"
const ENEMY_TURN := "ENEMY_TURN"
const REWARD_CHOICE := "REWARD_CHOICE"
const VICTORY := "VICTORY"
const DEFEAT := "DEFEAT"
const RUN_COMPLETE := "RUN_COMPLETE"
const READY := "READY"

const ENCOUNTERS := [
	{"name": "THE HOLLOW WARDEN", "health": 3, "damage": 2},
	{"name": "THE BRASS SENTINEL", "health": 6, "damage": 3},
	{"name": "THE LAST LANTERN", "health": 9, "damage": 4},
]

@export var starting_energy: int = 3
@export var enemy_starting_health: int = 3
@export var player_starting_health: int = 6

var deck: Array[String] = []
var discard_pile: Array[String] = []
var hand: Array[String] = []
var energy: int = 0
var enemy_health: int = 0
var player_health: int = 0
var player_block: int = 0
var state: String = READY
var encounter_index: int = 0
var enemy_name := ""
var enemy_damage: int = 0
var strike_bonus: int = 0
var selected_boons: Array[String] = []

func start_run() -> void:
	encounter_index = 0
	player_health = player_starting_health
	strike_bonus = 0
	selected_boons.clear()
	_start_encounter()

func reset_encounter() -> void:
	start_run()

func _start_encounter() -> void:
	var encounter: Dictionary = ENCOUNTERS[encounter_index]
	enemy_name = str(encounter["name"])
	enemy_health = int(encounter["health"])
	enemy_starting_health = enemy_health
	enemy_damage = int(encounter["damage"])
	deck = ["strike", "block"]
	discard_pile.clear()
	hand.clear()
	energy = starting_energy
	player_block = 0
	state = PLAYER_TURN
	_draw_hand()
	state_changed.emit(state)

func draw_card() -> String:
	if deck.is_empty():
		return ""
	var card: String = deck.pop_front()
	hand.append(card)
	return card

func _draw_hand() -> void:
	while not deck.is_empty():
		draw_card()

func get_strike_damage() -> int:
	return 3 + strike_bonus

func play_strike() -> String:
	if not _can_play("strike"):
		state_changed.emit(state)
		return "INVALID"
	hand.erase("strike")
	discard_pile.append("strike")
	energy -= 1
	enemy_health -= get_strike_damage()
	state_changed.emit(state)
	return "STRIKE"

func play_block() -> String:
	if not _can_play("block"):
		state_changed.emit(state)
		return "INVALID"
	hand.erase("block")
	discard_pile.append("block")
	energy -= 1
	player_block += 2
	state_changed.emit(state)
	return "BLOCK"

func _can_play(card: String) -> bool:
	return state == PLAYER_TURN and energy >= 1 and hand.has(card)

func resolve_enemy_turn() -> int:
	if state != PLAYER_TURN:
		state_changed.emit(state)
		return 0
	if enemy_health <= 0:
		_finish_encounter()
		return 0
	state = ENEMY_TURN
	state_changed.emit(state)
	var damage: int = maxi(0, enemy_damage - player_block)
	_discard_hand()
	player_block = 0
	player_health -= damage
	if player_health <= 0:
		state = DEFEAT
	else:
		deck = discard_pile.duplicate()
		discard_pile.clear()
		energy = starting_energy
		_draw_hand()
		state = PLAYER_TURN
	state_changed.emit(state)
	return damage

func _discard_hand() -> void:
	for card in hand:
		discard_pile.append(card)
	hand.clear()

func _finish_encounter() -> void:
	_discard_hand()
	player_block = 0
	if encounter_index >= ENCOUNTERS.size() - 1:
		state = RUN_COMPLETE
	else:
		state = REWARD_CHOICE
	state_changed.emit(state)

func choose_boon(boon: String) -> bool:
	if state != REWARD_CHOICE or boon not in ["recover", "empower"]:
		return false
	if boon == "recover":
		player_health = mini(player_starting_health, player_health + 2)
	else:
		strike_bonus += 1
	selected_boons.append(boon)
	encounter_index += 1
	_start_encounter()
	return true

func get_encounter_number() -> int:
	return encounter_index + 1

func get_total_encounters() -> int:
	return ENCOUNTERS.size()
