# Blacksite Zeta client updates

Minecraft **1.21.1**, NeoForge **21.1.250**, Java **21**.

Download [Install-Blacksite.bat](https://raw.githubusercontent.com/zazu197/blacksite-zeta-client-updates/main/Install-Blacksite.bat), close Minecraft, and double-click it. If the browser displays the code, use **Save as** and keep the `.bat` extension. The updater identifies your CurseForge Blacksite/Magitech profile from the standard or custom Minecraft folder. If several profiles match, it asks you to choose one. You can also drag a profile folder onto the BAT or pass its full path as the first argument.

The matching server additions remain **staged**. Do not launch the updated profile against the older server until the owner activates the matching update. This repository does not restart or change the Minecraft server.

## What the updater does

- Fetches the current [complete mod manifest](client-manifest.json) on every run.
- Checks all **286 required mod JARs** by filename, file size and SHA-256. Downloads only missing or incorrect files from this repository's versioned release assets.
- Installs four tested optional client optimizations directly from their authors: Entity Culling, More Culling, Particle Core and Fzzy Config. Change `BLACKSITE_OPTIMIZATIONS=1` to `0` in the readable BAT to skip these downloads.
- Replaces known outdated versions by their mod identity and precise filename prefixes. Removes Dirt Slabs and superseded Blacksite Effects/Platform files.
- Applies required configs, datapacks and quest definitions. Copies other resources/configs only when missing. Merges Entity Culling compatibility exceptions into your existing settings.
- Verifies downloads before changing the profile. Leaves saves, screenshots, maps, controls, shader selections and unrelated mods alone.
- **Creates no backups.** If writing fails after installation starts, rerun it to repair the update.

No administrator privileges, GitHub login, CurseForge API key, account access, encoded commands or GoFile link are needed. All code is visible in [Install-Blacksite.bat](Install-Blacksite.bat). Minecraft, Java and NeoForge come from your launcher; the updater does not install those runtimes.

## Included changes

The manifest includes the full client pack, every pending addition since Blacksite Platform 1.4.0, the Mekanism multiplier of 16, expanded Chemical upgrades, the reusable forcefield/factory GUI, all 22 requested content additions and their dependencies, Construction Sticks and Double Slabs, and 91 new quests across 10 chapters. The Blacksite Star is a nine-component endgame trophy. Existing quest IDs/progress are retained; the former Dirt Slabs task accepts Stone Slabs.

See [MODS.md](MODS.md) for every required and optional mod, exact versions/filenames and download checksums in the manifest. Mod authors retain their licenses and ownership; license files remain inside their JARs. Optional performance mods are downloaded from the authors rather than redistributed here. Double Slabs source: https://github.com/CJMinecraft01/DoubleSlabs.

## Electric Blaze superheating

The installed Create: Electric Blaze 1.0.0 already supports this. Use one Blaze Capacitor on a normal Blaze Burner to electrify it, then apply a **second capacitor** to the electric heater. Supply at least **1,063 FE/t continuously** with the pack defaults, and remove any redstone signal. Two powered capacitors reach the blue `SEETHING` state for superheated Create recipes; one uses 505 FE/t for `KINDLED` heat. No new mod, Blaze Cake or server restart is required. Full instructions: [Electric-Blaze-Heaters.txt](Electric-Blaze-Heaters.txt). [Author's instructions](https://www.curseforge.com/minecraft/mc-mods/create-electric-blaze).

## Distribution

Large client files live in [GitHub Releases](https://github.com/zazu197/blacksite-zeta-client-updates/releases), while this Git repository contains only readable code, manifests, documentation and verification reports. The private website/server repository stays private. The owner can publish another release and update `client-manifest.json`; players rerun the same BAT to check the complete pack again.
