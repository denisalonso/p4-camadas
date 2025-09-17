from datetime import datetime

def escreve(arquivo,emissor,len_pacote,num_pacote,total_pacotes,crc):
    horario = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    mensagem = f"{horario} / {emissor}/ {len_pacote} / {num_pacote} / {total_pacotes} / {crc}\n"
    with open(arquivo, 'a') as f:
        f.write(mensagem)

    return mensagem



    mensagem = escreve("requests_server.txt","recebimento",tamanho_pacote,entrada.package_number,entrada.size_all_packages,crc_bytes)
    print(mensagem)
    mensagem = escreve("requests_client.txt","envio",tamanho_pacote,num_pacote,all_pacotes,crc_bytes)
    print(mensagem)