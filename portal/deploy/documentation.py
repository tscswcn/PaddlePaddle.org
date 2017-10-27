import os
import tempfile
import requests
import traceback
from urlparse import urlparse

from django.conf import settings

from deploy import documentation_generator, strip, sitemap_generator
from portal import sitemap_helper


def transform(original_documentation_dir, generated_docs_dir, version):
    """
    Given a raw repo directory contents, perform the following steps (conditional to the repo):
    - Generate the output HTML contents from its source content generator engine.
    - Strip their contents from the static files and header, footers, that cause inconsistencies.
    - Generate individual sitemaps.
    """
    try:
        print 'Processing docs at %s to %s for version %s' % (original_documentation_dir, generated_docs_dir, version)
        if not os.path.exists(os.path.dirname(original_documentation_dir)):
            print 'Cannot strip documentation, source_dir=%s does not exists' % original_documentation_dir
            return

        doc_generator = None
        convertor = None
        sm_generator = None
        output_dir_name = None

        if original_documentation_dir:
            original_documentation_dir = original_documentation_dir.rstrip('/')

        # Remove the heading 'v', left in for purely user-facing convenience.
        if version[0] == 'v':
            version = version[1:]

        # If this seems like a request to build/transform the core Paddle docs.
        if original_documentation_dir.lower().endswith('/paddle'):
            doc_generator = documentation_generator.generate_paddle_docs
            convertor = strip.sphinx
            sm_generator = sitemap_generator.sphinx_sitemap
            output_dir_name = 'documentation'

        # Or if this seems like a request to build/transform the book.
        elif original_documentation_dir.lower().endswith('/book'):
            doc_generator = documentation_generator.generate_book_docs
            convertor = strip.book
            sm_generator = sitemap_generator.book_sitemap
            output_dir_name = 'book'

        # Or if this seems like a request to build/transform the models.
        elif original_documentation_dir.lower().endswith('/models'):
            doc_generator = documentation_generator.generate_models_docs
            convertor = strip.models
            sm_generator = sitemap_generator.models_sitemap
            output_dir_name = 'models'

        else:
            raise Exception('Unsupported content.')

        if not generated_docs_dir:
            # If we have not already generated the documentation, then run the document generator
            print 'Generating documentation at %s' % original_documentation_dir
            if doc_generator:
                generated_docs_dir = doc_generator(original_documentation_dir, output_dir_name)

        print 'Stripping documentation at %s, version %s' % (generated_docs_dir, version)
        if convertor:
            convertor(generated_docs_dir, version, output_dir_name)

        print 'Generating sitemap for documentation at %s, gen_docs_dir=%s,  version %s' % \
              (original_documentation_dir, generated_docs_dir, version)
        if sm_generator:
            sm_generator(original_documentation_dir, generated_docs_dir, version, output_dir_name)

        sitemap_helper.generate_sitemap(version, 'en')
        sitemap_helper.generate_sitemap(version, 'zh')

    except Exception as e:
        print 'Unable to process documentation: %s' % e
        traceback.print_exc(original_documentation_dir)


def fetch_and_transform(source_url, version):
    """
    For an arbitrary URL of Markdown contents, fetch and transform them into a
    "stripped" and barebones HTML file.
    """
    response = requests.get(source_url)
    tmp_dir = tempfile.gettempdir()
    source_markdown_file = tmp_dir + urlparse(source_url).path

    if not os.path.exists(os.path.dirname(source_markdown_file)):
        os.makedirs(os.path.dirname(source_markdown_file))

    with open(source_markdown_file, 'wb') as f:
        f.write(response.content)

    strip.markdown_file(source_markdown_file, version, tmp_dir)
