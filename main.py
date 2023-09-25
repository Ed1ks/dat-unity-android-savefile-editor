import json
from datetime import datetime, date

import msgpack
from msgpack import Timestamp


def main():
    # read raw
    f = open("input.dat", "rb")
    a = f.read()
    g = msgpack.unpackb(a, object_hook=decode_datetime, raw=False)

    # write json
    with open("edit.json", "w") as file:
        file.write(json.dumps(g, indent=2, default=json_serialize))

    input("Edit the generated json and press Enter to continue...")

    f = open("edit.json", "r")
    a = f.read()
    g = json.loads(a, object_hook=json_deserialize)

    # write new
    h = msgpack.packb(g, default=encode_datetime, use_bin_type=False)
    with open("output.dat", "wb") as binary_file:
        # Write bytes to file
        binary_file.write(h)

    print("Successfully created output.dat file")
    input("Press Enter to continue...")


def list_of_dicts_decode(obj):
    for key, value in obj.items():
        if isinstance(value, dict):
            obj[key] = list_of_dicts_decode(value)
        elif isinstance(value, Timestamp):
            obj[key] = value.to_datetime()
    return obj


def list_of_dicts_encode(obj):
    for key, value in obj.items():
        if isinstance(value, dict):
            obj[key] = list_of_dicts_encode(value)
        elif isinstance(value, datetime):
            obj[key] = Timestamp.from_datetime(value)
    return obj


def decode_datetime(obj):
    if isinstance(obj, dict):
        obj = list_of_dicts_decode(obj)
    if '__datetime__' in obj:
        print(obj)
        obj = datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    return obj


def encode_datetime(obj):
    if isinstance(obj, dict):
        obj = list_of_dicts_encode(obj)
    elif isinstance(obj, datetime):
        obj = Timestamp.from_datetime(obj)
    if isinstance(obj, datetime):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    return obj


def json_serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def json_deserialize(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, dict):
                obj[key] = list_of_dicts_encode(value)
            elif isinstance(value, str):
                try:
                    obj[key] = datetime.fromisoformat(value)
                except:
                    pass
    return obj


if __name__ == '__main__':
    main()
