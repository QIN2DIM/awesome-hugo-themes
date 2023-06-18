# -*- coding: utf-8 -*-
# Time       : 2021/10/3 8:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
from __future__ import annotations

import asyncio
import sys
import typing
from abc import ABC, abstractmethod
from asyncio import create_task
from typing import Iterable

import aiohttp
from aiohttp import ClientSession
from gevent.queue import Queue


class AshFramework(ABC):
    def __init__(self, work_q: Queue = None, docker: Iterable = None):
        if sys.platform.startswith("win") or "cygwin" in sys.platform:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        else:
            asyncio.set_event_loop(asyncio.new_event_loop())

        # 任务容器：queue
        self.work_q = work_q or Queue()
        self.done_q = Queue()
        # 任务容器：迭代器
        self.docker = docker
        # 任务队列满载时刻长度
        self.max_queue_size: int = 0

    async def _launch(self, session: aiohttp.ClientSession = None):
        while not self.work_q.empty():
            context = self.work_q.get_nowait()
            await self._control_driver(context, session=session)

    @abstractmethod
    async def _control_driver(self, context: typing.Any, session: ClientSession):
        """并发函数"""

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

    async def async_fire(self):
        self.preload()
        self._overload()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51"
        }
        conn = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
            task_list = []
            for _ in range(64):
                task = create_task(self._launch(session))
                task_list.append(task)
            await asyncio.wait(task_list)

        self.offload()

    def perform(self):
        asyncio.run(self.async_fire())
