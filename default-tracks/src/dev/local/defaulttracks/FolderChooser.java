package dev.local.defaulttracks;

import bml.notifications.Notifications;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * A folder picker for the preset location (Bitwig's Settings has no text field). Bitwig runs with AWT headless,
 * so the dialog is macOS's own, opened through osascript.
 */
final class FolderChooser {
    private FolderChooser() {}

    static void choose() {
        // The dialog waits for the user, so keep it off Bitwig's UI thread.
        Thread thread = new Thread(FolderChooser::run, "default-tracks-folder");
        thread.setDaemon(true);
        thread.start();
    }

    private static void run() {
        try {
            File start = PresetFinder.searchRoot();
            if (!start.isDirectory()) start = PresetFinder.userLibrary();
            String script = "tell application \"System Events\"\n"
                    + "activate\n"
                    + "set f to choose folder with prompt \"Choose the folder with your Default track presets\""
                    + (start.isDirectory() ? " default location (POSIX file \"" + start.getPath().replace("\"", "\\\"") + "\")" : "")
                    + "\nend tell\n"
                    + "POSIX path of f";
            Process process = new ProcessBuilder(List.of("osascript", "-e", script)).redirectErrorStream(true).start();
            String out = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8).trim();
            if (process.waitFor() != 0) {
                DefaultTracks.MOD.log("folder dialog ended: " + out);   // cancelled, or no dialog possible
                return;
            }
            File folder = new File(out);
            Settings.setCustomFolder(folder.getPath());
            Settings.setLocation(1);
            DefaultTracks.MOD.log("preset folder set to " + folder);
            Notifications.toast("Default Tracks: using " + folder.getPath());
        } catch (Throwable t) {
            DefaultTracks.MOD.log("folder dialog failed", t);
            Notifications.toast("Default Tracks: could not open the folder dialog");
        }
    }
}
