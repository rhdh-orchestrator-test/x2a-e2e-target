# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server setup scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring the migration preserves the security and compliance testing capabilities

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains a limited number of scripts and playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.command` module or consider migrating to Ansible's built-in assertion capabilities
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with the Ansible provisioner
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or another Ansible-based management solution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with specific security settings (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Preserve these security settings in the Ansible playbooks
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Ensure SSH hardening is included in the Ansible playbooks and maintain InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible
  - Mitigation: Use Ansible's `command` module to run InSpec tests or consider migrating to Ansible's native assertion capabilities

- **Chef Automate Replacement**: Finding an equivalent Ansible-based solution for Chef Automate functionality
  - Mitigation: Consider Ansible Automation Platform or other Ansible-based management solutions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Standardize and optimize existing playbooks
   - Add documentation and improve variable usage

2. **Chef Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Convert to Ansible playbooks
   - Implement Ansible Vault for credential storage
   - Test thoroughly to ensure equivalent functionality

3. **Testing Framework**: Medium complexity
   - Decide whether to maintain Test Kitchen or migrate to Molecule
   - Ensure InSpec tests continue to work with the new Ansible implementation

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are essential and must be preserved
3. The Chef Automate and Chef Infra Server setup scripts are needed in the Ansible version
4. The target environment will continue to be Ubuntu 20.04 or similar
5. The hardcoded credentials in the setup scripts are for demonstration only and will be replaced with secure alternatives
6. The existing Ansible playbooks are functional and follow best practices
7. No external dependencies or integrations beyond what's visible in the repository