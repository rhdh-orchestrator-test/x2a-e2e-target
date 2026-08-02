# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec tests for compliance automation
3. Example configurations for web server deployment with SSL/TLS security

The migration complexity is relatively low as most of the repository already contains Ansible playbooks. The primary focus will be on converting the Chef Automate and Chef Infra Server deployment scripts to Ansible roles and playbooks. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible role for Chef Automate deployment or migrate to alternative compliance solution
- **Chef InSpec**: Consider using Ansible's built-in assert module or integrating with other compliance tools like OpenSCAP
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening (disabling SSLv3, enabling TLSv1.2) which must be preserved in the migration
- **SSH Hardening**: InSpec tests verify SSH root login is disabled, which should be enforced in the migrated Ansible playbooks
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider integrating with Let's Encrypt for production
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password, email)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible's assert module or integrate with other compliance tools
- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with equivalent Ansible roles
  - Mitigation: Create Ansible roles for Chef Automate deployment or migrate to alternative compliance solution

### Migration Order

1. **website-https-deployment** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert InSpec tests to Ansible assertions or equivalent

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Integrate with website-https-deployment playbook

3. **chef-automate-deployment** (moderate complexity)
   - Convert Bash scripts to Ansible roles and playbooks
   - Implement secrets management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, not production deployments
2. The Chef Automate and Chef Infra Server deployment is intended for on-premises or generic cloud VMs
3. The hardcoded credentials in the setup scripts are for demonstration purposes only
4. The InSpec tests are used for compliance verification and could be replaced with equivalent Ansible mechanisms
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The migration will maintain the same functionality but consolidate on Ansible as the single configuration management tool