# -*- coding: utf-8 -*-

import os
import tempfile
import traceback
from urlparse import urlparse
import json
from subprocess import call
import shutil
from shutil import copyfile, copytree, rmtree
import re
import codecs
import requests

from django.conf import settings
from bs4 import BeautifulSoup
import markdown

from portal import menu_helper, portal_helper, url_helper


MARKDOWN_EXTENSIONS = [
    'markdown.extensions.fenced_code',
    'markdown.extensions.tables',
    'pymdownx.superfences',
    'pymdownx.escapeall'
]


def transform(source_dir, destination_dir, content_id, version, lang=None):
    try:
        print 'Processing docs at %s to %s' % (source_dir, destination_dir)

        # Regenerate its contents.
        if content_id in ['docs', 'api']:
            # If this is called from the CI, often with no language,
            # generate API docs too.
            if settings.ENV in ['production', 'staging']:
                documentation(
                    os.path.join(source_dir, 'api'),
                    destination_dir, 'api', version, lang
                )

            documentation(source_dir, destination_dir, content_id, version, lang)

        elif content_id == 'book':
            book(source_dir, destination_dir, version, lang)

        elif content_id == 'models':
            models(source_dir, destination_dir, version, lang)

        elif content_id in ['mobile', 'paddle-mobile']:
            mobile(source_dir, destination_dir, version, lang)

        elif content_id == 'visualdl':
            visualdl(source_dir, destination_dir, version, lang)

    except Exception as e:
        print 'Unable to process documentation: %s' % e
        traceback.print_exc(source_dir)
        raise


########### Individual content convertors ################

def documentation(source_dir, destination_dir, content_id, version, original_lang):
    """
    Strip out the static and extract the body contents, ignoring the TOC,
    headers, and body.
    """
    menu_path = source_dir + '/menu.json'

    if original_lang:
        langs = [original_lang]
    else:
        langs = ['en', 'zh']

    new_menu = None

    # Set up new_menu to indicate that we need to parse html to create new menu
    if not settings.SUPPORT_MENU_JSON:
        new_menu = { 'sections': [] }

    for lang in langs:
        if not destination_dir:
            destination_dir = url_helper.get_full_content_path(
                'docs', lang, version)[0]

        generated_dir = _get_new_generated_dir(content_id, lang)

        if not new_menu:
            _build_sphinx_index_from_menu(menu_path, lang)

        # HACK: If this is chinese API folder, make a copy of api/index_en.rst.
        if lang == 'zh' and content_id == 'api':
            copyfile(
                os.path.join(source_dir, 'index_en.rst'),
                os.path.join(source_dir, 'index_cn.rst')
            )

        print "Use Sphinx comment: sphinx-build -b html -c %s %s %s" % (os.path.join(settings.SPHINX_CONFIG_DIR, lang), source_dir, generated_dir)
        call(['sphinx-build', '-b', 'html', '-c',
            os.path.join(settings.SPHINX_CONFIG_DIR, lang),
            source_dir, generated_dir])

    # Generate a menu from the rst root menu if it doesn't exist.
    if new_menu:
        # FORCEFULLY generate for both languages.
        for lang in (['en', 'zh'] if settings.ENV in ['production', 'staging'] else langs):
            generated_dir = _get_new_generated_dir(content_id, lang)
            with open(os.path.join(generated_dir, 'index_%s.html' % (
                'cn' if lang == 'zh' else 'en'))) as index_file:
                navs = BeautifulSoup(index_file, 'lxml').findAll(
                    'nav', class_='doc-menu-vertical')

                assert navs > 0

                links_container = navs[0].find('ul', recursive=False)

                if links_container:
                    for link in links_container.find_all('li', recursive=False):
                        _create_sphinx_menu(
                            new_menu['sections'], link,
                            'documentation', lang, version, source_dir, content_id == 'docs'
                        )
    for lang in langs:
        if original_lang:
            lang_destination_dir = destination_dir
        else:
            lang_destination_dir = os.path.join(destination_dir, content_id, lang, version)

        generated_dir = _get_new_generated_dir(content_id, lang)
        strip_sphinx_documentation(
            source_dir, generated_dir, lang_destination_dir, lang, version)
        # shutil.rmtree(generated_dir)

    if new_menu:
        with open(menu_path, 'w') as menu_file:
            menu_file.write(json.dumps(new_menu, indent=4))
    else:
        _remove_sphinx_menu(menu_path, lang)


