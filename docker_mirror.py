#!/usr/bin/python
# coding=utf8

mirrors = [

]



'''
centos

/etc/sysconfig/docker

--

OPTIONS='--selinux-enabled --log-driver=journald --signature-verification=false --registry-mirror=http://hub-mirror.c.163.com'

systemctl restart docker

docker pull centos

docker rmi centos
--


'''

import platform


mirrors = {
    "netease": "http://hub-mirror.c.163.com",
    "ustc": "https://docker.mirrors.ustc.edu.cn",
    "official": "https://registry.docker-cn.com",
    "aliyun": "https://2h3po24q.mirror.aliyuncs.com"  # use your own aliyun mirror url instead.
}

docker_config_map = {
    "Ubuntu": {
        "config": "/etc/default/docker",
        "prefix": "DOCKER_OPTS="
    },
    "CentOS Linux": {
        "config": "/etc/sysconfig/docker",
        "prefix": "OPTIONS="
    }
}


def get_dist():
    return platform.linux_distribution()[0]


def get_config(dist):
    return docker_config_map[dist]["config"]


def get_prefix(dist):
    return docker_config_map[dist]["prefix"]


def get_new_options(option, mirror):
    # OPTIONS='--selinux-enabled --log-driver=journald --signature-verification=false'
    arr = option.strip()[:-1] + "" + mirror
    print arr
    return arr


def get_speed(mirror):
    dist = get_dist()
    docker_config = get_config(dist)
    prefix = get_prefix(dist)
    new_line = ""
    with open(docker_config, "r") as f:
        for line in f:
            # print line
            if line.startswith(prefix):
                line = get_new_options(line, mirror)
            new_line += line

    return 0

if __name__ == "__main__":
    max_speed = 0
    max_mirror = ""
    for k, v in mirrors.items():
        speed = get_speed(v)
        if speed > max_speed:
            max_mirror = k
