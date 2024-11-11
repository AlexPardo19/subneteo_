import ipaddress
import math

class SubnetCalculator:
    def calculate_subnets(self, ip, mask, num_subnets):
        try:
            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
            new_prefix = network.prefixlen + max(0, (num_subnets - 1).bit_length())
            new_prefix = min(new_prefix, 32)
            
            subnets = list(network.subnets(new_prefix=new_prefix))[:num_subnets]

            result = {
                'network': str(network.network_address),
                'netmask': str(network.netmask),
                'subnets': []
            }

            for subnet in subnets:
                subnet_info = {
                    'network': str(subnet.network_address),
                    'netmask': str(subnet.netmask),
                    'first_ip': str(subnet.network_address + 1) if subnet.num_addresses > 2 else "N/A",
                    'last_ip': str(subnet.broadcast_address - 1) if subnet.num_addresses > 2 else "N/A",
                    'broadcast': str(subnet.broadcast_address)
                }
                result['subnets'].append(subnet_info)

            return result
        except ValueError as e:
            raise ValueError(f"Error al calcular subredes: {str(e)}")

    def determine_ip_class(self, ip):
        first_octet = int(ip.split('.')[0])
        if 1 <= first_octet <= 126:
            return "A"
        elif 128 <= first_octet <= 191:
            return "B"
        elif 192 <= first_octet <= 223:
            return "C"
        elif 224 <= first_octet <= 239:
            return "D (Multicast)"
        elif 240 <= first_octet <= 255:
            return "E (Reservada)"
        else:
            return "Dirección IP no válida"

