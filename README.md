## How to run

####1) Clone Paddle repositories
```
mkdir paddlepaddle
cd paddlepaddle
git clone git@github.com:PaddlePaddle/Paddle.git
git clone git@github.com:PaddlePaddle/book.git
git clone git@github.com:PaddlePaddle/models.git
```

####2) Run PaddlePaddle.org Docker Image within "paddlepaddle" subdirectory

```
docker run -d -p 8000:8000 -v `pwd`:/var/content nguyenthuan/paddlepaddle.org:latest
```

####3) Open up your browser and navigate to [http://localhost:8000](http://localhost:8000).

## Additional Resources
- [Full installation instructions](INSTALL.md)
- [Content repositories](CONTENT_REPO.md)

## How to Contribute

We appreciate contribution to various aspects of the platform and supporting content, apart from better presenting these materials.

You may fork or clone this repository, or begin asking questions and providing feedback and leave bug reports on Github Issues.

* [PaddlePaddle](https://github.com/PaddlePaddle/Paddle/blob/develop/doc/howto/dev/contribute_to_paddle_en.md)
* [Book](https://github.com/PaddlePaddle/book#contribute)

## Copyright and License

PaddlePaddle.org is provided under the [Apache-2.0 license](https://github.com/PaddlePaddle/Paddle/blob/develop/LICENSE).