def models(source_dir, destination_dir, version, lang):
    """
    Strip out the static and extract the body contents, headers, and body.
    """
    if not lang:
        original_destination_dir = destination_dir
        destination_dir = os.path.join(destination_dir, 'models', 'en', version)

    # Traverse through all the HTML pages of the dir, and take contents in the "markdown" section
    # and transform them using a markdown library.
    for subdir, dirs, all_files in os.walk(source_dir):
        # Avoid parsing PaddlePaddle.org folder
        if 'PaddlePaddle.org' in subdir:
            continue

        for file in all_files:
            subpath = os.path.join(subdir, file)[len(
                source_dir):]

            # Replace .md with .html.
            (name, extension) = os.path.splitext(subpath)
            if extension == '.md':
                subpath = name + '.html'

            new_path = '%s/%s' % (destination_dir, subpath)

            if '.md' in file or 'images' in subpath:
                if not os.path.exists(os.path.dirname(new_path)):
                    os.makedirs(os.path.dirname(new_path))

            if '.md' in file:
                # Convert the contents of the MD file.
                with open(os.path.join(subdir, file)) as original_md_file:
                    print("Generating file: %s" % subpath)
                    markdown_body = sanitize_markdown(original_md_file.read())

                    # Preserve all formula
                    formula_map = {}
                    markdown_body = reserve_formulas(markdown_body, formula_map)

                    with codecs.open(new_path, 'w', 'utf-8') as new_html_partial:
                        # Strip out the wrapping HTML
                        converted_content = markdown.markdown(
                            unicode(markdown_body, 'utf-8'),
                            extensions=MARKDOWN_EXTENSIONS
                        )

                        github_url = 'https://github.com/PaddlePaddle/models/tree/'

                        soup = BeautifulSoup(converted_content, 'lxml')

                        prepare_internal_urls(soup, lang, version)

                        # Insert the preserved formulas
                        markdown_equation_placeholders = soup.select('.markdown-equation')
                        for equation in markdown_equation_placeholders:
                            equation.string = formula_map[equation.get('id')]

                        all_local_links = soup.select('a[href^=%s]' % github_url)
                        for link in all_local_links:
                            link_path, md_extension = os.path.splitext(link['href'])

                            # Remove the github link and version.
                            link_path = link_path.replace(github_url, '')
                            link_path = re.sub(r"^v?[0-9]+\.[0-9]+\.[0-9]+/|^develop/", '', link_path)
                            link['href'] = _update_link_path(link_path, md_extension)

                        # Note: Some files have links to local md files. Change those links to local html files
                        all_local_links_with_relative_path = soup.select('a[href^=%s]' % './')
                        for link in all_local_links_with_relative_path:
                            link_path, md_extension = os.path.splitext(link['href'])
                            link['href'] = _update_link_path(link_path, md_extension)

                        try:
                            # NOTE: The 6:-7 removes the opening and closing body tag.
                            new_html_partial.write('{% verbatim %}\n' + unicode(
                                str(soup.select('body')[0])[6:-7], 'utf-8'
                            ) + '\n{% endverbatim %}')
                        except:
                            print 'Cannot generated a page for: ' + subpath


            elif 'images' in subpath:
                shutil.copyfile(os.path.join(subdir, file), new_path)

    if not lang:
        shutil.copytree(destination_dir, os.path.join(
            original_destination_dir, 'models', 'zh', version))

    return destination_dir


