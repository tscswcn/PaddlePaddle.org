from urlparse import urlparse
import zipfile
import os
import tempfile

import requests

from deploy import strip
from django.conf import settings


def transform(source_dir, version, output_dir, specified_source=None):
    convertor = None
    extracted_source_dir = None

    # python manage.py deploy_documentation book v0.10.0 generated_contents/
    # remove the heading 'v'
    if version[0] == 'v':
        version = version[1:]

    if source_dir in settings.GIT_REPO_MAP:
        git_repo = settings.GIT_REPO_MAP[source_dir]
        git_repo = git_repo + version + '.zip'
        extracted_dir = source_dir + '-' + version
        response = requests.get(git_repo)
        tmp_zip_file = settings.TEMPORARY_DIR + source_dir + '.zip'

        with open(tmp_zip_file, 'wb') as f:
            f.write(response.content)

        with zipfile.ZipFile(tmp_zip_file, "r") as zip_ref:
            zip_ref.extractall(settings.TEMPORARY_DIR)
            extracted_source_dir = settings.TEMPORARY_DIR + '/' + extracted_dir
    else:
        extracted_source_dir = source_dir

    if 'documentation' in source_dir or specified_source == 'documentation':
        print 'is documentation'
        convertor = strip.sphinx

    elif 'book' in source_dir or specified_source == 'book':
        print 'is book'
        convertor = strip.book

    elif 'models' in source_dir or specified_source == 'models':
        print 'is models'
        convertor = strip.models

    print 'extracted_source_dir: ', extracted_source_dir
    print 'version: ', version
    print 'specified_source: ', specified_source

    if convertor:
        if output_dir:
            print 'has output_dir'
            convertor(extracted_source_dir, version, output_dir)
        elif settings.EXTERNAL_TEMPLATE_DIR:
            print 'has EXTERNAL_TEMPLATE_DIR'
            convertor(extracted_source_dir, version, settings.EXTERNAL_TEMPLATE_DIR)
        else:
            return


def fetch_and_transform(source_url, version):
    response = requests.get(source_url)
    tmp_dir = tempfile.gettempdir()
    source_markdown_file = tmp_dir + urlparse(source_url).path

    if not os.path.exists(os.path.dirname(source_markdown_file)):
        os.makedirs(os.path.dirname(source_markdown_file))

    with open(source_markdown_file, 'wb') as f:
        f.write(response.content)

    strip.markdown_file(source_markdown_file, version, tmp_dir)
