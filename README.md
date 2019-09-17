# docker_mirror

查找国内最快的docker镜像源。

Python编写，需要root权限，支持Ubuntu/Deepin/Centos7/Arch，其他操作系统需要补充。

Ubuntu/CentOS/Deepin/Arch支持docker community.

使用方法非常简单，下载 [docker_mirror.py](https://raw.githubusercontent.com/silenceshell/docker_mirror/master/docker_mirror.py) 文件到本地，执行下面的命令即可，脚本会自动从Azure, Tencent, Aliyun, Netease, ustc尝试下载`registry:2`镜像，并计算使用的时间；按使用时间最少的镜像设置docker配置，并重启docker进程。

```
sudo apt install python-pip
sudo pip install docker -i https://mirrors.aliyun.com/pypi/simple
sudo python ./docker_mirror.py
```

脚本执行后，就可以直接使用最快的docker镜像了。

嗖嗖嗖！
