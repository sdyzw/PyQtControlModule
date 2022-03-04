import traceback
import warnings
from pathlib import Path

# from psutil import long

from need.Common.base_operate import get_remote_ip_network_disk_path, remote_to_local, random_n_str, del_file_or_dir
from need.setting import settings

ip_flag_path = {
    '192.168.1.134': {'/': ['CAMEL-Metal', '文件中转站'], '/CAMEL-Metal': ['文件中转站', 'CAMEL-软件']},
}


# x80000000 = long(0x80000000)


class ConnectLocalAttr(object):
    FLAG_SIZE = 1
    FLAG_UIDGID = 2
    FLAG_PERMISSIONS = 4
    FLAG_AMTIME = 8
    
    # FLAG_EXTENDED = x80000000
    
    def __init__(self):
        """
        Create a new (empty) SFTPAttributes object.  All fields will be empty.
        """
        self._flags = 0
        self.st_size = None
        self.st_uid = None
        self.st_gid = None
        self.st_mode = None
        self.st_atime = None
        self.st_mtime = None
        self.filename = None
        self.attr = {}
    
    def initialize(self, obj: Path):
        if not obj.exists():
            return
        
        stat = obj.stat()
        
        self.filename = obj.name
        
        attr_list = []
        attr_list = ['st_size', 'st_uid', 'st_gid', 'st_mode', 'st_atime', 'st_mtime']
        attr_list = ['st_size', 'st_uid', 'st_gid', 'st_mode', 'st_atime', 'st_mtime']
        
        for field in attr_list:
            setattr(self, field, getattr(stat, field, None))


class ConnectLocal:
    
    def __init__(self, ip, *args, **kwargs):
        if not ip:
            ip = settings.host
        self.ip = ip
        self.start = None
        self.device = None
        self.connect_flag = False
        self._get_local_info()
        # super().__init__(*args, **kwargs)
    
    def _get_local_info(self):
        flag_path = ip_flag_path.get(self.ip)
        if not flag_path:
            return
        
        self.start, self.device = get_remote_ip_network_disk_path(flag_path)
        if all([self.start, self.device]):
            self.connect_flag = True
        print(self.start, self.device)
    
    def close(self):
        del self
    
    def get(self, remote, local, callback=None):
        actual_remote = remote_to_local(self.device, self.start, remote)
        local = self.get_en_file(local)
        
        flag = self._local_file_a_to_b(actual_remote, local)
        a = 1
        if flag:
            a = self.get_de_file(local)
        # callback(a, a)
        if callback:
            try:
                callback(a, a)
            except:
                traceback.print_exc()
    
    def put(self, local, remote, callback=None):
        print(local, remote, callback, 11111111111111111111)
        actual_remote = remote_to_local(self.device, self.start, remote)
        actual_remote = self.get_en_file(actual_remote)
        
        flag = self._local_file_a_to_b(local, actual_remote, )
        # a = self.get_de_file(actual_remote)
        # callback(a, a)
        
        a = 1
        if flag:
            a = self.get_de_file(actual_remote)
        if callback:
            try:
                callback(a, a)
            except:
                traceback.print_exc()
        # if callback:
        #     try:
        #         callback(1, 1)
        #     except:
        #         traceback.print_exc()
    
    def listdir_attr(self, path):
        if ':' not in str(path):
            path = remote_to_local(self.device, self.start, path)
        p_path = Path(path)
        filelist = []
        if not p_path.exists() or not p_path.is_dir():
            return []
        for _ in p_path.iterdir():
            file_attr = ConnectLocalAttr()
            file_attr.initialize(_)
            filelist.append(file_attr)
        return filelist
    
    def mkdir(self, dir_):
        try:
            if ':' not in str(dir_):
                dir_ = remote_to_local(self.device, self.start, dir_)
            Path(dir_).mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise PermissionError('拒绝访问：无权限')
        except:
            traceback.print_exc()
            raise Exception('新建错误')
    
    def stat(self, path):
        
        if ':' not in str(path):
            path = remote_to_local(self.device, self.start, path)
        p_path = Path(path)
        return p_path.stat()
    
    @staticmethod
    def get_en_file(file_):
        if isinstance(file_, Path):
            file_ = file_.as_posix()
        file_ += '.tmp'
        return file_
    
    @staticmethod
    def get_de_file(file_):
        p_local = Path(file_)
        a_size = p_local.stat().st_size
        
        def change_old_file(old_file: Path):
            try:
                old_add_str = f'.old {random_n_str(4)}'
                old_name = old_file.as_posix() + old_add_str
                old_file.rename(old_name)
            except Exception as e:
                traceback.print_exc()
                print('重命名旧文件失败')
                return change_old_file(old_file)
            return old_name
        
        if file_[-4:] == '.tmp':
            n_file = Path(file_[:-4])
            del_name = None
            if n_file.exists():
                del_name = change_old_file(n_file)
            
            p_local.rename(file_[:-4])
            if del_name:
                del_file_or_dir(del_name)
        return a_size
    
    def _local_file_a_to_b(self, a, b, b_is_dir=False, callback=None):
        
        """
        本地复制文件
        :param a: 文件
        :param b: 路径或者文件本身
        :param b_is_dir: b是文件或者路径
        :return:
        """
        
        print('本地文件复制：a复制到b', a, b)
        if not all([a, b, ]):
            warnings.warn("路径为空，无法进行当前操作")
            return
        if Path(a) == Path(b):
            return
        p_b = Path(b)
        
        if not Path(a).exists():
            return False
        
        sum_st_size = 0
        
        if not b_is_dir:
            p_b.parent.mkdir(parents=True, exist_ok=True)
            p_a = Path(a)
            if not p_a.exists():
                return
            p_b.write_bytes(p_a.read_bytes())
            sum_st_size += p_a.stat().st_size
        else:
            if not isinstance(a, list):
                a = [a]
            for be_a in a:
                p_be_a = Path(be_a)
                if not p_be_a.exists():
                    continue
                
                new = p_b.joinpath(p_be_a.name)
                new.parent.mkdir(parents=True, exist_ok=True)
                new.write_bytes(p_be_a.read_bytes())
                sum_st_size += p_be_a.stat().st_size
        return True
        # try:
        #     if callback:
        #         callback()


