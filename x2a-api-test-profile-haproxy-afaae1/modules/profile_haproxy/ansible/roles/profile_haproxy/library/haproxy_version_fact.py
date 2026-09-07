#!/usr/bin/python3

# Custom Ansible module to get HAProxy version
# Replaces Puppet custom fact haproxy_version.rb

from ansible.module_utils.basic import AnsibleModule
import subprocess
import re

def get_haproxy_version():
    """Get HAProxy version from command line"""
    try:
        result = subprocess.run(['haproxy', '-v'], 
                              capture_output=True, 
                              text=True, 
                              stderr=subprocess.STDOUT)
        
        if result.returncode == 0:
            # Parse version from output like "HA-Proxy version 2.4.18-0ubuntu1.2"
            match = re.search(r'version\s+(\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
        
        return None
        
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

def main():
    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True
    )
    
    version = get_haproxy_version()
    
    if version:
        module.exit_json(
            changed=False,
            ansible_facts={'haproxy_version': version},
            version=version
        )
    else:
        module.exit_json(
            changed=False,
            ansible_facts={'haproxy_version': None},
            version=None
        )

if __name__ == '__main__':
    main()