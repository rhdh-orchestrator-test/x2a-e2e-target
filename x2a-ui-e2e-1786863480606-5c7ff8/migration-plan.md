# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a standardized Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to convert. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be directly reused) and medium complexity for converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test page for the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set up equivalent monitoring and compliance capabilities
  - Configure centralized management for Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Disable older SSL/TLS protocols

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be implemented as Ansible tasks
  - Ensure PermitRootLogin is disabled
  - Implement equivalent security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Challenge: InSpec has specific testing constructs that don't directly map to Ansible
  - Mitigation: Use a combination of Ansible assert module and custom modules where needed

- **Chef Server Replacement**: Determining the appropriate Ansible management solution
  - Challenge: Chef Automate provides compliance and management features
  - Mitigation: Evaluate AWX/Tower or other Ansible management platforms

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, can be directly reused
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible playbooks for equivalent functionality

### Assumptions

1. The current Ansible playbooks are working as expected and don't require significant modifications
2. The InSpec tests are critical for compliance validation and need equivalent functionality in the Ansible solution
3. The Chef Automate/Infra Server deployment is needed for the target environment
4. No external dependencies or integrations beyond what's visible in the repository
5. The migration will maintain the same level of security and compliance validation
6. The target environment will continue to be Ubuntu 20.04 or compatible systems