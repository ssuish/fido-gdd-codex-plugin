extends Node

const INK := Color("#101722")
const INK_LIGHT := Color("#1a2835")
const PANEL := Color("#21313f")
const PANEL_EDGE := Color("#587083")
const PAPER := Color("#f4e7c8")
const PAPER_MUTED := Color("#c6b895")
const BRASS := Color("#e4b85b")
const BRASS_DARK := Color("#8a642b")
const TEAL := Color("#66d4c2")
const RED := Color("#ef7770")
const VIOLET := Color("#b69ce7")

const ASSET_ROOT := "res://assets/deck_builder/"
const STRIKE_EMOJI := ASSET_ROOT + "Emojis/Free/PNG Big (256 px)/emojis_black_outline (1).png"
const BLOCK_EMOJI := ASSET_ROOT + "Emojis/Free/PNG Big (256 px)/emojis_black_outline (15).png"
const RECOVER_EMOJI := ASSET_ROOT + "Emojis/Free/PNG Big (256 px)/emojis_health_bar (1).png"
const EMPOWER_EMOJI := ASSET_ROOT + "Emojis/Free/PNG Big (256 px)/emojis_black_outline (21).png"
const SHIELD_ICON := ASSET_ROOT + "Status/PNG Small (64 px)/combat_small.png"
const ATTACK_ICON := ASSET_ROOT + "Status/PNG Small (64 px)/flame_small.png"
const ARCANE_ICON := ASSET_ROOT + "Status/PNG Small (64 px)/arcane_small.png"

@onready var encounter: DeckBuilder = $DeckBuilder
@onready var ui: Control = $UI

var state_label: Label
var encounter_label: Label
var feedback_label: Label
var enemy_name_label: Label
var enemy_hp_label: Label
var enemy_intent_label: Label
var enemy_bar: ProgressBar
var player_hp_label: Label
var block_label: Label
var energy_label: Label
var strike_stat_label: Label
var boon_label: Label
var energy_pips: Array[Panel] = []
var strike_card: Button
var block_card: Button
var strike_effect: Label
var block_effect: Label
var end_turn_button: Button
var reset_button: Button
var start_overlay: Panel
var reward_overlay: Panel
var terminal_overlay: Panel
var terminal_title: Label
var terminal_detail: Label
var last_feedback := "Begin a run to face the Hollow Warden."

func _ready() -> void:
	_build_ui()
	encounter.state_changed.connect(_on_encounter_state_changed)
	strike_card.pressed.connect(_on_strike_pressed)
	block_card.pressed.connect(_on_block_pressed)
	end_turn_button.pressed.connect(_on_end_turn_pressed)
	reset_button.pressed.connect(_on_reset_pressed)
	_refresh(encounter.state)

