from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class TrafficClassTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.0.0.1')  # HTTP client
        h2 = self.addHost('h2', ip='10.0.0.2')  # HTTP server
        h3 = self.addHost('h3', ip='10.0.0.3')  # UDP source
        h4 = self.addHost('h4', ip='10.0.0.4')  # Blocked host

        for h in [h1, h2, h3, h4]:
            self.addLink(h, s1)

if __name__ == '__main__':
    setLogLevel('info')
    topo = TrafficClassTopo()
    net = Mininet(topo=topo,
                  controller=RemoteController,
                  switch=OVSSwitch)
    net.start()
    CLI(net)
    net.stop()
