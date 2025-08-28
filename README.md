# Simulação de Rede IoT Heterogênea para Análise de Desempenho

## 🎯 Sobre o Projeto

Este projeto, desenvolvido para a disciplina de Avaliação de Desempenho em Redes de Computadores do Instituto Federal da Paraíba, tem como objetivo modelar, emular e avaliar o desempenho de uma rede IoT heterogênea em um cenário de Smart City.

O ambiente é orquestrado com **Docker Compose** e emula três perfis de dispositivos IoT (Low, Medium e High-Tier), cada um com limites de recursos de hardware distintos e simulando aplicações baseadas em datasets públicos. A comunicação entre os dispositivos e os serviços na nuvem é estabelecida através de uma rede emulada com **Mininet**, que atua como gateway/roteador, permitindo a manipulação de características de rede como latência e perda de pacotes.

A plataforma conta com um stack de monitoramento completo com **Prometheus**, **Node Exporter** e **Blackbox Exporter**, permitindo a análise de desempenho em tempo real através de um dashboard customizado no **Grafana**.

## 🛠️ Tecnologias Utilizadas

* **Orquestração:** Docker & Docker Compose
* **Emulação de Rede:** Mininet
* **Simulação dos Dispositivos:** Python 3.9
* **Comunicação:** MQTT (Broker Mosquitto)
* **Biblioteca MQTT:** Paho-MQTT para Python
* **Monitoramento e Coleta de Métricas:**
    * **Prometheus:** Coleta e armazenamento de métricas de séries temporais.
    * **Node Exporter:** Coleta de métricas de recursos do host (CPU, memória) de cada dispositivo IoT.
    * **Blackbox Exporter:** Monitoramento de latência, jitter e perda de pacotes na rede via ICMP.
* **Visualização e Análise:** Grafana
* **Testes de Rede ( degradação de link):** NetEm (integrado ao Mininet)

## 📂 Estrutura do Repositório

<img width="334" height="446" alt="image" src="https://github.com/user-attachments/assets/c8c3f5c7-10c5-4f0e-84be-441c8b9e92df" />


## 🚀 Aplicações e Dispositivos Simulados

Modelamos três aplicações distintas, cada uma emulando um dispositivo IoT com especificações de hardware diferentes, que são refletidas nos limites de recursos (`cpus`, `mem_limit`) de cada contêiner no `docker-compose.yml`.

### Tier Alto (High-Tier)

* **Aplicação Simulada:** Estação de Monitoramento da Qualidade da Água.
* **Perfil no Código:** `agua_station`
* **Dispositivo Real Emulado:** **Raspberry Pi 4 Model B (2GB)**.
    * **Recursos Alocados:** CPU: 1.0 core / RAM: 2048MB.
    * **Modelo de Comportamento:** Frequência de envio alta (a cada 60 segundos) e uma carga de trabalho de CPU constante para simular processamento contínuo de dados complexos.

### Tier Médio (Medium-Tier)

* **Aplicação Simulada:** Estação de Monitoramento de Poluição do Ar.
* **Perfil no Código:** `poluicao_station`
* **Dispositivo Real Emulado:** **Raspberry Pi Zero 2 W**.
    * **Recursos Alocados:** CPU: 0.4 core / RAM: 512MB.
    * **Modelo de Comportamento:** Frequência de envio moderada (a cada 5 minutos) e uma carga de trabalho de CPU intermitente, simulando um dispositivo que realiza processamento esporádico.

### Tier Baixo (Low-Tier)

* **Aplicação Simulada:** Lixeira Inteligente com sensor de nível.
* **Perfil no Código:** `lixeira_inteligente`
* **Dispositivo Real Emulado:** **Heltec WiFi LoRa 32 (ESP32)**.
    * **Recursos Alocados:** CPU: 0.1 core / RAM: 64MB.
    * **Modelo de Comportamento:** Frequência de envio baixa (a cada 10 minutos) e sem carga de trabalho de CPU extra, simulando um dispositivo de baixo consumo que passa a maior parte do tempo inativo para economizar energia.

## 📊 Fontes de Dados (Datasets de Referência)

* **Estação Ambiental (High-Tier):** [OpenSenseMap - Goethe-Institut São Paulo v2](https://opensensemap.org/explore/630539a1d7e0a3001bd65ac8)
* **Estação de Poluição (Medium-Tier):** [CityPulse Smart City Datasets (seção "Pollution")](http://iot.ee.surrey.ac.uk:8080/datasets.html#pollution)
* **Qualidade da Água (Low-Tier):** [NYC Open Data - Harbor Water Quality](https://data.cityofnewyork.us/Environment/Harbor-Water-Quality/5uug-f49n/data_preview)

## ⚙️ Como Executar

1.  **Pré-requisitos:**
    * Docker e Docker Compose.
    * Mininet (`sudo apt-get install mininet`).

2.  **Configuração e Inicialização:**
    * Clone este repositório.
    * Abra um terminal na pasta raiz do projeto.
    * Execute o script de setup para limpar o ambiente, criar as redes e iniciar todos os contêineres de serviço e dispositivos.
        ```bash
        sudo bash setup_mininet_env.sh
        ```
    * Após a execução do script, inicie a topologia de rede com o Mininet para estabelecer a conexão entre os dispositivos e a nuvem.
        ```bash
        sudo python3 mininet_topology.py
        ```
    * Isso abrirá o console do Mininet (`mininet>`). A simulação está ativa e os dispositivos já estão se comunicando. Mantenha este terminal aberto.

3.  **Acessando os Serviços:**
    * **Dashboard Grafana:** [http://localhost:3000](http://localhost:3000) (login: `admin` / senha: `admin`)
    * **Prometheus:** [http://localhost:9090](http://localhost:9090)

4.  **Importando o Dashboard:**
    * No Grafana, vá em **Dashboards -> New -> Import**.
    * Faça o upload do arquivo `grafana-data/dashboard.json` ou cole seu conteúdo.
    * Selecione sua fonte de dados Prometheus e finalize a importação.
    * OBS: é necessário trocar o UUID dentro do datasoruce do .json para funcionar.

## 🧪 Como Realizar Testes

Os testes de degradação de rede são realizados diretamente no console do Mininet, utilizando o **NetEm**. Os comandos `tc` (traffic control) são aplicados na interface do roteador (`r1-eth1`) que conecta toda a rede dos dispositivos IoT.

1.  **Execute os Comandos de Teste:** No terminal onde o `mininet_topology.py` está rodando (`mininet>`), execute um dos comandos abaixo.

    * **Exemplo 1: Aplicar 200ms de latência para todos os dispositivos IoT**
        ```
        mininet> r1 tc qdisc add dev r1-eth1 root netem delay 200ms
        ```

    * **Exemplo 2: Aplicar 15% de perda de pacotes**
        ```
        mininet> r1 tc qdisc add dev r1-eth1 root netem loss 15%
        ```

    * **Exemplo 3: Aplicar latência com variação (jitter)**
        ```
        mininet> r1 tc qdisc add dev r1-eth1 root netem delay 100ms 20ms
        ```

    * **Para remover todas as regras e voltar ao normal:**
        ```
        mininet> r1 tc qdisc del dev r1-eth1 root
        ```
