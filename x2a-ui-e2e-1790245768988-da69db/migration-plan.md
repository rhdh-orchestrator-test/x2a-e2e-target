# MIGRATION FROM CHEF INSPEC EXAMPLES TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. Rather than traditional Chef cookbooks requiring migration, this is already an Ansible-based implementation with InSpec testing. The migration scope is minimal, focusing on modernizing existing Ansible playbooks and potentially replacing InSpec tests with native Ansible testing approaches.

**Timeline Estimate**: 1-2 weeks for modernization and testing framework evaluation
**Complexity**: Low - No actual Chef cookbooks to migrate, only example playbooks to modernize

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that demonstrate compliance automation patterns:

### MODULE INVENTORY

**apache-https-setup**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host deployment
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, Hello World website deployment

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols (POODLE fix)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, vulnerability remediation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test file for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Currently used for compliance testing - evaluate replacement with Ansible native testing or molecule
- **Test Kitchen**: Used for infrastructure testing - consider migration to molecule for Ansible-native testing
- **OpenSSL Ansible modules**: Already in use - ensure latest collection versions (community.crypto)

### Security Considerations
- **SSL/TLS Configuration**: Existing playbooks properly implement TLS 1.2 enforcement and disable vulnerable protocols
- **Certificate Management**: Self-signed certificates used for testing - production deployments should integrate with proper CA or Let's Encrypt
- **SSH Hardening**: InSpec tests verify SSH root login restrictions - ensure Ansible playbooks implement these controls
- **Credential Management**: 
  - Hardcoded passwords in deployment scripts (userpassword='password')
  - No vault usage detected in current playbooks
  - SSL private keys generated without passphrase protection

### Technical Challenges
- **Testing Framework Migration**: Deciding whether to keep InSpec for compliance testing or migrate to Ansible native testing approaches
- **Test Kitchen Replacement**: Evaluating molecule vs maintaining Test Kitchen for infrastructure testing
- **Compliance Automation**: Ensuring STIG controls and security baselines remain testable after any testing framework changes

### Migration Order
1. **Ansible Playbook Modernization** (Priority 1 - low risk, immediate value)
   - Update to latest Ansible syntax and best practices
   - Implement proper variable management and vault integration
   - Update to latest community.crypto collection modules

2. **Testing Framework Evaluation** (Priority 2 - moderate complexity)
   - Assess InSpec vs Ansible native testing for compliance validation
   - Consider molecule integration for playbook testing
   - Maintain existing compliance test coverage

3. **Security Hardening** (Priority 3 - security focused)
   - Remove hardcoded credentials from deployment scripts
   - Implement proper certificate management workflows
   - Add comprehensive security baseline testing

### Assumptions
- This repository serves as example/demo code rather than production infrastructure requiring migration
- The goal is to modernize existing Ansible implementations rather than migrate from Chef
- InSpec testing may be retained for compliance validation if it provides value over native Ansible testing
- Deployment scripts are for lab/demo environments and may not require production-grade security
- Ubuntu 20.04 target platform may need updating to more recent LTS versions
- Test Kitchen configuration suggests development/testing workflow that may benefit from molecule migration
- SSL certificate generation approach is appropriate for demo/testing but not production use