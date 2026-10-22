"""Adaptador de infraestructura para obtener estado de adaptadores con psutil."""

import psutil
from netops_desk.adapters import AdapterInfo

class PsutilAdaptersRunner:
    def run(self) -> list[AdapterInfo]:
        stats = psutil.net_if_stats()
        adapters = []
        
        for name, stat in stats.items():
            # psutil devuelve los flags como un conjunto de strings
            is_multicast = "multicast" in stat.flags if hasattr(stat, "flags") else False
            
            adapters.append({
                "name": name,
                "is_up": stat.isup,
                "speed_mbps": stat.speed,
                "mtu": stat.mtu,
                "is_multicast": is_multicast
            })
            
        return adapters