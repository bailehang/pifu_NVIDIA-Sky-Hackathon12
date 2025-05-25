# skin_analysis/config_loader.py
import yaml
import sys
import os

DEFAULT_CONFIG_FILENAME = 'config.yaml'

def get_config_path(config_filename=None):
    """
    获取配置文件的绝对路径。
    默认在当前脚本所在目录中查找config_filename。
    """
    if config_filename is None:
        config_filename = DEFAULT_CONFIG_FILENAME
    # __file__ 是当前文件的路径 (config_loader.py)
    # os.path.dirname(__file__) 是 config_loader.py 所在的目录 (skin_analysis)
    # 因此，config_path 将是 skin_analysis/config.yaml
    return os.path.join(os.path.dirname(__file__), config_filename)

def load_raw_config_dict(config_path=None):
    """
    从YAML文件加载原始配置字典。
    这个函数只负责加载，不进行过多解释。
    """
    if config_path is None:
        config_path = get_config_path()

    # 对于配置文件本身的读取，我们暂时固定使用 'utf-8'
    # 如果需要让这个也动态配置，会引入更复杂的启动引导问题
    config_file_encoding = 'utf-8' 

    try:
        print(f"正在从以下路径加载配置文件: {config_path} (使用编码: {config_file_encoding})")
        with open(config_path, 'r', encoding=config_file_encoding) as f:
            raw_config = yaml.safe_load(f)
        if raw_config is None: # 如果文件为空或只包含注释，safe_load可能返回None
            print(f"错误: 配置文件 {config_path} 为空或格式不正确。")
            sys.exit(1)
        print("原始配置文件加载成功。")
        return raw_config
    except FileNotFoundError:
        print(f"错误: 配置文件 {config_path} 未找到。")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"错误: 解析配置文件 {config_path} 失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"加载原始配置时发生未知错误: {e}")
        sys.exit(1)

class AppConfig:
    """
    应用程序配置类。
    封装了从原始字典中获取配置项的逻辑，包括默认值和必需项校验。
    """
    def __init__(self, raw_config_dict):
        self._config = raw_config_dict
        self._config_dir = os.path.dirname(os.path.abspath(__file__)) # <<< --- 这行是关键的补充
        self._validate_essential_configs()

    def _validate_essential_configs(self):
        """校验配置文件中必须存在的顶级键和一些关键子键。"""
        essential_paths = {
            "API URL": ('api_settings', 'url'),
            "API Key": ('api_settings', 'key'),
            "Default Image Path": ('default_image', 'path')
        }
        for name, path_tuple in essential_paths.items():
            current_level = self._config
            try:
                for key in path_tuple:
                    current_level = current_level[key]
            except KeyError:
                print(f"错误: 配置文件中缺少必须的配置项 '{'.'.join(path_tuple)}' ({name})。请检查配置文件。")
                sys.exit(1)
            except TypeError: # 如果中间路径不是字典
                 print(f"错误: 配置文件结构不正确，期望 '{'.'.join(path_tuple[:-1])}' 是一个字典，但找到了其他类型。")
                 sys.exit(1)


    @property
    def api_url(self):
        return self._config['api_settings']['url']

    @property
    def api_key(self):
        return self._config['api_settings']['key']

    @property
    def api_key_header_name(self):
        return self._config.get('api_settings', {}).get('api_key_header_name', 'ailabapi-api-key')

    @property
    def request_timeout_seconds(self):
        return self._config.get('api_settings', {}).get('request_timeout_seconds', 30)

    @property
    def default_image_path(self):
        """
        获取默认图片的绝对路径。
        它会解析配置文件中可能是相对路径的 'default_image.path'。
        相对路径是相对于 config.yaml 文件所在的目录。
        """
        raw_path_from_config = self._config['default_image']['path']
        if os.path.isabs(raw_path_from_config):
            # 如果配置中已经是绝对路径，直接使用
            return os.path.normpath(raw_path_from_config)
        else:
            # 如果是相对路径，则相对于配置文件所在目录进行解析
            # self._config_dir was set in __init__
            absolute_path = os.path.join(self._config_dir, raw_path_from_config)
            return os.path.normpath(absolute_path)

    # 文件上传细节
    @property
    def file_form_field_name(self):
        return self._config.get('file_upload_details', {}).get('form_field_name', 'image')

    @property
    def file_sent_filename_placeholder(self):
        return self._config.get('file_upload_details', {}).get('sent_filename_placeholder', 'file')

    @property
    def file_content_type(self):
        return self._config.get('file_upload_details', {}).get('content_type', 'application/octet-stream')

    # 通用设置
    @property
    def default_encoding(self):
        return self._config.get('general_settings', {}).get('default_encoding', 'utf-8')

    @property
    def json_indent(self):
        return self._config.get('general_settings', {}).get('json_indent', 4)

    @property
    def json_ensure_ascii(self):
        return self._config.get('general_settings', {}).get('json_ensure_ascii', False)


def get_app_config(config_path=None):
    """
    加载并返回一个AppConfig实例。
    这是外部模块应该使用的主要函数来获取配置。
    """
    raw_dict = load_raw_config_dict(config_path)
    return AppConfig(raw_dict)


# 测试块
if __name__ == '__main__':
    print("测试 config_loader.py...")
    app_configuration = get_app_config() 

    if app_configuration:
        print("\n--- AppConfig 测试访问 ---")
        print(f"API URL: {app_configuration.api_url}")
        print(f"API Key: {app_configuration.api_key}")
        print(f"API Key Header: {app_configuration.api_key_header_name}")
        print(f"Timeout: {app_configuration.request_timeout_seconds}")
        print(f"Default Image: {app_configuration.default_image_path}")
        print(f"Form Field: {app_configuration.file_form_field_name}")
        print(f"Sent Filename: {app_configuration.file_sent_filename_placeholder}")
        print(f"Content Type: {app_configuration.file_content_type}")
        print(f"Default Encoding: {app_configuration.default_encoding}")
        print(f"JSON Indent: {app_configuration.json_indent}")
        print(f"JSON Ensure ASCII: {app_configuration.json_ensure_ascii}")
        print("--- 测试结束 ---")