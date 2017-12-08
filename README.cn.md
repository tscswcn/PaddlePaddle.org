# PaddlePaddle.org

**PaddlePaddle.org** 是库网站 [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) 的开源项目：一个易于使用的，高效的，可扩展的分布式平台的深度学习。我们的目标是提供一个统一的网络 访问所有代码和PaddlePaddle项目相关的文档。该网站的目的是给用户提供统一一致的用户体验和提供关于PaddlePaddle最新的信息。
## 贡献 PaddlePaddle.org

我们感謝各个方面的贡献。

你可以克隆这个代碼库，或开始问问题和提供反馈和bug报告。

## PaddlePaddle.org 文档生成和查看器工具

**前提**: 我们推荐使用 Docker 来执行文档生成和查看器工具
[安装Docker](https://docs.docker.com/engine/installation/).

paddlepaddle.org不仅可以运行 [http://paddlepaddle.org](http://paddlepaddle.org)，它也可以生成文件并在本地机器上查看文档。运行文档工具，请看看 [视频教程](https://github.com/bobateadev/images/raw/master/viewer_tool_demo_cn.mp4)
或按照下面的说明：

### 文档查看器工具

#### 1) 运行 PaddlePaddle.org Docker Image. 
```
docker run -it -p 8000:8000 paddlepaddle/paddlepaddle.org:latest
```

#### 2) 打开浏览器，导航到 [http://localhost:8000](http://localhost:8000).

### 文档生成和查看器工具 (文件的创造者)

#### 1) Clone Paddle库
注意：如果您已经拥有这些存储库的本地副本，请跳过此步骤。
```
mkdir paddlepaddle
cd paddlepaddle
git clone git@github.com:PaddlePaddle/Paddle.git
git clone git@github.com:PaddlePaddle/book.git
git clone git@github.com:PaddlePaddle/models.git
```
 
现在你的目录应该看起来像：

```
- paddlepaddle
    - Paddle
    - book
    - models
    - mobile
```

#### 2) 在 *paddlepaddle* 目录运行 PaddlePaddle.org Docker Image
**注意:** PaddlePaddle.org 会在 -v (volume) 指定的内容存储库运行命令

```
docker run -it -p 8000:8000 -v `pwd`:/var/content paddlepaddle/paddlepaddle.org:latest
```

#### 3) 打开浏览器，导航到 [http://localhost:8000](http://localhost:8000).

### 不想使用 Docker?
你还可以通过运行Django框架直接激活工具的服务器。使用下面的命令来运行它。

#### 1) 复制 Paddle repositories 
```
mkdir paddlepaddle
cd paddlepaddle
git clone git@github.com:PaddlePaddle/Paddle.git
git clone git@github.com:PaddlePaddle/book.git
git clone git@github.com:PaddlePaddle/models.git
git clone git@github.com:PaddlePaddle/PaddlePaddle.org.git
```

#### 2) 在 *paddlepaddle* 目录运行PaddlePaddle.org.
```
export CONTENT_DIR=<path_to_paddlepaddle_working_directory> 
export ENV=''
cd PaddlePaddle.org/portal/
pip install -r requirements.txt
python manage.py runserver
```
#### 3) 打开浏览器，导航到 [http://localhost:8000](http://localhost:8000).

## 其他资源
- 想开发 PaddlePaddle.org，请参阅[指导](DEVELOPING.md)  
- 内容存储库是如何构造和读取的: [内容存储库](CONTENT_REPO.md)

## Copyright and License

PaddlePaddle.org is provided under the [Apache-2.0 license](https://github.com/PaddlePaddle/Paddle/blob/develop/LICENSE).

