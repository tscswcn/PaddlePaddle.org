import json
from django.conf import settings



SITEMAP_TEMLATE = {
    "books": [
        {
            "id": "tutorial",
            "name": "Tutorial",
            "chapters": ["getting_started", "tutorial", "advanced"]
        },
        {
            "id": "documentation",
            "name": "Documentation",
            "chapters": ["api", "advanced"]
        }
    ]
}


# Merge all site.json files
def _load_all_sections(lang=None):
    # Load from the external_drive
    lang_file_modifier = ""
    if lang == "zh":
        lang_file_modifier = "_cn"
    file_dir_list = ["book", "blog", "documentation"]

    all_sections = {}
    for dir_path in file_dir_list:
        file_path = "%s/%s/site%s.json" % (settings.EXTERNAL_TEMPLATE_DIR, dir_path, lang_file_modifier)
        try:
            json_data = open(file_path).read()
            data = json.loads(json_data)
            all_sections.update(data)
        except:
            print "Missing site.json from %s" % file_path
            pass

    return all_sections


def _get_sitemap_file_path(lang):
    return "sitemap.%s.json" % (lang)


def _generate_sitemap(lang):
    all_sections = _load_all_sections(lang)

    sitemap = {}
    for book in SITEMAP_TEMLATE["books"]:
        book_map = {
            "id": book["id"],
            "name": book["name"],
            "chapters": []
        }

        for chapter_id in book["chapters"]:
            chapter_ref_map = all_sections.get(chapter_id, None)

            if chapter_ref_map:
                chapter_map = {
                    "id": chapter_id
                }
                chapter_map.update(chapter_ref_map)
                book_map["chapters"].append(chapter_map)

                if 'sections' in chapter_ref_map:
                    sections = chapter_ref_map['sections']
                    if sections and "root_url" not in book_map :
                        book_map["root_url"] = sections[0]["link"]

        sitemap[book["id"]] = book_map


    file_path = "%s/sitemap.%s.json" % (settings.EXTERNAL_TEMPLATE_DIR, lang)
    with open(file_path, 'w') as fp:
        json.dump(sitemap, fp)

    return sitemap


def get_root_navigation(lang):
    try:
        with open(_get_sitemap_file_path(lang)) as json_data:
            data = json.load(json_data)
            return data
    except IOError:
        return _generate_sitemap(lang)


def get_book_navigation(book_id, lang):
    root_nav = get_root_navigation(lang)
    return root_nav.get(book_id, None)