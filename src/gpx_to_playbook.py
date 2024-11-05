# This script can be used to transform a .gpx file to yaml valid output for our playbook
import os
import sys
import argparse
import xml.etree.ElementTree as ET
import yaml

openstreetmap_namespace = "{http://www.topografix.com/GPX/1/1}trkpt"


def transform(input_file, output_file):
    # Reading from input file
    f = open(input_file, "r")
    data = f.read()
    # Convert to xml
    tree = ET.fromstring(data)
    # Checking output file
    yaml_output = ""
    for i, coordinate in enumerate(tree.iter(openstreetmap_namespace)):
        lat = coordinate.attrib.get("lat")
        lon = coordinate.attrib.get("lon")
        dump = yaml.dump({i+5: {"TYPE": "EXTERNAL",
                                "SUBTYPE": "GEO",
                                "PARAMETERS":
                                    {"ALTITUDE": 0,
                                     "LATITUDE": lat,
                                     "LONGITUDE": lon}
                                }})
        yaml_output += dump
    if output_file is not None:
        of = open(output_file, "w")
        of.write(yaml_output)
        of.close()
    else:
        print(yaml_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="gpx input file", required=True)
    parser.add_argument("-o", "--output_file", help="yaml output file", required=False)
    args = parser.parse_args()
    if os.path.isfile(args.input_file):
        transform(args.input_file, args.output_file)
    else:
        print("File path for input file is invalid or not a file")
        sys.exit(0)
