import os
import shutil
import codecs
from subprocess import call

from bs4 import BeautifulSoup
from django.conf import settings
import markdown

from deploy.operators import generate_operators_page


def generate_paddle_docs(original_documentation_dir, output_dir_name):
    """
    Given a Paddle doc directory, invoke a script to generate docs using Sphinx
    and after parsing the code base based on given config, into an output dir.
    """
    # Remove old generated docs directory
    destination_dir = _get_destination_documentation_dir(output_dir_name)
    if os.path.exists(destination_dir) and os.path.isdir(destination_dir):
        shutil.rmtree(destination_dir)

    if os.path.exists(os.path.dirname(original_documentation_dir)):
        destination_dir = _get_destination_documentation_dir(output_dir_name)
        settings_path = settings.PROJECT_ROOT
        script_path = settings_path + '/../../scripts/deploy/generate_paddle_docs.sh'

        if os.path.exists(os.path.dirname(script_path)):
            call([script_path, original_documentation_dir, destination_dir])

            # Now generate operators.
            operators_api_path = original_documentation_dir + '/operators.json'
            operators_page_path = generate_operators_page(
                operators_api_path, destination_dir)

            return destination_dir
        else:
            raise Exception('Cannot find script located at %s.' % script_path)
    else:
        raise Exception('Cannot generate documentation, directory %s does not exists.' % original_documentation_dir)


def generate_models_docs(original_documentation_dir, output_dir_name):
    """
    Strip out the static and extract the body contents, headers, and body.
    """
    # Traverse through all the HTML pages of the dir, and take contents in the "markdown" section
    # and transform them using a markdown library.
    destination_documentation_dir = _get_destination_documentation_dir(output_dir_name)

    for subdir, dirs, all_files in os.walk(original_documentation_dir):
        for file in all_files:
            subpath = os.path.join(subdir, file)[len(
                original_documentation_dir):]

            # Replace .md with .html.
            (name, extension) = os.path.splitext(subpath)
            if extension == '.md':
                subpath = name + '.html'

            new_path = '%s/%s' % (destination_documentation_dir, subpath)

            if '.md' in file or 'images' in subpath:
                if not os.path.exists(os.path.dirname(new_path)):
                    os.makedirs(os.path.dirname(new_path))

            if '.md' in file:
                # Convert the contents of the MD file.
                with open(os.path.join(subdir, file)) as original_md_file:
                    markdown_body = original_md_file.read()

                    with codecs.open(new_path, 'w', 'utf-8') as new_html_partial:
                        # Strip out the wrapping HTML
                        new_html_partial.write(
                            '{% verbatim %}\n' + markdown.markdown(
                                unicode(markdown_body, 'utf-8'),
                                extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables']
                            ) + '\n{% endverbatim %}'
                        )

            elif 'images' in subpath:
                shutil.copyfile(os.path.join(subdir, file), new_path)

    return destination_documentation_dir


def generate_mobile_docs(original_documentation_dir, output_dir_name):
    """
    Simply convert the markdown to HTML.
    """
    # Traverse through all the HTML pages of the dir, and take contents in the "markdown" section
    # and transform them using a markdown library.
    destination_documentation_dir = _get_destination_documentation_dir(output_dir_name)

    for subdir, dirs, all_files in os.walk(original_documentation_dir):
        for file in all_files:
            subpath = os.path.join(subdir, file)[len(
                original_documentation_dir):]

            # Replace .md with .html.
            (name, extension) = os.path.splitext(subpath)
            if extension == '.md':
                subpath = name + '.html'

            new_path = '%s/%s' % (destination_documentation_dir, subpath)

            if '.md' in file or 'image' in subpath:
                if not os.path.exists(os.path.dirname(new_path)):
                    os.makedirs(os.path.dirname(new_path))

            if '.md' in file:
                # Convert the contents of the MD file.
                with open(os.path.join(subdir, file)) as original_md_file:
                    markdown_body = original_md_file.read()

                    with codecs.open(new_path, 'w', 'utf-8') as new_html_partial:
                        # Strip out the wrapping HTML
                        html = markdown.markdown(
                            unicode(markdown_body, 'utf-8'),
                            extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables']
                        )

                        # TODO: Go through all URLs, and if their href matches a
                        # pattern of the Github repo pulled from Mobile,
                        # Replace it's .md extension with .html.
                        soup = BeautifulSoup(html, 'lxml')
                        all_local_links = soup.select('a[href^="."]')

                        for link in all_local_links:
                            # Since this is a Github repo, the default page should
                            # pick from a README.md instead of the webserver
                            # expected index.html.
                            if link['href'].endswith('/'):
                                link['href'] += 'README.md'

                            link_path, md_extension = os.path.splitext(link['href'])

                            if md_extension == '.md':
                                link['href'] = link_path + '.html'

                        new_html_partial.write(
                            '{% verbatim %}\n' + unicode(str(soup), 'utf-8') + '\n{% endverbatim %}')

            elif 'image' in subpath:
                shutil.copyfile(os.path.join(subdir, file), new_path)

    return destination_documentation_dir


def generate_book_docs(original_documentation_dir, output_dir_name):
    """
    Given a book directory, invoke a script to generate docs using repo scripts
    to generate HTML, into an output dir.
    """
    # Remove old generated docs directory
    destination_dir = _get_destination_documentation_dir(output_dir_name)
    if os.path.exists(destination_dir) and os.path.isdir(destination_dir):
        shutil.rmtree(destination_dir)

    if os.path.exists(os.path.dirname(original_documentation_dir)):
        destination_dir = _get_destination_documentation_dir(output_dir_name)
        settings_path = settings.PROJECT_ROOT
        script_path = settings_path + '/../../scripts/deploy/generate_book_docs.sh'

        if os.path.exists(os.path.dirname(script_path)):
            call([script_path, original_documentation_dir, destination_dir])
            return destination_dir
        else:
            raise Exception('Cannot find script located at %s.' % script_path)
    else:
        raise Exception('Cannot generate documentation, directory %s does not exists.' % original_documentation_dir)


def generate_blog_docs(original_documentation_dir, output_dir_name):
    # Unlike 'book', 'models' or 'Paddle', for 'blog' we do the strip first then build
    BLOG_TEMPLATE = '<div class="page-content"><div class="wrapper">{{ content }}</div></div>'

    destination_dir = _get_destination_documentation_dir(output_dir_name)
    if os.path.exists(destination_dir) and os.path.isdir(destination_dir):
        shutil.rmtree(destination_dir)

    if os.path.exists(os.path.dirname(original_documentation_dir)):
        destination_dir = _get_destination_documentation_dir(output_dir_name)
        settings_path = settings.PROJECT_ROOT
        script_path = settings_path + '/../../scripts/deploy/generate_blog_docs.sh'

        with open(original_documentation_dir+"/_layouts/default.html", "w") as fp:
            fp.write(BLOG_TEMPLATE)

        if os.path.exists(os.path.dirname(script_path)):
            call([script_path, original_documentation_dir, destination_dir])
            return destination_dir
        else:
            raise Exception('Cannot find script located at %s.' % script_path)
    else:
        raise Exception('Cannot generate documentation, directory %s does not exists.' % original_documentation_dir)


def _get_destination_documentation_dir(output_dir_name):
    documentation_dir = '%s/%s' % (settings.GENERATED_DOCS_DIR, output_dir_name)
    if not os.path.exists(documentation_dir):
        os.makedirs(documentation_dir)
    return documentation_dir
