# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test profile for validating HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **ssh-security-profile**:
    - Description: Chef InSpec test profile for validating SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance checks

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment example
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: Ansible Lint for static code analysis
  - Option 3: Ansible Test Plugins for runtime validation

- **Test Kitchen**: Replace with:
  - Ansible Molecule for test orchestration
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible roles for configuration management server deployment
  - Consider migrating to AWX/Ansible Tower as a replacement for Chef Automate

### Security Considerations

- **SSL Configuration**: The current playbooks enforce TLSv1.2 and disable SSLv3. Migration should maintain or enhance these security controls.
  - Migration approach: Preserve the existing Ansible tasks for SSL hardening, consider updating to include TLSv1.3 support

- **SSH Hardening**: The InSpec profile validates SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls, with idempotent checks

- **Self-signed Certificates**: The current solution generates self-signed certificates.
  - Migration approach: Maintain the existing Ansible OpenSSL module usage, consider adding support for Let's Encrypt as an alternative

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require careful mapping of test assertions.
  - Mitigation strategy: Create a mapping document for InSpec resources to Ansible modules, use Ansible assert module for validation

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs to be replicated.
  - Mitigation strategy: Implement Ansible callback plugins to generate compliance reports, consider integration with tools like Prometheus/Grafana for visualization

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and update to current Ansible best practices
   - Ensure idempotence and add tags for selective execution

2. **Testing Framework** - Moderate complexity
   - Set up Ansible Molecule for testing infrastructure
   - Create equivalent tests for the InSpec profiles

3. **Chef Deployment Scripts** - High complexity
   - Create Ansible roles to replace the Chef Automate/Server deployment scripts
   - Implement equivalent user/organization management functionality

### Assumptions

1. The primary goal is to migrate away from Chef components while preserving the existing Ansible functionality.
2. The InSpec tests are used for validation only and not for active remediation.
3. There are no additional Chef cookbooks or recipes beyond what's visible in the repository.
4. The deployment scripts are used for demonstration purposes and not in production environments.
5. The SSL/TLS configurations may need updating to current security best practices.
6. No external dependencies or integrations exist beyond what's documented in the files.
7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.