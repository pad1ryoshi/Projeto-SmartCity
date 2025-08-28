from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    "Um Node com encaminhamento IP habilitado."
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    "Topologia com um roteador conectando duas sub-redes."
    def build(self, **_opts):
        r1 = self.addNode('r1', cls=LinuxRouter, ip=None)
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        self.addLink(s1, r1, intfName2='r1-eth1')
        self.addLink(s2, r1, intfName2='r1-eth2')

def run():
    "Cria e executa a topologia completa de forma robusta"
    topo = NetworkTopo()
    # Usamos OVSBridge e não esperamos pela conexão com um controlador
    net = Mininet(topo=topo, switch=OVSBridge, controller=None, waitConnected=False)
    
    info('*** Iniciando a rede...\n')
    net.start()
    
    # --- Configuração das interfaces do roteador ---
    r1 = net['r1']
    info('*** Configurando IPs nas interfaces do roteador r1...\n')
    r1.cmd('ip addr add 10.10.10.1/24 dev r1-eth1')
    r1.cmd('ip addr add 10.10.20.1/24 dev r1-eth2')

    # --- Configuração manual dos switches para modo standalone ---
    s1 = net.get('s1')
    s2 = net.get('s2')
    info('*** Configurando switches para operar em modo standalone (sem controlador)...\n')
    s1.cmd('ovs-vsctl set-fail-mode s1 standalone')
    s2.cmd('ovs-vsctl set-fail-mode s2 standalone')

    # --- Anexando as redes Docker aos switches do Mininet ---
    info('*** Anexando redes Docker aos switches s1 e s2...\n')
    s1.attach('mn-veth1')
    s2.attach('mn-veth2')
    
    info('*** Roteador Mininet em execução.\n')
    info('*** A comunicação entre os dispositivos e a nuvem está estabelecida.\n')
    info('*** Para verificar o status dos switches, digite no CLI: sh ovs-vsctl show\n')
    info('*** Para testar, use "r1 ping 10.10.20.2" ou "r1 ping 10.10.10.3"\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
