# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible playbooks are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS verification, SSL protocol verification, SSH root login verification

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing, consider using OpenSCAP with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Configure system requirements (hostname, sysctl parameters)
  - Install and configure equivalent compliance and automation tools (options include AWX/Tower)

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH compliance checks in the InSpec tests must be implemented in the Ansible solution
  - Ensure root login remains disabled
  - Implement equivalent compliance checks using Ansible or Molecule

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count of credentials detected: 3 (username, password, organization name)

### Technical Challenges

- **Testing Framework Migration**: Moving from InSpec to Ansible-native testing tools
  - Mitigation: Map InSpec resources to equivalent Ansible modules or Molecule verifiers
  - Create a testing strategy document to ensure all compliance checks are preserved

- **Maintaining Compliance Validation**: Ensuring the same level of compliance checking
  - Mitigation: Document all compliance checks currently performed by InSpec and ensure equivalent checks are implemented in the Ansible solution

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **InSpec Tests** (convert to Ansible Molecule or equivalent)
4. **Chef Deployment Scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not to provide production-ready infrastructure code.

2. The Chef deployment scripts are used for setting up test environments, not production systems, given the hardcoded credentials.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

4. The current implementation uses self-signed certificates for HTTPS, which is acceptable for testing but may need to be replaced with proper certificate management for production.

5. There are no complex dependencies or integrations beyond what is visible in the repository.

6. The migration will focus on maintaining the same functionality and security posture, not adding new features.