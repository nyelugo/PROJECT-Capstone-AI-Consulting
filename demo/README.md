# Demo recordings, generated

Narrated screen recordings of the two demos, produced from a script rather than captured by
hand — so re-recording after a UI change costs a command, not an afternoon.

```bash
python -m demo.generate_demo mvp          # the MVP demo — slide 9's backup
python -m demo.generate_demo poc --login  # sign in to n8n once
python -m demo.generate_demo poc          # the POC demo — a required deliverable
```

Output lands in `demo/recordings/`. Needs `ffmpeg`, `playwright`, and `OPENAI_API_KEY`.

## How the picture and the words stay in step

Each cue in [`cues.py`](cues.py) pairs **what is said** with **what happens on screen**.

1. Every line is synthesised first, so its exact duration is known before the browser opens.
2. The recorder performs the cue's action, then holds the frame for precisely that duration.
3. Whatever the action itself cost — a page load, a model call — is *measured*, and the same
   amount of silence is laid in front of that cue's narration afterwards.

So the soundtrack is assembled to fit the video that actually happened, rather than the
video being nudged to fit an assumed soundtrack. Nothing is timed by hand and nothing drifts.

Narration is cached on the text: change a sentence and only that sentence is re-synthesised.
It is the only paid step, and a full run costs a fraction of a cent.

Text-to-speech is lifted from **PROJECT-Podcast-Studio** (`src/tts_generator.py`, by Adam,
Anand and Ugo) — same model, same streaming-to-disk approach, kept recognisable rather than
rewritten.

## What it refuses to do

- **Film a login page.** The POC target is the cohort n8n instance. If the session has
  expired the recorder stops on the first cue and tells you to run `--login`, rather than
  producing a beautifully narrated two-minute film of a sign-in form.
- **Guess at a renamed control.** A missing button fails in six seconds and prints every
  button label on the page. This is not hypothetical: the first cut referenced *"Send to
  that team"*, which was the tabs-era label, and the queue rebuild had renamed it.

## Known limits

- **The screen holds still while the narrator talks.** The app fits the viewport, so most
  `scroll_to` cues are no-ops. It reads as a calm walkthrough, not a broken recording — but
  it is not a motion graphic.
- **`.browser-profile/` holds a real session cookie** for the n8n instance. Gitignored, and
  it never contains an API key.
- **Cue text must match the live UI.** That is the coupling that makes the demo honest and
  also the thing that breaks first — which is why failures name what they found instead.

## Verifying a recording

Do not trust that it rendered. Pull frames and look:

```bash
for t in 5 20 40 60 80; do
  ffmpeg -v error -ss $t -i demo/recordings/mvp_demo.mp4 -frames:v 1 /tmp/f_$t.png -y
done
ffmpeg -i demo/recordings/mvp_demo.mp4 -af volumedetect -f null - 2>&1 | grep mean_volume
```

The first three cuts of the MVP demo all produced a valid, playable, correctly narrated
file. The first was missing the entire row detail, because Streamlit scrolls an inner
container and `window.scrollTo` silently does nothing. The second never showed the button
being pressed. Only frame-by-frame inspection caught either.
