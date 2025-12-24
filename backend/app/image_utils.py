from PIL import Image, ImageOps, ImageDraw
import os

def create_token(image_path, output_path, border_color="gold", border_width=10):
    """
    Cria um token circular a partir de uma imagem.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # Criar máscara circular
        size = (min(img.size), min(img.size))
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # Recortar imagem
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        
        # Adicionar borda (opcional, simples)
        # Para uma borda real, desenhamos um círculo vazio sobre a imagem
        draw_border = ImageDraw.Draw(output)
        draw_border.ellipse((0, 0) + size, outline=border_color, width=border_width)
        
        output.save(output_path)
        return output_path
    except Exception as e:
        print(f"Erro ao criar token: {e}")
        return None
