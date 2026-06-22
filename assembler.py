#!/usr/bin/env python3
"""Pat Fleet voice clip message assembler."""

from flask import Flask, send_file, jsonify, render_template_string
import os, json, re

app = Flask(__name__)
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pa")

# ── Categorization sets ───────────────────────────────────────────────────────

ORDINALS = {
    "first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth",
    "eleventh","twelveth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth",
    "eighteenth","nineteenth","twentieth","thirtieth","fortieth","fiftieth","sixtieth",
    "seventieth","eightieth","ninetieth","hundredth","thousandth","millionth","billionth",
}

NUMBERS_SPOKEN = {
    "zero","one","two","three","four","five","six","seven","eight","nine","ten",
    "eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen",
    "nineteen","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety",
    "hundred","thousand","million","billion","half","quarter","point",
    "dollars","dollar","cents","cent","penny","pennies","pound","pounds","pence",
    "sterling","euro","euros","percent",
}

STATES = {
    "alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware",
    "florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky",
    "louisiana","maine","maryland","massachusetts","michigan","minnesota","mississippi",
    "missouri","montana","nebraska","nevada","new-hampshire","new-jersey","new-mexico",
    "new-york","north-carolina","north-dakota","ohio","oklahoma","oregon","pennsylvania",
    "rhode-island","south-carolina","south-dakota","tennessee","texas","utah","vermont",
    "virginia","washington","west-virginia","wisconsin","wyoming",
}

CITIES = {
    "albuquerque","arlington","atlanta","austin","baltimore","boston","charlotte","chicago",
    "cleveland","colorado-springs","columbus","dallas","denver","detroit","el-paso",
    "fort-worth","fresno","honolulu","houston","indianapolis","jacksonville","kansas-city",
    "las-vegas","long-beach","los-angeles","memphis","mesa","miami","milwaukee",
    "minneapolis","nashville","new-orleans","oakland","oklahoma-city","omaha",
    "philadelphia","phoenix","portland","sacramento","saint-louis","san-antonio",
    "san-diego","san-francisco","san-jose","seattle","tucson","tulsa","virginia-beach",
    "washington-dc","wichita",
}

WEATHER = {
    "rain","rainfall","rainy","snow","snowing","snowy","fog","foggy","ice","icy",
    "wind","windy","cloudy","clouds","clear","sunny","sun","thunderstorm","lightning",
    "storm","tornado","hurricane","cyclone","typhoon","hail","sleet","sleeting",
    "freeze","freezing","weather","temperature","humidity","pressure","visibility",
    "altitude","barometric","celsius","fahrenheit","degrees","beaufort","doppler-radar",
    "national-weather-service","the-weather-at","for-the-weather","weather-station",
    "partly","mostly","scattered","patchy","high","low","chance-of","gale","severe",
    "rising","falling","clearing","changing","conditions","tide",
    "northerly","southerly","easterly","westerly","approaching","headed-towards",
    "turning-to","moving","bearing","heading",
}

TIME_WORDS = {
    "morning","afternoon","evening","midnight","tonight","tomorrow-night",
    "midnight-tonight","midnight-tomorrow-night","day","days","week","weeks",
    "month","months","year","years","hour","hours","minute","minutes","second","seconds",
    "time","date","daylight","gmt","eastern","central","mountain","pacific","european",
    "current-time-is","at-tone-time-exactly","what-time-it-is","what-time-it-is2",
    "enter-a-time","now","today","late","early","another-time","1-for-am-2-for-pm",
}

TECH = {
    "tcp","udp","ssh","ftp","http","dns","smtp","imap","pop","telnet","linux","windows",
    "unix","server","network","packet","port","protocol","channel","gigabits","gigabytes",
    "gigahertz","megabits","megabytes","megahertz","kilobits","kilobytes","kilohertz",
    "terabits","terabytes","bits","bytes","hertz","hz","uptime","load-average",
    "memory","disk","system","ping","ip","icmp","loss","simplex","duplex","frequency",
    "decode","encode","web","www-switchboard-com","doing-enum-lookup",
    "enum-lookup-failed","enum-lookup-successful","no-route-exists-to-dest",
    "cannot-complete-network-error","route-sip","q-dot-931","q-dot-9thirty1",
    "channel-insecure-warn","channel-secure","remote-base","repeater","variable",
    "node","status","portnumber","version","ssh","ssl",
}

