# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with the majority of time spent on converting InSpec tests to Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and shell scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration, including port listening status, HTTP response, and SSL/TLS protocol settings
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response validation, SSL/TLS protocol validation

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration, specifically checking if root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks, CCI compliance mapping

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `website_https.yml`: Ansible playbook for configuring HTTPS website. No migration needed as it's already in Ansible format.
- `poodle_fix.yml`: Ansible playbook for fixing SSL configuration to address POODLE vulnerability. No migration needed as it's already in Ansible format.
- `index.html`: Sample HTML file used in the website deployment. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Implement Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider integrating with OpenSCAP for compliance scanning

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSH Security Configuration**: The ssh_profile.rb InSpec test checks for secure SSH configuration. This should be implemented as an Ansible task that:
  1. Checks the SSH configuration
  2. Remediates any non-compliant settings
  3. Verifies the changes

- **SSL/TLS Security**: The website_https_verify.rb test checks for secure SSL/TLS configuration. This should be implemented as Ansible tasks that:
  1. Configure secure SSL/TLS settings
  2. Verify the configuration is correct
  3. Periodically check for compliance

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys
  - Count of credentials detected: 3 (username, password, and SSL private key)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require careful mapping of InSpec resources to Ansible modules. The main challenge is maintaining the same level of expressiveness and readability.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules, and develop reusable Ansible roles for common compliance checks.

- **Chef Automate Deployment**: The Chef Automate deployment scripts contain specific configurations that need to be carefully translated to Ansible.
  - Mitigation: Create an Ansible role specifically for Chef Automate deployment, with variables for all configurable parameters.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and don't need migration.
2. **Chef InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments.
2. The InSpec tests are used for compliance validation after Ansible playbook execution.
3. The deployment scripts are used for setting up test environments rather than production Chef servers.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The migration will maintain the same functionality but using Ansible-native solutions.
7. No specific performance requirements are needed for the migrated solution.
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only.