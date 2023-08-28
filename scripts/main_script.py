import re
import yaml
from cloudvision.Connector.grpc_client import GRPCClient, create_query
from cloudvision.Connector.codec.custom_types import Wildcard
from parser import base

def get_active_switches(client, pattern=None):
    path_elts = ["DatasetInfo", "Devices"]
    query = [create_query([(path_elts, [])], "analytics")]
    switches = {}
    for batch in client.get(query):
        for notif in batch["notifications"]:
            for serial, details in notif["updates"].items():
                if details["deviceType"] == "EOS" and details["status"] == "active" and (pattern is None or re.match(pattern, details["hostname"])):
                    switches[serial] = details

    return switches

def get_lldp_neighbors(client, device_id):
    path_elts = [
        "Sysdb",
        "l2discovery",
        "lldp",
        "status",
        "local",
        Wildcard(),
        "portStatus",
        Wildcard(),
        "remoteSystem",
        Wildcard(),
    ]
    dataset = device_id
    query = [create_query([(path_elts, [])], dataset)]
    result = {}
    for batch in client.get(query):
        for notif in batch["notifications"]:
            if not notif["updates"]:
                continue
            path_elts = notif["path_elements"]
            port = path_elts[7]
            nei_port_id = notif["updates"].get("msap", {}).get("portIdentifier", {}).get("portId", "")
            if port.startswith("Ethernet") and nei_port_id.startswith("Ethernet"):
                neighbors = {
                    "Hostname": notif["updates"].get("sysName", {}).get("value", {}).get("value", ""),
                    "Port": port,
                    "Neighbor Device ID": notif["updates"].get("sysName", {}).get("value", {}).get("value", ""),
                    "Neighbor Port ID": nei_port_id,
                    "eosVersion": notif["updates"].get("eosVersion", ""),
                    "primaryManagementIP": notif["updates"].get("primaryManagementIP", ""),
                }
                result[port] = neighbors
    return result

def create_yaml_topology(switches, lldp_data):
    nodes = []
    links = []
    seen_connections = set()

    default_variables = {
        'veos': {
            'username': 'cvpadmin',
            'password': 'arista123',
        },
        'generic': {
            'username': 'cvpadmin',
            'password': 'arista123',
            'version': 'Rocky-8.5',
        },
        'cvp': {
            'username': 'root',
            'password': 'cvproot',
            'version': '2022.3.1',
            'instance': 'singlenode',
        },
    }
    for serial, switch in switches.items():
        hostname = switch["hostname"]
        nodes.append({
            hostname: {
                "ip_addr": switch["primaryManagementIP"],
                "node_type": "veos",
                "version": switch["eosVersion"],
            }
        })
        for port, neighbor_data in lldp_data[serial].items():
            neighbor_hostname = neighbor_data['Neighbor Device ID']
            neighbor_port = neighbor_data['Neighbor Port ID']
            if not neighbor_hostname or not neighbor_port:
                continue
            connection = sorted([
                f"{hostname}:{port}",
                f"{neighbor_hostname}:{neighbor_port}",
            ])
            connection_tuple = tuple(connection)
            if connection_tuple not in seen_connections:
                links.append({"connection": connection})
                seen_connections.add(connection_tuple)

    topology = {
        "nodes": nodes,
        "links": links,
    }
    final_topology = {**default_variables, **topology}

    with open('topology.yaml', 'w') as file:
        yaml.dump(final_topology, file, default_flow_style=False)

def main(apiserver_addr, token=None, certs=None, ca=None, key=None, pattern=None):

    raw_responses = []

    with GRPCClient(apiserver_addr, token=token, key=key, ca=ca, certs=certs) as client:
        switches = get_active_switches(client, pattern)

        lldp_data = {}
        for serial in switches.keys():
            lldp_data[serial] = get_lldp_neighbors(client, serial)
        
        create_yaml_topology(switches, lldp_data)

    return 0

if __name__ == "__main__":
    base.add_argument("--pattern", type=str, help="Regex pattern to filter switches by hostname")
    args = base.parse_args()
    exit(main(args.apiserver, certs=args.certFile, key=args.keyFile,
              ca=args.caFile, token=args.tokenFile, pattern=args.pattern))