if __name__ == '__main__':
    """
    Main run
    """
    
    """
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/1A.51Bp_2g008Dn1', WindowsPath('tmp/1A.51Bp_2g008Dn1'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5CFF670>) 111111111111111111
192.168.1.134 22
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/2020_pgD7A30.0nA', WindowsPath('tmp/2020_pgD7A30.0nA'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5D12790>) 111111111111111111
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/220214-094325.png', WindowsPath('tmp/220214-094325.png'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5D12940>) 111111111111111111
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/220214-094334.png', WindowsPath('tmp/220214-094334.png'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5D129D0>) 111111111111111111
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/0Dng.A_2B0p00427', WindowsPath('tmp/0Dng.A_2B0p00427'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5D12A60>) 111111111111111111
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/220214-120304.png', WindowsPath('tmp/220214-120304.png'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5D12B80>) 111111111111111111
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/220214-120314.png', WindowsPath('tmp/220214-120314.png'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5D12C10>) 111111111111111111
    ('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/220214-120450.png', WindowsPath('tmp/220214-120450.png'), <function set_label_pic.<locals>.end_callback at 0x000001FCD5D12CA0>)
    """
    ip = '192.168.1.134'
    a = ConnectLocal(ip)
    # a.get('/CAMEL-Metal/ERP图片库/ERP-Image/Image/Mold/2020_pgD7A30.0nA', 'tmp/220214-094325.png')
    # a.put(r'E:\Code\ERP-Product\error\2022年2月28日 10点58分.txt', r'CAMEL-Metal/文件中转站\CAMEL-软件/测试.txt')
    print(a.listdir_attr(r'CAMEL-Metal/文件中转站\CAMEL-软件\CAMEL-ERP\6.3.2\6.3.2.3'))