DEPARTMENTS = {
    "accounting","billing","billing-and-collections","accounts-payable","accounts-receivable",
    "administration","auditing","business-development","cafeteria","claims","collections",
    "communications","company-dir-411","compliance","copy-center","counseling-services",
    "customer-accounts","customer-relations","customer-service","design","development",
    "directory","directory-assistance","distribution","engineering","facilities","finance",
    "food-service","food-services","health-center","helpdesk","housekeeping",
    "human-resources","information","inside-sales","internal-audit","investor-relations",
    "it-services","janitorial","legal","library","loss-prevention","maintenance",
    "management","manufacturing","marketing","motor-pool","new-accounts","office",
    "operations","order-desk","orders","outside-sales","personnel","planning",
    "presales-support","printing","production","projects","public-relations","purchasing",
    "quality-assurance","quality-control","rebates","reception","repair","research",
    "research-and-development","reservations","risk-management","room-service","sales",
    "sales-floor","security","shipping","shop","staffing","staff","store-accounting",
    "support","systems","technical-support","telesales","training","transportation",
    "travel","treasury","outside-transfer",
}

FUNNY = {
    "abandon-all-hope","all-your-base","away-naughty-boy","away-naughty-girl",
    "because-paranoid","blue-eyed-polar-bear","busy-hangovers","carried-away-by-monkeys",
    "could-lose-a-few-pounds","deadbeat","denial-of-service","dial-here-often",
    "gambling-drunk","giggle1","go-away1","go-away2","hang-on-a-second-angry",
    "hear-odd-noise","hear-toilet-flush","hello-world","i-dont-understand",
    "i-dont-understand2","i-dont-understand3","i-dont-understand4","i-dont-understand5",
    "i-grow-bored","infuriate-tech-staff","jedi-extension-trick","just-kidding-not-upset",
    "just-kidding-not-upset2","knock-knock","lots-o-monkeys","lyrics-louie-louie",
    "made-it-up","marryme","moron","moo1","moo2","nobody-but-chickens","not-taking-your-call",
    "oops1","oops2","oops3","one-small-step","one-small-step2","panic","perhaps-we-are",
    "perhaps-we-are2","plugh","quote","race","says-thats-stupid","self-destruct",
    "self-destruct-in","shiny-brass-lamp","someone-you-trust1","someone-you-trust2",
    "someone-you-trust3","something-terribly-wrong","sorry-cant-let-you-do-that",
    "sorry-cant-let-you-do-that2","sorry-cant-let-you-do-that3","system-crashed",
    "talking-to-myself","telephone-in-your-pocket","telephone-in-your-pocket2",
    "teletubbie-murder","that-tickles","the-monkeys-twice","there-is-no-customer-support",
    "tt-monkeysintro","tt-somethingwrong","tt-weasels","twisty-maze","uh-oh1","uh-oh2",
    "wait-offensive-sounds","walks-into-bar-mail","we-dont-have-tech-support",
    "weasels-eaten-phonesys","what-are-you-wearing","why-no-answer-mystery",
    "wrong-try-again-smarty","yeah","yes-dear","yes-dear2","you-seem-impatient",
    "you-sound-cute","groovy","asterisk-friend","for-louie-louie","all-your-base",
    "demo-congrats","demo-nogo","barn","barns","moo1","moo2","spy-agent",
    "tones-that-follow-are-for-the-deaf","crash","panic","oops1","oops2","oops3",
    "bad","moron","deadbeat","step-in-stream","beep","beeperr",
}

CONNECTORS = {
    "and","or","but","with","from","to","the","in","on","at","by","of","is","has",
    "was","not","if","then","this","that","a","up","down","for","your","our","my",
    "it","and-or","there-are","there-is-no","not-yet","currently","now","recently",
    "approximately","about","between","through","into","than","less-than","greater-than",
    "divided-by","times","plus","minus","point","per","within","towards","near","towards",
    "towards","past","after","before","during","while","also","too","very","quite",
    "slowly","quickly","early","late","already","still","yet","again","back",
    "comma","period","ampersand","semicolon","colon","hash","octothorpe","at-sign",
    "open-parenthesis","close-parenthesis","left-bracket","right-bracket",
    "backslash","pipe","splat","bar",
}

GREETINGS = {
    "hello-world","good","goodbye","welcome","morning","afternoon","evening",
    "thank-you","thanks-for-calling-today","thanks-for-using","thank-you-cooperation",
    "thank-you-for-calling","sorry","sorry2","im-sorry","we-apologize","were-sorry",
    "one-moment-please","hang-on-a-second","pls-hold-silent30","busy-pls-hold",
    "please-wait-connect-oncall-eng","please-try-again","please-try-again-later",
    "please-try","are-you-still-there","are-you-still-there2","good",
    "thnk-u-for-patience","wait-moment","auth-thankyou","privacy-thankyou",
    "queue-thankyou",
}

# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_ORDER = [
    "Numbers", "Ordinals", "Time", "Connectors", "Greetings",
    "US States", "US Cities", "Weather",
    "Departments", "Prompts",
    "Voicemail", "Conference", "Queue", "Agent", "Privacy",
    "Directory", "Calling Card", "Phrase Mgmt", "Monitor",
    "Tech", "Numeric IDs", "Fun & Easter Eggs",
    "Demo", "General",
]


