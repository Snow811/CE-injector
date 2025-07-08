import os
import xml.etree.ElementTree as ET
import hashlib
from utils.color_generator import generate_color_rgba
from utils.logger import log

# 🔍 Dynamically detect map file
ce_files = [f for f in os.listdir("ce") if f.endswith(".xml")]
if len(ce_files) != 1:
    raise RuntimeError("❌ Place exactly one CE .xml file in the /ce/ folder.")
MAP_FILE = ce_files[0]
MAP_BASENAME = MAP_FILE.replace(".xml", "")

# Paths
CE_PATH = f"ce/{MAP_FILE}"
OUTPUT_PATH = f"output/{MAP_BASENAME}_injected.xml"

def indent(elem, level=0):
    i = "\n" + "    " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

def normalized_zone_sig(zone_dict):
    return (
        zone_dict.get("name", "").strip().lower(),
        zone_dict.get("x", "").strip(),
        zone_dict.get("z", "").strip(),
        zone_dict.get("r", "").strip(),
        zone_dict.get("d", "2").strip(),
    )

def fuzzy_match(a, b):
    return a.lower() in b.lower() or b.lower() in a.lower()

def backup_ce_file():
    os.makedirs("backup", exist_ok=True)
    with open(CE_PATH, "r", encoding="utf-8") as src, open(f"backup/{MAP_BASENAME}_backup.xml", "w", encoding="utf-8") as dst:
        dst.write(src.read())
    log(f"📦 Backup created: backup/{MAP_BASENAME}_backup.xml")

def find_all_territory_files():
    return [
        os.path.join("input", f)
        for f in os.listdir("input")
        if f.endswith(".xml")
    ]

def parse_territory_files(file_paths):
    territories = []
    for path in file_paths:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            count = 0

            for territory in root.iter("territory"):
                zones = []
                for zone in territory.findall("zone"):
                    if "x" in zone.attrib and "z" in zone.attrib:
                        zones.append(zone.attrib.copy())

                if not zones:
                    continue

                color = territory.attrib.get("color")
                name_attr = territory.attrib.get("name")
                filename_base = os.path.splitext(os.path.basename(path))[0]
                is_zombie = "zombie" in filename_base.lower()

                territory_type_name = "zombie_territories" if is_zombie else filename_base
                t_name = name_attr or (None if is_zombie else filename_base)
                color = color or str(generate_color_rgba(t_name or filename_base, []))

                territories.append({
                    "type": territory_type_name,
                    "territory_name": t_name,
                    "color": color,
                    "zones": zones
                })
                count += 1

            log(f"✅ Parsed {count} blocks from {os.path.basename(path)}")

        except Exception as e:
            log(f"❌ Error parsing {os.path.basename(path)}: {e}")

    return territories

def inject_into_ce(territories):
    try:
        tree = ET.parse(CE_PATH)
        root = tree.getroot()
        territory_list = root.find("territory-type-list")
        if territory_list is None:
            territory_list = ET.SubElement(root, "territory-type-list")

        existing_types = {
            t.attrib.get("name", "").lower(): t
            for t in territory_list.findall("territory-type")
        }

        zone_sig_map = {}
        for typename, elem in existing_types.items():
            zone_sig_map[typename] = set(
                normalized_zone_sig(z.attrib)
                for t in elem.findall("territory")
                for z in t.findall("zone")
            )

        injected_blocks = 0
        skipped_zones = 0

        for entry in territories:
            ttype = entry["type"].lower()
            territory_name = entry["territory_name"]
            color = entry["color"]
            zones = entry["zones"]

            if not zones:
                continue

            if ttype not in existing_types:
                new_type = ET.SubElement(territory_list, "territory-type", {"name": entry["type"]})
                existing_types[ttype] = new_type
                zone_sig_map[ttype] = set()

            if not territory_name:
                territory_name = zones[0].get("name", "unnamed")

            t_elem = ET.SubElement(existing_types[ttype], "territory", {
                "visible": "1",
                "color": color,
                "name": territory_name
            })

            count = 0
            for zone in zones:
                sig = normalized_zone_sig(zone)
                if sig in zone_sig_map[ttype]:
                    skipped_zones += 1
                    continue
                ET.SubElement(t_elem, "zone", zone)
                zone_sig_map[ttype].add(sig)
                count += 1

            if count == 0:
                existing_types[ttype].remove(t_elem)
                log(f"⏩ Skipped block (all zones already exist) for: {territory_name} in {entry['type']}")
            else:
                injected_blocks += 1
                log(f"✔ Injected {count} zones into {entry['type']} ({territory_name})")

        indent(root)
        os.makedirs("output", exist_ok=True)
        tree.write(OUTPUT_PATH, encoding="utf-8", xml_declaration=True)
        log(f"\n✅ Injection complete. {injected_blocks} new blocks added.")
        if skipped_zones:
            log(f"🟡 {skipped_zones} zones skipped (already exist).")
        log(f"📄 Output saved to: {OUTPUT_PATH}")

    except Exception as e:
        log(f"❌ ERROR during injection: {e}")

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    os.makedirs("input", exist_ok=True)
    os.makedirs("ce", exist_ok=True)
    log(f"🌍 Using CE map file: {MAP_FILE}")
    backup_ce_file()
    files = find_all_territory_files()
    parsed = parse_territory_files(files)
    inject_into_ce(parsed)
