# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and verify secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

**Complexity**: Low to Medium - The repository contains a small number of files with straightforward functionality, but requires careful handling of security testing and compliance verification.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled according to security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112, V-38607)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Simple HTML file used for testing web server deployment - can be preserved as-is

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the setup scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX or Ansible Tower for centralized management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the InSpec tests to Ansible assert tasks that verify the same security controls

- **SSH Security Controls**: The SSH root login verification must be preserved
  - Approach: Create an Ansible task that checks the SSH configuration and fails if root login is enabled

- **Self-signed Certificates**: The certificate generation process should be preserved
  - Approach: Keep using the Ansible openssl_* modules as they are already Ansible-native

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match the InSpec tests

- **Test Reporting**: InSpec provides structured compliance reporting that Ansible doesn't natively support
  - Mitigation: Consider integrating with tools like Ansible Tower/AWX for reporting or implement custom reporting using Ansible's json_query filter

- **Idempotency**: Ensure all converted scripts maintain idempotency
  - Mitigation: Use Ansible's state modules rather than commands where possible, and add appropriate changed_when conditions

### Migration Order

1. **website-https and poodle-fix playbooks** (low risk, already Ansible)
   - Review and ensure they follow best practices
   - No actual migration needed as they are already Ansible playbooks

2. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assert tasks
   - Convert ssh_profile.rb to Ansible assert tasks
   - Integrate with Molecule for testing

3. **Chef deployment scripts** (high complexity)
   - Convert deploy-chef-server.sh to an Ansible playbook
   - Convert deploy-automate.sh to an Ansible playbook
   - Implement Ansible Vault for credential storage

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need functional changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The team has expertise in Ansible or will receive training
4. There is no requirement to maintain backward compatibility with Chef InSpec
5. The security compliance requirements will remain the same after migration
6. The deployment scripts are used in a controlled environment where the hardcoded credentials are acceptable (though they should be moved to Ansible Vault)
7. The self-signed certificates are acceptable for the environment (not production)