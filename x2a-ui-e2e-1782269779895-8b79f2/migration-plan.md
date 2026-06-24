# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with equivalent Ansible assertions using `assert` module
  - Consider using Ansible Molecule for testing infrastructure
  - Alternative: Keep InSpec tests but integrate them with Ansible using the `inspec` module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: Maintain the SSH security controls verified by the InSpec tests
  - Ensure root login remains disabled
  - Preserve compliance with security standards referenced in the tests (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in website_https.yml
  - Consider migrating to Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules
  - Challenge: InSpec has specialized resources for testing SSL/TLS configurations
  - Mitigation: Use Ansible's uri module with appropriate options or consider keeping InSpec for specialized tests

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks
  - Challenge: The scripts perform complex installation and configuration of Chef products
  - Mitigation: Create dedicated roles for Chef server installation if Chef infrastructure is still needed, or replace with Ansible AWX/Tower if moving away from Chef entirely

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires decision on whether to maintain Chef infrastructure)

### Assumptions

1. The primary goal is to consolidate on Ansible and move away from Chef for both configuration management and compliance testing
2. The Chef InSpec tests need to be converted to Ansible-native testing rather than maintained as InSpec tests
3. The Chef Automate and Chef Server deployment scripts are intended to be migrated to Ansible rather than maintained as-is
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. The security requirements and compliance standards referenced in the InSpec tests must be maintained in the Ansible implementation
6. No external dependencies or complex configurations exist beyond what is visible in the repository
7. The migration will maintain the same functionality and security posture as the original implementation