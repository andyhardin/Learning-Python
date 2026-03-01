#!/usr/bin/env python3
"""
Wordle Solver
=============
Suggests optimal guesses to solve Wordle puzzles in 6 tries.

Usage:
  Interactive mode  -- python3 wordle_solver.py
  Auto-solve mode   -- python3 wordle_solver.py --answer CRANE

Feedback format (5 characters, one per letter):
  G = Green  (correct letter, correct position)
  Y = Yellow (correct letter, wrong position)
  B = Black  (letter not in the word at all)

Example:
  Guess: CRANE  Answer: TRAIN
  C -> B   (not in TRAIN)
  R -> G   (R at position 1 in both)
  A -> G   (A at position 2 in both)
  N -> Y   (N is in TRAIN but at position 4, not 3)
  E -> B   (not in TRAIN)
  Feedback: BGGBY
"""

import argparse
import os
from collections import Counter

# ---------------------------------------------------------------------------
# Word list – fetched from the web and cached locally on first run.
# Falls back to the built-in list if the download fails.
# ---------------------------------------------------------------------------
WORD_LIST_URL = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"
WORD_LIST_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordle_words.txt")


def _load_words() -> list[str]:
    """Return sorted list of 5-letter words, downloading if needed."""
    # Use cached file if available
    if os.path.exists(WORD_LIST_CACHE):
        with open(WORD_LIST_CACHE) as f:
            words = [w.strip().lower() for w in f if len(w.strip()) == 5 and w.strip().isalpha()]
        if words:
            return sorted(set(words))

    # Try to download
    try:
        import urllib.request
        print(f"Downloading word list from {WORD_LIST_URL} ...")
        with urllib.request.urlopen(WORD_LIST_URL, timeout=10) as resp:
            text = resp.read().decode("utf-8")
        with open(WORD_LIST_CACHE, "w") as f:
            f.write(text)
        words = [w.strip().lower() for w in text.splitlines() if len(w.strip()) == 5 and w.strip().isalpha()]
        print(f"Downloaded {len(words)} words and cached to {WORD_LIST_CACHE}")
        return sorted(set(words))
    except Exception as exc:
        print(f"Warning: could not download word list ({exc}), using built-in list.")

    # Built-in fallback
    return sorted(set(w.lower() for w in _FALLBACK_WORDS.split() if len(w) == 5 and w.isalpha()))


