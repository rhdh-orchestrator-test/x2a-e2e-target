# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible's `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a standalone testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Molecule for Ansible role testing
  - Option 2: Use simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower
  - Option 2: Use GitLab CI/CD with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening configurations:
  - Ensure TLSv1.2 is enabled and older protocols are disabled
  - Maintain proper certificate generation and management
  - Consider using Ansible Vault for storing sensitive information

- **SSH Security**: Maintain SSH hardening practices:
  - Continue enforcing root login restrictions
  - Migrate compliance tests to ensure ongoing verification

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificate generation in website_https.yml
  - Recommend migrating to Ansible Vault for all credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-native testing requires careful mapping of test assertions:
  - Challenge: InSpec has specialized resources for testing SSL/TLS configurations
  - Mitigation: May need to develop custom Ansible modules or use shell commands with assertions

- **Compliance Reporting**: Chef Automate provides compliance reporting capabilities:
  - Challenge: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Consider integrating with tools like Prometheus/Grafana for reporting or maintaining a hybrid approach

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **ssl-poodle-fix** (low risk, already in Ansible)
   - Integrate with website-https role
   - Enhance with additional SSL hardening measures

3. **compliance-tests** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **chef-automate-deployment** (high complexity)
   - Replace with AWX/Ansible Tower deployment
   - Migrate user/organization management to Ansible inventory and variables

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The SSL configuration is for demonstration purposes and may need enhancement for production use
3. The hardcoded credentials in setup scripts are for demonstration only
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The migration will standardize on Ansible while preserving the compliance testing capabilities
7. No custom Chef resources or complex Chef-specific functionality is in use