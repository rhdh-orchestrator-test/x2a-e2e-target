# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing InSpec tests to Ansible-native testing solutions while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that fixes SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Verifies port 443 is listening, HTTPS is working, SSL3 is disabled, TLSv1.2 is enabled, SSH root login is disabled

- **chef-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Hostname configuration, system tuning, Chef Automate/Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be kept as-is or converted to a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing, consider using OpenSCAP with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for CI/CD pipelines
  - Compliance functionality can be replaced with OpenSCAP or similar tools

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture:
  - Keep the TLSv1.2 requirement
  - Consider adding support for TLSv1.3
  - Ensure proper certificate management

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the Ansible solution:
  - Verify SSH root login is disabled
  - Maintain compliance with referenced STIGs

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate/Infra Server deployment scripts (username, password)
  - Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing solutions while maintaining the same level of compliance verification:
  - Solution: Use Ansible Molecule with custom verifiers or OpenSCAP

- **Test Kitchen to Molecule Migration**: Ensuring test environments are properly configured:
  - Solution: Create equivalent Molecule scenarios for each Test Kitchen suite

- **Chef Automate/Infra Server Replacement**: Finding appropriate Ansible-native alternatives for the functionality provided by Chef Automate and Infra Server:
  - Solution: Implement AWX/Tower for web UI and job scheduling, integrate with CI/CD tools for pipeline functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule tests
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks with Ansible Vault for credentials
4. **Test Infrastructure** (kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README.md mentioning it's a companion to a white paper.
2. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
3. The deployment scripts are intended for single-node deployments rather than distributed systems.
4. There are no external dependencies or integrations beyond what is explicitly defined in the files.
5. The migration will maintain the same functionality but using Ansible-native solutions instead of Chef InSpec.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.