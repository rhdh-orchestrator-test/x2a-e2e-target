# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server functionality. Migration consideration: Keep as-is or incorporate into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Ansible's assert module for validation
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Vagrant (latest)**: Can be maintained for local development or replaced with containerized testing using Docker with Molecule

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable vulnerable protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to enforce secure TLS configurations

- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration should include equivalent tests.
  - Migration approach: Convert InSpec tests to Ansible assert statements or testinfra tests

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration.
  - Migration approach: Use Ansible's `acme_certificate` module for Let's Encrypt certificates

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms.
  - Mitigation: Use Ansible's assert module or testinfra for functional testing, or consider maintaining InSpec as a separate tool called from Ansible

- **Chef Automate Deployment**: The bash scripts for Chef Automate deployment need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower for similar functionality

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Convert to Ansible roles for better organization

2. **InSpec Tests** (moderate complexity)
   - Convert InSpec tests to Ansible-native testing solutions
   - Implement equivalent security checks using Ansible's assert module or testinfra

3. **Chef Automate Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The Chef components (InSpec) are used only for testing, not for configuration management.
3. There is no complex state management or data persistence that needs to be migrated.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and not used in production.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. There are no external dependencies or integrations not visible in the repository.
7. The migration will maintain the same level of security compliance testing currently provided by InSpec.