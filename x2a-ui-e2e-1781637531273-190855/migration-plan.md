# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components and moderate complexity for replacing the InSpec testing functionality with Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a template for the website. Can be directly used in Ansible without modification.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic validation
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Consider integrating with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation

- **Chef Automate/Infra Server**: Consider if these components need to be migrated:
  - If compliance reporting is needed: Evaluate AWX/Ansible Tower with compliance plugins
  - If configuration management only: Standard Ansible with source control is sufficient

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Preserve the same Apache configuration settings in Ansible tasks

- **SSH Security Controls**: The SSH root login restriction must be maintained
  - Migration approach: Create an Ansible task to ensure SSH configuration has `PermitRootLogin no`

- **Vault/secrets management**: 
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with Ansible-native testing solutions
  - Mitigation: Evaluate Ansible assert module combined with uri module for HTTP testing, or integrate with Testinfra for more advanced testing capabilities

- **SSL Certificate Management**: Ensuring secure handling of certificates
  - Mitigation: Use Ansible's crypto modules (openssl_*) with proper secret management via Ansible Vault

- **Chef Automate Replacement**: If compliance reporting is needed
  - Mitigation: Evaluate AWX/Tower with compliance plugins or other compliance tools that can integrate with Ansible

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better organization

2. **poodle_fix.yml** (low risk, already Ansible)
   - Integrate with the website_https role as a security hardening task
   - Ensure idempotency of the configuration

3. **InSpec Tests** (moderate complexity)
   - Develop equivalent tests using Ansible's testing capabilities
   - Implement Molecule for test orchestration

4. **Chef Deployment Scripts** (high complexity)
   - Determine if Chef Automate/Server functionality is still needed
   - If needed, create Ansible playbooks to deploy alternative solutions

### Assumptions

1. The primary goal is to migrate the compliance testing functionality from Chef InSpec to Ansible-native solutions
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and only need optimization
3. The Chef Automate and Chef Infra Server deployment scripts may not need direct migration if the compliance functionality is handled differently
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates are acceptable for the environment (not production)
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migration
7. The STIG compliance requirements referenced in the SSH profile are still applicable