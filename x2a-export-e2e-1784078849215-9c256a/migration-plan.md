# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as we need to replace InSpec tests with Ansible-compatible testing solutions. Estimated timeline for migration: 1-2 weeks.

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
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-compatible testing framework.
- `index.html`: Sample HTML file used for testing the web server configuration.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs or on-premises

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-testinfra for Python-based infrastructure testing as an alternative

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible Tower/AWX for centralized management
  - OpenSCAP for compliance scanning
  - Prometheus + Grafana for monitoring and reporting

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains or improves the security posture:
  - Maintain TLSv1.2 requirement
  - Consider upgrading to TLSv1.3 where supported
  - Ensure proper certificate management

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure SSH hardening is maintained in the Ansible-only solution
  - Implement equivalent checks for SSH root login restrictions

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing solutions:
  - Challenge: InSpec has specific testing syntax and resources that may not have direct equivalents
  - Mitigation: Use a combination of Molecule, testinfra, and custom Ansible tasks to achieve similar testing capabilities

- **Compliance Reporting**: If compliance reporting is a requirement:
  - Challenge: Chef Automate provides built-in compliance reporting that needs to be replaced
  - Mitigation: Implement OpenSCAP with Ansible or integrate with existing security tools

### Migration Order

1. **website_https.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better organization

2. **poodle_fix.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https role as a security enhancement

3. **InSpec Tests** (moderate complexity)
   - Develop equivalent tests using Ansible Molecule and testinfra
   - Ensure all compliance checks are maintained

4. **Chef Automate Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for deploying alternative compliance solutions
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.

2. The Chef Automate and Chef Infra Server deployment scripts are examples and not part of the core functionality.

3. The security compliance requirements (like disabling SSH root login and fixing POODLE vulnerability) need to be maintained in the migrated solution.

4. Test Kitchen is used primarily for testing and not for production deployment.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to cloud environments.

6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.

7. The self-signed certificates are for testing purposes and would be replaced with proper certificates in a production environment.