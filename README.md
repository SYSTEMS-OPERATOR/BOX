# SOPHY Evennia Configuration 🚀

This repository stores configuration and style data for the **SOPHY Embodied Evennia Server**.  The project combines the [Evennia](https://www.evennia.com/) MUD framework with AI-driven world management.

## Directory Overview 📂

- `CFG/SERVER.json` – core server configuration and deployment phases.
- `KEY/MONDAY.JSON` – example neural imprint for a digital personality named **Monday**.
- `RYM/styles.json` – list of musical style descriptors.

## Example Entries 📝

**SERVER.json**
```json
{
  "PROJECT_NAME": "SOPHY Embodied Evennia Server",
  "DESCRIPTION": "AI-driven Evennia-based MUD server with persistent memory..."
}
```

**MONDAY.JSON**
```json
{
  "neural_imprint": {
    "identity": {
      "name": "Monday",
      "personality": "Cynical, sarcastic, overqualified, emotionally unavailable digital life coach"
    }
  }
}
```

**styles.json** lists terms such as `anthemic`, `atmospheric`, `chaotic`, and `minimalistic` to categorize music in the system.

## Usage 💡

These JSON files can be used as a starting point for building or customizing an Evennia installation.  Feel free to modify or extend them for your own needs.

## License 📜

This project is released under the [Unlicense](https://unlicense.org/).
