🧰 Territory Injector for DayZ CE
Injects territory definitions (zombies, animals, custom packs) from modular XML files into a master chernarusplus.xml CE territory file — cleanly, safely, and without duplication.

🧠 What This Tool Does
Parses all .xml territory files in /input/ (except chernarusplus.xml)

Classifies each file:

"zombie" if filename includes zombie

Otherwise treated as an animal pack

For each <territory> block:

Extracts associated <zone>s

Skips duplicates already in CE file — even slightly different ones

Injects into:

<territory-type name="zombie_territories"> for zombies

Matching or new <territory-type> for animals

Automatically names anonymous territories using the first zone name

Deduplicates using: zone name, x, z, r, and d (defaults to "2")

Outputs: chernarusplus_injected.xml cleanly formatted

📁 Folder Structure
<pre> \\\plaintext 
project_root/
├── input/
│   ├── chernarusplus.xml          ← main CE territory file to inject into
│   ├── zombie_territories.xml     ← zombie territory packs
│   └── grizzlys.xml               ← animal-type packs
│
├── output/
│   └── chernarusplus_injected.xml  ← result after injection
│
├── backup/
│   └── chernarusplus_backup.xml    ← original CE file (pre-injection)
│
├── logs/
│   └── run.log                     ← summary of each injection run
│
├── utils/
│   ├── logger.py
│   └── color_generator.py
│
└── main.py                         ← entry point for the tool \\\ </pre>
⚙ How It Works Internally
💡 Injection Logic
Zombie files → inject into zombie_territories

If territory name is missing, uses first zone’s name

Animal files → territory-type is based on filename (e.g., grizzlys.xml → grizzlys)

New <territory-type> is created if needed

Territory name defaults to file name

🔍 Zone Deduplication Logic
Two zones are considered duplicates if all of the following match:

Attribute	Notes
name	e.g. "InfectedVillageTier1"
x	World X coordinate (string)
z	World Z coordinate
r	Spawn radius
d	Defaults to "2" if not present
This prevents subtle duplicates caused by inconsistencies in d values.

📝 Log Output Example
plaintext
📦 Backup created: backup/chernarusplus_backup.xml
✅ Parsed 3 blocks from zombie_territories.xml
✔ Injected 12 zones into zombie_territories (InfectedVillageTier1)
⏩ Skipped block (all zones already exist) for: Grizzlys in grizzlys
✅ Injection complete. 1 new blocks added.
🟡 3 zones skipped (already exist).
📄 Output saved to: output/chernarusplus_injected.xml
➕ How to Add New Territories
Drop your new XML file into the /input/ folder Example: firewolves.xml, fantazywolf.xml, zombie_newtown.xml

Run the tool — it will:

Backup the original

Parse and classify the new file

Match or create the proper <territory-type>

Deduplicate zones

Save output in /output/

❗ Don’t edit chernarusplus.xml manually. The tool handles injection, safety checks, and formatting.

🚨 Requirements
Input files must be valid XML

Each <territory> must contain at least one <zone> with x and z attributes

Zombie packs must provide zone name= values if the territory name is missing