CALL_HANDLING = {
    "call","call-forward","call-forwarding","call-fwd-cancelled","call-fwd-no-ans",
    "call-fwd-on-busy","call-fwd-parallel","call-fwd-unconditional","call-preempted",
    "call-quality-menu","call-requres","call-terminated","call-waiting","calls",
    "calls-taken-by","calls-waiting-for-rep","wakeup-call","wakeup-call-cancelled",
    "wakeup-daily","wakeup-for-daily","wakeup-for-one-time","wakeup-onetime",
    "not-rqsted-wakeup","rqsted-wakeup-for","this-is-yr-wakeup-call",
    "for-wakeup-call","for-a-daily-wakeup-call","to-rqst-wakeup-call",
    "to-cancel-wakeup","to-snooze-for","to-confirm-wakeup","wakeup-for-one-time",
    "pbx-invalid","pbx-invalidpark","pbx-transfer","outside-transfer",
    "transfer","call-preempted","connected","connecting","connection-failed",
    "connection-timed-out","disconnected","temp-disconnected","no-longer-in-service",
    "discon-or-out-of-service","in-service","terminated","terminating",
    "initiated","initiating","call-forward","call-fwd-cancelled",
    "all-circuits-busy-now","all-outgoing-lines-unavailable","cannot-complete-as-dialed",
    "cannot-complete-otherend-error","cannot-complete-temp-error",
    "check-number-dial-again","hangup-try-again","please-hang-up-and-dial-operator",
    "please-hang-up-and-try-again","pls-try-manually","pls-hold-while-try",
    "pls-wait-connect-call","pls-stay-on-line","pls-hold-silent30",
    "hold-or-dial-0","busy-pls-hold","one-moment-please","wtng-to-spk-w-rep",
    "all-reps-busy","nbdy-avail-to-take-call","first-in-line","in-the-queue",
    "in-the-line","you-are-caller-num","you-are-curr-call-num","avg-speed-answer",
    "est-hold-time-is","to-reach-first-rep","to-reach-operator","ext-or-zero",
    "extension","speed-dial","speed-dial-empty","speed","do-not-disturb",
    "roaming","local-authorities","limit-simul-calls","simul-call-limit-reached",
    "remote-already-in-this-mode","remote-already-in-this-mode-2",
    "feature-not-avail-line","option-is-invalid","option-not-implemented",
    "pbx-invalid","pbx-invalidpark","pbx-transfer",
    "call-preempted","call-terminated","call-waiting",
    "inbound","outbound",
}

CARD_EXTRA = {
    "card-balance-is","card-is-invalid","card-number","a-charge-for-this-svc",
    "a-collect-charge","a-collect-charge-of","a-connect-charge","a-connect-charge-of",
    "a-connect-charge","not-enough-credit","this-call-will-cost","cents-per-minute",
    "deposit","please-deposit","cents-please","on-monthly-tel-stment",
    "will-reflect-charge-of","to-hear-your-account-balance","your-account",
    "account-balance-is","not-auth-pstn","flagged-for-lea","lea-may-request-info",
    "international-call","believe-its-free",
}


def categorize(name: str) -> str:
    if name.startswith("vm-"):       return "Voicemail"
    if name.startswith("conf-"):     return "Conference"
    if name.startswith("queue-"):    return "Queue"
    if name.startswith("agent-"):    return "Agent"
    if name.startswith("privacy-"):  return "Privacy"
    if name.startswith("priv-"):     return "Privacy"
    if name.startswith("spy-"):      return "Monitor"
    if name.startswith("demo-"):     return "Demo"
    if name.startswith("astcc-"):    return "Calling Card"
    if name.startswith("pm-"):       return "Phrase Mgmt"
    if name.startswith("dir-"):      return "Directory"
    if name.startswith("tt-"):       return "Fun & Easter Eggs"
    if name.startswith("press-"):    return "Prompts"
    # Prompt-style prefixes
    if name.startswith("to-"):       return "Prompts"
    if name.startswith("pls-"):      return "Prompts"
    if name.startswith("please-"):   return "Prompts"
    if name.startswith("if-"):       return "Prompts"
    if name.startswith("enter-"):    return "Prompts"
    if name.startswith("T-"):        return "Prompts"
    if name.startswith("save-"):     return "Prompts"
    if name.startswith("say-"):      return "Prompts"
    if name.startswith("for-") and name not in ("for",): return "Prompts"
    # Explicit sets
    if name in ORDINALS:             return "Ordinals"
    if name in STATES:               return "US States"
    if name in CITIES:               return "US Cities"
    if name in NUMBERS_SPOKEN:       return "Numbers"
    if name in WEATHER:              return "Weather"
    if name in TIME_WORDS:           return "Time"
    if name in TECH:                 return "Tech"
    if name in DEPARTMENTS:          return "Departments"
    if name in FUNNY:                return "Fun & Easter Eggs"
    if name in CONNECTORS:           return "Connectors"
    if name in GREETINGS:            return "Greetings"
    if name in CALL_HANDLING:        return "Call Handling"
    if name in CARD_EXTRA:           return "Calling Card"
    if name == "conference" or name == "conference-call": return "Conference"
    if name.replace("-","").isdigit(): return "Numeric IDs"
    return "General"


TRANSCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcripts.json")
_transcripts = None

def get_transcripts():
    global _transcripts
    if _transcripts is None:
        if os.path.exists(TRANSCRIPT_FILE):
            with open(TRANSCRIPT_FILE) as f:
                _transcripts = json.load(f)
        else:
            _transcripts = {}
    return _transcripts


# ── Subdir metadata ───────────────────────────────────────────────────────────

SUBDIR_CATEGORY = {
    "digits":   "Digits",
    "letters":  "Letters",
    "phonetic": "Phonetic",
    "ha":       "Home Automation",
    "wx":       "Weather Station",
    "silence":  "Silence",
    "dictate":  "Dictate",
    "followme": "Follow Me",
}

PHONETIC_NAMES = {
    "a_p":"Alpha","b_p":"Bravo","c_p":"Charlie","d_p":"Delta","e_p":"Echo",
    "f_p":"Foxtrot","g_p":"Golf","h_p":"Hotel","i_p":"India","j_p":"Juliet",
    "k_p":"Kilo","l_p":"Lima","m_p":"Mike","n_p":"November","o_p":"Oscar",
    "p_p":"Papa","q_p":"Quebec","r_p":"Romeo","s_p":"Sierra","t_p":"Tango",
    "u_p":"Uniform","v_p":"Victor","w_p":"Whiskey","x_p":"X-ray",
    "y_p":"Yankee","z_p":"Zulu","9_p":"Nine","niner":"Niner",
}

MONTH_NAMES = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
DAY_NAMES   = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]


def subdir_label(subdir: str, stem: str) -> str:
    """Human-readable label for a clip from a subdirectory."""
    inflected = stem.endswith("_")
    base = stem[:-1] if inflected else stem
    suffix = " ·" if inflected else ""  # · marks compound/inflected form

    if subdir == "phonetic":
        return PHONETIC_NAMES.get(base, base) + suffix

    if subdir == "digits":
        if base.startswith("mon-"):
            return MONTH_NAMES[int(base[4:])] + suffix
        if base.startswith("day-"):
            return DAY_NAMES[int(base[4:])] + suffix
        if base.startswith("h-"):
            return base[2:] + " o'clock" + suffix
        if base == "a-m":   return "AM" + suffix
        if base == "p-m":   return "PM" + suffix
        if base == "oh":    return "oh" + suffix
        return base.replace("-", " ") + suffix

    if subdir == "letters":
        specials = {
            "at":"@","dash":"-","dollar":"$","dot":".","equals":"=",
            "exclaimation-point":"!","plus":"+","slash":"/","space":"(space)","zed":"Z",
        }
        if base in specials:
            return specials[base] + suffix
        return base.upper() + suffix

    if subdir == "silence":
        return base + "s silence"

    return base.replace("-", " ").replace("_", " ")


def scan_clips():
    """
    Walk AUDIO_DIR recursively and return a dict:
      { clip_name: (rel_path_to_file, subdir_or_None) }
    clip_name uses forward-slash for subdir clips: "digits/0", "letters/a", etc.
    Top-level clips keep their flat names.
    """
    found = {}

    def _add(name, relpath, subdir):
        # prefer .ulaw.wav over plain .wav
        if name in found and not relpath.endswith(".ulaw.wav"):
            return
        found[name] = (relpath, subdir)

    for entry in sorted(os.scandir(AUDIO_DIR), key=lambda e: e.name):
        if entry.is_dir() and entry.name not in ("ulaws",):
            subdir = entry.name
            if subdir not in SUBDIR_CATEGORY:
                continue
            for f in sorted(os.scandir(entry.path), key=lambda e: e.name):
                if not f.name.endswith(".wav"):
                    continue
                if f.name.endswith(".ulaw.wav"):
                    stem = f.name[:-9]
                else:
                    stem = f.name[:-4]
                clip_name = subdir + "/" + stem
                relpath = subdir + "/" + f.name
                _add(clip_name, relpath, subdir)
        elif entry.is_file() and entry.name.endswith(".wav"):
            fname = entry.name
            if fname.endswith(".ulaw.wav"):
                stem = fname[:-9]
            else:
                stem = fname[:-4]
            _add(stem, fname, None)

    return found


