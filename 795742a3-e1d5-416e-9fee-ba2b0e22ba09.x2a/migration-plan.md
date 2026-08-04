# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible playbooks are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Static HTML file used in the website deployment. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or DISA STIG tools that integrate with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and management
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible Security Automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) with proper secret management

- **SSH Hardening**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create Ansible tasks to enforce the same SSH security standards and use Ansible's assert module to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault or external secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use Ansible's assert module for basic checks and consider integrating with specialized compliance tools for more complex requirements.

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible Tower/AWX deployment.
  - Mitigation: Create Ansible playbooks that install and configure Ansible Tower/AWX with similar user/organization structure.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (already Ansible playbooks, low risk)
   - Review and optimize existing Ansible playbooks
   - Add documentation and improve variable management

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security checks

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production infrastructure codebase.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. There are no external dependencies or integrations beyond what's visible in the repository.
4. The migration will replace Chef InSpec with Ansible-native testing while maintaining the same compliance checks.
5. The deployment scripts are examples and not used in production environments.
6. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling.