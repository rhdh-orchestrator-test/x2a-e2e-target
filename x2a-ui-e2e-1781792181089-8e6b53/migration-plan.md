# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, as indicated by the README in the chef-and-ansible directory. Additionally, there are Chef Automate and Chef Infra Server deployment scripts in the setup-automate directory.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec test profiles. The migration complexity is low to moderate, as we need to:
1. Preserve the existing Ansible playbooks
2. Replace Chef InSpec tests with Ansible-native testing solutions

Estimated timeline: 1-2 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (specifically root login)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic validation
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for Ansible roles with support for various drivers (Vagrant, Docker, etc.)

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible Tower/AWX for job scheduling and reporting
  - OpenSCAP for compliance scanning
  - Prometheus and Grafana for monitoring and dashboards

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Maintain the same level of Apache security configuration

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be preserved
  - Convert STIG compliance checks to Ansible-based validation
  - Maintain security tagging and documentation for compliance purposes

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username: 'jtonello', password: 'password')
  - These should be migrated to Ansible Vault or another secure secret management solution

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec's declarative testing approach
  - InSpec provides a domain-specific language for compliance testing that is more concise than equivalent Ansible tasks
  - Solution: Use a combination of Ansible assert modules and custom modules where needed

- **Test Reporting**: InSpec provides structured test output and reporting
  - Solution: Implement custom reporting using Ansible callback plugins or integrate with external reporting tools

- **Compliance Metadata**: The InSpec profiles contain rich metadata (CCI IDs, STIG references)
  - Solution: Preserve this metadata in Ansible task documentation or in separate compliance documentation

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - These can remain largely unchanged as they are already in Ansible format
   - Review and update for best practices and idempotence

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Ansible-native testing using assert modules or Molecule
   - Preserve all compliance metadata and validation logic

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Convert to Ansible roles for infrastructure deployment
   - Implement secure credential management

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functioning correctly and follow best practices
3. There is no requirement to maintain backward compatibility with Chef Automate for compliance reporting
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
5. The Test Kitchen configuration is only used for development/testing and not in production pipelines
6. The STIG compliance requirements in the SSH profile need to be maintained in the Ansible solution
7. The self-signed certificates in the website_https.yml playbook are acceptable for the use case (not production)