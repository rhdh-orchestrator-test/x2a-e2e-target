#!/usr/bin/env python3
"""
Ansible custom fact to determine Redis role (primary or replica)
"""

import json
import os
import sys


def main():
    """Determine Redis role by checking for replica configuration"""
    config_file = '/etc/redis/conf.d/replica.conf'
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
                if 'replicaof' in content:
                    role = 'replica'
                else:
                    role = 'primary'
        else:
            role = 'primary'
        
        # Return fact in JSON format for Ansible
        fact = {
            'redis_role': role
        }
        
        print(json.dumps(fact))
        
    except Exception as e:
        # On error, default to primary
        fact = {
            'redis_role': 'primary'
        }
        print(json.dumps(fact))
        sys.exit(0)


if __name__ == '__main__':
    main()