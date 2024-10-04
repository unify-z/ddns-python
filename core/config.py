import yaml
import os

class Config:
    def __init__(self):
        self.c = self.load_config()
        self.domain = self.c.get('domain')
        self.sub_domain = self.c.get('sub_domain','home')
        self.enable_ipv6 = self.c.get('enable_ipv6')
        self.dns = self.c.get('dns', {})

    def load_config(self):
        try:
            with open(f'{os.getcwd()}/config/config.yaml', 'r') as file:
                config_data = yaml.safe_load(file)
                return config_data
        except FileNotFoundError:
            print("配置文件未找到，请检查路径是否正确。")
            return {}
        except yaml.YAMLError as exc:
            print(f"YAML格式错误: {exc}")
            return {}
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

