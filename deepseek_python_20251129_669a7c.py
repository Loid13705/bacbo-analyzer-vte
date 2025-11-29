"""
Configurações da aplicação
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

class AppConfig:
    """Gerencia configurações da aplicação"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.default_config = self.get_default_config()
        self.config = self.load_config()
        
    def get_default_config(self) -> Dict[str, Any]:
        """Retorna configurações padrão"""
        return {
            "app": {
                "name": "VT BacBo",
                "version": "1.0.0",
                "author": "VT Team",
                "auto_start": False,
                "minimize_to_tray": True
            },
            "ocr": {
                "language": "por",
                "confidence_threshold": 60,
                "preprocess_enabled": True,
                "auto_rotate": False
            },
            "capture": {
                "region": [0, 0, 800, 600],
                "interval": 2.0,
                "auto_save": True,
                "save_path": "captures"
            },
            "analysis": {
                "enable_semantic": True,
                "pattern_detection": True,
                "confidence_calculation": True,
                "max_history": 100
            },
            "ui": {
                "theme": "dark",
                "font_size": 10,
                "auto_scroll": True,
                "show_timestamps": True
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Mesclar com configurações padrão
                    return self.merge_configs(self.default_config, loaded_config)
            else:
                # Criar arquivo com configurações padrão
                self.save_config(self.default_config)
                return self.default_config.copy()
                
        except Exception as e:
            logging.error(f"Erro ao carregar configurações: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None):
        """Salva configurações no arquivo"""
        try:
            if config is None:
                config = self.config
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            logging.info("Configurações salvas com sucesso")
            
        except Exception as e:
            logging.error(f"Erro ao salvar configurações: {e}")
    
    def merge_configs(self, default: Dict, custom: Dict) -> Dict:
        """Mescla configurações padrão com personalizadas"""
        merged = default.copy()
        
        for key, value in custom.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self.merge_configs(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
                
        return merged
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Define valor de configuração"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def reset_to_defaults(self):
        """Restaura configurações padrão"""
        self.config = self.default_config.copy()
        self.save_config()