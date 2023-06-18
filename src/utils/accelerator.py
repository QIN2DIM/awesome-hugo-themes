# -*- coding: utf-8 -*-
# Time       : 2021/10/3 8:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from typing import Iterable

import gevent
from gevent.queue import Queue


class CoroutineSpeedup(ABC):
    def __init__(self, work_q: Queue = None, docker: Iterable = None):
        # 任务容器：queue
        self.work_q = work_q or Queue()
        self.done_q = Queue()
        # 任务容器：迭代器
        self.docker = docker
        # 协程数
        self.power: int = 1
        # 任务队列满载时刻长度
        self.max_queue_size: int = 0

    def _launch(self):
        while not self.work_q.empty():
            task = self.work_q.get_nowait()
            self.control_driver(task)

    def _overload(self):
        if self.docker:
            for task in self.docker:
                self.work_q.put_nowait(task)
        self.max_queue_size = self.work_q.qsize()

    @abstractmethod
    def preload(self):
        """数据加载"""

    def offload(self):
        """数据卸载"""

    @abstractmethod
    def control_driver(self, context: typing.Any):
        """并发函数"""

    def fire(self, power: int | None = 8) -> None:
        self.preload()
        self._overload()

        if self.max_queue_size != 0:
            self.power = min(power, self.max_queue_size)

        task_list = [gevent.spawn(self._launch) for _ in range(self.power)]
        gevent.joinall(task_list)

        self.offload()
