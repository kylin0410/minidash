# Import build-in or 3rd-party modules
import psutil
from flask import Blueprint, jsonify

# Import private modules
from util import device
from flask_jwt_extended import jwt_required

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/api/dashboard/net/wired', methods=['GET'])
@jwt_required
def dash_net_wired():
    """
    Get wired network status.
    ---
    tags:
      - Dashboard API
    responses:
      200:
        description: OK.
        schema:
          id: net_stat
          properties:
            ipv4_addr:
              type: string
            ipv4_mask:
              type: string
            mac_addr:
              type: string
    """
    data = device.get_network('eth0')
    return jsonify(data)


@dashboard.route('/api/dashboard/net/wireless', methods=['GET'])
@jwt_required
def dash_net_wireless():
    """
    Get wireless network status.
    ---
    tags:
      - Dashboard API
    responses:
      200:
        description: OK.
        schema:
          id: net_stat
          properties:
            ipv4_addr:
              type: string
            ipv4_mask:
              type: string
            mac_addr:
              type: string
    """
    data = device.get_network('wlan0')
    return jsonify(data)


@dashboard.route('/api/dashboard/usage', methods=['GET'])
@jwt_required
def dash_usage():
    """
    Get CPU/MEM/SWAP/FS usage information.
    ---
    tags:
      - Dashboard API
    responses:
      200:
        description: Return all usage information.
        schema:
          id: usage
          properties:
            cpu:
              type: integer
              description: CPU usage in average.
              default: 0.0
            mem:
              type: integer
              description: Memory usage.
              default: 0.0
            swap:
              type: integer
              description: SWAP usage.
              default: 0.0
            fs:
              type: integer
              description: Root file system usage.
              default: 0.0
    """
    data = {"cpu": 0.0, "mem": 0.0, "swap": 0.0, "fs": 0.0}
    fs = psutil.disk_usage('/')
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    data["cpu"] = psutil.cpu_percent()
    data["mem"] = vm.percent
    data["swap"] = swap.percent
    data["fs"] = fs.percent
    return jsonify(data)


@dashboard.route('/api/dashboard/version', methods=['GET'])
@jwt_required
def dash_version():
    """
    Get system version. @todo
    ---
    tags:
      - Dashboard API
    responses:
      200:
        description: Return system version.
        schema:
          id: system_version
          properties:
            build_ver:
              type: string
              description: Build version.
    """
    build_ver = ""
    with open("build.ver", "r") as f:
        build_ver = f.readline()
    data = {"build_ver": build_ver}
    return jsonify(data)