func _build_ui() -> void:
	ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ui.mouse_filter = Control.MOUSE_FILTER_STOP
	var background := ColorRect.new()
	background.color = INK
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(background)

	var top_bar := _panel(Rect2(18, 14, 924, 60), PANEL, PANEL_EDGE)
	ui.add_child(top_bar)
	_add_label(top_bar, "THE LAST LANTERN", Rect2(18, 7, 330, 28), 22, PAPER)
	encounter_label = _add_label(top_bar, "RUN  0 / 3", Rect2(20, 35, 280, 17), 10, PAPER_MUTED)
	state_label = _add_label(top_bar, "READY", Rect2(566, 15, 235, 28), 17, BRASS)
	state_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	reset_button = _button(top_bar, "RESTART", Rect2(816, 13, 88, 34), 11)

	var player_panel := _panel(Rect2(18, 90, 182, 224), PANEL, PANEL_EDGE)
	ui.add_child(player_panel)
	_add_label(player_panel, "YOUR VITALS", Rect2(16, 10, 150, 20), 11, PAPER_MUTED)
	player_hp_label = _add_label(player_panel, "HP  6 / 6", Rect2(16, 37, 150, 30), 21, PAPER)
	block_label = _add_label(player_panel, "BLOCK  0", Rect2(16, 74, 150, 23), 14, TEAL)
	_icon(player_panel, SHIELD_ICON, Rect2(140, 70, 25, 25))
	energy_label = _add_label(player_panel, "ENERGY  3 / 3", Rect2(16, 106, 150, 20), 11, BRASS)
	for index in range(3):
		var pip := _panel(Rect2(116 + index * 17, 110, 12, 12), BRASS_DARK, BRASS_DARK)
		player_panel.add_child(pip)
		energy_pips.append(pip)
	strike_stat_label = _add_label(player_panel, "STRIKE  3", Rect2(16, 141, 150, 20), 11, RED)
	_icon(player_panel, ATTACK_ICON, Rect2(140, 137, 25, 25))
	boon_label = _add_label(player_panel, "BOONS  —", Rect2(16, 178, 150, 30), 10, PAPER_MUTED)
	boon_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

	var enemy_panel := _panel(Rect2(218, 90, 524, 151), PANEL, PANEL_EDGE)
	ui.add_child(enemy_panel)
	enemy_name_label = _add_label(enemy_panel, "THE HOLLOW WARDEN", Rect2(20, 10, 300, 24), 17, PAPER)
	enemy_intent_label = _add_label(enemy_panel, "INTENT  ATTACKS FOR 2", Rect2(20, 39, 330, 20), 12, RED)
	_icon(enemy_panel, ATTACK_ICON, Rect2(340, 35, 23, 23))
	enemy_hp_label = _add_label(enemy_panel, "HP  3 / 3", Rect2(344, 10, 150, 24), 16, PAPER)
	enemy_hp_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	enemy_bar = ProgressBar.new()
	enemy_bar.position = Vector2(20, 80)
	enemy_bar.size = Vector2(474, 26)
	enemy_bar.show_percentage = false
	enemy_bar.add_theme_stylebox_override("background", _box(Color("#101720"), Color("#101720"), 6))
	enemy_bar.add_theme_stylebox_override("fill", _box(RED, RED, 6))
	enemy_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	enemy_panel.add_child(enemy_bar)
	_add_label(enemy_panel, "Enemy damage rises each encounter. Spend energy before ending your turn.", Rect2(20, 114, 474, 19), 10, PAPER_MUTED)

	var feedback_panel := _panel(Rect2(218, 258, 524, 70), INK_LIGHT, PANEL_EDGE)
	ui.add_child(feedback_panel)
	_add_label(feedback_panel, "COMBAT LOG", Rect2(16, 8, 120, 15), 10, PAPER_MUTED)
	feedback_label = _add_label(feedback_panel, last_feedback, Rect2(16, 26, 488, 32), 14, PAPER)
	feedback_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

	var turn_panel := _panel(Rect2(760, 90, 182, 238), PANEL, PANEL_EDGE)
	ui.add_child(turn_panel)
	_add_label(turn_panel, "TURN CONTROL", Rect2(16, 14, 150, 18), 11, PAPER_MUTED)
	_add_label(turn_panel, "Play both cards\nor hold one for later.", Rect2(16, 43, 150, 42), 13, PAPER)
	end_turn_button = _button(turn_panel, "END TURN", Rect2(16, 106, 150, 51), 15)
	_add_label(turn_panel, "Unused cards discard.\nBlock expires after attack.", Rect2(16, 175, 150, 38), 11, PAPER_MUTED)

	_add_label(ui, "YOUR HAND", Rect2(218, 342, 220, 18), 11, PAPER_MUTED)
	strike_card = _visual_card(ui, "STRIKE", "Deal damage", "COST  1", STRIKE_EMOJI, ATTACK_ICON, RED, Rect2(218, 365, 244, 157))
	block_card = _visual_card(ui, "BLOCK", "Gain block", "COST  1", BLOCK_EMOJI, SHIELD_ICON, TEAL, Rect2(478, 365, 244, 157))
	strike_effect = strike_card.get_meta("effect_label") as Label
	block_effect = block_card.get_meta("effect_label") as Label

	start_overlay = _overlay_panel()
	var start_title := _add_label(start_overlay, "THE LAST LANTERN", Rect2(40, 45, 580, 52), 36, BRASS)
	start_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var start_copy := _add_label(start_overlay, "Survive three deterministic encounters.\nChoose a boon after each victory.", Rect2(40, 115, 580, 52), 17, PAPER)
	start_copy.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var begin_button := _button(start_overlay, "BEGIN RUN", Rect2(210, 222, 240, 48), 15)
	begin_button.pressed.connect(_on_begin_pressed)

	reward_overlay = _overlay_panel()
	var reward_title := _add_label(reward_overlay, "CHOOSE A BOON", Rect2(40, 28, 580, 42), 28, BRASS)
	reward_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var reward_copy := _add_label(reward_overlay, "The next encounter begins after your choice.", Rect2(40, 70, 580, 24), 13, PAPER_MUTED)
	reward_copy.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var recover_card := _visual_card(reward_overlay, "RECOVER", "Restore 2 HP", "BOON", RECOVER_EMOJI, SHIELD_ICON, TEAL, Rect2(73, 110, 240, 174))
	var empower_card := _visual_card(reward_overlay, "EMPOWER", "+1 Strike damage", "BOON", EMPOWER_EMOJI, ARCANE_ICON, VIOLET, Rect2(347, 110, 240, 174))
	recover_card.pressed.connect(func(): _on_boon_pressed("recover"))
	empower_card.pressed.connect(func(): _on_boon_pressed("empower"))

	terminal_overlay = _overlay_panel()
	terminal_title = _add_label(terminal_overlay, "RUN COMPLETE", Rect2(40, 52, 580, 52), 35, BRASS)
	terminal_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	terminal_detail = _add_label(terminal_overlay, "", Rect2(64, 120, 532, 60), 16, PAPER)
	terminal_detail.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	terminal_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var replay_button := _button(terminal_overlay, "PLAY AGAIN", Rect2(210, 224, 240, 48), 15)
	replay_button.pressed.connect(_on_reset_pressed)

