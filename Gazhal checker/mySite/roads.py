from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user
import re
import regex

roads = Blueprint('roads', __name__)

LONG_VOWELS = {"ा", "ी", "ू", "े", "ो", "ै", "ौ"}
SHORT_SOUNDS = {"ि", "ु", "ृ","ई","म","च","ज","त",""}

BEHER_PATTERNS = {
	(1, 2, 1): "फ़ऊल",
	(2, 2): "फ़ेलुन",
	(1, 2, 2): "फ़ऊलुन",
	(2, 1): "फ़ेल"
}

BEHER_COLORS = {
	"फ़ऊल": "green",
	"फ़ेलुन": "pink",
	"फ़ऊलुन": "blue",
	"फ़ेल": "grey"
}

EXCEPTION_CLUSTERS = {"पह", "दिल", "उस", "बिल", "मिल", "छल", "जल", "फल", "हल", "अब", "लक", "लफ़",
					 "जिस", "की", "कि", "ज़ल", "कर", "बी", "बि", "लक", "चल", "शी","रह", "थी", "था", "है",
					 "हूँ","मत", "बस", "ख़ु", "नज़", "शब", "मन", "तन", "ग़म", "फ़िर", "तू", "ख़त", "ज़ोर", "दम",
					 "दाम", "कसम", "रंग", "संग", "बात", "रात", "सफ़","बत","हम","बिन","कुछ","कह","तुम","तर"}

def partition_word(word):
	graphemes = regex.findall(r'\X', word)
	parts, i = [], 0
	while i < len(graphemes):
		if i + 1 < len(graphemes):
			cluster = graphemes[i] + graphemes[i + 1]
			if cluster in EXCEPTION_CLUSTERS:
				parts.append(cluster)
				i += 2
				continue
		parts.append(graphemes[i])
		i += 1
	return parts

def score_segment(seg):
	score = 0
	for ch in regex.findall(r'\X', seg):
		if any(m in ch for m in LONG_VOWELS):
			return 2  # Long vowel always means 2, no matter what
		if any(m in ch for m in SHORT_SOUNDS):
			score += 1
	return min(score, 2)

def detect_beher(line_scores):
	matches, claimed = [], set()
	sorted_patterns = sorted(BEHER_PATTERNS.items(), key=lambda x: -len(x[0]))
	for pattern, name in sorted_patterns:
		length = len(pattern)
		for i in range(len(line_scores) - length + 1):
			if any(j in claimed for j in range(i, i+length)):
				continue
			if tuple(line_scores[i:i+length]) == pattern:
				matches.append({
					"index": i,
					"end": i+length-1,
					"name": name,
					"data": list(pattern)
				})
				claimed.update(range(i, i+length))
	return matches

def apply_color(structure):
	for couplet in structure.values():
		for line in couplet.values():
			scores = []
			index_map = []
			for word_data in line.values():
				if isinstance(word_data, dict):
					for word, segments in word_data.items():
						for seg in segments:
							scores.append(segments[seg]["score"])
							index_map.append((word, seg))

			matches = detect_beher(scores)
			if matches:
				line["beher"] = {i+1: match for i, match in enumerate(matches)}

	for couplet in structure.values():
		matched_ranges = {}
		for line_no, line in couplet.items():
			if "beher" in line:
				for b in line["beher"].values():
					key = (b["index"], b["end"], b["name"])
					matched_ranges.setdefault(key, []).append(line_no)

		for (start, end, name), line_nos in matched_ranges.items():
			color = BEHER_COLORS.get(name, "green")
			for ln in line_nos:
				line = couplet[ln]
				i = 0
				for word_data in line.values():
					if isinstance(word_data, dict):
						for word, segments in word_data.items():
							for seg in segments:
								if start <= i <= end:
									segments[seg]["color"] = color
								i += 1

def analyze_ghazal(text):
	# Keep punctuation needed for splitting, remove other junk
	text = re.sub(r"[“”‘’\"…–—\-‐‑‒·؟?!:;<>«»()\[\]{}@#\$%&\*/\\^~`+=_₹]", "", text)

	structure = {}
	# Split by full couplet end markers (Danda / Double Danda)
	raw_couplets = [c.strip() for c in re.split(r"[।॥]", text) if c.strip()]

	for c_idx, couplet in enumerate(raw_couplets, start=1):
		structure[c_idx] = {}
		# Split each couplet into 2 lines at commas
		for l_idx, line in enumerate(couplet.split(","), start=1):
			line = line.strip()
			if not line:
				continue
			structure[c_idx][l_idx] = {}
			words = line.split()
			for w_idx, word in enumerate(words, start=1):
				segments = partition_word(word)
				structure[c_idx][l_idx][w_idx] = {
					word: {seg: {"score": score_segment(seg), "color": "null"} for seg in segments}
				}

	apply_color(structure)
	return structure


@roads.route('/home', methods=["GET", "POST"])
def home():
	if request.method == "POST":
		ghazal_text = request.form.get("Gazhal", "").strip()
		structured = analyze_ghazal(ghazal_text)
		print(structured)
		return render_template("home.html", lines=structured, user=current_user)
	return render_template("home.html", lines={}, user=current_user)

@roads.route('/')
def redirhome():
	return redirect(url_for("roads.home"))
