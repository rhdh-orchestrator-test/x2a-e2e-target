#!/usr/bin/python3

# Copyright: (c) 2024, Ansible Migration
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: redis_role_fact
short_description: Determine Redis role (primary/replica)
description:
    - Checks for 'replicaof' directive in Redis replica configuration file
    - Returns 'replica' if replicaof is found, 'primary' otherwise
version_added: "1.0.0"
author:
    - Ansible Migration Team
options: {}
'''

EXAMPLES = r'''
- name: Get Redis role
  redis_role_fact:
  register: redis_role_result

- name: Display Redis role
  ansible.builtin.debug:
    msg: "Redis role is {{ redis_role_result.ansible_facts.redis_role }}"
'''

RETURN = r'''
ansible_facts:
    description: Facts about Redis role
    returned: always
    type: dict
    contains:
        redis_role:
            description: Redis role (primary or replica)
            returned: always
            type: str
            sample: "primary"
'''

import os
from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True
    )

    config_file = '/etc/redis/conf.d/replica.conf'
    redis_role = 'primary'

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
                if 'replicaof' in content:
                    redis_role = 'replica'
    except (IOError, OSError) as e:
        # If we can't read the file, assume primary role
        pass

    module.exit_json(
        changed=False,
        ansible_facts={'redis_role': redis_role}
    )


if __name__ == '__main__':
    main()