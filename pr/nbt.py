import struct
from io import BytesIO

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10


def _write_payload(buf, tag_type, value):
    if tag_type == TAG_BYTE:
        buf.write(struct.pack('>b', value))
    elif tag_type == TAG_SHORT:
        buf.write(struct.pack('>h', value))
    elif tag_type == TAG_INT:
        buf.write(struct.pack('>i', value))
    elif tag_type == TAG_LONG:
        buf.write(struct.pack('>q', value))
    elif tag_type == TAG_FLOAT:
        buf.write(struct.pack('>f', value))
    elif tag_type == TAG_DOUBLE:
        buf.write(struct.pack('>d', value))
    elif tag_type == TAG_BYTE_ARRAY:
        buf.write(struct.pack('>I', len(value)))
        buf.write(value)
    elif tag_type == TAG_STRING:
        encoded = value.encode('utf-8')
        buf.write(struct.pack('>H', len(encoded)))
        buf.write(encoded)
    elif tag_type == TAG_LIST:
        elem_type, items = value
        buf.write(struct.pack('>B', elem_type))
        buf.write(struct.pack('>I', len(items)))
        for item in items:
            _write_payload(buf, elem_type, item)
    elif tag_type == TAG_COMPOUND:
        for entry in value:
            t, name, v = entry
            _write_named_tag(buf, t, name, v)
        buf.write(struct.pack('>B', TAG_END))
    else:
        raise ValueError(f"Unknown tag type: {tag_type}")


def _write_named_tag(buf, tag_type, name, value):
    buf.write(struct.pack('>B', tag_type))
    name_bytes = name.encode('utf-8')
    buf.write(struct.pack('>H', len(name_bytes)))
    buf.write(name_bytes)
    _write_payload(buf, tag_type, value)


def serialize_nbt(root_compound):
    buf = BytesIO()
    _write_named_tag(buf, TAG_COMPOUND, "", root_compound)
    return buf.getvalue()