def load_clips():
    """Return sorted list of clip dicts."""
    transcripts = get_transcripts()
    all_clips = scan_clips()

    clips = []
    for name, (relpath, subdir) in sorted(all_clips.items()):
        if subdir:
            stem = name.split("/", 1)[1]
            label = subdir_label(subdir, stem)
            category = SUBDIR_CATEGORY[subdir]
        else:
            label = name.replace("-", " ")
            category = categorize(name)

        clips.append({
            "name": name,
            "file": relpath,
            "category": category,
            "label": label,
            "transcript": transcripts.get(name, ""),
        })
    return clips


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/clips")
def api_clips():
    return jsonify(load_clips())


@app.route("/audio/<path:filename>")
def audio(filename):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.abspath(path).startswith(os.path.abspath(AUDIO_DIR)):
        return "Forbidden", 403
    if not os.path.exists(path):
        return "Not found", 404
    return send_file(path, mimetype="audio/wav")


# ── HTML ──────────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pat Fleet Message Assembler</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0f1117;
      --surface: #1a1d27;
      --surface2: #22263a;
      --border: #2e3352;
      --accent: #5b6cf0;
      --accent-hover: #7080ff;
      --accent-dim: #2a3060;
      --text: #e2e6ff;
      --text-dim: #8890b0;
      --red: #e05060;
      --green: #40c080;
      --yellow: #e0c040;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* ── Header ── */
    header {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }
    header h1 {
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 0.02em;
      color: var(--text);
    }
    header h1 span { color: var(--accent); }
    #search {
      flex: 1;
      max-width: 380px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      padding: 6px 10px;
      font-size: 14px;
      outline: none;
      transition: border-color .15s;
    }
    #search:focus { border-color: var(--accent); }
    #search::placeholder { color: var(--text-dim); }
    #count-label {
      margin-left: auto;
      font-size: 12px;
      color: var(--text-dim);
    }

    /* ── Layout ── */
    .main-area {
      display: flex;
      flex: 1;
      overflow: hidden;
    }

    /* ── Sidebar ── */
    #sidebar {
      width: 175px;
      background: var(--surface);
      border-right: 1px solid var(--border);
      overflow-y: auto;
      flex-shrink: 0;
      padding: 8px 0;
    }
    .cat-btn {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 6px 12px;
      background: none;
      border: none;
      color: var(--text-dim);
      font-size: 12px;
      text-align: left;
      cursor: pointer;
      border-left: 3px solid transparent;
      transition: color .1s, background .1s;
    }
    .cat-btn:hover { background: var(--surface2); color: var(--text); }
    .cat-btn.active {
      color: var(--text);
      border-left-color: var(--accent);
      background: var(--accent-dim);
    }
    .cat-count {
      font-size: 10px;
      background: var(--surface2);
      border-radius: 10px;
      padding: 1px 5px;
    }
    .cat-btn.active .cat-count { background: var(--accent-dim); }

    /* ── Clip grid ── */
    #clip-area {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
    }
    #clip-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      align-content: flex-start;
    }
    .clip-btn {
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 5px;
      color: var(--text-dim);
      font-size: 11.5px;
      padding: 4px 8px;
      cursor: grab;
      transition: background .1s, border-color .1s, color .1s;
      user-select: none;
      text-align: left;
      display: flex;
      flex-direction: column;
      gap: 1px;
      position: relative;
    }
    .clip-btn:active { cursor: grabbing; }
    .clip-btn:hover {
      background: var(--accent-dim);
      border-color: var(--accent);
      color: var(--text);
    }
    .clip-btn.playing {
      border-color: var(--green);
      color: var(--green);
      background: #0a2010;
    }
    .clip-btn .play-icon {
      position: absolute;
      top: 3px; right: 5px;
      font-size: 9px;
      opacity: 0;
      transition: opacity .1s;
      pointer-events: none;
    }
    .clip-btn:hover .play-icon { opacity: 0.5; }
    .clip-btn.playing .play-icon { opacity: 1; content: "■"; }
    .clip-name { white-space: nowrap; padding-right: 12px; }
    .clip-transcript {
      font-size: 10px;
      opacity: 0.6;
      font-style: italic;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 180px;
    }
    .no-results {
      color: var(--text-dim);
      font-size: 13px;
      padding: 20px;
    }

    /* ── Sequence tray ── */
    #tray {
      border-top: 1px solid var(--border);
      background: var(--surface);
      flex-shrink: 0;
    }
    #tray-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-bottom: 1px solid var(--border);
    }
    #tray-header span { font-size: 12px; color: var(--text-dim); }
    .tray-btn {
      padding: 5px 12px;
      border-radius: 5px;
      border: none;
      font-size: 12px;
      cursor: pointer;
      font-weight: 600;
      transition: opacity .1s;
    }
    .tray-btn:disabled { opacity: .35; cursor: default; }
    #btn-play { background: var(--accent); color: #fff; }
    #btn-play:not(:disabled):hover { background: var(--accent-hover); }
    #btn-stop { background: var(--surface2); color: var(--text-dim); border: 1px solid var(--border); }
    #btn-stop:not(:disabled):hover { color: var(--red); border-color: var(--red); }
    #btn-clear { background: var(--surface2); color: var(--text-dim); border: 1px solid var(--border); }
    #btn-clear:not(:disabled):hover { color: var(--red); border-color: var(--red); }
    #seq-label { font-size: 11px; color: var(--text-dim); margin-left: auto; }
    #progress-bar {
      height: 2px;
      background: var(--accent);
      width: 0;
      transition: width .1s;
    }

    #sequence {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      padding: 8px 12px;
      min-height: 46px;
      max-height: 110px;
      overflow-y: auto;
      align-content: flex-start;
      transition: background .15s;
      border-radius: 4px;
    }
    #sequence.drag-over {
      background: rgba(91,108,240,.08);
      outline: 2px dashed var(--accent);
      outline-offset: -2px;
    }
    .seq-chip {
      display: flex;
      align-items: center;
      gap: 4px;
      background: var(--accent-dim);
      border: 1px solid var(--accent);
      border-radius: 4px;
      padding: 3px 6px;
      font-size: 11px;
      cursor: grab;
      user-select: none;
      color: var(--text);
      transition: opacity .1s;
      position: relative;
    }
    .seq-chip:active { cursor: grabbing; }
    .seq-chip.seq-playing {
      background: var(--green);
      border-color: var(--green);
      color: #000;
    }
    .seq-chip.dragging { opacity: .35; }
    .seq-chip .del {
      color: var(--text-dim);
      font-size: 13px;
      line-height: 1;
      cursor: pointer;
      padding: 0 2px;
      border-radius: 2px;
    }
    .seq-chip .del:hover { color: var(--red); }
    /* insertion cursor shown between chips during drag */
    .seq-insert {
      width: 2px;
      min-width: 2px;
      height: 26px;
      background: var(--accent);
      border-radius: 2px;
      align-self: center;
      flex-shrink: 0;
      box-shadow: 0 0 6px var(--accent);
    }
    #empty-msg {
      font-size: 12px;
      color: var(--text-dim);
      line-height: 30px;
      padding: 0 4px;
      pointer-events: none;
    }
  </style>
