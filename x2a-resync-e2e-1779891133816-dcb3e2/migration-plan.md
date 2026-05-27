# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTP response validation, SSL protocol verification, SSH configuration compliance

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef tools
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Sample HTML file used for testing. Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-test framework

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Consider these alternatives:
  - AWX/Ansible Tower for enterprise automation platform
  - Ansible Semaphore for lightweight GUI
  - GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Ensure Ansible roles for Apache maintain proper TLS configuration

- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Include equivalent checks in Ansible or use ansible-lint security rules

- **Self-signed Certificates**: The playbook generates self-signed certificates for HTTPS.
  - Migration approach: Use Ansible's crypto modules (openssl_*) which are already in use

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods.
  - Mitigation: Use Ansible assert module or consider maintaining InSpec tests separately if they provide value

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting capabilities.
  - Mitigation: Evaluate AWX/Tower compliance capabilities or integrate with additional compliance tools

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. Test Kitchen Configuration - Convert to Molecule
3. InSpec Tests - Convert to Ansible assertions or Molecule verifiers
4. Chef Deployment Scripts - Convert to Ansible roles for deploying alternative automation platforms

### Assumptions

1. The primary goal is to move away from Chef components while maintaining the same functionality
2. The InSpec tests are valuable and need equivalent functionality in the Ansible ecosystem
3. The deployment scripts for Chef Automate/Infra Server need to be replaced with equivalent Ansible automation platform deployment
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements (TLS 1.2, SSH hardening) must be maintained
6. The repository is primarily for demonstration/educational purposes rather than production use
7. No external dependencies or integrations beyond what's visible in the repository