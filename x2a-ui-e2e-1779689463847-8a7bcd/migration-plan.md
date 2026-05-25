# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as most of the configuration is already in Ansible format. The migration will primarily involve replacing Chef InSpec tests with Ansible-native testing solutions.

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)
Complexity: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Ansible Assert module for basic verification
  - Option 3: Ansible Lint for static code analysis
  - Option 4: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible Tower/AWX for job scheduling and reporting
  - OpenSCAP integration with Ansible for compliance scanning
  - Custom reporting solutions using Ansible callback plugins

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
  
- **SSH Security**: The SSH root login compliance check must be preserved in the Ansible testing framework.

- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing a more robust certificate management solution in the Ansible migration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets identified in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec tests with equivalent Ansible testing capabilities while maintaining the same level of compliance verification.
  - Mitigation: Use Ansible Molecule with Testinfra or integrate with OpenSCAP for compliance testing.

- **Test Kitchen Replacement**: Finding an equivalent workflow to Test Kitchen for testing Ansible playbooks.
  - Mitigation: Implement Ansible Molecule for a similar development and testing workflow.

- **Chef Automate Deployment**: Replacing the Chef Automate deployment scripts with Ansible playbooks.
  - Mitigation: Create Ansible roles for deploying alternative compliance and reporting solutions.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions using Molecule and Testinfra or other appropriate testing frameworks.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks for deploying alternative compliance and reporting solutions.

4. **Test Kitchen Configuration** (kitchen.yml): Replace with Ansible Molecule configuration for testing.

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing capabilities.

2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and follow best practices, requiring minimal changes.

3. There is no requirement to maintain compatibility with Chef Automate or Chef Infra Server after migration.

4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

5. The security compliance requirements (STIG references in ssh_profile.rb) must be preserved in the migrated solution.

6. The repository appears to be a demonstration or example repository rather than a production codebase, based on the README content and structure.

7. No external dependencies or complex integrations are present beyond what is visible in the repository.