#!/usr/bin/env python3
"""
VT BacBo - Main Application Entry Point
Analisador inteligente com OCR e interface moderna
"""

import sys
import logging
from pathlib import Path
import tkinter as tk

# Add src to path
src_path = Path(__file__).parent
sys.path.append(str(src_path))

from gui import MainApplication
from config import AppConfig
from ocr_engine import OCREngine
from analyzer import DataAnalyzer

class VTBacBoApp:
    """Classe principal da aplicação VT BacBo"""
    
    def __init__(self):
        self.config = AppConfig()
        self.setup_logging()
        self.ocr_engine = OCREngine()
        self.analyzer = DataAnalyzer()
        
    def setup_logging(self):
        """Configura sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('vt_bacbo.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run(self):
        """Inicia a aplicação"""
        try:
            self.logger.info("Iniciando VT BacBo...")
            
            # Inicializar interface gráfica
            root = tk.Tk()
            app = MainApplication(root, self.ocr_engine, self.analyzer)
            
            # Configurar janela principal
            root.title("VT BacBo - Analisador Inteligente")
            root.geometry("1200x800")
            root.minsize(1000, 700)
            
            # Centralizar janela
            root.eval('tk::PlaceWindow . center')
            
            self.logger.info("Interface inicializada com sucesso")
            
            # Iniciar loop principal
            root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar aplicação: {e}")
            sys.exit(1)

if __name__ == "__main__":
    app = VTBacBoApp()
    app.run()