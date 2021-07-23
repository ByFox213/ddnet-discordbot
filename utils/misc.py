#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import functools
import os
from asyncio.subprocess import PIPE
from typing import Awaitable, Callable, Tuple, Union

SHELL = os.getenv('SHELL')

async def run_process_shell(cmd: str, timeout: float=90.0) -> Tuple[str, str]:
    sequence = f'{SHELL} -c \'{cmd}\''
    proc = await asyncio.create_subprocess_shell(sequence, stdout=PIPE, stderr=PIPE)

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError('Process timed out')
    else:
        return stdout.decode(), stderr.decode()

async def run_process_exec(program: str, *args: str, timeout: float=90.0) -> Tuple[str, str]:
    proc = await asyncio.create_subprocess_exec(program, *args, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError('Process timed out')
    else:
        return stdout.decode(), stderr.decode()

def executor(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        fn = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, fn)
    return wrapper

async def maybe_coroutine(func: Union[Awaitable, Callable], *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
