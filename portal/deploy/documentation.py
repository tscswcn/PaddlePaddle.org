from deploy import strip
from django.conf import settings
import requests
import zipfile
import os


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
        convertor = strip.sphinx

    elif 'book' in source_dir or specified_source == 'book':
        convertor = strip.book

    elif 'models' in source_dir or specified_source == 'models':
        convertor = strip.models

    if not os.path.exists(os.path.dirname(extracted_source_dir)):
        print extracted_source_dir, ' is not a valid path'
        return

    if convertor:
        if output_dir:
            convertor(extracted_source_dir, version, output_dir)
        elif settings.EXTERNAL_TEMPLATE_DIR:
            convertor(extracted_source_dir, version, settings.EXTERNAL_TEMPLATE_DIR)
        else:
            print 'Please provide an output dir or set settings.EXTERNAL_TEMPLATE_DIR'
            return
