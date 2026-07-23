# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks (which are already in the target format)
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible
3. Preserving the InSpec testing functionality within an Ansible workflow

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a small team. The primary challenge will be replacing the Chef Automate/Infra Server deployment with equivalent Ansible automation while maintaining the compliance testing capabilities currently provided by InSpec.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or alternative configuration management approach
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.shell` module or migrate tests to Ansible's built-in assertion capabilities

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the migrated solution.
  - Migration approach: Preserve the OpenSSL certificate generation tasks in the Ansible playbook
  
- **POODLE Vulnerability Remediation**: The poodle_fix.yml playbook addresses a specific security vulnerability.
  - Migration approach: Maintain this security hardening in the consolidated Ansible playbook

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: The current setup uses InSpec for compliance testing with Ansible.
  - Mitigation: Either maintain InSpec tests and call them from Ansible or migrate tests to Ansible's native testing capabilities

- **Chef Automate Functionality**: Chef Automate provides compliance scanning and reporting.
  - Mitigation: Evaluate Ansible alternatives like AWX/Tower with compliance scanning plugins or maintain InSpec for compliance scanning

### Migration Order

1. **Consolidate Ansible Playbooks** (Low risk, already in target format)
   - Combine website_https.yml and poodle_fix.yml into a single playbook with clear task organization
   - Update the Kitchen configuration to use the consolidated playbook

2. **Convert Chef Deployment Scripts** (Medium complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Replace hardcoded variables with Ansible variables and Ansible Vault for sensitive data

3. **Enhance Testing Framework** (Medium complexity)
   - Integrate InSpec tests with Ansible or migrate to Ansible's native testing capabilities
   - Update CI/CD pipeline to use the new testing approach

### Assumptions

1. The primary goal is to consolidate on Ansible as the configuration management tool
2. InSpec testing capabilities are still desired for compliance verification
3. The Chef Automate and Chef Infra Server deployments are needed in the target environment
4. The current Ansible playbooks are functional and follow best practices
5. No additional Chef cookbooks or recipes exist beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or compatible
7. The migration will maintain the same level of security hardening currently implemented