package dev.local.defaulttracks;

/** The mod's saved settings. */
final class Settings {
    private Settings() {}

    static int location() { return DefaultTracks.MOD.settings().getInt("location", 0); }          // 0 user library, 1 custom folder
    static void setLocation(int n) { DefaultTracks.MOD.settings().putInt("location", n); }
    static boolean useCustomFolder() { return location() == 1; }
    static String customFolder() { return DefaultTracks.MOD.settings().get("folder", ""); }
    static void setCustomFolder(String path) { DefaultTracks.MOD.settings().put("folder", path); }
}
