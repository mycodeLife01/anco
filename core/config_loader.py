import yaml
from pathlib import Path
from addict import Dict
from functools import lru_cache
from typing import Any

# 定义配置文件的根目录
CONFIG_ROOT = Path(__file__).parent.parent / "configs"


# 使用lru_cache缓存文件读取操作，确保每个文件只被读取和解析一次
@lru_cache(maxsize=None)
def _load_single_yaml_file(filepath: Path) -> Dict:
    """加载单个YAML文件并返回addict.Dict对象。"""
    if not filepath.exists():
        raise FileNotFoundError(f"配置文件未找到: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Dict(data if data else {})  # 如果文件为空，返回空Dict
    except Exception as e:
        raise IOError(f"加载或解析YAML文件失败: {filepath}. 错误: {e}")


class ConfigLoader:
    """
    一个可以动态扫描并加载多个YAML文件的集中式配置加载器。
    """

    def __init__(self):
        # 动态加载prompts和descriptions目录下的所有yaml文件
        self._prompts = self._load_directory("prompts")
        self._descriptions = self._load_directory("descriptions")

    def _load_directory(self, subdir_name: str) -> Dict:
        """扫描指定子目录，加载所有YAML文件，并以文件名作为键。"""
        dir_path = CONFIG_ROOT / subdir_name
        if not dir_path.is_dir():
            # 如果目录不存在，可以返回空Dict或抛出异常，这里选择返回空Dict
            return Dict()

        all_configs = Dict()
        # 扫描所有.yaml和.yml文件
        for filepath in sorted(
            list(dir_path.glob("*.yaml")) + list(dir_path.glob("*.yml"))
        ):
            # 使用文件名（不含扩展名）作为key
            file_stem = filepath.stem
            all_configs[file_stem] = _load_single_yaml_file(filepath)

        return all_configs

    @property
    def prompts(self) -> Dict:
        """获取所有prompt模板，按文件名组织。"""
        return self._prompts

    @property
    def descriptions(self) -> Dict:
        """获取所有Pydantic字段的description，按文件名组织。"""
        return self._descriptions


# 全局唯一的加载器实例
config = ConfigLoader()


# --- 升级辅助函数get_desc以支持新结构 ---
def get_desc(key: str) -> str:
    """
    通过 'filename.ClassName.fieldName' 的键来获取description。
    例如: get_desc('user_model.User.username')
    """
    try:
        filename, class_name, field_name = key.split(".")
        return config.descriptions[filename][class_name][field_name]
    except (KeyError, ValueError, AttributeError):
        return f"ERROR: Description for '{key}' not found. Please check your key and YAML files."
