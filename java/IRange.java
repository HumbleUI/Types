package io.github.humbleui.types;

import lombok.*;
import org.jetbrains.annotations.*;

@Data
@With
public class IRange {
    @ApiStatus.Internal
    public final int _start;
    
    @ApiStatus.Internal
    public final int _end;

    @ApiStatus.Internal
    public static IRange _makeFromLong(long l) {
        return new IRange((int) (l >>> 32), (int) (l & 0xFFFFFFFF));
    }
}