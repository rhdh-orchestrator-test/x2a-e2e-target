# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef components.

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and best practices enforcement

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Install and configure equivalent monitoring/compliance solutions
  - Options include:
    - AWX/Ansible Tower for web UI and job scheduling
    - Prometheus + Grafana for monitoring
    - OpenSCAP for compliance scanning

### Security Considerations

- **SSL Configuration**: The current implementation secures Apache with self-signed certificates and disables vulnerable protocols. Migration approach: Maintain the same security posture using Ansible's openssl_* modules.

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled. Migration approach: Create an Ansible role that applies the same SSH hardening and includes verification tasks.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic. Mitigation: Use Ansible's assert module with carefully crafted conditions to match InSpec's behavior.

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible. Mitigation: Consider integrating with OpenSCAP or other compliance tools that can provide similar reporting capabilities.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to align with best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible tasks using assert module or integrate with Molecule.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks that set up equivalent functionality.

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use, based on the README content.

2. The InSpec tests are intended to verify the Ansible playbook configurations, not to be run independently in production.

3. The deployment scripts are examples and may contain simplified configurations not suitable for production environments (e.g., hardcoded passwords).

4. The migration goal is to have a fully Ansible-based solution that maintains the same functionality and security posture as the original mixed Chef/Ansible approach.

5. There are no external dependencies or integrations beyond what's visible in the repository.

6. The target environment will continue to be Ubuntu 20.04 or compatible systems.