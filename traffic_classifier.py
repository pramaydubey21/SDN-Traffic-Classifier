from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr

log = core.getLogger()

class TrafficClassifier(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        self.mac_to_port = {}
        log.info("TrafficClassifier running on %s", dpid_to_str(connection.dpid))

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        self.mac_to_port[packet.src] = event.port

        # Learn output port
        if packet.dst in self.mac_to_port:
            out_port = self.mac_to_port[packet.dst]
        else:
            out_port = of.OFPP_FLOOD

        # Check for IP packets
        ip = packet.find('ipv4')
        if ip:
            src_ip = str(ip.srcip)

            # RULE 1: Block h4 (10.0.0.4)
            if src_ip == '10.0.0.4':
                log.info("BLOCKED traffic from %s", src_ip)
                msg = of.ofp_flow_mod()
                msg.priority = 20
                msg.match.dl_type = 0x0800
                msg.match.nw_src = IPAddr('10.0.0.4')
                # No actions = drop
                self.connection.send(msg)
                return

            # RULE 2: ICMP - allow
            icmp = packet.find('icmp')
            if icmp:
                log.info("ICMP traffic from %s [ALLOWED]", src_ip)
                msg = of.ofp_flow_mod()
                msg.priority = 10
                msg.idle_timeout = 30
                msg.match.dl_type = 0x0800
                msg.match.nw_proto = 1
                msg.match.nw_src = IPAddr(src_ip)
                msg.actions.append(of.ofp_action_output(port=out_port))
                self.connection.send(msg)

            # RULE 3: TCP/HTTP - high priority
            tcp = packet.find('tcp')
            if tcp:
                if tcp.dstport == 80:
                    log.info("HTTP traffic from %s [HIGH PRIORITY]", src_ip)
                    msg = of.ofp_flow_mod()
                    msg.priority = 15
                    msg.idle_timeout = 60
                    msg.match.dl_type = 0x0800
                    msg.match.nw_proto = 6
                    msg.match.nw_src = IPAddr(src_ip)
                    msg.match.tp_dst = 80
                    msg.actions.append(of.ofp_action_output(port=out_port))
                    self.connection.send(msg)
                else:
                    log.info("TCP traffic from %s [ALLOWED]", src_ip)

            # RULE 4: UDP - log and allow
            udp = packet.find('udp')
            if udp:
                log.info("UDP traffic from %s [LOGGED]", src_ip)
                msg = of.ofp_flow_mod()
                msg.priority = 10
                msg.idle_timeout = 30
                msg.match.dl_type = 0x0800
                msg.match.nw_proto = 17
                msg.match.nw_src = IPAddr(src_ip)
                msg.actions.append(of.ofp_action_output(port=out_port))
                self.connection.send(msg)

        # Forward current packet
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=out_port))
        self.connection.send(msg)

class launch_controller(object):
    def __init__(self):
        core.openflow.addListenerByName("ConnectionUp", self._handle_ConnectionUp)

    def _handle_ConnectionUp(self, event):
        TrafficClassifier(event.connection)

def launch():
    core.registerNew(launch_controller)
