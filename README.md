# PaddlePaddle.org

**PaddlePaddle.org** is the repository for the website of the [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) open source project: an easy-to-use, efficient, and scalable distributed deep learning platform. The goal is to provide a unified web access to all code and documentation related to the PaddlePaddle project. The website is designed to yield uniform user experience and provide access to the latest information about PaddlePaddle.

## Overview

This website is built using the Python framework Django (1.8.11). All the content is served from built assets, and as a result, the website setup does not require any database infrastructure.

The webserver running the site is Gunicorn tied with Nginx. We use a Docker container to deploy it to a public cloud.

### Content Management

This website unifies contents from diverse opensource repos related to different technical and non-technical aspects of project, including:

* [Documentation, Getting started and how-to guide](https://github.com/PaddlePaddle/Paddle)
* [Application of Deep Learning with PaddlePaddle](https://github.com/PaddlePaddle/book)
* [Explanation of models available](https://github.com/PaddlePaddle/models)
* [Blog](https://github.com/PaddlePaddle/blog)

All of the content generated from these individual repos are compiled using different engines and static website generators. The build steps happen in the cloud using continuous integration, and consequently merges to the master or staging branches in the respective repos.

The following diagram shows how the contents from each of these sources are built:

![workflow](assets/workflow.png)

### Website Design

The website is a dynamically routed application, which unifies various content collections and creates a unified navigation experience.  As a result, the user can jump between, for example, the getting started guide and a detailed model explanation, without having to switch between multiple sites.

Each of the following content categories are composed of a single or multiple content repositories:

* **Documentation**: Combines content from Sphinx generated documentation of the core platform, version changes, and various models which are available for use with the platform.
* **Tutorials**: Combines content from Getting Started Guide, the PaddlePaddle Book, and a How-To Guide (for more advanced topics such as running on Kubernetes and distributed training).
* **PaddlePaddle Homepage**: Combines information from the portal repository on the status and history of the project. The homepage is responsive, for both desktop and mobile viewing.
* **Blog**: Includes recent updates and articles on PaddlePaddle uses and community.

The entire content is available in both Mandarin and English and served using Django's i18n support.

## Installation and Deployment

See [installation instructions](INSTALL.md) for setting up and deploying PaddlePaddle.org 

## How to Contribute

We appreciate contribution to various aspects of the platform and supporting content, apart from better presenting these materials.

You may fork or clone this repository, or begin asking questions and providing feedback and leave bug reports on Github Issues.

* [PaddlePaddle](https://github.com/PaddlePaddle/Paddle/blob/develop/doc/howto/dev/contribute_to_paddle_en.md)
* [Book](https://github.com/PaddlePaddle/book#contribute)

## Copyright and License

PaddlePaddle.org is provided under the [Apache-2.0 license](https://github.com/PaddlePaddle/Paddle/blob/develop/LICENSE).

