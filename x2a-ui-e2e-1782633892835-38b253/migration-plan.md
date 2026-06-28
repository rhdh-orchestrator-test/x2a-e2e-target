# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance with security standards

The migration complexity is low to medium, as most of the configuration is already in Ansible format. The primary work will involve integrating the Chef InSpec tests into an Ansible-native testing framework. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for compliance with security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with specific security requirements (SRG-OS-000112, V-38607)

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a template for website deployment. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated Ansible playbooks.
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled. This compliance check should be integrated into the Ansible workflow.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require careful mapping of test assertions to ensure equivalent coverage.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Server Deployment**: The Chef server deployment scripts need to be completely replaced as they are installing Chef-specific components.
  - Mitigation: Determine if Chef server functionality is still needed or if it can be replaced with Ansible automation controller

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Server Deployment Scripts** (high complexity, requires complete replacement)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef server deployment scripts are used for demonstration purposes and may not be needed in a pure Ansible environment.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The repository is primarily used for educational/demonstration purposes rather than production deployments.
6. The InSpec tests are focused on specific compliance requirements rather than comprehensive system testing.
7. There is no integration with external systems or services beyond what is explicitly configured in the playbooks.