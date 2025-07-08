import hashlib

# Generate a deterministic RGBA color based on territory name
def generate_color_rgba(name, existing_names):
    base_color = name_to_color(name)

    # Ensure uniqueness by nudging color if it's already used
    attempts = 0
    while base_color in [name_to_color(n) for n in existing_names] and attempts < 10:
        name += "_"
        base_color = name_to_color(name)
        attempts += 1

    return base_color

# Hash name → RGB → assemble full RGBA with full opacity
def name_to_color(name):
    hash_digest = hashlib.md5(name.encode()).hexdigest()

    # Use first 6 characters as RGB hex
    r = int(hash_digest[0:2], 16)
    g = int(hash_digest[2:4], 16)
    b = int(hash_digest[4:6], 16)
    a = 192  # Keep slightly translucent for better CE visuals

    # Clamp values to editor-safe midrange to avoid white/black/overbright
    r = 50 + (r % 150)
    g = 50 + (g % 150)
    b = 50 + (b % 150)

    # Convert to single ARGB int used by CE Tool
    argb = (a << 24) + (r << 16) + (g << 8) + b
    return argb
