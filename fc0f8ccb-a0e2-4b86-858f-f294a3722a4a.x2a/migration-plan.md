# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Chef InSpec test profiles that need to be preserved and integrated with Ansible
2. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks for a single developer or DevOps engineer. The primary focus will be on preserving the compliance testing capabilities while standardizing on Ansible for infrastructure automation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration example of Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved but should be reviewed for best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be preserved but should be reviewed for best practices.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment and security.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible alternatives:
  - Option 1: AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Ansible Semaphore for lightweight UI
  - Option 3: GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated Ansible playbooks.
  
- **SSH Security**: The InSpec profile tests for SSH root login being disabled. This compliance check should be preserved in the migrated solution.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL/TLS certificate references should be managed securely
  - Credentials found: 1 set of username/password in each deployment script

### Technical Challenges

- **InSpec Integration**: Determining the best approach to integrate compliance testing with Ansible. Options include:
  - Converting InSpec tests to Ansible assertions
  - Keeping InSpec and calling it from Ansible
  - Using Ansible's built-in modules for compliance checks
  
- **Chef Automate Replacement**: Identifying the right Ansible-based solution to replace Chef Automate's functionality:
  - Reporting and visualization
  - Compliance scanning
  - Node management

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Review and refactor `chef-and-ansible/website_https.yml` and `chef-and-ansible/poodle_fix.yml` for best practices
   - Update testing framework from Test Kitchen to Molecule

2. **InSpec Tests** (Medium complexity)
   - Decide on testing strategy (keep InSpec or convert to Ansible)
   - Implement chosen approach for `chef-and-ansible/tests/website_https_verify.rb` and `chef-and-ansible/tests/ssh_profile.rb`

3. **Chef Deployment Scripts** (High complexity)
   - Convert `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh` to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is standardizing on Ansible while preserving compliance testing capabilities
2. The existing Ansible playbooks are functional and follow reasonable practices
3. There is no requirement to maintain backward compatibility with Chef
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. The security requirements (TLS 1.2, SSH hardening) must be preserved
6. The deployment scripts are currently used for development/testing environments, not production
7. There are no external dependencies or integrations not visible in the repository