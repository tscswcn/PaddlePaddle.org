import os
import json
import re

from django.core.management import BaseCommand
from django.conf import settings
import docker

from deploy.operators import generate_operators_page
from deploy.sitemap_generator import get_destination_documentation_dir, get_sitemap_destination_path, \
    get_operator_sitemap_name, generate_operators_sitemap


DOCKER_IMAGE_NAME_TEMPLATE = 'paddlepaddle/paddle:%s'


#The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Usage: python manage.py update_operator_docs"

    def handle(self, *args, **options):
        path = '%s/docs' % settings.EXTERNAL_TEMPLATE_DIR
        version_re = re.compile('^[0-9]+\.[0-9]+\.[0-9]+$')

        print 'Running update_operator_docs command on path %s ...' % path

        for root, dirs, files in os.walk(path):
            if root == path:
                for dir in dirs:
                    full_path = '%s/%s/documentation' % (path, dir)

                    if dir == 'develop':
                        # always update operator docs for 'develop' branch
                        self._update_operator_docs_for_version(full_path, dir)
                    elif version_re.match(dir):
                        if dir != '0.9.0' and dir != '0.10.0':
                            # Only add operators for version != 0.9.0 or 0.10.0
                            existing_sitemap_path = '%s/%s' % (full_path, get_operator_sitemap_name('en'))

                            if not os.path.isfile(existing_sitemap_path):
                                # only update operator docs for versions if site.operators.en.json does not
                                # already exists
                                self._update_operator_docs_for_version(full_path, dir)

        print 'Complete update_operator_docs'


    def _update_operator_docs_for_version(self, path, version):
        try:
            client = docker.from_env()
            print '*** Updating operator documentation at %s ***' % path

            docker_image_name = None
            if version == 'develop':
                docker_image_name = DOCKER_IMAGE_NAME_TEMPLATE % 'latest'
            else:
                docker_image_name = DOCKER_IMAGE_NAME_TEMPLATE % version

            print 'Pulling docker image: %s' % docker_image_name
            client.images.pull(docker_image_name)

            print 'Generating operator docs...'
            operator_doc_json_string = client.containers.run(docker_image_name, 'print_operators_doc')

            output_path = get_destination_documentation_dir(version, 'documentation')
            generate_operators_page(operator_doc_json_string, output_path)

            print 'Generating operators sitemap...'
            for lang in ['en', 'zh']:
                generate_operators_sitemap(output_path, lang)

        except Exception as e:
            print 'Cannot update operator docs for path %s: %s' % (path, e)
