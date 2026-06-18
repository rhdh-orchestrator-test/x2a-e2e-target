# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid Chef InSpec and Ansible environment focused on compliance automation. The primary components are Ansible playbooks for configuring web servers with HTTPS support and Chef InSpec tests for verifying compliance. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security tagging with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower
  - Option 2: Use Ansible Automation Platform
  - Option 3: Set up GitLab CI/CD with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The current playbooks enforce TLSv1.2 and disable insecure protocols. Ensure this security hardening is maintained in the migrated solution.
  
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure this check is maintained in the Ansible-native testing solution.

- **Self-signed Certificates**: The current solution generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated during deployment but should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions and compliance checks.
  - Mitigation: Use Ansible's assert module combined with command/shell modules to replicate InSpec functionality.

- **Chef Automate Functionality**: If the team relies on Chef Automate's compliance reporting, finding an equivalent in the Ansible ecosystem may be challenging.
  - Mitigation: Consider integrating with compliance tools like OpenSCAP or Compliance as Code solutions.

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
2. **poodle-fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires replacement with Ansible automation platform deployment)

### Assumptions

1. The primary purpose of this repository is for demonstration/example purposes rather than production use, as indicated by the README.md.
2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems, not for Chef-managed systems.
3. The deployment scripts for Chef Automate and Chef Infra Server are included for demonstration but may not be actively used in the target environment.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production.
5. The Test Kitchen configuration is used for local testing and development, not for production deployment.
6. There are no external dependencies or integrations beyond what is explicitly defined in the repository.
7. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.