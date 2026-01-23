---
name: ltx2-prompting
description: |
  Comprehensive prompting guide for LTX-2 video generation model. Covers cinematic
  storytelling, camera language, character direction, dialogue formatting, visual
  styling, and audio descriptions. Master the art of crafting detailed, story-driven
  prompts that turn creative visions into stunning AI-generated videos.
license: MIT
allowed-tools: Read WebFetch
version: 1.0.0
tags: [ai, video-generation, ltx2, prompting, cinematography, storytelling]
category: ai/video
trigger_phrases:
  - "LTX"
  - "LTX-2"
  - "LTX2"
  - "video generation"
  - "video prompt"
  - "AI video"
  - "cinematic prompt"
  - "video storytelling"
variables:
  style:
    type: string
    description: Visual style preference
    enum: [cinematic, animation, stylized]
    default: cinematic
  complexity:
    type: string
    description: Prompt complexity level
    enum: [simple, intermediate, advanced]
    default: intermediate
---

# LTX-2 Video Prompting Guide

## Core Philosophy

**Paint a complete picture that flows naturally from beginning to end.** The key to great LTX-2 prompts is covering all the elements the model needs to bring your vision to life in a cohesive, story-driven narrative.

> "A good prompt tells a story - establishing shot, scene, action, characters, camera movement, and audio woven into one flowing paragraph."

---

## The 6 Essential Elements

Every effective LTX-2 prompt should include these elements:

| Element | Purpose | Example |
|---------|---------|---------|
| **Shot Establishment** | Define visual style and scale | "Cinematic close-up", "Wide establishing shot" |
| **Scene Setting** | Lighting, atmosphere, mood | "Warm golden light", "moody fog" |
| **Action Description** | What happens, in sequence | "walks slowly, then breaks into a run" |
| **Character Definition** | Physical details, emotions | "woman in her 30s, emotional expression" |
| **Camera Movement** | How the view changes | "camera dollies back", "slow pan right" |
| **Audio Description** | Sounds, dialogue, ambient | "whispers dramatically", ambient rain |

---

## Prompt Structure

### The Golden Format

Write your prompt as a **single flowing paragraph** that moves naturally from beginning to end:

```
[SHOT TYPE + STYLE] + [SCENE/SETTING] + [CHARACTER INTRO] +
[ACTION SEQUENCE] + [CAMERA MOVEMENT] + [DIALOGUE/AUDIO] +
[ENDING/RESOLUTION]
```

### Optimal Length

- **Simple scenes**: 4-5 sentences
- **Complex narratives**: 6-8 sentences
- **Multi-character dialogue**: 8-10 sentences

{% if complexity == "simple" %}
### Simple Prompt Template

```
A [shot type] of [subject/character]. [Setting and lighting].
[Main action described]. [Camera movement]. [Optional audio/mood].
```

**Example:**
```
A cinematic close-up of a chef's hands chopping vegetables rapidly.
Warm kitchen lighting with steam rising in the background. The knife
moves rhythmically as ingredients fly into a waiting bowl. The camera
slowly pulls back to reveal the busy restaurant kitchen. Ambient
sounds of sizzling pans and distant chatter fill the air.
```
{% endif %}

{% if complexity == "intermediate" %}
### Intermediate Prompt Template

```
[Style/Genre]. [Opening shot establishment]. [Scene setting with
atmosphere]. [Character introduction with physical details].
[Action sequence with clear progression]. [Camera movement describing
relationship to subject]. [Dialogue in quotation marks with delivery
style]. [Scene resolution or transition].
```

**Example:**
```
A warm sunny backyard. The camera starts in a tight cinematic
close-up of a woman and a man in their 30s, facing each other with
serious expressions. The woman, emotional and dramatic, says softly,
"That's it... Dad's lost it. And we've lost Dad." The man exhales,
slightly annoyed: "Stop being so dramatic, Jess." A beat. He glances
aside, then mutters defensively, "He's just having fun." The camera
slowly pans right, revealing the grandfather in the garden wearing
enormous butterfly wings, waving his arms in the air like he's trying
to take off.
```
{% endif %}

