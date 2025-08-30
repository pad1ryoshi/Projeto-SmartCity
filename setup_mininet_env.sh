#!/bin/bash

set -e

# --- ETAPA 1: LIMPEZA DEFINITIVA E ROBUSTA ---
echo "--- Limpando ambiente ---"
# Para o Mininet
mn -c > /dev/null 2>&1 || true

# Para e remove todos os contêineres do projeto pelo nome
echo "Parando e removendo contêineres antigos..."
docker stop iot-low-lixeira iot-medium-poluicao iot-high-agua mosquitto cadvisor prometheus blackbox-exporter grafana node-exporter > /dev/null 2>&1 || true
docker rm iot-low-lixeira iot-medium-poluicao iot-high-agua mosquitto cadvisor prometheus blackbox-exporter grafana node-exporter > /dev/null 2>&1 || true

# Remove as redes Docker
echo "Removendo redes Docker antigas..."
docker network rm devices_net services_net > /dev/null 2>&1 || true

# Remove as interfaces VETH
echo "Removendo interfaces VETH antigas..."
ip link del veth-devices > /dev/null 2>&1 || true
ip link del veth-services > /dev/null 2>&1 || true

# Uma pequena pausa para garantir que o sistema operacional processe as remoções
sleep 2
echo "Limpeza concluída."


# --- ETAPA 2: CRIAÇÃO DO AMBIENTE DE REDE ---
echo "--- Criando redes Docker ---"
DEVICES_NET_ID=$(docker network create --subnet=10.10.10.0/24 --gateway=10.10.10.1 devices_net)
SERVICES_NET_ID=$(docker network create --subnet=10.10.20.0/24 --gateway=10.10.20.1 services_net)
sleep 1

echo "--- Criando interfaces VETH para conectar com o Mininet ---"
ip link add veth-devices type veth peer name mn-veth1
ip link add veth-services type veth peer name mn-veth2
ip link set veth-devices up
ip link set mn-veth1 up
ip link set veth-services up
ip link set mn-veth2 up

DEVICES_BRIDGE="br-$(echo $DEVICES_NET_ID | cut -c1-12)"
SERVICES_BRIDGE="br-$(echo $SERVICES_NET_ID | cut -c1-12)"

echo "Conectando veth-devices à bridge: $DEVICES_BRIDGE"
ip link set veth-devices master $DEVICES_BRIDGE

echo "Conectando veth-services à bridge: $SERVICES_BRIDGE"
ip link set veth-services master $SERVICES_BRIDGE

# --- INÍCIO DA MODIFICAÇÃO ---
echo "--- Desativando STP nas pontes Docker para garantir conectividade imediata ---"
brctl stp $DEVICES_BRIDGE off
brctl stp $SERVICES_BRIDGE off
sleep 2

# --- ETAPA 3: INICIALIZAÇÃO DOS CONTÊINERES ---
echo "--- Iniciando todos os contêineres com o Docker Compose Unificado ---"
docker compose up -d --build

echo "--- Configurando rotas padrão nos dispositivos IoT ---"
docker exec iot-low-lixeira ip route add default via 10.10.10.1 || true
docker exec iot-medium-poluicao ip route add default via 10.10.10.1 || true
docker exec iot-high-agua ip route add default via 10.10.10.1 || true


echo -e "\n--- AMBIENTE PRONTO ---"
echo "Todos os contêineres Docker estão em execução. Verificando status:"
docker ps
