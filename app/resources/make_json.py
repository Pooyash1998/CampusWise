import csv
import json

def construct_json_from_csv(csv_filename, json_filename):
    study_programs = {}

    with open(csv_filename, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            study_program = row.get("Studiengang", "").strip()
            degree_type = row.get("AbschlussArt", "").strip()
            version = row.get("Version", "").strip()

            # Ignore empty or invalid values
            if not study_program or study_program.lower() == "nan":
                continue
            if not degree_type or degree_type.lower() == "nan":
                continue
            if version.lower() == "nan":
                version = "" 

            # Ensure the study program exists
            if study_program not in study_programs:
                study_programs[study_program] = {}

            # Ensure the degree type exists within the study program
            if degree_type not in study_programs[study_program]:
                study_programs[study_program][degree_type] = []

            # Avoid duplicates and add version
            if version and version not in study_programs[study_program][degree_type]:
                study_programs[study_program][degree_type].append(version)

    # Save the constructed JSON
    output_data = {"study_programs": study_programs}
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(output_data, json_file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
  construct_json_from_csv("resources/rwth.csv", "resources/study_programs.json")
