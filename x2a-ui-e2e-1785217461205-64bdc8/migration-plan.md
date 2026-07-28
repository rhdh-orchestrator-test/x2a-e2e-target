# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec and Ansible configurations that are used for demonstration and example purposes. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance automation. The repository is relatively small and contains:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is moderate, with a focus on preserving the compliance testing functionality while standardizing on Ansible. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that checks SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG, CCI)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML template for the website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Use Ansible's `assert` module for basic tests
  - Consider Molecule for more comprehensive testing
  - Alternatively, maintain InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or adapt existing kitchen.yml to work with Ansible-only testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure setup
  - Consider migrating to Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL security configurations:
  - Self-signed certificate generation
  - TLS protocol restrictions (disabling SSLv3, enabling TLSv1.2)
  - Apache SSL module configuration

- **SSH Security**: Maintain compliance checks for SSH configuration:
  - Root login restrictions
  - Protocol security settings

- **Vault/secrets management**:
  - Current implementation uses hardcoded passwords in shell scripts (userpassword='password')
  - Migrate to Ansible Vault for secure credential storage
  - 1 credential detected in setup-automate scripts (user password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider maintaining InSpec for testing while using Ansible for configuration management

- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI numbers) that needs to be preserved
  - Mitigation: Use Ansible tags and documentation to maintain compliance information
  - Consider implementing custom reporting to generate compliance documentation

### Migration Order

1. **website-https** and **poodle-fix** playbooks (low risk, already in Ansible)
   - Review and optimize existing Ansible code
   - Add documentation and improve variable usage

2. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure compliance metadata is preserved

3. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate/Infra Server deployment
   - Or create Ansible playbooks to deploy alternative solutions

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the same functionality
2. The compliance testing capabilities are important to preserve
3. The Chef Automate/Infra Server deployment scripts may be replaced with equivalent Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates are acceptable for the demonstration environment
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only