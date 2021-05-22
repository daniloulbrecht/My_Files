"""
Nome do arquivo : gera_html.py.
Autor : Danilo Nogueira Ulbrecht.
Ultima modificacao: 03/27/2020.
Versao do Python: 2.7 and 3.7.
Estilo revisado com flake8.

Descrição: Script criado para ler o diretorio do weathermap, identificar
os mapas criados e gerar um html consolidado com os links e miniaturas
para todos os mapas.
Quem manjar mais de HTML pode fazer um trabalho de formatacao muito melhor,
mas o trabalho "sujo" esta sendo feito por esse script.
Obs: Esse script deve ser copiado para o diretorio de instalacao do
Weathermap.
"""

from os import listdir  # Importa a funcao listdir.
from os import getcwd   # Importa a funcao getcwd.

directory = getcwd()  # Diretorio de mapas.

# Variavel do tipo lista, que ira receber o nome dos arquivos sem a extensao.
listademapas = []

# Funcao listdir, gera uma lista dos arquivos
# identificados no diretorio "directory".
# Para cada item (representado aqui pela variavel
# temporaria file) faca! ->

for file in listdir(directory):
    if file == "list.html":  # Ignore se o arquivo for list.html.
        continue

# Se o arquivo contiver no final so seu nome a string ".html" faca ->
    if file.endswith(".html"):
        # Quebra a string do arquivo .html em duas partes
        # (delimitado por ponto), mapa recebe apenas o nome e extensao recebe
        # o que vem depois do ponto (.html).
        mapa, extensao = file.split(".")
        # listamapas recebe variavel mapa na lista, roda o for de novo, recebe
        # mais um arquivo, roda de novo ...n vzs ate finalizar.
        listademapas.append(mapa)

# Abrimos o objeto arquivo list.html representado pela variavel pagina. Como
# abrimos em modo escrita, o arquivo original SEMPRE e apagado e reescrito.
pagina = open(directory+'/list.html', 'w')

# Abaixo escrevemos o cabecalho do arquivo.
pagina.write("""<!DOCTYPE html>
<html lang="pt-br">
  <head>
    <title>Lista de Mapas do Weathermap</title>
    <meta charset="utf-8">
	<style>
	.boxes{
	width:20%;
	float:left;
	}
	mainDiv{
		width:50%;
margin:auto;
	}
	img{
		max-width:100%;
	}
</style>
</head>
<body>
<div id="mainDiv">""")

pagina.close()  # Fechamos entao o arquivo.

# Abrimos novamente o arquivo, novamente representado pela variavel pagina,
# porem em modo append agora, que nao apaga o conteudo.
pagina = open(directory+'/list.html', 'a+')

# Direcionamos o ponteiro do arquivo para o final, assim o que escrevermos nas
# proximas instrucoes, serao escritos a partir da ultima linha
# e nao vai apagar o cabecalho.
pagina.seek(2)

# Para cada item(representado aqui por x) na lista listademapas,
# faca -> (escreve um bloco de codigo html para cada mapa.)
for x in listademapas:
    pagina.write("""    <div id="divOne" class="boxes">
	<a href="https://plataforma.weathermap.monitoracao.intranet/{}.html">
    <img src="{}.png" border="0" height="200" width="250" />
	<p>Mapa - {}</p>
	</a>
    </div>""".format(x, x, x))

# Aqui escrevemos o final do arquivo html.
pagina.write("""</body>
</html>""")

pagina.close()  # Fecha o arquivo.
