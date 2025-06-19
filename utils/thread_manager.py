#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
线程管理工具
提供线程池和异步任务执行功能
"""

import threading
import queue
import time
from typing import Callable, Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

class ThreadManager:
    """线程管理器，用于管理后台线程和执行异步任务"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式，确保只有一个线程管理器实例"""
        if cls._instance is None:
            cls._instance = super(ThreadManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化线程管理器"""
        if self._initialized:
            return
            
        # 线程池，用于执行异步任务
        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="StatusBar")
        # 任务队列，用于存储待执行的任务
        self.task_queue = queue.Queue()
        
        # 结果缓存，用于存储异步任务的结果
        self.results = {}
        
        # 启动后台线程处理任务
        self.stop_flag = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        # 标记为已初始化
        self._initialized = True
    
    def _worker(self):
        """工作线程，从队列中获取任务并执行"""
        while not self.stop_flag.is_set():
            try:
                # 从队列中获取任务，最多等待1秒
                task_id, func, args, kwargs, callback = self.task_queue.get(timeout=1)
                
                # 执行任务
                try:
                    result = func(*args, **kwargs)
                    self.results[task_id] = result
                    if callback:
                        callback(result)
                except Exception as e:
                    print(f"任务 {task_id} 执行失败: {e}")
                    self.results[task_id] = None
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except queue.Empty:
                # 队列为空，继续循环
                continue
    
    def submit_task(self, func: Callable, *args, 
                  task_id: Optional[str] = None,
                  callback: Optional[Callable[[Any], None]] = None, 
                  **kwargs) -> str:
        """
        提交任务到线程池执行
        
        Args:
            func: 要执行的函数
            *args: 函数的位置参数
            task_id: 任务ID，如果为None则自动生成
            callback: 任务完成后的回调函数
            **kwargs: 函数的关键字参数
            
        Returns:
            任务ID
        """
        # 如果没有提供任务ID，则使用时间戳生成
        if task_id is None:
            task_id = f"task_{time.time()}"
        
        # 将任务添加到队列
        self.task_queue.put((task_id, func, args, kwargs, callback))
        
        return task_id
    
    def get_result(self, task_id: str, wait: bool = False, timeout: float = None) -> Any:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            wait: 是否等待任务完成
            timeout: 等待超时时间（秒）
            
        Returns:
            任务结果，如果任务未完成且wait为False，则返回None
        """
        if task_id not in self.results and wait:
            # 等待任务完成
            start_time = time.time()
            while task_id not in self.results:
                time.sleep(0.1)
                if timeout is not None and time.time() - start_time > timeout:
                    return None
        
        return self.results.get(task_id)
    
    def shutdown(self):
        """关闭线程管理器"""
        self.stop_flag.set()
        if self.worker_thread.is_alive():
            self.worker_thread.join(2)  # 等待最多2秒
        self.executor.shutdown(wait=False)

