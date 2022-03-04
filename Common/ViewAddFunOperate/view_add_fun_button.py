import types

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QPushButton

from need.setting import settings

button_stat = {
    'refresh': {
        'enable' : True,
        'visible': True
    }
}


class ViewAddFunctionButton:
    """
    识图添加功能按键
    """
    
    refresh_style = """QPushButton{

                        font: bold 14px;
                        color: rgb(0, 85, 255);
                        border: 1px solid rgb(0, 0, 0);
                        border-radius: 12px;
                        background-color: rgb(230, 230, 230);
                    }

                    QPushButton:hover{
                        font: bold 16px;
                        color: rgb(0, 40, 255);
                        background-color: rgb(217, 217, 217);
                        padding-bottom: 2px;
                    }

                    QPushButton:pressed{

                        color: rgb(0, 0, 255);
                        background-color: rgb(189, 189, 189);
                        padding-top: 2px;
                    }

                    QPushButton:disabled{

                        color: rgb(173, 173, 173);
                        background-color: rgb(234, 234, 234);
                    }"""
    
    refresh_style1 = """
                        QPushButton{
                        border: 1px solid rgb(0, 0, 0);
                        border-radius: 12px;
                    }

                    QPushButton:hover{
                        background-color: rgb(171, 171, 171);
                    }

                    QPushButton:pressed{
                        background-color: rgb(121, 121, 121);
                    padding-top:2px;
                    }"""
    
    def __init__(self, view: QWidget):
        super().__init__()
        self.view = view
        self._button_flag = None
    
    def add_refresh_button(self):
        if not self.view or not isinstance(self.view, QWidget):
            return
        pb_refresh = self._new_a_refresh_button(self.view)
        setattr(self.view, '_pb_refresh', pb_refresh)
        
        self.view.enterEvent = types.MethodType(self.enterEvent, self.view)
        self.view.leaveEvent = types.MethodType(self.leaveEvent, self.view)
        
        refresh = getattr(self.view, 'refresh', None)  # lambda x=self.view:print(f'{self.view}不存在刷新函数')
        
        if not refresh:
            print(f'{self.view}不存在刷新函数')
            return self.pb_refresh.setEnabled(False)
        pb_refresh.clicked.connect(refresh)
        pb_refresh.clicked.connect(lambda: pb_refresh.setEnabled(False))
        pb_refresh.clicked.connect(lambda: QTimer.singleShot(2000, lambda: pb_refresh.setEnabled(True)))
    
    def open_button(self):
        self._button_flag = True
        self.pb_refresh.setEnabled(True)
    
    def close_button(self):
        self._button_flag = False
        self.pb_refresh.setEnabled(False)
    
    def _new_a_refresh_button(self, pa):
        self.pb_refresh = QPushButton('↻', pa)
        self.pb_refresh.resize(24, 24)
        self.pb_refresh.setStyleSheet(self.refresh_style)
        self.pb_refresh.setToolTip('刷新当前\n界面信息')
        
        self.pb_refresh.setVisible(False)
        
        return self.pb_refresh
    
    @staticmethod
    def enterEvent(self, a0: QtCore.QEvent) -> None:
        pb_refresh: QPushButton = getattr(self, '_pb_refresh', None)
        
        visible = button_stat.get('refresh', {}).get('visible', True)
        enable = button_stat.get('refresh', {}).get('enable', True)
        
        if not pb_refresh or not visible:
            return
        pb_refresh.setEnabled(enable)
        pb_refresh.setGeometry(
                self.width() - pb_refresh.width(),
                0,
                pb_refresh.width(),
                pb_refresh.height()
        )
        pb_refresh.setVisible(True)
        super(self.__class__, self).enterEvent(a0)
    
    @staticmethod
    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        pb_refresh = getattr(self, '_pb_refresh', None)
        if not pb_refresh:
            return
        pb_refresh.setVisible(False)
        super(self.__class__, self).leaveEvent(a0)


def load_setting():
    setting = settings.setdefault('setting', {}).setdefault('ViewAddFunctionButton', {})
    button_stat.update(setting)
