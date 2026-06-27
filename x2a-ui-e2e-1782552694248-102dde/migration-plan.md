# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve replacing Chef InSpec tests with Ansible-native solutions like ansible-lint or molecule. The estimated timeline for this migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with ansible-lint, Molecule, or other Ansible-native testing solutions
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
- **Chef Automate/Infra Server**: Consider if these deployment scripts need to be migrated or if they're just examples

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
- **SSH Security**: The InSpec test checks for SSH root login being disabled. This security check should be maintained in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates generated during playbook execution
  - No encrypted secrets management currently implemented

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require understanding the equivalent assertions and test structures.
- **Compliance Reporting**: If compliance reporting is a requirement, ensure the Ansible solution provides similar capabilities to Chef InSpec.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already Ansible playbooks, minimal changes needed)
2. **website_https_verify.rb** (convert InSpec tests to Ansible-native tests)
3. **ssh_profile.rb** (convert InSpec compliance control to Ansible-native compliance check)
4. **deploy-chef-server.sh** and **deploy-automate.sh** (convert to Ansible roles if needed)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible, not for production deployment.
2. The deployment scripts for Chef Automate and Chef Infra Server are examples and may not need to be migrated if Chef components are being replaced entirely.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The security compliance requirements will remain the same after migration.
5. No external data sources or complex state management is involved in the current implementation.
6. The migration is focused on replacing Chef InSpec with Ansible-native solutions while maintaining the same functionality.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with proper secret management in a production environment.