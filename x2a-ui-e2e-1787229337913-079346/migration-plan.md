# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG references

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Static HTML content for the website deployed by the Ansible playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules within playbooks
  - Option 2: Use Molecule for testing Ansible roles with testinfra as the verifier
  - Option 3: Maintain InSpec as a separate testing tool but integrate with Ansible CI/CD

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule for testing Ansible roles
  - Option 2: Create Ansible playbooks for test environment provisioning

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Use GitLab CI/CD or Jenkins for Ansible playbook execution
  - Option 3: Use Ansible Automation Platform if enterprise features are required

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Consider:
  - Using Ansible's `community.crypto` collection for certificate management
  - Integrating with Let's Encrypt for production-grade certificates
  - Implementing certificate rotation and renewal

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement:
  - Implement equivalent checks using Ansible's `assert` module
  - Consider using `ansible.posix.sshd_config` module for SSH configuration management
  - Implement comprehensive SSH hardening using the `devsec.hardening.ssh_hardening` role

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the Chef Automate/Infra Server deployment scripts
  - Migrate to Ansible Vault for secure credential storage
  - Consider integration with external secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing requires:
  - Understanding the InSpec resource model and mapping to Ansible modules
  - Implementing equivalent assertions in Ansible
  - Ensuring compliance metadata (CCI, STIG references) is preserved in documentation

- **Chef Automate/Infra Server Replacement**: Determining the appropriate replacement for Chef Automate/Infra Server depends on:
  - Current usage patterns and requirements
  - Need for a web UI for playbook execution
  - Compliance reporting requirements
  - Integration with existing CI/CD pipelines

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper directory structure
   - Create role with tasks, templates, handlers, and defaults
   - Move inline templates to template files
   - Implement idempotent certificate management

2. **poodle_fix.yml** (Priority 1): Integrate into a security hardening role
   - Create a dedicated SSL hardening role or task file
   - Implement idempotent configuration management
   - Add additional SSL/TLS hardening measures

3. **InSpec Tests** (Priority 2): Convert to Ansible testing framework
   - Implement equivalent tests using Ansible assert or Molecule/testinfra
   - Preserve compliance metadata in documentation
   - Ensure test coverage matches or exceeds current InSpec tests

4. **Chef Automate/Infra Server Deployment** (Priority 3): Replace with Ansible automation platform
   - Implement Ansible playbooks for deploying chosen automation platform
   - Migrate user and organization management to the new platform
   - Implement secure credential management

### Assumptions

1. The current implementation is used for testing and demonstration purposes, not production
2. The InSpec tests are used for compliance validation and security checks
3. The Chef Automate/Infra Server deployment scripts are used for setting up a test environment
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations not visible in the repository
6. The migration will preserve all current functionality while standardizing on Ansible
7. The hardcoded credentials in the deployment scripts are not used in production environments
8. The self-signed certificates are acceptable for the current use case
9. The repository is primarily used for educational or demonstration purposes
10. There are no custom Chef resources or complex Chef-specific logic that would be difficult to migrate to Ansible