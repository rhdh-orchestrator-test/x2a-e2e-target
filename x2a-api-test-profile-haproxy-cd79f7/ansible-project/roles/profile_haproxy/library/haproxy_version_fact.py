#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Custom Ansible fact module to get HAProxy version
# Converted from Puppet custom fact: haproxy_version.rb

DOCUMENTATION = '''
---
module: haproxy_version_fact
short_description: Get HAProxy version information
description:
    - Executes 'haproxy -v' command to extract version number
    - Only runs on Linux systems
    - Returns HAProxy version string or None if not available
author:
    - Converted from Puppet custom fact
'''

EXAMPLES = '''
- name: Get HAProxy version
  haproxy_version_fact:
  register: haproxy_version

- name: Display HAProxy version
  debug:
    msg: "HAProxy version: {{ haproxy_version.version }}"
'''

import re
import subprocess
import platform
from ansible.module_utils.basic import AnsibleModule


def get_haproxy_version():
    """Get HAProxy version by executing haproxy -v command."""
    # Only run on Linux systems (equivalent to Puppet's confine kernel: 'Linux')
    if platform.system().lower() != 'linux':
        return None
    
    try:
        # Execute haproxy -v command (equivalent to Puppet's Facter::Core::Execution.execute)
        result = subprocess.run(
            ['haproxy', '-v'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            # Extract version using regex (equivalent to Puppet's match(/version\s+(\d+\.\d+\.\d+)/)
            match = re.search(r'version\s+(\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
    
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        # HAProxy not installed or not accessible
        pass
    
    return None


def main():
    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True
    )
    
    version = get_haproxy_version()
    
    result = {
        'changed': False,
        'ansible_facts': {
            'haproxy_version': version
        },
        'version': version
    }
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()