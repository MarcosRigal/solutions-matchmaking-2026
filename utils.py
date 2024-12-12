import rti.idl as idl
from enum import IntEnum


@idl.enum
class ShapeFillKind(IntEnum):
    SOLID_FILL = 0
    TRANSPARENT_FILL = 1
    HORIZONTAL_HATCH_FILL = 2
    VERTICAL_HATCH_FILL = 3


@idl.struct(
    member_annotations={
        "color": [idl.key, idl.bound(128)],
    }
)
class ShapeType:
    color: str = ""
    x: idl.int32 = 0
    y: idl.int32 = 0
    shapesize: idl.int32 = 0


@idl.struct
class ShapeTypeExtended(ShapeType):
    fillKind: ShapeFillKind = ShapeFillKind.SOLID_FILL
    angle: idl.float32 = 0.0