{% if complexity == "advanced" %}
### Advanced Multi-Scene Template

```
[LOCATION/TIME]. [Detailed atmosphere and lighting setup]. [Opening
shot with cinematography terms]. [Character A introduction with full
physical description]. [Character A dialogue with emotion/delivery].
[Character B reaction and dialogue]. [Camera movement transition].
[New visual reveal]. [Continued action/dialogue]. [Pacing note or
style marker]. [Scene resolution with final visual].
```

**Example:**
```
INT. DAYTIME TALK SHOW SET – AFTERNOON. Soft studio lighting glows
across a warm-toned set. The audience murmurs faintly as the camera
pans to reveal three guests seated on a couch — a middle-aged couple
and the show's host sitting across from them. The host leans forward,
voice steady but probing: "When did you first notice that your
daughter, Missy, started to spiral?" The woman's face crumples; she
takes a shaky breath and begins to cry. Her husband places a
comforting hand on her shoulder, looking down before turning back
toward the host. Father (quietly, with guilt): "We… we don't know
what we did wrong." The studio falls silent for a moment. The camera
cuts to the host, who looks gravely into the lens. Host (to camera):
"Let's take a look at a short piece our team prepared." The lights
dim slightly as the camera pushes in on the mother's tear-streaked
face.
```
{% endif %}

---

## Shot Establishment

### Cinematography Terms

Use film industry language to establish your shot:

| Term | Description | Best For |
|------|-------------|----------|
| **Extreme close-up** | Fills frame with detail | Eyes, hands, objects |
| **Close-up** | Face or subject fills frame | Emotions, reactions |
| **Medium shot** | Waist-up framing | Dialogue, gestures |
| **Wide shot** | Full environment visible | Establishing, action |
| **Over-the-shoulder** | View past one subject to another | Conversations |
| **POV shot** | From character's perspective | Immersion, discovery |

### Scale and Style Modifiers

```
SCALE:
- intimate, claustrophobic
- expansive, epic
- balanced, measured

STYLE GENRES:
- Cinematic: period drama, film noir, fantasy, thriller, documentary
- Animation: stop-motion, 2D/3D, claymation, hand-drawn
- Stylized: comic book, cyberpunk, 8-bit pixel, surreal, painterly
```

{% if style == "cinematic" %}
### Cinematic Style Examples

```
FILM NOIR:
"A moody black-and-white shot of a detective in a fedora, cigarette
smoke curling upward. Hard shadows cut across his face as venetian
blinds stripe the wall behind him. He speaks in a gravelly voice:
'She walked in like trouble wearing heels.'"

PERIOD DRAMA:
"A sweeping crane shot over a Victorian ballroom, golden candlelight
reflecting off crystal chandeliers. Women in elaborate gowns waltz
with men in tailcoats. The camera descends to find our protagonist,
standing alone by a pillar, watching with quiet longing."

THRILLER:
"Tight handheld shot following a man running through rain-slicked
streets at night. Neon signs blur past. His breathing is heavy,
panicked. He glances back — the camera whips around to show nothing
but empty darkness. He whispers: 'They're still coming.'"
```
{% endif %}

{% if style == "animation" %}
### Animation Style Examples

```
PIXAR STYLE:
"A colorful kitchen scene with exaggerated, bouncy physics. A small
robot chef with oversized expressive eyes attempts to flip a pancake.
The pancake launches too high, sticks to the ceiling. The robot's
face shifts from pride to horror in classic Pixar timing. A beat.
The pancake slowly peels off and lands perfectly on the plate."

STOP-MOTION:
"Jittery stop-motion style. A clay fox cautiously approaches a
picnic basket in a handcrafted forest setting. Each movement is
deliberate, slightly jerky. The fox sniffs the basket, then looks
directly at camera with knowing eyes."

ANIME:
"Dynamic anime-style action sequence. A young warrior with flowing
blue hair charges forward, katana drawn. Speed lines blur the
background. She leaps, the camera tracking her arc in slow motion
as cherry blossoms scatter around her silhouette against the sun."
```
{% endif %}

