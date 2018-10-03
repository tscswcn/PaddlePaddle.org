# PaddlePaddle.org's content + API documentation generator

This repo contains all the tools to generate the English and Chinese version of the official website for [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) (an easy-to-use, efficient, and scalable distributed deep learning platform). Tied with [Django](https://www.djangoproject.com/), these tools augment [Sphinx](http://www.sphinx-doc.org/en/master/)'s documentation generation capabilities.

The tutorials here guide you to setup the website locally, so you can see exactly how your contributions will appear on [paddlepaddle.org](http://paddlepaddle.org).


## Installation

If you are working on improving code documentation (i.e. APIs) and are within a Docker container with PaddlePaddle, perform these steps within the container. You need to do this because the documentation generator for APIs has a dependency on PaddlePaddle.

On the other hand, if you are only improving the text/media content (since you don't need an installed or built PaddlePaddle) OR are building PaddlePaddle on your (host) machine, continue on your host machine.


1. **Download / clone the documentation repo (the PaddlePaddle.org repo does not contain the content):**

    ```bash
    git clone --recurse-submodules https://github.com/PaddlePaddle/FluidDoc
    ```

   You can place this anywhere on the computer; at a later step we will tell PaddlePaddle.org where it is.


2. **Pull PaddlePaddle.org into a new directory and install its dependencies.**

    But before that, make sure you have Python dependencies installed on your OS. For example, on an Ubuntu, run:
    ```bash
    sudo apt-get update && apt-get install -y python-dev build-essential
    ```

    Then,
    ```bash
    git clone https://github.com/PaddlePaddle/PaddlePaddle.org.git
    cd PaddlePaddle.org/portal

    # To install in a virtual environment.
    # virtualenv venv; source venv/bin/activate

    pip install -r requirements.txt
    ```

    *Optional: If you plan on translating website content between English and Chinese for improving PaddlePaddle.org, install [GNU gettext](https://www.gnu.org/software/gettext/) too.*


3. **Run PaddlePaddle.org (locally or through the Docker container).**

    Pass the list of directories (within the cloned FluidDoc directory) you wish to load and build content from (options include `--paddle`, `--book`, `--models`, and `--mobile`)

    ```bash
    ./runserver --paddle <path_to_paddle_dir> --book <path_to_book_dir>
    ```

    Open up your browser and navigate to [http://localhost:8000](http://localhost:8000).
    **NOTE**: *Links may take a few seconds to load the first time around since they are probably being built.*

    **ANOTHER NOTE**: *If you are doing this step through a Docker environment, make sure to map the port 8000 to your host machine*


## Writing new documentation or updating APIs

All content should be written in [Markdown](https://guides.github.com/features/mastering-markdown/) (the GitHub flavor) (even though there are some legacy pieces of content in `docs`).

After you have gone through the installation steps above, here are the steps you need to take:

- Before you start writing, we recommend reviewing these [guidelines on contributing content](https://github.com/PaddlePaddle/PaddlePaddle.org/wiki/Markdown-syntax-guideline).

---


### If you are writing new content:
- Create a new `.md` file OR edit an existing article's file within the appropriate directory of the repo you are contributing to.


###If you have updated the API comments and want to preview the updates:

Inside the Docker or host machine where Paddle is to be rebuilt, either:
-  Run the the script `paddle/scripts/paddle_build.sh` (from the main Paddle repository / codebase).

-  **OR** (if you want control / understanding over the process):
   - Create a new directory in the `Paddle` repo to build Paddle into. Let's call it `build`, for example.
   - Within this new directory, run the following `cmake` and `make` commands to build a new PaddlePaddle:

     ```bash
     cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_DOC=ON -DWITH_GPU=OFF -DWITH_MKL=OFF -DWITH_FLUID_ONLY=ON

     # You may replace `nproc` with the number of processor cores your system can offer for the build.
     make -j `nproc` gen_proto_py framework_py_proto copy_paddle_pybind paddle_python
     ```

   - Export the environment variable `PYTHONPATH` to include the this new `build` directory (or whatever you named it)


Note that if you are using Docker, `paddle_docker_build.sh` rebuilds a new Docker container. This destroys the PaddlePaddle.org installation on that Docker instance, so it is not the suggested way to rebuild your code if you wish to preview documentation.

---

- To view the changes in your browser, click **Refresh Content** on the top-righthand side corner.


## Contributing to improve the tools

We appreciate contribution to various aspects of the platform and supporting content, apart from better presenting these materials. You may fork or clone this repository, or begin asking questions and providing feedback and leave bug reports on Github Issues. Please refer to [Development Guide](DEVELOPING.md) on how to get started.


## Copyright and License

PaddlePaddle.org is provided under the [Apache-2.0 license](https://github.com/PaddlePaddle/Paddle/blob/develop/LICENSE).
