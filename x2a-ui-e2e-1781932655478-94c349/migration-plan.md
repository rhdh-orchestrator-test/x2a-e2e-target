# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup, virtual hosts, and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: InSpec tests to verify HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security control mapping to standards (SRG, CCI)

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Analyzing the source repository to determine target environment specifications:

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
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance platforms
  - Consider AWX/Ansible Tower as a replacement for centralized management

### Security Considerations

- **SSL/TLS Configuration**: Maintain the security hardening that disables SSLv3 and enables only TLSv1.2
- **Self-signed Certificates**: Preserve the certificate generation process in Ansible
- **SSH Security Controls**: Maintain compliance checks for SSH configuration
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks will require careful mapping of test assertions
  - Mitigation: Consider using the ansible.builtin.assert module or community.general.assert_cmd module

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Explore Ansible callback plugins for custom reporting or integration with compliance platforms

### Migration Order

1. **website-https-configuration** (already in Ansible, low risk)
2. **poodle-vulnerability-fix** (already in Ansible, low risk)
3. **chef-infrastructure-deployment** (moderate complexity, convert bash scripts to Ansible playbooks)
4. **website-https-compliance** (high complexity, convert InSpec tests to Ansible verification tasks)
5. **ssh-security-compliance** (high complexity, convert InSpec profile to Ansible verification tasks)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec alongside Ansible rather than production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The security compliance requirements (POODLE fix, SSH hardening) need to be maintained in the migrated solution
4. The Chef Automate and Chef Infra Server deployment scripts are used for demonstration purposes and may not need direct migration if the compliance functionality is handled differently in the Ansible ecosystem
5. No external data sources or complex state management is required
6. No custom Chef resources or complex Ruby code is present that would require special handling