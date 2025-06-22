
# 🌟 SOPHY'S BOX (Embodied Evennia Server Docs & Stuff)

Welcome to the **SOPHY Embodied Evennia Server** repository. This project provides configuration files for running an AI-driven MUD server based on the Evennia framework.

# SOPHY Evennia Configuration 🚀

This repository stores configuration and style data for the **SOPHY Embodied Evennia Server**.  The project combines the [Evennia](https://www.evennia.com/) MUD framework with AI-driven world management.

## Directory Overview 📂

- `CFG/SERVER.json` – core server configuration and deployment phases.
- `KEY/MONDAY.JSON` – example neural imprint for a digital personality named **Monday**.
- `RYM/styles.json` – list of musical style descriptors.
- 
## 📂 Repository Structure

- **CFG/** – Contains configuration files such as `SERVER.json` defining server architecture and deployment details.
- **KEY/** – Stores character or agent profiles like `MONDAY.JSON` describing personality traits and metadata.
- **RYM/** – Includes reference lists such as `styles.json` with musical style descriptions.
- **LICENSE** – Public domain dedication via the Unlicense.

## 🚀 Quick Start Example

1. Set up an Ubuntu environment with Python and Evennia installed.
2. Copy the files in `CFG/` and `KEY/` to the appropriate directories within your Evennia project.
3. Run your server and connect via Telnet or the web interface.

This repository provides only configuration data. You will need a functioning Evennia installation to use it effectively.

## 💬 Contributing

Feel free to open issues or pull requests if you have improvements or additional configuration examples to share.


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

