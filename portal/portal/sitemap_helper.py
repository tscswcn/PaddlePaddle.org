import json
from django.conf import settings


# Merge all site.json files
def load_all_sections():
    # Load from the external_drive
    file_dir_list = ["book", "blog", "documentation"]

    all_sections = {}
    for dir_path in file_dir_list:
        file_path = "%s/%s/site.json" % (settings.EXTERNAL_TEMPLATE_DIR, dir_path)
        json_data = open(file_path).read()
        data = json.loads(json_data)
        all_sections.update(data)

    return all_sections


# From all the sections, out a json file with all the tutorial related sections
def load_tutorial_book():
    try:
        # Check if there is an existing tutorial.json file already
        # Reuse if possible
        with open('tutorial.json') as json_data:
            data = json.load(json_data)
            return data
    except IOError:
        # tutorial.json is missing. Create a new one
        chapters = ["getting_started", "tutorial", "advanced"]
        tutorial_dict = {
            "id": "tutorial",
            "title": "Tutorial",
        }

        all_sections = load_all_sections()
        sections = []
        for chapter_id in chapters:
            if chapter_id in all_sections:
                sections.append(all_sections[chapter_id])

        tutorial_dict["chapters"] = sections
        with open('tutorial.json', 'w') as fp:
            json.dump(tutorial_dict, fp)

        return tutorial_dict