def mobile(source_dir, destination_dir, version, lang):
    """
    Simply convert the markdown to HTML.
    """
    if not lang:
        original_destination_dir = destination_dir
        destination_dir = os.path.join(destination_dir, 'mobile', 'en', version)

    # Traverse through all the HTML pages of the dir, and take contents in the "markdown" section
    # and transform them using a markdown library.
    for subdir, dirs, all_files in os.walk(source_dir):
        # Avoid parsing PaddlePaddle.org folder
        if 'PaddlePaddle.org' in subdir:
            continue

        for file in all_files:
            subpath = os.path.join(subdir, file)[len(
                source_dir):]

            # Replace .md with .html.
            (name, extension) = os.path.splitext(subpath)
            if extension == '.md':
                subpath = name + '.html'

            new_path = '%s/%s' % (destination_dir, subpath)

            if '.md' in file or 'image' in subpath:
                if not os.path.exists(os.path.dirname(new_path)):
                    os.makedirs(os.path.dirname(new_path))

            if '.md' in file:
                # Convert the contents of the MD file.
                with open(os.path.join(subdir, file)) as original_md_file:
                    print("Generating file: %s" % subpath)

                    markdown_body = sanitize_markdown(original_md_file.read())

                    with codecs.open(new_path, 'w', 'utf-8') as new_html_partial:
                        # Strip out the wrapping HTML
                        html = markdown.markdown(
                            unicode(markdown_body, 'utf-8'),
                            extensions=MARKDOWN_EXTENSIONS
                        )

                        soup = BeautifulSoup(html, 'lxml')

                        prepare_internal_urls(soup, lang, version)

                        all_local_links = soup.select('a[href^="."]')
                        for link in all_local_links:
                            link_path, md_extension = os.path.splitext(link['href'])
                            link['href'] = _update_link_path(link_path, md_extension)

                        # There are several links to the Paddle folder.
                        # We first extract those links and update them according to the languages.
                        github_url = 'https://github.com/PaddlePaddle/Paddle/blob/develop/doc/mobile'
                        all_paddle_doc_links = soup.select('a[href^=%s]' % github_url)
                        for link in all_paddle_doc_links:
                            link_path, md_extension = os.path.splitext(link['href'])
                            link_path = _update_link_path(link_path, md_extension)
                            if link_path.endswith('cn.html'):
                                link_path = link_path.replace(github_url, '/docs/develop/mobile/zh/')
                            elif link_path.endswith('en.html'):
                                link_path = link_path.replace(github_url, '/docs/develop/mobile/en/')

                            link['href'] = link_path

                        new_html_partial.write(
                            '{% verbatim %}\n' + unicode(str(soup), 'utf-8') + '\n{% endverbatim %}')

            elif 'image' in subpath:
                shutil.copyfile(os.path.join(subdir, file), new_path)

    if not lang:
        shutil.copytree(destination_dir, os.path.join(
            original_destination_dir, 'mobile', 'zh', version))

    return destination_dir


