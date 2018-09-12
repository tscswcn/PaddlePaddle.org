import os
import re
import json
import math
from subprocess import check_output
import tempfile

import nltk
import jieba

from textblob import TextBlob as tb
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management import BaseCommand


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Usage: python manage.py rebuild_index <language> <version> --content_id=<e.g. documentation>"

    def add_arguments(self, parser):
        parser.add_argument('language', nargs='+')
        parser.add_argument('version', nargs='+')
        parser.add_argument(
            '--content_id', action='store', default=None, dest='content_id')


    def build_api_document(self, source_dir):
        for subdir, dirs, all_files in os.walk(source_dir):
            for file in all_files:
                subpath = os.path.join(subdir, file)
                (name, extension) = os.path.splitext(file)

                # We explicitly only want to look at HTML files which are not indexes.
                if extension == '.html' and 'index_' not in file:
                    with open(os.path.join(settings.BASE_DIR, subpath)) as html_file:
                        soup = BeautifulSoup(html_file, 'lxml')

                        for api_call in soup.find_all(re.compile('^h(1|2|3)')):
                            try:
                                self.api_documents.append({
                                    'path': '/' + subpath + (api_call.a['href'] if (api_call.a and 'href' in api_call.a) else ''),
                                    'title': str(next(api_call.stripped_strings).encode('utf-8')),
                                    'prefix': os.path.splitext(os.path.basename(name))[0] if '.' in name else ''
                                })
                            except Exception as e:
                                print("Unable to parse the file at: %s" % subpath)


    def build_document(self, source_dir, lang):
        for subdir, dirs, all_files in os.walk(source_dir):
            for file in all_files:
                subpath = os.path.join(subdir, file)
                (name, extension) = os.path.splitext(file)

                if extension == '.html':
                    document = {
                        'path': '/' + subpath
                    }

                    if document['path'] in self.unique_paths:
                        continue

                    # And extract their document content so that we can TFIDF
                    # their contents.
                    with open(
                        os.path.join(settings.BASE_DIR, subpath)) as html_file:
                        soup = BeautifulSoup(html_file, 'lxml')

                        # Find the first header 1 or h2.
                        title = soup.find('h1')
                        if not title:
                            title = soup.find('h2')

                        if title:
                            document['title'] = next(title.stripped_strings)
                        else:
                            # No point trying to store a non-titled file
                            #     because it is probably a nav or index of sorts.
                            continue

                        # Segment the Chinese sentence through jieba library
                        if lang == 'zh':
                            chinese_seg_list = [" ".join(jieba.cut_for_search(str)) for str in soup.stripped_strings]
                            document['content'] = ", ".join(chinese_seg_list)
                        else:
                            document['content'] = ', '.join(soup.stripped_strings)

                    self.documents.append(document)
                    self.unique_paths.append(document['path'])

                    print 'Found "%s"...' % document['title'].encode('utf-8')


    def handle(self, *args, **options):
        self.documents = []
        self.api_documents = []
        self.unique_paths = []

        nltk.download('punkt')

        contents_to_build = []
        if options['content_id']:
            contents_to_build.append(options['content_id'])
        else:
            for maybe_dir in os.listdir(settings.WORKSPACE_DIR):
                if os.path.isdir(
                    os.path.join(settings.WORKSPACE_DIR, maybe_dir)):
                    contents_to_build.append(maybe_dir)

        # First we need to go through all the generated HTML documents.
        for content_to_build in contents_to_build:
            source_dir = os.path.join(
                settings.WORKSPACE_DIR, content_to_build,
                options['language'][0], options['version'][0]
            )

            if content_to_build == 'api' and options['version'][0] not in ['0.10.0', '0.11.0']:
                self.build_api_document(source_dir)

            else:
                self.build_document(source_dir, options['language'][0])


        # And create an index JS file that we can import.
        output_index_dir = os.path.join(
            settings.STATICFILES_DIRS[0],
            'indexes', options['language'][0] ,options['version'][0]
        )
        output_index_js = os.path.join(output_index_dir, 'index.js')
        output_toc_js = os.path.join(output_index_dir, 'toc.js')

        tmp_documents_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_documents_file.write(json.dumps(self.documents + self.api_documents))
        tmp_documents_file.close()

        with open(output_index_js, 'w') as index_file:
            index_file.write('var index = ' + check_output(['node',
                os.path.join(settings.PROJECT_ROOT, 'management/commands/build-index.js'), tmp_documents_file.name]))

        with open(output_toc_js, 'w') as toc_file:
            content_less_toc = {}

            for doc in self.documents + self.api_documents:
                if doc['path'] not in content_less_toc:
                    serialized_doc = {
                        'path': doc['path'],
                        'title': doc['title']
                    }

                    if 'prefix' in doc:
                        serialized_doc['prefix'] = doc['prefix']

                    content_less_toc[doc['path']] = serialized_doc

            toc_file.write('var indexPathMap = ' + json.dumps(content_less_toc))


        os.remove(tmp_documents_file.name)

        # Gzip the index generated.
        check_output(['gzip', output_index_js])
        check_output(['gzip', output_toc_js])
