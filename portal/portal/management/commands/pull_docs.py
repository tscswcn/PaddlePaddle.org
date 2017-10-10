from django.core.management import BaseCommand
from git import Repo
import os
import shutil


#The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):
    # Show this when the user types help
    help = "Usage: python manage.py pull_docs <version>"

    def add_arguments(self, parser):
        parser.add_argument('version', nargs='+')
        parser.add_argument('dest_dict', nargs='+', )

    # A command must define handle()
    def handle(self, *args, **options):
        book_repo_path = 'git@github.com:PaddlePaddle/book.git'
        models_repo_path = 'git@github.com:PaddlePaddle/models.git'

        temp_dict = 'temp'
        book_dest = 'temp/book'
        models_dest = 'temp/models'

        # Clone Book repo
        try:
            Repo.clone_from(book_repo_path, book_dest)
        except:
            print "Already cloned book repo"

        # Clone Models repo
        try:
            Repo.clone_from(models_repo_path, models_dest)
        except:
            print "Already cloned models repo"

        # Set dest_dict
        dest_dict_list = options['dest_dict']
        dest_dict = dest_dict_list[0] if dest_dict_list else None

        if dest_dict == None:
            raise
        else:
            print "Destination: %s" % dest_dict

        book_repo = Repo(book_dest)
        models_repo = Repo(models_dest)

        if 'version' in options:
            for version in options['version']:
                print 'Prepare version: %s' % version
                version_dict = '%s/%s' % (dest_dict, version)

                # Clean the dest folder
                if not os.path.exists(version_dict):
                    print "Create dir at: %s" % version_dict
                    os.makedirs(version_dict)

                book_repo.git.checkout(version)
                models_repo.git.checkout(version)

                if os.path.exists(version_dict):
                    print "Remove all files at: %s" % version_dict
                    shutil.rmtree(version_dict)

                print "Start copying"
                shutil.copytree(temp_dict, version_dict, symlinks=True)

