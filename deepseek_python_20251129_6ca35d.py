"""
Módulo de Análise - Processamento e análise de dados
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

class DataAnalyzer:
    """Analisador de dados para processamento inteligente"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.history = []
        self.patterns = self.load_patterns()
        
    def load_patterns(self) -> Dict[str, Any]:
        """Carrega padrões de reconhecimento"""
        return {
            'numeros': r'\b\d+\b',
            'porcentagens': r'\b\d+%\b',
            'moedas': r'R\$\s?\d+[,.]?\d*',
            'datas': r'\d{1,2}/\d{1,2}/\d{4}',
            'horarios': r'\d{1,2}:\d{2}',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'urls': r'https?://[^\s]+'
        }
    
    def analyze_text(self, text: str, source: str = 'ocr') -> Dict[str, Any]:
        """Analisa texto extraído e retorna insights"""
        try:
            analysis_start = datetime.now()
            
            # Análise básica
            basic_stats = self.get_basic_stats(text)
            
            # Detecção de padrões
            patterns_found = self.detect_patterns(text)
            
            # Análise semântica
            semantic_analysis = self.semantic_analysis(text)
            
            # Score de confiança
            confidence_score = self.calculate_confidence_score(
                basic_stats, patterns_found, semantic_analysis
            )
            
            analysis_time = (datetime.now() - analysis_start).total_seconds()
            
            result = {
                'timestamp': analysis_start.isoformat(),
                'basic_stats': basic_stats,
                'patterns_found': patterns_found,
                'semantic_analysis': semantic_analysis,
                'confidence_score': confidence_score,
                'analysis_time': analysis_time,
                'source': source
            }
            
            # Adicionar ao histórico
            self.history.append(result)
            
            self.logger.info(f"Análise concluída em {analysis_time:.2f}s - Confiança: {confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na análise: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'confidence_score': 0.0
            }
    
    def get_basic_stats(self, text: str) -> Dict[str, Any]:
        """Calcula estatísticas básicas do texto"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        lines = text.split('\n')
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'line_count': len([l for l in lines if l.strip()]),
            'avg_word_length': statistics.mean([len(word) for word in words]) if words else 0,
            'avg_sentence_length': statistics.mean([len(sent.split()) for sent in sentences if sent.strip()]) if sentences else 0,
            'unique_words': len(set(words)),
            'text_density': len(text) / max(1, len(words))
        }
    
    def detect_patterns(self, text: str) -> Dict[str, List[str]]:
        """Detecta padrões específicos no texto"""
        patterns_found = {}
        
        for pattern_name, pattern in self.patterns.items():
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    patterns_found[pattern_name] = matches
            except Exception as e:
                self.logger.warning(f"Erro no padrão {pattern_name}: {e}")
        
        return patterns_found
    
    def semantic_analysis(self, text: str) -> Dict[str, Any]:
        """Análise semântica básica do conteúdo"""
        # Palavras-chave comuns em contextos específicos
        keywords = {
            'financeiro': ['valor', 'preço', 'custo', 'investimento', 'lucro', 'prejuízo', 'orçamento'],
            'temporal': ['hora', 'tempo', 'data', 'prazo', 'deadline', 'vencimento'],
            'urgente': ['urgente', 'importante', 'crítico', 'prioridade', 'imediatamente'],
            'quantitativo': ['total', 'soma', 'média', 'máximo', 'mínimo', 'percentual']
        }
        
        semantic_results = {}
        text_lower = text.lower()
        
        for category, words in keywords.items():
            found_words = [word for word in words if word in text_lower]
            if found_words:
                semantic_results[category] = {
                    'keywords_found': found_words,
                    'count': len(found_words),
                    'intensity': len(found_words) / len(words)
                }
        
        # Detectar tom do texto
        tone_indicators = {
            'positivo': ['sucesso', 'excelente', 'ótimo', 'bom', 'parabéns'],
            'negativo': ['problema', 'erro', 'falha', 'atraso', 'cancelado'],
            'neutro': ['informamos', 'comunicado', 'aviso', 'notificação']
        }
        
        tone_scores = {}
        for tone, indicators in tone_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            tone_scores[tone] = score
        
        semantic_results['tone_analysis'] = tone_scores
        semantic_results['dominant_tone'] = max(tone_scores.items(), key=lambda x: x[1])[0] if tone_scores else 'neutro'
        
        return semantic_results
    
    def calculate_confidence_score(self, stats: Dict, patterns: Dict, semantic: Dict) -> float:
        """Calcula score de confiança baseado na análise"""
        score = 0.0
        
        # Baseado em estatísticas
        if stats['word_count'] > 5:
            score += 0.3
        
        # Baseado em padrões encontrados
        if patterns:
            score += 0.3
        
        # Baseado em análise semântica
        if semantic.get('keywords_found'):
            score += 0.2
        
        # Baseado em diversidade de palavras
        if stats.get('unique_words', 0) > 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def get_historical_data(self, limit: int = 50) -> List[Dict]:
        """Retorna dados históricos de análise"""
        return self.history[-limit:] if self.history else []
    
    def export_analysis(self, analysis_data: Dict, format_type: str = 'json') -> str:
        """Exporta análise em formato específico"""
        try:
            if format_type == 'json':
                return json.dumps(analysis_data, indent=2, ensure_ascii=False)
            elif format_type == 'text':
                return self.format_text_report(analysis_data)
            else:
                raise ValueError(f"Formato não suportado: {format_type}")
        except Exception as e:
            self.logger.error(f"Erro ao exportar análise: {e}")
            return f"Erro na exportação: {e}"
    
    def format_text_report(self, analysis: Dict) -> str:
        """Formata relatório em texto"""
        report = []
        report.append("=" * 50)
        report.append("RELATÓRIO DE ANÁLISE - VT BacBo")
        report.append("=" * 50)
        
        # Estatísticas básicas
        stats = analysis.get('basic_stats', {})
        report.append(f"\n📊 ESTATÍSTICAS:")
        report.append(f"   Caracteres: {stats.get('character_count', 0)}")
        report.append(f"   Palavras: {stats.get('word_count', 0)}")
        report.append(f"   Linhas: {stats.get('line_count', 0)}")
        report.append(f"   Palavras únicas: {stats.get('unique_words', 0)}")
        
        # Padrões encontrados
        patterns = analysis.get('patterns_found', {})
        if patterns:
            report.append(f"\n🎯 PADRÕES ENCONTRADOS:")
            for pattern_type, matches in patterns.items():
                report.append(f"   {pattern_type}: {len(matches)} ocorrências")
        
        # Análise semântica
        semantic = analysis.get('semantic_analysis', {})
        if semantic:
            report.append(f"\n🧠 ANÁLISE SEMÂNTICA:")
            report.append(f"   Tom predominante: {semantic.get('dominant_tone', 'N/A')}")
        
        # Confiança
        report.append(f"\n⭐ SCORE DE CONFIANÇA: {analysis.get('confidence_score', 0):.2%}")
        report.append(f"⏱️  Tempo de análise: {analysis.get('analysis_time', 0):.2f}s")
        
        return '\n'.join(report)