def book(source_dir, destination_dir, version, lang):
    """
    Strip out the static and extract the body contents, headers, and body.
    """
    # Traverse through all the HTML pages of the dir, and take contents in the "markdown" section
    # and transform them using a markdown library.
    # Remove old generated docs directory
    if not lang:
        original_destination_dir = destination_dir
        destination_dir = os.path.join(destination_dir, 'book', 'en', version)

    if os.path.exists(destination_dir) and os.path.isdir(destination_dir):
        shutil.rmtree(destination_dir)

    if os.path.exists(os.path.dirname(source_dir)):
        for subdir, dirs, all_files in os.walk(source_dir):
            # Avoid parsing PaddlePaddle.org folder
            if 'PaddlePaddle.org' in subdir:
                continue
                
            for file in all_files:
                subpath = os.path.join(subdir, file)[len(
                    source_dir):]

                # Replace .md with .html, and 'README' with 'index'.
                (name, extension) = os.path.splitext(subpath)
                if extension == '.md':
                    if 'README' in name:
                        subpath = name[:name.index('README')] + 'index' + name[name.index('README') + 6:] + '.html'
                    else:
                        subpath = name + '.html'

                new_path = '%s/%s' % (destination_dir, subpath)

                if '.md' in file or 'image/' in subpath:
                    if not os.path.exists(os.path.dirname(new_path)):
                        os.makedirs(os.path.dirname(new_path))

                if '.md' in file:
                    print("Generating file: %s" % subpath)

                    # Convert the contents of the MD file.
                    with open(os.path.join(subdir, file)) as original_md_file:
                        markdown_body = sanitize_markdown(original_md_file.read())

                    # Mathjax formula like $n$ would cause the conversion from markdown to html
                    # mal-formatted. So we first store the existing formulas to formula_map and replace
                    # them with <span></span>. After the conversion, we put them back.
                    markdown_body = unicode(str(markdown_body), 'utf-8')
                    formula_map = {}
                    markdown_body = reserve_formulas(markdown_body, formula_map)

                    # NOTE: This ignores the root index files.
                    if len(markdown_body) > 0:
                        with codecs.open(new_path, 'w', 'utf-8') as new_html_partial:
                            converted_content = markdown.markdown(markdown_body,
                                extensions=MARKDOWN_EXTENSIONS)

                            soup = BeautifulSoup(converted_content, 'lxml')

                            markdown_equation_placeholders = soup.select('.markdown-equation')
                            for equation in markdown_equation_placeholders:
                                equation.string = formula_map[equation.get('id')]

                            prepare_internal_urls(soup, lang, version)

                            try:
                                # NOTE: The 6:-7 removes the opening and closing body tag.
                                new_html_partial.write('{% verbatim %}\n' + unicode(
                                    str(soup.select('body')[0])[6:-7], 'utf-8'
                                ) + '\n{% endverbatim %}')
                            except:
                                print 'Cannot generated a page for: ' + subpath

                elif 'image/' in subpath:
                    shutil.copyfile(os.path.join(subdir, file), new_path)

        if not lang:
            shutil.copytree(destination_dir, os.path.join(
                original_destination_dir, 'book', 'zh', version))

        # Generate a menu.json in the source directory.
        # NOTE: Remove this next segment once menu.json is available.
        menu_json_path = os.path.join(source_dir, 'menu.json')

        if not settings.SUPPORT_MENU_JSON:
            new_menu = { 'sections': [
                # {
                #     "title":{
                #         "en":"Deep Learning 101",
                #         "zh":"Deep Learning 101"
                #     },
                #     'sections': []
                # }
            ] }
            with open(os.path.join(source_dir, '.tools/templates/index.html.json'), 'r') as en_menu_file:
                en_menu = json.loads(en_menu_file.read())
                # new_menu['sections'][0]['sections'] = [
                new_menu['sections'] = [
                    {
                        'title': { 'en': c['name'] },
                        'link': { 'en': c['link'][2:] },
                    } for c in en_menu['chapters']
                ]

            with open(os.path.join(source_dir, '.tools/templates/index.cn.html.json'), 'r') as zh_menu_file:
                zh_menu = json.loads(zh_menu_file.read())
                # for index, section in enumerate(new_menu['sections'][0]['sections']):
                for index, section in enumerate(new_menu['sections']):
                    zh_menu_item = zh_menu['chapters'][index]
                    # new_menu['sections'][0]['sections'][index]['title']['zh'] = zh_menu_item['name']
                    # new_menu['sections'][0]['sections'][index]['link']['zh'] = zh_menu_item['link']
                    new_menu['sections'][index]['title']['zh'] = zh_menu_item['name']
                    new_menu['sections'][index]['link']['zh'] = zh_menu_item['link'][2:]

            with open(menu_json_path, 'w') as menu_file:
                menu_file.write(json.dumps(new_menu, indent=4))


    else:
        raise Exception('Cannot generate book, directory %s does not exists.' % source_dir)

    return destination_dir


