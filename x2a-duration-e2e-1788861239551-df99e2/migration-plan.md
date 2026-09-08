# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with Chef InSpec test verification and Chef server deployment scripts. The migration scope is minimal as the infrastructure automation is already implemented in Ansible - the focus should be on replacing Chef InSpec testing with native Ansible testing approaches.

## Module Migration Plan

This repository contains example configurations and deployment scripts that demonstrate Chef InSpec integration with Ansible:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache HTTPS website deployment with SSL certificate generation, virtual host configuration, and security hardening
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Self-signed SSL certificates via OpenSSL, Apache virtual host configuration, SSL protocol enforcement (TLS 1.2), POODLE vulnerability mitigation

**chef-server-deployment**:
- Description: Chef Automate and Chef Infra Server deployment automation for lab environments
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `website_https.yml`: Main Ansible playbook for Apache HTTPS site deployment with SSL configuration
- `poodle_fix.yml`: Security hardening playbook to disable SSL 3.0 and enforce TLS 1.2
- `tests/website_https_verify.rb`: Chef InSpec tests for HTTPS functionality, SSL protocol verification, and service validation
- `tests/ssh_profile.rb`: Chef InSpec compliance profile for SSH root login security controls (STIG compliance)
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script with user/org provisioning
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing using ansible-test, molecule, or testinfra
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Evaluate need for centralized configuration management - consider Ansible Tower/AWX or Ansible Automation Platform

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses self-signed certificates - migration should consider proper certificate management with Let's Encrypt or enterprise CA integration
- **SSH Security Controls**: InSpec profile enforces SSH root login restrictions - ensure equivalent Ansible security hardening is maintained
- **STIG Compliance**: SSH profile includes STIG controls (RHEL-08-000227) - migration must preserve compliance requirements
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials - implement Ansible Vault for secrets management

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing requires rewriting test logic and assertions
- **Compliance Validation**: STIG compliance checks need translation from InSpec DSL to Ansible testing framework
- **Test Kitchen Replacement**: Existing Vagrant-based testing workflow needs migration to Molecule or similar Ansible testing tools
- **Chef Infrastructure Dependencies**: Deployment scripts assume Chef ecosystem - evaluate if Chef server components are still needed

### Migration Order

1. **Website HTTPS Demo** (low complexity) - Ansible playbooks are already present, only testing framework needs migration
2. **Testing Framework** (moderate complexity) - Replace InSpec tests with Ansible native testing approach
3. **Chef Server Deployment** (evaluate necessity) - Determine if Chef infrastructure is still required or can be decommissioned

### Assumptions

- The Chef InSpec testing framework is being replaced entirely with Ansible-native testing solutions
- Chef Automate and Chef Infra Server deployment may no longer be required if migrating away from Chef ecosystem
- Current SSL certificate approach (self-signed) is acceptable for the target environment or will be enhanced separately
- Ubuntu 20.04 target platform will be maintained or upgraded to a supported version
- Vagrant-based testing environment can be replaced with Molecule or equivalent Ansible testing framework
- STIG compliance requirements must be preserved in the migration to Ansible-native testing
- The repository serves as example/demo code rather than production infrastructure requiring migration