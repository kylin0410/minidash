# Import build-in or 3rd-party modules
import logging
from netaddr import IPAddress
import os
import psutil
import re
from subprocess import Popen, PIPE
import sys
import socket
import time
import traceback


def change_password(username, password):
    """
    Change password.
    """
    cmd = ['passwd', username]
    proc = Popen(cmd,
                 stdin=PIPE,
                 stdout=PIPE,
                 stderr=PIPE,
                 universal_newlines=True)
    proc.stdin.write("{}\n{}\n".format(password, password))
    proc.stdin.flush()

    # Give passwd cmd 2 seconds to finish and kill it otherwise.
    for x in range(0, 10):
        if proc.poll() is not None:
            break
        time.sleep(0.2)
    else:
        proc.terminate()
        time.sleep(1)
        proc.kill()
        logging.error("Command passwd did not terminate in 2 seconds.")
        return False
    if proc.returncode != 0:
        logging.error("Fail to change password to {}.".format(username))
        return False
    return True


def del_files(folder):
    """
    Delete files under given folder.
    """
    _exec_cmd(['rm ' + folder + '/*'], shell=True)


def get_service_stat(serv_name):
    """
    Get service status: {name, load, active, sub, desc}
    """
    res, stdout, stderr = _exec_cmd(
        ['systemctl list-units --type service --all | grep service'],
        shell=True)
    reg = (r'\s+(\S+.service)\s+(loaded|not-found)\s+(active|inactive)\s+'
           r'(dead|exited|running|waiting)\s+([^\n\r]+)')
    raw_data = re.findall(reg, stdout, re.MULTILINE)
    serv_stat = {'name': '', 'load': '', 'active': '', 'sub': '', 'desc': ''}
    for row in raw_data:
        if row[0] != serv_name:
            continue
        serv_stat = {
            'name': row[0],
            'load': row[1],
            'active': row[2],
            'sub': row[3],
            'desc': row[4].strip()
        }
    return serv_stat


def get_network(ifname):
    """
    Get network information by given interface name.
    """
    sysinfo = {'ipv4_addr': '', 'ipv4_mask': '', 'mac_addr': ''}
    for nic, addrs in psutil.net_if_addrs().items():
        if nic != ifname:
            continue
        for addr in addrs:
            if addr.family == socket.AF_INET:
                sysinfo['ipv4_addr'] = addr.address
                sysinfo['ipv4_mask'] = addr.netmask
            if addr.family == psutil.AF_LINK:
                sysinfo['mac_addr'] = addr.address
    return sysinfo


def list_camera():
    """
    List camera info
    """
    camera_list = []
    res, stdout, stderr = _exec_cmd(['v4l2-ctl', '--list-devices'])
    camera_info = {
        'usb_id': -1,
        'dev_name': '',
        'dev_path': '',
        'dev_id': -1,
        'status': 'normal'
    }
    got = False
    for line in stdout.splitlines():
        match = re.search(r'(.+\(usb-.+(\d)\)):', line)
        if match:
            got = True
            camera_info['dev_name'] = match.group(1)
            camera_info['usb_id'] = int(match.group(2))

        match = re.search(r'(/dev/video(\d+))', line)
        if match:
            camera_info['dev_path'] = match.group(1)
            camera_info['dev_id'] = int(match.group(2))
            if got:
                camera_list.append(camera_info)
                camera_info = {
                    'usb_id': -1,
                    'dev_name': '',
                    'dev_path': '',
                    'dev_id': -1,
                    'status': 'normal'
                }
                got = False
    return camera_list


def list_dns():
    """
    List domain name servers.
    """
    dns_list = []
    res, stdout, stderr = _exec_cmd(['cat', '/etc/resolv.conf'])
    for line in stdout.splitlines():
        match = re.search(r'nameserver\s+(\S+)', line)
        if match:
            dns_list.append(match.group(1))
    return dns_list


def pack_something(base_dir, tar_file, name):
    """
    Pack something by given parameters.
    """
    os.chdir(base_dir)
    _exec_cmd(['tar zcvf {} {}'.format(tar_file, name)], shell=True)
    _exec_cmd(['sync'])
    return os.path.join(base_dir, tar_file)


