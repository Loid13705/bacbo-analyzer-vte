"""
Interface Gráfica - GUI moderna e profissional
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from typing import Optional, Callable
import threading
from datetime import datetime
import json

class ModernTheme:
    """Configurações de tema moderno"""
    
    COLORS = {
        'primary': '#2C3E50',
        'secondary': '#34495E',
        'accent': '#3498DB',
        'success': '#27AE60',
        'warning': '#F39C12',
        'danger': '#E74C3C',
        'light': '#ECF0F1',
        'dark': '#2C3E50',
        'text_light': '#FFFFFF',
        'text_dark': '#2C3E50'
    }
    
    FONTS = {
        'title': ('Segoe UI', 16, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'normal': ('Segoe UI', 10),
        'small': ('Segoe UI', 9)
    }

class MainApplication(tk.Frame):
    """Aplicação principal com interface moderna"""
    
    def __init__(self, parent, ocr_engine, analyzer):
        super().__init__(parent)
        self.parent = parent
        self.ocr_engine = ocr_engine
        self.analyzer = analyzer
        self.theme = ModernTheme()
        self.is_capturing = False
        self.capture_thread = None
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        """Configura interface do usuário"""
        self.parent.configure(bg=self.theme.COLORS['primary'])
        self.setup_styles()
        self.create_header()
        self.create_main_area()
        self.create_status_bar()
        
    def setup_styles(self):
        """Configura estilos personalizados"""
        style = ttk.Style()
        
        # Configurar tema
        style.theme_use('clam')
        
        # Configurar estilos personalizados
        style.configure('Primary.TButton',
                       background=self.theme.COLORS['accent'],
                       foreground=self.theme.COLORS['text_light'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Secondary.TButton',
                       background=self.theme.COLORS['secondary'],
                       foreground=self.theme.COLORS['text_light'],
                       borderwidth=0)
        
        style.configure('Success.TButton',
                       background=self.theme.COLORS['success'],
                       foreground=self.theme.COLORS['text_light'])
        
        style.configure('Danger.TButton',
                       background=self.theme.COLORS['danger'],
                       foreground=self.theme.COLORS['text_light'])
        
        style.configure('Primary.TFrame',
                       background=self.theme.COLORS['primary'])
        
        style.configure('Secondary.TFrame',
                       background=self.theme.COLORS['secondary'])
        
        style.configure('Light.TFrame',
                       background=self.theme.COLORS['light'])
        
    def create_header(self):
        """Cria cabeçalho da aplicação"""
        header_frame = ttk.Frame(self.parent, style='Primary.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Logo e título
        title_frame = ttk.Frame(header_frame, style='Primary.TFrame')
        title_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            title_frame,
            text="🎮 VT BacBo - Analisador Inteligente",
            font=self.theme.FONTS['title'],
            fg=self.theme.COLORS['text_light'],
            bg=self.theme.COLORS['primary']
        )
        title_label.pack(pady=5)
        
        subtitle_label = tk.Label(
            title_frame,
            text="OCR Avançado + Análise em Tempo Real",
            font=self.theme.FONTS['small'],
            fg=self.theme.COLORS['text_light'],
            bg=self.theme.COLORS['primary']
        )
        subtitle_label.pack()
        
        # Botões de controle
        control_frame = ttk.Frame(header_frame, style='Primary.TFrame')
        control_frame.pack(side=tk.RIGHT)
        
        self.capture_btn = ttk.Button(
            control_frame,
            text="🎯 Iniciar Captura",
            style='Success.TButton',
            command=self.toggle_capture
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        settings_btn = ttk.Button(
            control_frame,
            text="⚙️ Configurações",
            style='Secondary.TButton',
            command=self.show_settings
        )
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(
            control_frame,
            text="📊 Exportar Dados",
            style='Primary.TButton',
            command=self.export_data
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
    def create_main_area(self):
        """Cria área principal da aplicação"""
        main_container = ttk.Frame(self.parent, style='Light.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Divisão em painéis
        paned_window = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Painel esquerdo - Captura e visualização
        left_frame = ttk.Frame(paned_window, style='Light.TFrame')
        paned_window.add(left_frame, weight=1)
        
        self.create_capture_panel(left_frame)
        
        # Painel direito - Análise e resultados
        right_frame = ttk.Frame(paned_window, style='Light.TFrame')
        paned_window.add(right_frame, weight=1)
        
        self.create_analysis_panel(right_frame)
        
    def create_capture_panel(self, parent):
        """Cria painel de captura e visualização"""
        # Frame de captura
        capture_frame = ttk.LabelFrame(parent, text="🎥 Captura de Tela", style='Light.TFrame')
        capture_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de visualização
        self.preview_label = tk.Label(
            capture_frame,
            text="Área de visualização\n\nClique em 'Iniciar Captura' para começar",
            bg='white',
            relief=tk.SUNKEN,
            font=self.theme.FONTS['normal'],
            justify=tk.CENTER
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controles de captura
        control_frame = ttk.Frame(capture_frame, style='Light.TFrame')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="Região:").pack(side=tk.LEFT)
        
        self.region_var = tk.StringVar(value="0,0,800,600")
        region_entry = ttk.Entry(control_frame, textvariable=self.region_var, width=20)
        region_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Selecionar Região",
            command=self.select_region
        ).pack(side=tk.LEFT, padx=5)
        
    def create_analysis_panel(self, parent):
        """Cria painel de análise e resultados"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de texto extraído
        text_frame = ttk.Frame(notebook)
        notebook.add(text_frame, text="📝 Texto Extraído")
        
        self.text_display = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#F8F9FA',
            fg=self.theme.COLORS['dark']
        )
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de análise
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="📊 Análise")
        
        self.analysis_display = scrolledtext.ScrolledText(
            analysis_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#F8F9FA'
        )
        self.analysis_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de histórico
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="📈 Histórico")
        
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=('timestamp', 'confidence', 'words'),
            show='headings'
        )
        self.history_tree.heading('timestamp', text='Data/Hora')
        self.history_tree.heading('confidence', text='Confiança')
        self.history_tree.heading('words', text='Palavras')
        
        self.history_tree.column('timestamp', width=150)
        self.history_tree.column('confidence', width=80)
        self.history_tree.column('words', width=80)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_status_bar(self):
        """Cria barra de status"""
        self.status_var = tk.StringVar(value="Pronto para iniciar")
        
        status_bar = ttk.Frame(self.parent, style='Secondary.TFrame', height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        status_label = tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=self.theme.FONTS['small'],
            fg=self.theme.COLORS['text_light'],
            bg=self.theme.COLORS['secondary']
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            status_bar,
            variable=self.progress_var,
            mode='determinate'
        )
        progress_bar.pack(side=tk.RIGHT, padx=10, pady=2, fill=tk.Y)
        
    def setup_bindings(self):
        """Configura atalhos de teclado"""
        self.parent.bind('<F1>', lambda e: self.show_help())
        self.parent.bind('<Control-q>', lambda e: self.parent.quit())
        self.parent.bind('<F5>', lambda e: self.toggle_capture())
        
    def toggle_capture(self):
        """Alterna entre iniciar/parar captura"""
        if not self.is_capturing:
            self.start_capture()
        else:
            self.stop_capture()
    
    def start_capture(self):
        """Inicia captura contínua"""
        self.is_capturing = True
        self.capture_btn.configure(text="⏹️ Parar Captura", style='Danger.TButton')
        self.status_var.set("Capturando...")
        
        # Iniciar thread de captura
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
    
    def stop_capture(self):
        """Para captura contínua"""
        self.is_capturing = False
        self.capture_btn.configure(text="🎯 Iniciar Captura", style='Success.TButton')
        self.status_var.set("Captura interrompida")
    
    def capture_loop(self):
        """Loop principal de captura"""
        while self.is_capturing:
            try:
                # Capturar região da tela
                region = self.parse_region(self.region_var.get())
                screenshot = self.ocr_engine.capture_screen_region(region)
                
                if screenshot is not None:
                    # Atualizar preview na thread principal
                    self.parent.after(0, self.update_preview, screenshot)
                    
                    # Processar OCR
                    ocr_result = self.ocr_engine.extract_text(screenshot)
                    
                    # Analisar texto
                    if ocr_result['text']:
                        analysis_result = self.analyzer.analyze_text(ocr_result['text'])
                        
                        # Atualizar interface
                        self.parent.after(0, self.update_results, ocr_result, analysis_result)
                
                # Intervalo entre capturas
                threading.Event().wait(2)  # 2 segundos
                
            except Exception as e:
                logging.error(f"Erro no loop de captura: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Erro", f"Erro na captura: {e}"))
                break
    
    def parse_region(self, region_str: str) -> tuple:
        """Converte string de região para tupla"""
        try:
            coords = [int(x.strip()) for x in region_str.split(',')]
            if len(coords) == 4:
                return tuple(coords)
        except:
            pass
        return (0, 0, 800, 600)  # Default
    
    def update_preview(self, screenshot):
        """Atualiza preview da captura (simplificado)"""
        # Em uma implementação real, converteríamos a imagem para PhotoImage
        self.preview_label.configure(
            text=f"Captura realizada: {screenshot.shape[1]}x{screenshot.shape[0]}\n"
                 f"Clique para visualizar imagem"
        )
    
    def update_results(self, ocr_result, analysis_result):
        """Atualiza resultados na interface"""
        # Texto extraído
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, ocr_result['text'])
        
        # Análise
        analysis_text = self.analyzer.format_text_report(analysis_result)
        self.analysis_display.delete(1.0, tk.END)
        self.analysis_display.insert(1.0, analysis_text)
        
        # Histórico
        self.update_history(analysis_result)
        
        # Status
        confidence = analysis_result.get('confidence_score', 0)
        self.status_var.set(f"Análise concluída - Confiança: {confidence:.2%}")
        self.progress_var.set(confidence * 100)
    
    def update_history(self, analysis_result):
        """Atualiza histórico de análises"""
        timestamp = analysis_result.get('timestamp', '')
        confidence = analysis_result.get('confidence_score', 0)
        word_count = analysis_result.get('basic_stats', {}).get('word_count', 0)
        
        # Formatar timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%H:%M:%S')
        except:
            formatted_time = timestamp
        
        self.history_tree.insert('', 0, values=(
            formatted_time,
            f"{confidence:.2%}",
            word_count
        ))
        
        # Limitar histórico a 50 itens
        if len(self.history_tree.get_children()) > 50:
            self.history_tree.delete(self.history_tree.get_children()[-1])
    
    def select_region(self):
        """Abre seletor de região da tela"""
        messagebox.showinfo("Selecionar Região", 
                          "Feature em desenvolvimento.\n"
                          "Por enquanto, digite as coordenadas manualmente no formato: x1,y1,x2,y2")
    
    def show_settings(self):
        """Mostra diálogo de configurações"""
        settings_window = tk.Toplevel(self.parent)
        settings_window.title("Configurações - VT BacBo")
        settings_window.geometry("400x300")
        settings_window.transient(self.parent)
        settings_window.grab_set()
        
        # Aqui seriam adicionados os controles de configuração
        ttk.Label(settings_window, text="Configurações em desenvolvimento...").pack(pady=20)
        ttk.Button(settings_window, text="Fechar", 
                  command=settings_window.destroy).pack(pady=10)
    
    def export_data(self):
        """Exporta dados atuais"""
        try:
            # Obter dados atuais
            current_text = self.text_display.get(1.0, tk.END).strip()
            if not current_text:
                messagebox.showwarning("Exportar", "Nenhum dado para exportar.")
                return
            
            # Criar dados para exportação
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'text': current_text,
                'analysis': self.analyzer.analyze_text(current_text)
            }
            
            # Salvar arquivo
            filename = f"vt_bacbo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Exportar", f"Dados exportados com sucesso!\nArquivo: {filename}")
            
        except Exception as e:
            messagebox.showerror("Exportar", f"Erro ao exportar dados: {e}")
    
    def show_help(self):
        """Mostra diálogo de ajuda"""
        help_text = """
VT BacBo - Ajuda Rápida

🎯 INICIAR CAPTURA:
- Clique em 'Iniciar Captura' ou pressione F5
- O sistema começará a capturar a região especificada

⚙️ CONFIGURAÇÕES:
- Defina a região de captura no formato: x1,y1,x2,y2
- Use 'Selecionar Região' para ajuda visual

📊 RESULTADOS:
- Veja o texto extraído na aba 'Texto Extraído'
- Análise detalhada na aba 'Análise'
- Histórico de capturas na aba 'Histórico'

📝 EXPORTAR:
- Use 'Exportar Dados' para salvar análise atual

Atalhos:
- F1: Mostrar esta ajuda
- F5: Iniciar/Parar captura
- Ctrl+Q: Sair do aplicativo
        """
        
        messagebox.showinfo("Ajuda - VT BacBo", help_text)