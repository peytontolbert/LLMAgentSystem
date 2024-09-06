import importlib
import os
from typing import Dict, Any, Callable
from app.logging.logging_manager import LoggingManager

class Plugin:
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.hooks: Dict[str, Callable] = {}

    def register_hook(self, hook_name: str, hook_function: Callable):
        self.hooks[hook_name] = hook_function

class PluginManager:
    def __init__(self, logging_manager: LoggingManager):
        self.logging_manager = logging_manager
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, Dict[str, Callable]] = {}

    def load_plugins(self, plugins_dir: str):
        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_name = filename[:-3]
                try:
                    module = importlib.import_module(f"app.plugins.{plugin_name}")
                    if hasattr(module, 'setup_plugin'):
                        plugin = module.setup_plugin()
                        self.register_plugin(plugin)
                        self.logging_manager.log_info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                except Exception as e:
                    self.logging_manager.log_error(f"Error loading plugin {plugin_name}: {str(e)}")

    def register_plugin(self, plugin: Plugin):
        self.plugins[plugin.name] = plugin
        for hook_name, hook_function in plugin.hooks.items():
            if hook_name not in self.hooks:
                self.hooks[hook_name] = {}
            self.hooks[hook_name][plugin.name] = hook_function

    def unregister_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            for hook_name in plugin.hooks:
                if hook_name in self.hooks and plugin_name in self.hooks[hook_name]:
                    del self.hooks[hook_name][plugin_name]
            del self.plugins[plugin_name]
            self.logging_manager.log_info(f"Unregistered plugin: {plugin_name}")

    async def execute_hook(self, hook_name: str, *args, **kwargs) -> Dict[str, Any]:
        results = {}
        if hook_name in self.hooks:
            for plugin_name, hook_function in self.hooks[hook_name].items():
                try:
                    results[plugin_name] = await hook_function(*args, **kwargs)
                except Exception as e:
                    self.logging_manager.log_error(f"Error executing hook {hook_name} for plugin {plugin_name}: {str(e)}")
        return results

# Example plugin implementation
def setup_plugin() -> Plugin:
    plugin = Plugin("ExamplePlugin", "1.0", "An example plugin")

    async def before_task_execution(task: Dict[str, Any]) -> Dict[str, Any]:
        # Modify the task or perform some action before task execution
        task["modified_by_plugin"] = True
        return {"status": "success", "message": "Task modified by ExamplePlugin"}

    plugin.register_hook("before_task_execution", before_task_execution)
    return plugin