func _overlay_panel() -> Panel:
	var overlay := _panel(Rect2(150, 108, 660, 310), Color("#182a38"), BRASS)
	overlay.z_index = 10
	ui.add_child(overlay)
	overlay.visible = false
	return overlay

func _visual_card(parent: Control, title: String, effect: String, cost: String, emoji_path: String, icon_path: String, accent: Color, rect: Rect2) -> Button:
	var card := Button.new()
	card.position = rect.position
	card.size = rect.size
	card.tooltip_text = ""
	card.add_theme_stylebox_override("normal", _box(Color("#263541"), accent.darkened(0.4), 12))
	card.add_theme_stylebox_override("hover", _box(Color("#364b58"), accent, 12))
	card.add_theme_stylebox_override("pressed", _box(Color("#46616a"), PAPER, 12))
	card.add_theme_stylebox_override("disabled", _box(Color("#202a32"), Color("#3a4650"), 12))
	parent.add_child(card)
	var art := _icon(card, emoji_path, Rect2(76, 12, 92, 78))
	art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	var badge := _panel(Rect2(14, 13, 48, 24), accent.darkened(0.25), accent)
	card.add_child(badge)
	var badge_label := _add_label(badge, cost, Rect2(2, 1, 44, 20), 9, PAPER)
	badge_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_icon(card, icon_path, Rect2(16, 112, 25, 25))
	var title_label := _add_label(card, title, Rect2(50, 101, 176, 24), 16, PAPER)
	var effect_label := _add_label(card, effect, Rect2(50, 124, 176, 22), 12, PAPER_MUTED)
	card.set_meta("art", art)
	card.set_meta("title_label", title_label)
	card.set_meta("effect_label", effect_label)
	card.set_meta("accent", accent)
	return card

func _panel(rect: Rect2, fill: Color, border: Color) -> Panel:
	var panel := Panel.new()
	panel.position = rect.position
	panel.size = rect.size
	panel.add_theme_stylebox_override("panel", _box(fill, border, 10))
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return panel

