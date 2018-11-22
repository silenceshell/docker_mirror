#!/usr/bin/python
# coding=utf8

import platform
import re
import time
import os
import docker
import json

mirror_prefix = "--registry-mirror="

mirrors = {
    "tencent": "https://mirror.ccs.tencentyun.com",
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
    },
    "Deepin": {
        "config": "/etc/default/docker",
        "prefix": "DOCKER_OPTS="
    }
}

docker_ce_config_map = {
    "Deepin": {
        "config": "/etc/docker/daemon.json",
        # "prefix": "registry-mirror"
    }
}

def get_dist():
    return platform.linux_distribution()[0]


def get_config(dist):
    return docker_config_map[dist]["config"]


def get_config_ce(dist):
    return docker_ce_config_map[dist]["config"]


def get_prefix(dist):
    return docker_config_map[dist]["prefix"]


def get_new_options(option, mirror):
    option = option.strip()
    quota = option[len(option) - 1]
    if mirror_prefix in option:
        r1 = re.compile('[\'\"]')
        results1 = r1.split(option)

        r2 = re.compile('[\s]')
        results2 = r2.split(results1[1].strip())
        for i in range(len(results2)):
            if results2[i].startswith(mirror_prefix):
                results2[i] = mirror_prefix + mirror
        new_option = results1[0] + quota + " ".join(results2) + quota
    else:
        new_option = option[:-1] + " " + mirror_prefix + mirror + quota
    new_option += "\n"
    return new_option


def execute_sys_cmd(cmd):
    result = os.system(cmd)
    return result


def set_docker_config(mirror):
    dist = get_dist()
    docker_config = get_config(dist)
    prefix = get_prefix(dist)
    new_line = ""
    options = ""
    with open(docker_config, "r") as f:
        for line in f:
            if line.startswith(prefix):
                options = get_new_options(line, mirror)
            else:
                new_line += line
        if options == "":
            options = prefix + "\'" + mirror_prefix + mirror + "\'"

    with open(docker_config, "w") as f:
        f.write(new_line)
        f.writelines(options)

def set_docker_config_ce(mirror):
    dist = get_dist()
    docker_config = get_config_ce(dist)
    config_dict={}
    if os.path.exists(docker_config) != True:
        # if file not exist, create it first.
        os.mknod(docker_config, 0644)
    else:
        with open(docker_config, "r") as f:
            config_dict = json.load(f)

    config_dict[u'registry-mirrors'] = [mirror]

    with open(docker_config, "w") as f:
        json.dump(config_dict, f)

def restart_docker_daemon():
    execute_sys_cmd("systemctl restart docker")


def get_speed(mirror, mirror_url):
    client = docker.from_env()
    version = client.version()[u'Version']
    if "ce" in version:
        set_docker_config_ce(mirror_url)
    else:
        set_docker_config(mirror_url)
    
    restart_docker_daemon()

    # try to delete busybox image in case.
    execute_sys_cmd("docker rmi registry:2 -f 1> /dev/null 2>&1")

    print "pulling registry:2 from {mirror}".format(mirror=mirror)
    begin_time = time.time()

    execute_sys_cmd("docker pull registry:2 1> /dev/null 2>&1")
    end_time = time.time()

    cost_time = end_time - begin_time
    print "mirror {mirror} cost time: {cost_time}\n".format(mirror=mirror, cost_time=cost_time)

    # delete centos images every time.
    execute_sys_cmd("docker rmi registry:2 -f 1> /dev/null 2>&1")

    return 204800 / cost_time

if __name__ == "__main__":
    max_speed = 0
    best_mirror = ""
    best_mirror_url = ""
    for k, v in mirrors.items():
        speed = get_speed(k, v)
        if speed > max_speed:
            max_speed = speed
            best_mirror = k
            best_mirror_url = v

    print "best mirror is: {mirror}, set docker config and restart docker daemon now.".format(mirror=best_mirror)
    set_docker_config(best_mirror_url)
    restart_docker_daemon()
