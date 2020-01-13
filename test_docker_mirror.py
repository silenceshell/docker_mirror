import pytest
from docker_mirror import execute_sys_cmd


def test_execute_sys_cmd():
    assert execute_sys_cmd("date") == 0
