package dev.local.defaulttracks;

import com.bitwig.flt.app.Hvv;

import java.io.File;
import java.io.IOException;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Locale;

/** Finds "Default ... Track.bwpreset" in the user library, or in a folder the user chose. */
final class PresetFinder {
    private PresetFinder() {}

    /** The user library from Bitwig's Locations setting, wherever the user put it. */
    static File userLibrary() {
        try {
            File library = Hvv.mEL().IKw();
            if (library != null) return library;
        } catch (Throwable t) {
            DefaultTracks.MOD.log("could not read the user library location", t);
        }
        return new File(System.getProperty("user.home"), "Documents/Bitwig Studio/Library");
    }

    /** The folder the search starts in, given the settings. */
    static File searchRoot() {
        if (Settings.useCustomFolder()) {
            String folder = Settings.customFolder();
            if (!folder.isBlank()) return new File(folder);
        }
        return userLibrary();
    }

    /** The preset file, or null when there is none. The shallowest match wins. */
    static File find(String presetName) {
        File root = searchRoot();
        if (!root.isDirectory()) return null;
        if (!Settings.useCustomFolder() && new File(root, "Presets").isDirectory()) root = new File(root, "Presets");
        String wanted = (presetName + ".bwpreset").toLowerCase(Locale.ROOT);
        File[] best = new File[1];
        int[] bestDepth = {Integer.MAX_VALUE};
        Path start = root.toPath();
        try {
            Files.walkFileTree(start, new SimpleFileVisitor<>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
                    Path name = file.getFileName();
                    if (name != null && name.toString().toLowerCase(Locale.ROOT).equals(wanted)) {
                        int depth = start.relativize(file).getNameCount();
                        if (depth < bestDepth[0]) {
                            bestDepth[0] = depth;
                            best[0] = file.toFile();
                        }
                    }
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult visitFileFailed(Path file, IOException e) {
                    return FileVisitResult.CONTINUE;
                }
            });
        } catch (IOException | RuntimeException e) {
            DefaultTracks.MOD.log("preset search failed in " + root, e);
        }
        return best[0];
    }
}