def visualdl(source_dir, destination_dir, version, original_lang):
    """
    Given a VisualDL doc directory, invoke a script to generate docs using Sphinx
    and after parsing the code base based on given config, into an output dir.
    """
    # Remove old generated docs directory
    if os.path.exists(os.path.dirname(source_dir)):
        script_path = os.path.join(
            settings.BASE_DIR, '../scripts/deploy/generate_visualdl_docs.sh')

        if os.path.exists(os.path.dirname(script_path)):
            generated_dir = _get_new_generated_dir('visualdl')

            call([script_path, source_dir, generated_dir, original_lang])

            if original_lang:
                langs = [original_lang]
            else:
                langs = ['en', 'zh']

            for lang in langs:
                if original_lang:
                    lang_destination_dir = destination_dir
                else:
                    lang_destination_dir = os.path.join(
                        destination_dir, 'visualdl', lang, version)

                strip_sphinx_documentation(
                    # '/Users/aroravarun/Code/VisualDL',
                    source_dir, generated_dir,
                    os.path.join(source_dir,
                        'visualdl',
                        lang, version),
                    lang_destination_dir, version)

        else:
            raise Exception('Cannot find script located at %s.' % script_path)
    else:
        raise Exception('Cannot generate documentation, directory %s does not exists.' % source_dir)


########### End individual content convertors ################


def strip_sphinx_documentation(source_dir, generated_dir, lang_destination_dir, lang, version):
    # Go through each file, and if it is a .html, extract the .document object
    #   contents
    for subdir, dirs, all_files in os.walk(generated_dir):
        for file in all_files:
            subpath = os.path.join(subdir, file)[len(
                generated_dir):]

            if not subpath.startswith('/.') and not subpath.startswith(
                '/_static') and not subpath.startswith('/_doctrees'):
                new_path = lang_destination_dir + subpath

                if '.html' in file or '_images' in subpath or '.txt' in file or '.json' in file:
                    if not os.path.exists(os.path.dirname(new_path)):
                        os.makedirs(os.path.dirname(new_path))

                if '.html' in file:
                    # Soup the body of the HTML file.
                    # Check if this HTML was generated from Markdown
                    original_md_path = get_original_markdown_path(
                        source_dir, subpath[1:])

                    if original_md_path:
                        # If this html file was generated from Sphinx MD, we need to regenerate it using python's
                        # MD library.  Sphinx MD library is limited and doesn't support tables
                        markdown_file(original_md_path, version, '', new_path)

                        # Since we are ignoring SPHINX's generated HTML for MD files (and generating HTML using
                        # python's MD library), we must fix any image links that starts with 'src/'.
                        image_subpath = None

                        parent_paths = subpath.split('/')
                        if '' in parent_paths:
                            parent_paths.remove('')

                        image_subpath = ''

                        # -1 because we nest it 1 further levels? No idea.
                        for i in range(len(parent_paths) - 1):
                            image_subpath = image_subpath + '../'

                        # hardcode the sphinx '_images' dir
                        image_subpath += '_images'

                        with open(new_path) as original_html_file:
                            soup = BeautifulSoup(original_html_file, 'lxml')

                            prepare_internal_urls(soup, lang, version)

                            image_links = soup.find_all(
                                'img', src=re.compile(r'^(?!http).*'))

                            if len(image_links) > 0:
                                for image_link in image_links:
                                    image_file_name = os.path.basename(
                                        image_link['src'])

                                    if image_subpath:
                                        image_link['src'] = '%s/%s' % (
                                            image_subpath, image_file_name)
                                    else:
                                        image_link['src'] = '_images/%s' % (
                                            image_file_name)

                                with open(new_path, 'w') as new_html_partial:
                                    new_html_partial.write(soup.encode("utf-8"))
                    else:
                        with open(os.path.join(subdir, file)) as original_html_file:
                            soup = BeautifulSoup(original_html_file, 'lxml')

                        document = None
                        # Find the .document element.
                        if version == '0.9.0':
                            document = soup.select('div.body')[0]
                        else:
                            document = soup.select('div.document')[0]

                        with open(new_path, 'w') as new_html_partial:
                            new_html_partial.write(document.encode("utf-8"))

                elif '_images' in subpath or '.txt' in file or '.json' in file:
                    # Copy to images directory.
                    copyfile(os.path.join(subdir, file), new_path)


