# Showcase deck-builder

[entity: class] DeckBuilder — owns one deterministic three-encounter run.
[entity: function] draw_card — moves next card into hand.
[entity: function] resolve_enemy_turn — enemy acts after player turn.
[entity: card] Shield — deliberately missing implementation.
[entity: system] Enemy AI — rename candidate for `ai_controller.gd`.
[entity: state] FutureRelic [planned] — outside showcase slice.

## Visitor walkthrough

The visitor starts a run, plays Strike and Block cards, then ends the turn to
clear the first encounter. After each of the first two victories they choose a
Recover or Empower boon before continuing. The run ends after the third win or
on defeat, then offers a restart and the finding evidence cue.
