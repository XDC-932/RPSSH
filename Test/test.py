
class TestDisp():
    def __init__(self):
        pass

    # 测试显示功能函数
    def __test_show__(self, win):
        try:
            win.runtime_msg = "demo test data"
            win.info.state = ds.State.run.value
            thread.daemon(self.__test_data_gen__, win)
            win.bnt_en.start = False
            win.bnt_en.stop = True
            win.disp_thread = thread.daemon(self.__auto_refresh_wave__, win)
        except Exception as e:
            win.runtime_msg = f"Test show failed: {e}"
            raise e

    # 测试数据生成
    def __test_data_gen__(self, win):
        try:
            while True:
                if win.info.state == ds.State.stop.value:
                    break
                else :
                    data = rng.gen_list(16384)
                    for val in data:
                        win.data.put(val)
                    time.sleep(1)
        except Exception as e:
            win.runtime_msg = f"Test data generation failed: {e}"
            raise e