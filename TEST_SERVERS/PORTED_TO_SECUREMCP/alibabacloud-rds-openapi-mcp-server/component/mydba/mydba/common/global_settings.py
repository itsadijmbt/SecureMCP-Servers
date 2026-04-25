# -*- coding: utf-8 -*-

class GlobalSettings:
    """
    用于控制服务的全局开关。
    Attributes:
        IS_EXIT (bool): 服务是否退出
    """
    IS_EXIT: bool = False
global_settings = GlobalSettings()
