# Blacksite Zeta client updates

Minecraft **1.21.1**, NeoForge **21.1.250**, Java **21**. The cumulative server update is active.

Download [Install-Blacksite.bat](https://raw.githubusercontent.com/zazu197/blacksite-zeta-client-updates/main/Install-Blacksite.bat), close Minecraft and double-click it. Save the page as a `.bat` if your browser displays its code. It finds the Blacksite/Magitech CurseForge profile in standard or custom folders. If several match, choose one. You can also drag the profile folder onto the BAT.

The readable installer checks all **286 required mods** by filename, size and SHA-256. It downloads missing or wrong files, removes known superseded mods, and applies all required configs, datapacks, resources and quests. Four optional performance mods are downloaded directly from their authors. Set `BLACKSITE_OPTIMIZATIONS=0` to skip them. Download this latest BAT for installer version 2; then rerun it whenever you want to update or repair the pack.

**No backups are created.** Saves, maps, personal controls, shader selections and unrelated mods are preserved. Voxy preferences and other Create settings are preserved while the necessary fixes are merged. Downloads pass validation before profile writes begin. If installation is interrupted, rerun the BAT.

## Cumulative changes

Includes every requested addition from the Mekanism/Platform update through Create Nuclear 2.0.0: multiplier 16, expanded Chemical upgrades, reusable forcefield/factory GUI, new content mods and dependencies, Construction Sticks, Double Slabs, and 91 new Blacksite Star quests. Existing quest IDs/progress remain valid; Stone Slabs replace the removed Dirt Slabs task. See [MODS.md](MODS.md) for the full mod list and the manifest for exact versions and checksums.

Create Better FPS is removed after the observed Create belt registration crash. Create supports **512 RPM** through Rotation Speed Controllers. Voxy local terrain collection is enabled, including the mining dimension. Server LOD support sends existing terrain only.

New ores require **newly generated chunks**. Existing chunks are preserved. Overworld ores stay in the mining dimension's Overworld layer (Y 68-244), with Nether/End ores in their matching layers. Create Nuclear retains its native Overworld ores too.

## Complete ZIP

The [latest release](https://github.com/zazu197/blacksite-zeta-client-updates/releases/tag/client-star-1.3.0) also includes the full CurseForge-importable ZIP: 285 bundled required JARs, configs, resources, quests and recipes. CurseForge or the BAT downloads Create Nuclear from its original author. Optional optimizations are fetched by the BAT. Your launcher supplies Minecraft, NeoForge and Java.

## Electric Blaze superheat

Apply a second Blaze Capacitor to an electric heater, supply at least **1,063 FE/t** continuously and remove redstone signals. This reaches blue SEETHING heat without another mod. See [Electric-Blaze-Heaters.txt](Electric-Blaze-Heaters.txt) and the [author's instructions](https://www.curseforge.com/minecraft/mc-mods/create-electric-blaze).

Large files use versioned GitHub Releases. This public repository contains only player updater code, manifests, documentation and verification reports. The website/server repository remains private. Mod authors retain ownership and licenses; license files remain in the JARs. Create Nuclear and optional optimizations use original author downloads. Double Slabs source: https://github.com/CJMinecraft01/DoubleSlabs.