</head>
<body>

<header>
  <h1>Pat Fleet <span>Message Assembler</span></h1>
  <input id="search" type="text" placeholder="Search clips…" autocomplete="off">
  <span id="count-label">loading…</span>
</header>

<div class="main-area">
  <nav id="sidebar"></nav>
  <div id="clip-area">
    <div id="clip-grid"></div>
  </div>
</div>

<div id="tray">
  <div id="tray-header">
    <button class="tray-btn" id="btn-play" disabled>▶ Play</button>
    <button class="tray-btn" id="btn-stop" disabled>■ Stop</button>
    <button class="tray-btn" id="btn-clear" disabled>✕ Clear</button>
    <span id="seq-label">Click a clip to preview · Drag to timeline to add</span>
  </div>
  <div id="progress-bar"></div>
  <div id="sequence"><span id="empty-msg">Sequence is empty</span></div>
</div>

<script>
(() => {
  let allClips = [];
  let sequence = [];
  let previewAudio = null;       // audio playing from grid preview
  let seqAudio = null;           // audio playing in sequence
  let isPlaying = false;
  let activeCategory = "All";

  // drag state
  let dragSource = null;         // 'grid' | 'seq'
  let dragClip = null;           // clip being dragged from grid
  let dragSeqIdx = null;         // index being dragged within seq
  let insertIdx = null;          // where to drop in seq

  const grid      = document.getElementById("clip-grid");
  const sidebar   = document.getElementById("sidebar");
  const seqEl     = document.getElementById("sequence");
  const searchEl  = document.getElementById("search");
  const countLbl  = document.getElementById("count-label");
  const btnPlay   = document.getElementById("btn-play");
  const btnStop   = document.getElementById("btn-stop");
  const btnClear  = document.getElementById("btn-clear");
  const seqLbl    = document.getElementById("seq-label");
  const progBar   = document.getElementById("progress-bar");

  // ── Load ───────────────────────────────────────────────────────────────────
  fetch("/api/clips").then(r => r.json()).then(clips => {
    allClips = clips;
    buildSidebar();
    renderGrid();
  });

  // ── Sidebar ────────────────────────────────────────────────────────────────
  function buildSidebar() {
    const counts = { All: allClips.length };
    for (const c of allClips) counts[c.category] = (counts[c.category] || 0) + 1;

    const order = [
      "All",
      "Digits","Letters","Phonetic","Silence",
      "Numbers","Ordinals","Time","Connectors","Greetings",
      "US States","US Cities","Weather","Weather Station",
      "Home Automation",
      "Departments","Prompts","Call Handling",
      "Voicemail","Conference","Queue","Agent","Privacy",
      "Directory","Calling Card","Phrase Mgmt","Monitor",
      "Dictate","Follow Me",
      "Tech","Numeric IDs","Fun & Easter Eggs","Demo","General",
    ];

    sidebar.innerHTML = "";
    for (const cat of order) {
      if (cat !== "All" && !counts[cat]) continue;
      const btn = document.createElement("button");
      btn.className = "cat-btn" + (cat === activeCategory ? " active" : "");
      btn.innerHTML = `<span>${cat}</span><span class="cat-count">${counts[cat] || 0}</span>`;
      btn.addEventListener("click", () => {
        activeCategory = cat;
        document.querySelectorAll(".cat-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        renderGrid();
      });
      sidebar.appendChild(btn);
    }
  }

  // ── Grid ───────────────────────────────────────────────────────────────────
  function renderGrid() {
    const q = searchEl.value.toLowerCase().trim();
    const filtered = allClips.filter(c => {
      if (activeCategory !== "All" && c.category !== activeCategory) return false;
      if (q && !c.name.includes(q) && !c.label.includes(q) &&
          !(c.transcript && c.transcript.toLowerCase().includes(q))) return false;
      return true;
    });

    countLbl.textContent = filtered.length + " clips";
    grid.innerHTML = "";

    if (!filtered.length) {
      const p = document.createElement("p");
      p.className = "no-results";
      p.textContent = "No clips match.";
      grid.appendChild(p);
      return;
    }

    for (const clip of filtered) {
      const btn = document.createElement("button");
      btn.className = "clip-btn";
      btn.draggable = true;
      btn.title = clip.name + "  |  " + clip.category +
                  (clip.transcript ? "\\n" + clip.transcript : "");

      const nameEl = document.createElement("span");
      nameEl.className = "clip-name";
      nameEl.textContent = clip.label;
      btn.appendChild(nameEl);

      if (clip.transcript) {
        const tx = document.createElement("span");
        tx.className = "clip-transcript";
        tx.textContent = clip.transcript;
        btn.appendChild(tx);
      }

      const icon = document.createElement("span");
      icon.className = "play-icon";
      icon.textContent = "▶";
      btn.appendChild(icon);

      // Click → preview (toggle)
      btn.addEventListener("click", () => {
        if (btn.classList.contains("playing")) {
          stopPreview();
        } else {
          playPreview(clip, btn);
        }
      });

      // Drag from grid → add to timeline
      btn.addEventListener("dragstart", e => {
        dragSource = "grid";
        dragClip = clip;
        e.dataTransfer.effectAllowed = "copy";
        e.dataTransfer.setData("text/plain", clip.name);
        // Ghost label
        const ghost = document.createElement("div");
        ghost.textContent = clip.label;
        ghost.style.cssText =
          "position:absolute;top:-999px;background:#5b6cf0;color:#fff;" +
          "padding:4px 8px;border-radius:4px;font-size:12px;white-space:nowrap";
        document.body.appendChild(ghost);
        e.dataTransfer.setDragImage(ghost, 0, 0);
        setTimeout(() => ghost.remove(), 0);
      });

      btn.addEventListener("dragend", () => { dragSource = null; dragClip = null; });

      grid.appendChild(btn);
    }
  }

  searchEl.addEventListener("input", renderGrid);

  // ── Grid preview ───────────────────────────────────────────────────────────
  function playPreview(clip, btn) {
    stopPreview();
    const audio = new Audio("/audio/" + encodeURIComponent(clip.file));
    previewAudio = audio;
    btn.classList.add("playing");
    btn.querySelector(".play-icon").textContent = "■";
    audio.play();
    audio.addEventListener("ended", () => {
      btn.classList.remove("playing");
      btn.querySelector(".play-icon").textContent = "▶";
      if (previewAudio === audio) previewAudio = null;
    });
  }

  function stopPreview() {
    if (previewAudio) { previewAudio.pause(); previewAudio = null; }
    document.querySelectorAll(".clip-btn.playing").forEach(b => {
      b.classList.remove("playing");
      const ic = b.querySelector(".play-icon");
      if (ic) ic.textContent = "▶";
    });
  }

  // ── Timeline drag-and-drop ─────────────────────────────────────────────────
  seqEl.addEventListener("dragover", e => {
    if (!dragSource) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = dragSource === "grid" ? "copy" : "move";
    seqEl.classList.add("drag-over");
    insertIdx = computeInsertIdx(e.clientX, e.clientY);
    renderSequence(insertIdx);
  });

  seqEl.addEventListener("dragleave", e => {
    if (!seqEl.contains(e.relatedTarget)) {
      seqEl.classList.remove("drag-over");
      insertIdx = null;
      renderSequence();
    }
  });

  seqEl.addEventListener("drop", e => {
    e.preventDefault();
    seqEl.classList.remove("drag-over");
    const idx = insertIdx ?? sequence.length;

    if (dragSource === "grid" && dragClip) {
      sequence.splice(idx, 0, { ...dragClip, uid: Date.now() + Math.random() });
    } else if (dragSource === "seq" && dragSeqIdx !== null) {
      const moved = sequence.splice(dragSeqIdx, 1)[0];
      const dest = dragSeqIdx < idx ? idx - 1 : idx;
      sequence.splice(dest, 0, moved);
    }

    dragSource = null; dragClip = null; dragSeqIdx = null; insertIdx = null;
    renderSequence();
  });

  function computeInsertIdx(mx, my) {
    const chips = [...seqEl.querySelectorAll(".seq-chip")];
    if (!chips.length) return 0;
    for (let i = 0; i < chips.length; i++) {
      const r = chips[i].getBoundingClientRect();
      if (mx < r.left + r.width / 2) return i;
    }
    return chips.length;
  }

  // ── Sequence render ────────────────────────────────────────────────────────
  function renderSequence(dropAt) {
    seqEl.innerHTML = "";

    if (!sequence.length) {
      const msg = document.createElement("span");
      msg.id = "empty-msg";
      msg.textContent = "Drag clips here to build a message";
      seqEl.appendChild(msg);
      btnPlay.disabled = true;
      btnClear.disabled = true;
      seqLbl.textContent = "Drag clips here to build a message";
      progBar.style.width = "0";
      return;
    }

    btnPlay.disabled = isPlaying;
    btnClear.disabled = false;
    seqLbl.textContent = sequence.map(c => c.label).join(" · ");

    for (let i = 0; i < sequence.length; i++) {
      // Insertion cursor before this chip
      if (dropAt === i) seqEl.appendChild(makeCursor());

      const item = sequence[i];
      const chip = document.createElement("div");
      chip.className = "seq-chip";
      chip.draggable = true;
      chip.dataset.idx = i;
      chip.innerHTML = `<span>${item.label}</span><span class="del" data-idx="${i}">×</span>`;

      chip.querySelector(".del").addEventListener("click", e => {
        e.stopPropagation();
        sequence.splice(+e.target.dataset.idx, 1);
        renderSequence();
      });

      chip.addEventListener("dragstart", e => {
        dragSource = "seq";
        dragSeqIdx = i;
        chip.classList.add("dragging");
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", item.name);
      });

      chip.addEventListener("dragend", () => {
        dragSource = null; dragSeqIdx = null; insertIdx = null;
        chip.classList.remove("dragging");
        renderSequence();
      });

      seqEl.appendChild(chip);
    }

    // Cursor at end
    if (dropAt === sequence.length) seqEl.appendChild(makeCursor());
  }

  function makeCursor() {
    const el = document.createElement("div");
    el.className = "seq-insert";
    return el;
  }

  // ── Sequence playback ──────────────────────────────────────────────────────
  async function playSequence() {
    if (!sequence.length || isPlaying) return;
    stopPreview();
    isPlaying = true;
    btnPlay.disabled = true;
    btnStop.disabled = false;
    btnClear.disabled = true;

    for (let i = 0; i < sequence.length; i++) {
      if (!isPlaying) break;
      const item = sequence[i];
      progBar.style.width = (i / sequence.length * 100) + "%";
      document.querySelectorAll(".seq-chip").forEach((c, ci) =>
        c.classList.toggle("seq-playing", ci === i));

      await new Promise(resolve => {
        const audio = new Audio("/audio/" + encodeURIComponent(item.file));
        seqAudio = audio;
        audio.onended = resolve;
        audio.onerror = resolve;
        audio.play().catch(resolve);
      });
    }
    stopPlayback();
  }

  function stopPlayback() {
    isPlaying = false;
    if (seqAudio) { seqAudio.pause(); seqAudio = null; }
    document.querySelectorAll(".seq-chip.seq-playing").forEach(c => c.classList.remove("seq-playing"));
    progBar.style.width = "0";
    btnPlay.disabled = sequence.length === 0;
    btnStop.disabled = true;
    btnClear.disabled = sequence.length === 0;
  }

  btnPlay.addEventListener("click", playSequence);
  btnStop.addEventListener("click", stopPlayback);
  btnClear.addEventListener("click", () => { stopPlayback(); sequence = []; renderSequence(); });

  document.addEventListener("keydown", e => {
    if (e.target === searchEl) return;
    if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      isPlaying ? stopPlayback() : playSequence();
    }
    if (e.key === "Escape") { stopPlayback(); sequence = []; renderSequence(); }
  });
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    print(f"Starting Pat Fleet Message Assembler…")
    print(f"Open http://localhost:{args.port} in your browser")
    print()
    print("Controls:")
    print("  Left-click a clip  → add to sequence")
    print("  Right-click a clip → preview (play once)")
    print("  Space/Enter        → play / stop sequence")
    print("  Escape             → stop and clear")
    app.run(host="0.0.0.0", debug=False, port=args.port)
