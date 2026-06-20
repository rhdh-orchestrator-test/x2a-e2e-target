# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring Apache web servers with HTTPS
2. Chef InSpec tests for validating security compliance of those deployments

Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration complexity is **LOW** as most of the infrastructure code is already in Ansible format. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions. Estimated timeline: **1-2 weeks** for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server deployment with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 protocol

- **website-https-compliance**:
    - Description: InSpec tests to verify HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh-compliance**:
    - Description: InSpec profile to verify SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for web server testing

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation

- **Chef Automate/Infra Server**: Consider migrating to:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Content Collections for role and module management

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enforces TLSv1.2
- **SSH Security**: Maintain compliance checks for SSH configuration (root login disabled)
- **Self-signed Certificates**: Consider implementing more robust certificate management using Ansible's certificate modules
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated during deployment

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic
  - Mitigation: Use Ansible assert module with appropriate conditional checks
  
- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated
  - Mitigation: Consider implementing custom reporting using Ansible callbacks or integrating with tools like Ansible Tower

- **Test Kitchen Workflow**: Current workflow uses Test Kitchen for orchestration
  - Mitigation: Implement equivalent workflow using Molecule for testing Ansible roles

### Migration Order

1. **website-https** and **poodle-fix** playbooks (already in Ansible format, minimal changes needed)
2. **website-https-compliance** tests (convert InSpec tests to Ansible assertions or Molecule tests)
3. **ssh-compliance** profile (convert InSpec profile to Ansible security checks)
4. **chef-deployment** scripts (convert to Ansible playbooks for deploying Ansible Tower/AWX)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security compliance requirements (disabling SSLv3, SSH root login) must be maintained in the migrated solution.
4. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration purposes and can be replaced with equivalent Ansible Tower/AWX deployment.
5. No external data sources or complex inventory management is being used in the current implementation.
6. The migration will focus on maintaining the same functionality while moving entirely to Ansible-native solutions.
7. No specific performance requirements are documented that would affect the migration approach.