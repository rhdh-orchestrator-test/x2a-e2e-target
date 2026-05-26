# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity as most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server with HTTPS configuration, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-fix**:
    - Description: Security patch for Apache to mitigate POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, security hardening

- **website-https-verify**:
    - Description: InSpec test profile for validating HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-profile**:
    - Description: InSpec test profile for validating SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks, STIG controls

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. No migration needed, can be used as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For website_https_verify.rb: Use Ansible's uri module in assert tasks or molecule verify
  - For ssh_profile.rb: Use Ansible's assert module with command/shell modules or ansible-lint security checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: The deployment scripts for Chef infrastructure can be converted to Ansible roles that deploy alternative monitoring/compliance solutions:
  - Consider migrating to Ansible AWX/Tower for orchestration
  - Use Prometheus/Grafana for monitoring
  - Use OpenSCAP or Ansible's built-in security roles for compliance

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the existing Ansible playbook (poodle_fix.yml) to an Ansible role with proper idempotence checks

- **SSH Hardening**: The SSH security profile must be maintained
  - Migration approach: Create an Ansible role that implements the same security controls and uses assert tasks for validation

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically; this approach can be maintained but with proper secret management for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar validation logic
  - Consider using ansible-lint for static analysis of security practices

- **Compliance Reporting**: InSpec provides structured compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting using Ansible's callback plugins or integrate with tools like OpenSCAP

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
2. **poodle-fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Server/Automate deployment scripts** (high complexity, requires architectural decisions on replacement technologies)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef InSpec tests are used only for validation and not for remediation.
3. The deployment scripts for Chef Server and Automate are examples and not part of the core functionality to be migrated.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The migration will maintain the same level of security validation but using Ansible-native approaches.
7. No actual Chef cookbooks or recipes need migration as the repository primarily contains Ansible playbooks with InSpec tests.