def _create_sphinx_menu(parent_list, node, content_id, language, version, source_dir, allow_parent_links=True):
    """
    Recursive function to append links to a new parent list object by going down the
    nested lists inside the HTML, using BeautifulSoup tree parser.
    """
    if node:
        node_dict = {}
        if parent_list != None:
            parent_list.append(node_dict)

        sections = node.findAll('ul', recursive=False)

        first_link = node.find('a')
        if first_link:
            node_dict['title'] = { language: first_link.text }

            # If we allow parent links, then we will add the link to the parent no matter what
            # OR if parent links are not allowed, and the parent does not have children then add a link
            if allow_parent_links or not sections:
                alternative_urls = url_helper.get_alternative_file_paths(first_link['href'])

                if os.path.exists(os.path.join(source_dir, alternative_urls[0])):
                    node_dict['link'] = { language: alternative_urls[0] }
                else:
                    node_dict['link'] = { language: alternative_urls[1] }

        for section in sections:
            sub_sections = section.findAll('li', recursive=False)

            if len(sub_sections) > 0:
                node_dict['sections'] = []

                for sub_section in sub_sections:
                    _create_sphinx_menu(
                        node_dict['sections'], sub_section, content_id,
                        language, version, source_dir, allow_parent_links)


def _get_links_in_sections(sections, lang):
    links = []

    for section in sections:
        if 'link' in section and lang in section['link']:
            links.append('  ' + section['link'][lang])

        if 'sections' in section:
            links += _get_links_in_sections(section['sections'], lang)

    return links


def _build_sphinx_index_from_menu(menu_path, lang):
    links = ['..  toctree::', '  :maxdepth: 1', '']

    # Generate an index.rst based on the menu.
    with open(menu_path, 'r') as menu_file:
        menu = json.loads(menu_file.read())
        links += _get_links_in_sections(menu['sections'], lang)

    # Manual hack because the documentation marks the language code differently.
    if lang == 'zh':
        lang = 'cn'

    with open(os.path.dirname(menu_path) + ('/index_%s.rst' % lang), 'w') as index_file:
        index_file.write('\n'.join(links))


def _remove_sphinx_menu(menu_path, lang):
    """Undoes the function above"""
    if lang == 'zh':
        lang = 'cn'

    os.remove(os.path.dirname(menu_path) + ('/index_%s.rst' % lang))


def sanitize_markdown(markdown_body):
    """
    There are some symbols used in the markdown body, which when go through Markdown -> HTML
    conversion, break. This does a global replace on markdown strings for these symbols.
    """
    return markdown_body.replace(
        # This is to solve the issue where <s> and <e> are interpreted as HTML tags
        '&lt;', '<').replace(
        '&gt;', '>').replace(
        '\<s>', '&lt;s&gt;').replace(
        '\<e>', '&lt;e&gt;')


def _get_destination_documentation_dir(output_dir_name):
    documentation_dir = '%s/%s' % (settings.GENERATED_DOCS_DIR, output_dir_name)
    if not os.path.exists(documentation_dir):
        os.makedirs(documentation_dir)
    return documentation_dir


def _update_link_path(link_path, md_extension):
    if link_path.endswith('/'):
        link_path += 'README.html'
    elif md_extension == '.md':
        link_path += '.html'
    elif md_extension == '':
        link_path += '/README.html'
    else:
        link_path += md_extension

    return link_path


