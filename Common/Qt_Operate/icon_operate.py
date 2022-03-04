import warnings

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget

from need.Common.static_file_find import get_file_path


def set_icon(by_op: QWidget, _icon: str):
    """
    给QWidget设置图标
    """
    icon = QIcon()
    icon.addPixmap(QPixmap(get_file_path(_icon)), QIcon.Normal, QIcon.Off)
    try:
        print(icon.isNull())
        for _ in ['setIcon',
                  
                  'setWindowIcon'
                  ]:
            fun = getattr(by_op, _, None)
            if fun:
                fun(icon)
        # by_op.setWindowIcon(icon)
    except:
        warnings.warn("设置图标失败")
    

if __name__ == '__main__':
    """
    Main run
    """
    a =  QPushButton()
    