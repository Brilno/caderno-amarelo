from PIL import Image
import os

def encontrar_faixa_padrao(imagem, cor_alvo=(35, 31, 32), tolerancia=15, altura_faixa=4, offset_corte=43):
    """
    Encontra posições onde há uma faixa da cor especificada no último pixel da direita.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y <= altura - altura_faixa:
        faixa_encontrada = True
        
        # Verifica se os 'altura_faixa' pixels consecutivos no último pixel (largura - 1) casam com a cor
        for dy in range(altura_faixa):
            pixel = pixels[largura - 1, y + dy]  # ÚLTIMO pixel da direita
            
            if len(pixel) >= 3:
                r, g, b = pixel[:3]
            else:
                r = g = b = pixel[0]
            
            # Verifica a tolerância da cor RGB (35, 31, 32)
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            # Corta 43 pixels antes do início do padrão
            posicao_corte = y - offset_corte
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado em y={y}. Ponto de corte definido em y={posicao_corte}")
            
            # Avança após o padrão para evitar re-detecção do mesmo bloco
            y += altura_faixa
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo=(35, 31, 32)):
    """
    Divide a imagem verticalmente com base nos pontos de corte identificados.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Busca posições considerando 4px de altura e corte 43px antes
    posicoes_corte = encontrar_faixa_padrao(imagem, cor_alvo=cor_alvo, altura_faixa=4, offset_corte=43)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte.")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Ignora cortes inválidos ou sobrepostos
        if posicao_corte <= posicao_anterior and i > 0:
            continue
            
        # Corta do ponto anterior até a posição de corte atual
        if posicao_corte > posicao_anterior:
            area_corte = (0, posicao_anterior, largura, posicao_corte)
            secao = imagem.crop(area_corte)
            
            nome_arquivo = f"parte_{i+1:03d}.png"
            caminho_completo = os.path.join(pasta_saida, nome_arquivo)
            secao.save(caminho_completo)
            print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte

    # Corta a seção final restante da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo final: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes-divididas"           # Substitua pelo nome da pasta de saída
    
    # Padrão RGB (35, 31, 32)
    cor_do_padrao = (35, 31, 32)
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Divisão concluída!")