{% if style == "stylized" %}
### Stylized Visual Examples

```
CYBERPUNK:
"Neon-drenched cityscape at night. A woman with a futuristic
transparent visor solders a robotic arm, blue sparks reflecting
in her eyes. Holographic advertisements flicker in the rain-streaked
window behind her. She pauses, hearing a distant sound, and says
with suspicion: 'Who's there?'"

COMIC BOOK:
"Bold comic book style with heavy black outlines and flat colors.
A superhero lands in a dramatic three-point pose, cape billowing.
POW! effects radiate from the impact crater. The camera pushes in
on their determined eyes."

SURREAL:
"Dreamlike, painterly visuals. A man in a bowler hat walks up
an endless staircase that loops back on itself, Escher-style.
Clouds drift past at eye level. He tips his hat to a passing fish
swimming through the air, unfazed."
```
{% endif %}

---

## Scene Setting

### Lighting Conditions

Be specific about light sources and quality:

```
NATURAL LIGHT:
- golden hour glow, warm sunset
- harsh midday sun, high contrast shadows
- overcast, soft diffused light
- moonlit, cool blue tones

ARTIFICIAL LIGHT:
- warm tungsten, orange glow
- cold fluorescent, greenish tint
- flickering candlelight, dancing shadows
- neon glow, vibrant color spill

DRAMATIC LIGHTING:
- backlighting, silhouette effect
- rim light, edge definition
- under-lighting, horror effect
- motivated light through window/door
```

### Atmosphere and Environment

```
WEATHER/PARTICLES:
- fog, mist, haze
- rain, drizzle, downpour
- dust particles in light beams
- snow, ash, embers floating
- smoke, steam, vapor

TEXTURES:
- rough stone, weathered wood
- smooth metal, glossy surfaces
- worn fabric, aged leather
- wet pavement, reflective puddles

COLOR PALETTE:
- warm earth tones (amber, rust, cream)
- cool blues and grays
- high contrast, saturated
- muted, desaturated, faded
- monochromatic with accent color
```

---

## Action Description

### Writing Movement

Use **present tense** and describe actions as a natural sequence:

```
GOOD (Sequential, present tense):
"The robot walks slowly forward. It begins to run, gaining speed.
It stops suddenly, and the camera continues past, revealing another
robot standing ahead."

BAD (Static, past tense):
"The robot walked and then it ran and stopped."
```

### Pacing and Temporal Effects

```
PACING TERMS:
- slow motion, time seems to stretch
- rapid cuts, quick editing
- lingering shot, holding on the moment
- continuous shot, no cuts
- freeze-frame, time stops

TRANSITIONS:
- fade-in, fade-out
- seamless transition
- quick zoom, snap cut
- dynamic movement into next scene
```

### Action Verb Library

```
MOVEMENT:
walks, runs, sprints, stumbles, glides, crawls, leaps, drifts

GESTURES:
reaches, points, waves, grabs, releases, touches, embraces

EXPRESSIONS:
smiles, frowns, grimaces, winces, gasps, sighs, glares

INTERACTIONS:
hands over, catches, drops, picks up, examines, reveals
```

---

## Character Definition

### Physical Description Checklist

Include relevant details based on shot scale:

```
CLOSE-UP needs:
✓ Facial features, expression
✓ Skin texture, makeup
✓ Eye color, emotional state
✓ Hair style, color

MEDIUM SHOT needs:
✓ Age range
✓ Clothing style, colors
✓ Posture, body language
✓ Hand positions, gestures

WIDE SHOT needs:
✓ Overall silhouette
✓ Movement style
✓ Relationship to environment
✓ Group positioning
```

### Showing Emotion (Not Telling)

```
INSTEAD OF:           USE:
"looks sad"      →    "eyes downcast, shoulders slumped"
"seems angry"    →    "jaw clenched, fists tight"
"feels confused" →    "brow furrowed, head tilted"
"appears nervous"→    "fidgets with hands, glances around"
"is excited"     →    "eyes wide, leaning forward eagerly"
```

