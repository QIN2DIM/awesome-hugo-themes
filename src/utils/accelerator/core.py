# -*- coding: utf-8 -*-
# Time       : 2021/10/3 8:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

import gevent
from gevent.queue import Queue


class CoroutineSpeedup:

    def __init__(self, work_q: Queue = None, task_docker=None, power: int = None, debug: bool = True):
        # 任务容器：queue
        self.work_q = work_q if work_q else Queue()
        self.done_q = Queue()
        # 任务容器：迭代器
        self.task_docker = task_docker
        # 协程数
        self.power = power
        # 是否打印日志信息
        self.debug_logger = debug
        # 任务队列满载时刻长度
        self.max_queue_size = 0

    def launch(self):
        while not self.work_q.empty():
            task = self.work_q.get_nowait()
            self.control_driver(task)

    def control_driver(self, task):
        """
        rewrite this method
        @param task:
        @return:
        """

    def preload(self):
        """

        :return:
        """

    def offload_task(self):
        """

        @return:
        """
        if self.task_docker:
            for task in self.task_docker:
                self.work_q.put_nowait(task)
        self.max_queue_size = self.work_q.qsize()

    def killer(self):
        """

        @return:
        """
        pass

    def go(self, power: int = 8) -> None:
        """

        @param power: 协程功率
        @return:
        """

        # 任务重载
        self.preload()
        self.offload_task()
        task_list = []
        # 配置弹性采集功率
        power_ = self.power if self.power else power
        if self.max_queue_size != 0:
            power_ = self.max_queue_size if power_ > self.max_queue_size else power_
        self.power = power_
        # 任务启动
        for _ in range(power_):
            task = gevent.spawn(self.launch)
            task_list.append(task)
        gevent.joinall(task_list)
        # 缓存回收
        self.killer()