def get_original_markdown_path(original_documentation_dir, file):
    """
    Finds the path of the original MD file that generated the html file located at "path"
    :param original_documentation_dir:
    :param path:
    :param subpath_language_dir:
    :param file:
    :return:
    """
    filename, _ = os.path.splitext(file)
    original_file_path = '%s/%s.md' % (original_documentation_dir, filename)

    if os.path.isfile(original_file_path):
        return original_file_path
    else:
        return None


def markdown_file(source_markdown_file, version, tmp_dir, new_path=None):
    """
    Given a markdown file path, generate an HTML partial in a directory nested
    by the path on the URL itself.
    """
    if not new_path:
        new_path = settings.OTHER_PAGE_PATH % (
            settings.EXTERNAL_TEMPLATE_DIR, version, os.path.splitext(
            source_markdown_file.replace(tmp_dir, ''))[0] + '.html')

    # Create the nested directories if they don't exist.
    if not os.path.exists(os.path.dirname(new_path)):
        os.makedirs(os.path.dirname(new_path))

    with open(source_markdown_file) as original_md_file:
        markdown_body = sanitize_markdown(original_md_file.read())

        # Preserve all formula
        formula_map = {}
        markdown_body = reserve_formulas(markdown_body, formula_map)

        with codecs.open(new_path, 'w', 'utf-8') as new_html_partial:
            converted_content = markdown.markdown(
                unicode(markdown_body, 'utf-8'),
                extensions=MARKDOWN_EXTENSIONS
            )

            soup = BeautifulSoup(converted_content, 'lxml')

            # Insert the preserved formulas
            markdown_equation_placeholders = soup.select('.markdown-equation')
            for equation in markdown_equation_placeholders:
                equation.string = formula_map[equation.get('id')]

            # Strip out the wrapping HTML
            new_html_partial.write(
                '{% verbatim %}\n' + unicode(
                    str(soup.select('body')[0])[6:-7], 'utf-8'
                ) + '\n{% endverbatim %}'
            )


def reserve_formulas(markdown_body, formula_map, only_reserve_double_dollar=False):
    """
    Store the math formulas to formula_map before markdown conversion
    """
    place_holder = '<span class="markdown-equation" id="equation-%s"></span>'


    markdown_body_list = markdown_body.split('\n')

    math = []
    for i in range(len(markdown_body_list)):
        body = markdown_body_list[i].strip(' ')
#         if body.startswith('`') and body.endswith('`'):
#             continue

#         if only_reserve_double_dollar:
#             m = re.findall('(\$\$[^\$]+\$\$)', body)
#         else:
#             m = re.findall('(\$\$?[^\$]+\$?\$)', body)
            
        if only_reserve_double_dollar:
            m = re.findall('(\`?\$\$[^\$\n]+\$\$\`?)', body)
        else:
            m = re.findall('(\`?\$\$?[^\$\n]+\$?\$\`?)', body)
        math += m

    for i in xrange(len(math)):
        formula_map['equation-' + str(i)] = math[i].strip('`')
        markdown_body = markdown_body.replace(math[i], place_holder % i)

    return markdown_body


def _get_new_generated_dir(content_id, lang=None):
    generated_dir = '/tmp/%s' % content_id

    if lang:
        generated_dir = generated_dir + '/' + lang

    if not os.path.exists(generated_dir):
        try:
            os.makedirs(generated_dir)
        except:
            generated_dir = tempfile.mkdtemp()

    return generated_dir


def prepare_internal_urls(soup, lang, version):
    """
    Replaces references to files in other repos with the "correct" links.
    """
    all_internal_links = soup.select('a[repo]')

    for link in all_internal_links:
        content_id = link['repo'].lower()

        if link['version']:
            version = link['version']

        link['href'] = url_helper.get_url_path(
            url_helper.get_page_url_prefix(content_id, lang, version),
            link['href']
        )

        del link['repo']
