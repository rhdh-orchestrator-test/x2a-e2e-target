# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of Ansible playbooks for web server configuration and Chef InSpec tests for validation, along with Chef Automate and Chef Infra Server deployment scripts. The estimated timeline for migration is 1-2 weeks given the limited scope and straightforward configurations.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with SSL/TLS setup and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Deployment script for Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Consider maintaining InSpec as a standalone testing tool that works with Ansible

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Use existing Vagrant driver or alternatives like Docker

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the current playbooks:
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Self-signed certificates should be replaced with proper certificate management
  
- **SSH Hardening**: The SSH compliance profile checks for root login restrictions:
  - Ensure Ansible playbooks enforce the same SSH security controls
  - Consider expanding SSH hardening based on the existing compliance profile

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username: 'jtonello', password: 'password') should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for key storage or integrate with external certificate management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing will require careful mapping of assertions:
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible assert module with appropriate conditions or maintain InSpec as a separate tool

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment:
  - Challenge: The deployment scripts set up Chef-specific infrastructure
  - Mitigation: Replace with Ansible Automation Platform deployment or equivalent CI/CD pipeline setup

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Add proper secret management for SSL certificates

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate into the website-https playbook as a security role
   - Enhance with additional hardening measures

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert statements or Molecule tests
   - Alternatively, maintain as standalone tests that can be executed post-deployment

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible Automation Platform deployment
   - Or implement equivalent CI/CD pipeline with GitLab/GitHub Actions

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use
2. The InSpec tests are considered valuable and should be preserved in some form
3. The deployment scripts are examples and not used in production environments
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The security requirements (TLS configuration, SSH hardening) must be maintained in the migrated solution
7. No specific performance requirements are documented that would affect the migration approach