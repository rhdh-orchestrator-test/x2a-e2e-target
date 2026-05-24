# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of Chef components that need migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-verification**:
    - Description: InSpec tests for verifying HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL/TLS protocol security checks

- **ssh-security-profile**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112, RHEL-08-000227)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache
- `poodle_fix.yml`: Ansible playbook for remediating SSL POODLE vulnerability in Apache
- `index.html`: Sample HTML file for the web server

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For simple tests: Use Ansible assert module
  - For complex compliance testing: Integrate with Ansible Lint or Molecule
  - Alternative: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the HTTPS configuration
  - Current implementation disables SSLv3 and enables only TLSv1.2
  - Migration should maintain or improve this security posture

- **SSH Security Hardening**: The SSH security profile checks must be preserved
  - Current implementation verifies that root login is disabled
  - Migration should include equivalent checks in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module for simple tests, consider keeping InSpec for complex compliance testing

- **Chef Server Deployment**: Replacing Chef Automate and Chef Infra Server deployment with equivalent Ansible roles
  - Mitigation: Research existing Ansible roles for similar functionality or create custom roles

### Migration Order

1. **Ansible Playbooks** (Low risk, no migration needed)
   - `website_https.yml` and `poodle_fix.yml` are already Ansible playbooks and don't require migration

2. **InSpec Tests** (Moderate complexity)
   - Convert `website_https_verify.rb` and `ssh_profile.rb` to Ansible tests
   - Implement equivalent functionality using Ansible's testing capabilities

3. **Chef Deployment Scripts** (High complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Replace Chef-specific functionality with Ansible equivalents

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.

2. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are functioning correctly and don't require modification beyond the testing framework.

3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment and will need to be replaced with equivalent Ansible functionality.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. There are no external dependencies or integrations beyond what's visible in the repository.

6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.