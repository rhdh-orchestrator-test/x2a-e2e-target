# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is focused on converting the InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec tests with Ansible playbooks for secure web server deployment
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: HTTPS configuration, SSL/TLS security testing, web server deployment with Apache

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user and organization creation, system configuration

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled using self-signed certificates. Migration considerations include preserving the SSL certificate generation and Apache configuration.

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2. Migration considerations include ensuring the security hardening is maintained.

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Vagrant to create a test environment and runs the Ansible playbook. Migration considerations include replacing with an Ansible-native testing framework.

- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies the web server is listening on port 443, returns a 200 status code, contains expected content, and has proper SSL/TLS configuration. Migration considerations include converting to Ansible-compatible testing.

- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control that ensures SSH root login is disabled. Migration considerations include converting to Ansible-compatible security testing.

- `setup-automate/deploy-automate.sh`: Bash script that deploys Chef Automate and Chef Infra Server. Migration considerations include creating an equivalent Ansible playbook for server deployment.

- `setup-automate/deploy-chef-server.sh`: Bash script that deploys Chef Infra Server without Automate. Migration considerations include creating an equivalent Ansible playbook for server deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider ansible-test for unit testing
  - For compliance testing, consider OpenSCAP with Ansible integration or Ansible Compliance as Code

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2 to prevent POODLE vulnerability.
  - Migration approach: Ensure the Ansible playbook continues to enforce the same SSL/TLS protocol restrictions.

- **SSH Security**: The SSH root login restriction must be maintained.
  - Migration approach: Convert the InSpec control to an equivalent Ansible task that enforces the same SSH configuration.

- **Self-signed Certificates**: The current implementation generates self-signed certificates for HTTPS.
  - Migration approach: Maintain the same certificate generation process or consider integrating with Let's Encrypt for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts (username/password in both deploy-automate.sh and deploy-chef-server.sh)

### Technical Challenges

- **Testing Framework Conversion**: Converting Chef InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Use Ansible Molecule which provides similar functionality for infrastructure testing, or integrate with other testing frameworks like Serverspec or Testinfra.

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible playbooks.
  - Mitigation strategy: Create Ansible roles that perform the same server setup and configuration tasks, using Ansible modules for package installation, service configuration, and user management.

- **System Configuration**: The deployment scripts set system parameters like vm.max_map_count and vm.dirty_expire_centisecs.
  - Mitigation strategy: Use the Ansible sysctl module to configure these kernel parameters.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible Molecule or other compatible testing framework
   - Update CI/CD pipeline to use the new testing framework

3. **Chef Server Deployment Scripts** (Medium complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secret management with Ansible Vault

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need functional changes.
3. The deployment scripts are used for setting up development/test environments and not production systems (given the hardcoded credentials).
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. There is no requirement to maintain backward compatibility with Chef InSpec or Test Kitchen.
6. The migration will include improving security practices by implementing proper secret management.