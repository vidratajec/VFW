import re
import json
from collections import defaultdict

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.9f') # da ne spremeni majhnih stevil na 0

#Thank you chatGPT

def parse_abaqus_report(file_path, output_json_path, target_region):
    with open(file_path, "r") as file:
        content = file.read()

    # Regular expressions
    frame_pattern = re.compile(r"Frame: Increment\s+(\d+): Step Time =\s+([\d.E+-]+)")
    region_pattern = re.compile(r"Field Output reported at integration points for region: (.+?)\n", re.MULTILINE)
    data_block_pattern = re.compile(r"^-{10,}\n((?:\s*\d+\s+\d+\s+[-\d.E+]+\s+[-\d.E+]+\s+[-\d.E+]+\s+[-\d.E+]+\n)+)", re.MULTILINE)
    row_pattern = re.compile(r"\s*(\d+)\s+(\d+)\s+([-\d.E+]+)\s+([-\d.E+]+)\s+([-\d.E+]+)\s+([-\d.E+]+)")

    parsed_data = defaultdict(lambda: defaultdict(dict))
    frame_headers = list(frame_pattern.finditer(content))

    for i, frame_match in enumerate(frame_headers):
        frame_id = int(frame_match.group(1))
        start = frame_match.end()
        end = frame_headers[i + 1].start() if i + 1 < len(frame_headers) else len(content)
        frame_block = content[start:end]

        # Split by region sections
        region_sections = list(region_pattern.finditer(frame_block))
        for j, region_match in enumerate(region_sections):
            region_name = region_match.group(1)
            if region_name.strip() != target_region.strip():
                continue  # Skip non-target regions

            reg_start = region_match.end()
            reg_end = region_sections[j + 1].start() if j + 1 < len(region_sections) else len(frame_block)
            region_block = frame_block[reg_start:reg_end]

            # Find data blocks
            for data_block in data_block_pattern.findall(region_block):
                for row in row_pattern.findall(data_block):
                    element, int_pt, s11, s22, s33, s12 = row
                    parsed_data[frame_id][int(element)][int(int_pt)] = {
                        "S": [float(s11),float(s22),float(s33),float(s12)]
                        #"S11": float(s11),
                        #"S22": float(s22),
                        #"S33": float(s33),
                        #"S12": float(s12)
                    }

    # Save JSON
    with open(output_json_path, "w") as json_file:
        json.dump(parsed_data, json_file, indent=2)

    #print(f"Parsed data for region '{target_region}' saved to: {output_json_path}")


parse_abaqus_report("Data4ele/Stress4ele.txt", "Data4ele/Napetost.JSON", target_region="STENA-1.Region_1")
