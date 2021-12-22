package io.github.humbleui.types;

import lombok.*;
import org.jetbrains.annotations.*;

@Data
@With
public class IPoint {
    public static final IPoint ZERO = new IPoint(0, 0);

    @ApiStatus.Internal public final int _x;
    @ApiStatus.Internal public final int _y;

    @ApiStatus.Internal
    public static IPoint _makeFromLong(long l) {
        return new IPoint((int) (l >>> 32), (int) (l & 0xFFFFFFFF));
    }

    @NotNull
    public IPoint offset(int dx, int dy) {
        return dx == 0 && dy == 0 ? this : new IPoint(_x + dx, _y + dy);
    }

    @NotNull
    public IPoint offset(@NotNull IPoint vec) {
        assert vec != null : "IPoint::offset expected other != null";
        return offset(vec._x, vec._y);
    }

    @NotNull
    public IPoint scale(int scale) {
        return scale(scale, scale);
    }

    @NotNull
    public IPoint scale(int sx, int sy) {
        return (sx == 1 && sy == 1) || (_x == 0 && _y == 0) ? this : new IPoint(_x * sx, _y * sy);
    }

    @NotNull
    public IPoint inverse() {
        return scale(-1, -1);
    }

    public boolean isEmpty() {
        return _x <= 0 || _y <= 0;
    }

    @NotNull @Contract("-> new")
    public Point toPoint() {
        return new Point(_x, _y);
    }
}