_FALLBACK_WORDS = """
about above abuse actor acute admit adopt adult after again agent agree ahead
alarm album alert alien align alive alley allow alone along alter angel anger
angle angry ankle annex apart apple apply apron arena argue arise armor aroma
arose array arrow aside asset attic audio audit avoid awake award aware awful
bacon badge badly basic basin basis batch beach beard beast began begin being
belly below bench birth black blade blame bland blank blast blaze bleed blend
bless blink block blood bloom blown blunt board bonus boost booth bored bound
brain brave bread break breed brick bride brief bring brink brisk broad broke
brook broom brush buddy build built bulge bunch buyer cabin candy carry catch
cause cease chain chair chalk chaos charm chart chase cheap check cheek cheer
chess chest chime china chips choir choke chose civil claim clamp clash clasp
class clean clear clerk click cliff climb cling clock close cloth cloud coast
color comet comic coral count court cover craft crane crash crawl crazy cream
creek crime crisp cross crust curly curse curve daily dance dealt death decay
delay dense depth devil diary digit disco ditch dizzy dodge doing doubt dough
draft drain drama drank drawn dream dress dried drift drink drive drone drove
drown dusty dwarf dying eager eagle early earth eight elect elbow elite empty
enemy enjoy enter entry equal error essay event every exact exist extra faint
fairy false fancy fatal fault feast field fiery fifth fifty fight final first
fixed flake flame flare flash flask fleet flesh flock flood floor flour flown
fluid focus force forge forth found frail frame frank fraud fresh front frost
fruit funny flush giant given gland glass glide gloom gloss glove going grace
grade grain grand grant grasp grass grave great green greet grief grind grove
grown gruff guard guile guise gusto habit happy harsh haste haven heart heavy
heist hence hinge hoist holly honey honor horse hotel house human hurry hyena
ideal image imply index indie infer inner input inter intro irony issue ivory
jewel juice juicy jumpy label large laser later laugh layer leapt lease leave
level light lilac limit lingo liver lodge logic loose lotus lower lucky lurid
magic major maker manor maple march match mayor metal minor minus mixed model
money month moral mower muddy murky music naive naval nexus night noble noise
north noted novel nudge ocean occur offer often olive omega onset opera orbit
order other outer paint panic paper party pasta patch pause peach pearl phone
photo piano pilot pitch pixel place plain plane plank plant plate plaza plead
point polar poppy pound power press price pride prime print prior prism probe
proxy prune pulse punch pupil purse quake queen query quest queue quick quiet
quota quote radar radio raise rally ranch range rapid raven reach rebel reign
relax repay rider ridge rifle rigid risky rival river rogue rouge rough round
route royal ruddy ruler rumor rusty sadly saint salad scale scare scene scone
scope score scout seize sense serve seven shake shall shame shape share shark
sharp sheep sheer shelf shell shift shine shirt shock shoot shore short shout
shrug siege sight silly since sixth sixty skill skull slain slang slash slept
slice slide slime sloth smart smell snail snake sneak solar solve sonic sorry
south space spade spare spark speak spear spend spice spine spite split spoke
spoon sport spray squad stack staff stage stain stale stall stamp stand stark
start state steal steam steel steep steer stern stick stiff still stock stomp
stone stood stoop store storm story stove straw strip stung style sugar sunny
super swamp swear sweet swept swift swore table taint taken tally taste tawny
teach tense theme there these thick thing think thorn those three threw throw
thumb thump thyme tiger tight tired toast token total touch tough tower toxic
trace track trade trail train trait tramp trash trawl tread trend trial tribe
trick troop trout truck truly trust truth tunic tutor tweed twirl twist tying
ultra uncle union unity until upper upset urban usher usual utter vague valid
value valve vapor vault verse vigor viper viral virus visit visor vista vital
vivid vocal voice voter wacky wager waste watch water weary wedge weird whale
wheat wheel where which while white whole width wield witch witty woods world
worry worst worth would wrath wreck wring wrote yacht yearn yeast yield young
youth zebra zonal zoned bloom spree three brine groan bland stank creep crimp
swirl plumb truce scram blunt drool swoon perch birch tryst pluck sniff churn
kneel gruel prawn froth scald stomp brawl squab brawl crypt cleft clump stomp
glint clung crave drove clung glyph spook brood snort tuber rivet liner shady
borax coven chime chant stoic lilac lemur quail talon colic ember gripe tunic
skirt elope swamp groin mince finch scrub gloat joust strut bliss knack abbey
abbot abyss agony algae alloy amble amiss amuse annoy antic anvil apathy aptly
arbor ardor arduous arid armor aroma abyss atone attic augur avid baste batch
baton bawdy bayou beady beard berth bigot binge bland blare bleat bleed bleep
bliss bloat bloke bloom blotch blown bluff blunt blurs botch brace brash brawn
braze brood broth broil bruit brunt brusk burly cabal cache cadet cairn carte
catch chafe champ chide child chomp clasp cleft cling cloak clove clown clump
comet comic comfy could creak crest crimp crisp croon cruel crust crypt cupid
daffy daunt decoy defer delta depot diode drawl drool duchy dumpy dunce dusty
egret eject elite ember equip erupt etude evict evoke exert exile extra flank
flare flask flaunt fledge flint float floss flung flunk flute foamy forte foyer
freak frost froth froze frugal fudge frump gaunt gaudy gauze gavel giddy given
gizmo glare glean glint gloat gloss glove glyph gnash golem gouge gourd guava
guile guise gulch gully gusto gypsy hammy handy harpy heady hedge hefty helot
hertz hippo hitch hoary hobby holly homer homey horde hotly hovels hunky husky
hyper igloo inane incur inept inert inlay inset inter jaded jamb joint joust
knave kneel knell knife knock knoll knurl lance latch latent laxly leafy leaky
leapt leech liege lingo livid llama loamy loathe lobby lodge lofty loner
loner lunge lusty mafia mambo manic manor manly maple mauve mealy meaty
merit messy midst milky mimic minty mirth moldy molten morph motif mousy
muddy muggy mulch mummy murky musty nifty ninety nippy noble nifty nomad
notch noway nubby nutty nylon oaken oaken occur octet oddly offal omega
onset outdo ovoid pagan pasty patchy pesky petty phony pinch plaid plain
plait plank plasm plumb plume plunk poise pokey polka pommel poppy potty
pouty privy prone prong pronk proof prowl psalm pubic pudgy puffy pulpy
punky puppy purge purse pushy quaff qualm qualm quasi quirk quota radon
rajah rakish rally randy ratty reedy redux regal repel repot rider ripen
rivet rogue roomy rummy rupee rusty saggy salty sappy sassy savvy scald
scoff scold scone scrub scuff seedy serum shady shaky sheen shoal shorn
showy shrug silky sissy sitar sixty skimp skunk sleek slept slick slink
slimy sloop slosh slump slunk slurp smack smear smirk smite smock snaky
snide sniff snore snout soggy solar sorry sparky speck spiky spill spiny
spire spook spout spray spree sprig spunk squab squat squaw squib stomp
stony stony stoat stomp strep strew strop strut stung study stump stunk
squint squelch shuck slung swipe swoop syrup tabby tacky taffy tangy taunt
tepid terse theme thick tidal tipsy toffy topaz torch touchy toxic tramp
trawl trend trite troop trove truce tryst tubby tulip tulle tutor twang
tweak tweed twerp twill twine twirl twitch tying ulcer ultra umbra unify
unzip upper urban usurp uvula vague vapor vapid venom vigil viper viral
vivid vixen vomit vowed vying wacky wader waifu wanly waver weedy wimpy
windy winky wired wizen woken wooly wormy wrung wussy yacht yeoman yield
yucky yukky zappy zappy zingy zippy zooms
"""

