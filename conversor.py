from PIL import Image
import os

def converter_para_ico():
    # Nome do seu arquivo PNG (ajuste se necessário)
    png_original = "ChatGPT Image 29_11_2025, 17_24_16.png"
    ico_output = "logo.ico"
    
    if not os.path.exists(png_original):
        print(f"ERRO: Arquivo {png_original} não encontrado!")
        print("Certifique-se de que está na mesma pasta")
        return
    
    try:
        img = Image.open(png_original)
        # Converte para ICO com tamanhos múltiplos
        img.save(ico_output, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
        print(f"✓ Sucesso! logo.ico criado na pasta atual")
        print(f"✓ Tamanho da imagem original: {img.size}")
    except Exception as e:
        print(f"Erro na conversão: {e}")

if __name__ == "__main__":
    converter_para_ico()
