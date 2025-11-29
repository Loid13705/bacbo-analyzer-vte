"""
Módulo de OCR - Reconhecimento Óptico de Caracteres
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Optional, Dict, Any
import time

class OCREngine:
    """Motor de OCR para captura e processamento de texto"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tesseract_path = self.find_tesseract()
        self.setup_tesseract()
        
    def find_tesseract(self) -> str:
        """Localiza o executável do Tesseract"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Users\*\AppData\Local\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract'
        ]
        
        for path in possible_paths:
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                # Testa se funciona
                pytesseract.get_tesseract_version()
                self.logger.info(f"Tesseract encontrado em: {path}")
                return path
            except (pytesseract.TesseractNotFoundError, Exception):
                continue
                
        raise Exception("Tesseract não encontrado. Instale o Tesseract OCR.")
    
    def setup_tesseract(self):
        """Configura parâmetros do Tesseract"""
        self.custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzçãõâêîôûàèìòùáéíóúäëïöüÿñ'
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa a imagem para melhorar OCR"""
        try:
            # Converter para escala de cinza
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Aplicar filtro para reduzir ruído
            denoised = cv2.medianBlur(gray, 3)
            
            # Aplicar threshold adaptativo
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Operação morfológica para melhorar texto
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento: {e}")
            return image
    
    def extract_text(self, image: np.ndarray, lang: str = 'por') -> Dict[str, Any]:
        """Extrai texto da imagem usando OCR"""
        try:
            start_time = time.time()
            
            # Pré-processar imagem
            processed_image = self.preprocess_image(image)
            
            # Converter numpy array para PIL Image
            pil_image = Image.fromarray(processed_image)
            
            # Executar OCR
            text_data = pytesseract.image_to_data(
                pil_image, 
                lang=lang,
                config=self.custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Processar resultados
            extracted_text = self.process_ocr_results(text_data)
            
            processing_time = time.time() - start_time
            self.logger.info(f"OCR concluído em {processing_time:.2f}s")
            
            return {
                'text': extracted_text,
                'confidence': self.calculate_confidence(text_data),
                'processing_time': processing_time,
                'raw_data': text_data
            }
            
        except Exception as e:
            self.logger.error(f"Erro no OCR: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'processing_time': 0.0,
                'raw_data': {},
                'error': str(e)
            }
    
    def process_ocr_results(self, text_data: Dict) -> str:
        """Processa e organiza os resultados do OCR"""
        try:
            # Combinar texto detectado
            lines = {}
            for i in range(len(text_data['text'])):
                if int(text_data['conf'][i]) > 30:  # Confiança mínima
                    line_num = text_data['line_num'][i]
                    text = text_data['text'][i].strip()
                    
                    if text:
                        if line_num not in lines:
                            lines[line_num] = []
                        lines[line_num].append(text)
            
            # Ordenar por linha e juntar texto
            sorted_lines = sorted(lines.items())
            full_text = '\n'.join([' '.join(line_text) for _, line_text in sorted_lines])
            
            return full_text.strip()
            
        except Exception as e:
            self.logger.error(f"Erro ao processar resultados OCR: {e}")
            return ""
    
    def calculate_confidence(self, text_data: Dict) -> float:
        """Calcula confiança média do OCR"""
        try:
            confidences = [float(conf) for conf in text_data['conf'] if float(conf) > 0]
            return sum(confidences) / len(confidences) if confidences else 0.0
        except:
            return 0.0
    
    def capture_screen_region(self, region: tuple) -> Optional[np.ndarray]:
        """Captura região específica da tela"""
        try:
            import mss
            with mss.mss() as sct:
                monitor = {
                    "left": region[0],
                    "top": region[1],
                    "width": region[2] - region[0],
                    "height": region[3] - region[1]
                }
                screenshot = sct.grab(monitor)
                return np.array(screenshot)
        except Exception as e:
            self.logger.error(f"Erro na captura de tela: {e}")
            return None