WORDS: list[str] = _load_words()

# A known-good opening guess (high letter-frequency word)
DEFAULT_FIRST_GUESS = "crane"

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def get_feedback(guess: str, answer: str) -> str:
    """Return a 5-char feedback string (G/Y/B) for *guess* vs *answer*."""
    guess = guess.lower()
    answer = answer.lower()
    feedback = ["B"] * 5
    answer_pool = list(answer)

    # First pass: greens
    for i in range(5):
        if guess[i] == answer_pool[i]:
            feedback[i] = "G"
            answer_pool[i] = None  # consumed

    # Second pass: yellows
    for i in range(5):
        if feedback[i] == "G":
            continue
        if guess[i] in answer_pool:
            feedback[i] = "Y"
            answer_pool[answer_pool.index(guess[i])] = None  # consumed

    return "".join(feedback)


def filter_words(candidates: list[str], history: list[tuple[str, str]]) -> list[str]:
    """
    Filter *candidates* by applying every (guess, feedback) pair in *history*.
    """
    for guess, feedback in history:
        guess = guess.lower()
        feedback = feedback.upper()

        # Gather per-letter information
        info: dict[str, dict] = {}
        for letter in guess:
            if letter not in info:
                info[letter] = {"green": [], "yellow": [], "black": []}

        for i, (letter, fb) in enumerate(zip(guess, feedback)):
            info[letter][fb == "G" and "green" or fb == "Y" and "yellow" or "black"].append(i)

        # Build constraints from gathered info
        min_counts: dict[str, int] = {}
        exact_counts: dict[str, int] = {}  # set when letter has ≥1 black
        green_pos: dict[int, str] = {}     # position -> required letter
        excl_pos: dict[str, set[int]] = {} # letter -> forbidden positions

        for letter, d in info.items():
            min_counts[letter] = len(d["green"]) + len(d["yellow"])
            if d["black"]:
                exact_counts[letter] = min_counts[letter]
            for pos in d["green"]:
                green_pos[pos] = letter
            if d["yellow"]:
                excl_pos.setdefault(letter, set()).update(d["yellow"])

        # Apply constraints to each candidate
        next_candidates = []
        for word in candidates:
            ok = True

            # Green positions must match
            for pos, letter in green_pos.items():
                if word[pos] != letter:
                    ok = False
                    break
            if not ok:
                continue

            # Letter counts and excluded positions
            for letter, mn in min_counts.items():
                cnt = word.count(letter)
                if cnt < mn:
                    ok = False
                    break
                if letter in exact_counts and cnt != exact_counts[letter]:
                    ok = False
                    break
                if letter in excl_pos:
                    for pos in excl_pos[letter]:
                        if word[pos] == letter:
                            ok = False
                            break
                if not ok:
                    break

            if ok:
                next_candidates.append(word)

        candidates = next_candidates

    return candidates


def score_word(word: str, candidates: list[str]) -> int:
    """
    Score *word* by summing per-candidate-pool letter frequencies for each
    unique letter in *word*.  Higher score = more information gained.
    """
    freq = Counter(letter for w in candidates for letter in set(w))
    return sum(freq[letter] for letter in set(word))


def best_guess(candidates: list[str], all_words: list[str]) -> str:
    """Return the highest-scoring candidate word."""
    if not candidates:
        return ""
    if len(candidates) <= 2:
        return candidates[0]
    return max(candidates, key=lambda w: score_word(w, candidates))


# ---------------------------------------------------------------------------
# Interactive helpers
# ---------------------------------------------------------------------------

def _validate_feedback(fb: str) -> bool:
    return len(fb) == 5 and all(c in "GYBgyb" for c in fb)


