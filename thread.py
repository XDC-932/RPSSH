import threading

def daemon(func, *args, **kwargs):
	thread = threading.Thread(target=func, args=args, kwargs=kwargs)
	thread.daemon = True  # 设置为守护线程
	thread.start()
	return thread