def reboot():
    """
    System reboot.
    """
    _exec_cmd(['reboot'])


def restart_service(serv_name):
    """
    Restart service by given name.
    """
    _exec_cmd(['systemctl', 'restart', serv_name])


def set_network(config, dhcpcd_path):
    """
    Enable network setting.
    """
    dhcp_enable = config.get('dhcp_enable', 1)
    wired = config.get('wired', {})
    ipv4_addr = wired.get('ipv4_addr', '192.168.1.2')
    ipv4_mask = wired.get('ipv4_mask', '255.255.255.0')
    ipv4_route = wired.get('ipv4_route', '192.168.1.1')
    mask_bits = IPAddress(ipv4_mask).netmask_bits()
    dns_list = config.get('dns', ['8.8.8.8', '223.5.5.5'])
    dns_str = ' '.join(dns_list)
    with open('/tmp/dhcpcd.conf', 'w') as out:
        out.write('hostname\n')
        out.write('clientid\n')
        out.write('persistent\n')
        out.write('option rapid_commit\n')
        out.write('option domain_name_servers, domain_name,')
        out.write(' domain_search, host_name\n')
        out.write('option classless_static_routes\n')
        out.write('option interface_mtu\n')
        out.write('require dhcp_server_identifier\n')
        out.write('slaac private\n\n')
        if 0 == dhcp_enable:
            out.write('interface eth0\n')
            out.write('static ip_address={}/{}\n'.format(ipv4_addr, mask_bits))
            out.write('static routers={}\n'.format(ipv4_route))
            out.write('static domain_name_servers={}\n'.format(dns_str))
        else:
            out.write('profile static_eth0\n')
            out.write('static ip_address={}/{}\n'.format(ipv4_addr, mask_bits))
            out.write('static routers={}\n'.format(ipv4_route))
            out.write('static domain_name_servers={}\n\n'.format(dns_str))
            out.write('# fallback to static profile on eth0\n')
            out.write('interface eth0\n')
            out.write('fallback static_eth0\n')

    # See if new conf equals to old one.
    diff = True
    res, stdout, stderr = _exec_cmd(['diff', '/tmp/dhcpcd.conf', dhcpcd_path])
    if not stdout:
        diff = False
        _exec_cmd(['rm', '/tmp/dhcpcd.conf'])
    else:
        _exec_cmd(['mv', '/tmp/dhcpcd.conf', dhcpcd_path])
    return diff


def start_service(serv_name):
    """
    Start service by given name.
    """
    _exec_cmd(['systemctl', 'enable', serv_name])
    _exec_cmd(['systemctl', 'start', serv_name])


def stop_service(serv_name):
    """
    Stop service by given name.
    """
    _exec_cmd(['systemctl', 'stop', serv_name])
    _exec_cmd(['systemctl', 'disable', serv_name])


def uppack_file(filename, base_folder):
    """
    Unpack file.
    """
    os.chdir(base_folder)
    res, stdout, stderr = _exec_cmd(['tar', 'zxvf', filename])
    return res


def _exec_cmd(cmd_args, timeout=3, shell=False):
    """
    Private function. Execute command and get standart output message.
    """
    stdout, stderr = '', ''
    proc = None
    try:
        logging.debug(cmd_args)
        proc = Popen(cmd_args, stdout=PIPE, stderr=PIPE, shell=shell)
        stdout, stderr = proc.communicate(timeout=timeout)
        stdout = stdout.decode('utf-8', errors='ignore')
        stderr = stderr.decode('utf-8', errors='ignore')
    except Exception:
        tp, value, tb = sys.exc_info()
        logging.error('\n    '.join(
            map(str.strip, traceback.format_exception(tp, value, tb))))
    finally:
        res = None
        if proc:
            proc.terminate()
            res = proc.returncode
            if res is None:
                res = -1
        logging.debug("res={}, stdout={}.".format(res, stdout))
        if res != 0:
            logging.error("res={}, stderr={}".format(res, stderr))
    return res, stdout, stderr


if __name__ == '__main__':
    pass
