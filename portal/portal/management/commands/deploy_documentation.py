from django.core.management import BaseCommand
from deploy import documentation


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Usage: python manage.py deploy_documentation --source=<source> --dest_gen_docs_dir=<dest_gen_docs_dir> --doc_version=<version>"

    def add_arguments(self, parser):
<<<<<<< HEAD
        print 'add_arguments'
        parser.add_argument('source_dir', nargs='+')
        parser.add_argument('version', nargs='+')
        parser.add_argument('output_dir', nargs='+')
        parser.add_argument('specified_source', nargs='+')

    # A command must define handle()
    def handle(self, *args, **options):
        print 'handle options'
        print options
        if 'source_dir' in options:
            documentation.transform(
                options['source_dir'][0], options['version'][0], options['output_dir'][0],
                options['specified_source'][0])
=======
        parser.add_argument('--source', dest='source')
        parser.add_argument('--dest_gen_docs_dir', dest='dest_gen_docs_dir')
        parser.add_argument('--doc_version', dest='doc_version')

    # A command must define handle()
    def handle(self, *args, **options):
        documentation.transform(
            options['source'],
            options.get('dest_gen_docs_dir', None),
            options['doc_version'])
>>>>>>> 3e40f7cb527e84076156588f4e7780f0993127d1