def _print_board(history: list[tuple[str, str]]) -> None:
    sep = "+" + "-" * 17 + "+"
    print(sep)
    for guess, feedback in history:
        colored = []
        for letter, fb in zip(guess.upper(), feedback.upper()):
            if fb == "G":
                colored.append(f"[G]{letter}")
            elif fb == "Y":
                colored.append(f"[Y]{letter}")
            else:
                colored.append(f"[ ]{letter}")
        print("| " + "  ".join(colored) + " |")
    print(sep)


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def interactive_mode(words: list[str]) -> None:
    """User plays Wordle; solver suggests guesses and collects feedback."""
    print("\n=== Wordle Solver – Interactive Mode ===")
    print("After each guess, enter feedback as 5 chars: G=green Y=yellow B=black")
    print("Type 'back' to undo the last guess, 'quit' to exit.\n")

    history: list[tuple[str, str]] = []
    attempt = 1

    while attempt <= 6:
        candidates = filter_words(words[:], history)

        guess = best_guess(candidates, words)
        print(f"Attempt {attempt}/6  ({len(candidates)} candidates remaining)")
        print(f"  Suggested guess: {guess.upper()}")

        # Allow the user to override the guess
        override = input("  Press Enter to use it, or type your own guess: ").strip().lower()
        if override == "quit":
            print("Bye!")
            return
        if override == "back":
            if history:
                undone = history.pop()
                attempt -= 1
                print(f"  Undid guess '{undone[0].upper()}'. Back to attempt {attempt}.\n")
                if history:
                    _print_board(history)
            else:
                print("  Nothing to undo.\n")
            continue
        if override and len(override) == 5 and override.isalpha():
            guess = override

        # Collect feedback
        while True:
            fb = input(f"  Feedback for '{guess.upper()}' (e.g. BGYBB): ").strip()
            if fb.lower() == "quit":
                print("Bye!")
                return
            if fb.lower() == "back":
                if history:
                    undone = history.pop()
                    attempt -= 1
                    print(f"  Undid guess '{undone[0].upper()}'. Back to attempt {attempt}.\n")
                    if history:
                        _print_board(history)
                else:
                    print("  Nothing to undo.\n")
                break  # restart the outer loop at the updated attempt
            if _validate_feedback(fb):
                history.append((guess, fb.upper()))
                _print_board(history)

                if fb.upper() == "GGGGG":
                    print(f"\nSolved in {attempt} attempt{'s' if attempt > 1 else ''}! The word was {guess.upper()}.\n")
                    return

                candidates = filter_words(words[:], history)
                if not candidates:
                    print("\nNo candidates left – double-check your feedback entries.\n")
                    return

                print(f"  Remaining candidates: {', '.join(c.upper() for c in candidates[:10])}"
                      + (" …" if len(candidates) > 10 else "") + "\n")
                attempt += 1
                break

            print("  Invalid – enter exactly 5 chars using G, Y, B.")

    if attempt > 6:
        candidates = filter_words(words[:], history)
        print(f"Could not solve in 6 attempts. Remaining: {', '.join(c.upper() for c in candidates)}\n")


def auto_mode(answer: str, words: list[str]) -> None:
    """Solver plays against a known answer and prints each step."""
    answer = answer.lower()
    if answer not in words:
        # Add it so the solver can actually find it
        words = words + [answer]

    print(f"\n=== Wordle Solver – Auto Mode  (answer: {answer.upper()}) ===\n")

    candidates = words[:]
    history: list[tuple[str, str]] = []

    for attempt in range(1, 7):
        guess = best_guess(candidates, words) if attempt > 1 else DEFAULT_FIRST_GUESS
        fb = get_feedback(guess, answer)
        history.append((guess, fb))

        print(f"Attempt {attempt}: {guess.upper()}  →  {fb}  "
              f"({len(candidates)} candidates before this guess)")
        _print_board(history)

        if fb == "GGGGG":
            print(f"Solved in {attempt} attempt{'s' if attempt > 1 else ''}!\n")
            return

        candidates = filter_words(candidates, [(guess, fb)])
        if not candidates:
            print("No candidates left – something went wrong.\n")
            return

    print(f"Failed to solve. Remaining candidates: {', '.join(c.upper() for c in candidates)}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wordle Solver – suggests optimal guesses.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--answer", metavar="WORD",
        help="Run in auto-solve mode against this answer (5 letters).",
    )
    parser.add_argument(
        "--wordlist", metavar="FILE",
        help="Path to a plain-text file with one 5-letter word per line.",
    )
    args = parser.parse_args()

    words = WORDS[:]
    if args.wordlist:
        try:
            with open(args.wordlist) as fh:
                extra = [w.strip().lower() for w in fh if len(w.strip()) == 5 and w.strip().isalpha()]
            words = sorted(set(words + extra))
            print(f"Loaded {len(extra)} words from {args.wordlist} ({len(words)} total).")
        except OSError as exc:
            print(f"Warning: could not read wordlist – {exc}")

    if args.answer:
        if len(args.answer) != 5 or not args.answer.isalpha():
            parser.error("--answer must be a 5-letter word.")
        auto_mode(args.answer, words)
    else:
        interactive_mode(words)


if __name__ == "__main__":
    main()
