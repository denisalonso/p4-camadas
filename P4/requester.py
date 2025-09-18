from datetime import datetime

    
def escreve(arquivo,emissor,len_pacote,num_pacote,total_pacotes,crc):
    # Cria ou abre o arquivo em modo de anexação
    horario = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    mensagem = f"{horario} / {emissor}/ {len_pacote} / {num_pacote} / {total_pacotes} / {crc}\n"
    with open(arquivo, 'a') as f:
        # Escreve a mensagem e a hora no arquivo
        f.write(mensagem)

    return mensagem
# Exemplo de uso