func _box(fill: Color, border: Color, radius: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(radius)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 5
	style.content_margin_bottom = 5
	return style

func _add_label(parent: Control, text: String, rect: Rect2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.position = rect.position
	label.size = rect.size
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(label)
	return label

func _icon(parent: Control, path: String, rect: Rect2) -> TextureRect:
	var icon := TextureRect.new()
	# Set the sizing policy before assigning the texture. This prevents the
	# imported 64/256px source size from becoming the control's minimum size.
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icon.custom_minimum_size = Vector2.ZERO
	icon.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	icon.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	icon.position = rect.position
	icon.size = rect.size
	icon.texture = load(path)
	# Re-apply the size after loading because TextureRect refreshes its minimum
	# size when a texture is assigned.
	icon.custom_minimum_size = Vector2.ZERO
	icon.size = rect.size
	icon.clip_contents = true
	icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(icon)
	return icon

func _button(parent: Control, text: String, rect: Rect2, font_size: int) -> Button:
	var button := Button.new()
	button.text = text
	button.position = rect.position
	button.size = rect.size
	button.add_theme_font_size_override("font_size", font_size)
	button.add_theme_color_override("font_color", PAPER)
	button.add_theme_color_override("font_hover_color", Color.WHITE)
	button.add_theme_color_override("font_disabled_color", Color("#697481"))
	button.add_theme_stylebox_override("normal", _box(INK_LIGHT, PANEL_EDGE, 8))
	button.add_theme_stylebox_override("hover", _box(Color("#304353"), BRASS, 8))
	button.add_theme_stylebox_override("pressed", _box(Color("#405b65"), TEAL, 8))
	button.add_theme_stylebox_override("disabled", _box(Color("#1a222b"), Color("#303b47"), 8))
	parent.add_child(button)
	return button

func _on_begin_pressed() -> void:
	last_feedback = "The Hollow Warden bars the way."
	encounter.start_run()

func _on_encounter_state_changed(next_state: String) -> void:
	_refresh(next_state)

func _on_strike_pressed() -> void:
	var result := encounter.play_strike()
	last_feedback = "Strike hits for %d." % encounter.get_strike_damage()
	if result == "INVALID":
		last_feedback = _invalid_card_reason("strike")
	_refresh(encounter.state)

func _on_block_pressed() -> void:
	var result := encounter.play_block()
	last_feedback = "Block raised by 2."
	if result == "INVALID":
		last_feedback = _invalid_card_reason("block")
	_refresh(encounter.state)

func _on_end_turn_pressed() -> void:
	if encounter.enemy_health <= 0:
		last_feedback = "The enemy falls. Choose your reward."
		encounter.resolve_enemy_turn()
		return
	last_feedback = "The enemy attacks..."
	var damage := encounter.resolve_enemy_turn()
	last_feedback = "The attack was blocked." if damage == 0 else "You take %d damage. Cards redraw for the next turn." % damage
	_refresh(encounter.state)

func _on_boon_pressed(boon: String) -> void:
	last_feedback = "Recovered 2 HP." if boon == "recover" else "Strike damage increased by 1."
	encounter.choose_boon(boon)

func _on_reset_pressed() -> void:
	last_feedback = "A new run awaits."
	encounter.start_run()

func _invalid_card_reason(card: String) -> String:
	if encounter.state != DeckBuilder.PLAYER_TURN:
		return "Cards can only be played during your turn."
	if not encounter.hand.has(card):
		return "That card is in your discard pile."
	return "Not enough energy."

func _refresh(next_state: String) -> void:
	var has_run := next_state != DeckBuilder.READY
	state_label.text = next_state.replace("_", " ")
	state_label.add_theme_color_override("font_color", RED if next_state == DeckBuilder.DEFEAT else TEAL if next_state == DeckBuilder.RUN_COMPLETE else BRASS if next_state == DeckBuilder.PLAYER_TURN else PAPER_MUTED)
	encounter_label.text = "RUN  %d / %d" % [encounter.get_encounter_number() if has_run else 0, encounter.get_total_encounters()]
	player_hp_label.text = "HP  %d / %d" % [maxi(0, encounter.player_health), encounter.player_starting_health]
	block_label.text = "BLOCK  %d" % encounter.player_block
	energy_label.text = "ENERGY  %d / %d" % [encounter.energy, encounter.starting_energy]
	strike_stat_label.text = "STRIKE  %d" % encounter.get_strike_damage()
	boon_label.text = "BOONS  " + (", ".join(encounter.selected_boons) if not encounter.selected_boons.is_empty() else "—")
	for index in range(energy_pips.size()):
		var pip_color := BRASS if index < encounter.energy else BRASS_DARK
		energy_pips[index].add_theme_stylebox_override("panel", _box(pip_color, pip_color, 4))
	enemy_name_label.text = encounter.enemy_name
	enemy_hp_label.text = "HP  %d / %d" % [maxi(0, encounter.enemy_health), encounter.enemy_starting_health]
	enemy_bar.max_value = maxf(1.0, float(encounter.enemy_starting_health))
	enemy_bar.value = maxi(0, encounter.enemy_health)
	enemy_intent_label.text = "INTENT  ATTACKS FOR %d" % encounter.enemy_damage if next_state in [DeckBuilder.PLAYER_TURN, DeckBuilder.ENEMY_TURN] else "INTENT  ENCOUNTER PAUSED"
	feedback_label.text = last_feedback
	_refresh_card(strike_card, "strike", "Deal %d damage" % encounter.get_strike_damage())
	_refresh_card(block_card, "block", "Gain 2 block")
	end_turn_button.disabled = next_state != DeckBuilder.PLAYER_TURN
	reset_button.disabled = next_state == DeckBuilder.READY
	start_overlay.visible = next_state == DeckBuilder.READY
	reward_overlay.visible = next_state == DeckBuilder.REWARD_CHOICE
	terminal_overlay.visible = next_state in [DeckBuilder.DEFEAT, DeckBuilder.RUN_COMPLETE]
	if terminal_overlay.visible:
		var completed := encounter.get_encounter_number() - (0 if next_state == DeckBuilder.RUN_COMPLETE else 1)
		terminal_title.text = "RUN COMPLETE" if next_state == DeckBuilder.RUN_COMPLETE else "DEFEAT"
		terminal_title.add_theme_color_override("font_color", BRASS if next_state == DeckBuilder.RUN_COMPLETE else RED)
		terminal_detail.text = "%d of %d encounters cleared.\nBoons: %s" % [completed, encounter.get_total_encounters(), ", ".join(encounter.selected_boons) if not encounter.selected_boons.is_empty() else "none"]

func _refresh_card(card: Button, card_id: String, effect: String) -> void:
	var available := encounter.state == DeckBuilder.PLAYER_TURN and encounter.energy >= 1 and encounter.hand.has(card_id)
	card.disabled = not available
	card.tooltip_text = "Click to play." if available else _invalid_card_reason(card_id)
	(card.get_meta("effect_label") as Label).text = effect
	(card.get_meta("art") as TextureRect).modulate = Color.WHITE if available else Color("#70808b")
