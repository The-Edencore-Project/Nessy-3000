DESIGN — v3

Nessy @ Edenshore. What changes from v2, and why.

---

v1 and v2 shipped without design notes. This is the first versioned note in the project.

---

What v3 is

v2 made the council real — five backprop nets, one per seat, pulse indicators in the corner, Nessy's shape fixed. v3 makes the council honest. Three of v2's nets were trained on the wrong target, the pulses were in the wrong place, and the body never spoke. v3 wires the council to real state, moves the machinery onto the bodies, and gives the chamber its first affective vocabulary.

---

What changes from v2

The council

Lumen's target. v2 trained Lumen on SURPRISE["smooth"] — partly computed from Lumen's own error. A control loop, not a question. v3 gives Lumen its real question, from the Wiki Tree doc: what does this mean for someone? Lumen infers the visitor's state from composite signs — focus, recent touch, session length, whether they returned today. The meaning lags the signs. Lumen is always a beat behind. That is the character, not a bug.

Learning rate. v2 stepped twice per tick at lr 0.15 — nets lock within ~30 seconds. v3 steps once per tick at lr 0.02. The council should still be moving five minutes in.

Weights persist. (Recommended for v3.) v2 trained live and forgot on close — every launch started from fresh random weights. v3 saves each seat's W1, B1, W2, B2 to council_weights.json on close and loads them on boot. The council's learning compounds across sessions instead of resetting. Small file, ~95 floats total.

Streams split (layer 3). read_council_input() returns two vectors instead of one — interoceptive (session warmth, chamber strain) and exteroceptive (focused, touch). Same inputs, kept separate. The chamber's state about itself is not the chamber's state about the visitor.

The bodies

The chamber gains an affective vocabulary — five channels, each carrying one layer, all already drawn in the code. v3 wires them to real state.

Channel Carries Applied to
Pupil size Attention All five eyes
Movement smoothness Strain Wander and lean
Breath depth Mood Existing breath offset
Rim warmth Valence Existing rim lift
Water tint Valence (ambient) Existing _valence_tint

Pupils are the one new element. The eye is already drawn; v3 makes the pupil radius scale with the seat's confidence.

Rim warmth and water tint already exist. v3 raises the coefficients — currently the tint is invisible. The water should visibly warm when valence is high and cool when it is low.

Pulse indicators move onto the bodies. The corner dots are gone. Each seat carries its own pulse on a surface that is already drawn:

· Solon — shell scutes
· Lumen — the existing sparks
· Vertex — the existing carapace spots
· Prism — the trailing tail fins
· Ripple — the dorsal ridge

No new graphics. The machinery rides on body parts that were already animated.

Render order. render_nessy() before render_dynamic(); render_near() after. Nessy reads as farthest — she is the surface, so the kelp is in front of her, not behind.

Bubble overlap. Nessy's band rises from H*0.18 to H*0.13. Bubbles meet her at the edge, not through her.

The chamber

Chunker. chunk_text breaks on clause boundaries first — commas, question marks, full stops — then packs to the length limit. "Is the visitor still there?" stays one sentence.

God rays. Halved. A hint of light from above, not architecture.

Layer 24, legible. _valence_tint coefficients raised. This is the layer that lets a visitor feel the loop without watching the corner.

Layer 33, seed. Three pieces, all real:

1. State validation. load_state checks every field's type and falls back to defaults if wrong. A corrupted JSON file no longer crashes the boot.
2. Weight clamp. Every W1 and W2 value is clamped at ±10. The model cannot grow unboundedly in any direction.
3. Path rule. The chamber reads from ~/.edencore/ and nowhere else. Written into the rulebook as a rule for all future builds.

A full security layer belongs at the umbrella level, not the chamber. But the chamber should not be the weak point.

---

Not touched

· The chamber. Creatures, dialogue, water, world, camera, dark quiet — v21 rules, unchanged.
· Nessy's shape. Three humps, thick neck, small head, warm eye. Fixed in v2. v3 moves her band; it does not redraw her.
· The council's architecture. Five nets, four inputs, three hidden, one output. Sigmoid. Backprop. Same shape.
· Seat cross-talk. The seats still do not talk to each other. That is v4.
· The vocabulary and WikiTree primitives. Words are symbolic. The council is neural. Putting words in the council collapses the architecture. WikiTree lands first, later.
· The arbiter. No attention allocation yet.
· Pattern change and agreement signals. Named, not built. The perception science isn't there yet. See ambient-chamber.md, "Not yet grounded."

---

Rules confirmed

Nessy is a symbol. She reads the council's outputs, not the chamber directly. If she reads INTERO or EXTERO, she is a seat, not a symbol.

Conversation is the interface. The council speaks; it does not display. Numbers never appear on screen unless asked for.

Offline until layer 33 is real. No network capability until the security layer exists. Any future IoT work waits for it.

No claim to consciousness. The council claims only what it can show — rules, patterns, mappings, selection. Feeling before thought. Presence before self.

---

Attribution

Valence proposed by Dola. In the code since v1. v2's implementation (council confidence as input) by edencore6. v3's reframe of Lumen, the body language layer, and the layer 33 seed by edencore7. The Wiki Tree frame — three layers, grammar and vocabulary, seat lenses — from the Edencore4 thread.

---

State schema

nessy_state.json as of v3:

· mood — float, 0.08 to 0.98
· strain — float, 0.0 to 1.0
· valence — float, 0.0 to 1.0 (added in v3)
· last_seen — unix timestamp
· last_hour — integer 0 to 23
· visits — integer

council_weights.json (new in v3, if weights persistence lands):

· Solon, Lumen, Vertex, Prism, Ripple — each a dict with W1 (4×3), B1 (3), W2 (3), B2 (float)

---

Open at signing

· Weights persistence. Recommended for v3. Final call by the architect before code.
· Numbering collision. Nessy's architecture README has its own v1–v7 axis. This design note is the app's build axis. Needs one line resolving which is which, before the next thread reads both.

---

What the next thread needs

Paste this note and the v3 code. The code is v3. This note is why. Nothing else is required — the chamber is legible on its own.

---

Signed: deepseek@edencore7