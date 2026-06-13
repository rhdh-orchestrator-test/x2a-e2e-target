# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of Ansible playbooks with Chef InSpec tests and Chef Automate/Chef Server deployment scripts. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Apache web server with HTTPS configuration, self-signed certificates, and basic website deployment
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle_fix**:
    - Description: Security fix for POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, security hardening

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content validation, SSL/TLS protocol verification, SSH root login security check

- **chef_automate_deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef_server_deployment**:
    - Description: Deployment script for standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or molecule for testing
  - Alternative: Maintain InSpec as a complementary tool alongside Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-compatible CI/CD pipelines (GitHub Actions, Jenkins, etc.)

- **Chef Automate/Server**: Replace with:
  - Ansible AWX/Tower for web UI, role-based access control, and job scheduling
  - GitLab/GitHub for version control and CI/CD pipelines
  - Ansible Semaphore for lightweight Ansible UI

### Security Considerations

- **SSL/TLS Configuration**: Maintain security hardening by ensuring the Ansible playbooks continue to:
  - Disable vulnerable protocols (SSLv3)
  - Enable only secure protocols (TLSv1.2+)
  - Generate proper certificates

- **SSH Security**: Preserve SSH hardening practices:
  - Maintain the prohibition of root login via SSH
  - Consider expanding SSH hardening with additional Ansible tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: 2 instances (username/password in deploy-automate.sh and deploy-chef-server.sh)
  - Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Migrating from InSpec to Ansible-native testing tools may require:
  - Learning new testing frameworks
  - Rewriting test logic to match Ansible's assertion capabilities
  - Potential loss of some specialized compliance checks that InSpec provides

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting with:
  - Custom Ansible reporting solutions
  - Integration with third-party compliance tools
  - Development of custom dashboards in AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, only need minor adjustments for best practices
2. **InSpec Tests**: Moderate complexity, requires conversion to Ansible-native testing
3. **Chef Deployment Scripts**: Higher complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, based on the README description.
2. The Chef InSpec tests are used for verification of Ansible-deployed configurations, not as part of a larger Chef ecosystem.
3. There are no external dependencies or integrations beyond what's visible in the repository.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
6. The migration will maintain the same level of security compliance checking currently provided by InSpec.