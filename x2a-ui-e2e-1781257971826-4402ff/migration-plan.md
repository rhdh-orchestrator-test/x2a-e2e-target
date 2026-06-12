# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2, restarts Apache and SSH services

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or included as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for Python-based testing
  - Option 2: Use Ansible Molecule with Goss for YAML-based testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that either:
  - Install and configure open-source alternatives like AWX (Ansible Tower)
  - Or set up a simpler CI/CD pipeline using GitLab/GitHub Actions with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain the restriction to TLSv1.2 protocol
  - Ensure proper certificate handling

- **SSH Security**: The SSH root login check must be preserved in the new testing framework
  - The STIG compliance checks should be maintained with proper documentation

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password') should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly and don't require migration of existing certificates

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework will require careful mapping of InSpec resources to equivalent testing constructs
  - Challenge: InSpec has domain-specific language for compliance testing that may not have direct equivalents
  - Mitigation: Use Ansible Molecule with Testinfra or Goss, which provide similar capabilities

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Challenge: The scripts perform Chef-specific operations that need to be replaced with Ansible alternatives
  - Mitigation: Replace with AWX/Tower deployment or other CI/CD infrastructure

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and can be preserved with minimal changes
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific functionality

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications
3. There is no dependency on Chef-specific resources beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates are for testing purposes only and don't need to be preserved
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and should be replaced with secure alternatives
7. The migration will focus on maintaining the same functionality rather than enhancing it
8. Test Kitchen is only used for development/testing and not in production environments