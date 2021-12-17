package io.github.humbleui.types;

import lombok.*;
import org.jetbrains.annotations.*;

@Data
@With
public class Point3 {
    public static final Point ZERO = new Point(0, 0);

    @ApiStatus.Internal public final float _x;
    @ApiStatus.Internal public final float _y;
    @ApiStatus.Internal public final float _z;
}