package dev.local.savenewversion;

import java.io.File;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Works out the file name of the next version of a project file. Plain Java, no Bitwig names. */
final class VersionName {
    private static final String EXT = ".bwproject";
    private static final Pattern SUFFIX = Pattern.compile("^(.*?)(?:-(\\d{10}|\\d{1,4}))?$");
    private static final DateTimeFormatter STAMP = DateTimeFormatter.ofPattern("ddMMyyHHmm");

    private VersionName() {}

    /** The file to save the next version to, or {@code current} when the name isn't a .bwproject. */
    static File next(File current, boolean byDate) {
        String name = current.getName();
        if (!name.endsWith(EXT)) return current;
        String stem = name.substring(0, name.length() - EXT.length());
        Matcher m = SUFFIX.matcher(stem);
        String base = m.matches() && !m.group(1).isEmpty() ? m.group(1) : stem;
        File dir = current.getParentFile();
        if (byDate) {
            return new File(dir, base + "-" + STAMP.format(LocalDateTime.now()) + EXT);
        }
        int highest = 1;
        File[] siblings = dir == null ? null : dir.listFiles();
        if (siblings != null) {
            Pattern mine = Pattern.compile(Pattern.quote(base) + "-(\\d{1,4})" + Pattern.quote(EXT));
            for (File f : siblings) {
                Matcher n = mine.matcher(f.getName());
                if (n.matches()) highest = Math.max(highest, Integer.parseInt(n.group(1)));
            }
        }
        return new File(dir, base + "-" + (highest + 1) + EXT);
    }
}
