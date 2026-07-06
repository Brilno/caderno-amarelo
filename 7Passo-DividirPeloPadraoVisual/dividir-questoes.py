import os
from PIL import Image

def encontrar_faixa_dinamica(imagem, cor_alvo, tolerancia=15, altura_base=4, margem_erro=3):
    """
    Encontra posições onde há uma faixa vertical na coluna 0 da cor especificada,
    aceitando uma margem de erro na altura dessa faixa.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Altura mínima e máxima aceitáveis com base na margem de erro
    altura_minima = max(1, altura_base - margem_erro)
    altura_maxima = altura_base + margem_erro
    
    y = 0
    while y < altura:
        # Pega o pixel da coluna 0
        pixel = pixels[0, y]
        r, g, b = pixel[:3]
        
        # Verifica se o pixel atual coincide com a cor alvo
        if (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia):
            
            # Conta quantos pixels consecutivos da mesma cor existem para baixo
            altura_faixa_detectada = 0
            while (y + altura_faixa_detectada < altura):
                p_atual = pixels[0, y + altura_faixa_detectada]
                r_c, g_c, b_c = p_atual[:3]
                
                if (abs(r_c - cor_alvo[0]) <= tolerancia and 
                    abs(g_c - cor_alvo[1]) <= tolerancia and 
                    abs(b_c - cor_alvo[2]) <= tolerancia):
                    altura_faixa_detectada += 1
                else:
                    break
            
            # Verifica se a altura da faixa está dentro do intervalo aceitável (4 px +- 3)
            if altura_minima <= altura_faixa_detectada <= altura_maxima:
                # Corta 40 pixels ANTES de começar a faixa
                posicao_corte = y - 40
                if posicao_corte < 0:
                    posicao_corte = 0
                
                posicoes_corte.append((posicao_corte, y + altura_faixa_detectada))
                print(f"Faixa encontrada de altura {altura_faixa_detectada}px em y={y}. Ponto de corte: y={posicao_corte}")
                
                # Avança o ponteiro para depois da faixa encontrada
                y += altura_faixa_detectada
                continue
                
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando 40 pixels antes das faixas encontradas
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado.")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Busca os pontos de corte e fim das faixas
    dados_cortes = encontrar_faixa_dinamica(imagem, cor_alvo)
    
    if not dados_cortes:
        print("Nenhum padrão visual correspondente foi encontrado na coluna 0.")
        return
    
    print(f"Encontrados {len(dados_cortes)} padrões visuais para corte.")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (posicao_corte, fim_faixa) in enumerate(dados_cortes):
        # Evita cortes inválidos ou repetidos no mesmo ponto
        if posicao_corte <= posicao_anterior and i > 0:
            continue
            
        # Corta o bloco correspondente à questão anterior
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # O próximo bloco deve começar a contar a partir do ponto de corte atual
        posicao_anterior = posicao_corte
    
    # Corta a última seção restante (da última faixa até o final da folha)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(dados_cortes)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    # --- ATUALIZE ESTAS LINHAS CONFORME O SEU PASSO 7 ---
    caminho_imagem = "colunas_concatenadas_verticalmente.png" 
    pasta_saida = "questoes_divididas"
    
    # Definição direta do RGB alvo pedido: (35, 31, 32)
    cor_do_padrao = (35, 31, 32)
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Processo concluído! Verifique as imagens na pasta de saída.")