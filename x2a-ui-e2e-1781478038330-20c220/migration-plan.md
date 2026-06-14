# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificates, and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL/TLS by disabling SSLv3 and enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, service restart handlers

- **https-compliance-tests**:
    - Description: InSpec tests to verify HTTPS configuration, port status, and content delivery
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security tagging with STIG IDs

- **chef-server-deployment**:
    - Description: Automated deployment of Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef server installation, user and organization creation

- **chef-automate-deployment**:
    - Description: Automated deployment of Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef server integration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML content for website deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance and automation platforms
  - Consider AWX/Ansible Automation Platform as replacement for Chef Automate

### Security Considerations

- **SSL/TLS Configuration**: Maintain security hardening by ensuring the Ansible playbooks continue to:
  - Disable vulnerable SSL/TLS protocols (SSLv3)
  - Enforce TLSv1.2 or higher
  - Generate proper certificates with appropriate permissions

- **SSH Hardening**: Preserve SSH security controls:
  - Maintain the check for disabled root login
  - Consider expanding SSH hardening with Ansible security roles

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username: jtonello, password: password)
  - Replace with Ansible Vault for secure credential storage
  - Consider integration with external secret management systems

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing or integrating Chef InSpec tests
  - Solution: Convert InSpec tests to equivalent Ansible assert tasks or use ansible-test
  - Alternative: Keep InSpec and invoke it from Ansible playbooks

- **Certificate Management**: The current solution uses Ansible's openssl modules
  - Solution: Continue using Ansible's native openssl modules, which are already well-implemented

- **Test Environment**: Current testing relies on Test Kitchen with Vagrant
  - Solution: Migrate to Molecule for testing Ansible roles and playbooks

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to Ansible role for better reusability

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the website-https role as a security task
   - Update handlers for service restarts

3. **https-compliance-tests** and **ssh-security-compliance** (moderate complexity)
   - Convert InSpec tests to Ansible assert tasks
   - Create verification playbooks to run post-deployment

4. **chef-server-deployment** and **chef-automate-deployment** (high complexity)
   - Determine if Chef server/Automate functionality is still needed
   - If needed, create Ansible playbooks to deploy alternative solutions

### Assumptions

1. The primary purpose of this repository is demonstrating compliance automation alongside configuration management
2. The InSpec tests are essential for compliance verification and must be preserved in some form
3. The Chef server and Automate deployment scripts are examples and not critical production components
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The migration will standardize on Ansible while maintaining equivalent functionality
6. No external data sources or integrations beyond what's visible in the repository are required
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only