---

## Camera Movement

### Camera Language Dictionary

```
LATERAL MOVEMENT:
- pans left/right: Camera rotates horizontally on axis
- tracks left/right: Camera physically moves sideways
- follows: Camera moves with subject

DEPTH MOVEMENT:
- dollies in/out: Camera moves toward/away from subject
- pushes in: Same as dolly in, often for emphasis
- pulls back: Same as dolly out, reveals more

VERTICAL MOVEMENT:
- tilts up/down: Camera rotates vertically
- cranes up/down: Camera physically rises/descends
- booms up/down: Same as crane

COMBINED:
- arcs around: Camera circles the subject
- tracks and pans: Movement while rotating
- crane with tilt: Rise while adjusting angle
```

### Camera Relationship to Subject

Always describe what the camera sees **after** movement:

```
GOOD:
"The camera dollies back, keeping the robot in medium shot, until
a second robot appears in an over-the-shoulder composition."

"The camera pans right, revealing the grandfather in the garden
wearing butterfly wings."

BAD:
"The camera moves." (No relationship or result described)
```

### Camera Feel

```
STABLE:
- static frame, locked off
- smooth dolly, steady movement
- controlled pan, measured

DYNAMIC:
- handheld, slight shake
- jittery, energetic
- following action, reactive

SPECIFIC EFFECTS:
- lens flare from light source
- shallow depth of field, bokeh
- motion blur on fast movement
```

---

## Audio and Dialogue

### Dialogue Formatting

Always use **quotation marks** and describe delivery:

```
FORMAT:
Character (delivery style): "Dialogue text here."

EXAMPLES:
Reporter (live, excited): "Black gold has been found!"
Baker (whispering dramatically): "Today… I achieve perfection."
Host (to camera, gravely): "Let's take a look at what happened."
Father (quietly, with guilt): "We don't know what we did wrong."
```

### Voice Characteristics

```
DELIVERY STYLES:
- whispers, mutters, speaks softly
- says clearly, states firmly
- shouts, screams, yells
- announces energetically
- drones monotonously

VOICE QUALITIES:
- gravelly, deep
- high-pitched, childlike
- robotic, mechanical
- resonant, with gravitas
- distorted, radio-style
```

### Ambient Audio

```
ENVIRONMENT SOUNDS:
- coffeeshop chatter, clinking cups
- rain and wind, thunder
- forest birds, rustling leaves
- city traffic, distant sirens
- machinery hum, industrial noise

MUSICAL ELEMENTS:
- tense underscore
- uplifting orchestral swell
- eerie silence
- rhythmic percussion
- soft acoustic guitar
```

---

## What Works Well

LTX-2 excels at:

### Strengths

```
✓ CINEMATIC COMPOSITIONS
  Wide, medium, close-up shots with thoughtful lighting
  Shallow depth of field and natural motion

✓ EMOTIVE HUMAN MOMENTS
  Single-subject emotional expressions
  Subtle gestures and facial nuance

✓ ATMOSPHERE & SETTING
  Fog, mist, golden hour, rain, reflections
  Ambient textures that ground the scene

✓ CLEAN CAMERA LANGUAGE
  "Slow dolly in", "handheld tracking", "over-the-shoulder"
  Clear, specific directions

✓ STYLIZED AESTHETICS
  Painterly, noir, analog film, fashion editorial
  Named styles early in prompt

✓ LIGHTING AND MOOD
  Backlighting, color palettes, rim light
  Specific light sources anchor tone

✓ VOICE AND DIALOGUE
  Characters can talk and sing
  Multiple languages supported
```

---

## What to Avoid

### Common Pitfalls

