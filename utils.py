import re
import os
import threading
import shutil

from shell import OpenStackShell

class OpenStackManager:
    def __init__(self, sh_filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sh_folder_path = os.path.join(script_dir, "sh-files")
        self.file_sh_path = os.path.join(sh_folder_path, sh_filename)

        self.shell = OpenStackShell(
            self.file_sh_path, 
            password=""
        )
        self.openstack_lock = threading.Lock()

    def get_images(self):
        with self.openstack_lock:
            images = self.shell.exec("openstack image list --max-width 500")
            pattern = r"\|\s*([a-f0-9\-]{36})\s*\|\s*(CC-.*?)\s*\|\s*(\w+)\s*\|"
            matches = re.findall(pattern, images)
            return {match[1]: match[0] for match in matches}

    def get_keypairs(self):
        with self.openstack_lock:
            keys = self.shell.exec("openstack keypair list --max-width 500")
            pattern_keys = r"\|\s*([^\|]+?)\s*\|\s*[0-9a-f:]*\s*\|\s*\w+\s*\|"
            matches = re.findall(pattern_keys, keys)
            return matches

    def get_secgroup(self):
        with self.openstack_lock:
            sec = self.shell.exec("openstack security group list -c ID -c Name --max-width 500")
            pattern_sec = r"\|\s*([a-f0-9-]{36})\s*\|\s*([^\|]+?)\s*\|"
            matches = re.findall(pattern_sec, sec)
            return {match[1]: match[0] for match in matches}

    def get_networks(self):
        with self.openstack_lock:
            output = self.shell.exec("openstack network list -c ID -c Name --max-width 500")
            pattern_net = r"\|\s*([a-f0-9-]{36})\s*\|\s*([^\|]+?)\s*\|"
            matches = re.findall(pattern_net, output)
            return {match[1].strip(): match[0] for match in matches}

    def new_floating_ip(self, machine_name):
        with self.openstack_lock:
            ip_name = machine_name + "-floating-ip"
            result = self.shell.exec("openstack floating ip create --description " + ip_name + " public")

            pattern_ip_id = r"\|\s*id\s*\|\s*([^\|]+?)\s*\|"
            matches = re.findall(pattern_ip_id, result)

            pattern_ip_addr = r"\|\s*floating_ip_address\s*\|\s*([^\|]+?)\s*\|"
            matches_addr = re.findall(pattern_ip_addr, result)

            return matches[0], matches_addr[0]

    def add_floating_ip(self, server_name, ip_id):
        with self.openstack_lock:
            self.shell.exec("openstack server add floating ip " + server_name + " " + ip_id)

    def get_server(self):
        with self.openstack_lock:
            servers = {}
            result = self.shell.exec("openstack server list -c ID -c Name -c Networks -c Status --max-width 500")
            for line in result.strip().splitlines():
                parts = [p.strip() for p in line.strip('|').split('|')]
                if len(parts) < 3:
                    continue
                vm_id, name, status, net_info = parts
                #filtra status ACTIVE, altrimenti problemi con floating ip
                if status != "ACTIVE":
                    continue
                match = re.search(r'=[^,]+,\s*([\d.]+)', net_info)
                public_ip = match.group(1) if match else None
                servers[name] = [vm_id, public_ip]
            return servers

    def delete_server(self, name):
        with self.openstack_lock:
            cmd = "openstack server delete " + name + " -v"
            print(cmd)
            self.shell.exec(cmd)

    def delete_floating_ip(self, ip_addr):
        with self.openstack_lock:
            self.shell.exec("openstack floating ip delete " + ip_addr)


    def get_nodes(self):
        return [
            "compute_arm64",
            "compute_cascadelake",
            "compute_cascadelake_r",
            "compute_gigaio",
            "compute_haswell_ib",
            "compute_icelake_r650",
            "compute_icelake_r750",
            "compute_liquid",
            "compute_skylake",
            "compute_zen3",
            "gpu_k80",
            "gpu_m40",
            "gpu_mi100",
            "gpu_p100",
            "gpu_p100_nvlink",
            "gpu_p100_v100",
            "storage",
            "storage_hierarchy"
        ]

    def new_reservation(self, node_type, machine_name, end_date, end_time):
        end_date_time = f"{end_date} {end_time}"

        with self.openstack_lock:
            command = (
                "openstack reservation lease create --reservation "
                f"min=1,max=1,resource_type=physical:host,resource_properties='[\"=\", \"$node_type\", \"{node_type}\"]' "
                f'--start-date "now" --end-date "{end_date_time}" {machine_name} -c reservations'
            )
            result = self.shell.exec(command)

            pattern_error = "ERROR: Not enough resources available with query"
            if pattern_error in result:
                print("Errore: Risorse non sufficienti per la prenotazione.")
                return None, None

            pattern_reservation_id = r'"id":\s*"([^"]+)"'
            pattern_lease_id = r'"lease_id":\s*"([^"]+)"'

            reservation_id = re.findall(pattern_reservation_id, result)
            lease_id = re.findall(pattern_lease_id, result)

            print(f"Reservation ID: {reservation_id}")
            print(f"Lease ID: {lease_id}")

            return reservation_id, lease_id

    def create_baremetal_machine(self, image_id, key, sec_group, network, res_id, lease_id, name):
        with self.openstack_lock:
            command = [
                "openstack", "server", "create",
                "--flavor", "baremetal",
                "--image", image_id,
                "--key-name", key,
                "--security-group", sec_group,
                "--hint", "reservation=" + res_id[0],
                "--property", "reservation_id="+lease_id[0],
                "--network", network,
                name
            ]

            cmd_str = " ".join(command)
            result = self.shell.exec(cmd_str)
            return result


    def get_flavors(self):
        with self.openstack_lock:
            flavor = self.shell.exec("openstack flavor list --max-width 500")
            pattern = r"\|\s*(\d+)\s*\|\s*(m[^\|]+?)\s*\|"
            matches = re.findall(pattern, flavor)
            return {match[1]: match[0] for match in matches}

    def create_virtual_machine(self, flavor, image_id, key, sec_group, network, name):
        with self.openstack_lock:
            command = [
                "openstack", "server", "create",
                "--flavor", flavor,
                "--image", image_id,
                "--key-name", key,
                "--security-group", sec_group,
                "--network", network,
                name
            ]

            cmd_str = " ".join(command)
            result = self.shell.exec(cmd_str)
            return result
