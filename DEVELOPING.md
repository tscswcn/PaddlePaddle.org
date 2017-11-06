# PaddlePaddle.org Development Guide

Welcome to PaddlePaddle.org (PPO) development guide.  This guild is intended for developers of the PaddlePaddle.org website, and will cover how to setup a development environment for PPO, how to submit code to github, and finally how to test your changes on the testing enviroments.

## Technology Stack

This website is built using the Python framework [Django](https://www.djangoproject.com/)  (1.8.11). All the content is served from built assets, and as a result, the website setup does not require any database infrastructure.

The webserver running the site is Gunicorn tied with [Nginx](https://www.nginx.com/). We use a Docker container to deploy it to a public cloud.


## Installation

Please see [Installation Guide](INSTALL.md) to get your enviroment setup for development.

## Git branching model

PaddlePaddle.org utilizes a branching model focusing on two main branches, **develop** and **master**.

- **develop**:  Default branch that contains all the latest development code slated for the next release of the product.
- **master**: The main branch that contains the latest production ready release of the product.

This model also utilizes a few supporting branches:

- **feature**:  Feature branches typically resides within a developer's fork and are branched off of *develop* branch.  These branches are used during development of new features and when completed are merged into origin/develop.  They can be named anything except for master, develop, release-\*, or hotfix-\*
- **release**:  When a PaddlePaddle.org is ready for a new release, a developer would create a release branch off of *develop* branch.  No major code changes should occur on this branch.  However minor bug fixes are allowed.  After the release is ready, this branch is merged into *master* (and tagged), at which point the branch will be removed.   
- **hotfix**:  Used to fix critical production issues.  Typically this branch would be created off of *master* brach, and then merged back into *master* and *develop* once the hotfix is complete

Please visit [A successful git branching model](http://nvie.com/posts/a-successful-git-branching-model/) for more details on this structure

## Testing Environments

PaddlePaddle.org utilizes Travis-CI to provide for a continuous integration testing environment with every code checking.  PaddlePaddle.org monitors three branches:

- **develop**:  Checkin to this branch will deploy PaddlePaddle.org to the development environment at [http://staging.paddlepaddle.org:82](http://staging.paddlepaddle.org:82)
- **release-&ast;**:  Checkin to this branch will deploy PaddlePaddle.org to the development environment at [http://staging.paddlepaddle.org](http://staging.paddlepaddle.org)
- **develop**:  Checkin to this branch will deploy PaddlePaddle.org to the development environment at [http://www.paddlepaddle.org](http://www.paddlepaddle.org)

Please see [Deployment Guide](DEPLOY.md) for more details.