```
✗ INTERNAL STATES WITHOUT VISUAL CUES
  BAD: "She feels sad"
  GOOD: "Her eyes glisten, she looks down at her hands"

✗ TEXT AND LOGOS
  LTX-2 cannot generate readable text
  Avoid signage, brand names, printed material

✗ COMPLEX PHYSICS / CHAOTIC MOTION
  Jumping, juggling, rapid twisting causes artifacts
  (Dancing works well, though!)

✗ SCENE COMPLEXITY OVERLOAD
  Too many characters, layered actions, excessive objects
  Start simple, add complexity gradually

✗ INCONSISTENT LIGHTING LOGIC
  BAD: "Warm sunset with cold fluorescent glow"
  Unless motivated, keep lighting coherent

✗ OVER-COMPLICATED PROMPTS
  More instructions = higher chance some won't appear
  Begin simple, iterate to add layers
```

---

## Complete Examples

### Action Scene

```
An action packed, cinematic shot of a monster truck driving fast
towards the camera, the truck passes the camera as it pans left to
follow the truck's reckless drive. Dust and motion blur surround the
truck, handheld feel to the camera as it tries to track its ride into
the distance. The truck then drifts and turns around, then drives
back towards the camera until seen in extreme close-up.
```

### Comedy Scene

```
A warm, intimate cinematic shot inside a cozy bar. The camera opens
on a young female singer with short brown hair singing into a
microphone while strumming an acoustic guitar, eyes closed. The
camera slowly arcs left around her, keeping her face in sharp focus
as band members remain softly blurred behind her. Warm light wraps
around her face as framed photos drift past in the background.
Ambient live music fills the space, led by her clear vocals over
gentle acoustic strumming.
```

### Dramatic Dialogue

```
INT. OVEN – DAY. Static camera from inside the oven, looking outward
through slightly fogged glass. Warm golden light glows around freshly
baked cookies. The baker's face fills the frame, eyes wide with
focus, his breath fogging the glass as he leans in. Baker (whispering
dramatically): "Today… I achieve perfection." He leans even closer.
"Golden edges. Soft center. The gods themselves will smell these
cookies and weep." Baker: "Wait—" (beat) "Did I… forget the
chocolate chips?" Cut to side view — coworker pops into frame,
chewing casually. Coworker (mouth full): "Nope. You forgot the
sugar." Quick zoom back to the baker's horrified face. Pixar style
acting and timing.
```

### Animation Scene

```
Pinocchio is sitting in an interrogation room, looking nervous and
slightly sweating. He's saying very quietly to himself "I didn't do
it... I didn't do it... I'm not a murderer". Pinocchio's nose is
quickly getting longer and longer. The camera zooms in on the
double-sided mirror in the back of the room. The mirror turns black
as the camera approaches, exposing a blurry silhouette of two FBI
detectives in the dark room on the other side. One says "I'm telling
you, I have a feeling something is off with this kiddo."
```

---

## Iteration Workflow

LTX-2 is designed for fast experimentation:

```
1. START SIMPLE
   Begin with core action + one character + basic setting

2. GENERATE AND REVIEW
   What worked? What's missing?

3. ADD LAYERS
   Include camera movement, lighting details, audio

4. REFINE SPECIFICS
   Adjust timing words, character details, atmosphere

5. STYLE POLISH
   Add genre markers, film characteristics, mood anchors

6. ITERATE
   Don't be afraid to try variations!
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│ LTX-2 PROMPT CHECKLIST                                          │
├─────────────────────────────────────────────────────────────────┤
│ □ Shot type (close-up, medium, wide)                            │
│ □ Visual style (cinematic, animation, stylized)                 │
│ □ Lighting (source, quality, mood)                              │
│ □ Setting/atmosphere (location, weather, textures)              │
│ □ Character details (age, clothing, physical cues)              │
│ □ Action sequence (present tense, beginning to end)             │
│ □ Camera movement (what moves, what's revealed)                 │
│ □ Dialogue in quotes with delivery style                        │
│ □ Single flowing paragraph                                      │
│ □ 4-8 descriptive sentences                                     │
├─────────────────────────────────────────────────────────────────┤
│ WORKS WELL: emotions, atmosphere, clean camera, styled looks    │
│ AVOID: text, complex physics, overloaded scenes, vague moods    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Skills

- `prompt-engineering` - General prompting techniques
- `video-production` - Video editing and production concepts
- `cinematography` - Film and camera techniques
